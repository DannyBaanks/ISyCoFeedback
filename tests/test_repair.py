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


def test_failed_precondition_writes_nothing(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a0", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b0", encoding="utf-8")
    try:
        apply_patch_files(tmp_path, [
            {"path": "a.txt", "old_content": "a0", "new_content": "a1"},
            {"path": "b.txt", "old_content": "WRONG", "new_content": "b1"},
        ])
    except ValueError as error:
        assert "precondition" in str(error)
    else:
        raise AssertionError("stale patch was accepted")
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "a0"


def test_write_failure_rolls_back_earlier_files(tmp_path: Path) -> None:
    import os
    import pytest
    (tmp_path / "a.txt").write_text("a0", encoding="utf-8")
    b = tmp_path / "b.txt"
    b.write_text("b0", encoding="utf-8")
    b.chmod(0o444)
    if os.access(b, os.W_OK):
        pytest.skip("running as a user that can write read-only files")
    try:
        with pytest.raises(OSError):
            apply_patch_files(tmp_path, [
                {"path": "a.txt", "old_content": "a0", "new_content": "a1"},
                {"path": "b.txt", "old_content": "b0", "new_content": "b1"},
            ])
    finally:
        b.chmod(0o644)
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "a0"
