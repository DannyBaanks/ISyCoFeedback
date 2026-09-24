# ✨ ISyCoFeedback

<p align="center">
  <strong>When a project breaks, it should leave you with a way forward.</strong>
</p>

<p align="center">
  <a href="README.md">🇪🇸 Versión en español</a>
</p>

ISyCoFeedback is a friendly command-line companion for any repository.

```text
run it       →  see what happened
test it      →  know if it really works
try again    →  stop after three honest attempts
save proof   →  keep the useful details
ask for help →  prepare an issue or contribution
```

No magic “fixed!” messages. No endless retry loops. No lost context.

Just a calm, repeatable path from **“it broke”** to **“here is what we know.”**

> **Status:** `0.1.0 ALPHA` — already demonstrated against the real
> Chrome-to-Fox repository through an external local contract.

## The idea in one picture

```text
Your project  →  a tiny local contract  →  ISyCoFeedback  →  a useful next step
```

Your project keeps ownership of its commands. ISyCoFeedback gives those
commands a consistent, human-friendly surface.

## A tiny demo

```console
$ isycofeedback test
TEST  FAIL

$ isycofeedback retry
ATTEMPT 1/3  FAIL
ATTEMPT 2/3  FAIL
ATTEMPT 3/3  FAIL

Repair budget exhausted.
Evidence saved.
Next steps: issue • fork • pull request
```

The failure is now captured, reproducible, and ready to be understood by
another person.

## Try it in two minutes

```console
$ isycofeedback init
$ isycofeedback doctor
$ isycofeedback capabilities
$ isycofeedback test
```

The first command creates a small `.isycofeedback.yml` file without silently
inventing a workflow.

```yaml
version: 1

project:
  name: My Project

commands:
  test: "your test command"
  verify: "your verification command"
  reproduce: "your reproduction command"

retry:
  max_attempts: 3

secrets:            # environment variable NAMES only, never values
  - GITHUB_TOKEN
```

**Secrets.** `secrets:` lists environment variable names, not values, so the
manifest never holds a secret. At run time ISyCoFeedback reads those values
from the environment and replaces them with `[REDACTED]` in receipts and in the
stderr it prints. Receipts live in `.isycofeedback/`, which is created with its
own `.gitignore` so they never ride along in a commit.

## Real-world proof: Chrome-to-Fox

ISyCoFeedback has run the real Chrome-to-Fox test suite with:

```text
GIT  PASS
MANIFEST  PASS
PROJECT  Chrome-to-Fox
TEST  PASS
```

See the full transcript in
[docs/DEMO-CHROME-TO-FOX.md](docs/DEMO-CHROME-TO-FOX.md).

## Privacy and honesty

- Project configuration contains commands, not credentials.
- Receipts are local and ignored by Git by default.
- API keys are never written into project manifests or receipts.
- A project is marked `PASS` only when its real verification command passes.
- GitHub actions are prepared as dry-runs before any remote change.

## What is ready today?

| Experience | Status |
|---|---|
| `init`, `doctor`, `capabilities` | ✅ Working |
| Run, test, verify, reproduce | ✅ Working |
| Receipts and evidence | ✅ Working |
| Three-attempt retry boundary | ✅ Working |
| Patch-based fake repair | ✅ Working |
| OpenAI-compatible request builder | ✅ Working |
| GitHub issue / PR dry-run | ✅ Working |
| Firefox browser demonstration | 🚧 Next milestone |

## Development

```console
$ PYTHONPATH=src py -m pytest -q
27 passed
```

The roadmap lives in [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT. See [LICENSE](LICENSE).
