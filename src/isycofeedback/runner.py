"""Execute commands declared by a repository and capture their evidence."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import time


@dataclass(frozen=True)
class CommandResult:
    command: str
    cwd: str
    exit_code: int | None
    stdout: str
    stderr: str
    started_at: str
    ended_at: str
    duration_ms: int
    timed_out: bool
    verdict: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_command(command: str, cwd: Path, timeout_seconds: float = 60.0) -> CommandResult:
    """Run one declared command with a hard timeout and captured streams."""
    started = datetime.now(timezone.utc)
    start_clock = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as error:
        exit_code = None
        stdout = _as_text(error.stdout)
        stderr = _as_text(error.stderr)
        timed_out = True

    ended = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - start_clock) * 1000)
    return CommandResult(
        command=command,
        cwd=str(cwd),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        started_at=started.isoformat(),
        ended_at=ended.isoformat(),
        duration_ms=duration_ms,
        timed_out=timed_out,
        verdict="TIMEOUT" if timed_out else ("PASS" if exit_code == 0 else "FAIL"),
    )


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value
