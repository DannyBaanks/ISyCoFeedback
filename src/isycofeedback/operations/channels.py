"""Explicit local recording channel; no external delivery is implied."""
from .canonical import stable_id
from .domain import ActionRequest, ActionResult, ActionStatus

class RecordingChannel:
    identity = "mock-channel/1"
    def __init__(self) -> None:
        self.requests: list[ActionRequest] = []
    def send(self, request: ActionRequest) -> ActionResult:
        self.requests.append(request)
        return ActionResult(request.action_id, self.identity, stable_id("mock", request.action_id), ActionStatus.ACKNOWLEDGED,
                            True, "received", None, None, None,
                            provider_accepted=True, delivery="KNOWN", reached_ringing="TRUE",
                            terminal_cause="ACKNOWLEDGED", retry_safe="FALSE")


