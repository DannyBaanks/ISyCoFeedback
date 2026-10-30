import importlib.util
import json
import shlex
import sys

import pytest


def workflow_type():
    assert importlib.util.find_spec('isycofeedback.workflow'), 'unified workflow is missing'
    from isycofeedback.workflow import Workflow
    return Workflow


def command():
    return f'{shlex.quote(sys.executable)} -c "from pathlib import Path; raise SystemExit(0 if Path(\'value.txt\').read_text() == \'fixed\' else 1)"'


def patch(path='value.txt'):
    return [{'path': path, 'old_content': 'broken', 'new_content': 'fixed'}]


def test_repair_runs_original_command_and_seals_receipt(tmp_path):
    Workflow = workflow_type()
    (tmp_path/'value.txt').write_text('broken')
    result = Workflow(tmp_path).run(command(), run_id='repair-1', allowed_paths=('value.txt',),
                                   provider=lambda attempt, failure: patch())
    assert result.verdict == 'PASS'
    assert result.attempts == 2
    from isycofeedback.receipts import verify_receipt
    receipt = json.loads(result.receipt_path.read_text())
    assert verify_receipt(receipt)[0]
    receipt['result']['exit_code'] = 99
    assert not verify_receipt(receipt)[0]


def test_denied_patch_cannot_change_files(tmp_path):
    Workflow = workflow_type()
    (tmp_path/'value.txt').write_text('broken')
    (tmp_path/'policy.txt').write_text('broken')
    result = Workflow(tmp_path).run(command(), run_id='deny-1', allowed_paths=('value.txt',),
                                   provider=lambda attempt, failure: patch('policy.txt'))
    assert result.verdict == 'DENIED'
    assert (tmp_path/'policy.txt').read_text() == 'broken'
    assert (tmp_path/'value.txt').read_text() == 'broken'


def test_attempt_budget_survives_reopening(tmp_path):
    Workflow = workflow_type()
    counter = f'{shlex.quote(sys.executable)} -c "from pathlib import Path; p=Path(\'count\'); p.write_text(p.read_text()+\'x\' if p.exists() else \'x\'); raise SystemExit(1)"'
    first = Workflow(tmp_path).run(counter, run_id='budget', max_attempts=2)
    second = Workflow(tmp_path).run(counter, run_id='budget', max_attempts=2)
    assert first.verdict == second.verdict == 'REPAIR_EXHAUSTED'
    assert first.attempts == second.attempts == 2
    assert (tmp_path/'count').read_text() == 'xx'


def test_reusing_identity_with_different_command_is_rejected(tmp_path):
    Workflow = workflow_type()
    Workflow(tmp_path).run('true', run_id='same')
    with pytest.raises(ValueError, match='contract'):
        Workflow(tmp_path).run('false', run_id='same')


def test_symlink_is_denied_even_when_target_is_inside_repository(tmp_path):
    Workflow = workflow_type()
    (tmp_path/'value.txt').write_text('broken')
    (tmp_path/'alias.txt').symlink_to(tmp_path/'value.txt')
    result = Workflow(tmp_path).run(command(), run_id='link', allowed_paths=('alias.txt',),
                                   provider=lambda attempt, failure: patch('alias.txt'))
    assert result.verdict == 'DENIED'
    assert (tmp_path/'value.txt').read_text() == 'broken'


def test_document_api_is_available_without_an_external_provider():
    assert importlib.util.find_spec('isycofeedback.documents'), 'document core is missing'
    from isycofeedback.documents.pipeline import Document, DocumentPipeline, Extraction, FieldValue
    from isycofeedback.documents.validation import FieldConfidencePolicy

    class Extractor:
        name = 'test-normalizer'
        def extract(self, document):
            return Extraction({'result': FieldValue('ok', None, {'source': 'test'})}, None)

    class Reject:
        def review(self, extraction):
            return False

    result = DocumentPipeline(Extractor(), Reject(), rules=(FieldConfidencePolicy(('result',), .8),)).run(
        Document(b'input', 'sample.txt', 'text/plain'))
    assert result.status == 'REJECTED'
    assert result.evidence.verify()[0]


def test_unknown_run_is_not_reexecuted(tmp_path):
    Workflow = workflow_type()
    from isycofeedback.workflow_store import WorkflowStore
    store = WorkflowStore(tmp_path/'.isycofeedback/workflows.db')
    contract = Workflow.contract(tmp_path, 'touch should-not-exist', 3, ())
    store.begin('interrupted', contract)
    store.reserve('interrupted')
    store.close()
    workflow = Workflow(tmp_path)
    assert workflow.recover() == ['interrupted']
    result = workflow.run('touch should-not-exist', run_id='interrupted')
    assert result.verdict == 'UNKNOWN'
    assert result.attempts == 1
    assert not (tmp_path/'should-not-exist').exists()


def test_completed_run_with_missing_evidence_cannot_report_pass(tmp_path):
    Workflow = workflow_type()
    result=Workflow(tmp_path).run('true',run_id='replay')
    result.receipt_path.unlink()
    repeated=Workflow(tmp_path).run('true',run_id='replay')
    assert repeated.verdict == 'INVALID_EVIDENCE'
    assert repeated.attempts == 1


def test_unsuccessful_repair_restores_original_file(tmp_path):
    Workflow = workflow_type()
    (tmp_path/'value.txt').write_text('broken')
    result=Workflow(tmp_path).run(command(),run_id='rollback',max_attempts=2,
        allowed_paths=('value.txt',),provider=lambda attempt,failure:[
            {'path':'value.txt','old_content':'broken','new_content':'still-broken'}])
    assert result.verdict == 'REPAIR_EXHAUSTED'
    assert (tmp_path/'value.txt').read_text() == 'broken'
