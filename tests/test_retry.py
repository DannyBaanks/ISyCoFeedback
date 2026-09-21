import sys
from pathlib import Path

from isycofeedback.retry import retry_command


def _python(code: str) -> str:
    return f'"{sys.executable}" -c "{code}"'


def test_retry_stops_after_exactly_three_failures(tmp_path: Path) -> None:
    result = retry_command(_python("raise SystemExit(2)"), tmp_path)

    assert len(result.attempts) == 3
    assert result.final_verdict == "REPAIR_EXHAUSTED"


def test_retry_stops_early_when_command_passes(tmp_path: Path) -> None:
    marker = tmp_path / "attempt"
    code = f"from pathlib import Path; p=Path(r'{marker}'); n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1)); raise SystemExit(0 if n >= 1 else 1)"

    result = retry_command(_python(code), tmp_path)

    assert len(result.attempts) == 2
    assert result.final_verdict == "PASS"
