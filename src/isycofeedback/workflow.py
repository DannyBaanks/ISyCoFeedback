"""Bounded verification, patch gates, durable attempts and sealed evidence."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .operations.canonical import sha256
from .receipts import create_receipt, save_receipt, seal_receipt
from .repair import PatchProvider, apply_patch_files
from .runner import run_command
from .workflow_store import WorkflowStore


@dataclass(frozen=True)
class WorkflowResult:
    run_id: str
    verdict: str
    attempts: int
    receipt_path: Path | None


def _validate_patches(root: Path, patches: list[dict[str, str]], allowed: tuple[str, ...]) -> None:
    if not isinstance(patches, list) or not patches:
        raise ValueError('proposal must be a nonempty patch list')
    seen = set()
    for patch in patches:
        if not isinstance(patch, dict) or not all(isinstance(patch.get(key), str)
                                                for key in ('path', 'old_content', 'new_content')):
            raise ValueError('invalid patch contract')
        relative = Path(patch['path'])
        path = relative.as_posix()
        if relative.is_absolute() or '..' in relative.parts or path not in allowed or path in seen:
            raise ValueError('patch path is not allowed')
        if any(part in {'.git', '.isycofeedback', '.github', '.gitlab'} for part in relative.parts):
            raise ValueError('control files cannot be patched')
        if relative.parts[0] in {'tests', 'test'} or relative.name in {'.gitlab-ci.yml', '.isycofeedback.yml'}:
            raise ValueError('verification and policy files cannot be patched')
        target = root / relative
        if any(parent.is_symlink() for parent in [target, *target.parents] if parent != root.parent):
            raise ValueError('symlink patch paths are not allowed')
        if not target.is_file() or not target.resolve().is_relative_to(root):
            raise ValueError('patch target must be an existing project file')
        seen.add(path)


class Workflow:
    def __init__(self, repository: Path, evidence_root: Path | None = None):
        self.repository = repository.resolve()
        self.evidence_root = (evidence_root or repository).resolve()

    @staticmethod
    def contract(repository: Path, command: str, max_attempts: int, allowed_paths: tuple[str, ...]) -> dict:
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= 3:
            raise ValueError('max_attempts must be between 1 and 3')
        return {'schema': 'isycofeedback.workflow/1', 'repository': str(repository.resolve()),
                'command_hash': sha256(command), 'max_attempts': max_attempts,
                'allowed_paths': sorted(set(allowed_paths))}

    def _store(self):
        directory = self.evidence_root / '.isycofeedback'
        directory.mkdir(parents=True, exist_ok=True)
        (directory / '.gitignore').write_text('*\n', encoding='utf-8')
        return WorkflowStore(directory / 'workflows.db')

    def history(self) -> list[dict]:
        store = self._store()
        try:
            return store.history()
        finally:
            store.close()

    def recover(self) -> list[str]:
        store = self._store()
        try:
            identities = store.recover(str(self.repository))
            for identity in identities:
                backups = store.backups(identity)
                contract = json.loads(store.get_run(identity)['contract'])
                restored = True
                for backup in backups:
                    relative = Path(backup['path'])
                    target = self.repository / relative
                    try:
                        _validate_patches(self.repository, [{'path': backup['path'],
                            'old_content': backup['original'], 'new_content': backup['proposed']}],
                            tuple(contract['allowed_paths']))
                    except ValueError:
                        restored = False
                        continue
                    if not target.is_file():
                        restored = False
                        continue
                    current = target.read_text(encoding='utf-8')
                    if current == backup['proposed']:
                        target.write_text(backup['original'], encoding='utf-8')
                    elif current != backup['original']:
                        restored = False
                if restored:
                    store.clear_backups(identity)
            return identities
        finally:
            store.close()

    def attempts(self, run_id: str) -> list[dict]:
        store = self._store()
        try:
            return store.attempts(run_id)
        finally:
            store.close()

    def run(self, command: str, *, run_id: str | None = None, max_attempts: int = 3,
            allowed_paths: tuple[str, ...] = (), provider: PatchProvider | None = None,
            timeout_seconds: float = 60.0, secrets: list[str] | None = None,
            action: str = 'test') -> WorkflowResult:
        identity = run_id or uuid4().hex
        if not isinstance(identity, str) or not identity.strip() or len(identity) > 200:
            raise ValueError('invalid run identity')
        contract = self.contract(self.repository, command, max_attempts, allowed_paths)
        # Timeout is part of the execution contract; never silently widen it on replay.
        if timeout_seconds <= 0:
            raise ValueError('timeout must be positive')
        if timeout_seconds != 60.0:
            contract['timeout_seconds'] = timeout_seconds
        store = self._store()
        originals: dict[Path, str] = {}
        receipt_path = None
        keep_verified_patch = False
        try:
            row, inserted = store.begin(identity, contract)
            if not inserted:
                verdict = 'UNKNOWN' if row['status'] in {'READY', 'RUNNING'} else row['status']
                if verdict not in {'UNKNOWN'}:
                    from .audit import audit_evidence
                    from .receipts import verify_receipt
                    try:
                        path = Path(row['receipt_path'])
                        expected_parent = self.evidence_root / '.isycofeedback' / 'receipts'
                        record = json.loads(path.read_text(encoding='utf-8'))
                        valid = (path.parent == expected_parent and verify_receipt(record)[0]
                                 and record['workflow']['run_id'] == identity
                                 and record['workflow']['contract_hash'] == sha256(contract)
                                 and record['workflow']['attempt'] == row['attempts']
                                 and record['workflow']['verdict'] == row['status']
                                 and audit_evidence(self.evidence_root)[0])
                    except (OSError, ValueError, TypeError, KeyError):
                        valid = False
                    if not valid:
                        verdict = 'INVALID_EVIDENCE'
                return WorkflowResult(identity, verdict, row['attempts'],
                                      Path(row['receipt_path']) if row['receipt_path'] else None)
            verdict = 'REPAIR_EXHAUSTED'
            for _ in range(max_attempts):
                number = store.reserve(identity)
                result = run_command(command, self.repository, timeout_seconds)
                receipt = create_receipt(action, result, secrets)
                store.record(identity, number, receipt['result'])
                verdict = 'PASS' if result.verdict == 'PASS' else 'REPAIR_EXHAUSTED'
                receipt['workflow'] = {'run_id': identity, 'attempt': number, 'contract_hash': sha256(contract),
                                       'verdict': verdict if number == max_attempts or verdict == 'PASS' else 'FAIL'}
                receipt_path = save_receipt(self.evidence_root, seal_receipt(receipt))
                if verdict == 'PASS':
                    break
                if originals:
                    for target, original in originals.items():
                        target.write_text(original, encoding='utf-8')
                    originals.clear()
                    store.clear_backups(identity)
                if number == max_attempts:
                    break
                if provider is not None:
                    try:
                        proposal = provider(number, result)
                        _validate_patches(self.repository, proposal, allowed_paths)
                        originals = {self.repository / patch['path']: (self.repository / patch['path']).read_text(encoding='utf-8')
                                     for patch in proposal}
                        if any(secret and (any(secret in original for original in originals.values())
                            or any(secret in patch['old_content'] or secret in patch['new_content'] for patch in proposal))
                            for secret in (secrets or [])):
                            originals.clear()
                            raise ValueError('configured secrets cannot be persisted in patch backups')
                        store.save_backup(identity, proposal)
                        apply_patch_files(self.repository, proposal)
                    except (ValueError, KeyError, TypeError):
                        verdict = 'DENIED'
                        receipt['workflow']['verdict'] = verdict
                        receipt['run_id'] = uuid4().hex
                        receipt_path = save_receipt(self.evidence_root, seal_receipt(receipt))
                        break
            if verdict != 'PASS':
                for target, original in originals.items():
                    target.write_text(original, encoding='utf-8')
            store.finish(identity, verdict, receipt_path)
            keep_verified_patch = verdict == 'PASS'
            store.clear_backups(identity)
            return WorkflowResult(identity, verdict, number, receipt_path)
        finally:
            try:
                if not keep_verified_patch:
                    for target, original in originals.items():
                        target.write_text(original, encoding='utf-8')
                    if originals:
                        store.clear_backups(identity)
            finally:
                store.close()
