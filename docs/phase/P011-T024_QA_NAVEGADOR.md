# P011-T024 — QA de navegador del candidato instalado

Fecha: 2026-10-24. Decisión: [D180](../DECISIONS.md#d180--p011-t024-qa-de-navegador-del-candidato-y-tres-correcciones-de-presentación).
Base: `98f7667`. Tarea de [NEXT_STEPS](../NEXT_STEPS.md#p011-t024--qa-de-navegador-del-candidato-instalado);
candidato de [T016](P011-T016_PRIMER_USO_QA.md). Cierra la QA visual conjunta pendiente de T010/T021/T022.

## 1. Alcance autorizado (HITL)

Propuesta presentada antes de ejecutar y autorizada por el usuario («Autorizo»):

| Punto | Decisión |
|---|---|
| Candidato | `build_distribution.py` + `check_distribution.py` de HEAD en el scratchpad de la sesión, instalación del README en un venv del scratchpad, todo `--offline` con `.local/uv-cache`; sin red |
| Datos | [`P011-T024_seed.py`](P011-T024_seed.py), que reutiliza el driver de T016: CLI `claude` falsa, ejemplo mínimo del README y API con sesión/CSRF; `serve` en `127.0.0.1` con puerto aleatorio hasta un fichero de parada |
| Navegador | Claude in Chrome, pestaña nueva en el Chrome del usuario, solo sobre la URL de loopback; clave de sesión sintética del propio servicio |
| Cierre | Servicio detenido, pestaña cerrada y scratchpad desechable; capturas saneadas en [`P011-T024_QA/`](P011-T024_QA/) |
| Matriz (2.º HITL) | Todas las pantallas en las 8 combinaciones, con capturas representativas (no una por celda) |

Sin credenciales, proveedores, configuración personal (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`) ni
datos privados. El driver lee del checkout solo el ejemplo TOML y la sonda pública de pruebas (`--clone` = checkout).

## 2. Datos sintéticos sembrados

| Proyecto | Estado | Para qué pantalla |
|---|---|---|
| `alpha` | Creado desde cero (trabajo es), tarea COMMITTED, P001 cerrada con tag y archivo | Resumen, fase cerrada, run con commit |
| `beta` | Incorporado desde un repositorio existente (trabajo en), tarea COMMITTED | Incorporación, chat, ajustes (idioma de trabajo fijo) |
| `gamma` | Creado (trabajo en); la validación de su tarea falla dos veces → run **STOPPED** | Tarea, run detenido con diagnóstico y decisión |
| `delta` | Creado (trabajo es) con definición respondida y borradores sin aceptar | Creación con propuestas pendientes |
| `epsilon` | Registrado y su carpeta movida después | Proyecto no disponible con diagnóstico del servicio |

## 3. Método

- **Pantallas (14):** proyectos, nuevo proyecto, creación (`delta`), incorporación (`beta`), resumen (`alpha`), fase
  cerrada, tarea (`gamma`), run detenido, run con commit, chat, ajustes, preferencias, proyecto no disponible y 404.
  Aparte: puerta de sesión (en/es, claro/oscuro), diagnóstico del servicio en un formulario (vista previa de carpeta con
  ruta relativa → 422 sin mutar nada) y foco por teclado.
- **Combinaciones (8):** idioma visual en/es (cambiado desde la pantalla de Preferencias y por su API) × tema
  claro/oscuro (selector de la cabecera, `harness-theme`) × escritorio 1440 px / móvil.
- **Móvil:** Chrome no reduce la ventana por debajo de **500 px** CSS (ya bajo el breakpoint de 880 px). Se emula además
  una maquetación de **390 px** con `zoom` CSS en la raíz para medir desbordes. El iframe de 390 px queda descartado
  porque el servicio prohíbe el embebido (protección anti-framing correcta).
- **Auditoría automática** ([`P011-T024_audit.js`](P011-T024_audit.js)) en cada carga: claves de catálogo crudas,
  marcadores sin sustituir, desbordes horizontales de página, controles sin nombre accesible y contraste WCAG AA del
  texto (4,5:1; 3:1 grande; controles deshabilitados exentos). Validada con un elemento de contraste 1,86 y un botón
  sin nombre inyectados, que detecta. Además: `lang` del documento, título, consola sin errores, revisión visual de
  cada captura (arriba y desplazada en móvil).
- **Re-verificación** con el candidato corregido: barrido SPA (`pushState`) de las 14 pantallas por combinación con la
  misma auditoría y capturas de las secciones corregidas.

Nota de método: la navegación de la extensión llega con `Sec-Fetch-Site: cross-site` y la guardia del servicio la
rechaza (`origin_rejected`, diseño anti-CSRF); se recarga desde la propia página (same-origin). Una URL escrita o
abierta desde el terminal llega como `none` y no se ve afectada.

## 4. Hallazgos y correcciones

| # | Hallazgo (todas las combinaciones) | Corrección |
|---|---|---|
| 1 | Run: «Command duration: 0.03816141700008302 s», float crudo y con punto también en es | `Tests.tsx` pasa el número a `tests.seconds` (formato `Intl` del idioma: «0.042 s» / «0,042 s»); la columna de duración por test usa `Intl.NumberFormat` |
| 2 | Fase cerrada: «Fase cerrada sobre este READY el 2026-10-24T07:59:05.496378+00:00», ISO crudo | `Phases.tsx` usa `rich` con `when()` (fecha local, ISO en el tooltip): «24/10/26, 10:18» / «10/24/26, 10:18 AM» |
| 3 | Intentos del run: «Intento 2 executor · COMPLETE», rol y estado sin traducir | `Run.tsx` traduce el rol con `ROLES` (metrics) y `ui.tsx` añade al mapa de `Status` los estados de intento que guardan los adaptadores (`COMPLETE`, `PARTIAL`, `INVALID`, `CANCELLED`, `TIMEOUT`/`TIMED_OUT`) con 5 claves en/es |

Regresiones Node nuevas en `frontend/tests/i18n.test.mjs`: duración localizada desde el catálogo real y etiqueta
propia en/es para cada resultado de intento. Capturas [antes](P011-T024_QA/before-es-light-run-duration-jobs.jpg) /
[después](P011-T024_QA/after-es-light-desktop-run-duration-jobs.jpg) en §6.

## 5. Matriz por pantalla y combinación

Leyenda: **OK** sin hallazgos; **F→OK** hallazgo de §4 corregido y re-verificado. Columnas: idioma/tema/tamaño (D =
escritorio 1440 px, M = móvil 500 px + 390 px emulado).

| Pantalla | en/cl/D | en/os/D | en/cl/M | en/os/M | es/cl/D | es/os/D | es/cl/M | es/os/M |
|---|---|---|---|---|---|---|---|---|
| Proyectos | OK | OK | OK | OK | OK | OK | OK | OK |
| Nuevo proyecto (+ diagnóstico 422) | OK | OK | OK | OK | OK | OK | OK | OK |
| Creación (`delta`, borradores) | OK | OK | OK | OK | OK | OK | OK | OK |
| Incorporación (`beta`) | OK | OK | OK | OK | OK | OK | OK | OK |
| Resumen (`alpha`) | OK | OK | OK | OK | OK | OK | OK | OK |
| Fase cerrada (`alpha` P001) | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK |
| Tarea (`gamma`) | OK | OK | OK | OK | OK | OK | OK | OK |
| Run detenido (`gamma`) | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK |
| Run con commit (`alpha`) | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK | F→OK |
| Chat (`beta`) | OK | OK | OK | OK | OK | OK | OK | OK |
| Ajustes (`beta`, trabajo fijo) | OK | OK | OK | OK | OK | OK | OK | OK |
| Preferencias | OK | OK | OK | OK | OK | OK | OK | OK |
| No disponible (`epsilon`) | OK | OK | OK | OK | OK | OK | OK | OK |
| 404 | OK | OK | OK | OK | OK | OK | OK | OK |

Criterios por celda: textos en el idioma visual sin claves crudas ni marcadores (el único marcador detectado,
`{{INSTRUCTIONS}}…` en Ajustes, es texto legítimo de la plantilla de prompts); `lang`/título traducidos; cero
desbordes de página a 1440/500/390 px (las tablas anchas van en regiones `table-scroll` desplazables con `tabindex=0`
y `aria-label`); cero controles sin nombre; cero textos bajo AA; consola sin errores.

Transversales: puerta de sesión en en/es y ambos temas, con aviso de cierre traducido; foco visible (contorno sólido
2 px, cobalto en claro y azul claro en oscuro) y enlace «Saltar al contenido»; tras activar un botón que se deshabilita
durante la petición, el foco cae a `body` pero Tab continúa desde ese botón (punto de partida secuencial de Chrome);
diagnóstico del servicio en es «422 · root_not_absolute: La carpeta debe ser una ruta absoluta.» con contraste AA en
ambos temas. Los resaltados de navegación vistos en algunas capturas eran el hover del puntero (`aria-current` solo
marca la página activa).

## 6. Excepciones técnicas mantenidas (HITL) y observaciones

HITL: el usuario elige **mantener como códigos técnicos** los valores internos visibles y documentarlos:

- acción de cada job del run (`start`, `commit`, `phase_check`…), etapa del motor (`acceptance`, `committed`… en
  «Etapa», en «Bloqueo en acceptance: …» y en Estadísticas) y veredictos (`ACCEPT`, `READY`);
- campos de huella en Ajustes (`reviewer_cli_launch_sha256`…) y estados mostrados en `title`.

Por reglas ya decididas (T010 §Exceptions, T022): los motivos de parada/aceptación se muestran en el idioma de su
emisión (`gamma` se emitió con visual en: «Deterministic validation failed» también en es); el diagnóstico de
`epsilon` incluye el texto del sistema operativo («[Errno 2] No such file or directory») dentro de la frase traducida;
el contenido sintético del proyecto («Entregar el flujo sintético.», «Synthetic definition») va en su idioma de trabajo
o tal como se escribió. Nota para T017: README/README.es pueden citar esta QA de navegador (fuera de las rutas de T024).

## 7. Capturas saneadas

Ninguna muestra rutas del área temporal (llevan el usuario local), claves ni datos privados; las vistas con rutas se
revisaron sin guardarse. JPEG/PNG originales del navegador, sin retocar.

| Captura | SHA-256 |
|---|---|
| [before-es-light-run-duration-jobs](P011-T024_QA/before-es-light-run-duration-jobs.jpg) | `8e1cb36010b4ee9797e1c969653956519f83962dec62de1cf8b1e1b0f7e0e934` |
| [before-es-light-run-attempts](P011-T024_QA/before-es-light-run-attempts.jpg) | `685331d351e555813a0c8ac4076dcfee39896285a323b2c58e0bc58135040354` |
| [before-es-light-phase-closure-date](P011-T024_QA/before-es-light-phase-closure-date.jpg) | `61d48efef68dc3e98a3cb7acd716a86580e0a942af5f21b7e4e02dcb46c95768` |
| [after-en-light-desktop-run-duration-jobs](P011-T024_QA/after-en-light-desktop-run-duration-jobs.jpg) | `0d1b8f88487a5743d2f5c1ee389b4481cf343536e622dd1640522fa03703d4f6` |
| [after-en-light-desktop-run-attempts](P011-T024_QA/after-en-light-desktop-run-attempts.jpg) | `80042d99a835bd9038523c4735b648e5f7d96882acae8e99a0467ad8a8969d94` |
| [after-en-light-desktop-phase-closure-date](P011-T024_QA/after-en-light-desktop-phase-closure-date.jpg) | `3be8b805bba7cc359b0de5cf3402d4ded28beb598bf1f23ebe5758f8b42a9d47` |
| [after-es-light-desktop-run-duration-jobs](P011-T024_QA/after-es-light-desktop-run-duration-jobs.jpg) | `89dcf1100a97412e97163fb97b802511d81218fffc5fde7131bf15bafdcabedc` |
| [after-es-light-mobile-phase-closure-date](P011-T024_QA/after-es-light-mobile-phase-closure-date.jpg) | `cf96340df0ef25bd91a7800b057a81e26645268fa4edc9c976020817b9ad6a91` |
| [after-es-dark-mobile-run-attempts](P011-T024_QA/after-es-dark-mobile-run-attempts.jpg) | `6225f29ab5466452f8e6efe1bfdf3a74ea3323b50e3b107cc82236b26df865ee` |
| [after-es-dark-mobile-run-duration](P011-T024_QA/after-es-dark-mobile-run-duration.jpg) | `8e598753cee3f641f9429d1e16e11c84ae236e296b7a635fa3e0dcb0df1dbb02` |
| [en-light-desktop-preferences](P011-T024_QA/en-light-desktop-preferences.jpg) | `3675b8dbc6f9b32ee39b371db1b0d06a220af54bcae7a36d54cb2b27354fe935` |
| [en-dark-desktop-creation-drafts](P011-T024_QA/en-dark-desktop-creation-drafts.jpg) | `b9d92efea57c757d4f26f1f68afc9836de83b0d661a2052f2e61c1474460cc3c` |
| [en-dark-desktop-run-stopped](P011-T024_QA/en-dark-desktop-run-stopped.jpg) | `8c45193b20775ffc6d944f254b1cba2d302e54980680c8e010c26914481a0207` |
| [en-dark-mobile-task](P011-T024_QA/en-dark-mobile-task.jpg) | `f1a9b764af0318b37693dc15323a01c8952acde479f1ba7070c16e0c07f13ae5` |
| [en-light-mobile-onboarding](P011-T024_QA/en-light-mobile-onboarding.jpg) | `10054f88fdcf1581e5dcfd9290b1501c6cadb9de5be87728926b51b0197940e5` |
| [es-light-mobile-settings-work-language](P011-T024_QA/es-light-mobile-settings-work-language.jpg) | `66fedadd62463de67b16d60a38ad8d2197326f8a83b9c6f0e6b492874af3eace` |
| [es-dark-desktop-service-diagnostic](P011-T024_QA/es-dark-desktop-service-diagnostic.png) | `babb79413b0207eb6dfbc27bf606910ec1bed668caa01089200e0c5bf80fe597` |
| [es-light-desktop-sign-in](P011-T024_QA/es-light-desktop-sign-in.jpg) | `35fef861e0e775a72c6dfb0406928c553b61d8db803526b73d1c48f27cf3a6ae` |

## 8. Paquetes, checks y omisiones

| Paso | Resultado |
|---|---|
| Build del candidato de `98f7667` | Idéntico al de T016: wheel `537b32fd…9c99`, sdist `c4a21e38…7fd87`, `pylock.toml` `20a327c3…cf9` |
| `check_distribution.py` (candidato inicial y corregido) | Correctos ambos |
| Node / tipos / build del cliente tras corregir | 95/95 (93 + 2 nuevos) / `tsc` correcto / build correcto |
| Candidato corregido (árbol de esta tarea) | wheel `529e06476a636419d212334c94ee39566de1278e61dc91d294360b69ad5239de`, sdist `113e50d791001b267fc8c43642e50e1f4d1fb04032f43e56c6e65e7e33001d21`, `pylock.toml` sin cambios |
| Siembra con el candidato corregido | `alpha` CLOSED/`p001`, `beta` COMMITTED, `gamma` STOPPED; 8 barridos de 14 pantallas sin hallazgos |
| Al terminar | Ningún `harness-local serve` vivo; pestaña cerrada; scratchpad desechable |

No ejecutados: unittest/pytest/Alembic (no cambia Python, esquema ni API; `check_distribution` instala y recorre el
paquete), otros navegadores (Safari/Firefox), anchura real de 390 px en ventana (mínimo de Chrome 500 px; 390 emulado),
lectores de pantalla, CLI reales, proveedores, red y publicación. La instantánea pública de T015/T016 cambia en los 7
archivos de cliente/pruebas de esta tarea; T017 verifica el manifiesto y los hashes del candidato final.
