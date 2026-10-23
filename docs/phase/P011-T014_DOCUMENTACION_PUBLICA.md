# P011-T014 — Documentación inglesa y README completo de primer uso

Fecha: 2026-10-23. Decisión: [D176](../DECISIONS.md#d176--p011-t014-baseline-pública-en-docspublic-y-readme-inglés-de-primer-uso).
Base: `a319742`. Tarea de [NEXT_STEPS](../NEXT_STEPS.md#p011-t014--documentación-inglesa-y-readme-completo-de-primer-uso);
contrato [T001 §8](P011-T001_CONTRATO_APERTURA.md#8-lista-permitida-del-corte-inicial-y-continuidad).

## 1. Decisiones HITL de esta sesión

1. **Ubicación de la baseline pública.** Árbol autocontenido `docs/public/` que replica la raíz del candidato
   (`docs/public/AGENTS.md` → `AGENTS.md`, `docs/public/docs/*` → `docs/*`). Los documentos privados en español
   (`docs/*.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) siguen vivos y sin cambios de contenido para T015–T018.
   El `README.md` raíz pasa a ser el README inglés público y `README.es.md` la entrada española; para no duplicar
   bytes, ambos viven solo en la raíz y T015 los toma de ahí (no hay copia en `docs/public/`).
2. **Desglose.** Especificación, arquitectura, modelo de datos y flujos públicos en inglés pasan a la nueva
   **P011-T023**, antes de T015 (precedente T010 → T021 → T022). T014 entrega README/entrada española,
   instrucciones de agentes, ejemplo mínimo, DECISIONS de partida y ROADMAP/STATE/NEXT_STEPS públicos.
3. **Numeración de DECISIONS pública.** Se conservan los números que cita el código (D088 ×117, D072 ×48, D167 ×37…):
   cada entrada pública es una reescritura inglesa, autocontenida y en su estado vigente, sin contenido privado
   (rutas, modelos elegidos, commits, áreas o enlaces al archivo). Preámbulo: huecos esperados, números < D200 de la
   baseline, nuevas decisiones desde **D200**. Así las referencias del código resuelven sin tocar código y no chocan
   con decisiones privadas posteriores (D176+ de este checkout). `Hn.m`/`PNNN-TNNN` y nombres de formatos se explican
   en el preámbulo; los DNNN de tests usados como datos sintéticos se declaran como tales.

## 2. Entregables

| Archivo | Destino en el candidato | Contenido |
|---|---|---|
| `README.md` (raíz, reescrito) | `README.md` | Propósito, estado/licencia, funcionamiento, dos entradas, requisitos servicio/build/agentes/hijo, autenticación, CLI verificadas/candidatas, primer clon con cachés, paquete, configuración, primer uso hasta COMMITTED y cierre, idiomas con ejemplo es/en, seguridad, operación (reinicio, actualización, backup, diagnóstico, desinstalación), alcance/límites, desarrollo y contribución |
| `README.es.md` (nuevo) | `README.es.md` | Entrada española: resumen y navegación a cada apartado inglés |
| `examples/local_config.minimal.example.toml` (nuevo) | igual | `local-config-7` de un proveedor (Claude en ambos roles, nota para Codex), perfil declarado `python-unittest` y composición `python`, sin `[[projects]]` |
| `CONTRIBUTING.md` (ampliado) | igual | Enlace al apartado de desarrollo y mantenimiento de DECISIONS/STATE/NEXT_STEPS |
| `docs/public/AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | raíz | Instrucciones públicas D088 (48/8/5 líneas), sin rutas/proyectos privados |
| `docs/public/docs/STATE.md` | `docs/STATE.md` | Base acumulada pública (4,4 KiB) y fase activa P001 |
| `docs/public/docs/ROADMAP.md` | `docs/ROADMAP.md` | P001 — modo continuo opcional (D156, v0.2.0) y huecos conocidos sin fase |
| `docs/public/docs/NEXT_STEPS.md` | `docs/NEXT_STEPS.md` | P001 sin tareas («Pending a confirmed plan») y restricciones compartidas |
| `docs/public/docs/DECISIONS.md` | `docs/DECISIONS.md` | Preámbulo y 79 decisiones de partida (61 citadas por el código más fundacionales) |
| `docs/phase/P011-T014_public_docs_check.py` | privado | Comprobador estático del candidato (abajo) |

Cambios privados: `docs/ARCHITECTURE.md` actualiza dos anclas hacia el README inglés (`#requirements`,
`#supported-scope-and-limits`); seguimiento en STATE/NEXT_STEPS/ROADMAP/plan y D176.

## 3. Mapa para T015

- `docs/public/**` se copia a la raíz del candidato y **sustituye** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` y todo
  `docs/`. Nada de `docs/*.md`, `docs/flows/`, `docs/phase/` ni `docs/archive/` privados entra en el candidato.
- De la raíz: `README.md`, `README.es.md`, `LICENSE`, `NOTICE.md`, `NOTICE-THIRD-PARTY.md`, `CONTRIBUTING.md`,
  `SECURITY.md`, `examples/*.toml` y `examples/managed_demo.py` (no `examples/first_use/` ni `provider_matrix/`).
- T023 añadirá a `docs/public/docs/` SPECIFICATION, ARCHITECTURE, DDBB-DIAGRAM y `flows/`, y el apartado
  «Contributing and documentation» del README enlazará esos documentos. Hasta entonces el README solo enlaza lo
  que existe en el candidato.
- Si T015 u otra tarea añaden citas DNNN al código, el comprobador exige su entrada pública antes del corte.

## 4. Criterios de aceptación

| Criterio | Resultado |
|---|---|
| Documentación pública vigente inglesa, navegación española, enlaces/anclas y parsers/presupuestos D088 | Cumplido para los documentos de T014; especificación/arquitectura/datos/flujos → T023 (HITL) |
| Baseline nueva con decisiones iniciales autocontenidas, sin ADR/fases privadas ni DNNN sin explicar | Cumplido: 79 entradas reescritas, preámbulo, todos los DNNN del código con entrada |
| README: propósito/estado/licencia, requisitos servicio/build/hijo, autenticación, primer clon sin cachés, paquete, ejemplo de un proveedor, TOML, sesión, preparación y primer COMMITTED | Cumplido. El criterio dice «TOML v5»: el formato vigente es `local-config-7` (T012) y es el que se documenta |
| Exactamente dos entradas, sin visor/observación/importación/normalización del harness anterior | Cumplido; el registro de un proyecto ya gestionado se explica como registro normal |
| Idiomas, CLI verificadas/candidatas, red/cachés/consumo, confirmaciones, reinicio/actualización/backup, diagnóstico, desinstalación y contribución | Cumplido |
| Visual global, default de trabajo e inmutabilidad; ejemplo español visual/inglés técnico para ambos proveedores | Cumplido (README «Languages» y README.es) |
| Desarrollo separado del uso instalado, sin modelos/rutas privadas, solo capacidades entregadas, plataformas/evidencia pendientes declaradas | Cumplido; el primer uso se declara no ensayado (T016) |

## 5. Validación

| Comando / check | Resultado |
|---|---|
| `uv run … python docs/phase/P011-T014_public_docs_check.py` | 12 Markdown públicos, 51 enlaces relativos y anclas resueltos en la vista del candidato; AGENTS ≤60 líneas/32 KiB, envoltorios ≤15; `parse_roadmap` → P001, `plan_tasks` → 0, `decision_index` → 79 únicas y ordenadas con `Status:`; STATE 4.962 B, base 4.533 B, NEXT_STEPS 615 B; 61 DNNN citados por el código con entrada pública; sin patrones privados (archivo, tareas privadas, rutas personales, modelos, ReferenceProject, correo) |
| Carga de `examples/local_config.minimal.example.toml` con rutas sintéticas (`load_local_config`, `inspect_local_config` + `summary`) | `local-config-7`, `supervisor=true`, perfil `python-unittest`, composición `python`, agentes reviewer/executor; sin procesos |
| `harness-local [--ui-language en] {—,backup-create,migrate,serve,check-config} --help` | Argumentos del README coinciden con la CLI |
| Comandos de scripts (`build_distribution.py --out-dir`, `check_distribution.py --dist`, `scripts/dev`, `export_openapi.py`, `generate:types`) | Contrastados con el código y `package.json`, sin ejecutarlos |
| `python3 docs/phase/P011-T013_links.py docs/*.md docs/flows/*.md docs/phase/*.md README.md README.es.md CONTRIBUTING.md` | 750 enlaces, 0 rotos tras corregir dos anclas de ARCHITECTURE |
| Búsqueda de tests que lean README/ejemplos; `python3 -m unittest discover -s tests` | Ninguno lee los archivos cambiados; unittest 8/8 OK |

No ejecutado: pytest/Node/Alembic (no cambia código ni tests), build/wheel, servicios, navegador, CLI de proveedores, instalaciones,
red ni ensayo de primer uso (T016).

## 6. Pendientes y notas

- **Enlace archivado congelado.** `docs/archive/phase-010/SUMMARY.md` enlaza `README.md#alcance-soportado`; la sección
  equivalente es ahora «Supported scope and limits». El archivo no se edita (contrato T001) ni se añade un alias
  privado al README público; queda explicado aquí.
- **Texto «observers» en la ayuda de la CLI** (`cli.help.writers_stopped`, `migrate.writers`, resto de T013): está en
  los catálogos de `src/`, fuera de las rutas de T014. El README no lo repite. Propietaria: T017 (o una tarea con
  esas rutas).
- **T016**: al ensayar el primer uso, actualizar las frases «not yet rehearsed» de README, README.es y STATE públicos y
  corregir cualquier paso que no funcione tal como está escrito. El perfil `python-unittest` del ejemplo falla hasta
  que exista `tests/` con un test; el comentario lo indica.
- **Presupuesto privado.** STATE privado se mantiene por debajo de 24 KiB compactando su seguimiento; NEXT_STEPS ya
  superaba 48 KiB antes de esta tarea (aviso, sin truncar) y crece con la sección de T023.
