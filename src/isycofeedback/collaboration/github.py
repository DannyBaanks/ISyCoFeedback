"""GitHub payload generation; remote mutation is deliberately out of scope here."""

from typing import Any


def build_issue_payload(project: str, git_head: str, receipt: dict[str, Any]) -> dict[str, str]:
    result = receipt.get("result", {})
    return {
        "title": f"Failure in {project}",
        "body": _body(
            project,
            git_head,
            receipt,
            "## Reproduction\n```\n{command}\n```\n\n## Failure\n{stderr}\n\n## Verdict\n{verdict}",
        ),
    }


def build_pr_payload(project: str, git_head: str, receipt: dict[str, Any], verified: bool) -> dict[str, object]:
    result = receipt.get("result", {})
    status = "VERIFIED" if verified else "UNVERIFIED"
    return {
        "title": f"Fix: {project} failure",
        "body": _body(
            project,
            git_head,
            receipt,
            f"## Validation\n{status}\n\n## Command\n```\n{{command}}\n```\n\n## Result\n{{stderr}}",
        ),
        "dry_run": True,
    }


def _body(project: str, git_head: str, receipt: dict[str, Any], template: str) -> str:
    result = receipt.get("result", {})
    details = template.format(
        command=result.get("command", "unknown"),
        stderr=result.get("stderr", ""),
        verdict=result.get("verdict", "UNKNOWN"),
    )
    return f"# {project}\n\nCommit: `{git_head}`\nRun ID: `{receipt.get('run_id', 'unknown')}`\n\n{details}\n"
