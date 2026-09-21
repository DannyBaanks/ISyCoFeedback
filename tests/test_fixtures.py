from pathlib import Path

from isycofeedback.manifest import load_manifest


ROOT = Path(__file__).parents[1]


def test_pass_fixture_declares_test_and_verify() -> None:
    manifest = load_manifest(ROOT / "fixtures/pass-repo")

    assert manifest.project_name == "pass-repo"
    assert manifest.commands["test"] == "echo PASS"
    assert manifest.commands["verify"] == "echo VERIFIED"


def test_chrome_to_fox_example_keeps_github_outside_core_commands() -> None:
    example = (ROOT / "examples/chrome-to-fox.isycofeedback.yml").read_text(encoding="utf-8")

    assert "name: Chrome-to-Fox" in example
    assert "api-key" not in example
