# Flujo — ejecución de una tarea

Recorrido de un run `task` desde que se encola hasta el commit del harness (D015–D026, D047, D052). El revisor
planifica y revisa en solo lectura; el ejecutor es el único escritor; el commit es una acción separada.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant API as API /api/managed
    participant DB as SQLite
    participant S as Supervisor
    participant E as Motor (core/engine)
    participant R as Revisor (CLI, solo lectura)
    participant X as Ejecutor (CLI, escritor)
    participant G as Git del checkout
    U->>API: encolar tarea (Idempotency-Key)
    API->>DB: run QUEUED + job QUEUED
    S->>DB: reclamar job (lease, lock del checkout)
    S->>E: run con contexto, perfil y versiones congelados
    E->>G: captura previa (checkout limpio en v2)
    alt plan determinista suficiente
        E->>E: contrato desde NEXT_STEPS
    else planificación del revisor
        E->>R: plan-task (sesión nueva)
        R-->>E: contrato + selección del ejecutor
    end
    loop hasta ACCEPT, BLOCKED o límite de revisiones
        E->>X: execute-task o revise-task (sesión nueva)
        X->>G: edita dentro de las rutas permitidas
        E->>G: evidencia (árbol, diff, fingerprint)
        E->>E: rutas, validaciones del perfil y JUnit
        E->>R: review-task con diff y validaciones
        R-->>E: ACCEPT, REVISE o BLOCKED
    end
    E->>DB: acceptance_ready, stopped, blocked o revision_limit
    S->>DB: job DONE y lock liberado
    U->>API: confirmar commit (hash mostrado)
    API->>DB: job commit QUEUED
    S->>G: CommitIntent sellado y commit con CAS
    S->>DB: COMMITTED + bloques gestionados (v2)
```

## Estados del run

```mermaid
stateDiagram-v2
    [*] --> QUEUED
    QUEUED --> ACTIVE: supervisor reclama el job
    ACTIVE --> PLANNING
    PLANNING --> EXECUTING
    EXECUTING --> VALIDATING
    VALIDATING --> REVIEWING
    REVIEWING --> EXECUTING: REVISE dentro del límite
    REVIEWING --> ACCEPTANCE_READY: ACCEPT y aceptación elegible
    REVIEWING --> BLOCKED: BLOCKED
    REVIEWING --> REVISION_LIMIT: límite agotado
    ACTIVE --> STOPPED: parada con etapa y motivo
    ACTIVE --> REFUSED: guardia antes de efectos
    ACTIVE --> RECOVERY_REQUIRED: lease vencido o fallo incierto
    RECOVERY_REQUIRED --> INTERRUPTED: confirmación del escritor detenido
    STOPPED --> QUEUED: revalidar o reintentar (acción explícita)
    ACCEPTANCE_READY --> COMMITTING: job commit
    COMMITTING --> COMMITTED
    COMMITTED --> [*]
```

`PREPARING` y `VALIDATING` son etapas de checkpoint; los roles `phase`, `chat`, `definition` y `planning` usan
`CHECKING` o `ANSWERING`. El job sigue `QUEUED → ACTIVE → DONE | REFUSED | RECOVERY_REQUIRED → INTERRUPTED`; un
intento sin resultado al confirmar la parada queda `INTERRUPTED` sin reintento automático.

## Fuente en el código

- `core/engine/workflow.py` (bucle plan → ejecución → validación → revisión), `core/engine/contracts.py`,
  `core/engine/planning.py`, `core/engine/acceptance.py`, `core/engine/commit.py`.
- `storage/managed.py` (cola, lease, lock, estados), `services/managed.py` (supervisor), `adapters/cli_agents.py`,
  `adapters/commands.py`, `adapters/git.py`.
- Bloques gestionados en el commit: `core/engine/documents.py` (ver [documentos](documents.md)).
