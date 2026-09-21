from pathlib import Path

from isycofeedback.cli import main


def test_init_creates_small_manifest_without_inventing_commands(tmp_path: Path, capsys) -> None:
    assert main(["init", "--path", str(tmp_path), "--name", "Fixture"]) == 0
    output = capsys.readouterr().out

    assert "Created" in output
    manifest = (tmp_path / ".isycofeedback.yml").read_text(encoding="utf-8")
    assert "name: Fixture" in manifest
    assert "commands:" in manifest


def test_capabilities_reports_only_declared_commands(tmp_path: Path, capsys) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(
        "version: 1\nproject:\n  name: Fixture\ncommands:\n  test: echo ok\n",
        encoding="utf-8",
    )

    assert main(["capabilities", "--path", str(tmp_path)]) == 0

    assert capsys.readouterr().out.splitlines() == [
        "RUN          NO",
        "TEST         YES",
        "VERIFY       NO",
        "REPRODUCE    NO",
        "RETRY        YES (3)",
        "REPAIR       NO",
        "ISSUE        NO",
        "FORK         NO",
        "PR           NO",
    ]


def test_no_arguments_prints_terminal_menu(capsys) -> None:
    assert main([]) == 0

    assert "ISyCoFeedback" in capsys.readouterr().out
