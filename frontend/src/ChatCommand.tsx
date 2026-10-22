import type { S } from './managed-api';
import { phaseSection } from './chat-commands';
import { Link } from './navigation';
import { PhaseCreate, PhaseDetail } from './Phases';
import { Empty, Evidence, Loading, Stale, Status, usePoll } from './ui';
import { useWorkspace } from './workspace';
import { Tests } from './Tests';

/** Reuses the actual action controls, including their CAS, confirmation and pending request handling. */
export function ChatCommand({ command }: { command: S['ChatCommandRead'] }) {
  const { project, refresh } = useWorkspace();
  const phases = usePoll<S['PhaseSummaryRead'][]>(`/projects/${project}/phases`, 3000, refresh);
  if (command.name === 'tests') return command.run_id ? <CommandTests run={command.run_id} />
    : <Empty title="Sin validaciones de tarea"><p>Elige una tarea como contexto o ejecuta primero una tarea normal.</p></Empty>;
  if (!phases.data) return phases.error ? <p role="alert">{phases.error}</p> : <Loading />;
  const phase = phases.data.find(p => p.code === command.phase_code);
  if (command.name === 'abrir-fase') {
    if (phases.error) return <p role="alert">{phases.error}</p>;
    const open = phases.data.find(p => !['CLOSED', 'ABANDONED'].includes(p.status));
    if (open) return <p className="state state-attention">La fase <Link to={{ name: 'phase', project, phase: open.code }}>{open.code}</Link> sigue abierta. Ciérrala antes de abrir la siguiente.</p>;
    return <PhaseCreate />;
  }
  if (!phase) return <Empty title="No hay fase de contexto"><p>Crea una fase con /abrir-fase o elige una conversación con fase.</p></Empty>;
  return <CommandPhase code={phase.code} command={command} />;
}

function CommandPhase({ code, command }: { code: string; command: S['ChatCommandRead'] }) {
  const { project, refresh } = useWorkspace();
  const phase = usePoll<S['PhaseRead']>(`/projects/${project}/phases/${encodeURIComponent(code)}`, 1500, refresh);
  if (!phase.data) return phase.error ? <p role="alert">{phase.error}</p> : <Loading />;
  return <div className="chat-command-result">
    <p>Fase <Link to={{ name: 'phase', project, phase: code }}>{code}</Link> · versión actual {phase.data.version} <Status kind="phase" value={phase.data.status} /></p>
    <Stale error={phase.error} />
    {phase.data.version !== command.phase_version && <p className="hint">La fase cambió desde el comando. Los controles muestran la versión actual y exigen su confirmación.</p>}
    <PhaseDetail phase={phase.data} stale={!!phase.error} section={phaseSection(command.name)} />
    {command.name === 'estado' && <Evidence title="Preguntas, tareas y evidencia de fase" value={{ tasks: phase.data.tasks, questions: phase.data.questions, ready: phase.data.ready }} />}
  </div>;
}

function CommandTests({ run }: { run: string }) {
  const { refresh } = useWorkspace();
  const detail = usePoll<S['ManagedRunRead']>(`/runs/${encodeURIComponent(run)}`, 2000, refresh);
  if (!detail.data) return detail.error ? <p role="alert">{detail.error}</p> : <Loading />;
  const latest = detail.data.history.latest_cycle;
  return <div><p>Última validación de <Link to={{ name: 'run-short', run }}>{detail.data.task_id}</Link>. Solo consulta; no ejecuta tests.</p>
    <Stale error={detail.error} />
    {latest?.validation ? <Tests runId={run} cycle={latest.number} validation={latest.validation} /> : <p>No hay validación observada.</p>}
  </div>;
}
