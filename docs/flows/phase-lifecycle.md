# Flujo — ciclo de vida de una fase

Implementado: D032, D034 y cierre unificado de D088/P008-T004 (D091).

## Estados de la fase

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: bootstrap, cierre anterior o alta por API
    ACTIVE --> CHECKING: check bajo el lock
    NEEDS_RECONCILIATION --> CHECKING
    READY_TO_CLOSE --> CHECKING
    BLOCKED --> CHECKING
    CHECKING --> READY_TO_CLOSE: READY
    CHECKING --> NEEDS_RECONCILIATION: REVISE, STATE mayor de 24 KiB o base mayor de 12 KiB
    CHECKING --> BLOCKED: BLOCKED o preguntas abiertas
    CHECKING --> ACTIVE: NOT_READY o fallo (estado previo)
    ACTIVE --> BLOCKED: pregunta bloqueante
    BLOCKED --> ACTIVE: preguntas respondidas
    NEEDS_RECONCILIATION --> ACTIVE: documentos adoptados por hash
    READY_TO_CLOSE --> CLOSING: autorización sobre el READY mostrado
    ACTIVE --> CLOSING: abandono confirmado
    BLOCKED --> CLOSING: abandono confirmado
    NEEDS_RECONCILIATION --> CLOSING: abandono confirmado
    CLOSING --> CLOSED: tag y commit de archivo registrados
    CLOSING --> ABANDONED: archivo registrado, sin tag
    CLOSING --> NEEDS_RECONCILIATION: vínculo obsoleto
    CLOSED --> [*]
    ABANDONED --> [*]
```

Una enmienda conserva la definición anterior e invalida READY y lotes. El lote desatendido encadena
`tarea → commit → siguiente tarea`, pero nunca comprueba ni cierra. Un cierre interrumpido mantiene la intención
sellada: tras confirmar el escritor detenido, una nueva petición explícita reanuda el mismo run y commit.

## Cierre y archivo unificados

```mermaid
flowchart TD
    A["Check READY y autorización propia"] --> B["Verificar checkout limpio, base documental y ausencia de trabajo pendiente"]
    B --> C["Congelar archivo y sucesora desde ROADMAP; rechazar colisiones y enlaces"]
    C --> D["Job bajo el lock: reobservar READY y sellar la intención de commit"]
    D --> E["Persistir intención del tag y crearlo sobre el HEAD evaluado"]
    E --> F["CAS de documentos y artefactos: solo bytes anteriores o sellados"]
    F --> G["Un commit: STATE, NEXT_STEPS, REVIEW, SUMMARY y docs/phase/ en archive/phase-NNN/"]
    G --> H["STATE fresco con base compacta; NEXT_STEPS con objetivo y criterios de N+1, sin tareas"]
    H --> I["ROADMAP: N completada y enlace a Archivo; docs/phase/ vacía"]
    I --> J["SQLite registra el cierre y crea N+1 ACTIVE con sus documentos adoptados, atómicamente"]
    J --> K["Planificar N+1 después: texto del usuario o propuesta phase_planning"]
    K --> L["Vista previa y confirmación del hash: commit documental y nueva definición D034"]
```

El abandono usa el mismo archivo y commit, sin exigir READY ni crear tag. Si ROADMAP no tiene sucesora, se archiva y
se deja indicado que no hay fase activa. STATE y NEXT_STEPS se archivan por bytes; también los artefactos binarios y
las subcarpetas de `docs/phase/`. REVIEW y SUMMARY se generan desde la instantánea SQLite.

Las nuevas transiciones separadas H6.3 se rechazan. Sus intenciones ya selladas conservan la vía de recuperación;
los endpoints se mantienen hasta su retirada de API/UI en T006. Nunca se recalcula una intención pendiente ni se
reescriben sus snapshots. El prompt de planificación usa el destino exacto del contexto: la fase ACTIVE vacía, o la
siguiente en conversaciones anteriores (T005, D092). Propone NEXT_STEPS y exige confirmación propia del plan; no
autoriza otra transición. La adaptación de UI sigue pendiente de T006.

## Fuente en el código

- `core/engine/phases.py`, `storage/phases.py`: check, cierre, preguntas, enmiendas, abandono y lote.
- `storage/closure.py`, `core/engine/document_ops.py`: preparación, intención y adopción del archivo.
- `storage/phase_plan.py`, `storage/planning.py`: plan posterior confirmado y conversación sobre la fase activa vacía.
- `storage/transition.py`: conciliación de transiciones antiguas.
- `core/engine/documents.py`: REVIEW, SUMMARY y proyecciones de STATE, NEXT_STEPS y ROADMAP.
