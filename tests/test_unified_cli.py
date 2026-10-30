import json
import sys

from isycofeedback.cli import main


def manifest(path, command):
    path.joinpath('.isycofeedback.yml').write_text(
        f'version: 1\nproject:\n  name: example\ncommands:\n  test: >-\n    {command}\nretry:\n  max_attempts: 3\n')


def test_repair_cli_rechecks_the_manifest_command(tmp_path, capsys):
    (tmp_path/'value.txt').write_text('broken')
    (tmp_path/'check.py').write_text("from pathlib import Path\nraise SystemExit(0 if Path('value.txt').read_text() == 'fixed' else 1)\n")
    manifest(tmp_path, f'"{sys.executable}" check.py')
    proposal = tmp_path/'proposal.json'
    proposal.write_text(json.dumps([{'path':'value.txt','old_content':'broken','new_content':'fixed'}]))
    assert main(['repair','--path',str(tmp_path),'--patch-file',str(proposal),'--allow','value.txt','--run-id','cli-repair']) == 0
    assert 'PASS' in capsys.readouterr().out
    assert main(['audit','--path',str(tmp_path)]) == 0
    assert 'VALID' in capsys.readouterr().out
    assert main(['history','--path',str(tmp_path)]) == 0
    assert 'cli-repair' in capsys.readouterr().out


def test_audit_rejects_a_changed_receipt(tmp_path, capsys):
    manifest(tmp_path, f'"{sys.executable}" -c "print(1)"')
    assert main(['test','--path',str(tmp_path)]) == 0
    receipt = next((tmp_path/'.isycofeedback/receipts').glob('*.json'))
    data=json.loads(receipt.read_text());data['result']['exit_code']=99
    receipt.write_text(json.dumps(data))
    capsys.readouterr()
    assert main(['audit','--path',str(tmp_path)]) == 1
    assert 'INVALID' in capsys.readouterr().out


def test_retry_reusing_run_identity_does_not_reset_budget(tmp_path, capsys):
    manifest(tmp_path, f'"{sys.executable}" -c "raise SystemExit(1)"')
    assert main(['retry','--path',str(tmp_path),'--run-id','bounded']) == 1
    assert main(['retry','--path',str(tmp_path),'--run-id','bounded']) == 1
    assert len(list((tmp_path/'.isycofeedback/receipts').glob('*.json'))) == 3


def test_demo_exercises_real_verification_and_denial(capsys):
    assert main(['demo']) == 0
    output=capsys.readouterr().out
    for status in ['PASS','DENIED','REPAIR_EXHAUSTED','INVALID']:
        assert status in output
