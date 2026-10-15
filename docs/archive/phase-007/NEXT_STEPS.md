# Plan archivado — P007 Agentes configurables e interfaz de producto (antes H6)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 6 — Agentes configurables e interfaz de producto

Añadido el 2026-10-13 por decisión del usuario (D052, D054). Orden: H6.1 antes que la UI.

**Hito cerrado el 2026-10-15 (D087):** H6.1–H6.5 completados.

#### H6.1 Revisor y ejecutor con proveedor elegible (D052)

Completado offline el 2026-10-13 (`cli-5`, `local-config-2`); comprobación funcional
real de las cuatro combinaciones completada el 2026-10-14 (`cli-9`, D071).
[Resultado y límites](PROVIDER_MATRIX_CLI9_RUN.md). Consentimiento agotado.

- Revisor y ejecutor Codex o Claude, en cualquier combinación. El usuario fija el revisor; el revisor fija modelo y esfuerzo del ejecutor (catálogo o libre).
- Planificación `agent` | `deterministic` como ajuste por proyecto.
- Criterio: matriz de las cuatro combinaciones verificada offline por el adaptador real, con historiales anteriores legibles.

#### H6.2 Interfaz de producto (D054)

Alcance fijado el 2026-10-14 (D076): seis entregas E1–E6. E1 (shell, navegación y diseño) completada offline
(D077, [entrega](H6.2_E1_SHELL.md)). E2 (registro de proyectos) completada offline (D078,
[entrega](H6.2_E2_REGISTRY.md)). E3 (documentación) completada offline (D080,
[entrega](H6.2_E3_DOCS.md)). E4 (creación y planificación) completada offline (D081–D082,
[entrega](H6.2_E4_SETUP.md)); E5 (chat global) completada offline (D083,
[entrega](H6.2_E5_CHAT.md)); E6 (estadísticas y tests) completada offline (D084,
[entrega](H6.2_E6_STATS.md)). Revisión de cierre (D085, [dictamen](REVIEW.md)): seis
criterios cumplidos y diffs sin paginar; corregido con los hallazgos menores (D086,
[entrega](H6.2_DIFF_PAGINATION.md)). **Cerrado el 2026-10-15 por decisión del usuario (D087).**
[Alcance y criterios](NEXT_STEPS.md).

- Arquitectura de información y sistema de diseño de dashboard: navegación, cabecera con sesión, estados vacíos útiles, tablas y estados consistentes.
- Alta de proyectos desde la UI con registro en SQLite y confirmación explícita de confianza; el bootstrap de proyectos nuevos, accesible desde el inicio.
- Configuración de agentes (H6.1) y chat accesibles desde la UI.
- Criterio: QA visual con navegador sobre `scripts/dev` y recorridos de alta → tarea → revisión → commit sin editar archivos a mano.
- Ampliado por D072 ([diseño §7–§9](DOCUMENT_ORGANIZATION.md)): URLs por
  proyecto, fase, tarea y run con carga por recurso; editor de documentos; chat
  global con comandos; métricas por tarea; tests OK/KO; estadísticas por proyecto
  y globales; asistente de creación conversacional. Orden confirmado (D073): después de
  H6.3–H6.5, como tarea completamente distinta.

#### H6.3 Contrato documental y transición de fase (D072, D073)

Completado offline el 2026-10-14, opt-in con `documents = "v2"`.
[Entrega y límites](H6.3_DOCUMENT_CONTRACT.md).

- Plantilla documental v2, bloques gestionados v2, ROADMAP como fuente de las fases y alias en español del parser de NEXT_STEPS.
- Regeneración mecánica de bloques en cada commit de tarea; `phase_transition` (archivo `phase-NNN`, STATE/NEXT_STEPS frescos, fase siguiente en un commit conciliable); `document_edit` con CAS y deriva.
- Criterio: con fixtures sintéticos, una sesión nueva reconstruye la siguiente tarea solo desde los documentos y el archivo es idéntico al HEAD cerrado.

#### H6.4 Métricas por intento y estadísticas (D072, D074)

Completado offline el 2026-10-14. [Catálogo, entrega y límites](H6.4_METRICS.md).

