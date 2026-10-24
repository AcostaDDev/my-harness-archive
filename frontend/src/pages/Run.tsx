import { memo, useEffect, useRef, useState } from "react";
import { appendDiffPage, byteSize } from "../diff.ts";
import { useI18n } from "../Language";
import type { LoadedDiff } from "../diff.ts";
import { Logs } from "../Logs";
import { ROLES } from "../metrics.ts";
import { managed, managedApi, jobRequest, ManagedError } from "../managed-api";
import type { S } from "../managed-api";
import { Link, navigate } from "../navigation";
import { Permissions } from "../Permissions";
import { href, runRoute } from "../router.ts";
import { Tests } from "../Tests";
import { DiffLines, Empty, Evidence, Fields, Hash, Loading, PageHeader, Pagination, Stale, Status, message, usePoll, when } from "../ui";
import { useWorkspace } from "../workspace";

/** `/runs/:id`: resolves the canonical run URL and replaces it in the history. */
export function RunRedirect({ run }: { run: string }) {
  const { t } = useI18n();
  const read = usePoll<S["ManagedRunRead"]>(`/runs/${encodeURIComponent(run)}`, 0);
  useEffect(() => {
    const route = read.data && runRoute(read.data);
    if (route) navigate(route, { replace: true });
  }, [read.data]);
  if (read.missing) return <Empty title={t("run.missing")}><p>{t("not_found.hint")} <Link to={{ name: "home" }}>{t("not_found.back")}</Link></p></Empty>;
  if (read.data && !read.data.project_id) return <Empty title={t("run.unregistered.title")}><p>{t("run.unregistered.body")}</p></Empty>;
  return read.error ? <p role="alert" className="state state-error">{read.error}</p> : <Loading>{t("run.searching")}</Loading>;
}

// With a job queued, running or pending recovery the run changes by itself; without one, it only changes through
// a new action (from this page, which rereads at once, or from another tab), so a spaced poll is enough.
const ACTIVE_POLL = 1500;
const SETTLED_POLL = 15000;

