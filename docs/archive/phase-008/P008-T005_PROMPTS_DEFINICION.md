# P008-T005 — Prompts y definición bajo el contrato unificado

Implementación de [D092](../DECISIONS.md#d092--p008-t005-prompts-y-definición-bajo-el-contrato-unificado), sobre
D088/D089 y la planificación posterior de D091. Trabajo manual, sin registrar este repositorio en el harness.

## Resultado

- `define-project`, `plan-phase`, `reconcile-phase`, `close-phase`, `review-task`, `execute-task` y `revise-task`
  tienen identidades nuevas por hash. Retiran las carpetas antiguas y especifican discovery desde AGENTS,
  DECISIONS único, diagramas de datos/flujos, artefactos de fase y propuestas de ADR. La reconciliación autorizada
  conserva su excepción para añadir decisiones respaldadas sin tocar bloques gestionados ni historia.
- Definición versión 4: once documentos obligatorios en el resultado aceptado. Conserva los siete borradores
  obligatorios y completa instrucciones/diagrama ausentes por plantilla (D089); los valores por defecto del título
  y comandos del perfil entran en el contexto congelado. Los borradores personalizados conservan sus bytes.
  La aceptación bloquea AGENTS >60 líneas y CLAUDE/GEMINI >15. Solo se añaden a la plantilla flujos Markdown de un
  nivel; las carpetas retiradas, artefactos y flujos anidados no se admiten como borradores.
- La planificación usa el destino exacto de `context.next`, incluida la fase ACTIVE vacía que deja el cierre, y
  explica la confirmación propia del plan. Añade instrucciones y DDBB-DIAGRAM a las lecturas acotadas del contexto.
  El prompt del check no exige el plan de la sucesora para READY.
- `document_layout = "d088-4"` se centraliza en el núcleo documental. La composición rechaza versiones anteriores
  antes de preparar comandos o invocar agentes. La conciliación de transiciones ya selladas conserva sus bytes,
  intención y run originales, admitiendo el salto de versión solo para ese escritor y con el resto del contexto y
  versiones idénticos.

## Alcance técnico y compatibilidad

La versión nueva y la recuperación de transiciones requieren dos extensiones mínimas a las rutas enumeradas en T005:
`services/local_config.py` importa la constante del núcleo y `services/managed.py` la usa al recuperar una intención
sellada. Se aplica el mismo mecanismo de D091, sin agentes, permisos nuevos ni recálculo de intenciones.

Los catálogos, prompts, esquemas e intentos congelados anteriores siguen leyéndose íntegros. No cambia el codec,
adaptador CLI, modelo de datos, migración, dependencia ni esquema de salida del agente. API/UI siguen en T006 y la
inyección de AGENTS en todos los roles sigue en T007; mencionar discovery en el prompt no acredita esa inyección.

## Verificación

- Checks ligeros: 12 correctos con `python3 -m unittest discover -s tests -p 'test_*.py'`.
- Primera pasada dirigida: 179 pruebas correctas (definición, prompts, bootstrap, cierre y configuración).
- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 1.158 pruebas y 121 subtests correctos,
  en 529,89 segundos. Incluye los tres casos de recuperación d088-1/2/3 y la cuarentena del contrato d088-3.
  Solo el aviso conocido de deprecación Starlette/httpx; no se cambia ninguna dependencia para corregirlo.
- Quince Markdown editados/nuevos: 230 enlaces relativos/anclas y bloques gestionados válidos. ROADMAP parsea ocho
  fases, NEXT_STEPS quince tareas y DECISIONS 92 decisiones únicas; STATE/base/NEXT_STEPS dentro de presupuesto.
- Tres diagramas de los dos flujos editados aceptados por Mermaid 11.17.2 local: comprobación de sintaxis sin DOM ni
  render, con DOMPurify sustituido solo en memoria. Diff revisado y `git diff --check` correcto.

Las pruebas usan Git/SQLite temporales, agentes falsos, procesos sintéticos y ningún dato privado. Cubren desde
carpeta vacía a commit raíz/P001, instrucciones personalizadas o por defecto, guardias de aceptación y CAS,
versiones y snapshots conservados, recuperación de transiciones y planificación de la fase activa tras el cierre.

No se ejecutan pruebas Node, build del frontend ni `alembic check` independiente: no cambian UI, OpenAPI, modelos ni
migraciones. La suite pytest incluye pruebas de API y migraciones en bases temporales. Sin harness sobre este
checkout, proveedores reales, smokes, push o publicación.