- `attempt_metrics` materializada con procedencia por campo, captura de turnos, relleno idempotente y agregados por tarea, fase, proyecto y global; tests OK/KO.
- Criterio: sin doble conteo, null distinto de cero y métricas conservadas tras la retención de logs.

#### H6.5 Creación y planificación conversacionales (D072, D075)

Completado offline el 2026-10-14. [Entrega y límites](H6.5_CONVERSATIONAL_CREATION.md).

- Conversaciones `definition` y `phase_planning` del revisor, borradores en disco con CAS, aceptación hacia bootstrap v2 o transición.
- Criterio: de carpeta vacía a commit raíz con P001 y `phase-000`, sin que el agente escriba ni se admitan archivos ajenos.

## Alcances conservados

### Agentes revisor y ejecutor con proveedor elegido por el usuario — alcance

_Origen: `docs/discovery/AGENT_ROLES_SCOPE.md`._

Escrito el 2026-10-13 antes de cualquier código. D052. **Implementado y verificado offline
el mismo día**: ver [entrega](AGENT_ROLES.md).
Sustituye la asignación fija de la especificación (§1 «Codex planifica… Claude
Code ejecuta… Codex revisa», F05 y la tabla de prompts): contradicción material
señalada y resuelta por el usuario.

#### Decisiones del usuario

1. Dos agentes visibles para el usuario: el **revisor**, que planifica, revisa,
   evalúa fases, conversa y propone el bootstrap (solo lectura), y el
   **ejecutor**, que implementa el código (único escritor).
2. Cada agente puede ser Codex o Claude: Claude/Claude, Codex/Codex,
   Claude/Codex y Codex/Claude.
3. El usuario fija el proveedor, el modelo y el esfuerzo del revisor.
4. El revisor fija el modelo y el esfuerzo del ejecutor en cada tarea y en cada
   revisión. El usuario elige por proyecto uno de dos modos:
   - **acotado**: catálogo de modelos y esfuerzos permitidos; el motor rechaza
     lo que quede fuera (regla actual de la especificación);
   - **libre**: cualquier modelo y esfuerzo que acepte la CLI del ejecutor; el
     motor solo valida la forma.
5. Toda tarea pasa por el revisor. Por ahora, el revisor siempre planifica. Más
   adelante, el revisor decidirá si planificar o despachar directamente
   («JEV», término del usuario; no se implementa ahora).
6. La planificación determinista **se mantiene como ajuste del usuario** por
   proyecto. Con `agent`, el revisor lee NEXT_STEPS, analiza el código con más
   detalle y redacta el prompt del ejecutor, eligiendo su modelo y esfuerzo.
   Con `deterministic`, el ejecutor recibe el contrato directamente de
   NEXT_STEPS, con la selección escrita allí y validada según el modo
   catálogo/libre. La revisión del resultado la hace siempre el revisor.

#### Estado actual que cambia

| Lugar | Acoplamiento actual |
|---|---|
| `adapters/cli_agents.py` `invoke` | `claude` si el rol es `executor`; si no, `codex` |
| `argv_for` | Codex solo admite roles de lectura; Claude solo `executor` |
| Concesiones H3.2 | Herramientas concedibles solo para Claude ejecutor |
| `local_config` (`local-config-1`) | Tablas fijas `[providers.codex]` y `[providers.claude]` |
| `EnginePolicy` | `planner_*` y `reviewer_*` separados; catálogo obligatorio para el ejecutor |
| Textos | Docstrings de chat/bootstrap y `Bootstrap.tsx` nombran Codex |

Ya es independiente del rol: `adapters/streams.py` interpreta por proveedor
(mensaje final de Codex; `result`/`structured_output` de Claude) y sirve igual
para un Claude revisor o un Codex ejecutor.

#### Alcance propuesto (incremento `cli-5`, `local-config-2`)

- **Configuración:** `[agents.reviewer]` y `[agents.executor]`, cada una con
  `provider`, ejecutable, versión, entorno, timeout y, solo en el revisor,
  modelo y esfuerzo. Selección del ejecutor `mode = "catalog" | "open"`.
  `local-config-1` se sigue leyendo como revisor Codex + ejecutor Claude, con
  la misma política.
