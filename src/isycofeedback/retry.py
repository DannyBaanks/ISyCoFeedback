"""Bounded retry orchestration for declared repository commands."""

from dataclasses import dataclass
from pathlib import Path

from isycofeedback.runner import CommandResult, run_command


@dataclass(frozen=True)
class RetryResult:
    attempts: tuple[CommandResult, ...]
    final_verdict: str


def retry_command(
    command: str,
    cwd: Path,
    max_attempts: int = 3,
    timeout_seconds: float = 60.0,
) -> RetryResult:
    """Run a command until it passes or reaches the hard attempt limit."""
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3")

    attempts: list[CommandResult] = []
    for _ in range(max_attempts):
        result = run_command(command, cwd, timeout_seconds)
        attempts.append(result)
        if result.verdict == "PASS":
            return RetryResult(tuple(attempts), "PASS")
    return RetryResult(tuple(attempts), "REPAIR_EXHAUSTED")
