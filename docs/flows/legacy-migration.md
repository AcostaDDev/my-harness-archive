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

## Cambios previstos en P008 (D088, sin implementar)

El Flujo A (T009–T012) añade, sobre esta vía y sobre proyectos v1/v2 de este harness, la normalización documental al
layout unificado: inventario de solo lectura, mapa determinista de renombrados y movimientos, propuesta del revisor
para fusionar y adelgazar y un commit confirmado con CAS.

## Fuente en el código

- `core/legacy.py`, `adapters/legacy.py`, `storage/legacy.py`, `storage/observation.py`, `services/observation.py`.
- `core/migration.py`, `adapters/migration.py`, `storage/migration.py`, `services/migration.py`.
