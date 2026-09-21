from pathlib import Path

from isycofeedback.diagnostics import diagnose


def test_doctor_reports_manifest_and_missing_gh_without_secrets(tmp_path: Path) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(
        "version: 1\nproject:\n  name: Fixture\ncommands:\n  test: echo ok\n",
        encoding="utf-8",
    )

    report = diagnose(tmp_path)

    assert report["manifest"] == "PASS"
    assert report["commands"] == ["test"]
    assert "gh" in report
