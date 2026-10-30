# ISyCoFeedback unified core

Danny requested a local merger of his Feedback, operational lifecycle and document-evidence projects, with MIT licensing and removal of vendor/customer coupling. The existing Feedback repository remains the canonical project. Source repositories remain recoverable; remote publication is a separate action.

## Product and scope

One Python package and CLI: execute a declared repository command, optionally apply a bounded proposed patch, verify the original command, persist attempts, and produce independently checkable evidence. Preserve generic document validation/review and operational action/persistence APIs as library modules. No customer datasets, logistics adapters, telephony, cloud sync, vendor extraction SDK, old GUI, or previous contest branding in the resulting product.

The local merge does not implement or claim a real GitLab Duo flow, public deployment or automatic general-purpose AI repair. A patch provider interface and a JSON patch CLI make that next integration concrete. Original creation dates/history remain disclosed.

## Architecture

- Existing runner/manifest/patch components remain compatible.
- `documents`: generic DocumentPipeline, validation rules, evidence graph, ledger, offline extraction and report rendering. MIT source notices are preserved in LICENSE/PROVENANCE.
- `operations`: generic events, acknowledgement policy, action contracts, durable lifecycle, memory/SQLite persistence and receipt verification. Remove customer-specific policies and all external channels.
- `workflow`: orchestrates real commands and patch providers; persistent attempt reservation before execution, stable run identity, allowlisted paths and evidence records. SQLite durability builds on the imported backend. A restart never silently retries an in-flight command.
- Existing receipts gain an integrity seal and feed the imported ledger. A retained expected ledger head can detect truncation. Hashes do not establish identity or make evidence immutable against its owner.
- CLI retains existing commands and adds repair, workflow history/recovery, evidence verification and a synthetic demo.

## Constraints and acceptance

Python >=3.11 (required by imported code), PyYAML only for base runtime; optional PDF extraction via pypdf. New schema names belong to ISyCoFeedback; legacy source data is not migrated silently. No network or home access in tests. No product reference to the two removed organizations, including imported comments and test fixtures.

Meaningful tests: existing suite; adapted document core and operational persistence regressions; successful repair checked by original command; denied path writes nothing; attempt budget survives reopening; interrupted work is UNKNOWN; altered evidence fails; retained ledger head detects truncation; secrets absent from persisted records. Packaging and CLI demo must also work.
