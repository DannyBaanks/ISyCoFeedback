"""Read-only environment checks for the feedback CLI."""

from pathlib import Path
import shutil
import subprocess

from isycofeedback.manifest import ManifestError, load_manifest


def diagnose(repository: Path, manifest_path: Path | None = None) -> dict[str, object]:
    """Return a machine-readable doctor report without exposing credentials."""
    report: dict[str, object] = {
        "git": "PASS" if _is_git_repository(repository) else "NO",
        "gh": "AVAILABLE" if shutil.which("gh") else "UNAVAILABLE",
        "python": "AVAILABLE",
    }
    try:
        manifest = load_manifest(repository, manifest_path)
    except ManifestError as error:
        report["manifest"] = "FAIL"
        report["manifest_error"] = str(error)
        report["commands"] = []
    else:
        report["manifest"] = "PASS"
        report["project"] = manifest.project_name
        report["commands"] = sorted(manifest.commands)
    return report


def _is_git_repository(repository: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"
