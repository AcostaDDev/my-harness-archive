import { useState } from "react";
import type { ReactNode } from "react";
import { BarChart, ColumnChart, StackedColumns } from "../charts";
import type { Datum, Stacked } from "../charts";
import type { S } from "../managed-api";
import { compact, count, coverage, coverageText, duration, percent, PROVENANCE, PURPOSES, ROLES, rootLabel, usd } from "../metrics.ts";
import type { Sum } from "../metrics.ts";
import { Link } from "../navigation";
import { Empty, Loading, PageHeader, Pagination, Stale, Status, usePoll, when } from "../ui";

// Statistics (H6.2 E6) over /api/managed/metrics/* (D074): each panel reads its resource, lists are paginated
// and null is shown as "no data", never as zero. The cost is the API equivalent the provider reports.

const INTERVAL = 15000;
type Scope = { project?: string; phase?: string; task?: string };
type Projects = { id: string; root: string }[];

function query(scope: Scope, extra: Record<string, string | number> = {}) {
  const params = new URLSearchParams();
  if (scope.project) params.set("project_id", scope.project);
  if (scope.phase) params.set("phase", scope.phase);
  if (scope.task) params.set("task", scope.task);
  for (const [key, value] of Object.entries(extra)) params.set(key, String(value));
  const text = params.toString();
  return text ? `?${text}` : "";
}

/** Sum with its coverage: "no data" if nobody contributes, a "partial" mark if only some attempts do. */
function Amount({ value, attempts, format = count }: { value: Sum; attempts: number; format?: (n: number | null) => string }) {
  const state = coverage(value, attempts);
  if (state === "absent") return <span className="muted" title={coverageText(value, attempts)}>sin dato</span>;
  return <span title={coverageText(value, attempts)}>{format(value.sum)}{state === "partial" && <sup className="partial"> parcial</sup>}</span>;
}

function Provenance({ of, row }: { of: string; row: S["AttemptMetricRead"] }) {
  const value = row.provenance[of] ?? "absent";
  const [label, title] = PROVENANCE[value] ?? [value, value];
  return <abbr className={`provenance provenance-${value}`} title={title}>{label}</abbr>;
}

function Tile({ label, value, children }: { label: string; value: ReactNode; children?: ReactNode }) {
  return <div className="tile"><p className="tile-label">{label}</p><p className="tile-value">{value}</p>{children && <p className="tile-note">{children}</p>}</div>;
}

function TableView({ title, children }: { title: string; children: ReactNode }) {
  return <details className="chart-table"><summary>{title}</summary><div className="table-scroll" tabIndex={0} role="region" aria-label={title}>{children}</div></details>;
}

// --- page --------------------------------------------------------------------------------------

export function StatsPage({ project, refresh = 0 }: { project?: string; refresh?: number }) {
  const scope: Scope = { project };
  const summary = usePoll<S["MetricsSummaryRead"]>(`/metrics/summary${query(scope)}`, INTERVAL, refresh);
  const projects = usePoll<S["ManagedProjectRead"][]>(project ? null : "/projects", 0);
  const list: Projects = projects.data ?? [];
  const s = summary.data;
  return <>
    <PageHeader title="Estadísticas">
      <p>{project ? "Consumo y calidad del trabajo de los agentes en este proyecto." : "Consumo y calidad del trabajo de los agentes en todos los proyectos de este servicio."} Los
        tokens son los que informa cada proveedor: «sin dato» significa que ningún intento los informó, no cero. El coste es el
        equivalente API reportado, no una factura ni una cuota.</p>
    </PageHeader>
    <Stale error={s ? summary.error : undefined} />
    {summary.missing ? <Empty title={`No existe el proyecto ${project}`} />
      : !s ? summary.error ? <p role="alert" className="state state-error">No se pudieron leer las métricas: {summary.error}</p> : <Loading />
        : <Headline summary={s} />}
    {s && s.attempts_without_metrics > 0 && <p className="state state-attention" role="status">
      {s.attempts_without_metrics} intentos resueltos no tienen métricas: son anteriores a la captura. El relleno es explícito
      (<code>harness-local metrics-backfill --database RUTA</code>); hasta entonces no cuentan en ningún total.</p>}
    {s && <>
      <Consumption scope={scope} projects={list} refresh={refresh} />
      <Favorites scope={scope} refresh={refresh} />
      {project && <Tasks scope={scope} refresh={refresh} />}
      <TestsEvolution scope={scope} projects={list} refresh={refresh} />
      <Stops summary={s} />
      <Attempts scope={scope} projects={list} refresh={refresh} />
    </>}
  </>;
}

