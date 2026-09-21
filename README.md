# ✨ ISyCoFeedback

## When a project breaks, it should leave you with a way forward.

ISyCoFeedback is a friendly command-line companion for any repository.

It helps you:

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
> Chrome-to-Fox repository through an external local contract. The project is
> young, but the core promise is working.

---

## The idea in one picture

```text
┌──────────────────────┐
│      Your project    │
│  any language, any   │
│  build, any workflow │
└──────────┬───────────┘
           │  a tiny local contract
           ▼
┌──────────────────────┐
│   ISyCoFeedback      │
│                      │
│  run • test • verify │
│  retry • repair     │
│  evidence • share   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  A useful next step  │
│  not just a red mark │
└──────────────────────┘
```

Your project keeps ownership of its own commands. ISyCoFeedback simply gives
those commands a consistent, human-friendly surface.

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

The important part is not the red output. It is that the failure is now
captured, reproducible, and ready to be understood by another person.

## Why people use it

### 🧭 Less guessing

You can see the command, the folder, the timing, the output, and the exact
result of every attempt.

### 🧱 No endless loops

The default repair budget is three attempts. Then it stops and shows you the
next useful actions.

### 🧾 No “trust me” success

A project is only marked `PASS` when its real verification command passes.

### 🛟 Better handoffs

When something fails, the saved evidence can become the starting point for an
issue, a fork, or a pull request.

### 🌍 Works with your project

Python, JavaScript, Rust, shell scripts, build tools, or something wonderfully
strange — the project defines its own commands.

## Try it in two minutes

From a repository you want to give a feedback surface to:

```console
$ isycofeedback init
$ isycofeedback doctor
$ isycofeedback capabilities
$ isycofeedback test
```

The first command creates a small `.isycofeedback.yml` file. It does not try
to guess your project’s meaning or silently invent a workflow.

Example:

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
```

That is the whole idea: your repository declares the buttons; ISyCoFeedback
makes them consistent.

## Real-world proof: Chrome-to-Fox

ISyCoFeedback has already run the real Chrome-to-Fox test suite with:

```text
GIT  PASS
MANIFEST  PASS
PROJECT  Chrome-to-Fox
TEST  PASS
```

The evidence was stored outside the consumer repository, so the consumer was
not modified during the demonstration.

It also caught a real behavior difference: Chrome-to-Fox’s analyzer printed
an empty error list while returning a failure exit code. ISyCoFeedback kept
that result as `FAIL` instead of pretending the text meant success.

See the full, honest transcript in
[docs/DEMO-CHROME-TO-FOX.md](docs/DEMO-CHROME-TO-FOX.md).

## What happens to your private data?

- Project configuration contains commands, not credentials.
- Receipts are local and ignored by Git by default.
- API keys are never written into project manifests or receipts.
- Optional AI repair receives a bounded failure envelope, not your whole
  repository by default.
- GitHub actions are currently prepared as dry-runs before any remote change.

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
| Live provider request | ⚠️ Needs an unsandboxed integration run |

## The promise

ISyCoFeedback does not try to become your build system, your project manager,
or your repository’s brain.

It is the small layer that makes failure understandable and contribution
possible.

## Development

```console
$ PYTHONPATH=src py -m pytest -q
27 passed
```

The product roadmap lives in [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT. See [LICENSE](LICENSE).
