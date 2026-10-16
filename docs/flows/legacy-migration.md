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
layout unificado. Implementado: el inventario de solo lectura (P008-T009, D096). Pendientes: el mapa determinista de
renombrados y movimientos (T010), la propuesta del revisor para fusionar y adelgazar (T011) y un commit confirmado
con CAS (T012).

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
    G -. "T010–T012, pendientes" .-> H["Mapa, propuesta del revisor y commit confirmado"]
```

## Fuente en el código

- `core/legacy.py`, `adapters/legacy.py`, `storage/legacy.py`, `storage/observation.py`, `services/observation.py`.
- `core/migration.py`, `adapters/migration.py`, `storage/migration.py`, `services/migration.py`.
- `core/project_import.py`, `adapters/project_import.py` (inventario del Flujo A).