function Headline({ summary }: { summary: S["MetricsSummaryRead"] }) {
  const c = summary.consumption;
  const t = summary.tasks;
  const tests = summary.tests;
  const cases = tests.cases;
  return <section className="tiles" aria-label="Resumen">
    <Tile label="Intentos de agente" value={count(c.attempts)}>
      {c.accounting.terminal} con total del proveedor · {c.accounting.messages} por mensajes (parcial) · {c.accounting.absent} sin uso informado
    </Tile>
    <Tile label="Tokens totales" value={<Amount value={c.tokens.total_tokens} attempts={c.attempts} format={compact} />}>
      {coverageText(c.tokens.total_tokens, c.attempts)}
    </Tile>
    <Tile label="Equivalente API" value={<Amount value={c.cost_usd} attempts={c.attempts} format={usd} />}>
      Reportado por el proveedor, {coverageText(c.cost_usd, c.attempts)}
    </Tile>
    <Tile label="Tiempo de agente" value={<Amount value={c.attempt_wall_ms} attempts={c.attempts} format={v => duration(v, "ms")} />}>
      Suma de intentos, no tiempo transcurrido
    </Tile>
    <Tile label="Aceptadas a la primera" value={t.reviewed ? `${t.accepted_first_time} de ${t.reviewed}` : "sin dato"}>
      {t.reviewed ? `${percent(t.accepted_first_time, t.reviewed)} de las tareas revisadas` : "Ninguna tarea revisada todavía"}
    </Tile>
    <Tile label="Revisiones" value={t.corrections ? count(t.corrections.sum) : "sin dato"}>
      {t.corrections ? `Correcciones del ejecutor en ${t.corrections.tasks} tareas` : "Ninguna tarea con ejecución"}
    </Tile>
    <Tile label="Hasta el commit" value={t.seconds_to_commit ? duration(t.seconds_to_commit.sum / t.seconds_to_commit.tasks) : "sin dato"}>
      {t.seconds_to_commit ? `Media de ${t.seconds_to_commit.tasks} tareas · máximo ${duration(t.seconds_to_commit.max)}` : `${t.committed} tareas con commit`}
    </Tile>
    <Tile label="Tests en la última validación" value={tests.tasks_with_validation ? `${tests.commands_passed} OK · ${tests.commands_failed} KO` : "sin dato"}>
      {!tests.tasks_with_validation ? "Ninguna tarea validada" : cases
        ? `Comandos de ${tests.tasks_with_validation} tareas · casos JUnit ${cases.passed} OK · ${cases.failed + cases.error} KO${cases.skipped ? ` · ${cases.skipped} omitidos` : ""}`
        : `Comandos de ${tests.tasks_with_validation} tareas · sin reportes JUnit legibles`}
    </Tile>
  </section>;
}

// --- consumption -------------------------------------------------------------------------------

type Dimension = S["MetricGroupsRead"]["dimension"] | "reported_model";
const DIMENSIONS: [Dimension, string][] = [["phase", "Fase"], ["root", "Proyecto"], ["day", "Día"], ["role", "Rol"],
  ["provider", "Proveedor"], ["requested_model", "Modelo solicitado"], ["requested_effort", "Esfuerzo solicitado"],
  ["reported_model", "Modelo reportado"]];
const PAGE = 10;

function keyLabel(dimension: Dimension, key: string | null, projects: Projects) {
  if (dimension === "root") return rootLabel(key, projects);
  if (key == null) return "sin declarar";
  if (dimension === "role") return ROLES[key] ?? key;
  return key;
}

