import sys
from pathlib import Path

from isycofeedback.runner import run_command


def _python(code: str) -> str:
    return f'"{sys.executable}" -c "{code}"'


def test_run_command_captures_cwd_stdout_stderr_and_exit_code(tmp_path: Path) -> None:
    result = run_command(
        _python("import os,sys; print(os.getcwd()); print('warning', file=sys.stderr); sys.exit(7)"),
        cwd=tmp_path,
    )

    assert result.exit_code == 7
    assert str(tmp_path) in result.stdout
    assert result.stderr.strip() == "warning"
    assert result.cwd == str(tmp_path)
    assert result.verdict == "FAIL"


def test_run_command_reports_timeout(tmp_path: Path) -> None:
    result = run_command(_python("import time; time.sleep(0.2)"), cwd=tmp_path, timeout_seconds=0.01)

    assert result.timed_out is True
    assert result.verdict == "TIMEOUT"

