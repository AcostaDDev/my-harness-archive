# P012-T002 — Instalación e incorporación real: paradas de preparación

Fecha: 2026-10-24. **Estado actual: preflight corregido aprobado; detenida al abrir Chrome por rechazo cross-site; no completada.**
Decisiones: [D185](../DECISIONS.md#d185--p012-t002-autorizada-y-detenida-por-caché-django-incompleta) (primera parada),
[D186](../DECISIONS.md#d186--p012-t002-descargas-autorizadas-y-falso-rechazo-de-choices-multilínea) (reanudación y segunda parada),
[D188](../DECISIONS.md#d188--p012-t002-preflight-corregido-aprobado-y-parada-en-la-apertura-de-chrome) (paquete corregido y tercera parada).
[Contrato](../NEXT_STEPS.md#p012-t002--instalación-incorporación-b-y-perfil-declarado-con-proveedores-reales),
[propuesta confirmada](P012-T001_PROPUESTA_OPERATIVA.md).

Los §§1–6 conservan el registro de la **primera parada por caché**, resuelta después por consentimiento expreso.
Los §§7–9 conservan la reanudación y segunda parada; §§10–13 registran la continuación con T008 y tercera parada.

## 1. Autorización y base

El usuario pide **«Haz commit y comienza con la siguiente tarea.»** tras confirmar T001. Se hace commit local
`dc5edd4` (`docs: confirm P012 operational validation proposal`) y se interpreta la instrucción como autorización
expresa para **T002** bajo los parámetros de T001, incluidas preparación offline, verificador con CLI falsas,
instalación, servicio/UI e invocaciones acotadas. T003/T004 no quedan autorizadas.

Base de producto `c5cfc9b4586dbdb64075624e268e2f187749d430`; antes de operar, diff nulo de fuentes del paquete,
frontend, scripts, README, metadatos y lock frente a esa base; checkout limpio después del commit T001.
Inicio UTC: `2026-10-24T16:31:37.424552+00:00`. Parada UTC: `2026-10-24T16:33:28.666320+00:00`.

Área nueva elegida en T001: `$HOME/Documents/harness-validation/p012-20261024`, fuera de checkouts,
sin enlaces en sus componentes ni ancestros Git. Creada con umask 077/directorios 0700; TOML y npmrc privados 0600.
No se reutiliza ni consulta el área de P009. No se modifica configuración global.

## 2. Preparación ejecutada

| Operación | Resultado |
|---|---|
| Revalidación `--version` y hashes de lanzadores/toolchain frente a T001 | Codex 0.164.0, Claude 2.1.310, Python 3.14.4/3.13.13, Node 24.15.0, npm 11.12.1 y uv 0.12.19 coinciden |
| Materializar TOML confirmado, sin iniciar producto | `config/harness-local.toml`, modo 0600; SHA-256 `d882c42d1385599279e740fce9a687905b4ae51330cf07767bcedb1cc72c3843` |
| npmrc de usuario y global | Archivos distintos, vacíos y privados dentro de `config/` |
| Construcción offline, UI y paquete | Exit 0; assets, sdist, wheel, pylock PEP 751 y SHA256SUMS generados |
| Integridad de artefactos generados | SHA-256 calculados y cotejados con SHA256SUMS, sin discrepancias |
| Inventario de cachés locales permitidas | 358 archivos ZIP examinados; 5 de 17 pins tienen wheel original compatible y hash del lock; **12 faltan** |

Build desde este checkout, sin registrarlo ni ejecutarlo como proyecto del harness:

```sh
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist"
```

`AREA` es el destino elegido; `REPO=$HOME/Documents/projects/my_harness`. PATH explícito de Node/uv,
`UV_OFFLINE=true`, `UV_PYTHON_DOWNLOADS=never`, `UV_NO_CONFIG=true`; npmrc vacíos del área y notificador npm
desactivado. No hubo descarga. El build reinstala frontend desde caché y recompila sus assets ignorados;
no cambia fuentes versionadas. Aviso de tamaño de chunks de Vite, sin error de construcción.

| Artefacto en `AREA/dist` | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `46d29c209f90a8f67c02e4295753688ec0c646c5c0f0259575fed5910117d9d6` |
| `harness_local-0.1.0.tar.gz` | `79e256de8a3fa14d29465fbcbaea47b8600908b7b5a1dcfd43b3f6f83cc842c5` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |
| `SHA256SUMS` | `35b32527f986e069e21df11c972048dd78b43d06b6ee050f476b6bae4e8ecb75` |

El hash observado del wheel coincide con el histórico de P011; se registra como resultado de esta construcción,
no como prueba de instalación o verificación funcional. `check_distribution.py` **no se ha ejecutado**: el inventario
revela la falta de caché antes de esa operación y aplica la parada de T001. Checksums válidos no equivalen a comprobar
miembros/metadatos ni a ensayar el wheel instalado.

## 3. Parada: wheelhouse Django incompleto

Se inspeccionan cachés locales uv del checkout/usuario y pip del usuario, incluidos cuerpos HTTP ZIP, sin red,
sin ejecutar su contenido ni copiar configuración/credenciales. Solo se aceptan archivos originales cuyo pin,
versión, tags de wheel y SHA-256 coinciden con el lock Django empaquetado (hash
`0f2ce9afc90274a6da1b6c1d8b10cc62d6f530dd0b1f1c8c95609fd27d313c1b`).
Directorios uv descomprimidos no sustituyen al wheel original con hash publicado.

Encontrados: `asgiref==3.10.0`, `packaging==25.0`, `pluggy==1.6.0`, `Pygments==2.20.0` y
`typing_extensions==4.15.0`. Su procedencia permanece en el informe privado; aún no se copian al wheelhouse.

| Pin que falta | Requisito |
|---|---|
| `Django==5.2.17` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `django-stubs==5.2.7` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `django-stubs-ext==5.2.7` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `iniconfig==2.1.0` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `mypy==1.18.2` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `mypy_extensions==1.1.0` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `pathspec==0.12.1` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `pytest==9.0.3` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `pytest-django==4.11.1` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `ruff==0.14.1` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `sqlparse==0.6.0` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |
| `types-PyYAML==6.0.12.20250915` | Wheel compatible con CPython 3.13/macOS arm64, hash del lock |

Lista exacta con todos los SHA-256 admisibles del lock original:
[P012-T002_WHEELS_FALTANTES.lock](P012-T002_WHEELS_FALTANTES.lock), hash
`ee5a8a8a404e9e19e347ac960b803fe1615fc96e6b56b21f7a983bc0bb913947`. Contiene solo esos doce pins; no autoriza instalar ni descargar nada.
Múltiples hashes para un pin son las variantes del lock: elegir **un** wheel compatible por pin, sin sdist,
reconstrucción ni resolución de nuevas dependencias, y cotejar el archivo recibido antes de usarlo.

Se detiene T002 conforme a la regla de caché incompleta de T001/NEXT_STEPS. Es un prerrequisito operativo ausente,
no un defecto acreditado del producto; no se crea tarea de corrección ni se toca código.

## 4. Consumo, estado conservado y omisiones

| Proveedor | Llamadas observadas | Techo del tramo |
|---|---|---|
| Claude | **0** | 12 |
| Codex | **0** | 3 |

Solo se lanzan CLI con `--version`, sin prompt ni modelo. No se ejecuta check-config/preflight, verificador con CLI
falsas, instalación del harness/fixture, init-db, servicio, UI, incorporación, tarea, validaciones Django o commit del
fixture. No existen SQLite operativa, repositorio B, jobs, locks o procesos del servicio/agentes de esta operación.
El build ha terminado con exit 0; el área y artefactos se conservan, sin limpieza persistente ni procesos propios activos.
T001 queda congelada en su commit; README/docs públicas, archivos de fases previas, diagramas y flujos intactos.
No se ejecutan suites del producto porque no cambia código. Tampoco se opera el Django de P009, ReferenceProject,
remotos, tags, push o publicación. Los cambios de documentación de T002 quedan sin commit.

**Lo acreditado:** construcción offline actual y checksums de los artefactos, versiones locales, materialización
privada de la configuración e identificación del prerrequisito ausente. **Lo pendiente:** verificación completa,
instalación/preflight, fixture/validaciones, incorporación y tarea COMMITTED con proveedores reales.

## 5. Continuación que requiere decisión del usuario

Dos caminos: aportar un wheelhouse local nuevo permitido con los doce archivos originales compatibles, o autorizar
consulta de metadatos públicos en PyPI y descarga de **hasta doce wheels**, exclusivamente los pins/hashes del archivo
adjunto, desde `pypi.org`/`files.pythonhosted.org` hacia `AREA/wheels`. Sin builds, scripts, actualizaciones ni
paquetes adicionales. Los cinco originales ya localizados se copiarían desde caché con verificación de hash.

La descarga no está autorizada por «comienza»: la regla de red de P012 exige su consentimiento separado con lista
y hashes. El usuario debe autorizar también **reanudar T002 tras esta parada**, manteniendo el mismo presupuesto
(sin llamadas consumidas), modelos y área. Si elige fuente local, se verifica antes de continuar y no se usa red.
Una vez resuelto: revalidar toolchain/identidades, ejecutar verificador offline, instalar el wheel y B, revisar TOML,
ejecutar las ocho comprobaciones del perfil antes del registro, preflight y recorrido UI bajo la autorización renovada.
Sin fallback ni reintento automático.

## 6. Comprobaciones del registro

- Parsers puros: 12 fases, 7 tareas P012 y 185 decisiones; 555 enlaces/anclas de los cinco Markdown
  modificados/nuevos válidos.
- Lista de faltantes: 12 pins y conjuntos de hashes copiados exactamente del lock empaquetado; hash del archivo
  comprobado. Sin dependencias adicionales.
- Presupuestos D088 correctos: STATE 11.340/24.576 bytes, base acumulada 8.718/12.288 y NEXT_STEPS 13.982/49.152.
- Diff documental revisado y `git diff --check` correcto. Cuerpos D001–D184, T001, archivos, baseline pública,
  fuentes, diagrama y flujos conservados.

No se declara completada T002 ni se adelantan T003/T004.

## 7. Reanudación autorizada y wheelhouse resuelto

El usuario responde **«Autorizar esas descargas y reanudar T002»** a la propuesta concreta de consultar metadatos
públicos en `pypi.org`, descargar hasta doce wheels desde `files.pythonhosted.org` según la lista y hashes de §3,
y reanudar con área/modelos/presupuesto intactos. Se hacen doce consultas de metadatos y se descargan doce wheels
compatibles con CPython 3.13/macOS arm64; tamaño/hash comprobados antes de escribir el archivo final.
Se copian cinco originales de las cachés ya inventariadas, revalidando sus hashes; no se descargan otros paquetes,
sources o intérpretes ni se ejecutan builds de dependencias. La instalación posterior vuelve a ser offline.

[Manifiesto saneado de los 17 wheels](P012-T002_WHEELS_VERIFICADOS.sha256), SHA-256
`d4cee2453093a3746ec3a15abe4709b222fa11ddb68646d35be672bc6d1b4e7a`. La lista de faltantes se conserva como evidencia de la primera parada; ya está resuelta.
Plan de descarga/URLs públicas, procedencia local de los cinco originales y logs íntegros permanecen privados.

| Operación tras reanudar | Resultado |
|---|---|
| `check_distribution.py --dist AREA/dist` | Exit 0: miembros/metadatos/licencias/hashes exactos y wheel instalado fuera del checkout; UI/API/sesión, definición D088, tarea/commit/reinicio y consulta restaurada con CLI falsas |
| Venv e instalación del harness | Python 3.14.4; `uv pip sync --offline … pylock.toml`, luego wheel verificado con `--offline --no-deps`; exit 0 |
| Lock Django del paquete instalado | Hash igual al confirmado en T001; copia privada usada para instalar B |
| Venv e instalación de B | Python 3.13.13; 17 wheels con `--offline --no-index --no-deps --no-build --require-hashes`; exit 0 |
| Fuente original de B | 15 archivos sintéticos, modelo Item/migración, vista/ruta, dos tests y configuración ruff/mypy; sin documentos del harness ni datos privados |
| Formato inicial del fixture | `ruff format .` como generación manual del fixture, antes de su baseline/commit; no formateador del perfil ni corrección de salida de agente |
| Dos preparaciones | Python y Django `--version`, ambas exit 0 |
| Seis validaciones del perfil declarado | pytest/JUnit **2 passed**, ruff check, ruff format --check, mypy (**10 source files**), manage.py check y makemigrations --check: exit 0 |
| Commit inicial sintético | `f6a2d9dc054725b2cd1f9e323bf387ce092925c2`, autor sintético elegido, sin remotos; manifiesto de rutas/modos/blobs/SHA-256 privado |
| `harness-local check-config TOML --preflight` instalado, fuera del checkout | **Exit 1**: revisor Claude rechazado por `unsupported_values`; ejecutor Codex compatible condicionado |

TOML sin modificaciones frente al materializado de T001; no se edita para saltar la guardia. El entorno operativo
y el fixture se conservan. El verificador ha terminado y limpiado sus temporales normales; no se mantiene servicio.

## 8. Segunda parada: lector de choices corta en el salto de línea

El informe observa Claude **2.1.310**, version/help exit 0, sin flags ausentes, pero devuelve
`unsupported_values = {"--permission-mode": ["dontAsk"]}`. La ayuda enumera ese valor en una línea de continuación.
Codex **0.164.0** pasa con `version_help_match`, `candidate`, `conditional-known-interface` e
`internal_effects_verified=false`; eso no acredita inferencia ni efectos internos.

Se acota la causa leyendo `adapters/cli_diagnostics.py:unsupported_values`: la expresión que captura
`choices`/`possible values` excluye `\n`, por lo que solo lee la primera línea de una lista partida.
Comprobación pura con **texto sintético**, sin volver a lanzar CLI ni invocar proveedores:

```text
--permission-mode <mode> Mode
    (choices: "acceptEdits", "auto",
    "bypassPermissions", "manual", "dontAsk", "plan")
--permission-prompts <target> (choices: "host", "none")
--output-format <format> (choices: "text", "json", "stream-json")
```

La función actual produce `{"--permission-mode": ["dontAsk"]}` con esa lista partida; al poner exactamente los
mismos valores en una línea produce `{}`. Reproducción privada guardada; no se copia la ayuda real a fixtures
públicos ni se interpreta la comprobación sintética como compatibilidad real nueva.

Fallo del producto confirmado y acotado como **P012-T008**, pendiente de implementación con tests sintéticos.
Sin modificar código en T002, debilitar permisos, cambiar CLI/modelo/esfuerzo, parchear TOML/SQLite, repetir
preflight, iniciar servicio o realizar llamadas. La corrección y un wheel nuevo deberán preceder a cualquier
consentimiento nuevo de reanudación real.

## 9. Estado final y comprobaciones tras la segunda parada

- Llamadas a modelos Claude/Codex: **0/0**, techo intacto **12/3**. Solo version/help en las CLI reales;
  el recorrido del verificador usa CLI falsas, sin coste de proveedor.
- Build, verificación/instalación del wheel y preparación con las ocho comprobaciones de B acreditados;
  **preflight rechazado**, init-db/servicio operativo/UI/registro/incorporación/tarea/COMMITTED sin ejecutar.
  No se acredita validación real B/D095 ni el bucle básico con proveedores.
- Sin SQLite operativa, jobs, locks o procesos propios activos. Área, wheelhouse, configuración, venv, fixture
  y evidencia privados conservados; se mantienen los hashes/base originales, sin reparación de resultados.
- No se ejecutan suites del producto: no cambia código; solo la comprobación pura del lector con texto sintético.
  La suite de dos tests Django y validadores corresponden al fixture. T003/T004 no autorizadas ni iniciadas.
- Los documentos vivos y D186 reflejan el bloqueo actual y T008 como siguiente tarea. Parsers: 12 fases,
  8 tareas y 186 decisiones; **558 enlaces/anclas válidos**. Presupuestos STATE/base/NEXT_STEPS:
  **11.539/24.576**, **8.718/12.288** y **16.461/49.152** bytes. Diff revisado y `git diff --check` correcto.
- Manifiesto de 17 wheels cotejado de nuevo contra sus archivos; bytes del fixture inicial intactos y sin SQLite
  operativa. Cuerpos D001–D184, T001, archivos históricos, fuentes, baseline pública, diagrama y flujos conservados.

## 10. Continuación autorizada con el paquete corregido

El usuario pide «Continúa con la siguiente tarea a realizar. Finaliza con un commit» después del commit de T008.
Se interpreta, con el precedente de §1/D185, como autorización nueva para T002 sobre la
[propuesta concreta de T008 §5](P012-T008_CORRECCION_PREFLIGHT.md#5-propuesta-concreta-de-continuación-de-t002-sin-ejecutar).
Se comunica ese alcance antes de operar: base nueva, `dist-t008`/`venv-t008`, mismo fixture, configuración y modelos,
techo 12 Claude/3 Codex, parada al primer fallo. Sin autorizar T003/T004, descargas ni cambios globales.

Base nueva: **`6efbd829dff16de58c39247358f0b5cf7d208466`** (`fix: parse wrapped CLI help choices within option bounds`).
Checkout limpio antes de construir. Fuente `cli_diagnostics.py` y política derivada coinciden con T008 §4;
locks, README, TOML completo (incluidos comentarios), versiones y los ocho hashes de herramientas coinciden con T001.
Área sin enlaces ni ancestros Git, destinos nuevos ausentes, fixture limpio en `f6a2d9d` y sin remotos;
los 17 wheels coinciden con el manifiesto previo. Se captura un manifiesto privado para comprobar conservación.

| Operación | Resultado |
|---|---|
| Build offline en `AREA/dist-t008` | Exit 0; UI recompilada, sdist/wheel/pylock/SHA256SUMS nuevos |
| Checksums y `check_distribution.py --dist AREA/dist-t008` | Exit 0; miembros/metadatos/licencias y recorrido del wheel instalado con CLI falsas |
| `AREA/venv-t008`, Python 3.14.4 | Instalación offline desde pylock con hashes, luego wheel `--no-deps`; exit 0 |
| Política del paquete instalado | `1156d0c9c8ad969c6762653eadadb5626c3d8f203d6e7ce821611d6286cc79d5`, igual a T008 |
| `check-config TOML --preflight`, fuera del checkout | **Exit 0**; Claude 2.1.310 y Codex 0.164.0 `version_help_match`, `unsupported_values={}` |
| Compatibilidad de ambas CLI | `candidate`, `conditional-known-interface`, `internal_effects_verified=false`; sin acreditar auth/inferencia |
| Dos preparaciones y seis validaciones de B | Exit 0: Python 3.13.13, Django 5.2.17, pytest/JUnit **2 passed**, ruff check/format, mypy **10 fuentes**, check y makemigrations |
| Puertos 8024/8025 antes de arrancar | Libres |
| `init-db --database AREA/state/harness.sqlite3` | Exit 0; base nueva `0025_project_work_languages` |
| `serve` instalado con TOML original, puerto 8024 | Arranque completo, sesión local bajo `AREA/tmp`; sin registrar proyectos |

| Artefacto en `AREA/dist-t008` | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `5df9e000dd9f1bb9056103b519439a8352f48c4ba57c4173c2482f5ddca15e0b` |
| `harness_local-0.1.0.tar.gz` | `96c0a7d7971b6ad5b43f9645156755c9d4c757f3d6ce064618c3fb5e8cc7ee53` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |
| `SHA256SUMS` | `cf1d75a3078781f745f1d2ec14bc875089a5149bba6c2827efb4758c3d877a83` |

Build y verificador usan los comandos de T008 §5 con caché del checkout, `TMPDIR=AREA/tmp`, npmrc privados vacíos,
`UV_OFFLINE=true`, `UV_PYTHON_DOWNLOADS=never` y `UV_NO_CONFIG=true`. La instalación usa los comandos de T001 §3
con destinos nuevos. Servicio/preflight desde AREA, HOME privado y entornos explícitos del TOML para los agentes.
Sin descargas, configuración global ni importación del producto desde el checkout. Logs completos privados.

## 11. Tercera parada: apertura automatizada de Chrome

La primera apertura mediante la herramienta de navegador de `http://127.0.0.1:8024/` muestra:

```json
{"detail":{"code":"origin_rejected","diagnostic":"Request from a foreign site."}}
```

La lectura de `api/security.py:local_request` identifica ese diagnóstico exclusivamente con
`Sec-Fetch-Site: cross-site`. La guardia funciona según su contrato; **no se acredita un defecto del producto**
ni se conoce aún por qué la apertura automatizada se clasificó así. No se capturan los headers del navegador.
El Host/puerto usados coinciden con el servicio. No se cambia la guardia, cabeceras, navegador ni configuración
para saltarla; tampoco se repite navegación, login, registro o llamada tras el rechazo.

Se aplica la parada de permisos de T001 §6. Se detiene el proceso propio con SIGINT tras comprobar su comando;
el proceso termina normalmente y el puerto 8024 queda cerrado. SQLite conservada, con **0 jobs, 0 runs,
0 conversaciones, 0 incorporaciones y 0 locks de checkout**. No se ha invocado ningún modelo: **Claude 0/12,
Codex 0/3**. La sesión temporal se elimina en la limpieza normal del servicio.

## 12. Evidencia acreditada, límites y conservación

T008 queda acreditada además en el preflight de las CLI reales instaladas: ya no rechaza la lista multilínea.
El paquete corregido se ha construido, verificado e instalado fuera del checkout; fixture y precondiciones en verde,
SQLite inicializada y servicio arrancado/detenido. **UI autenticada, registro, incorporación B, perfil D095 con
agentes y tarea COMMITTED siguen sin ejecutar**. No se declara completa T002 ni se adelantan T003/T004.

Manifiesto privado cotejado tras parar: `AREA/dist` y configuración original conservados por bytes; los 15 archivos
versionados de B conservados por bytes y modos; baseline Git intacta. `venv` anterior no se usa ni se modifica;
los nuevos artefactos se conservan junto a los originales. El área no se limpia, SQLite no se edita manualmente.
No hay cambios del producto, datos/modelos/migraciones, flujos, baseline pública o fases archivadas en este commit.
No se repiten suites del producto: solo build/verificador, preflight y ocho checks del fixture necesarios en el tramo.

## 13. Propuesta de continuación para HITL, sin ejecutar

Reanudar T002 con `dist-t008`/`venv-t008` ya verificados y **la misma SQLite**, sin repetir init-db/build/instalación.
Revalidar conservación, configuración/identidades y puerto libre; reiniciar el servicio en 8024 y navegar escribiendo
la URL en la barra de direcciones de Chrome, como navegación iniciada por el usuario, en lugar de la apertura
automatizada anterior. Mantener las guardias Host/Origin/CSRF intactas y no sobrescribir cabeceras. Este método es
una propuesta pendiente de comprobar, no un éxito anticipado. Si vuelve a rechazarse, parar y conservar evidencia.

Si abre, continuar login/registro/B/tarea exclusivamente desde UI bajo T001, con misma pareja/modelos y techos
**12/3**, **0/0 consumidos**, sin fallback ni nuevas descargas; 4 h de techo por sesión. Detener al terminar o al
primer fallo. T003/T004 siguen sin autorización. La continuación requiere respuesta del usuario tras esta parada.

## 14. Comprobaciones del registro de la tercera parada

- Parsers puros: **12 fases, 8 tareas P012, 188 decisiones**; **567 enlaces/anclas relativos** válidos en los
  cinco Markdown modificados. Presupuestos STATE/base/NEXT_STEPS: **11.820/24.576**, **8.718/12.288** y
  **17.121/49.152** bytes.
- Cuerpos D001–D187 y §§1–9 anteriores de este registro conservados; solo se actualiza su cabecera y se añaden
  estas secciones. T001/T008, archivos históricos y baseline pública intactos.
- Hashes de la distribución nueva contrastados con SHA256SUMS; política instalada y manifiesto de conservación
  comprobados. Diff revisado y `git diff --check` correcto; solo `docs/**`, sin suites adicionales del producto.
