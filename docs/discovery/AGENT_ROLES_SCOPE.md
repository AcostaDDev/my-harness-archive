# Agentes revisor y ejecutor con proveedor elegido por el usuario — alcance

Escrito el 2026-10-13 antes de cualquier código. D052. **No implementado.**
Sustituye la asignación fija de la especificación (§1 «Codex planifica… Claude
Code ejecuta… Codex revisa», F05 y la tabla de prompts): contradicción material
señalada y resuelta por el usuario.

## Decisiones del usuario

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

## Estado actual que cambia

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

## Alcance propuesto (incremento `cli-5`, `local-config-2`)

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

## Pendiente de caracterizar antes del código (version/help, sin consumo)

- Codex 0.162.1: flags de `workspace-write` y eventos de cambios de archivos en
  `--json`.
- Claude 2.1.295/2.1.296: salida estructurada (`--json-schema` u otra) y
  aislamiento de solo lectura con `--tools`.
- Vocabularios de esfuerzo de cada CLI.
- Si se adopta Claude 2.1.296 en el mismo incremento, ya que el enlace del
  usuario apunta a esa versión.

## Después de la implementación

- Smoke autorizado de la matriz con proveedores: propuesta aparte, después de la
  implementación offline.

Fuera: App Server/SDK, otros proveedores, la decisión inteligente de planificar
(«JEV») y la elección de proveedor por tarea.
