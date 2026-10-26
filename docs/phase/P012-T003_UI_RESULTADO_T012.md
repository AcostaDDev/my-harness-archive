# P012-T003 — Consulta UI restaurada verificada tras T012

Fecha: **2026-10-26**. **Estado: T003 completada con evidencia acumulada y salvedad de identidad autorizada.**
Base operativa del build: **`92e800d07b11f63b9d9a2fc9c57ad1d46f55e586`**, solo documentación posterior a
**`f94842980235d1801e6a99505bffd329f63e1f85`**, producto T012 sin cambios y 24 hashes de código correctos.
[Guion original](P012-T012_VISTA_CONSULTA.md#4-propuesta-de-continuación-t003-solo-ui-sin-autorizar),
[parada anterior conservada](P012-T003_UI_T012.md), [evidencia inicial T003 conservada](P012-T003_CHAT_BACKUP_REAL.md).
Decisión: [D204](../DECISIONS.md#d204--p012-t003-consulta-ui-restaurada-verificada-con-salvedad-autorizada).

## 1. Consentimiento y guardias

Tras el commit **92e800d** y la pregunta específica, el usuario responde **«Autorizo»** a continuar solamente
la copia de consulta conservando `unknown` para la identidad histórica del host. Sin cambiar código, SQLite,
identidades o guardias. Se mantiene el límite original desde aproximadamente **07:23 UTC**, una hora y cero
llamadas de modelos. No se repone saldo ni se autoriza T004 o el arranque de la base operativa.

Reanudación **07:30:16 UTC**: checkout limpio, sin diferencias de producto frente a f948429, manifiesto T012
correcto y destinos nuevos. Cinco hashes de bases/manifiestos coinciden con el guion, integridad/FK/esquema
0025 correctos y **16.798 filas iguales por todas sus columnas** en fuente, bundle y restauración. Ambas copias
conservan 0x483532 y `execution_authorized=false`; WAL existentes vacíos, lecturas sin `immutable=1`.
Fixtures B/B2/clon, configuraciones/distribuciones/diffs, ocho herramientas y 42 artefactos intactos.

Estado conservado: **13 DONE/1 QUEUED/14 STOPPED/0 locks**. P001-T002/job 14 sigue sin owner, intentos,
preparaciones o ciclos. Las 39 referencias de identidad comprobadas, incluidas las de los 14 procesos,
devuelven `unknown`; sus grupos locales están ausentes. La excepción autoriza consulta, **no certifica la
muerte de escritores históricos** ni convierte `unknown` en `dead`.

## 2. Distribución e instalación offline

Se ejecutan los cinco comandos del guion: build, verificador, venv con Python **3.14.4**, sync desde pylock e
instalación del wheel sin dependencias adicionales; todos **exit 0**, sin descargas. Destinos nuevos
`dist-t012/` y `venv-t012/`; distribuciones/venv anteriores conservados. El verificador contrasta miembros,
metadatos, licencias, fuentes y checksums, y completa su recorrido aislado con CLI falsas: sesión, UI/API,
definición D088, tarea/commit/reinicio, errores y restauración sintéticos. No se confunde con los runs reales.

| Artefacto nuevo | SHA-256 |
|---|---|
| Wheel 0.1.0 | `730891f8de5b68b9279e6d8a96a7066a3dd3e1ba9c5b64c5336e2f4814f41520` |
| sdist 0.1.0 | `e3fce96e4fffce3ac3250da3863e9bcfe88cf6edd9b4f35853ae78052d52bfed` |
| pylock.toml | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |
| SHA256SUMS | `c5d0194a052f8f9d92c2cd8674238c5513a9f9e6aa932811b7fa81a09bcb43be` |

Los **259 archivos instalados del paquete** coinciden por bytes con el wheel. Build Vite correcto, con aviso
existente de chunks mayores de 500 kB. No se ejecuta preflight de CLI, modelos, validadores/formateador del
fixture, inicialización o migración de bases reales.

## 3. Consulta UI y alcance observado

Único servicio real desde AREA: `venv-t012/bin/harness-local serve --database AREA/restored/t003/state.sqlite3
--port 8025`, sin configuración de agentes o configuración ambiental heredada, HOME/TMPDIR/PATH explícitos.
No se arranca 8024. Supervisor: **read_only_archive=true**, enabled/alive/ports_configured/
commit_writer_configured **false**. La UI muestra permanentemente el contexto de copia y la advertencia de
que consultar no reanuda trabajo ni certifica parada de escritores. Idioma actual **es**, sin cambiar preferencias.

Chrome requiere recuperar la vinculación de ventana/pestaña tras el uso concurrente y dos timeouts del control
nativo. Se crea una pestaña dedicada vacía y se introduce la URL por la barra nativa; se vuelve a vincular la
página cargada. El autocompletado de Bitwarden bloquea temporalmente la automatización DOM: se descarta con
Escape y se usan controles nativos cuando procede. Sin rechazo de origen/auth del producto, reconfiguración
de seguridad, guardado de credenciales o fallback de API como sustituto del QA UI.

| Observación UI | Resultado |
|---|---|
| URL directa y entrada desde inicio por id | Run `e3fa4ae6…` visible; recarga conserva la consulta independiente |
| Detalle y commit | COMMITTED/«Commit hecho», commit **6f021211b307**, revisión 0 ACCEPT |
| Diff bajo demanda | Tres rutas, completo; hash mostrado `db6fa9b245b8…`, contenido de vista/tests/flujo visible |
| Validaciones y JUnit | Seis comandos exit 0; **13 casos**, individuales visibles con éxito observado y duraciones |
| XML original | Enlace conservado y hash completo en UI; bytes contrastados puntualmente por HTTP |
| Métricas por run | Tres intentos: selección/modelo reportado, tokens, turnos, duración y equivalente API con procedencia; ausencia de coste Codex distinta de cero |
| Primer REVISION_LIMIT `b94eedef…` | Sin commit, revisión REVISE, pytest exit 5/JUnit parcial con cero casos; resultados conservados |
| Segundo REVISION_LIMIT `f98b16d9…` | Sin commit, REVISE, 13 casos previos y fallos Ruff check/formato conservados |
| QUEUED `d235e9d5…` | P001-T002/job 14 En cola, sin intentos o métricas; sin controles de ejecución/recuperación |
| Ruta operativa directa de proyecto/fase/tarea/run | «Esta página no está disponible en una copia de consulta», vuelta al archivo; sin workspace |

Las lecturas HTTP nuevas se limitan a la señal de supervisor y al contraste puntual de hash del diff y bytes
del original enlazado desde la UI, con sesión local efímera. No se repite la matriz HTTP anterior o la prueba
de mutación 409; esa evidencia conserva su procedencia D200. Diff SHA-256
**`db6fa9b245b8d7d9f9c10c534bf611ccbc526434673e35f46030e73ed892b3c0`** y original JUnit
**`7e51116eeec2b61fac2b2f4281a63852934a5b63bb1223e15e27a34a68ad4e63`** (**1.660 bytes**) coinciden con T003.
El XML se guarda en `tmp/t003-ui-t012-downloads/`; no se atribuye una descarga de navegador a ese contraste HTTP.

Capturas y accesibilidad privadas de detalle/commit, diff/casos, métricas, ambos fallos, cola y ruta bloqueada
en `state/operator/t003-ui-t012-*`. Una captura intermedia de navegación todavía en inicio se conserva aparte;
el segundo REVISION_LIMIT se acredita con los archivos `revision-b2-verified`, no con esa captura intermedia.
No se exportan claves, SQLite, prompts completos o streams al repositorio.

## 4. Parada y conservación

Servicio detenido normalmente a las **07:42:13 UTC**; puerto 8025 cerrado y clave retirada. Puerto 8024 sigue
cerrado. Comprobación final **07:43:02 UTC**, unos **20 minutos** desde la preparación original, incluida la
interrupción HITL. Cero llamadas nuevas Claude/Codex; acumulado T003 **2/3 Claude y 0/0 Codex** de D200.

- Los **cinco hashes** de base operativa, manifiestos y SQLite de backup/restauración permanecen idénticos
  a los del guion original; COMPLETE y autorización de ejecución false conservados.
- **16.798 filas** iguales por todas sus columnas entre fuente/bundle/restauración, integridad/FK/revisión
  correctas. Cero filas operativas nuevas; 13 DONE/1 QUEUED/14 STOPPED/0 locks.
- Tarea pendiente con cero intentos/preparaciones/ciclos, job sin propietario, checkout sin ejecución nueva.
  Tres fixtures conservan HEAD, archivos/modos y sus diffs exactos; 42 artefactos, ocho herramientas y los
  **254 archivos privados previos inventariados** conservan hashes y modos.
- Las 39 referencias históricas siguen `unknown` y todos sus grupos locales ausentes. El proceso nuevo de
  consulta se detiene por su identidad viva comprobada, sin señalizar identidades persistidas.
- Log del servicio sin respuestas de error salvo las comprobaciones normales de sesión; únicas peticiones
  HTTP mutantes: login local. Sin acciones de producto, nuevas tareas, commits/tags de hijos o cambios globales.

Evidencia privada: `before.json`, logs de build/verificador/instalación/servicio, `package.json`,
`narrow-hashes.json`, capturas/AX, `stop.json` y `final.json`, todos bajo el prefijo anterior y sin sobrescribir
los informes de la parada o de los tramos anteriores. `qa.json` contrasta los textos observados y fija hashes
de 12 archivos de evidencia UI verificada; la pestaña temporal del navegador queda cerrada.

## 5. Dictamen y omisiones

**T003 cumple sus tres criterios con evidencia acumulada**: chat/comando/confirmación sin ejecución y
backup/restauración/API proceden de D200; consulta UI independiente, conservación y parada de este tramo
completan el criterio pendiente tras T012. La salvedad de identidad histórica queda explícita y autorizada.
No es una nueva ejecución de tarea ni certificación de muerte de escritores. P001 del clon sigue ACTIVE.

Sin cambio de producto/API/modelos/migraciones/flujo o baseline pública: no se repiten pytest/unittest,
Node/tipos, Alembic o validaciones de fixtures ya acreditadas. Se ejecutan build Vite, distribución/recorrido
sintético del wheel, contraste de instalación, QA real de Chrome y conservación de datos, además de checks
documentales y revisión del diff. Otras plataformas/navegadores, idioma visual en, logs originales, paginación
adicional y la tarea TypeScript de T004 no se prueban aquí.

Checks documentales correctos: **12 fases, 7 criterios P012, 12 tareas y 204 decisiones**, **665 enlaces/anclas**
relativos válidos en los seis Markdown de la entrega. Presupuestos STATE/base/NEXT_STEPS:
**18.679/24.576**, **9.171/12.288**, **35.245/49.152 bytes**. Cuerpos D001–D203 e informes congelados,
producto, archivo histórico y baseline pública intactos; diff revisado y `git diff --check` correcto.

**Siguiente:** preparar la propuesta de arranque T004 respetando D199 y el job QUEUED; autorización separada
antes de efectos. P012 sigue abierta, sin cierre del hijo, tags en este repositorio, push o publicación.
Los informes anteriores y D001–D203 se conservan por bytes; este resultado se añade con su propia procedencia.
