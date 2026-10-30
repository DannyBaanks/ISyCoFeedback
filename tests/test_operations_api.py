from isycofeedback.operations.channels import RecordingChannel
from isycofeedback.operations.domain import make_event, SentinelVerdict, LeaseState
from isycofeedback.operations.evidence import make_receipt, verify_receipt
from isycofeedback.operations.pipeline import FixedClock, run_ack_lease


def event():
    return make_event(schema_version='operational-event/1',source='example-ci',
        source_event_type='review-required',source_ref='pipeline-1',entity_type='review',
        entity_id='review-1',observed_at='2026-10-21T12:00:00Z',
        payload={'ack_due_at':'2026-10-21T12:01:00Z','contact_ref':'reviewer-fixture'})


def test_denied_operation_never_calls_channel():
    channel=RecordingChannel()
    result=run_ack_lease(event(),FixedClock('2026-10-21T12:02:00Z'),channel,
                         {'communication_allowed':False})
    assert result['verdict'] is SentinelVerdict.BLOCKED
    assert not channel.requests


def test_recording_channel_is_explicit_and_receipt_detects_mutation():
    channel=RecordingChannel()
    result=run_ack_lease(event(),FixedClock('2026-10-21T12:02:00Z'),channel,
                         {'communication_allowed':True,'channel':'recording'})
    assert result['lease'].state is LeaseState.SATISFIED
    assert len(channel.requests) == 1
    receipt=make_receipt(result)
    assert verify_receipt(receipt)[0]
    receipt['components']['result']['acknowledged']=False
    assert not verify_receipt(receipt)[0]
