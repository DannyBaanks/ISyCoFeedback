import importlib.util
from pathlib import Path

from isycofeedback.receipts import create_receipt, save_receipt
from isycofeedback.runner import run_command
import pytest


def test_new_product_contains_no_removed_integrations():
    package=Path(__file__).resolve().parents[1]/'src/isycofeedback'
    # Reintroducing a removed integration into runtime source must fail this gate.
    removed=['road'+'star','nut'+'rient','d'+'ws']
    assert not [(str(p),word) for p in package.rglob('*.py')
                for word in removed if word in p.read_text().lower()]


def test_unknown_delivery_is_never_acknowledged():
    assert importlib.util.find_spec('isycofeedback.operations')
    from isycofeedback.operations.domain import ActionResult, ActionStatus
    result=ActionResult('action','provider',None,ActionStatus.ACKNOWLEDGED,
                        True,None,None,None,None,delivery='UNKNOWN')
    assert not result.recipient_acknowledged()


def test_external_anchor_detects_truncated_command_history(tmp_path):
    from isycofeedback.documents.ledger import Ledger, verify_ledger
    save_receipt(tmp_path,create_receipt('test',run_command('true',tmp_path)))
    save_receipt(tmp_path,create_receipt('test',run_command('true',tmp_path)))
    ledger=tmp_path/'.isycofeedback/ledger.jsonl'
    head=Ledger(ledger).head()
    ledger.write_text(ledger.read_text().splitlines()[0]+'\n')
    assert verify_ledger(ledger)[0]
    assert not verify_ledger(ledger,expected_head=head)[0]


def test_invalid_receipt_id_creates_no_external_directories(tmp_path):
    from isycofeedback.receipts import seal_receipt
    receipt=create_receipt('test',run_command('true',tmp_path))
    receipt['run_id']='../../outside/subdir/item'
    with pytest.raises(ValueError, match='identity'):
        save_receipt(tmp_path,seal_receipt(receipt))
    assert not (tmp_path/'outside').exists()


def test_timeout_stops_child_before_it_can_write(tmp_path):
    import os
    import sys
    import time
    if os.name != 'posix':
        pytest.skip('POSIX process-group regression')
    (tmp_path/'delayed.py').write_text("import time\nfrom pathlib import Path\ntime.sleep(.3)\nPath('late-write').write_text('bad')\n")
    result=run_command(f'"{sys.executable}" delayed.py',tmp_path,timeout_seconds=.03)
    assert result.verdict == 'TIMEOUT'
    time.sleep(.4)
    assert not (tmp_path/'late-write').exists()
