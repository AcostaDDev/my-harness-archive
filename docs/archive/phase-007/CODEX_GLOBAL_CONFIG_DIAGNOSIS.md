# Diagnóstico offline de la configuración global de Codex (D062)

Completado el 2026-10-13 sobre `f930dc5`, Git inicialmente limpio. Petición
del usuario: «continúa», aplicada únicamente a la tarea activa de diagnóstico
offline de NEXT_STEPS. [Hallazgo D061](PROVIDER_MATRIX_CLI7_RUN.md),
[evidencia/verificaciones D062](CODEX_GLOBAL_CONFIG_DIAGNOSIS.json).
No se ejecutó ninguna CLI real, sesión, preflight, login o inferencia.

## Conclusión

**El delta de D061 está acreditado ahora:** se añadió exactamente una sección
de confianza para el checkout de Codex→Codex. La CLI 0.162.1 contiene una
vía interna de persistencia de confianza en `config.toml`; los flags usados
omiten carga de configuración, reglas y persistencia de sesiones, sin
establecer una frontera de escritura para el propio proceso CLI.

La vía estática, el delta y los tiempos hacen **muy probable** un efecto de
arranque de Codex, antes de los comandos visibles del modelo. La atribución
al proceso exacto sigue siendo una inferencia: no se conservó una auditoría
de syscalls ni se hizo una nueva reproducción dinámica. No se atribuye el
cambio a una herramienta de edición del modelo ni al motor Python.

**No se implementa una corrección de transporte:** ninguna opción candidata
ha demostrado offline impedir esa persistencia conservando la autenticación
existente y los límites D024/D059. Se registra este límite antes de modificar
el diseño. `cli-7`, contratos, permisos, historiales y cuarentena se conservan.

## Delta exacto verificado por hashes, sin restauración

La configuración actual conserva el hash posterior registrado en D061. Se
lee una vez y se construye una inversa solo en memoria: quitar la sección
observada, desde su cabecera hasta la siguiente sección TOML, sin quitar
bytes anteriores. Esa candidata coincide con el hash previo de la línea base.

```toml
[projects."/private/tmp/harness-provider-matrix-3/codex-codex/web"]
trust_level = "trusted"

```

| Comprobación | Resultado |
|---|---|
| SHA-256 previo D061 | `d8ebfad0d22c39330ea177413b2e512105364312cccfac00a67145d5a3e4d978` |
| SHA-256 posterior y actual | `f8b81fb360dcfccf36d3aefdc7d7ebdbbbe21d756e844c3e80221c855acd8ab4` |
| Inicio de la sección en bytes actuales | 3094 |
| Tamaño de la sección, incluidos sus saltos finales | 93 bytes |
| SHA-256 de esos 93 bytes | `cd6b9416e00778c364a8b7094db8d800aa356b14256eaf76dd62a9e6c9d76faa` |
| SHA-256 de la inversa en memoria | Igual al previo D061 |

Esto acredita que la entrada no existía antes y que la adición es todo el
delta de bytes entre ambos hashes. No se inventa una copia previa ni se
deduce el delta por parecido semántico. No se guardan la configuración
completa ni la inversa; solo hashes, ubicación/tamaño y la sección del
checkout de ensayo. No se abre `auth.json` ni se extraen credenciales.

## Binario fijado y persistencia interna

Se lee el mismo nativo que en D059, resuelto por el wrapper npm instalado:
`@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex`.
246642624 bytes, SHA-256
`74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0`.
Solo lectura de bytes, símbolos y desensamblado acotado con `objdump`;
ninguna función de Codex se invoca.

Las descripciones de argumentos del binario delimitan los flags:

| Flag | Semántica anunciada, traducida |
|---|---|
| `--ignore-user-config` | No cargar `$CODEX_HOME/config.toml`; autenticación sigue usando CODEX_HOME |
| `--ignore-rules` | No cargar archivos execpolicy de reglas de usuario/proyecto |
| `--strict-config` | Rechazar campos no reconocidos de config.toml |
| `--ephemeral` | No persistir archivos de sesión |

Ninguna descripción promete impedir escrituras de configuración o aislar
el HOME. El registro congelado de D061 usa HOME real y no contiene CODEX_HOME:
sus claves son HOME, USER, PATH, TMPDIR y LANG. `USER` validado por UID
conserva D024; no separa el estado escribible de la autenticación.

