# ISyCoFeedback MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the smallest standalone CLI that can execute a repository contract, record evidence, enforce three attempts, and demonstrate the flow against Chrome-to-Fox.

**Architecture:** A Python package exposes a thin CLI over focused modules for manifest loading, command execution, receipts, retry, diagnostics, and dry-run collaboration payloads. The consumer repository owns its commands; the core only executes declared commands and evaluates exit status.

**Tech Stack:** Python 3.10+, `argparse`, standard library JSON/YAML-compatible manifest parser with a small dependency, pytest, subprocess, and filesystem receipts.

**Spec:** `docs/ROADMAP.md`

## Global Constraints

- The project remains repository- and language-agnostic.
- Default retry budget is exactly 3 attempts and never unbounded.
- PASS requires the declared verification command to exit successfully.
- API keys never enter project config, receipts, prompts, stdout, or logs.
- GitHub operations are dry-run first and remain outside the core runner.
- Runtime evidence is local and ignored by default.
- Chrome-to-Fox is a consumer fixture; its unrelated files are not modified.

## Review Focus

- Missing or malformed manifest: reject with a configuration classification; test in manifest task.
- Command timeout and non-zero exit: preserve stdout/stderr and classify failure; test in runner task.
- Four attempts after three failures: impossible by construction; test in retry task.
- Secret-like values in evidence: redact before persistence; test in receipts task.
- Missing external tools such as Firefox or gh: report unavailable capability without false success; test in diagnostics task.

### Task 1: Standalone project and manifest

**Files:**
- Create: `pyproject.toml`
- Create: `src/isycofeedback/__init__.py`
- Create: `src/isycofeedback/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] Write failing tests for valid, missing, malformed, and capability-free manifests.
- [ ] Run `pytest tests/test_manifest.py -q` and confirm collection/code failures.
- [ ] Implement manifest loading and validation with explicit command capabilities.
- [ ] Run the focused tests and then the full suite.
- [ ] Commit as `feat: add repository manifest contract`.

### Task 2: Command runner and receipts

**Files:**
- Create: `src/isycofeedback/runner.py`
- Create: `src/isycofeedback/receipts.py`
- Test: `tests/test_runner.py`
- Test: `tests/test_receipts.py`

- [ ] Write failing tests for cwd preservation, stdout/stderr, exit code, timeout, redaction, and unique run IDs.
- [ ] Run focused tests and confirm failures.
- [ ] Implement bounded subprocess execution and JSON receipts under `.isycofeedback/`.
- [ ] Verify receipts contain no configured secret values.
- [ ] Run the full suite and commit `feat: record command evidence`.

### Task 3: CLI, doctor, capabilities, and init

**Files:**
- Create: `src/isycofeedback/cli.py`
- Create: `src/isycofeedback/diagnostics.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_diagnostics.py`

- [ ] Write failing tests for `init`, `doctor`, `capabilities`, and no-argument menu output.
- [ ] Implement only read-only diagnostics and explicit starter manifest generation.
- [ ] Verify commands in a disposable repository.
- [ ] Commit `feat: add diagnostic CLI surface`.

### Task 4: Retry and verification semantics

**Files:**
- Create: `src/isycofeedback/retry.py`
- Test: `tests/test_retry.py`
- Modify: `src/isycofeedback/cli.py`

- [ ] Write failing tests for exactly three failures, early pass, and preserved attempts.
- [ ] Implement deterministic retry orchestration.
- [ ] Run tests and inspect attempt count in receipts.
- [ ] Commit `feat: enforce bounded retry loop`.

### Task 5: Fixtures and Chrome-to-Fox contract

**Files:**
- Create: `fixtures/pass-repo/.isycofeedback.yml`
- Create: `fixtures/fail-repo/.isycofeedback.yml`
- Create: `tests/test_fixtures.py`
- Create: `examples/chrome-to-fox.isycofeedback.yml`

- [ ] Write tests that run the pass and fail fixtures through the public CLI.
- [ ] Implement the example consumer manifest without editing Chrome-to-Fox.
- [ ] Verify pass output, three-failure output, receipts, and dry-run options.
- [ ] Commit `test: add substrate-independent fixtures`.

### Task 6: Fake repair and OpenAI-compatible provider

**Files:**
- Create: `src/isycofeedback/repair.py`
- Create: `src/isycofeedback/providers/openai_compatible.py`
- Test: `tests/test_repair.py`
- Test: `tests/test_provider.py`

- [ ] Write failing tests for fake patch application, disabled provider, request shape, timeout, and secret exclusion.
- [ ] Implement bounded patch envelopes and provider transport.
- [ ] Verify repair success only after the declared verification passes.
- [ ] Commit `feat: add bounded repair provider`.

### Task 7: GitHub dry-run payloads and final demonstration

**Files:**
- Create: `src/isycofeedback/collaboration/github.py`
- Test: `tests/test_github_dry_run.py`
- Create: `docs/DEMO-CHROME-TO-FOX.md`
- Modify: `README.md`

- [ ] Write failing tests for issue, fork, and PR dry-run payloads.
- [ ] Implement payload generation without remote mutation.
- [ ] Run the complete suite and the documented Chrome-to-Fox demo.
- [ ] Record exact outputs, limitations, hashes, and git status.
- [ ] Commit `docs: document Chrome-to-Fox dogfood`.
