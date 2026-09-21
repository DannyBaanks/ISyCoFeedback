from isycofeedback.collaboration.github import build_issue_payload, build_pr_payload


def _receipt() -> dict[str, object]:
    return {
        "run_id": "run-123",
        "action": "test",
        "result": {
            "command": "pytest -q",
            "cwd": "/tmp/project",
            "exit_code": 1,
            "stderr": "assertion failed",
            "verdict": "FAIL",
        },
    }


def test_issue_payload_contains_reproduction_and_run_id() -> None:
    payload = build_issue_payload("Fixture", "abc123", _receipt())

    assert payload["title"] == "Failure in Fixture"
    assert "pytest -q" in payload["body"]
    assert "run-123" in payload["body"]
    assert "assertion failed" in payload["body"]


def test_pr_payload_marks_unverified_changes_explicitly() -> None:
    payload = build_pr_payload("Fixture", "abc123", _receipt(), verified=False)

    assert payload["title"] == "Fix: Fixture failure"
    assert "UNVERIFIED" in payload["body"]
    assert payload["dry_run"] is True
