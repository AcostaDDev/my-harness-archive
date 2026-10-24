# P012-T010 — Formateador en perfiles declarados

Fecha: 2026-10-24. Base: `e68fdfa`. **Estado: implementada y verificada offline; sin reanudar T002.**
Decisión: [D194](../DECISIONS.md#d194--p012-t010-formateador-declarativo-optativo-en-local-config-8).
Origen: [alternativas revisadas y elección HITL](P012-T002_PROPUESTA_CONTINUIDAD_RUFF.md), tras D193.

## 1. Elección y alcance

El usuario elige **«Implementar formateador declarativo offline (recomendado)»**. Autoriza la ampliación del
producto con pruebas sintéticas; no otro intento real ni ampliar el techo de Codex o las correcciones.
El fallo anterior sigue siendo una salida del ejecutor rechazada correctamente. Se habilita al operador una
capacidad del motor D133 que el TOML de perfiles declarados de D095 todavía no exponía.

Una sola tarea: lector de configuración, selección de formatos en registro/recetas, ejemplo, tests y documentos.
No se modifica el motor, runner, adaptadores CLI, modelos, migraciones, API, tipos frontend, códec, prompts ni
implementaciones de recetas ligadas a recibos. No se construye/instala un wheel operativo ni se modifica el área real.

## 2. Contrato implementado

Se añade **`local-config-8`**. Solo en él, un perfil declarado admite:

```toml
formatter_argv = ["ruff", "format", "--"]
formatter_paths = ["*.py"]
```

- Ambos campos son opcionales como par: si aparece uno, se exige el otro; presentes deben ser listas no vacías
  de texto válido. Omitir ambos conserva las tuplas vacías del perfil y el comportamiento anterior.
- Argv sin shell, ejecutable como nombre simple, sin operadores/sustituciones y terminado en `--`.
  Los patrones son relativos, sin escapes o duplicados. Se reutilizan las validaciones existentes.
- La composición debe mapear el ejecutable y autorizar el perfil (`authorize_profile_commands = true`).
  Un prefijo de comandos permitido o una autorización exacta no habilitan por sí solos el formateador variable.
- El runner existente registra `formatter-paths`: solo el argv exacto del perfil seguido de archivos regulares
  existentes del checkout; rechaza enlaces, escapes, opciones, directorios, otro cwd, entorno extra u otro argv.
- El motor D133 selecciona archivos cambiados, existentes, coincidentes y permitidos por el contrato. Formatea
  tras el turno del ejecutor y antes de capturar/validar/revisar. Revalidar no formatea; sin coincidencias no ejecuta.
  Conserva su timeout de 120 s, tratamiento de fallos y `formatting_json` con comando, rutas, resultado e identidad.
- La revisión y aceptación observan esos bytes; el commit confirma su evidencia exacta. No se conceden rutas,
  shell o red al agente ni se debilitan las seis validaciones del perfil.

`check-config` añade `formatter_argv`/`formatter_paths` al resumen solo si hay formateador; no expone valores de
entorno. El ejemplo privado pasa a v8 con ambas líneas **comentadas**, para que activarlas sea una elección
expresa del operador y el perfil sin ellas conserve su contenido.

## 3. Compatibilidad y congelación

| Caso | Resultado |
|---|---|
| Configuraciones v1–v7 | Mismas reglas/hashes; v4–v7 siguen rechazando las claves formatter del perfil declarado |
| v8 sin el par | Mismo perfil/contexto y huellas efectivas que v7; cambia el identificador de formato |
| v8 con formateador | Perfil completo en la huella de composición; argv también en la autorización nativa |
| Cambio de argv, patrones o activación | Jobs ya admitidos rechazados/cuarentena antes de procesos; historial e intención intactos |
| CLI v7/v8 | Misma detección por PATH explícito, mínimos, identidad/política congelada y revalidación por intento |
| Presets, trabajo en/es y registro | v8 conserva v5–v7; la selección del proyecto sigue siendo explícita y auditable |
| Recetas | v8 selecciona v2 igual que v6/v7; v5 mantiene v1, sin tocar implementaciones/huellas/recibos |
| Historial de formateo | Ya soportado en formato 8; no hay códec nuevo o reescritura de snapshots |

La separación `AUTOMATIC_FORMATS = (v7, v8)` evita que introducir la nueva versión desactive accidentalmente el
descubrimiento de v7. Registro y mapa de generaciones admiten v8 de forma explícita. No se actualizan los TOML
operativos ni se migra silenciosamente un registro o un job existente.

## 4. Verificación offline

- **28 regresiones nuevas** en `test_declared_formatters.py`: carga sin procesos, resumen, rechazo v4–v7,
  diecisiete configuraciones inválidas, identidad sin formateador y cuarentena por activar/cambiar argv/patrones.
- Recorrido parametrizado con CLI y herramientas **sintéticas**, Git/SQLite temporales y runner nativo real:
  una regla de formato artificial rechaza el resultado sin formateador; al declararlo se ejecuta antes de las
  seis validaciones, se guarda su autorización `formatter-paths`, el revisor ve el registro y el commit contiene
  los bytes formateados. Cero correcciones y solo dos invocaciones de agentes falsos con plan determinista.
  No usa Ruff real ni código/streams privados como fixtures.
- **177 checks dirigidos** existentes/ampliados: perfiles declarados, D133, configuración, registro, recetas,
  descubrimiento CLI y selección de agentes. Incluyen diecisiete casos adicionales de v8 en detección automática
  (carga y todas las parejas/idiomas). Las recetas v1 conservan sus bytes y huellas fijadas.
- **106 checks dirigidos** de motor, comandos, idioma de trabajo, selección por registro v5/v8 y selección de
  recetas por formato; las dos parejas mixtas nuevas del registro v8 pasan hasta commit y cambio posterior.
- **8 unittest correctos**. Aviso existente de deprecación Starlette/httpx; no implica fallo del producto.

Comandos:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_declared_formatters.py
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_declared_profiles.py tests/product/test_profile_formatter.py tests/product/test_local_config.py tests/product/test_project_registry.py tests/product/test_recipe_versions.py tests/product/test_cli_discovery.py tests/product/test_project_agents.py
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_project_agents.py::test_selected_presets_drive_the_plan_and_execution tests/product/test_recipe_v2_preparation.py::test_v5_keeps_v1_and_successors_select_v2_from_the_same_recipe_keys tests/product/test_commands.py tests/product/test_work_language.py tests/product/test_engine.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

La investigación previa de continuidad añade ocho tests existentes, independientes de la ampliación, sobre
presupuesto/revalidación, contexto, checkout sucio, edición CAS y fases. No se contabilizan como regresiones nuevas.
No se ejecutan suites frontend o Alembic: no cambia UI, contrato API ni datos. No se acredita build/wheel instalado,
Ruff real, CLI real, nuevo preflight o éxito de T002.

Comprobación documental final: **12 fases, 7 criterios P012, 10 tareas, 194 decisiones y 658 enlaces/anclas
relativos** válidos en los once Markdown modificados/nuevos. STATE/base/NEXT_STEPS: **13.007/24.576**,
**8.896/12.288** y **24.022/49.152 bytes**. Cuerpos D001–D193 y documentación histórica/pública conservados;
TOML del ejemplo válido como v8. Diff revisado y `git diff --check` correcto.

## 5. Continuación operativa propuesta, todavía sin autorizar

La siguiente tarea vuelve a ser **T002**, con un consentimiento nuevo sobre una propuesta operativa completa.
La alternativa B (un ciclo de corrección y techo Codex 4) no ha sido elegida. Mantener **cero correcciones**,
pareja/modelos/esfuerzos originales y techo T002 **12 Claude/3 Codex**, consumido **7/2**.

Guion que deberá concretarse y revisarse antes de operar:

1. Base del wheel: commit de esta tarea. Construir/verificar offline en `AREA/dist-t010` e instalar en
   `AREA/venv-t010`, con hashes y sin sobrescribir dist/venv anteriores. Conservar cachés/locks verificados;
   una ausencia obliga a parar, sin descargar automáticamente.
2. Crear `AREA/projects/managed-b-t010` desde **`9808fd97…`**, clon local sin optimización/hardlinks, sin
   checkout inicial y después detached en el commit completo. Retirar solo su origin y contrastar árbol/modos;
   no copiar los tres cambios fallidos, ignorados o historiales de SQLite. B/B2 intactos en sus rutas originales.
   Venv Python 3.13.13 y 17 wheels por hash, TMPDIR privado 0700 dentro del nuevo checkout.
3. Nueva copia `AREA/config/harness-local-t010.toml`, formato v8 y 0600. Conservar los perfiles/presets anteriores;
   añadir perfil **python-django-t010** derivado del aprobado, con las mismas preparaciones/validaciones y el
   par formatter mostrado arriba. Nueva composición **django-t010** y presets **claude-t010/codex-t010** con
   rutas del venv/temporal nuevo. Defaults, permisos, modelos/esfuerzos y perfiles viejos sin formateador añadido.
   El formato v8 cambia el identificador de composición vivo de los registros cargados: **no** se promete igualdad
   de todas sus versiones con v7. Los runs guardados conservan sus versiones v7 y no se operan ni reanudan.
4. Preflight explícito y ocho checks iniciales del hijo en verde antes de invocar modelos. Servicio 8024 con
   nueva copia/venv y misma SQLite por vías normales. Registro UI **p012-b-t010**, es/es, composición/presets
   nuevos. Es un proyecto ya documentado: **no repetir la conversación B**.
5. Crear su P001 por UI a partir de ROADMAP/NEXT_STEPS. Confirmar un commit documental preparatorio por UI/CAS:
   AGENTS refleja perfil/composición y formateador nuevos; DECISIONS añade la elección expresa del operador.
   No editar código, archivos históricos o bloques gestionados a mano; no reparar un resultado previo.
   Adoptar los hashes que corresponda y comprobar checkout limpio antes de la tarea.
6. Misma tarea y tres rutas: plan agente → una ejecución → formateador nativo → seis validaciones/JUnit →
   revisión → aceptación exacta y commit solo si procede. Previsión **2 Claude + 1 Codex**, acumulado **9/3**;
   sin turnos B, correcciones, reenvío idempotente adicional o cierre de P001. Parada al primer fallo.
7. Servicio detenido al terminar, evidencia saneada, contadores e integridad/conservación. T003/T004, red extra,
   configuración global, publicación, tags/push y cualquier segundo intento quedan fuera.

Este guion no es consentimiento ni acredita la preparación futura. Falta fijar comandos, hashes/deltas exactos,
revisión documental y autorización operativa. Esta sesión no crea esos destinos ni consume el saldo real 5/1.