- **Adaptador:** constructor de argv por (proveedor, acceso):
  - Codex lectura: el actual.
  - Codex escritura: `--sandbox workspace-write` y `approval_policy="never"`,
    sin red; sin concesiones de herramientas, que se rechazan explícitamente.
  - Claude escritura: el actual.
  - Claude lectura: solo `Read`, `Glob` y `Grep`, `dontAsk`, sin MCP, hooks ni
    sesión persistida; salida estructurada si la CLI la admite.
  - El hash congelado incluye el reparto agente → proveedor. Las versiones
    `cli-1`…`cli-4` siguen siendo legibles.
- **Política:** revisor único (planificador = revisor); el planificador
  separado desaparece de la configuración nueva. `planning_mode` es un ajuste
  explícito (`agent` | `deterministic`); `agent` en la plantilla. Selección del ejecutor validada según el modo y el vocabulario de
  esfuerzo de su proveedor. Cambiar de modo invalida jobs pendientes, igual que
  hoy cualquier cambio de composición.
- **Permisos H3.2:** capacidades declaradas por proveedor; un proveedor que no
  puede imponer una concesión la rechaza antes de lanzar.
- **UI/API:** mostrar proveedor, modelo y esfuerzo de cada agente; textos
  neutros («revisor», «ejecutor»).
- **Pruebas offline:** matriz de las cuatro combinaciones con CLI falsas por el
  adaptador real, rechazos de configuración, modos catálogo/libre, compatibilidad
  `local-config-1` e historiales anteriores.

#### Pendiente de caracterizar antes del código (version/help, sin consumo)

- Codex 0.162.1: flags de `workspace-write` y eventos de cambios de archivos en
  `--json`.
- Claude 2.1.295/2.1.296: salida estructurada (`--json-schema` u otra) y
  aislamiento de solo lectura con `--tools`.
- Vocabularios de esfuerzo de cada CLI.
- Si se adopta Claude 2.1.296 en el mismo incremento, ya que el enlace del
  usuario apunta a esa versión.

#### Después de la implementación

- Smoke autorizado de la matriz con proveedores: propuesta aparte, después de la
  implementación offline.

Fuera: App Server/SDK, otros proveedores, la decisión inteligente de planificar
(«JEV») y la elección de proveedor por tarea.

### H6.2 — UI de producto: alcance previo

_Origen: `docs/discovery/H6.2_SCOPE.md`._

Fijado con el usuario el 2026-10-14 sobre `7b2c2eb`, con Git limpio (D076). Base: D054,
D072 §6–§9 y D073 punto 6. Construye la interfaz una sola vez sobre los contratos estables de
H6.3–H6.5. No autoriza proveedores, CLI reales, push ni publicación. **Ninguna entrega se ha iniciado.**

#### Decisiones del usuario

1. **Registro híbrido TOML + SQLite.** El TOML del operador sigue siendo la autoridad de lo que
   ejecuta: agentes, Git, ejecutables y entornos. Los conjuntos de comandos por perfil pasan a ser
   **composiciones con nombre**. La UI registra proyectos en SQLite (raíz canónica, confianza
   explícita, perfil, `documents = "v2"`, bootstrap, política de modelos y esfuerzos) y elige una
   composición del TOML. Ningún ejecutable, entorno ni argv se concede por HTTP.
2. **Markdown con `markdown-it` y Mermaid diferido.** Dos dependencias nuevas con versión fijada.
   `markdown-it` va con `html: false` y con validación de enlaces. Mermaid usa
   `securityLevel: "strict"` y se carga de forma diferida, solo en la sección de documentación.
3. **Chat global dentro de H6.2, en entrega propia.** Esa entrega implementa primero el backend:
   turnos sobre una instantánea de solo lectura del HEAD, sin tomar el lock (D073 punto 5, cambia
   D035), y comandos deterministas (D072 §8). La UI del chat va después.
4. **Enrutador y estilos propios, sin dependencias.** Enrutador mínimo sobre History API y CSS con
   tokens, modo claro y oscuro, sin framework. El servidor del wheel sirve `index.html` en las
   rutas que no son de API.

#### Entregas

