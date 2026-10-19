import { useState } from "react";
import { createOnce, managed } from "../managed-api";
import type { S } from "../managed-api";
import { pendingPreparationStep, preparationStatus } from "../preparation.ts";
import { DiffBlock, Evidence, Hash, Stale, usePoll } from "../ui";
import { useWorkspace } from "../workspace";

type Plan = S["PreparationPlanRead"];
type Change = S["PreparationChangeInput"];

export function Preparation() {
  const { project, refresh, busy, operate } = useWorkspace();
  const read = usePoll<S["PreparationRead"]>(`/projects/${project}/preparation`, 1500, refresh);
  const [mode, setMode] = useState<"offline" | "network">("offline");
  const [preview, setPreview] = useState<{ plan: Plan; change: Change }>();
  const [journal, setJournal] = useState<S["PreparationOperationRead"]>();
  const [confirmed, setConfirmed] = useState(false);
  const data = read.data;
  if (!data?.available) return null;
  const op = data.operation;
  const working = op?.status === "QUEUED" || op?.status === "ACTIVE";
  const retry = op && ["FAILED", "RECOVERY_REQUIRED", "CANCELLED"].includes(op.status);
  const next = op ? pendingPreparationStep(op.steps as { number: number; status: string }[]) : undefined;
  async function show() {
    const change: Change = { expected_version: data!.project_version, mode,
      ...(retry ? { previous_id: op!.id, retry_step: next } : {}) };
    const plan = await managed<Plan>(`/projects/${project}/preparation/preview`, change);
    setPreview({ plan, change }); setConfirmed(false);
  }
  const control = (action: string) => operate(async () => {
    await createOnce(`/preparations/${op!.id}/${action}`, {
      expected_version: op!.version, plan_sha256: op!.plan_sha256,
    } satisfies S["PreparationControlInput"]);
    setPreview(undefined); setConfirmed(false);
  });
  return <section className="panel" aria-labelledby="django-preparation">
    <h2 id="django-preparation">Preparar Django</h2>
    <Stale error={read.error} />
    <p>Después del commit documental, esta receta crea el entorno, el proyecto y la app base, valida sus herramientas y hace un commit técnico. Las tareas se habilitan cuando termina.</p>
    {data.prepared && <p className="state state-ok" role="status">Django preparado. Puedes continuar con las tareas de la fase.</p>}
    {data.diagnostic && <p className="state state-attention">{data.diagnostic}</p>}
    {op && <>
      <p role="status"><strong>{preparationStatus(op.status)}</strong> · operación <code>{op.id}</code></p>
      <progress max={op.steps.length} value={op.steps.filter(s => s.status === "DONE").length} aria-label="Pasos de preparación completados" />
      <ol>{op.steps.map(s => <li key={String(s.id)}>{String(s.spec && (s.spec as Record<string, unknown>).label)} · {({ DONE: "Completado", STARTED: working ? "En curso" : "Sin resultado acreditado", PENDING: "Pendiente" } as Record<string, string>)[String(s.status)] ?? String(s.status)}</li>)}</ol>
      {op.diagnostic && <p className="state state-attention">{op.diagnostic}</p>}
      <button className="button-quiet" disabled={busy} onClick={() => void operate(async () => {
        setJournal(await managed<S["PreparationOperationRead"]>(`/preparations/${op.id}`));
      })}>Consultar capturas y journal completo</button>
      {journal?.id === op.id && <Evidence title="Plan confirmado, capturas y journal de preparación" value={journal} />}
      {working && <button className="button-quiet" disabled={busy || op.cancel_requested} onClick={() => void control("cancel")}>Cancelar preparación</button>}
      {retry && <button className="button-quiet" disabled={busy} onClick={() => void control("confirm-stopped")}>Comprobar y confirmar escritor detenido</button>}
    </>}
    {!data.prepared && !working && <>
      <label>Modo de instalación<select value={mode} onChange={e => { setMode(e.target.value as "offline" | "network"); setPreview(undefined); setConfirmed(false); }}>
        <option value="offline">Offline: usar wheels locales y caché del hijo</option>
        <option value="network">Red: descargar wheels fijados de PyPI</option>
      </select></label>
      <p className="hint">La caché y el entorno permanecen dentro del hijo. Un fallo detiene la preparación y conserva sus bytes; no se repite ningún comando automáticamente.</p>
      <button disabled={busy || !!op && !retry} onClick={() => void operate(show)}>{retry ? `Revisar nueva intención desde el paso ${next ?? "pendiente"}` : "Revisar plan de preparación"}</button>
    </>}
    {preview && <div className="decision">
      <p>Destino: <code>{preview.plan.root}</code> · modo {preview.plan.mode} · hash <Hash value={preview.plan.preview_sha256} /></p>
      <h3>Archivos del commit técnico</h3>
      {preview.plan.files.map(file => <details key={String(file.path)}><summary><code>{String(file.path)}</code> · <Hash value={String(file.sha256)} /></summary><DiffBlock diff={String(file.diff ?? "")} label={`Archivo nuevo: ${String(file.path)}`} /><details><summary>Contenido completo</summary><pre>{String(file.content)}</pre></details></details>)}
      <h3>Comandos y efectos confirmables</h3>
      <ol>{preview.plan.steps.map((step, n) => <li key={n}><strong>{String(step.label)}</strong>{Array.isArray(step.argv) && <pre>{JSON.stringify(step.argv)}</pre>}</li>)}</ol>
      <Evidence title="Versiones, lock, entorno público, red, límites y commit" value={preview.plan} />
      <label className="check"><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Autorizo estos archivos, comandos, instalación, modo de red y commit dentro del hijo.</label>
      <button disabled={busy || !confirmed} onClick={() => void operate(async () => {
        await createOnce(`/projects/${project}/preparation/confirm`, {
          change: preview.change, preview_sha256: preview.plan.preview_sha256,
        } satisfies S["PreparationConfirmInput"]);
        setPreview(undefined); setConfirmed(false);
      })}>Confirmar preparación Django</button>
    </div>}
  </section>;
}