| Evidencia estática | Ubicación |
|---|---|
| Llamada a `ConfigManager::current_cli_overrides` en la ruta de confianza | `0x101876b98` |
| Llamada directa a `codex_core::config::set_project_trust_level` | `0x101876bb8` → `0x1053feb34` |
| Esa función une la ruta con el literal `config.toml` | literal en offset de archivo 188751713 |
| Llamada a `apply_blocking_to_resolved_file` | `0x1053febd0` → `0x10595f740` |
| Diagnóstico de fallo que continúa con confianza en memoria para el thread | literal en offset 185608673, referenciado junto a la llamada |
| `FileAuthStorage::load` une su raíz con `auth.json` | función `0x106e10cf4`, literal en offset 189224334 |

La ruta pertenece a la infraestructura interna de App Server de la CLI,
según la llamada a ConfigManager, el diagnóstico y los literales thread/start.
Eso no cambia la integración del producto: Harness Local sigue invocando CLI,
sin adoptar App Server/SDK. El optimizador omite nombres de algunas funciones;
no se usa el nombre del símbolo externo anterior como identidad del caller.
No se certifican todas las condiciones que llegan a esa rama ni una opción
de supresión a partir de este desensamblado parcial.

## Cronología conservada

| Dato D061 | UTC |
|---|---|
| Inicio de captura del escritor | 17:42:29.936259 |
| mtime de configuración global | 17:42:30.103366 |
| Registro de `thread.started` | 17:42:30.138617 |
| Registro del primer comando del modelo | 17:42:34.296534 |

Los tiempos de eventos son de recepción/persistencia por el harness, no
timestamps de ejecución internos de Codex. Son compatibles con persistencia
de confianza al crear el thread, anterior a las herramientas visibles;
no sustituyen una traza de quién escribió el archivo.

## Opciones consideradas y límites antes de implementar

| Opción | Por qué no se aplica en esta entrega |
|---|---|
| Añadir `-c projects.<checkout>.trust_level="trusted"` | La confianza en memoria no prueba que la ruta de thread/start omita persistir. Un fake que exija el override solo verificaría nuestro supuesto. |
| CODEX_HOME privado por intento | Confina la raíz de estado, pero desplaza también el almacén de auth anunciado por la CLI. No está verificado que conserve la sesión existente sin copiar/enlazar credenciales o login. |
| HOME sintético | Cambia autenticación y más fuentes del entorno; no es equivalente al entorno D024 ya comprobado. |
| Cambiar almacén a keyring/ephemeral o versión de CLI | La autenticación/configuración efectiva no está caracterizada para esa combinación; altera el baseline. |
| Restaurar la entrada tras ejecutar o precrear confianza global | Sigue modificando configuración global, borra evidencia o puede pisar cambios concurrentes; no corrige la frontera. |
| Contener el proceso CLI desde el operador | Es una posible frontera real; requiere alcance explícito, compatibilidad de auth/refresh/archivos auxiliares y pruebas propias. El sandbox de herramientas actual no la certifica. |

El límite es de contención del proceso CLI y de separación estado/auth,
no del permiso de editar `src/estimate.ts`. No se cambia a read-only el
escritor, ni se amplían sandbox/red/aprobaciones para sortear el hallazgo.
Los mensajes sobre confianza en memoria permiten estudiar una contención
externa como siguiente propuesta; no garantizan su funcionamiento real.

## Verificación y cierre

- Verificador retenido en
  `/private/tmp/h62_codex_diagnosis-20261013/verify.py`, junto con tres
  desensamblados acotados y `result.json`; hashes en el manifiesto.
- Cinco casos con HOME/configuración completamente sintéticos: adición
  exacta aceptada y cuatro negativos (cambio ajeno, hash posterior incorrecto,
  ausencia de delta y cabecera duplicada). Comprueban el método de prueba
  por hashes, **no simulan la persistencia ni la autenticación de Codex**.
- Manifiesto/línea base D061, sus 14 instantáneas referenciadas y hashes de
  prompts coincidentes. SQLite abierta solo en lectura. La configuración
  global mantiene el mismo hash durante y al finalizar el diagnóstico.
- Documentación, JSON, enlaces locales y diff comprobados. Sin pytest,
  builds, Node o QA visual nuevos: solo cambia documentación. Sin cambios
  de producto, esquema, codec, `cli-7`, local-config, dependencias o locks.
- Sin red, instalaciones, CLI reales, auth status/login/refresh, subagentes,
  harness de desarrollo, publicación/push o cambios de las áreas de matriz.

Siguiente tarea separada: concretar una propuesta de contención del proceso
Codex que preserve autenticación existente, con alcance y criterios offline
antes de implementar. Matrices y consumo siguen sin autorización nueva;
H6.2 no iniciado. El diagnóstico se completa con el límite registrado, sin
presentar una corrección hipotética como implementada.
