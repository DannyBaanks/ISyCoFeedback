// Synthetic-only fixtures. Replace this module with a validated API adapter in a future integration.
export type RepairStatus = "Awaiting review" | "Verifying" | "Completed";
export const repairs = [
  {
    id: "sample-842",
    repo: "gitback/demo-api",
    branch: "main",
    pipeline: "#842",
    job: "test:unit",
    sha: "8e42bf1",
    status: "Awaiting review" as RepairStatus,
    time: "12 min ago",
    title: "Unit tests fail on empty response",
    summary:
      "A nullable API response reaches the formatter without a guard. The example patch adds a defensive fallback.",
    failure: "Expected status 200, received 500",
    log: "Example log · synthetic\n> test:unit\nFAIL src/handlers.test.ts\nTypeError: Cannot read properties of null (reading “items”)\n  at formatResponse (src/format.ts:42)",
    diff: [
      {
        kind: "ctx",
        text: "export function formatResponse(payload: Payload | null) {",
      },
      { kind: "del", text: "  return payload.items.map(formatItem)" },
      { kind: "add", text: "  if (!payload) return { items: [] }" },
      { kind: "add", text: "  return payload.items.map(formatItem)" },
      { kind: "ctx", text: "}" },
    ],
    tests: [
      ["test:unit", "Passed · sample"],
      ["test:types", "Passed · sample"],
      ["lint", "Passed · sample"],
    ],
    events: [
      ["Pipeline failed", "Sample · test:unit returned exit code 1"],
      ["Duo analysis", "Example diagnosis prepared for review"],
      ["Patch proposed", "Example diff · guard for nullable payload"],
      ["Tests verified", "Sample verification results shown below"],
      ["Human review", "Awaiting your review · no merge is performed"],
    ],
  },
  {
    id: "sample-817",
    repo: "gitback/worker-kit",
    branch: "fix/retry-window",
    pipeline: "#817",
    job: "test:integration",
    sha: "2ac91de",
    status: "Verifying" as RepairStatus,
    time: "Yesterday",
    title: "Retry window boundary mismatch",
    summary:
      "Example repair changes the boundary comparison for retry eligibility.",
    failure: "Expected retry at window edge",
    log: "Example log · synthetic\nFAIL retry-window.test.ts\nExpected: true\nReceived: false",
    diff: [
      { kind: "del", text: "  return elapsed < retryWindow" },
      { kind: "add", text: "  return elapsed <= retryWindow" },
    ],
    tests: [
      ["test:integration", "Running · sample"],
      ["test:unit", "Passed · sample"],
    ],
    events: [
      ["Pipeline failed", "Sample · integration check failed"],
      ["Duo analysis", "Example diagnosis prepared"],
      ["Patch proposed", "Example boundary adjustment"],
      ["Tests verified", "Sample checks in progress"],
      ["Human review", "Pending synthetic verification"],
    ],
  },
  {
    id: "sample-791",
    repo: "gitback/demo-api",
    branch: "main",
    pipeline: "#791",
    job: "test:unit",
    sha: "7cf03a9",
    status: "Completed" as RepairStatus,
    time: "Oct 18",
    title: "Normalize empty pagination cursor",
    summary:
      "Example review completed in this local preview. No remote state changed.",
    failure: "Cursor parser rejected empty value",
    log: "Example log · synthetic\nFAIL pagination.test.ts\nExpected normalized cursor",
    diff: [{ kind: "add", text: "  const cursor = input.cursor || undefined" }],
    tests: [
      ["test:unit", "Passed · sample"],
      ["test:types", "Passed · sample"],
    ],
    events: [
      ["Pipeline failed", "Sample event"],
      ["Duo analysis", "Example diagnosis"],
      ["Patch proposed", "Example patch"],
      ["Tests verified", "Sample checks passed"],
      ["Human review", "Marked reviewed locally in example"],
    ],
  },
];
export const projects = [
  {
    name: "gitback/demo-api",
    description: "Example service · API response handling",
    branch: "main",
    pipeline: "#842",
    state: "Failed · Sample",
    repair: "sample-842",
  },
  {
    name: "gitback/worker-kit",
    description: "Example package · background jobs",
    branch: "fix/retry-window",
    pipeline: "#817",
    state: "Verifying · Sample",
    repair: "sample-817",
  },
];
