# P009-T014 — Definición con revisor Codex en un hijo sin Git

Fecha: 2026-10-20. Decisión [D124](../DECISIONS.md#d124--p009-t014-cli-13-codex-define-un-proyecto-nuevo-fuera-de-git).
Base: `f3c8ed9` (D123). Origen: [parada de T007](P009-T007_CREACION_DJANGO.md#4-fallo-y-parada).

## Resultado

El adaptador pasa a **`cli-13`**: Codex recibe `--skip-git-repo-check` también cuando el rol `definition`
redacta la definición D088 de una carpeta nueva. El resto del argv no cambia. La CLI falsa reproduce ahora la
negativa de Codex fuera de Git, y el ensayo de T005 la habría detectado. Ningún proveedor invocado.

## 1. Cuándo recibe Codex el flag

| Petición Codex | `cli-12` | `cli-13` |
|---|---|---|
| `chat` o `definition` sobre una exportación (D083/D102) | sí | sí |
| `definition` con plantilla congelada `define-project`, sobre la carpeta viva | no (fallo de T007) | **sí** |
| `definition` con `import-project` (Flujo A, checkout Git vivo) | no | no |
| `planner`, `reviewer`, `phase`, `planning`, `bootstrap`, `chat` sobre la carpeta viva | no | no |
| `executor` (`workspace-write`) | no | no |

Claude no tiene esa comprobación y su argv no cambia.

**Criterio:** la condición se deduce de la petición congelada (rol y nombre de plantilla en el snapshot del prompt),
no del disco en el momento del lanzamiento. Así, el argv sigue siendo función de lo congelado y auditable por intento.
Una definición D088 no puede apuntar a Git:

- `submit_message` rechaza el turno si el destino contiene `.git` o pertenece a un repositorio (`import_required`).
- La observación previa a la invocación incluye `import_required`. Si aparece `.git` después de encolar, el turno
  falla sin invocar al agente («Drafts changed after the message was queued»).
- La aceptación lo bloquea igualmente, y tras el commit raíz la conversación queda cerrada a turnos nuevos.

**Efecto del flag:** solo salta la comprobación de arranque de Codex («Not inside a trusted directory…»). Siguen
igual el sandbox `read-only`, la memoria desactivada (D066), `project_doc_max_bytes=0` (D094) y la ausencia del
override de confianza. Según la guardia de `thread/start` acreditada en D068/D122, Codex solo persiste confianza
si los permisos efectivos escriben el cwd, y un revisor en solo lectura no los tiene. Es el mismo flag que ya
reciben las exportaciones desde D083, en los mismos pins.

## 2. Versión del adaptador

El argv cambia para una clase de peticiones, así que se versiona el adaptador (regla de D052 y alcance de T013;
precedente D102, `cli-11` → `cli-12`). Efectos:

- Un job congelado con `cli-12` y aún sin reclamar pasa a `RECOVERY_REQUIRED` en `bind_process_journal`, antes
  del preflight y de cualquier lanzamiento: es la comparación de versiones de siempre, sin código nuevo.
- Runs terminados, sus snapshots, métricas e historiales conservan `cli-12` y se siguen leyendo; no se reescriben.
- Sin cambios de esquema, API, codec (7), layout documental (`d088-12`), `local-config` ni baseline de versiones de CLI.
- En el área del piloto el único job, el del turno fallido, está DONE según la [evidencia de T007](P009-T007_CREACION_DJANGO.md#4-fallo-y-parada).
  No queda nada que poner en cuarentena. Esto no se ha comprobado sobre su SQLite, que no se ha abierto.

## 3. CLI falsa

`tests/product/cli_process_probe.py` falla en `exec` como el pin, con exit 1 y el mismo mensaje en stderr, si el
directorio de `--cd` (o el cwd) no está dentro de ningún repositorio Git y falta `--skip-git-repo-check`. Busca
`.git` en el directorio y en sus padres, como Codex. `--version` y `--help` no cambian. Es siempre activa, no
opcional, para que cualquier ensayo con un revisor Codex en un hijo nuevo la encuentre.

Con la sonda nueva y el adaptador `cli-12`, la suite da 26 fallos. Uno es la variante sintética de
`test_django_journey`, la definición con revisor Codex del ensayo de T005: el caso de T007, que con `cli-13` pasa.
Los otros 25 lanzaban Codex en checkouts temporales que no eran repositorios, donde el Codex real tampoco
arrancaría (`test_cli_agents`, `test_cli_memory`, `test_metrics`, `test_codex_workspace_write`). Se corrige la
fixture, no el adaptador: el `context` de `test_managed` hace `git init`, como ya hacía el de `test_engine`, y la
prueba del contrato de raíces escribibles de la propia sonda pasa el flag de forma explícita para llegar a él.
Los 617 tests que dependen de esa fixture pasan.

## 4. La conversación del hijo admite un turno nuevo

Por lectura de `PlanningRepository.submit_message`, solo impiden un turno nuevo: un turno `QUEUED`, el proyecto
ya creado desde esa definición, un destino dentro de Git o una versión esperada obsoleta. Un turno `FAILED` deja
la conversación abierta. El turno siguiente congela el fallido en `previous_turns`, sin respuesta. Cada turno es
un run propio con sus versiones, así que un turno `cli-13` sobre una conversación empezada con `cli-12` es
válido. La prueba lo reproduce con el adaptador real y la CLI falsa: primero con la regla `cli-12`, que falla
como en T007, y después con `cli-13` en la misma conversación. El segundo turno queda ANSWERED con propuestas,
cwd en el hijo y `read-only`, y el hijo sigue vacío y sin `.git`.

En el piloto, la reanudación envía un mensaje nuevo a la conversación existente, tras recargar su versión en la UI.
Ese turno cuenta como invocación dentro de los 20 de T007 (ya se consumió 1).

## 5. Verificación

- `tests/product/test_definition_git_check.py` (8 tests): argv por versión de Codex (flag único y resto idéntico),
  roles/plantillas/ejecutor/Claude sin flag, exportaciones conservadas, sonda frente a carpeta sin Git/con flag/
  subcarpeta de un repositorio, conversación con turno fallido y turno nuevo, y cuarentena de un turno `cli-12`.
- Aserciones de la versión vigente actualizadas a `cli-13` en 9 archivos de pruebas existentes; fixture
  `test_managed.context` convertida en repositorio y una prueba de la sonda con el flag explícito (§3).
- Suite offline completa: 1.585 tests y 121 subtests correctos; una omisión esperada (variante Django real sin
  wheelhouse).
- unittest: 12 checks correctos. Sin Alembic ni OpenAPI/Node: no cambian esquema, API ni frontend.
  `alembic check` contra la base local de desarrollo informa que no está al día; no se migró, por no ser pertinente.

## 6. Límites y siguiente paso

- No se ha observado Codex real con el flag en una carpeta sin Git. Si escribiera algo en el destino durante
  el turno, la observación antes/después lo detectaría y descartaría la respuesta. El piloto lo acreditará.
- La [propuesta de T006](P009-T006_PROPUESTA_PILOTO.md#8-actualización-tras-t014) se actualiza con la nueva
  identidad del adaptador (D121 §6). Reanudar T007 sigue exigiendo un wheel construido desde este commit y una
  **autorización nueva del usuario** (D123). P009-T015 sigue pendiente y es obligatoria antes del cierre documental.
