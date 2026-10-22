# Flujo — preferencias de idioma

Ajustes globales de la instalación (P011-T007, D166): idioma visual mutable y default de trabajo para futuras altas.
El visual se congela en cada job al admitirlo; cambiarlo rige solo las admisiones posteriores.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant UI as Interfaz
    participant API as API gestionada
    participant DB as SQLite
    UI->>API: GET /preferences (tras la sesión, al recuperar el foco y en cada consulta de sesión)
    API->>DB: lee la fila singleton (no la crea ni la repara)
    API-->>UI: formato, versión, ui_language, default_work_language, estado
    U->>UI: elige idiomas en Preferencias
    UI->>API: PUT /preferences (expected_version, Idempotency-Key)
    alt versión vigente
        API->>DB: lock de escritura; fila version+1 y evento encadenado
        API-->>UI: preferencias guardadas; la UI cambia de idioma
    else otra ventana guardó antes
        API-->>UI: 409 preferences_conflict; la UI relee y pide revisar
    end
    U->>API: nueva tarea, turno u operación (Idempotency-Key)
    API->>DB: misma transacción: lee preferencias y sella language_context en el job
    Note over API,DB: reanudar un run copia el valor de su primer job; nunca se recaptura
```

- Fila inválida (editada fuera del servicio): la lectura devuelve `en` con estado `invalid`, la UI avisa y toda
  admisión nueva responde 409 `preferences_invalid` hasta guardar de nuevo. Ningún GET la repara.
- `default_work_language` todavía no lo consume ningún alta: T008 lo usará como selección inicial, sin cambiar
  proyectos existentes. La directiva de idioma al agente llega con T009; hoy el visual congelado es procedencia.
- CLI: `--ui-language en|es` solo para esa invocación; sin él, preferencias de la base existente (lectura en solo
  lectura) o `en`. No guarda nada.
- Restauración de consulta: lee preferencias; el middleware rechaza el PUT como cualquier escritura.

## Fuente en el código

- `storage/preferences.py`, `storage/managed.py::_language`, `api/managed.py` (`/preferences`), `api/session.py`.
- `i18n/` (catálogos del servicio), `cli.py::cli_language`, `launcher.py`.
- `frontend/src/{i18n.ts,i18n/*.json,Language.tsx,pages/Preferences.tsx}`.
