# Flujo — ciclo de vida de una fase

Estado vigente (D032, D034, H6.3) y cambio aprobado para P008 (D088).

## Estados de la fase (implementado)

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: bootstrap, transición o alta por API
    ACTIVE --> CHECKING: check (job bajo el lock)
    NEEDS_RECONCILIATION --> CHECKING
    READY_TO_CLOSE --> CHECKING
    BLOCKED --> CHECKING
    CHECKING --> READY_TO_CLOSE: READY
    CHECKING --> NEEDS_RECONCILIATION: REVISE
    CHECKING --> BLOCKED: BLOCKED o preguntas abiertas
    CHECKING --> ACTIVE: NOT_READY o fallo (estado previo)
    ACTIVE --> BLOCKED: pregunta bloqueante
    BLOCKED --> ACTIVE: preguntas respondidas
    NEEDS_RECONCILIATION --> ACTIVE: documentos adoptados por hash
    READY_TO_CLOSE --> CLOSING: autorización de cierre sobre el READY mostrado
    CLOSING --> CLOSED: tag sobre el HEAD evaluado
    CLOSING --> NEEDS_RECONCILIATION: vínculo READY obsoleto (STALE)
    ACTIVE --> ABANDONED: abandono explícito
    CLOSED --> [*]
    ABANDONED --> [*]
```

Una enmienda crea una versión nueva de la definición e invalida READY y lotes. El lote desatendido encadena
tarea → commit → siguiente tarea, pero nunca comprueba ni cierra.

## Cierre y transición hoy (H6.3)

```mermaid
flowchart TD
    A["Check READY"] --> B["Cerrar: autorización propia, tag, sin tocar documentos"]
    B --> C{"¿Plan de N+1?"}
    C -- "usuario o phase_planning" --> D["Vista previa de la transición"]
    C -- "sin más fases en ROADMAP" --> D
    D --> E["Confirmar hash, motivo e Idempotency-Key"]
    E --> F["Commit único: archive/phase-NNN con STATE, NEXT_STEPS, REVIEW y SUMMARY"]
    F --> G["STATE fresco con base acumulada, NEXT_STEPS con el plan, ROADMAP regenerado"]
    G --> H["Fase N+1 ACTIVE con documentos adoptados"]
```

## Cierre previsto en P008 (D088, tarea P008-T004, sin implementar)

```mermaid
flowchart TD
    A["Check READY"] --> B["Cerrar con autorización: tag sobre el HEAD evaluado"]
    B --> C["Mismo flujo, un commit conciliable"]
    C --> D["docs/archive/phase-NNN: STATE, NEXT_STEPS, REVIEW, SUMMARY y el contenido de docs/phase/"]
    D --> E["STATE: base acumulada compacta y fase activa N+1"]
    D --> F["NEXT_STEPS: objetivo de N+1 tomado de ROADMAP, sin tareas"]
    D --> G["ROADMAP: N completada con enlace a su archivo"]
    D --> H["docs/phase/ vacía"]
    F --> I["Planificación de N+1 posterior (phase_planning o usuario)"]
```

## Fuente en el código

- `core/engine/phases.py`, `storage/phases.py` (check, cierre, preguntas, enmiendas, abandono, lote).
- `core/engine/document_ops.py` (`preview_transition`), `storage/transition.py`, `core/engine/documents.py`
  (`render_review`, `render_summary`, `render_roadmap`).
- Plantillas `close-phase.md` y `reconcile-phase.md`.