function Consumption({ scope, projects, refresh }: { scope: Scope; projects: Projects; refresh: number }) {
  const choices = DIMENSIONS.filter(([value]) => scope.project ? value !== "root" : value !== "phase");
  const [dimension, setDimension] = useState<Dimension>(scope.project ? "phase" : "root");
  const [offset, setOffset] = useState(0);
  const day = dimension === "day";
  const size = day ? 30 : PAGE;
  const models = dimension === "reported_model";
  const path = models ? `/metrics/models${query(scope, { order: "tokens", offset, limit: size })}`
    : `/metrics/groups${query(scope, { dimension, order: day ? "key" : "tokens", offset, limit: size })}`;
  const read = usePoll<S["MetricGroupsRead"] | S["ModelMetricGroupsRead"]>(path, INTERVAL, refresh);
  // When the grouping changes, the previous read (another schema) remains in the first render: only the one
  // matching the chosen dimension is painted.
  const data = read.data?.dimension === dimension ? read.data : undefined;
  const choose = (value: Dimension) => { setDimension(value); setOffset(0); };
  const label = choices.find(([value]) => value === dimension)![1].toLowerCase();
  return <section className="panel" aria-labelledby="consumption">
    <div className="panel-head">
      <h2 id="consumption">Consumo</h2>
      <label className="inline-select">Agrupar por<select value={dimension} onChange={e => choose(e.target.value as Dimension)}>
        {choices.map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select></label>
    </div>
    <p className="hint">{models
      ? "Tokens de salida por modelo que informa el proveedor (Claude). Codex no informa modelo; sus intentos no aparecen aquí."
      : day ? "Tokens totales por día UTC de inicio del intento, del más antiguo al más reciente. Solo los días con intentos; un círculo vacío marca un día cuyos intentos no informan tokens (sin dato, no cero)."
        : `Tokens totales por ${label}, de mayor a menor. La entrada cruda no se suma: su semántica depende del proveedor.`}</p>
    <Stale error={data ? read.error : undefined} />
    {!data ? <Loading /> : !data.items.length ? <Empty title="Sin intentos en este ámbito" />
      : models ? <ModelConsumption groups={data as S["ModelMetricGroupsRead"]} />
        : <GroupConsumption groups={data as S["MetricGroupsRead"]} dimension={dimension} projects={projects} />}
    <Pagination offset={offset} next={data?.next_offset} onChange={setOffset} size={size} label={day ? "Días anteriores y posteriores" : "Páginas de grupos"} />
  </section>;
}

function GroupConsumption({ groups, dimension, projects }: { groups: S["MetricGroupsRead"]; dimension: Dimension; projects: Projects }) {
  const items = dimension === "day" ? [...groups.items].reverse() : groups.items;
  const data: Datum[] = items.map(g => {
    const label = keyLabel(dimension, g.key, projects);
    const total = g.tokens.total_tokens;
    return { key: String(g.key), label, value: total.sum,
      tip: [total.sum == null ? "sin dato" : `${count(total.sum)} tokens`, label, `${g.attempts} intentos · ${coverageText(total, g.attempts)}`,
        `Equivalente API: ${usd(g.cost_usd.sum)}`] };
  });
  return <>
    {dimension === "day" ? <ColumnChart data={data} label="Tokens totales por día" /> : <BarChart data={data} label="Tokens totales por grupo" />}
    <TableView title="Ver como tabla">
      <table className="table">
        <thead><tr><th scope="col">Grupo</th><th scope="col" className="numeric">Intentos</th><th scope="col" className="numeric">Sin caché</th>
          <th scope="col" className="numeric">Caché leída</th><th scope="col" className="numeric">Caché escrita</th><th scope="col" className="numeric">Salida</th>
          <th scope="col" className="numeric" title="Subconjunto de la salida">Razonamiento</th><th scope="col" className="numeric">Total</th>
          <th scope="col" className="numeric" title="num_turns de Claude">Turnos rep.</th><th scope="col" className="numeric" title="Elementos del stream de Codex">Turnos der.</th>
          <th scope="col" className="numeric">Equivalente API</th><th scope="col" className="numeric">Tiempo de agente</th></tr></thead>
        <tbody>{items.map(g => <tr key={String(g.key)}>
          <th scope="row">{keyLabel(dimension, g.key, projects)}</th>
          <td className="numeric">{g.attempts}</td>
          {(["uncached_input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "total_tokens"] as const).map(name =>
            <td key={name} className="numeric"><Amount value={g.tokens[name]} attempts={g.attempts} /></td>)}
          <td className="numeric"><Amount value={g.turns_reported} attempts={g.attempts} /></td>
          <td className="numeric"><Amount value={g.turns_derived} attempts={g.attempts} /></td>
          <td className="numeric"><Amount value={g.cost_usd} attempts={g.attempts} format={usd} /></td>
          <td className="numeric"><Amount value={g.attempt_wall_ms} attempts={g.attempts} format={v => duration(v, "ms")} /></td>
        </tr>)}</tbody>
      </table>
    </TableView>
  </>;
}

function ModelConsumption({ groups }: { groups: S["ModelMetricGroupsRead"] }) {
  const data: Datum[] = groups.items.map(g => ({ key: g.key, label: g.key, value: g.tokens.output_tokens.sum,
    tip: [g.tokens.output_tokens.sum == null ? "sin dato" : `${count(g.tokens.output_tokens.sum)} tokens de salida`, g.key, `${g.attempts} intentos`, `Equivalente API: ${usd(g.cost_usd.sum)}`] }));
  return <>
    <BarChart data={data} label="Tokens de salida por modelo reportado" />
    <TableView title="Ver como tabla">
      <table className="table">
        <thead><tr><th scope="col">Modelo</th><th scope="col" className="numeric">Intentos</th><th scope="col" className="numeric">Entrada</th>
          <th scope="col" className="numeric">Caché leída</th><th scope="col" className="numeric">Caché escrita</th><th scope="col" className="numeric">Salida</th>
          <th scope="col" className="numeric">Razonamiento</th><th scope="col" className="numeric">Equivalente API</th></tr></thead>
        <tbody>{groups.items.map(g => <tr key={g.key}>
          <th scope="row" className="mono">{g.key}</th><td className="numeric">{g.attempts}</td>
          {(["input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens"] as const).map(name =>
            <td key={name} className="numeric"><Amount value={g.tokens[name]} attempts={g.attempts} /></td>)}
          <td className="numeric"><Amount value={g.cost_usd} attempts={g.attempts} format={usd} /></td>
        </tr>)}</tbody>
      </table>
    </TableView>
  </>;
}

// --- favorites by role -------------------------------------------------------------------------

function Favorites({ scope, refresh }: { scope: Scope; refresh: number }) {
  const [order, setOrder] = useState<"attempts" | "tokens">("attempts");
  const roles = usePoll<S["MetricGroupsRead"]>(`/metrics/groups${query(scope, { dimension: "role", order: "attempts", limit: 20 })}`, INTERVAL, refresh);
  return <section className="panel" aria-labelledby="favorites">
    <div className="panel-head">
      <h2 id="favorites">Favoritos por rol</h2>
      <label className="inline-select">Según<select value={order} onChange={e => setOrder(e.target.value as "attempts" | "tokens")}>
        <option value="attempts">Número de intentos</option><option value="tokens">Tokens totales</option></select></label>
    </div>
    <p className="hint">Lo solicitado en cada intento (selección congelada), no lo que el proveedor dice haber usado.</p>
    {!roles.data ? <Loading /> : !roles.data.items.length ? <Empty title="Sin intentos en este ámbito" />
      : <div className="table-scroll" tabIndex={0} role="region" aria-label="Favoritos por rol">
        <table className="table">
          <thead><tr><th scope="col">Rol</th><th scope="col" className="numeric">Intentos</th><th scope="col">Proveedor</th><th scope="col">Modelo</th><th scope="col">Esfuerzo</th></tr></thead>
          <tbody>{roles.data.items.map(r => r.key && <tr key={r.key}>
            <th scope="row">{ROLES[r.key] ?? r.key}</th><td className="numeric">{r.attempts}</td>
            {(["provider", "requested_model", "requested_effort"] as const).map(dimension =>
              <td key={dimension}><Favorite scope={scope} role={r.key!} dimension={dimension} order={order} refresh={refresh} /></td>)}
          </tr>)}</tbody>
        </table>
      </div>}
  </section>;
}

function Favorite({ scope, role, dimension, order, refresh }: { scope: Scope; role: string; dimension: string; order: string; refresh: number }) {
  const read = usePoll<S["MetricGroupsRead"]>(`/metrics/groups${query(scope, { dimension, role, order, limit: 2 })}`, INTERVAL, refresh);
  if (!read.data) return <span className="muted">…</span>;
  const [first, second] = read.data.items;
  if (!first) return <span className="muted">sin dato</span>;
  const metric = (g: S["MetricGroupRead"]) => order === "tokens" ? `${compact(g.tokens.total_tokens.sum)} tokens` : `${g.attempts} intentos`;
  return <span><span className="mono">{first.key ?? "sin declarar"}</span> <span className="muted">({metric(first)}{second ? `; luego ${second.key ?? "sin declarar"}` : ""})</span></span>;
}

// --- tasks -------------------------------------------------------------------------------------

function Tasks({ scope, refresh }: { scope: Scope; refresh: number }) {
  const [offset, setOffset] = useState(0);
  const read = usePoll<S["Page_TaskMetricsRead_"]>(`/metrics/tasks${query(scope, { offset, limit: PAGE })}`, INTERVAL, refresh);
  return <section className="panel" aria-labelledby="task-quality">
    <h2 id="task-quality">Tareas</h2>
    <p className="hint">Revisiones = ejecuciones después de la primera. Los tokens incluyen los intentos fallidos. Tests: última validación de la tarea.</p>
    {!read.data ? <Loading /> : !read.data.items.length && !offset ? <Empty title="Todavía no hay tareas con runs" />
      : <div className="table-scroll" tabIndex={0} role="region" aria-label="Calidad por tarea">
        <table className="table">
          <thead><tr><th scope="col">Tarea</th><th scope="col">Estado</th><th scope="col">Primer veredicto</th><th scope="col" className="numeric">Revisiones</th>
            <th scope="col" className="numeric">Hasta el commit</th><th scope="col">Tests</th><th scope="col" className="numeric">Tokens</th><th scope="col" className="numeric">Paradas</th></tr></thead>
          <tbody>{read.data.items.map(t => <tr key={`${t.phase_code}/${t.task_id}`}>
            <th scope="row"><Link className="mono" to={{ name: "task", project: scope.project!, phase: t.phase_code, task: t.task_id }}>{t.task_id}</Link></th>
            <td>{t.status ? <Status value={t.status} /> : <span className="muted">sin run</span>}</td>
            <td>{t.first_verdict ?? <span className="muted">sin revisión</span>}{t.accepted_first_time && <span className="muted"> (a la primera)</span>}</td>
            <td className="numeric">{t.corrections ?? <span className="muted">sin dato</span>}</td>
            <td className="numeric">{t.seconds_to_commit == null ? <span className="muted">sin commit</span> : duration(t.seconds_to_commit)}</td>
            <td><TestCounts tests={t.tests} /></td>
            <td className="numeric"><Amount value={t.consumption.tokens.total_tokens} attempts={t.consumption.attempts} format={compact} /></td>
            <td className="numeric">{t.stops.length}</td>
          </tr>)}</tbody>
        </table>
      </div>}
    <Pagination offset={offset} next={read.data?.next_offset} onChange={setOffset} size={PAGE} label="Páginas de tareas" />
  </section>;
}

function TestCounts({ tests }: { tests: S["ValidationCountsRead"] | null }) {
  if (!tests) return <span className="muted">sin validar</span>;
  const cases = tests.cases;
  return <span className="nowrap">
    <span className={tests.commands_failed ? "count-ko" : "count-ok"}>{tests.commands_failed ? "KO" : "OK"}</span>{" "}
    comandos {tests.commands_passed}/{tests.commands_passed + tests.commands_failed}
    {cases && <span className="muted"> · casos {cases.passed} OK, {cases.failed + cases.error} KO</span>}
  </span>;
}

// --- tests: trend ------------------------------------------------------------------------------

function TestsEvolution({ scope, projects, refresh }: { scope: Scope; projects: Projects; refresh: number }) {
  const [offset, setOffset] = useState(0);
  const dimension = scope.project ? "phase" : "root";
  const read = usePoll<S["ValidationGroupsRead"]>(`/metrics/validations${query(scope, { dimension, offset, limit: 30 })}`, INTERVAL, refresh);
  const items = read.data ? [...read.data.items].reverse() : [];
  const label = (key: string) => dimension === "root" ? rootLabel(key, projects) : key;
  const data: Stacked[] = items.map(g => ({ key: g.key, label: label(g.key), ok: g.passed, ko: g.failed,
    tip: [`${g.passed} OK · ${g.failed} KO`, label(g.key), `${g.validations} validaciones · comandos ${g.commands_passed} OK, ${g.commands_failed} KO`] }));
  return <section className="panel" aria-labelledby="tests-evolution">
    <h2 id="tests-evolution">{scope.project ? "Tests: evolución por fase" : "Tests por proyecto"}</h2>
    <p className="hint">Cada validación de cada tarea, también las revalidaciones. OK: todos los comandos correctos y ningún fallo nuevo en JUnit.
      Las validaciones no guardan su hora, así que la evolución se lee por fase, no por día.</p>
    {!read.data ? <Loading /> : !items.length ? <Empty title="Todavía no hay validaciones" /> : <>
      <StackedColumns data={data} label={scope.project ? "Validaciones OK y KO por fase" : "Validaciones OK y KO por proyecto"} />
      <TableView title="Ver como tabla">
        <table className="table">
          <thead><tr><th scope="col">{dimension === "root" ? "Proyecto" : "Fase"}</th><th scope="col" className="numeric">Validaciones</th><th scope="col" className="numeric">OK</th>
            <th scope="col" className="numeric">KO</th><th scope="col" className="numeric">Comandos OK</th><th scope="col" className="numeric">Comandos KO</th><th scope="col">Casos JUnit</th></tr></thead>
          <tbody>{items.map(g => <tr key={g.key}>
            <th scope="row">{dimension === "phase" && scope.project ? <Link className="mono" to={{ name: "phase", project: scope.project, phase: g.key }}>{g.key}</Link> : label(g.key)}</th>
            <td className="numeric">{g.validations}</td><td className="numeric">{g.passed}</td><td className="numeric">{g.failed}</td>
            <td className="numeric">{g.commands_passed}</td><td className="numeric">{g.commands_failed}</td>
            <td>{g.cases ? `${g.cases.passed} OK · ${g.cases.failed + g.cases.error} KO${g.cases.skipped ? ` · ${g.cases.skipped} omitidos` : ""} (${g.validations_with_cases} validaciones con reporte)` : <span className="muted">sin reportes legibles</span>}</td>
          </tr>)}</tbody>
        </table>
      </TableView>
    </>}
    <Pagination offset={offset} next={read.data?.next_offset} onChange={setOffset} size={30} label="Páginas de validaciones" />
  </section>;
}

// --- stops -------------------------------------------------------------------------------------

function Stops({ summary }: { summary: S["MetricsSummaryRead"] }) {
  const stops = summary.stops;
  return <section className="panel" aria-labelledby="stops">
    <h2 id="stops">Paradas</h2>
    {!stops.items.length ? <Empty title="Ningún run se ha detenido" /> : <>
      <p className="hint">Motivos más frecuentes{stops.distinct > stops.items.length ? ` (${stops.items.length} de ${stops.distinct} distintos)` : ""}.</p>
      <div className="table-scroll" tabIndex={0} role="region" aria-label="Paradas por motivo">
        <table className="table">
          <thead><tr><th scope="col" className="numeric">Veces</th><th scope="col">Tipo</th><th scope="col">Etapa</th><th scope="col">Motivo</th></tr></thead>
          <tbody>{stops.items.map((item, index) => <tr key={index}>
            <td className="numeric">{item.count}</td><td>{PURPOSES[item.purpose] ?? item.purpose}</td><td>{item.stage}</td><td className="wide">{item.reason}</td>
          </tr>)}</tbody>
        </table>
      </div>
    </>}
  </section>;
}

// --- attempts ----------------------------------------------------------------------------------

// Attempt outcome (D074): `COMPLETE`/`FAILED`/`INVALID`/`PARTIAL` come from the CLI adapter stream,
// `COMPLETED` from adapters without a stream and `INTERRUPTED` from confirming a stopped writer.
const ATTEMPT: Record<string, [string, string]> = {
  COMPLETE: ["Completo", "ok"], COMPLETED: ["Completo", "ok"], FAILED: ["Fallido", "danger"], INVALID: ["Inválido", "danger"],
  PARTIAL: ["Parcial", "attention"], INTERRUPTED: ["Interrumpido", "danger"],
};

function AttemptStatus({ value }: { value: string }) {
  const [label, tone] = ATTEMPT[value] ?? [value, "neutral"];
  return <span className={`status status-${tone}`} title={value}><span className="status-mark" aria-hidden="true" />{label}</span>;
}

export function Attempts({ scope, projects = [], refresh, title = "Intentos" }: { scope: Scope; projects?: Projects; refresh: number; title?: string }) {
  const [offset, setOffset] = useState(0);
  const read = usePoll<S["Page_AttemptMetricRead_"]>(`/metrics/attempts${query(scope, { offset, limit: PAGE })}`, INTERVAL, refresh);
  const projectOf = (root: string) => scope.project ?? projects.find(p => p.root === root)?.id;
  return <section className="panel" aria-labelledby="attempts">
    <h2 id="attempts">{title}</h2>
    <p className="hint">Una fila por intento, del más antiguo al más reciente, con la procedencia de cada valor:
      {Object.entries(PROVENANCE).map(([key, [label, text]]) => <span key={key}> <abbr className={`provenance provenance-${key}`} title={text}>{label}</abbr> {text.split(":")[0].toLowerCase()}.</span>)}</p>
    {!read.data ? <Loading /> : !read.data.items.length && !offset ? <Empty title="Sin intentos en este ámbito" />
      : <div className="table-scroll" tabIndex={0} role="region" aria-label={title}>
        <table className="table">
          <thead><tr><th scope="col">Inicio</th>{!scope.project && <th scope="col">Proyecto</th>}{!scope.task && <th scope="col">Tarea</th>}<th scope="col">Rol</th><th scope="col">Proveedor y modelo</th>
            <th scope="col">Resultado</th><th scope="col" className="numeric">Tokens</th><th scope="col" className="numeric">Turnos</th>
            <th scope="col" className="numeric">Equivalente API</th><th scope="col" className="numeric">Duración</th></tr></thead>
          <tbody>{read.data.items.map(a => {
            const project = projectOf(a.root);
            return <tr key={a.attempt_id}>
              <td className="nowrap">{project && a.purpose === "task"
                ? <Link to={{ name: "run", project, phase: a.phase_code, task: a.task_id, run: a.run_id }}>{when(a.started_at)}</Link> : when(a.started_at)}</td>
              {!scope.project && <td className="nowrap">{rootLabel(a.root, projects)}</td>}
              {!scope.task && <td className="mono nowrap">{a.task_id}{a.purpose !== "task" && <span className="muted"> · {PURPOSES[a.purpose] ?? a.purpose}</span>}</td>}
              <td>{ROLES[a.role] ?? a.role}<span className="muted"> #{a.number}</span></td>
              <td><span className="nowrap">{a.provider ?? <span className="muted">sin proceso</span>}{" "}
                <span className="mono" title="Solicitado">{a.requested_model ?? "—"}</span>{a.requested_effort && <span className="muted"> / {a.requested_effort}</span>}</span>
                {a.reported_models && <span className="cell-note" title="Reportado por el proveedor">usó {a.reported_models.join(", ")}</span>}</td>
              <td><AttemptStatus value={a.status} />{a.verdict && <span className="cell-note">{a.verdict}</span>}{a.error && <p className="cell-error" title={a.error}>{a.error}</p>}</td>
              <td className="numeric nowrap">{count(a.total_tokens)} <Provenance of="total_tokens" row={a} /></td>
              <td className="numeric nowrap">{count(a.turns)} <Provenance of="turns" row={a} /></td>
              <td className="numeric nowrap">{usd(a.cost_usd)} <Provenance of="cost_usd" row={a} /></td>
              <td className="numeric nowrap">{duration(a.wall_ms, "ms")} <Provenance of="wall_ms" row={a} /></td>
            </tr>;
          })}</tbody>
        </table>
      </div>}
    <Pagination offset={offset} next={read.data?.next_offset} onChange={setOffset} size={PAGE} label="Páginas de intentos" />
  </section>;
}

// --- task --------------------------------------------------------------------------------------

/** Metrics of a task (H6.2 E6): agents, attempts, tokens (failures included), turns and latest validation. */
export function TaskMetrics({ project, phase, task, refresh }: { project: string; phase: string; task: string; refresh: number }) {
  const scope: Scope = { project, phase, task };
  const read = usePoll<S["Page_TaskMetricsRead_"]>(`/metrics/tasks${query(scope, { limit: 1 })}`, INTERVAL, refresh);
  const validations = usePoll<S["ValidationGroupsRead"]>(`/metrics/validations${query(scope, { dimension: "task" })}`, INTERVAL, refresh);
  const t = read.data?.items[0];
  if (!read.data) return <section className="panel"><h2>Métricas</h2><Loading /></section>;
  if (!t) return null;
  const c = t.consumption;
  const all = validations.data?.items[0];
  return <>
    <section className="panel" aria-labelledby="task-metrics">
      <h2 id="task-metrics">Métricas</h2>
      <div className="tiles tiles-compact">
        <Tile label="Intentos" value={count(c.attempts)}>{Object.entries(t.attempts_by_role).map(([role, n]) => `${ROLES[role] ?? role} ${n}`).join(" · ") || "ninguno"}</Tile>
        <Tile label="Tokens (incluidos fallos)" value={<Amount value={c.tokens.total_tokens} attempts={c.attempts} format={compact} />}>{coverageText(c.tokens.total_tokens, c.attempts)}</Tile>
        <Tile label="Turnos" value={<>{c.turns_reported.sum != null && <><Amount value={c.turns_reported} attempts={c.attempts} /> <abbr className="provenance provenance-reported" title={PROVENANCE.reported[1]}>rep.</abbr></>}
          {c.turns_reported.sum != null && c.turns_derived.sum != null && " · "}
          {c.turns_derived.sum != null && <><Amount value={c.turns_derived} attempts={c.attempts} /> <abbr className="provenance provenance-derived" title={PROVENANCE.derived[1]}>der.</abbr></>}
          {c.turns_reported.sum == null && c.turns_derived.sum == null && <span className="muted">sin dato</span>}</>}>
          Reportados (Claude) y derivados (Codex) no se suman entre sí</Tile>
        <Tile label="Equivalente API" value={<Amount value={c.cost_usd} attempts={c.attempts} format={usd} />}>{coverageText(c.cost_usd, c.attempts)}</Tile>
        <Tile label="Revisiones" value={t.corrections == null ? "sin dato" : count(t.corrections)}>{t.executions} ejecuciones · primer veredicto {t.first_verdict ?? "sin revisión"}</Tile>
        <Tile label="Hasta el commit" value={t.seconds_to_commit == null ? "sin commit" : duration(t.seconds_to_commit)}>
          {t.seconds_to_accept == null ? "Sin aceptación" : `Aceptada a los ${duration(t.seconds_to_accept)}`}</Tile>
        <Tile label="Última validación" value={<TestCounts tests={t.tests} />}>
          {all ? `${all.validations} validaciones en total: ${all.passed} OK, ${all.failed} KO` : "Sin validaciones"}</Tile>
      </div>
      {t.agents.length > 0 && <>
        <h3>Agentes</h3>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Agentes de la tarea">
          <table className="table">
            <thead><tr><th scope="col">Rol</th><th scope="col">Proveedor</th><th scope="col">Modelo solicitado</th><th scope="col">Esfuerzo</th><th scope="col" className="numeric">Intentos</th></tr></thead>
            <tbody>{t.agents.map((a, index) => <tr key={index}>
              <td>{ROLES[a.role] ?? a.role}</td><td>{a.provider ?? <span className="muted">sin proceso</span>}</td>
              <td className="mono">{a.requested_model ?? "—"}</td><td>{a.requested_effort ?? "—"}</td><td className="numeric">{a.attempts}</td>
            </tr>)}</tbody>
          </table>
        </div>
      </>}
      {t.stops.length > 0 && <>
        <h3>Paradas</h3>
        <ul className="checklist">{t.stops.map((stop, index) => <li key={index}><strong>{stop.stage}</strong>: {stop.reason}</li>)}</ul>
      </>}
    </section>
    <Attempts scope={scope} refresh={refresh} title="Intentos de la tarea" />
  </>;
}
