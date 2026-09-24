import sys
from pathlib import Path
import json

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


def test_issue_uses_most_recent_receipt(tmp_path: Path, capsys) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(_manifest("echo latest"), encoding="utf-8")
    main(["test", "--path", str(tmp_path)])
    capsys.readouterr()
    main(["test", "--path", str(tmp_path)])
    capsys.readouterr()
    receipts = sorted((tmp_path / ".isycofeedback/receipts").glob("*.json"))
    newest = max(receipts, key=lambda path: json.loads(path.read_text())["created_at"])
    newest_id = json.loads(newest.read_text())["run_id"]

    assert main(["issue", "--path", str(tmp_path), "--dry-run"]) == 0

    assert newest_id in capsys.readouterr().out


def test_test_command_can_use_external_manifest(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "contract.yml"
    repository = tmp_path / "repository"
    repository.mkdir()
    manifest_path.write_text(_manifest("echo external"), encoding="utf-8")

    assert main(["test", "--path", str(repository), "--manifest", str(manifest_path)]) == 0

    assert "TEST  PASS" in capsys.readouterr().out


def test_external_manifest_can_store_evidence_outside_consumer(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "contract.yml"
    repository = tmp_path / "repository"
    evidence = tmp_path / "evidence"
    repository.mkdir()
    manifest_path.write_text(_manifest("echo external"), encoding="utf-8")

    assert main([
        "test", "--path", str(repository), "--manifest", str(manifest_path), "--evidence-path", str(evidence)
    ]) == 0

    assert list((evidence / ".isycofeedback/receipts").glob("*.json"))
    assert not (repository / ".isycofeedback").exists()
    capsys.readouterr()


def test_named_secret_env_is_redacted_from_receipt_and_stderr(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("IFB_TEST_TOKEN", "tok-9f8e7d6c5b4a")
    leak = f'"{sys.executable}" -c "import os,sys; t=os.environ[\'IFB_TEST_TOKEN\']; print(t); print(t, file=sys.stderr); sys.exit(1)"'
    (tmp_path / ".isycofeedback.yml").write_text(_manifest(leak) + "secrets:\n  - IFB_TEST_TOKEN\n", encoding="utf-8")

    assert main(["test", "--path", str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "tok-9f8e7d6c5b4a" not in captured.out + captured.err
    receipt = next((tmp_path / ".isycofeedback/receipts").glob("*.json")).read_text(encoding="utf-8")
    assert "tok-9f8e7d6c5b4a" not in receipt
    assert "[REDACTED]" in receipt


def test_evidence_dir_ignores_itself_in_the_host_repo(tmp_path: Path) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(_manifest(f'"{sys.executable}" -c "print(1)"'), encoding="utf-8")

    main(["test", "--path", str(tmp_path)])

    assert (tmp_path / ".isycofeedback" / ".gitignore").read_text(encoding="utf-8") == "*\n"
