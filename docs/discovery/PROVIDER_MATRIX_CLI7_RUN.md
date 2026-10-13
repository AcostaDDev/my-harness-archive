# Ejecución acotada de D060 (`cli-7`): resultado y parada

Ejecutada una vez el 2026-10-13 sobre `42971ef`, con Git limpio en `main`.
Autorización del usuario: «Autorizo», tras revisar la
[propuesta D060](PROVIDER_MATRIX_CLI7_PROPOSAL.md), selecciones y límites
de nueve invocaciones/90 minutos. D061 registra el resultado;
[manifiesto y verificaciones](PROVIDER_MATRIX_CLI7_RESULT.json).
**Matriz cerrada con parada preventiva; consentimiento agotado.**

## Resultado

| # | Combinación | Run | Resultado | Invocaciones |
|---|---|---|---|---:|
| 2 | Codex → Codex | `58119c8c-314f-49dd-b1b4-9256cd680d46` | `COMMITTED`, commit `585a35c009a4e68d9d90eb4f9af981afffd9e8f2` | 3 Codex |
| 3 | Claude → Claude | — | No lanzada: parada global | 0 |
| 4 | Claude → Codex | — | No lanzada: parada global | 0 |

La 1, completada en D057, no se repitió. El recorrido de la 2 ocurrió a las
17:42 UTC; el servicio terminó antes de revisar si procedía iniciar la 3.
Sin retries, fallback, recuperación, nuevas selecciones, check/cierre de fase
o relanzamientos. No se agotó el plazo total.

## Preparación comprobada

Área `/private/tmp/harness-provider-matrix-3` (BASE): wheel, sdist,
requirements, tres scripts y tres TOML coinciden con todos los hashes del
[manifiesto D060](PROVIDER_MATRIX_CLI7_PREPARATION.json). TOML 0600;
checkouts limpios con dos commits y estado/cli-tmp vacíos al comenzar.
Wheel `79ac961dfc90f82c4b0a1437df222d93b33f1fb343e6e3f22e4437862dabe9e0`
y venv D051 conservados, sin reconstruir ni instalar. El servicio operó
desde ese paquete, fuera del checkout del producto.

Puerto :8013 sin listener observado antes y después. Solo se lanzó
`run_pairing.sh BASE codex-codex`, fuera del sandbox con aprobación.
Preflight `version_help_match` para ambos agentes Codex 0.162.1, sin flags
ausentes. Claude no invocado, ni version/help.

Antes de lanzar se guardaron HEAD/árbol, hashes de documentos, hashes de
cuatro archivos globales y nombres de entradas de `~/.claude/projects`, en
`BASE/execution-baseline.json`. Sin copiar contenidos de configuración
global ni credenciales.

## Codex → Codex: edición, validación y commit reales

| Rol | Intento | Pared | Selección solicitada |
|---|---|---:|---|
| Planificador | `a72438f4-fdb3-41d9-981f-0b629e84455f` | 11,7 s | `gpt-6-luna` / `medium` |
| Ejecutor | `4b799b76-8bcf-4abb-a663-19c985196db7` | 9,4 s | `gpt-6-luna` / `low` |
| Revisor | `e64d77ff-99c8-47a8-bad6-f65df46fd001` | 4,3 s | `gpt-6-luna` / `medium` |

Los tres COMPLETE, exit 0, terminal observado, stderr vacío, sesiones nuevas
y `cli-7` congelado. Uso reportado en el manifiesto, separado de selección
solicitada. Codex no reporta modelo/esfuerzo efectivos; retries internos,
cuota y factura de suscripción siguen desconocidos.

- Planificador: original con listas válidas, `executor_selection` objeto,
  `allowed_paths = ["src/estimate.ts"]`, `validation_commands = []`, selección
  del catálogo y rutas prohibidas concretas. No hizo falta normalizar argv.
- Escritor: `workspace-write`, red solicitada desactivada, aprobación never,
  raíz canónica explícita y `exclude_slash_tmp=true`. Aclaración de transporte
  D059 y hash contrastados. Stdout registra dos comandos de lectura/estado
  y un `file_change` completado en `src/estimate.ts`. Diff exactamente
  `tasks * 45` → `tasks * 30`, conservando validaciones y mensaje de RangeError.
- Seis comandos nativos exit 0: versiones Node/npm, `npm ci --offline`,
  check/test/build del perfil. Capturas completas sin truncamiento, hashes
  contrastados y grupos muertos. JUnit original completo, tres casos
  aprobados, sin diagnósticos: 778 bytes, SHA-256
  `08b513db4bdf77cafb7337ec8bd9ba5521dd1d4b291ccb58f01430f5500c2afb`.
