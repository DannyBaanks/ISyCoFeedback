from pathlib import Path

import pytest

from isycofeedback.manifest import ManifestError, load_manifest


def test_load_manifest_returns_declared_commands(tmp_path: Path) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(
        """
version: 1
project:
  name: Fixture
commands:
  test: echo test
  verify: echo verify
retry:
  max_attempts: 3
""",
        encoding="utf-8",
    )

    manifest = load_manifest(tmp_path)

    assert manifest.project_name == "Fixture"
    assert manifest.commands == {"test": "echo test", "verify": "echo verify"}
    assert manifest.max_attempts == 3


def test_missing_manifest_is_a_configuration_error(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="manifest not found"):
        load_manifest(tmp_path)


def test_invalid_retry_budget_is_rejected(tmp_path: Path) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(
        "version: 1\nproject:\n  name: Fixture\ncommands:\n  test: echo test\nretry:\n  max_attempts: 4\n",
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="max_attempts must be between 1 and 3"):
        load_manifest(tmp_path)


def test_unknown_command_is_not_exposed_as_a_capability(tmp_path: Path) -> None:
    (tmp_path / ".isycofeedback.yml").write_text(
        "version: 1\nproject:\n  name: Fixture\ncommands:\n  test: echo test\ncommands_extra:\n  deploy: echo deploy\n",
        encoding="utf-8",
    )

    manifest = load_manifest(tmp_path)

    assert manifest.commands == {"test": "echo test"}
