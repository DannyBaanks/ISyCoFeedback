"""Load and validate the small project-local feedback contract."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


MANIFEST_NAME = ".isycofeedback.yml"
SUPPORTED_COMMANDS = frozenset(
    {"run", "test", "verify", "retry", "diagnose", "reproduce", "repair"}
)


class ManifestError(ValueError):
    """Raised when a project manifest is missing or invalid."""


@dataclass(frozen=True)
class Manifest:
    """Validated public configuration supplied by a repository."""

    project_name: str
    commands: dict[str, str]
    max_attempts: int = 3
    github: dict[str, bool] | None = None

    @property
    def capabilities(self) -> frozenset[str]:
        return frozenset(self.commands)


def load_manifest(repository: Path, manifest_path: Path | None = None) -> Manifest:
    """Load a project manifest, optionally from an external contract path."""
    path = manifest_path or repository / MANIFEST_NAME
    if not path.is_file():
        raise ManifestError(f"manifest not found: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ManifestError(f"invalid YAML: {error}") from error

    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a mapping")
    if data.get("version") != 1:
        raise ManifestError("version must be 1")

    project = data.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str):
        raise ManifestError("project.name must be a string")

    commands = _read_commands(data.get("commands"))
    retry = data.get("retry", {})
    if retry is None:
        retry = {}
    if not isinstance(retry, dict):
        raise ManifestError("retry must be a mapping")
    max_attempts = retry.get("max_attempts", 3)
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or not 1 <= max_attempts <= 3:
        raise ManifestError("max_attempts must be between 1 and 3")

    github = data.get("github", {})
    if not isinstance(github, dict):
        raise ManifestError("github must be a mapping")
    github_flags = {key: value for key, value in github.items() if isinstance(key, str) and isinstance(value, bool)}
    return Manifest(project_name=project["name"], commands=commands, max_attempts=max_attempts, github=github_flags)


def _read_commands(value: Any) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ManifestError("commands must be a mapping")

    commands: dict[str, str] = {}
    for name, command in value.items():
        if name not in SUPPORTED_COMMANDS:
            continue
        if not isinstance(command, str) or not command.strip():
            raise ManifestError(f"commands.{name} must be a non-empty string")
        commands[name] = command
    return commands
