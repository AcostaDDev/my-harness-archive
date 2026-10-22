# P010-T006 — Documentación de instalación y alcance soportado

Fecha: 2026-10-22. Base: `cda9090`. Decisión:
[D148](../DECISIONS.md#d148--p010-t006-documentación-de-instalación-y-alcance-soportado).
**Estado: completada.** Solo documentación y comentarios de ejemplos; sin cambios de código, esquema, API, tipos,
versiones ni configuración. Sin proveedores, servicios, instalaciones ni smokes.

## 1. Contraste con el código

| Fuente | Hecho comprobado | Documentación antes | Ahora |
|---|---|---|---|
| `adapters/cli_agents.py` (`SUPPORTED`, `WRITE_SUPPORTED`), D122 | Codex 0.161.0/0.162.1/0.163.0 en lectura y 0.162.1/0.163.0 en escritura; Claude 2.1.295/2.1.296/2.1.304 en ambos roles; adaptador `cli-13` | README: Codex «0.162.1 para escribir» y Claude 2.1.295/2.1.296 | Tabla por CLI y rol en README, con el uso real registrado de cada versión |
| `migrations/versions/` | Cabeza `0023_run_projection` | ARCHITECTURE §1 y §3: `0021` | `0023` y `0001…0023` |
| `core/engine/serialization.py` | Escribe el formato 8 del historial; lee 1–8 | ARCHITECTURE §3: «formatos 1–7» | Formato 8; lectura 1–8 |
| `services/local_config.py` | `local-config-5` vigente; lee 1–4; registro y creación con 3/4/5; presets y recetas solo en v5 | ARCHITECTURE §3: `local-config-4` y creación con 3/4 | v5, lectura 1–4, 3/4/5 y fila de recetas y preparación |
| `launcher.py`, `cli.py`, D043 | `init-db` solo crea; `serve` exige el esquema del paquete; ninguna orden instalada migra una base existente | Sin mención en README ni ARCHITECTURE §9 | Sección «Actualizar» en README, párrafo en §9 y límite en §10 |
| `cli.py` | Órdenes `backup-*`, `logs-*`, `metrics-backfill`, `diagnose-cli`, `legacy-*` | README sin backup ni operación | Sección «Operación» en README |
| `profiles/typescript_web.py` | Protege `package.json`, `package-lock.json`, `tsconfig.json`, `scripts/**` y `tests/**` | Solo en el contrato de T001 (§5) | Límite en README y ARCHITECTURE §10 |
| `pyproject.toml`, `scripts/toolchain.py` | Paquete `0.1.0`; Python 3.14.4, uv 0.12.19, Node 24.15.0, npm 11.12.1 | Coherente | Sin cambio; README explicita que la primera versión no es `1.0.0` |

README también corrige el estado de P009/P010, el enlace al archivo de la última fase cerrada (`phase-009`) y la
estructura de `examples/`. ARCHITECTURE §12 resume T003–T005 y T011.

## 2. Ejemplos

- `local_config.example.toml` sigue siendo `local-config-4`: `test_example_template_documents_the_local_config_4_keys`
  fija ese formato y `tests/**` queda fuera de las rutas de esta tarea. Un comentario indica que la misma plantilla
  vale como v5 cambiando `format`.
- `django-recipe.example.toml` avisa de que su `[compositions.django]` choca con la de la plantilla y debe añadirse con
  otro nombre.
- Los guiones de `first_use/` y `provider_matrix/` son históricos y no se tocan (D122); README los presenta así.

Comprobación, con `load_local_config` y rutas y ejecutables sintéticos en un directorio temporal:

| Combinación | Resultado |
|---|---|
| Plantilla tal cual (`local-config-4`) | carga |
| Plantilla con `format = "local-config-5"` | carga; misma composición y adaptador `cli-13` |
| v5 + fragmento TypeScript web | carga |
| v5 + fragmento Django sin renombrar | `TOML UTF-8 inválido`: `[compositions.django]` declarada dos veces |
| v5 + fragmento Django con `[compositions.django-recipe]` | carga |

## 3. Alcance soportado

README distingue lo verificado offline y lo probado con proveedores reales, citando la evidencia:

- **Con uso real:** ejecución → revisión → commit, fases y cierre (D050, D071, D139); las cuatro combinaciones
  (D071 y piloto P009); receta Django en macOS arm64 con Python 3.13 (D139).
- **Solo offline:** receta TypeScript web (también con node/npm reales y caché local), perfil declarado de D095,
  importaciones A/B, chat ligado a tareas, backup y restauración, y lecturas acotadas de T003/T011.
- **Pendiente de decisión:** la validación real de A/B y del perfil declarado (T008).
- Codex 0.161.0 no tiene uso real localizado. Los usos reales anteriores a `cli-13` se presentan como históricos.

## 4. Decisión con el usuario

El paquete instalado no tiene actualizador de bases (D043) y P010-T003 sube el esquema a `0023`: una base operativa en
`0022`, como la del área de P009, no arranca con el paquete de P010. Elección del usuario en el bucle HITL: documentar
el límite vigente y anotarlo para que T007 valore si se acota como tarea de producto. No se documenta ninguna vía
manual sobre `storage/migrate.py`, que no es una interfaz del paquete instalado.

## 5. Verificación

| Comprobación | Resultado |
|---|---|
| Contraste estático de versiones, órdenes, esquema, codec y formatos (§1) | coherente tras los cambios |
| Carga de la plantilla y los fragmentos con `load_local_config` (§2) | según la tabla |
| `pytest -q tests/product/test_project_registry.py tests/product/test_declared_profiles.py tests/product/test_typescript_preparation.py` | 76 pasan, 1 omitida (variante opt-in con node/npm reales sin caché explícita) |
| Enlaces relativos y anclas de README, ARCHITECTURE, STATE, NEXT_STEPS, ROADMAP y esta entrega | sin rotos |
| Parsers documentales (`parse_roadmap`, `plan_tasks`, `decision_index`) | 10 fases, 11 tareas de P010 en orden y 148 decisiones |
| Presupuestos | STATE 10.057/24.576 bytes (base acumulada 5.624/12.288) y NEXT_STEPS 20.431/49.152 |
| `git diff --check` | correcto |

No se ejecutan los comandos de instalación, construcción ni operación de README: la tarea no autoriza construir el
wheel, crear venvs ni levantar el servicio. Su verificación corresponde a T009.

## 6. Resultados y límites

- Los tres módulos de pruebas que leen `examples/` pasan tras cambiar los comentarios. No se ejecutan la suite
  completa, unittest, Node, tipos/build ni Alembic: no cambia código, esquema, API ni UI.
- Las afirmaciones de uso real proceden de decisiones y archivos de fase, no de nuevas ejecuciones.
- El procedimiento de instalación de README coincide con el verificado en P009-T015 (D126); el paquete de P010 no se
  ha construido ni verificado todavía.
