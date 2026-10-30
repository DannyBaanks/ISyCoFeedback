"""A real local verification cycle driven by explicit synthetic patch proposals."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from .audit import audit_evidence
from .receipts import verify_receipt
from .workflow import Workflow


def _demo(root: Path) -> int:
    root.mkdir(parents=True, exist_ok=True)
    (root/'value.txt').write_text('broken', encoding='utf-8')
    (root/'check.py').write_text("from pathlib import Path\nraise SystemExit(0 if Path('value.txt').read_text() == 'fixed' else 1)\n", encoding='utf-8')
    command = f'"{sys.executable}" check.py'
    def proposal(path):
        return lambda attempt, failure: [{'path': path, 'old_content': 'broken', 'new_content': 'fixed'}]

    workflow = Workflow(root)
    repaired = workflow.run(command, run_id='demo-repair', allowed_paths=('value.txt',), provider=proposal('value.txt'))
    print(f'REPAIR {repaired.verdict} ({repaired.attempts} verifications; fixed proposal, no AI)')
    (root/'value.txt').write_text('broken', encoding='utf-8')
    denied = workflow.run(command, run_id='demo-denied', allowed_paths=('value.txt',), provider=proposal('check.py'))
    print(f'SCOPE {denied.verdict}')
    exhausted = workflow.run(command, run_id='demo-exhausted')
    print(f'BUDGET {exhausted.verdict} ({exhausted.attempts} verifications)')
    valid, _, head = audit_evidence(root)
    print(f'LEDGER {"VALID" if valid else "INVALID"}; retain head externally: {head}')
    receipt = json.loads(repaired.receipt_path.read_text(encoding='utf-8'))
    receipt['result']['exit_code'] = 99
    tampered = not verify_receipt(receipt)[0]
    print(f'TAMPER {"INVALID" if tampered else "VALID"}')
    return 0 if (repaired.verdict, denied.verdict, exhausted.verdict, valid, tampered) == (
        'PASS', 'DENIED', 'REPAIR_EXHAUSTED', True, True) else 1


def run_demo(output: Path | None = None) -> int:
    if output is not None:
        if output.exists() and any(output.iterdir()):
            raise ValueError('demo output directory must be new or empty')
        return _demo(output)
    with TemporaryDirectory(prefix='isycofeedback-demo-') as directory:
        return _demo(Path(directory))
