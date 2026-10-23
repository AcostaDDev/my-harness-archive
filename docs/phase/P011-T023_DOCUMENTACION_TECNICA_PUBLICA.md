# P011-T023 — Especificación, arquitectura, datos y flujos públicos en inglés

Fecha: 2026-10-23. Decisión: [D177](../DECISIONS.md#d177--p011-t023-documentación-técnica-pública-autocontenida-en-inglés).
Base: `7a4e64e`. Tarea de [NEXT_STEPS](../NEXT_STEPS.md#p011-t023--especificación-arquitectura-datos-y-flujos-públicos-en-inglés);
desglose HITL de T014 ([D176](../DECISIONS.md#d176--p011-t014-baseline-pública-en-docspublic-y-readme-inglés-de-primer-uso)).

## 1. Entregables

| Archivo (bajo `docs/public/docs/`) | Fuente privada | Tratamiento |
|---|---|---|
| `SPECIFICATION.md` | `docs/SPECIFICATION.md` | Reescritura inglesa del comportamiento vigente: propósito, conceptos, roles, requisitos F01–F22 (renumerados sin los retirados F03/F05 privados, sin columna de fase), reglas 1–12 (la 12 explicita idioma visual/trabajo de D158), contrato documental, cierre, dos entradas, no funcionales, trece criterios globales y fuera de alcance con el modo continuo de D156 como planificado. Sin §12/§13 de ampliaciones privadas |
| `ARCHITECTURE.md` | `docs/ARCHITECTURE.md` | Stack, componentes, módulos, patrones, persistencia, agentes/configuración, API/UI/seguridad, convenciones (ya en inglés), desarrollo/operación (remite al README) y límites. Sin §11–§13 de historia de fases |
| `DDBB-DIAGRAM.md` | `docs/DDBB-DIAGRAM.md` | Doce bloques `erDiagram` con columnas idénticas y comentarios traducidos; prosa inglesa y encabezados sin códigos de fase |
| `flows/*.md` (14) | `docs/flows/*.md` | Los 14 flujos vigentes en inglés, sin enlaces al archivo, fases, entregas ni piloto P009; `legacy-migration.md` se publica como `legacy-compatibility.md` (describe solo compatibilidad de datos retirados). Sección «Source» en cada flujo, contrastada con `src/` |

Otros cambios: `README.md` («Contributing and documentation») y `README.es.md` enlazan los cuatro documentos;
`docs/phase/P011-T014_public_docs_check.py` amplía el comprobador (abajo). Documentos privados sin cambios de contenido
salvo seguimiento (STATE, NEXT_STEPS, ROADMAP, plan, DECISIONS).

## 2. Criterios de redacción aplicados

- **DNNN.** Solo se citan decisiones con entrada en la DECISIONS pública (60 distintas en los documentos nuevos);
  las privadas sin entrada (D015–D027, D101, D103, D105–D112, D117/D118, D135, D145–D147…) se sustituyen por la
  descripción del comportamiento. No se añaden entradas a la DECISIONS pública ni decisiones D200+.
- **Sin historia privada.** Ningún enlace a `docs/archive`/`docs/phase`, códigos `PNNN-TNNN` privados, hitos `Hn.m`
  ni evidencias de entregas. `archive/phase-000/` aparece solo como ruta del producto en los proyectos gestionados.
- **Nombre privado.** El módulo `profiles/reference_project.py` existe en el código del candidato; la arquitectura pública lo
  describe como «perfil solo biblioteca» sin nombrarlo (patrón privado del comprobador). Queda como nota para T015/T017.
- **Tokens de protocolo** (`/estado`, `/tarea`…, estados, códigos 409, formatos) intactos; el flujo de chat explica el
  significado de los comandos españoles.
- Afirmaciones nuevas respecto de los originales contrastadas con el código: banderas `--restricted`/`dontAsk`
  (`adapters/cli_agents.py`), texto de la directiva (`core/engine/language.py`), estado «inferred from code»
  (`templates/onboard-project.md`), comandos del chat (`chat_commands.COMMANDS`) y rutas de las secciones «Source».

## 3. Comprobador ampliado

`P011-T014_public_docs_check.py`:

- Normaliza rutas con `..` (`posixpath.normpath`): antes un enlace `../README.md` desde `docs/` se resolvía mal y se
  marcaba fuera del candidato.
- Nuevo `check_document_references`: todo DNNN de los documentos públicos (salvo DECISIONS) necesita entrada
  pública; `D200` (primer número nuevo, nombrado en AGENTS y el preámbulo) se declara reservado.
- El patrón privado de archivo pasa de cualquier `archive/phase-N` a enlaces hacia un archivo y a las fases privadas
  001–010; `archive/phase-000/` de los proyectos gestionados es comportamiento del producto.

## 4. Validación

| Comando | Resultado |
|---|---|
| `uv run … python docs/phase/P011-T014_public_docs_check.py` | 29 Markdown públicos, 244 enlaces relativos y anclas en la vista del candidato; presupuestos D088 y parsers (P001, 0 tareas, 79 decisiones); 61 DNNN del código y 62 de documentos con entrada pública; sin patrones privados. Verde |
| `uv run … python docs/phase/P011-T013_er_parity.py docs/public/docs/DDBB-DIAGRAM.md` | 51 tablas, 520 columnas, 12 bloques ER, 60 relaciones; sin problemas |
| `node docs/phase/P011-T013_mermaid_check.mjs frontend docs/public/docs/flows/*.md docs/public/docs/DDBB-DIAGRAM.md` | 35 diagramas (5 secuencia, 15 flowchart, 3 estados, 12 ER), 0 fallos (un `;` en una nota de secuencia corregido) |
| `python3 docs/phase/P011-T013_links.py docs/public/docs/*.md docs/public/docs/flows/*.md` | 195 enlaces; 4 «rotos» esperados: `../README.md` solo resuelve en la vista del candidato (README vive en la raíz, D176), validado por el comprobador de T014 |
| Búsqueda de español y códigos privados en los documentos nuevos | Sin restos salvo los tokens de comandos del chat |

No ejecutado: suites pytest/unittest/Node, Alembic, builds, servicios, navegador, proveedores ni red (no cambia
código ni tests; solo documentación y el comprobador de la fase). Sin render DOM de Mermaid. Revisión inglesa propia,
sin revisión externa.

## 5. Pendientes y notas

- T015 copia `docs/public/**` al candidato; el mapa de D176 sigue vigente con los cuatro documentos nuevos.
- Nombre de perfil privado en el código (`profiles/reference_project.py`): decidir en T015/T017 si se renombra o se acepta.
- Los documentos públicos describen la misma realidad que los privados en la base `7a4e64e`; desde la apertura, los
  cambios de producto actualizan los públicos (D157) y los privados dejan de ser fuente.