Cada entrega es una tarea aparte, con su verificación, su QA visual y su actualización de STATE,
NEXT_STEPS y DECISIONS. El orden es vinculante salvo que el usuario lo cambie: E4 necesita E2 y E3,
y E5 necesita E1.

##### E1 — Shell, navegación y sistema de diseño

- Enrutador propio con las rutas de D072 §7 (`/`, `/projects/:p`, `/phases`, `PNNN`, `PNNN-TNNN`,
  runs por id), enlace directo, recarga e historial. Una ruta desconocida muestra un estado 404 útil.
- Resolución de los códigos `PNNN` y `PNNN-TNNN` a ids. Si las lecturas actuales no la permiten sin
  traer listas completas, se añade una lectura por código.
- Fallback del servidor: `index.html` en `GET` de rutas que no empiezan por `/api/`. Los recursos
  inexistentes de `/api/` siguen dando 404 JSON.
- Sistema de diseño con el plugin de diseño (`frontend-design`): tokens, tipografía, tablas,
  estados (vacío, carga, error, bloqueado), cabecera con sesión y modo oscuro.
- Las pantallas funcionales actuales (fases, permisos, logs, tests, prompts y bootstrap v1) se
  trasladan a sus URLs, con carga por recurso y paginación. La navegación legacy (H1) se conserva
  en `/legacy`. Las simulaciones H0.3 salen de la navegación.
- Configuración de agentes (H6.1) visible en solo lectura en `/projects/:p/settings`.

##### E2 — Registro de proyectos (D054)

- Formato `local-config-3`: composiciones con nombre (ejecutables, entorno, límites y comandos
  autorizados del perfil) y raíces bajo las que la UI puede registrar proyectos. También expone
  `bootstrap_enabled`. `local-config-1` y `-2` se siguen leyendo; sus `[[projects]]` siguen siendo
  válidos y se muestran como proyectos del operador, no editables desde la UI.
- Migración nueva: registro de proyectos versionado y auditado (quién, cuándo, hash de la fila, raíz
  canónica, confianza, perfil y composición). Baja lógica, nunca borrado; el historial se conserva.
- API de alta, cambio y baja, con vista previa y confirmación ligadas al hash y la versión, y con
  la confianza como confirmación aparte. Los ids no pueden coincidir con los del TOML. La raíz debe
  quedar bajo una raíz autorizada, sin enlaces y fuera del estado del servicio.
- El hash de la composición congelada incluye la versión del registro. Cambiar un proyecto con jobs
  pendientes se rechaza, y la cuarentena existente cubre el resto. El runtime incorpora el proyecto
  sin reiniciar.
- UI en `/projects/new` y en ajustes del proyecto (perfil, política, composición, prompts y techo de
  permisos).

##### E3 — Documentación

- Árbol (`/projects/:p/docs/*path`) y visor con `markdown-it` y Mermaid diferido. Los enlaces solo
  admiten rutas relativas y `http(s)`. Las imágenes del repositorio se sirven por la API y nunca
  apuntan fuera.
- Editor con hash base, vista previa del diff y confirmación de `document_edit`. Muestra los
  conflictos de CAS, la deriva («cambios locales sin confirmar»: confirmar o regenerar), los bloques
  gestionados bloqueados, `archive/**` en solo lectura y los bloqueos que provoca la deriva.
- El historial por documento queda fuera, salvo que una lectura existente ya lo dé.

##### E4 — Creación y planificación de fase

- `/projects/:p/setup`: brief, turnos de `definition`, borradores (aplicar, descartar y editar con
  CAS), preguntas aplazadas con motivo y vista previa de la aceptación con sus bloqueos. Al aceptar,
  bootstrap v2 y P001.
- `phase_planning` desde la fase cerrada, y transición con `plan_proposal`.
- Registro de una carpeta vacía con bootstrap (E2) → creación, desde la UI de inicio a fin.

##### E5 — Chat global

- Backend: turnos de chat sobre una instantánea de solo lectura del HEAD (worktree temporal o árbol
  exportado), sin el lock del checkout, comparando la evidencia de la instantánea antes y después.
  Las propuestas aceptadas siguen creando tareas normales. Es un cambio deliberado de D035 y se
  registra como decisión.