export function RunPage({ phase, task, run: id }: { phase: string; task: string; run: string }) {
  const { t, n, rich } = useI18n();
  const { project, busy, refresh, operate, send } = useWorkspace();
  const [run, setRun] = useState<S["ManagedRunRead"]>();
  const [jobs, setJobs] = useState<S["Page_ManagedJobRead_"]>();
  const [jobOffset, setJobOffset] = useState(0);
  const [attempts, setAttempts] = useState<S["Page_ManagedAttemptRead_"]>();
  const [offset, setOffset] = useState(0);
  const [cycles, setCycles] = useState<S["Page_CycleRead_"]>();
  const [cycleOffset, setCycleOffset] = useState(0);
  const [events, setEvents] = useState<S["ManagedEventRead"][]>([]);
  const [missing, setMissing] = useState(false);
  const cursor = useRef(0);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [commitConfirmed, setCommitConfirmed] = useState(false);
  const path = `/runs/${encodeURIComponent(id)}`;
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const [r, j, a, e, c] = await Promise.all([managed<S["ManagedRunRead"]>(path), managed<S["Page_ManagedJobRead_"]>(`${path}/jobs?offset=${jobOffset}`),
          managed<S["Page_ManagedAttemptRead_"]>(`${path}/attempts?offset=${offset}`), managed<S["ManagedEventsRead"]>(`${path}/events?after=${cursor.current}&limit=50`),
          managed<S["Page_CycleRead_"]>(`${path}/cycles?offset=${cycleOffset}`)]);
        if (active) {
          setRun(r); setJobs(j); setAttempts(a); setCycles(c); setError(""); cursor.current = e.cursor;
          setEvents(previous => [...previous, ...e.items.filter(item => !previous.some(old => old.sequence === item.sequence))]);
          timer = setTimeout(() => void poll(), e.has_more ? 0 : r.active_job === null ? SETTLED_POLL : ACTIVE_POLL);
        }
      } catch (e) {
        if (!active) return;
        if (e instanceof ManagedError && e.status === 404) setMissing(true);
        setError(message(e)); timer = setTimeout(() => void poll(), 3000);
      }
    }
    void poll(); return () => { active = false; clearTimeout(timer); };
  }, [path, offset, jobOffset, cycleOffset, refresh]);
  useEffect(() => { setCommitConfirmed(false); setConfirmed(false); }, [run?.version]);
  // A URL with another phase, task or project is corrected to the canonical one without adding history.
  const canonical = run && runRoute(run);
  useEffect(() => {
    if (canonical && href(canonical) !== window.location.pathname) navigate(canonical, { replace: true });
  }, [canonical && href(canonical)]);
  if (missing && !run) return <Empty title={t("run.missing")}><p>{rich("run.back_to_task", { task: <Link className="mono" to={{ name: "task", project, phase, task }}>{task}</Link> })}</p></Empty>;
  if (!run) return error ? <p role="alert" className="state state-error">{error}</p> : <Loading>{t("run.loading")}</Loading>;
  const locked = run.locked_by_job !== null;
  const stale = !!error;
  function action(name: S["RunActionCreate"]["action"]) {
    void operate(() => send(jobRequest(`/runs/${run!.id}/actions`, { action: name, expected_version: run!.version })));
  }
  const documentRun = run.purpose === "document_export" || run.purpose === "bootstrap";
  const outcome = documentRun ? (run.purpose === "bootstrap" ? t("run.outcome.bootstrap") : t("run.outcome.export"))
    : run.status === "COMMITTED" ? t("run.outcome.committed")
      : run.history.acceptance?.eligible ? t("run.outcome.eligible") : t("run.outcome.none");
  return <>
    <PageHeader code title={t("trail.run", { id: run.id.slice(0, 8) })} aside={<Status value={run.status} />}>
      <p>{rich("run.lede", { task: <Link className="mono" to={{ name: "task", project, phase: run.phase_id, task: run.task_id }}>{run.task_id}</Link>,
        phase: <Link className="mono" to={{ name: "phase", project, phase: run.phase_id }}>{run.phase_id}</Link> })} {outcome}</p>
    </PageHeader>
    <Stale error={error} />
    {run.history.stop && <p className="state state-attention">{t("run.stop", { stage: run.history.stop.stage, reason: run.history.stop.reason })}</p>}

    <section className="panel" aria-labelledby="run-summary">
      <h2 id="run-summary">{t("stats.summary")}</h2>
      <Fields items={[
        [t("stats.column.stage"), run.stage], [t("phase.observed_version"), `${run.version}`], [t("stats.revisions"), t("runs.revisions", { count: run.revisions, limit: run.revision_limit })],
        [t("run.commit"), run.commit ? <><Status value={run.commit.status} /> <Hash value={run.commit.commit ?? run.commit.expected_commit} /></> : <span className="muted">{t("stats.no_commit")}</span>],
        [t("run.created"), when(run.created_at)], [t("tests.identifier"), <code>{run.id}</code>],
      ]} />
      {!documentRun && <p className="hint">{t("run.checkpoint")}</p>}
      {typeof run.history.task?.additional_notes === "string" && <div className="entry"><h3>{t("run.notes")}</h3><p className="turn-answer">{run.history.task.additional_notes}</p></div>}
      <Evidence title={t("run.history_evidence")} value={run.history} />
      <Evidence title={t("run.commit_evidence")} value={{ commit: run.commit, versions: run.versions }} />
    </section>

    {run.purpose === "task" && ["revalidate", "retry_executor", "commit"].some(a => run.actions.includes(a as S["RunActionCreate"]["action"])) && <section className="decision decision-attention" aria-labelledby="run-decision">
      <h2 id="run-decision">{t("run.decision")}</h2>
      <div className="actions">
        <button className="button-quiet" disabled={busy || locked || stale || !run.actions.includes("revalidate")} onClick={() => action("revalidate")}>{t("run.revalidate")}</button>
        <button className="button-quiet" disabled={busy || locked || stale || !run.actions.includes("retry_executor")} onClick={() => { if (window.confirm(t("run.retry_confirm"))) action("retry_executor"); }}>{t("run.retry")}</button>
      </div>
      <label className="check"><input type="checkbox" checked={commitConfirmed} onChange={e => setCommitConfirmed(e.target.checked)} />{t("run.commit_confirm")}</label>
      <button disabled={busy || locked || stale || !commitConfirmed || !run.actions.includes("commit")} onClick={() => action("commit")}>{t("run.commit_submit")}</button>
    </section>}

    {run.history.cycle_count > 0 && <section className="panel" aria-labelledby="run-cycles">
      <h2 id="run-cycles">{t("stats.revisions")} <span className="count">{run.history.cycle_count}</span></h2>
      {cycles?.items.map(c => <div className="entry" key={c.number}>
        <h3>{t("run.cycle", { number: c.number, verdict: c.verdict ?? t("run.no_verdict") })}</h3>
        <CycleDiff runId={run.id} number={c.number} sha256={c.diff_sha256} bytes={c.diff_bytes} paths={c.changed_paths.length} />
        <Tests runId={run.id} cycle={c.number} validation={c.validation} />
        {c.formatting && <Evidence title={n("run.formatting", (c.formatting.paths as string[] | undefined)?.length ?? 0)} value={c.formatting} />}
        <Evidence title={t("run.validation_evidence")} value={c.validation} /><Evidence title={t("run.review_evidence")} value={c.review} />
      </div>)}
      <Pagination offset={cycleOffset} next={cycles?.next_offset} onChange={setCycleOffset} label={t("run.pages.cycles")} />
    </section>}

    {run.purpose === "task" && <Permissions run={run} busy={busy || stale} refresh={refresh} operate={operate} />}

    <section className="panel" aria-labelledby="run-jobs">
      <h2 id="run-jobs">{t("run.jobs")}</h2>
      {!jobs?.items.length && <p className="hint">{t("run.jobs.empty")}</p>}
      {jobs?.items.map(job => <div key={job.id} className={job.status === "RECOVERY_REQUIRED" ? "entry entry-open" : "entry"}>
        <p><strong>{t("run.job", { id: job.id })}</strong> {job.action} <Status value={job.status} /></p>
        {job.diagnostic && <p>{job.diagnostic}</p>}
        {job.status === "RECOVERY_REQUIRED" && <div className="decision decision-attention">
          <p>{t("run.recovery.lease")} {t(run.purpose === "bootstrap" ? "run.recovery.bootstrap" : run.purpose === "bootstrap_discovery" ? "run.recovery.discovery"
            : run.purpose === "document_export" ? "run.recovery.export" : "run.recovery.task")}</p>
          <label>{t("run.recovery.evidence")}<input value={reason} onChange={e => setReason(e.target.value)} maxLength={2000} /></label>
          <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />{t("run.recovery.confirm")}</label>
          <button disabled={busy || stale || !confirmed || !reason.trim() || !job.owner_token} onClick={() => void operate(async () => {
            await managedApi.confirm(job.id, { owner_token: job.owner_token!, expected_version: run.version, reason }); setConfirmed(false);
          })}>{t("run.recovery.submit")}</button>
        </div>}
        <Evidence title={t("run.job.evidence", { id: job.id })} value={job} />
      </div>)}
      <Pagination offset={jobOffset} next={jobs?.next_offset} onChange={setJobOffset} label={t("run.pages.jobs")} />
    </section>

    <section className="panel" aria-labelledby="run-attempts">
      <h2 id="run-attempts">{t("stats.attempts.title")}</h2>
      {!attempts?.items.length && <p className="hint">{t("run.attempts.empty")}</p>}
      {attempts?.items.map(a => <div className="entry" key={a.id}>
        <p><strong>{t("run.attempt", { number: a.number })}</strong> {ROLES[a.role] ? t(ROLES[a.role]) : a.role} <Status value={a.status} /></p>
        <Logs runId={run.id} attemptId={a.id} />
        <Evidence title={t("run.attempt.evidence")} value={a} /></div>)}
      <Pagination offset={offset} next={attempts?.next_offset} onChange={setOffset} label={t("stats.pages.attempts")} />
    </section>

    <details className="panel panel-collapsible">
      <summary><h2>{t("run.events")} <span className="count">{events.length}</span></h2></summary>
      <ol className="events">{events.map(e => <li key={e.sequence}><p><strong>{e.sequence}</strong> {e.kind} {when(e.recorded_at)}</p><Evidence title={t("run.event.evidence")} value={e.payload} /></li>)}</ol>
    </details>
  </>;
}

