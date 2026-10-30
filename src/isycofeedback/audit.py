"""Verify the ledger and every corresponding sealed command receipt."""
import json
from pathlib import Path

from .documents.ledger import Ledger, verify_ledger
from .receipts import verify_receipt


def audit_evidence(repository: Path, expected_head: str | None = None) -> tuple[bool, list[str], str | None]:
    directory = repository / '.isycofeedback'
    ledger = Ledger(directory / 'ledger.jsonl')
    try:
        valid, errors = verify_ledger(ledger.path, expected_head=expected_head)
        if not valid:
            return False, errors, None
        identities = set()
        for entry in ledger.entries():
            identity = entry.execution_id
            if len(identity) != 32 or any(c not in '0123456789abcdef' for c in identity):
                return False, ['invalid receipt identity in ledger'], None
            if identity in identities:
                return False, ['duplicate receipt identity in ledger'], None
            identities.add(identity)
            receipt = json.loads((directory/'receipts'/f'{identity}.json').read_text(encoding='utf-8'))
            ok, reason = verify_receipt(receipt)
            if not ok or receipt['run_id'] != identity or receipt['receipt_sha256'] != entry.record_sha256:
                return False, [reason if not ok else 'receipt does not match ledger'], None
        actual = {path.stem for path in (directory/'receipts').glob('*.json')}
        if identities != actual:
            return False, ['receipt set does not match ledger'], None
        return True, [], ledger.head()
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return False, ['malformed or missing evidence'], None
