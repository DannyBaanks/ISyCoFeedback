"""Command-line entry point for ISyCoFeedback."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from isycofeedback.diagnostics import diagnose
from isycofeedback.collaboration.github import build_issue_payload, build_pr_payload
from isycofeedback.manifest import MANIFEST_NAME, ManifestError, load_manifest
from isycofeedback.receipts import create_receipt, save_receipt
from isycofeedback.retry import retry_command
from isycofeedback.runner import run_command


CAPABILITY_ORDER = (
    ("run", "RUN"),
    ("test", "TEST"),
    ("verify", "VERIFY"),
    ("reproduce", "REPRODUCE"),
    ("retry", "RETRY"),
    ("repair", "REPAIR"),
    ("issue", "ISSUE"),
    ("fork", "FORK"),
    ("pr", "PR"),
)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        _print_menu()
        return 0
    if args.command == "init":
        return _init(args.path, args.name)
    if args.command == "doctor":
        return _doctor(args.path, args.manifest)
    if args.command == "capabilities":
        return _capabilities(args.path, args.manifest)
    if args.command in {"run", "test", "verify", "reproduce"}:
        return _execute(args.command, args.path, args.manifest, args.evidence_path)
    if args.command == "retry":
        return _retry(args.path, args.manifest, args.evidence_path)
    if args.command in {"issue", "pr"}:
        return _collaboration(args.command, args.path, args.dry_run, args.manifest, args.evidence_path)
    parser.error(f"unsupported command: {args.command}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="isycofeedback")
    subparsers = parser.add_subparsers(dest="command")
    for name in ("doctor", "capabilities", "run", "test", "verify", "retry", "reproduce"):
        command = subparsers.add_parser(name)
        command.add_argument("--path", type=Path, default=Path.cwd())
        command.add_argument("--manifest", type=Path)
        if name in {"run", "test", "verify", "retry", "reproduce"}:
            command.add_argument("--evidence-path", type=Path)
    for name in ("issue", "pr"):
        command = subparsers.add_parser(name)
        command.add_argument("--path", type=Path, default=Path.cwd())
        command.add_argument("--manifest", type=Path)
        command.add_argument("--dry-run", action="store_true")
        command.add_argument("--evidence-path", type=Path)
    init = subparsers.add_parser("init")
    init.add_argument("--path", type=Path, default=Path.cwd())
    init.add_argument("--name")
    return parser


def _init(repository: Path, name: str | None) -> int:
    path = repository / MANIFEST_NAME
    if path.exists():
        print(f"Exists: {path}")
        return 0
    project_name = name or repository.name
    path.write_text(
        f"version: 1\nproject:\n  name: {project_name}\ncommands: {{}}\nretry:\n  max_attempts: 3\n",
        encoding="utf-8",
    )
    print(f"Created: {path}")
    return 0


def _doctor(repository: Path, manifest_path: Path | None = None) -> int:
    for key, value in diagnose(repository, manifest_path).items():
        if key == "manifest_error":
            print(f"MANIFEST_ERROR  {value}")
        elif isinstance(value, list):
            print(f"{key.upper()}  {', '.join(value) or 'NONE'}")
        else:
            print(f"{key.upper()}  {value}")
    return 0


def _capabilities(repository: Path, manifest_path: Path | None = None) -> int:
    try:
        manifest = load_manifest(repository, manifest_path)
    except ManifestError as error:
        print(f"CONFIGURATION_FAILURE  {error}")
        return 1
    github = manifest.github or {}
    for key, label in CAPABILITY_ORDER:
        if key == "retry":
            print(f"{label:<12} YES ({manifest.max_attempts})")
            continue
        enabled = key in manifest.commands or github.get({"issue": "issues", "pr": "pull_requests"}.get(key, key), False)
        print(f"{label:<12} {'YES' if enabled else 'NO'}")
    return 0


def _execute(action: str, repository: Path, manifest_path: Path | None = None, evidence_path: Path | None = None) -> int:
    try:
        manifest = load_manifest(repository, manifest_path)
    except ManifestError as error:
        print(f"CONFIGURATION_FAILURE  {error}")
        return 1
    command = manifest.commands.get(action)
    if command is None:
        print(f"UNSUPPORTED_CAPABILITY  {action}")
        return 1
    result = run_command(command, repository)
    receipt = save_receipt(evidence_path or repository, create_receipt(action, result))
    print(f"{action.upper()}  {result.verdict}")
    print(f"Receipt: {receipt}")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return 0 if result.verdict == "PASS" else 1


def _retry(repository: Path, manifest_path: Path | None = None, evidence_path: Path | None = None) -> int:
    try:
        manifest = load_manifest(repository, manifest_path)
    except ManifestError as error:
        print(f"CONFIGURATION_FAILURE  {error}")
        return 1
    command = manifest.commands.get("test")
    if command is None:
        print("UNSUPPORTED_CAPABILITY  test")
        return 1
    retry_result = retry_command(command, repository, manifest.max_attempts)
    for number, result in enumerate(retry_result.attempts, start=1):
        save_receipt(evidence_path or repository, create_receipt("retry", result))
        print(f"ATTEMPT {number}/{manifest.max_attempts}  {result.verdict}")
    print(f"{retry_result.final_verdict}")
    return 0 if retry_result.final_verdict == "PASS" else 1


def _collaboration(
    action: str,
    repository: Path,
    dry_run: bool,
    manifest_path: Path | None = None,
    evidence_path: Path | None = None,
) -> int:
    if not dry_run:
        print("REMOTE_MUTATION_REQUIRES_DRY_RUN")
        return 1
    receipts = list(((evidence_path or repository) / ".isycofeedback" / "receipts").glob("*.json"))
    if not receipts:
        print("NO_EVIDENCE")
        return 1
    receipt_path = max(
        receipts,
        key=lambda path: json.loads(path.read_text(encoding="utf-8")).get("created_at", ""),
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    project = load_manifest(repository, manifest_path).project_name
    head_result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    git_head = head_result.stdout.strip() if head_result.returncode == 0 else "unknown"
    payload = build_issue_payload(project, git_head, receipt) if action == "issue" else build_pr_payload(project, git_head, receipt, verified=False)
    print("DRY-RUN")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _print_menu() -> None:
    print("ISyCoFeedback")
    print("─────────────────────────")
    print("\n[1] Run\n[2] Test\n[3] Verify\n[4] Retry\n[5] Diagnose\n[6] Reproduce\n[7] Repair\n[8] Save evidence\n[9] Open issue\n[F] Fork\n[P] Pull request\n[Q] Quit")


if __name__ == "__main__":
    sys.exit(main())