/**
 * Reviewed diff of a cycle: read when opened, in 64 KiB pages bound to the hash of the run summary, and not
 * requested again on every poll. A page that does not continue what is shown discards it instead of mixing it.
 * Scalar props and memo: polling the run does not repaint a diff of thousands of lines; each page is its chunk.
 */
const CycleDiff = memo(function CycleDiff({ runId, number, sha256, bytes, paths }: { runId: string; number: number; sha256: string; bytes: number; paths: number }) {
  const { t, n, language } = useI18n();
  const [diff, setDiff] = useState<LoadedDiff>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const request = useRef(0);
  useEffect(() => { request.current++; setDiff(undefined); setError(""); setLoading(false); }, [runId, number, sha256]);
  async function more(current?: LoadedDiff) {
    const id = ++request.current;
    setLoading(true); setError("");
    try {
      const page = await managed<S["CycleDiffRead"]>(`/runs/${encodeURIComponent(runId)}/cycles/${number}/diff?offset=${current?.next ?? 0}&sha256=${sha256}`);
      if (id !== request.current) return;
      const next = appendDiffPage(current, page);
      setDiff(next ?? undefined);
      if (!next) setError(t("run.diff.discontinuous"));
    } catch (e) {
      if (id === request.current) setError(message(e));
    } finally {
      if (id === request.current) setLoading(false);
    }
  }
  return <details className="evidence" onToggle={e => { if (e.currentTarget.open && !diff && !loading) void more(); }}>
    <summary>{t("run.diff.summary", { paths: n("run.diff.paths", paths), size: byteSize(bytes, language) })}</summary>
    {diff && (diff.size ? <pre className="diff" aria-label={t("run.diff.label", { number })}>{diff.pages.map((page, index) => <DiffLines key={index} text={page} />)}</pre>
      : <p className="hint">{t("prompts.no_diff")}</p>)}
    {loading && <Loading>{t("run.diff.loading")}</Loading>}
    {error && <p role="alert" className="state state-error">{error}</p>}
    {diff && diff.size > 0 && <p className="hint">{diff.next === null ? t("run.diff.complete") : t("stats.of", { part: byteSize(diff.loaded, language), whole: byteSize(diff.size, language) })} · <Hash value={diff.sha256} /></p>}
    {(diff?.next != null || (error && !loading)) && <button type="button" className="button-quiet" disabled={loading} onClick={() => void more(diff)}>
      {diff ? t("run.diff.more") : t("run.diff.load")}</button>}
  </details>;
});
