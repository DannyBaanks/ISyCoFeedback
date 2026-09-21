from pathlib import Path

from isycofeedback.repair import apply_patch_files, repair_command


def test_repair_applies_fake_patch_and_requires_verification(tmp_path: Path) -> None:
    target = tmp_path / "status.txt"
    target.write_text("broken", encoding="utf-8")

    def fake_provider(attempt, failure):
        assert attempt == 1
        assert failure.verdict == "FAIL"
        return [{"path": "status.txt", "old_content": "broken", "new_content": "fixed"}]

    result = repair_command("test \"$(cat status.txt)\" = fixed", tmp_path, fake_provider)

    assert result.final_verdict == "PASS"
    assert len(result.attempts) == 2
    assert target.read_text(encoding="utf-8") == "fixed"


def test_patch_cannot_escape_repository(tmp_path: Path) -> None:
    try:
        apply_patch_files(tmp_path, [{"path": "../outside.txt", "old_content": "", "new_content": "x"}])
    except ValueError as error:
        assert "outside repository" in str(error)
    else:
        raise AssertionError("path traversal patch was accepted")
