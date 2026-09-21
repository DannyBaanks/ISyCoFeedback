"""Bounded, patch-oriented repair orchestration."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from isycofeedback.runner import CommandResult, run_command


PatchProvider = Callable[[int, CommandResult], list[dict[str, str]]]


@dataclass(frozen=True)
class RepairResult:
    attempts: tuple[CommandResult, ...]
    final_verdict: str


def apply_patch_files(repository: Path, patches: list[dict[str, str]]) -> list[Path]:
    """Apply exact-content patches that remain inside *repository*."""
    changed: list[Path] = []
    for patch in patches:
        relative = Path(patch["path"])
        target = (repository / relative).resolve()
        root = repository.resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"patch path outside repository: {relative}")
        if not target.is_file():
            raise ValueError(f"patch target not found: {relative}")
        current = target.read_text(encoding="utf-8")
        if current != patch["old_content"]:
            raise ValueError(f"patch precondition failed: {relative}")
        target.write_text(patch["new_content"], encoding="utf-8")
        changed.append(relative)
    return changed


def repair_command(
    command: str,
    cwd: Path,
    provider: PatchProvider,
    max_attempts: int = 3,
    timeout_seconds: float = 60.0,
) -> RepairResult:
    """Verify, request bounded patches, and verify again after each patch."""
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3")

    attempts: list[CommandResult] = []
    result = run_command(command, cwd, timeout_seconds)
    attempts.append(result)
    if result.verdict == "PASS":
        return RepairResult(tuple(attempts), "PASS")

    for attempt in range(1, max_attempts):
        patches = provider(attempt, result)
        apply_patch_files(cwd, patches)
        result = run_command(command, cwd, timeout_seconds)
        attempts.append(result)
        if result.verdict == "PASS":
            return RepairResult(tuple(attempts), "PASS")
    return RepairResult(tuple(attempts), "REPAIR_EXHAUSTED")
