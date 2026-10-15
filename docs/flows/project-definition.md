# Flujo — creación de un proyecto (definición conversacional)

Proyecto nuevo en una carpeta vacía con el contrato documental v2 (D072, D075, D082). El agente nunca escribe: el
harness aplica borradores confirmados con CAS y el commit raíz sigue el bootstrap D037.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant API as API planning
    participant DB as SQLite
    participant R as Revisor (definition, solo lectura)
    participant D as Carpeta destino
    U->>API: brief Markdown (máx. 256 KiB)
    API->>DB: conversación definition con brief congelado por hash
    loop turnos
        U->>API: mensaje
        API->>DB: turno QUEUED con contexto congelado (brief, borradores y hashes, ediciones del usuario)
        DB->>R: define-project (sesión nueva)
        R-->>DB: respuesta, preguntas, borradores completos y pendientes
        U->>API: aplicar borrador (confirmación y hash)
        API->>D: escritura con CAS sobre el hash leído en el turno
        U->>D: edición en su editor (se detecta por hash en el turno siguiente)
    end
    U->>API: vista previa de aceptación
    API-->>U: documentos íntegros, archive/phase-000, P001 y bloqueos
    U->>API: confirmar (hash, motivo, Idempotency-Key)
    API->>DB: job bootstrap con intención sellada
    DB->>D: commit raíz con esos bytes exactos
    DB->>DB: P001 ACTIVE y documentos adoptados
```

Bloquean la aceptación: documentos obligatorios ausentes, ROADMAP sin fases, P001 sin objetivo y criterios,
NEXT_STEPS sin una tarea P001-TNNN válida, preguntas bloqueantes abiertas sin aplazar o archivos ajenos a la plantilla.

## Cambios previstos en P008 (D088, sin implementar)

- La plantilla incorpora `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs/DDBB-DIAGRAM.md` (o «Sin persistencia»),
  `docs/flows/*.md` y `docs/phase/`; desaparecen `decisions/`, `architecture/` y `research/` (T002, T005).
- La creación v1 (formulario D037/H4.2) se retira; solo queda esta conversación (T002, T006).
- Un repositorio con contenido entra por los flujos de importación A o B (T009–T015).

## Fuente en el código

- `core/engine/definition.py`, `storage/planning.py`, `adapters/bootstrap.py`, `storage/bootstrap.py`.
- Plantillas `define-project.md` y `plan-phase.md`; `core/engine/documents.py` (`skeleton`).
