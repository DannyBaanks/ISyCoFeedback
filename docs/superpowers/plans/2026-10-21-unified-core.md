# Unified core implementation plan

**Goal:** Merge the three owned projects into a usable local ISyCoFeedback core.

**Architecture:** Import generic document and operational modules under one namespace; connect their evidence and persistence to command/repair workflows. Keep original repositories intact except the requested missing MIT license.

**Tech stack:** Python >=3.11, stdlib SQLite, PyYAML; optional pypdf.

**Spec:** ../specs/2026-10-21-unified-core-design.md

## Constraints and review focus

No vendor/customer SDKs or datasets. No network during tests. Check stale patches, symlink/path escapes, subprocess interruption, replay/identity mismatch, tampered/truncated receipts and secret persistence. No claims of live Duo or deployment.

## Tasks (native execution in this session)

- [x] Import generic modules and their behavioral regression tests; rename namespaces/schema/default storage and remove excluded integration code.
- [x] Add workflow integration tests before implementation: real repair, DENY before write, persistent attempts, interrupted recovery and evidence tamper detection.
- [x] Implement bounded workflow and durable attempt reservation, sealed receipts and chained evidence. Connect existing CLI execution and add repair/history/recovery/verification.
- [x] Replace product README with coherent usage, add MIT/provenance and CI. Preserve legacy source identity in provenance only.
- [x] Run the whole suite in an offline sandbox, demo positive and negative outcomes, verify packaging and inspect final diff.
