# P008-T017 — Referencias vigentes

Fecha: 2026-10-17. Resuelve H4 de la [revisión de salida](P008_REVISION_SALIDA.md), tras T016.
Decisión: [D106](../DECISIONS.md#d106--p008-t017-referencias-vigentes-sin-cambiar-contratos).

## Resultado y contraste

- SPECIFICATION F11: cierre y UI implementados (D091/D093); F18: perfiles implementados (D095), con el ejemplo
  Django aún pendiente de confirmación sobre el proyecto del usuario.
- ARCHITECTURE: `cli-12` contrastado con `adapters/cli_agents.py`; formatos de configuración y perfiles con
  `services/local_config.py` (`REGISTRABLE` admite 3/4); `document_layout = "d088-9"` ya estaba actualizado por
  T016 y se conserva. Se corrige también la tabla de módulos, que aún excluía los perfiles declarados del TOML.
- `serve --config`, diagnóstico del registro y Home/Registry: v4 visible junto a la compatibilidad vigente.
- Prompts: `core/engine/phases.py` usa `close-phase` para el check; `storage/phases.py` usa `reconcile-phase`
  para construir el contrato de una tarea documental. Se explican ambos usos y la confirmación independiente del
  cierre. `bootstrap-project` se identifica como plantilla histórica de la creación v1 retirada (D093).
- Se aclara que el rol `definition` redacta o analiza AGENTS como evidencia (D094/D098/D102), y que el control
  de carga automática documentado en `flows/task-run.md` se introdujo en `cli-11`. No cambia ningún flujo ni diagrama.
- STATE, NEXT_STEPS, ROADMAP e índice de decisiones actualizados. Las decisiones anteriores y registros de
  entregas/revisión permanecen intactos; documentan lo observado en su fecha.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_launcher.py
  tests/product/test_project_registry.py tests/product/test_prompts.py`: 52 correctas; solo el aviso conocido
  de Starlette/httpx. Fixtures temporales y agentes falsos.
- Ayuda de `serve --help` comprobada invocando el parser: muestra v4 y lectura de 1–3, sin iniciar el servicio.
- `node --test frontend/tests/*.test.mjs`: 75 correctas.
- `npm --prefix frontend run build`: TypeScript y Vite correctos; aviso de tamaño de chunks superior a 500 kB.
- 34 Markdown activos/raíz/phase/flows: 379 enlaces relativos y anclas correctos. Presupuestos de instrucciones,
  STATE/base y NEXT_STEPS correctos; parsers con 106 decisiones, ocho fases y diecisiete tareas.
- Diff revisado y `git diff --check` correcto; sin cambios en diagramas ni artefactos generados.
- Sin tests nuevos: el cambio es de textos reversibles. Sin suite pytest completa, Alembic ni regeneración
  de OpenAPI: no cambian lógica operativa, esquema ni contratos. Sin comprobación visual de la UI.
- Sin ejecución del harness sobre este repositorio, proveedores reales, smokes, push, publicación, subagentes
  ni cambios de configuración global.

## Continuidad

Repetir la revisión de salida de P008 sobre las correcciones T016/T017. Esta tarea no declara la fase lista
para cerrar; cierre y archivo quedan para una operación posterior.
