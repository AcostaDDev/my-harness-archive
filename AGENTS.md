# my_harness — instrucciones para agentes

Harness Local: aplicación local que orquesta agentes de desarrollo. Este repositorio se desarrolla a mano con Codex y
Claude Code; los roles revisor y ejecutor describen el producto, no estas sesiones. Ambas herramientas pueden analizar,
implementar y revisar cuando el usuario lo pide.

## Discovery al empezar una sesión

1. `docs/STATE.md`: base acumulada y fase activa.
2. `docs/NEXT_STEPS.md`: tareas de la fase activa y siguiente tarea.
3. `docs/ROADMAP.md`: sección de la fase activa.
4. `docs/SPECIFICATION.md` y `docs/ARCHITECTURE.md`: solo las secciones que afecten a la tarea.
5. `docs/DECISIONS.md`: las decisiones que cite la tarea; el índice, para buscar precedentes.
6. `docs/DDBB-DIAGRAM.md` y `docs/flows/` si la tarea toca datos o flujos.
7. `docs/archive/` solo cuando un documento lo cite.

## Reglas inquebrantables

- No inventar fuera de la especificación ni de lo decidido. Ante una incongruencia entre documentos, o entre
  documentos y código, preguntar antes de cambiar el diseño. Los detalles reversibles se resuelven con criterio.
- Paridad: un cambio de modelos o migraciones actualiza `docs/DDBB-DIAGRAM.md`; un cambio de flujo, `docs/flows/`,
  en la misma tarea.
- No ejecutar el harness sobre este repositorio ni lanzar agentes, proveedores, smokes, push o publicación sin
  autorización explícita. No modificar la configuración global del usuario.
- ReferenceProject (`$HOME/Documents/projects/reference_project`) solo se lee. Fixtures siempre sintéticos: sin runs,
  credenciales ni datos privados.
- Una tarea acotada cada vez. No descartar cambios ajenos; si otra sesión usa el checkout, revisar el estado antes de
  editar. Commits solo cuando el usuario los pide.
- Nunca dar por implementado lo que solo está diseñado. Historiales y snapshots congelados no se reescriben.
- Al terminar: checks pertinentes, diff revisado, `docs/STATE.md` y `docs/NEXT_STEPS.md` al día, decisiones duraderas
  en `docs/DECISIONS.md` (`## DNNN — título`) y artefactos de trabajo en `docs/phase/`. Decir qué se probó y qué no.

## Comandos (desde la raíz; offline tras la primera instalación)

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q   # paralelo (xdist); -n 0 en serie
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
node --test frontend/tests/*.test.mjs
npm --prefix frontend run check
npm --prefix frontend run build
scripts/dev   # API :8013 y Vite :5173, con migración y backup previos
```

Instalación, regeneración de tipos OpenAPI y operación con el wheel: `docs/ARCHITECTURE.md` §9.
