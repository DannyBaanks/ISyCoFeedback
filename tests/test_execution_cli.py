import sys
from pathlib import Path

from isycofeedback.cli import main


def _manifest(command: str) -> str:
    return f"version: 1\nproject:\n  name: Fixture\ncommands:\n  test: >-\n    {command}\n  verify: >-\n    {command}\nretry:\n  max_attempts: 3\n"


def test_test_command_runs_declared_command_and_writes_receipt(tmp_path: Path, capsys) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(_manifest(f'"{sys.executable}" -c "print(\'ok\')"'), encoding="utf-8")

    assert main(["test", "--path", str(tmp_path)]) == 0

    assert "TEST  PASS" in capsys.readouterr().out
    assert len(list((tmp_path / ".isycofeedback/receipts").glob("*.json"))) == 1


def test_retry_command_stops_after_three_failures(tmp_path: Path, capsys) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(_manifest(f'"{sys.executable}" -c "raise SystemExit(4)"'), encoding="utf-8")

    assert main(["retry", "--path", str(tmp_path)]) == 1

    output = capsys.readouterr().out
    assert output.count("ATTEMPT") == 3
    assert "REPAIR_EXHAUSTED" in output


def test_issue_and_pr_require_dry_run_and_show_payload(tmp_path: Path, capsys) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(_manifest("false"), encoding="utf-8")
    main(["test", "--path", str(tmp_path)])
    capsys.readouterr()

    assert main(["issue", "--path", str(tmp_path), "--dry-run"]) == 0
    issue_output = capsys.readouterr().out
    assert "DRY-RUN" in issue_output
    assert "Failure in Fixture" in issue_output

    assert main(["pr", "--path", str(tmp_path), "--dry-run"]) == 0
    assert "UNVERIFIED" in capsys.readouterr().out
