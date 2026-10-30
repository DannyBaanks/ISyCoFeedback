import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity as ActivityIcon,
  FolderKanban,
  Wrench,
  UserRound,
  GitBranch,
  GitCommit,
  ChevronRight,
  ArrowLeft,
  Copy,
  Check,
  Clock3,
  AlertTriangle,
  CircleCheck,
  FlaskConical,
  Search,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
} from "lucide-react";
import { projects, repairs } from "./fixtures";
import "./styles.css";
type Page = "Activity" | "Projects" | "Repairs" | "Account";
const nav = [
  ["Activity", ActivityIcon],
  ["Projects", FolderKanban],
  ["Repairs", Wrench],
  ["Account", UserRound],
] as const;
function App() {
  const [page, setPage] = useState<Page>("Activity"),
    [selected, setSelected] = useState<string | null>(null),
    [query, setQuery] = useState(""),
    [toast, setToast] = useState(""),
    [expanded, setExpanded] = useState(false),
    [localStatus, setLocalStatus] = useState<Record<string, string>>({});
  const repair = repairs.find((x) => x.id === selected);
  const say = (s: string) => {
    setToast(s);
    window.setTimeout(() => setToast(""), 3200);
  };
  const open = (id: string) => {
    setSelected(id);
    setPage("Repairs");
    setExpanded(false);
  };
  const filtered = useMemo(
    () =>
      repairs.filter((r) =>
        (r.repo + " " + r.title + " " + r.status)
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [query],
  );
  const copy = async () => {
    try {
      await navigator.clipboard.writeText("8e42bf1");
      say("Sample SHA copied. No repository was contacted.");
    } catch {
      say("Clipboard unavailable. Sample SHA: 8e42bf1");
    }
  };
  return (
    <>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <div className="app">
        <aside className="sidebar">
          <Brand />
          <div className="side-label">
            WORKSPACE <span className="sample-chip">SAMPLE</span>
          </div>
          <nav aria-label="Primary">
            {nav.map(([n, I]) => (
              <button
                key={n}
                className={"nav-item " + (page === n ? "active" : "")}
                onClick={() => {
                  setPage(n);
                  setSelected(null);
                }}
              >
                <I size={19} />
                <span>{n}</span>
                {n === "Activity" && <span className="nav-count">1</span>}
              </button>
            ))}
          </nav>
          <div className="side-bottom">
            <div className="connection">
              <span className="offline-dot" />
              <div>
                <b>GitLab not connected</b>
                <small>Preview workspace</small>
              </div>
            </div>
            <div className="side-foot">Local preview only</div>
          </div>
        </aside>
        <div className="main-wrap">
          <header className="topbar">
            <Brand compact />
            <div className="top-right">
              <span className="demo-pill">
                <span />
                Preview mode
              </span>
              <button
                className="connect-btn"
                onClick={() => {
                  setPage("Account");
                  say("Connection is not available in this preview.");
                }}
              >
                GitLab not connected
              </button>
            </div>
          </header>
          <div className="notice" role="status">
            <ShieldCheck size={16} />
            <span>
              <b>Preview mode</b> · synthetic sample data · GitLab not connected
            </span>
          </div>
          <main id="main" tabIndex={-1}>
            <div className="page-head">
              <div>
                <p className="eyebrow">
                  GITBACK / {selected ? "REPAIR DETAIL" : page.toUpperCase()}
                </p>
                <h1>{repair ? "Review sample repair" : page}</h1>
                <p className="subhead">
                  {repair
                    ? "Understand the proposal and inspect example evidence before deciding."
                    : page === "Activity"
                      ? "A clear path from pipeline failure to human review."
                      : page === "Projects"
                        ? "Example repositories and their latest synthetic pipeline state."
                        : page === "Repairs"
                          ? "Review proposed changes and example verification evidence."
                          : "Your preview workspace and connection status."}
                </p>
              </div>
              {repair && (
                <button
                  className="back-button"
                  onClick={() => setSelected(null)}
                >
                  <ArrowLeft size={16} /> All repairs
                </button>
              )}
            </div>
            {page === "Activity" && (
              <Activity open={open} copy={copy} setPage={setPage} />
            )}
            {page === "Projects" && (
              <Projects query={query} setQuery={setQuery} open={open} />
            )}
            {page === "Repairs" && !repair && (
              <RepairsList
                filtered={filtered}
                query={query}
                setQuery={setQuery}
                open={open}
                localStatus={localStatus}
              />
            )}
            {page === "Repairs" && repair && (
              <RepairDetail
                repair={repair}
                expanded={expanded}
                setExpanded={setExpanded}
                localStatus={localStatus[repair.id]}
                act={(s) => {
                  setLocalStatus({ ...localStatus, [repair.id]: s });
                  say(`${s} · local preview state only; nothing was sent.`);
                }}
              />
            )}
            {page === "Account" && <Account />}
          </main>
          <footer className="footer">
            GitBack preview <span>·</span> Built for the GitLab ecosystem{" "}
            <span>·</span> No remote actions
          </footer>
        </div>
        <nav className="mobile-nav" aria-label="Primary navigation">
          {nav.map(([n, I]) => (
            <button
              key={n}
              className={page === n ? "active" : ""}
              onClick={() => {
                setPage(n);
                setSelected(null);
              }}
              aria-current={page === n ? "page" : undefined}
            >
              <I size={20} />
              <span>{n}</span>
            </button>
          ))}
        </nav>
      </div>
      <div className="toast" aria-live="polite" aria-atomic="true">
        {toast && (
          <>
            <Check size={17} />
            {toast}
          </>
        )}
      </div>
    </>
  );
}
function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={"brand " + (compact ? "brand-compact" : "")}>
      <div className="mark" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <span>GitBack</span>
      {!compact && <small>PREVIEW</small>}
    </div>
  );
}
function Sample({ children = "Sample" }: { children?: React.ReactNode }) {
  return <span className="sample-tag">{children}</span>;
}
function Activity({
  open,
  copy,
  setPage,
}: {
  open: (id: string) => void;
  copy: () => void;
  setPage: (p: Page) => void;
}) {
  return (
    <>
      <section className="focus-layout">
        <article className="incident">
          <div className="incident-top">
            <div className="incident-type">
              <span className="failure-icon">
                <AlertTriangle size={17} />
              </span>
              <span>PIPELINE FAILURE</span>
            </div>
            <Sample>Sample</Sample>
          </div>
          <h2>Unit tests fail on empty response</h2>
          <p className="incident-summary">
            A null API response reaches the formatter without a guard.
          </p>
          <div className="repo-line">
            <span className="repo-symbol">GB</span>
            <b>gitback/demo-api</b>
            <Sample>Example project</Sample>
          </div>
          <div className="metadata">
            <span>
              <GitBranch />
              main
            </span>
            <span>
              <GitCommit />
              8e42bf1 <Sample />
            </span>
            <span>
              <Clock3 />
              12 min ago <Sample />
            </span>
          </div>
          <div className="jobline">
            <span>Failed job</span>
            <code>test:unit</code>
            <span className="error-text">exit code 1</span>
          </div>
          <div className="incident-actions">
            <button className="primary" onClick={() => open("sample-842")}>
              View sample repair <ChevronRight size={17} />
            </button>
            <button className="secondary" onClick={copy}>
              <Copy size={16} /> Copy commit SHA
            </button>
          </div>
          <p className="local-hint">
            These controls only open or copy example data locally.
          </p>
        </article>
        <article className="journey">
          <div className="journey-head">
            <div>
              <span className="eyebrow">REVIEW PATH</span>
              <h2>From failure to a decision</h2>
            </div>
            <Sample>Entire flow is synthetic</Sample>
          </div>
          <ol className="timeline">
            {[
              [
                "fail",
                "Pipeline failed",
                "Sample · test:unit returned exit code 1",
                "1",
              ],
              [
                "analysis",
                "Duo analysis",
                "Example diagnosis · not a real Duo session",
                "2",
              ],
              [
                "patch",
                "Patch proposed",
                "Example diff · inspect before deciding",
                "3",
              ],
              [
                "verify",
                "Tests verified",
                "Sample results · not executed tests",
                "4",
              ],
              [
                "review",
                "Human review",
                "Awaiting your review · no auto-merge",
                "5",
              ],
            ].map((x, i) => (
              <li
                key={x[1]}
                className={
                  i === 0
                    ? "tl-error"
                    : i === 4
                      ? "tl-pending"
                      : i === 3
                        ? "tl-success"
                        : ""
                }
              >
                <span className="tl-node">
                  {i === 0 ? (
                    <AlertTriangle />
                  ) : i === 3 ? (
                    <Check />
                  ) : i === 4 ? (
                    <UserRound />
                  ) : (
                    <span>{x[3]}</span>
                  )}
                </span>
                <div>
                  <div className="tl-title">
                    {x[1]} <Sample />
                  </div>
                  <p>{x[2]}</p>
                </div>
              </li>
            ))}
          </ol>
          <button className="text-link" onClick={() => open("sample-842")}>
            Inspect example evidence <ChevronRight size={16} />
          </button>
        </article>
      </section>
      <section className="activity-section">
        <div className="section-title">
          <div>
            <span className="eyebrow">RECENT</span>
            <h2>Activity</h2>
          </div>
          <button className="text-link" onClick={() => setPage("Repairs")}>
            All repairs <ChevronRight size={16} />
          </button>
        </div>
        <div className="activity-row">
          <span className="mini-icon warn">
            <AlertTriangle />
          </span>
          <div>
            <b>Pipeline #842 failed</b>
            <p>gitback/demo-api · test:unit</p>
          </div>
          <Sample />
          <span className="row-time">12 min ago</span>
        </div>
        <div className="activity-row">
          <span className="mini-icon purple">
            <Wrench />
          </span>
          <div>
            <b>Example repair is ready for review</b>
            <p>Nullable response guard · 8e42bf1</p>
          </div>
          <Sample />
          <span className="row-time">11 min ago</span>
        </div>
      </section>
      <div className="empty-tip">
        <div className="empty-symbol">
          <CircleCheck />
        </div>
        <div>
          <b>No real activity is connected</b>
          <p>
            This feed contains fixtures only. Connectors are not available in
            this preview.
          </p>
        </div>
      </div>
    </>
  );
}
function SearchBox({
  value,
  onChange,
  label = "Filter sample data",
}: {
  value: string;
  onChange: (v: string) => void;
  label?: string;
}) {
  return (
    <label className="search-box">
      <Search size={17} />
      <span className="sr-only">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Filter sample data"
      />
    </label>
  );
}
function Projects({
  query,
  setQuery,
  open,
}: {
  query: string;
  setQuery: (s: string) => void;
  open: (id: string) => void;
}) {
  const list = projects.filter((p) =>
    (p.name + " " + p.description + " " + p.state)
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  return (
    <>
      <div className="list-toolbar">
        <p>
          <Sample /> All repository and pipeline details are synthetic.
        </p>
        <SearchBox value={query} onChange={setQuery} />
      </div>
      <div className="project-grid">
        {list.map((p, i) => (
          <article className="project-card" key={p.name}>
            <div className="project-heading">
              <span className="repo-symbol large">GB</span>
              <span className="project-index">SAMPLE PROJECT 0{i + 1}</span>
              <button
                className="icon-button"
                aria-label={`Open ${p.name}`}
                onClick={() => open(p.repair)}
              >
                <ChevronRight />
              </button>
            </div>
            <h2>{p.name}</h2>
            <p>{p.description}</p>
            <div className="project-meta">
              <span>
                <GitBranch />
                {p.branch}
              </span>
              <span>Latest pipeline {p.pipeline}</span>
            </div>
            <div className="project-status">
              <span className="status-dot" />
              {p.state}
              <Sample />
            </div>
            <button className="text-link" onClick={() => open(p.repair)}>
              Open sample project <ChevronRight size={16} />
            </button>
          </article>
        ))}
      </div>
      {!list.length && (
        <Empty
          title="No sample projects match"
          detail="Try another local filter or clear the search."
        />
      )}
      <p className="source-note">
        Search is performed in this browser against bundled fixtures. No remote
        repository is queried.
      </p>
    </>
  );
}
function RepairsList({
  filtered,
  query,
  setQuery,
  open,
  localStatus,
}: {
  filtered: typeof repairs;
  query: string;
  setQuery: (s: string) => void;
  open: (id: string) => void;
  localStatus: Record<string, string>;
}) {
  return (
    <>
      <div className="list-toolbar">
        <p>
          <Sample /> Each item below is synthetic; no real tests ran.
        </p>
        <SearchBox value={query} onChange={setQuery} />
      </div>
      {(["Awaiting review", "Verifying", "Completed"] as const).map(
        (status) => {
          const rows = filtered.filter(
            (r) => (localStatus[r.id] || r.status) === status,
          );
          return (
            <section className="repair-group" key={status}>
              <div className="group-title">
                <h2>{status}</h2>
                <span className="count">{rows.length}</span>
                <span className="muted">Sample state</span>
              </div>
              {rows.length ? (
                rows.map((r) => (
                  <button
                    className="repair-row"
                    key={r.id}
                    onClick={() => open(r.id)}
                  >
                    <span className="repair-icon">
                      <Wrench />
                    </span>
                    <span className="repair-info">
                      <b>{r.title}</b>
                      <small>
                        {r.repo} <span>·</span> pipeline {r.pipeline}{" "}
                        <span>·</span> <code>{r.job}</code>
                      </small>
                    </span>
                    <Sample />
                    <span className="row-time">{r.time}</span>
                    <ChevronRight size={18} />
                  </button>
                ))
              ) : (
                <div className="group-empty">
                  No {status.toLowerCase()} examples match this filter.
                </div>
              )}
            </section>
          );
        },
      )}
      <p className="source-note">
        Changing a sample status in its detail only updates this view; it does
        not persist after reload.
      </p>
    </>
  );
}
function RepairDetail({
  repair: r,
  expanded,
  setExpanded,
  localStatus,
  act,
}: {
  repair: (typeof repairs)[number];
  expanded: boolean;
  setExpanded: (b: boolean) => void;
  localStatus?: string;
  act: (s: string) => void;
}) {
  return (
    <>
      <div className="detail-banner">
        <div className="banner-icon">
          <AlertTriangle />
        </div>
        <div>
          <div className="banner-label">
            SYNTHETIC FAILURE <Sample />
          </div>
          <h2>{r.failure}</h2>
          <p>Example failure message · not a live pipeline log</p>
        </div>
        <span className="state-pill">{localStatus || r.status}</span>
      </div>
      <div className="detail-grid">
        <section className="detail-main">
          <article className="detail-panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">PATCH PROPOSED</span>
                <h2>Example diff</h2>
              </div>
              <Sample>Not a real fix</Sample>
            </div>
            <div className="diff-box">
              {r.diff.map((l, i) => (
                <div className={"diff-line " + l.kind} key={i}>
                  <span>
                    {l.kind === "add" ? "+" : l.kind === "del" ? "−" : " "}
                  </span>
                  <code>{l.text}</code>
                </div>
              ))}
            </div>
            <p className="honesty">
              <AlertTriangle size={16} /> Proposal text is synthetic. A proposed
              patch is not a verified fix.
            </p>
          </article>
          <article className="detail-panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">VERIFICATION</span>
                <h2>Example test results</h2>
              </div>
              <Sample />
            </div>
            <div className="test-list">
              {r.tests.map(([name, result]) => (
                <div className="test-row" key={name}>
                  <span className="test-icon">
                    <FlaskConical />
                  </span>
                  <b>{name}</b>
                  <span className="test-result">{result}</span>
                  <Sample />
                </div>
              ))}
            </div>
            <p className="honesty green">
              <CircleCheck size={16} /> These are fixture results. Tests were
              not executed by this interface.
            </p>
          </article>
          <article className="detail-panel evidence-panel">
            <button
              className="evidence-toggle"
              aria-expanded={expanded}
              onClick={() => setExpanded(!expanded)}
            >
              <span>
                <span className="eyebrow">EVIDENCE</span>
                <b>Example job log</b>
                <Sample />
              </span>
              {expanded ? <ChevronUp /> : <ChevronDown />}
            </button>
            {expanded && <pre className="log">{r.log}</pre>}
          </article>
        </section>
        <aside className="detail-side">
          <article className="detail-panel context-panel">
            <span className="eyebrow">INCIDENT CONTEXT</span>
            <h3>{r.repo}</h3>
            <Sample>Example repository</Sample>
            <dl>
              <dt>Pipeline</dt>
              <dd>
                {r.pipeline} <Sample />
              </dd>
              <dt>Branch</dt>
              <dd>
                <code>{r.branch}</code>
              </dd>
              <dt>Commit SHA</dt>
              <dd>
                <code>{r.sha}</code> <Sample />
              </dd>
              <dt>Failed job</dt>
              <dd>
                <code>{r.job}</code>
              </dd>
              <dt>Updated</dt>
              <dd>
                {r.time} <Sample />
              </dd>
            </dl>
          </article>
          <article className="detail-panel">
            <span className="eyebrow">REVIEW PATH</span>
            <ol className="mini-timeline">
              {r.events.map((e, i) => (
                <li key={e[0]}>
                  <span
                    className={
                      i === 0
                        ? "mini-node error"
                        : i === 4
                          ? "mini-node pending"
                          : "mini-node"
                    }
                  >
                    {i < 4 ? <Check size={12} /> : <UserRound size={12} />}
                  </span>
                  <div>
                    <b>{e[0]}</b>
                    <p>{e[1]}</p>
                  </div>
                </li>
              ))}
            </ol>
          </article>
          <div className="review-box">
            <h3>Your review</h3>
            <p>
              These buttons only change this sample view. Nothing is sent or
              merged.
            </p>
            <button
              className="primary full"
              onClick={() => act("Accepted sample")}
            >
              Accept sample
            </button>
            <button
              className="secondary full"
              onClick={() => act("Changes requested")}
            >
              Request changes
            </button>
            <small>Local state resets when you reload.</small>
          </div>
        </aside>
      </div>
    </>
  );
}
function Account() {
  const [show, setShow] = useState(false);
  return (
    <div className="account-layout">
      <section className="detail-panel account-card">
        <div className="account-icon">
          <UserRound />
        </div>
        <div>
          <span className="eyebrow">ACCOUNT STATUS</span>
          <h2>GitLab not connected</h2>
          <p>
            GitBack is running as a local preview. There is no OAuth flow, API
            connection, or active account in this build.
          </p>
          <Sample>Preview only</Sample>
        </div>
      </section>
      <section className="detail-panel connection-card">
        <div>
          <h2>Connect a GitLab account</h2>
          <p>
            Connection setup is planned for a future integration. No credentials
            are requested or stored here.
          </p>
        </div>
        <button className="secondary" onClick={() => setShow(!show)}>
          {show ? "Hide details" : "Why is this unavailable?"}
        </button>
        {show && (
          <div className="explain">
            <b>Not available in preview</b>
            <p>
              OAuth consent, least-privilege scopes, secure token storage,
              pipeline webhooks, and verified Duo workflow contracts must be
              implemented and reviewed before connection is enabled.
            </p>
          </div>
        )}
      </section>
      <section className="trust-note">
        <ShieldCheck />
        <div>
          <b>Human review stays in control</b>
          <p>
            GitBack proposes and verifies. This preview has no merge action and
            cannot change remote state.
          </p>
        </div>
      </section>
    </div>
  );
}
function Empty({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty-state">
      <span>
        <Search />
      </span>
      <h2>{title}</h2>
      <p>{detail}</p>
    </div>
  );
}

if ("serviceWorker" in navigator && import.meta.env.PROD)
  window.addEventListener("load", () =>
    navigator.serviceWorker.register("/sw.js").catch(() => {}),
  );
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
