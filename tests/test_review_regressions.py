import os
import sys
import time

import pytest

from isycofeedback.workflow import Workflow
from isycofeedback.operations.persistence.repository import RunRepository
from isycofeedback.operations.persistence.memory import MemoryBackend
from isycofeedback.operations.persistence.sqlite import SQLiteBackend
from isycofeedback.operations.domain import make_event


@pytest.mark.parametrize('boundary',['command','evidence','finish'])
def test_exception_after_patch_restores_source(tmp_path,monkeypatch,boundary):
    import isycofeedback.workflow as module
    (tmp_path/'value.txt').write_text('broken')
    (tmp_path/'check.py').write_text("from pathlib import Path\nraise SystemExit(Path('value.txt').read_text() != 'fixed')\n")
    command=f'"{sys.executable}" check.py'
    target={'command':'run_command','evidence':'save_receipt'}.get(boundary)
    calls=0
    if target:
        original=getattr(module,target)
        def failing(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2:
                raise OSError('simulated boundary failure')
            return original(*args,**kwargs)
        monkeypatch.setattr(module,target,failing)
    else:
        def failing(*args,**kwargs):
            raise OSError('simulated commit failure')
        monkeypatch.setattr(module.WorkflowStore,'finish',failing)
    with pytest.raises(OSError):
        Workflow(tmp_path).run(command,run_id='exception',allowed_paths=('value.txt',),
            provider=lambda attempt,result:[{'path':'value.txt','old_content':'broken','new_content':'fixed'}])
    assert (tmp_path/'value.txt').read_text()=='broken'


def test_truncating_last_run_receipt_and_ledger_cannot_replay_pass(tmp_path):
    Workflow(tmp_path).run('true',run_id='prior')
    result=Workflow(tmp_path).run('true',run_id='last')
    ledger=tmp_path/'.isycofeedback/ledger.jsonl'
    ledger.write_text(ledger.read_text().splitlines()[0]+'\n')
    result.receipt_path.unlink()
    assert Workflow(tmp_path).run('true',run_id='last').verdict=='INVALID_EVIDENCE'


@pytest.mark.parametrize('memory',[True,False])
def test_operational_recovery_preserves_phase_and_marks_terminal(tmp_path,memory):
    backend=MemoryBackend() if memory else SQLiteBackend(tmp_path/'ops.db')
    repo=RunRepository(backend)
    event=make_event(schema_version='operational-event/1',source='test',source_event_type='test',
        source_ref='source',entity_type='test',entity_id='test',observed_at='2026-10-21T12:00:00Z',payload={})
    repo.start_run('interrupted',event,{},source_adapter='test',channel_adapter='test',policy_version='test')
    assert repo.recover_incomplete()[0]['execution_id']=='interrupted'
    repo.mark_recovery('interrupted')
    run=repo.get_run('interrupted')
    assert run['state']=='RECOVERY_REQUIRED'
    assert run['last_demonstrated_phase']=='RUN_STARTED'
    assert not repo.recover_incomplete()
    backend.close()


def test_interrupt_reaps_detached_command(tmp_path,monkeypatch):
    if os.name!='posix':
        pytest.skip('POSIX interrupt regression')
    import isycofeedback.runner as module
    original=module.subprocess.Popen
    processes=[]
    def interrupting(*args,**kwargs):
        process=original(*args,**kwargs)
        def interrupt(*args,**kwargs):
            raise KeyboardInterrupt()
        process.communicate=interrupt
        processes.append(process)
        return process
    monkeypatch.setattr(module.subprocess,'Popen',interrupting)
    (tmp_path/'delayed.py').write_text("import time\nfrom pathlib import Path\ntime.sleep(.25)\nPath('orphan').write_text('bad')\n")
    with pytest.raises(KeyboardInterrupt):
        module.run_command(f'"{sys.executable}" delayed.py',tmp_path)
    time.sleep(.35)
    assert not (tmp_path/'orphan').exists()
    assert processes[0].poll() is not None


def test_document_evidence_binds_validation_policy():
    from isycofeedback.documents.pipeline import Document,DocumentPipeline,Extraction,FieldValue
    from isycofeedback.documents.validation import RequiredFieldsRule
    class Service:
        name='fixed-normalizer'
        def extract(self,document):
            return Extraction({'field':FieldValue('ok',1.,{})},1.)
    class Reviewer:
        def review(self,extraction):
            return True
    document=Document(b'input','example.txt','text/plain')
    first=DocumentPipeline(Service(),Reviewer()).run(document)
    second=DocumentPipeline(Service(),Reviewer(),rules=(RequiredFieldsRule(('field',)),)).run(document)
    assert first.status==second.status=='AUTO_APPROVED'
    assert first.evidence.record_sha256!=second.evidence.record_sha256


@pytest.mark.parametrize('edited_after_crash',[False,True])
def test_crash_recovery_restores_only_unchanged_proposed_content(tmp_path,edited_after_crash):
    from isycofeedback.workflow_store import WorkflowStore
    (tmp_path/'value.txt').write_text('user-change' if edited_after_crash else 'fixed')
    store=WorkflowStore(tmp_path/'.isycofeedback/workflows.db')
    store.begin('crashed',Workflow.contract(tmp_path,'true',3,('value.txt',)))
    store.save_backup('crashed',[{'path':'value.txt','old_content':'broken','new_content':'fixed'}])
    store.close()
    assert Workflow(tmp_path).recover()==['crashed']
    assert (tmp_path/'value.txt').read_text()==('user-change' if edited_after_crash else 'broken')
    if edited_after_crash:
        (tmp_path/'value.txt').write_text('fixed')
        assert Workflow(tmp_path).recover()==['crashed']
        assert (tmp_path/'value.txt').read_text()=='broken'


def test_shared_evidence_recovery_does_not_touch_another_repository(tmp_path):
    from isycofeedback.workflow_store import WorkflowStore
    first=tmp_path/'first';second=tmp_path/'second';evidence=tmp_path/'evidence'
    first.mkdir();second.mkdir()
    (second/'value.txt').write_text('fixed')
    store=WorkflowStore(evidence/'.isycofeedback/workflows.db')
    store.begin('foreign',Workflow.contract(second,'true',3,('value.txt',)))
    store.save_backup('foreign',[{'path':'value.txt','old_content':'broken','new_content':'fixed'}])
    store.close()
    assert Workflow(first,evidence).recover()==[]
    assert (second/'value.txt').read_text()=='fixed'
    assert Workflow(second,evidence).recover()==['foreign']
    assert (second/'value.txt').read_text()=='broken'


def test_recovery_does_not_follow_a_replaced_parent_symlink(tmp_path):
    from isycofeedback.workflow_store import WorkflowStore
    other=tmp_path/'other';other.mkdir();(other/'value.txt').write_text('fixed')
    (tmp_path/'nested').symlink_to(other,target_is_directory=True)
    store=WorkflowStore(tmp_path/'.isycofeedback/workflows.db')
    store.begin('linked',Workflow.contract(tmp_path,'true',3,('nested/value.txt',)))
    store.save_backup('linked',[{'path':'nested/value.txt','old_content':'broken','new_content':'fixed'}])
    store.close()
    assert Workflow(tmp_path).recover()==['linked']
    assert (other/'value.txt').read_text()=='fixed'


def test_configured_secrets_are_never_stored_in_patch_backups(tmp_path):
    secret='secret-for-backup-regression'
    (tmp_path/'source.txt').write_text(secret)
    result=Workflow(tmp_path).run('false',run_id='secret-backup',allowed_paths=('source.txt',),
        secrets=[secret],provider=lambda attempt,result:[
            {'path':'source.txt','old_content':secret,'new_content':'removed'}])
    assert result.verdict=='DENIED'
    for file in (tmp_path/'.isycofeedback').rglob('*'):
        if file.is_file():
            assert secret.encode() not in file.read_bytes()
