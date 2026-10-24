# Flujo — idioma de trabajo por proyecto

P011-T008 (D167; contrato [T001 §2/§4](../archive/phase-011/P011-T001_CONTRATO_APERTURA.md#2-autoridad-persistencia-y-controles-de-idioma)).
El idioma de trabajo (`en`/`es`) rige documentación, planes y código que escriben los agentes en un proyecto. Se elige
una vez por raíz canónica y no cambia; el idioma visual es una preferencia global aparte
([preferencias](language-preferences.md)). Desde T009 (D169) el par del job llega al agente como directiva y los
documentos que genera el harness usan el idioma de trabajo ([abajo](#directiva-y-documentos-generados-p011-t009-d169)).

```mermaid
flowchart TD
    D["Default global de trabajo (Preferencias)"] --> SEL["Alta: la UI inicializa la selección con el default"]
    SEL --> REG{"¿Cómo llega el proyecto?"}
    REG -- "registrar checkout existente (B)" --> RP["POST /registry/preview con work_language"]
    REG -- "crear carpeta nueva" --> CP["POST /project-creations/preview con work_language"]
    REG -- "TOML local-config-6/7" --> T6["[[projects]].work_language; la carga no escribe"]
    REG -- "proyecto sin valor (TOML 1–5, v6/v7 sin clave, registros previos)" --> NO["Sin idioma confirmado"]
    RP --> H["Vista previa: valor elegido + default y versión (procedencia, fuera del hash)"]
    CP --> H
    H --> X{"¿La raíz ya tiene otro valor?"}
    X -- sí --> IM["409 work_language_immutable"]
    X -- no --> CF["Confirmar con el hash: fila project_work_languages en la misma transacción del alta"]
    T6 --> ST["Arranque del servicio: asocia una vez (source toml)"]
    ST --> Y{"¿SQLite ya tenía otro valor?"}
    Y -- sí --> STOP["El servicio no arranca: diagnóstico de inmutabilidad"]
    Y -- no --> OK["Contexto del proyecto con work_language"]
    CF --> OK
    NO --> G["Toda admisión nueva: 409 work_language_required"]
    NO --> MP["Ajustes: POST /projects/{id}/work-language/preview"]
    MP --> MB{"¿Trabajo sin terminar o pendiente?"}
    MB -- sí --> MW["Se resuelve primero; la confirmación se rechaza (pending_work)"]
    MB -- no --> MC["Confirmar con hash y motivo: ausente → valor (source migration)"]
    MC --> OK
    OK --> J["Cada job nuevo sella language-context-1: visual actual + trabajo + procedencia"]
    J --> A["Cada intento copia el par del job; las continuaciones heredan el del primer job"]
```

- Inmutabilidad: actualizar o dar de baja un registro con `work_language` en el cuerpo devuelve 409
  `work_language_immutable`; la reapertura (baja y nuevo registro de la misma raíz) solo admite el valor original y
  conserva la fila original. Un TOML v6/v7 con otro valor detiene el arranque; sin la clave, el proyecto lee el valor ya
  confirmado. Los ajustes del proyecto solo lo muestran.
- Cambiar el default de trabajo entre vista previa y confirmación no altera el valor confirmado: el hash sella el
  valor elegido y la asociación existente; el default y su versión quedan como procedencia en `confirmation`.
- La confirmación explícita no traduce, renombra ni inspecciona archivos; no se infiere el idioma del contenido.
- Admisión: el par se lee en la transacción que admite cada job nuevo (tarea, turno, check, commit, operación
  documental, preparación…). Reintentos, revalidaciones y reanudaciones copian el `language_context` del primer job
  del run, también `ui-language-1` o null de jobs anteriores; no reciben trabajo inventado.
- Un contexto de proyecto obsoleto con otro `work_language` (no debería ocurrir: la fila no cambia) se rechaza.
- Downgrade de `0025` rechazado si hay alguna asociación. Backup y restauración de consulta la conservan.
- Recetas: en `local-config-6` y `local-config-7`, `[recipes]` elige las recetas v2, que preparan con el idioma de la fila y lo sellan
  en plan y recibo; sin fila, la preparación se rechaza antes de efectos ([flujo](project-preparation.md#recetas-v2-por-idioma-de-trabajo-p011-t020-d168), D168).

## Directiva y documentos generados (P011-T009, D169)

```mermaid
flowchart TD
    J["Job admitido: language-context-1 (visual + trabajo)"] --> S["Supervisor: lee solo el par sellado del job"]
    S --> R["render_attempt: plantilla editable (inglés) + directiva language-directive-1 + esquema del motor"]
    R --> V{"¿Par válido y trabajo igual al del contexto congelado?"}
    V -- no --> X["Parada en prompts antes de invocar"]
    V -- sí --> P["Prompt por stdin (Codex exec / Claude --print); snapshot con language y su hash"]
    S --> N["Job sin par (anterior a D167 o ui-language-1): prompt sin directiva, como antes"]
    W["Idioma de trabajo del contexto congelado"] --> D["Bloques, plantilla D088, REVIEW/SUMMARY, DEFINITION, transición, SUMMARY de B"]
    W --> T["Texto de tarea desde chat y etiquetas de la reconciliación"]
    C["Contexto sin trabajo (anterior a D167)"] --> E["Bytes españoles históricos; texto de chat en inglés histórico"]
```

- La directiva incluye «Respond to the user in {visual}. Write project documentation and code in {trabajo}.», los
  campos V (al usuario) y W (documentos/código) de cada rol según T001 §4, los valores T literales y las etiquetas
  D088 del idioma de trabajo. Precede a cualquier instrucción lingüística de las plantillas, que siguen editables.
- Cambiar el visual rige solo jobs nuevos: reintentos y revalidaciones heredan el par del primer job.
- Mensajes de commit y trailers siguen técnicos en inglés (HITL); los parsers leen etiquetas en/es.

## Fuente en el código

- `core/engine/language.py` (directiva), `core/engine/prompts.py::render_attempt`, `services/managed.py`
  (`job_language`), `core/engine/document_text.py` y `documents.py` (vocabulario en/es).
- `storage/work_language.py` (fila, captura del par), `storage/registry.py::confirm_work_language`,
  `storage/managed.py::_language`/`agent_started`.
- `services/project_registry.py` (vista previa/sello), `services/project_creation.py` (`project-creation-2`),
  `services/work_language.py` (confirmación explícita), `services/managed_runtime.py` (arranque TOML y contexto),
  `services/local_config.py` (`local-config-6/7`).
- `api/managed.py` (`/projects/{id}/work-language`, códigos 409), `api/schemas.py`.
- `frontend/src/WorkLanguage.tsx`, `pages/Registry.tsx`, `pages/Settings.tsx`.