- Review ACCEPT sin hallazgos/preguntas, política sin violaciones y aceptación
  elegible. Evidencia de validación/review/aceptación coincidente: base
  `a6865bcd54085b3387f22108229efda8ca1bb9c0`, huella
  `c1d3f9a7ab546ce0ac22ee563e6559dee00e0df520be4ed1f0b4374251b66b14`,
  árbol `008b8ced2a260c82ea33d827068d9fe239f3cca0`.
- Intención COMMITTED, id esperado igual al observado, autor
  `Harness Provider Matrix <matrix@example.invalid>`. HEAD tiene un único
  commit nuevo, padre igual a la regresión preparada y árbol igual al
  revisado. Única ruta cambiada `src/estimate.ts`, documentos intactos y Git
  limpio. 120 eventos. Lectores sin cambios Git observados en sus evidencias
  ni eventos de cambio de archivos en stdout.

Acredita escritura real de Codex con D059 en este ensayo. No demuestra que
las raíces temporales causaran la negativa de D057 ni permite inspeccionar
el mensaje interno de permisos que recibió el modelo.

## Cambio global observado y parada

La comprobación posterior detectó un cambio de SHA-256 en
`$HOME/.codex/config.toml`, fuera de BASE:

| Observación | Valor |
|---|---|
| Hash previo, 17:42:10 UTC | `d8ebfad0d22c39330ea177413b2e512105364312cccfac00a67145d5a3e4d978` |
| Hash posterior | `f8b81fb360dcfccf36d3aefdc7d7ebdbbbe21d756e844c3e80221c855acd8ab4` |
| mtime posterior | `2026-10-13T17:42:30.103366+00:00` |
| Inicio del escritor | `2026-10-13T17:42:29.936259+00:00` |
| Entrada presente después | `[projects."/private/tmp/harness-provider-matrix-3/codex-codex/web"]`, `trust_level = "trusted"` |

El mtime coincide con el lanzamiento del escritor. **La línea base solo
conserva hashes**: no acredita el delta exacto, que la entrada fuese nueva
ni la atribución concluyente a la CLI; otro escritor concurrente no queda
descartado. El hallazgo basta para parar preventivamente por la condición
de D060 sobre efectos fuera de BASE. El commit correcto no autoriza continuar.

Los otros tres archivos muestreados (`.claude/settings.json`,
`.claude/settings.local.json`, `.gitconfig`) conservan hashes; no se observan
entradas nuevas de proyectos Claude. Es un muestreo, sin auditoría exhaustiva
del filesystem. No se restauró, borró ni editó directamente configuración
global. Se conserva el cambio observado para diagnóstico posterior,
fuera del alcance de esta entrega.

3/4 mantienen TOML/HEAD iniciales, Git limpio, state/cli-tmp vacíos, sin
SQLite, evidencia, jobs, intentos o servicio. No se invocó Claude, auth status
ni login. Su comportamiento real con el esquema tipado D058 sigue pendiente.

## Cierre, verificaciones y evidencia

SQLite reabierta en lectura: integridad/FK correctas, ambos jobs DONE con
propietarios cerrados, tres procesos STOPPED y cero locks. Identidades de
CLI/comandos/servicio comprobadas ausentes con señal 0, sin señales de parada
adicionales. Apagado Uvicorn completo, clave retirada, `driver-exit 0` y
`serve-exit 143` por TERM normal. Sin recuperación o liberación manual de locks.

Originales en `BASE/codex-codex/state/`, snapshots API en
`BASE/codex-codex/evidence/`. Se añaden allí `sqlite-history.json`,
`process-specs.json`, `global-observation.json` y `verification.json`.
Hashes de stdout/stderr, prompts, instantáneas, verificador y línea base en
el manifiesto de resultado. `/private/tmp/h61_verify.py` no lanza proveedores
ni muta SQLite/Git/configuración; solo añade evidencias bajo BASE. El primer
pase se ajustó porque `spec.agent` es reviewer para planner/reviewer, sin
repetir el recorrido o cambiar el producto.

Verificación pertinente: recorrido real, hashes, contenido exacto, cierres,
documentación/diff/enlaces. No se repiten pytest, build del producto, cliente
Node separado o QA visual: no cambia código/UI/esquema/codec/dependencias/locks.
Las validaciones TypeScript/Node del checkout desechable sí se ejecutaron.
Sin instalación con red, publicación/push, ReferenceProject, subagentes de desarrollo
o avance a H6.2. Áreas D055/D057 sin usarse ni modificarse por esta ejecución.

Siguiente tarea separada: diagnóstico offline del cambio global, sin sesiones
de inferencia. Una ejecución posterior requiere nueva propuesta/consentimiento.
