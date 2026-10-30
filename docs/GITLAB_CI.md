# GitLab CI and Duo trigger smoke check

The normal `verify` job installs the Python development dependencies, runs the
test suite and both deterministic demos, and builds a wheel. In parallel,
`verify_web` uses `npm ci` and builds the PWA from its lockfile. Neither job
calls an AI provider or mutates project files.

The `duo_smoke_failure` job is excluded from normal branch and merge request
pipelines. To test the GitLab-managed `Fix CI/CD Pipeline` trigger deliberately:

1. Start **Run pipeline** from the GitLab project UI.
2. Set the pipeline variable `GITBACK_DUO_SMOKE` to `1`.
3. Wait for `verify` to pass. The following smoke job then fails intentionally
   and makes the pipeline fail, which is the event configured on the Showcase
   trigger.
4. Inspect the Duo session, its proposed changes or merge request, and the
   resulting pipeline before treating the integration as verified.

Do not add `GITBACK_DUO_SMOKE=1` to project, group, or instance variables. The
smoke job is meant to run only in a deliberate web-started test pipeline. The
failure itself is not a repair test; it only verifies that a failed pipeline
reaches the flow. A real failing test and independently verified repair are
still required for the product demo.
