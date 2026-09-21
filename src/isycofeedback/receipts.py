"""Persist immutable, secret-redacted execution receipts."""

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from isycofeedback.runner import CommandResult


def redact(value: str, secrets: list[str]) -> str:
    """Replace configured secret values before evidence is persisted."""
    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def create_receipt(action: str, result: CommandResult, secrets: list[str] | None = None) -> dict[str, object]:
    """Build a JSON-safe receipt for one command execution."""
    secret_values = secrets or []
    result_data = {
        key: redact(value, secret_values) if isinstance(value, str) else value
        for key, value in result.to_dict().items()
    }
    return {
        "run_id": uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "result": result_data,
    }


def save_receipt(repository: Path, receipt: dict[str, object]) -> Path:
    """Write one receipt without overwriting any earlier run."""
    path = repository / ".isycofeedback" / "receipts" / f"{receipt['run_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
