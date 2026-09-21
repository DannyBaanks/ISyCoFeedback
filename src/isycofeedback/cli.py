"""Command-line entry point for ISyCoFeedback."""

import argparse
from pathlib import Path
import sys

from isycofeedback.diagnostics import diagnose
from isycofeedback.manifest import MANIFEST_NAME, ManifestError, load_manifest


CAPABILITY_ORDER = (
    ("run", "RUN"),
    ("test", "TEST"),
    ("verify", "VERIFY"),
    ("reproduce", "REPRODUCE"),
    ("retry", "RETRY"),
    ("repair", "REPAIR"),
    ("issue", "ISSUE"),
    ("fork", "FORK"),
    ("pr", "PR"),
)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        _print_menu()
        return 0
    if args.command == "init":
        return _init(args.path, args.name)
    if args.command == "doctor":
        return _doctor(args.path)
    if args.command == "capabilities":
        return _capabilities(args.path)
    parser.error(f"unsupported command: {args.command}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="isycofeedback")
    subparsers = parser.add_subparsers(dest="command")
    for name in ("doctor", "capabilities"):
        command = subparsers.add_parser(name)
        command.add_argument("--path", type=Path, default=Path.cwd())
    init = subparsers.add_parser("init")
    init.add_argument("--path", type=Path, default=Path.cwd())
    init.add_argument("--name")
    return parser


def _init(repository: Path, name: str | None) -> int:
    path = repository / MANIFEST_NAME
    if path.exists():
        print(f"Exists: {path}")
        return 0
    project_name = name or repository.name
    path.write_text(
        f"version: 1\nproject:\n  name: {project_name}\ncommands: {{}}\nretry:\n  max_attempts: 3\n",
        encoding="utf-8",
    )
    print(f"Created: {path}")
    return 0


def _doctor(repository: Path) -> int:
    for key, value in diagnose(repository).items():
        if key == "manifest_error":
            print(f"MANIFEST_ERROR  {value}")
        elif isinstance(value, list):
            print(f"{key.upper()}  {', '.join(value) or 'NONE'}")
        else:
            print(f"{key.upper()}  {value}")
    return 0


def _capabilities(repository: Path) -> int:
    try:
        manifest = load_manifest(repository)
    except ManifestError as error:
        print(f"CONFIGURATION_FAILURE  {error}")
        return 1
    github = manifest.github or {}
    for key, label in CAPABILITY_ORDER:
        if key == "retry":
            print(f"{label:<12} YES ({manifest.max_attempts})")
            continue
        enabled = key in manifest.commands or github.get({"issue": "issues", "pr": "pull_requests"}.get(key, key), False)
        print(f"{label:<12} {'YES' if enabled else 'NO'}")
    return 0


def _print_menu() -> None:
    print("ISyCoFeedback")
    print("─────────────────────────")
    print("\n[1] Run\n[2] Test\n[3] Verify\n[4] Retry\n[5] Diagnose\n[6] Reproduce\n[7] Repair\n[8] Save evidence\n[9] Open issue\n[F] Fork\n[P] Pull request\n[Q] Quit")


if __name__ == "__main__":
    sys.exit(main())
