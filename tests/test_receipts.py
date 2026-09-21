import json
from pathlib import Path

from isycofeedback.receipts import create_receipt, redact, save_receipt
from isycofeedback.runner import run_command


def test_redact_removes_secret_values() -> None:
    assert redact("token=super-secret", ["super-secret"]) == "token=[REDACTED]"


def test_receipts_have_unique_ids_and_do_not_persist_secrets(tmp_path: Path) -> None:
    result = run_command("printf 'token=super-secret'", cwd=tmp_path)
    first = create_receipt("test", result, secrets=["super-secret"])
    second = create_receipt("test", result, secrets=["super-secret"])

    assert first["run_id"] != second["run_id"]
    assert "super-secret" not in json.dumps(first)

    path = save_receipt(tmp_path, first)

    assert path == tmp_path / ".isycofeedback" / "receipts" / f"{first['run_id']}.json"
    assert "super-secret" not in path.read_text(encoding="utf-8")
