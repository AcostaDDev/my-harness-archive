# Flujo — harness anterior: observación y paso a gestionado

Un checkout con `.harness/runs` de un harness anterior (ReferenceProject) se observa en lectura y puede pasar a modo
gestionado (D012–D014, D027). Ninguna de las dos vías reescribe hoy los documentos del proyecto.

```mermaid
flowchart TD
    A["Checkout con .harness/runs"] --> B["legacy-import: índice SQLite por ruta y hash"]
    B --> C["Navegación y observación opt-in (polling, SSE)"]
    C --> D["Vista previa de migración sin escrituras"]
    D --> E["Activación: copia inmutable del historial fuera del checkout"]
    E --> F["Marcador .harness/managed-mode.json"]
    F --> G["Modo gestionado: el motor rechaza actividad legacy posterior"]
    G --> H["Reversión opcional: exportación verificada y retirada del marcador"]
```

## Estados de la activación

```mermaid
stateDiagram-v2
    [*] --> PREPARING
    PREPARING --> ACTIVE: copia, manifiesto y marcador verificados
    PREPARING --> FAILED
    ACTIVE --> REVERTING: reversión confirmada
    REVERTING --> REVERTED
    REVERTED --> [*]
    FAILED --> [*]
```

## Flujo A en P008 (D088)

El Flujo A (T009–T012) añade, sobre esta vía y sobre proyectos v1/v2 de este harness, la normalización documental al
layout unificado. Implementados: el inventario de solo lectura (P008-T009, D096), el mapa determinista de
renombrados, movimientos y composición de decisiones (P008-T010, D097) y la conversación `project_import` en la que
el revisor propone fusiones y adelgazamiento como borradores privados (P008-T011, D098). Pendiente: la vista previa y
el commit confirmado con CAS (T012).

```mermaid
flowchart TD
    A["Proyecto registrado"] --> B{"Git, HEAD con archivos y checkout limpio"}
    B -- no --> R["Rechazo con diagnóstico, sin escrituras"]
    B -- sí --> C["Árbol de HEAD: Markdown raíz, docs/ y .harness/ sin runs"]
    C --> D["Blobs por cat-file; enlaces y submódulos rechazados sin leer"]
    C --> E[".harness/runs por lstat (D027)"]
    D --> F["Clase y regla por entrada, origen, fases, instrucciones y bloques"]
    E --> F
    F --> G["Inventario con inventory_sha256"]
    G --> M["Mapa: bytes comprobados contra el inventario"]
    M --> N["Movimientos por regla: alias, renumeración, phase-000, artefactos de fase"]
    M --> O["Decisiones inequívocas: archivo en phase-000 y sección en DECISIONS"]
    N --> P{"¿Destino libre en el árbol original?"}
    O --> P
    P -- no --> Q["review: target-conflict"]
    P -- sí --> S["Mapa con árbol resultante, review, foreign, missing y map_sha256"]
    Q --> S
    S --> T["Conversación project_import: inventario y mapa congelados en SQLite"]
    T --> U["Turno: ¿checkout igual al inventariado? Textos del árbol resultante y borradores congelados"]
    U --> V["Revisor de solo lectura (rol definition): borradores, preguntas y pendientes"]
    V --> W{"¿Esquema y rutas D088 válidos, origen y área sin cambios?"}
    W -- no --> X["Turno FAILED sin fallback; nada se escribe"]
    W -- sí --> Y["Propuestas; aplicar o editar con CAS en import-drafts/ junto a SQLite"]
    Y --> Z{"GET …/import: ¿preguntas bloqueantes resueltas o aplazadas, documentos y límites D088?"}
    Z -. "T012, pendiente" .-> H["Vista previa y commit confirmado"]
```

Límite (D098): con `.harness/runs` sin activar, la guardia de modo D027 rechaza los turnos de la conversación; la
conversación y su estado sí se pueden crear y consultar. D099 fija el orden para T012: primero la activación D027 y
después la importación, con el marcador de la activación viva tolerado por el inventario y fuera del commit.

## Fuente en el código

- `core/legacy.py`, `adapters/legacy.py`, `storage/legacy.py`, `storage/observation.py`, `services/observation.py`.
- `core/migration.py`, `adapters/migration.py`, `storage/migration.py`, `services/migration.py`.
- `core/project_import.py`, `adapters/project_import.py` (inventario del Flujo A).
- `core/project_normalization.py` (mapa de normalización del Flujo A).
- `core/engine/import_conversation.py`, `storage/import_drafts.py`, `storage/planning.py` (conversación del Flujo A).