- Comandos deterministas (`/estado`, `/tests`, `/siguiente`, `/lote`, `/check`, `/cerrar`,
  `/exportar`, `/abrir-fase`, `/tarea <texto>`). Se reconocen por sintaxis, sin modelo, y usan las
  mismas confirmaciones que el botón equivalente. Ninguno concede permisos ni se salta una
  confirmación.
- UI `/projects/:p/chat[/:conversation]` con varias conversaciones y contexto de fase o tarea.

##### E6 — Estadísticas y tests

- `/stats` y `/projects/:p/stats` sobre `/metrics/*`: consumo por fase, día, rol, proveedor y modelo;
  favoritos por rol; aceptación a la primera; revisiones; duraciones; paradas; tests OK/KO y su
  evolución.
- En la tarea: agentes, intentos, tokens (también de fallos), turnos y la última validación. Muestra
  la procedencia, nunca trata null como cero y presenta el coste como «equivalente API».
- Gráficos sin dependencia nueva (SVG propio), salvo una decisión aparte.

#### Criterios de aceptación del hito

- Cada URL se abre por enlace directo y por recarga, en desarrollo (`scripts/dev`) y desde el wheel.
- Ninguna acción repite efectos al reintentar ni al recargar. Las confirmaciones se ligan a hash y
  versión.
- Carga por recurso: el resumen de un proyecto no trae tareas, y logs, diffs y casos de test van
  paginados.
- Markdown sin HTML ejecutable, comprobado con casos hostiles (`<script>`, `javascript:`,
  `on*=`, SVG/Mermaid con HTML incrustado).
- QA visual con navegador sobre `scripts/dev` y datos sintéticos en cada entrega, en claro, oscuro y
  ancho estrecho.
- Recorrido sintético completo, sin editar archivos a mano: alta → creación → primera tarea →
  revisión → commit → cierre → transición con plan propuesto.
- Siguen en verde pytest, los checks estándar, las pruebas Node, `tsc`, el build y `alembic check`.
  Las pruebas nuevas del cliente (enrutador, render seguro) usan `node --test`, sin un runner nuevo.

#### Fuera de alcance

Proveedores o CLI reales (la UI se prueba con adaptadores falsos), `.harness/project.yaml` portable,
multiusuario o acceso remoto, conceder ejecutables o entornos por HTTP, edición del TOML desde la UI,
historial Git de documentos, i18n (la UI va en español), push y publicación.

#### Riesgos y comprobaciones al implementar

- E1: comprobar si `StaticFiles(html=True)` permite el fallback o hace falta una ruta propia, sin
  tapar los 404 de `/api/`.
- E2: el runtime hoy compone proyectos al arrancar. Incorporarlos en caliente no puede romper la
  congelación por job ni la exclusión de un escritor por checkout.
- E3: fijar versiones de `markdown-it` y `mermaid` con al menos dos semanas de antigüedad. La
  instalación necesita red una vez y actualiza `package-lock.json`. Medir el tamaño del bundle con
  la carga diferida.
- E5: la instantánea no debe dejar worktrees huérfanos tras una caída. La recuperación se prueba.

## NEXT_STEPS al cerrar la fase (D087)

### Siguiente paso: elección del usuario tras cerrar el Hito 6

Estado al 2026-10-15:

- **H6.2 y el Hito 6 cerrados por decisión del usuario (D087)**, tras corregir los hallazgos de la revisión de cierre
  (D086, [entrega](H6.2_DIFF_PAGINATION.md)). Hitos 0–6 completados; el backlog no define más hitos.
- Ninguna tarea iniciada. La siguiente la elige el usuario.

#### Candidatas, sin iniciar

1. **`package.json` de un proyecto `typescript-web` nuevo** (límite de E4): el ejecutor no puede crearlo y bloquea la
   primera validación real de esos proyectos. Requiere propuesta y decisión antes de implementar.
2. **Piloto real del producto**: un recorrido completo de H6.2 con CLI reales (creación → tarea → revisión → commit →
   cierre → transición) y las métricas de objetivo del backlog. Requiere propuesta y consentimiento nuevos.
3. Mejoras menores: hora de cada validación (cambia el formato del historial), lectura del run sin decodificar el
   historial completo, avisos *low* de KaTeX.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
