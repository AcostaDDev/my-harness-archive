# Propuesta de contención del proceso Codex (D063)

Preparada el 2026-10-13 sobre `9db047a`, Git inicialmente limpio. Completa la
propuesta activa de NEXT_STEPS; **no implementa transporte ni habilita consumo**.
[Antecedente D062](CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
[evidencia de esta entrega](CODEX_PROCESS_CONTAINMENT_EVIDENCE.json).

## Resultado y decisión propuesta

La candidata sustentada para estudiar es una **frontera externa de escritura
para el proceso completo en macOS**, conservando HOME, USER y la localización
original de auth, con denegación de escrituras fuera de raíces explícitas.
Un experimento con `sandbox-exec` y Python ha leído auth ficticia y ha impedido
modificarla, modificar configuración y escribir fuera de las raíces permitidas,
también desde un hijo. No es una prueba del login de Codex ni un adaptador listo.

No se ha encontrado una separación estado/auth verificable para el binario
fijado que permita cambiar CODEX_HOME y garantizar la sesión existente sin
copiar/enlazar credenciales. No se afirma que tal opción sea imposible: falta
un contrato y evidencia de resolución/refresh para 0.162.1. Por ello no se
propone migrar el almacén ni cambiar HOME como solución inmediata.

**Límite material antes de cualquier implementación:** conservar ubicación y
lectura de credenciales no garantiza conservar autenticación funcional.
Denegar su persistencia puede romper refresh; permitir red puede renovar o
invalidar tokens en el servidor incluso si la escritura local falla. Una
frontera de filesystem no promete «sin refresh». No se relaja la prohibición
de cambios globales ni se autoriza esa comprobación real en esta entrega.

## Autoridades y fuentes offline

- [D024](../../DECISIONS.md#d024--entorno-del-smoke-validado-por-uid-y-hash-de-configuración-nuevo):
  HOME/PATH/TMPDIR/LANG y USER validado por UID, sin herencia ambiental de
  secretos. D024 prueba una dependencia de Claude, no el almacén de Codex.
- [D049](../phase-006/LOCAL_CONFIG.md): TOML privado del operador, confianza y entornos
  explícitos, composición congelada, cuarentena antes de efectos. La versión
  actual es local-config-2 por D052.
- [Adaptador actual](../../../src/harness_local/adapters/cli_agents.py): cli-7
  lanza el proceso con entorno completo; omite carga de configuración/reglas y
  sesiones, solicita sandbox read-only/workspace-write a las herramientas.
  Esto no encierra las escrituras internas de la CLI. D059 conserva checkout
  canónico en writable_roots, exclude_slash_tmp y TMPDIR explícito.
- [Especificación §10](../phase-000/01-especificacion-harness-local.md): permisos como
  intersección; worktree y comprobación de diff no constituyen sandbox.
  [Backlog](../phase-000/02-backlog-y-plan-de-desarrollo.md): núcleo independiente de
  plataforma, CLI primero; esta exploración no introduce Docker obligatorio.
- D062 localiza `FileAuthStorage::load` → `auth.json` bajo su raíz y la
  persistencia de confianza en config.toml; recoge la ayuda que liga auth a
  CODEX_HOME. SHA-256 del nativo comprobado de nuevo, sin ejecutarlo:
  `74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0`.
- Se localizaron en sus bytes `cli_auth_credentials_store`, `FileAuthStorage`,
  `KeyringAuthStorage`, `EphemeralAuthStorage` y `refresh_token`. Esto acredita
  presencia, **no selección efectiva, precedencia ni compatibilidad**. No se
  abrió auth.json real, configuración global ni llavero. No se invocó Codex.
- Consulta OpenAI Docs limitada a evidencia local por el alcance offline; no
  se usa documentación web actual para certificar el comportamiento del pin.

## Auth y estado: inventario de requisitos

| Fuente/efecto | Evidencia disponible | Tratamiento propuesto y pendiente |
|---|---|---|
| Archivo auth bajo CODEX_HOME o raíz derivada de HOME | Ruta FileAuthStorage acreditada por D062; almacén efectivo de la sesión no inspeccionado | Lectura por CLI en origen, jamás copia, enlace o persistencia en artefactos. Escritura, rename, unlink y chmod denegados. Confirmar fuente efectiva sin exponer valores antes de una prueba real. |
| Llavero | Símbolo KeyringAuthStorage presente | Fuera de la candidata inicial: IPC con un servicio puede modificar estado fuera del sandbox. No dar por seguro por proteger sus archivos. No cambiar el selector ni consultar el llavero. |
| Auth efímera/API key/variables de token | Símbolo efímero presente; semántica no caracterizada | No inyectar secretos por env/stdin/argv ni convertir suscripción a API; no hay puente de credenciales autorizado. |
| Refresh remoto y persistencia local | `refresh_token` presente; flujo exacto no caracterizado | Si requiere escritura, fallo explícito. No se concede excepción ni se reintenta; falta determinar efectos remotos y conducta real al fallar save. |
| Confianza/config.toml | D061/D062 acreditan delta y vía interna | Denegar toda escritura al HOME original, incluidos temporales hermanos y reemplazos atómicos; no precrear confianza ni restaurar después. |
| Historial, logs, SQLite/WAL/SHM, cachés, locks de CLI | Inventario exacto de rutas/requisitos pendiente | No permitir todo CODEX_HOME. Cada redirección necesita soporte acreditado del pin; si exige escribir en origen, detener, no ampliar por conveniencia. |
| TMPDIR y checkout | Explícitos/congelados en cli-7 | TMPDIR nuevo y privado por intento; checkout escribible solo para ejecutor; lector sin excepción al checkout. Nunca todo /tmp o HOME. |
| Artefactos del harness y SQLite operativa | Escritos por el padre/adaptador | Permanecen fuera de raíces escribibles del hijo; stdout/stderr mediante pipes, no entregar descriptores de DB o archivos privados. |

La candidata limita escrituras directas y heredadas; **no aísla lecturas de
secretos del modelo**, no controla por sí sola tráfico de inferencia y no
cubre servicios a los que el proceso delegue escrituras. El sandbox interno
seguirá siendo necesario para las herramientas; no se elimina por añadir el
externo. La composición de ambos necesita pruebas, no una suposición.

## Comparación de alternativas para 0.162.1

| Opción | Ventaja | Límite / decisión |
|---|---|---|
| Contención externa macOS manteniendo HOME/auth | Conserva las rutas y no duplica secretos; puede denegar la escritura interna de confianza | Candidata para calificación offline. Fallo de refresh, sandbox anidado, IPC, auxiliares y errores de persistencia no resueltos. |
| CODEX_HOME privado con auth separado | Estado auxiliar podría vivir por intento | No hay ruta separada acreditada ni resolución del keyring verificada; no elegir basándose solo en símbolos. Requiere caracterización adicional o capacidad upstream documentada para el pin. |
| HOME privado, copia o symlink de auth | Haría localizable un archivo | Cambia D024 o expone/duplica credenciales; no propuesto. Un enlace tampoco confina las escrituras al destino. |
| Confianza por override, chmod del HOME o restauración posterior | Cambio pequeño | Override no prueba ausencia de persistencia; chmod afecta al usuario y es reversible por el dueño; restauración modifica globales y pierde concurrencia/evidencia. Descartados. |
| Cuenta separada/VM/contenedor | Otra frontera de sistema | Nueva autenticación/operación y posible copia de secretos; no conserva sesión por defecto. Fuera de alcance, sin convertirlo en requisito del MVP. |

Portabilidad: el ensayo es únicamente macOS arm64 de este equipo. La presencia
de `/usr/bin/sandbox-exec` no promete disponibilidad futura ni una API portable.
Linux necesitaría una implementación y pruebas propias (p. ej. aislamiento de
montajes/credenciales); Windows, otra frontera nativa. Ninguna se declara
soportada. Backend ausente o incompatible debe rechazar, nunca lanzar sin él.

## Experimento realizado, separado del producto

[Sonda retenida](CODEX_PROCESS_CONTAINMENT_PROBE.py), solo biblioteca estándar;
HOME sintético con token literal `FAKE-NOT-A-CREDENTIAL`, USER del UID local,
PATH mínimo, TMPDIR privado, dos archivos originales y checkout desechable.
No importa harness ni ejecuta CLI, shell de modelo o autenticación de proveedor.
Perfil experimental: permitir operaciones por defecto, denegar red y todas
las escrituras de archivo, y permitir escritura solo en `allowed/` y `checkout/`.
**No es un perfil de producción**: no restringe IPC ni lecturas generales.

Primera aplicación dentro del sandbox de desarrollo: exit 71,
`sandbox_apply: Operation not permitted`, antes de iniciar el hijo. No se
interpretó como prueba de contención. Segunda ejecución fuera, autorizada por
el mecanismo de permisos, con área sintética nueva: salida esperada 23.

Resultados: lectura ficticia correcta; ocho denegaciones reales del SO
(config, auth, unlink, chmod, creación en HOME, temporal exterior, escape por
symlink y reemplazo atómico); escritura de temporal/checkout permitida;
un descendiente también recibe denegación. Hash, modo y mtime de ambos
originales ficticios se conservan. Salida 23 deliberada representa fallo
terminal si una escritura de refresh fuese necesaria; un solo lanzamiento
por ensayo, sin retry/fallback. **La decisión de fallar es del fake**: no
certifica que Codex reporte ni propague igual ese error. Red denegada por
perfil, sin ensayo de sockets ni solicitudes remotas.

Reproducción manual, macOS y sin proveedores:

```sh
python3 docs/discovery/CODEX_PROCESS_CONTAINMENT_PROBE.py
```

La sonda conserva resultados bajo `/private/tmp/h63-containment/` y no limpia
áreas anteriores. Si no puede aplicar el sandbox, falla; no se relanza fuera
automáticamente. No es un check portable ni forma parte de pytest de producto.

## Alcance separado para calificar e implementar después

Primero calificar un lanzador experimental **solo sintético**, sin conectarlo
a la composición real. Matriz de aceptación pendiente:

1. HOME/auth ficticios existentes, ausentes e ilegibles; escritura de refresh
   denegada con diagnóstico y conteo de invocaciones uno. Nunca tokens en
   stdout/stderr, intención o hash de configuración; metadatos de prueba sí.
2. Lector no escribe checkout; escritor solo en checkout/TMPDIR exactos.
   Canonicalización, rutas con espacios/comillas, `..`, enlaces de raíz y
   escapes por symlink/hardlink, rename, unlink, metadatos y subdirectorios.
   Rechazar raíces solapadas con HOME/estado/artefactos o excesivamente amplias.
3. Estado auxiliar simulado (config temporal/rename, caché, SQLite y locks),
   intentos de escritura fuera de TMPDIR y auth inmutable después de caída.
4. Descendientes, sandbox anidado con restricciones de herramientas equivalentes
   a D059, descriptores heredados, IPC/delegación. Si hay vías no contenidas,
   delimitarlas o rechazar soporte; no anunciar aislamiento completo.
5. Lanzador ausente/perfil inválido/denegado → ningún proceso objetivo; sin
   bypass automático. Exit, señal, terminal ausente, timeout/cancelación y
   grupos bajo el protocolo gate/identidad existente antes de efectos.
6. Captura y errores distinguen rechazo de lanzamiento, fallo de proceso,
   auth sintética y persistencia denegada. No clasificar cualquier exit como
   auth ni aceptar éxito por conservar hashes si hubo efectos desconocidos.

Solo tras ese dictamen, delimitar integración del adaptador. Propuesta de
impacto, **no cambios aplicados**: nuevo backend explícito en configuración del
operador y hashes de perfil/raíces/launcher/plataforma; nuevo `cli-8` al cambiar
transporte y `local-config-3` si se amplía el TOML. Preflight también debe pasar
por la frontera; `check-config` sin preflight sigue sin procesos. Comparación
congelada debe poner jobs cli-7/composición anterior en cuarentena antes de
cualquier efecto, nunca migrar su historial. No basta un wrapper oculto en
PATH. El núcleo sigue sin conocer sandbox-exec. Schema/codec solo cambiarían
si la evidencia requerida no cabe en los contratos actuales; no se decide una
migración especulativa. Claude y validadores quedan fuera del alcance, con sus
límites existentes explícitos.

## Puerta para una comprobación real futura

No basta aprobar este documento. Antes de solicitar consumo: resolver fuente
de auth, auxiliares obligatorios, composición del sandbox y qué puede hacer
refresh sin persistencia. Si no puede garantizarse «sin refresh» con la CLI
fijada, registrar incompatibilidad; pedir una decisión específica sobre ese
riesgo o una capacidad distinta, sin fingir que solo es un permiso de lectura.

Una propuesta nueva deberá fijar ejecutable/hash, paquete, perfil, entorno y
raíces, modelos/esfuerzos elegidos por el usuario, herramientas y red, número
máximo de invocaciones/timeouts, efectos locales y remotos autorizados,
observabilidad sin secretos y parada al primer fallo. No login/logout,
reparación de credenciales, copias/enlaces, excepciones de escritura global o
reintentos implícitos. Retries internos siguen desconocidos (D019). Cualquier
cambio global obliga a detener y conservar evidencia, nunca restaurar solo.

La prueba de auth y la matriz 3/4 son alcances distintos; D050/D055/D057/D060
siguen agotados. No se repite la 1 o la 2 ya completas para explorar auth.
H6.2, recuperación/locks y publicación/push permanecen fuera.

## Cierre de aceptación

Propuesta concreta, opciones, frontera, fuentes y estado/auth identificados;
evidencia offline reproducible y límites explícitos. D024/D059, versiones,
contratos e historiales conservados. Cero proveedores, preflight real, login,
refresh, lecturas de secretos, cambios globales o harness de desarrollo.

Verificación proporcional: sonda OS descrita, lectura estática/hash del binario,
JSON, sintaxis Python sin ejecutar proveedor, enlaces locales y diff. No suite
pytest/build/Node/QA visual: no cambia código de producto ni UI. **No hay
contención de producto implementada ni autenticación real certificada.**
La siguiente tarea es la calificación offline acotada anterior; no iniciada.
