# P010-T009 — Verificación final del paquete

Fecha: 2026-10-22. Base a verificar: `d6a69c8`; producto sin cambios desde `dd7b958`.
**Estado: completada; dictamen favorable en el alcance declarado.** Decisión:
[D152](../DECISIONS.md#d152--p010-t009-paquete-final-verificado-y-dictamen-favorable).
Alcance real decidido en D151: A/B y perfil Django declarado aplazados, con sus límites. No se cierra P010 en T009.

## 1. Alcance revisable de la comprobación

- Checks offline de AGENTS: pytest completo (incluido el caso intermitente de T007), unittest, Node, tipos/build
  y Alembic sobre SQLite nueva temporal. Las dos variantes opt-in Django/TypeScript conservan su omisión salvo
  autorización específica; no se consultan ni migran bases existentes.
- Área nueva privada: `/private/tmp/harness-p010-t009-pe8g8zj7`, fuera de checkouts. Logs, dist, venvs, SQLite,
  proyectos y respuestas sintéticos solo en esa área o temporales hijos. Caches existentes de desarrollo
  `.local/uv-cache` y `.local/npm-cache`; sin descargas ni cambios de configuración global.
- Construcción: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/build_distribution.py
  --out-dir /private/tmp/harness-p010-t009-pe8g8zj7/dist`. Ejecuta `npm ci --offline --ignore-scripts` desde el lock,
  tipos/build, `uv build --offline --no-python-downloads` y export de requirements. Solo reinstala node_modules
  del frontend y genera assets ignorados; no ejecuta el harness sobre este repositorio.
- Verificación: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/check_distribution.py
  --dist /private/tmp/harness-p010-t009-pe8g8zj7/dist`. Se ha leído el script completo: instala el wheel y sus pins
  offline por hashes en un venv nuevo; verifica UI/assets, sesión, migración `0022`→`0023` con instantánea,
  definición D088/tarea/commit/reinicio idempotentes con puertos de agentes falsos, backup y restauración de consulta.
  Solo crea commits en fixtures sintéticos y levanta servicios en puertos efímeros de loopback.
- QA visual: servir los assets del mismo wheel en loopback con API sintética, sin supervisor ni proveedores.
  Chrome en una pestaña nueva para preparación TypeScript (T002), definición sin borradores/con borradores (T004), fase abierta/cerrada/con
  sucesora/deriva real y documentos (T005), paginación de ciclos/diff/JUnit de un run (T003) y métricas (T011).
  Respuestas basadas en los contratos y fixtures existentes; la QA de presentación no acredita una integración
  adicional con el backend. Capturas saneadas e informe en `docs/phase/`; scripts auxiliares solo en el área temporal.
- Medidas de lecturas acotadas: contrastar evidencia T003/T011 y reejecutar sus pruebas de historiales grandes
  como parte de pytest; no usar historiales operativos.
- Parada ante falta de caché/dependencia, fallo de instalación/servicio o hallazgo de producto; conservar evidencia,
  detener procesos propios y acotar una corrección separada antes del dictamen. Sin instalación global, servicios
  persistentes, red externa, CLI reales, proveedores, operación de P009/ReferenceProject, push, publicación o cierre T010.
  Al terminar se detienen todos los servicios y se cierra la pestaña propia. El área se conserva para revisión;
  no se elimina material operativo ajeno. Ninguna dependencia ausente dispara descarga implícita.

## 2. Autoridad y resultados

Preparación realizada: checkout limpio al comenzar; instrucciones, decisiones D144–D151, entregas y verificador
leídos; macOS 26.4.1 arm64, Python 3.14.4 y Node 24.15.0/npm 11.12.1/uv 0.12.19 comprobados. Área privada creada.

El contrato T009 exige concretar y autorizar instalaciones/servicios/smokes antes de ejecutarlos. Tras presentar §1,
el usuario responde **«Autorizo.»** en el bucle HITL: construcción offline, verificador del wheel instalado con
puertos falsos y servicios temporales de loopback, y QA visual con API sintética. D151 sigue vigente; esta
autorización no incluye proveedores reales ni la instalación operativa.

Checks ordinarios ejecutados sobre `d6a69c8`, sin cambios de producto:

| Comprobación | Resultado |
|---|---|
| `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q` | 1682 passed, 2 skipped, 121 subtests passed; 123,49 s; 10 avisos de deprecación FastAPI/Starlette/httpx |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 12 OK |
| `node --test frontend/tests/*.test.mjs` | 82 pasan |
| `npm --prefix frontend run check` | correcto |
| Alembic `upgrade head` y `check` mediante `_config` sobre SQLite temporal nueva | sin operaciones nuevas |
| `scripts/build_distribution.py --out-dir …/dist` con uv/npm offline | correcto; instala 175 paquetes desde el lock/caché, comprueba tipos y construye UI, sdist y wheel |
| `scripts/check_distribution.py --dist …/dist` con uv offline | correcto; venv nuevo, 18 dependencias por hashes y wheel sin dependencias implícitas |

Las dos omisiones son las variantes opt-in de Django y TypeScript con sus caches/entornos reales; se mantienen
como en T012, sin activar variables de opt-in ni leer el área de P009. El caso intermitente de `test_commands.py`
observado en T007 pasa dentro de la suite completa; no se repite sin nueva incertidumbre. También pasan las pruebas
de lecturas acotadas de T003/T011: equivalencia con la lectura anterior y cero consultas a `history_json` o llamadas
al codec en vistas, incluidas las de historiales grandes. No se repiten mediciones de tiempos bajo otra carga:
las medidas históricas siguen identificadas en sus entregas.

Logs locales en `logs/` del área de §1; hashes y resultados en la
[evidencia saneada](P010-T009_EVIDENCE.json). El build solo emite el aviso conocido de chunk mayor de 500 kB.
No se ejecuta `npm audit` ni se consulta la red: los avisos KaTeX conocidos conservan su condición de límite.

## 3. Paquete final instalado fuera del checkout

| Artefacto | Bytes | SHA-256 |
|---|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | 1.650.938 | `94a6699e7c2e36cc42bcf45e1e2feb4d2028aa722756b47cb862087919792b17` |
| `harness_local-0.1.0.tar.gz` | 1.512.596 | `5dd0c72e897f4e43c02bf34ed4d17e2574b417e86e4e21173df3a6649ba211f2` |
| `requirements.txt` | 11.324 | `4587b997650b377d167ff9cad68708cfaffb9e080294867a2541188c044bf873` |

El verificador contrasta por bytes todo `src/harness_local` y los assets con el wheel; comprueba que el módulo
cargado procede del venv instalado, con cwd externo y sin Node ni proveedor en PATH. Instalación offline por hashes,
sin modificar el venv operativo. Se acreditan:

- `init-db` solo crea; `serve` rechaza base ausente/vacía/incompatible; sesión, CSRF y assets protegidos operan.
- CLI instalada `migrate`: base sintética `0022`→`0023`, declaración de parada obligatoria, copia `premigration-1`
  con hash/integridad/revisión comprobados, repetición `current` sin alterar bytes ni duplicar copia y base ausente
  rechazada sin crearla. T012 ya cubre historiales 1–8 y negativas; el wheel confirma su entrada instalada.
- Definición D088 con propuestas confirmadas, commit raíz y P001; tarea con contenido exacto hasta COMMITTED;
  repetición de confirmaciones y reinicio sin duplicar commits ni invocar otra vez el adaptador falso.
- Backup verificado y restauración solo de consulta con el checkout original retirado: historial, commit,
  intentos y eventos legibles; escrituras rechazadas y supervisor deshabilitado.

Solo el fixture explícito se copia al área temporal: nunca se carga producto desde el checkout. Las invocaciones
son funciones falsas, sin ejecutar CLI reales ni acceder a credenciales. No se migra la instalación de P009.

## 4. QA visual del mismo wheel

Chrome, viewport de escritorio por defecto, una pestaña temporal. Se extraen y contrastan **102 assets** del wheel;
la API de presentación sirve instantáneas sintéticas, sin supervisor. Fases/documentos y run/métricas proceden de
fixtures existentes y las vistas reales sobre SQLite nueva; definición y preparación usan sus contratos tipados,
el manifiesto y los pasos empaquetados. Los ajustes iniciales de campos requeridos (`tag_kind`, scope de métricas)
son del generador local de respuestas, antes de la QA, sin cambios de producto. Scripts auxiliares y respuestas
completas se conservan solo en el área temporal.

| Caso | Resultado observado | Captura |
|---|---|---|
| T002: preparación TypeScript | Nombre de receta, manifiesto/lock, comandos offline, tareas bloqueadas y confirmación deshabilitada hasta consentir. Solo se pide una vista previa ficticia; no se confirma ni instala | [preparación](P010-T009_QA/typescript-preparation.jpg) |
| T004: definición sin borradores | Ayuda de carpeta nueva y marcadores opcionales visible | [carpeta nueva](P010-T009_QA/definition-empty.jpg) |
| T004: editor con parejas de marcadores | Ayuda de conservar la pareja o retirarla entera; edición de prueba descartada, sin escritura | [editor](P010-T009_QA/definition-draft.jpg) |
| T005: fase abierta | Deriva frente a base visible y cierre deshabilitado sin READY; no se ejecutan acciones | [abierta](P010-T009_QA/phase-open.jpg) |
| T005: cerrada sin sucesora | Archivo íntegro, renovación esperada, documentos vivos coincidentes y READY histórico; sin adoptar/cerrar de nuevo | [cerrada](P010-T009_QA/phase-closed.jpg) |
| T005: cerrada con sucesora | P002 es dueña de documentos vivos; exportación desde P001 deshabilitada | [sucesora](P010-T009_QA/phase-successor.jpg) |
| T005: deriva real | NEXT_STEPS cambiado y SUMMARY de archivo alterado señalados; CLOSED y READY histórico conservados | [deriva](P010-T009_QA/phase-drift.jpg) |
| T005: documentación | Sin deriva falsa tras cerrar; cambio externo confirmado en Git remite al cierre histórico | [al día](P010-T009_QA/docs-closed.jpg), [deriva real](P010-T009_QA/docs-drift.jpg) |
| T003: ciclos, diff y JUnit | Ciclos 0–9 y 10; diff UTF-8 de 111.000 bytes leído con offsets 0/65.527 hasta «Completo»; JUnit 50/50/1, casos 0/50/100 y último Siguiente deshabilitado | [diff](P010-T009_QA/run-diff.jpg), [JUnit y segunda página de ciclos](P010-T009_QA/run-junit.jpg) |
| T011: métricas | Uso ausente como «sin dato», tarea y validaciones visibles; sin errores de renderizado observados | [métricas](P010-T009_QA/metrics.jpg) |

Los avisos «aviso» y el comando rechazado `rm -rf x` que aparecen en JUnit son texto del fixture de
`test_run_projection.synthetic`: no se ejecuta ese comando y el resultado sintético dice `outside policy`.
No se observan solapamientos o cortes que impidan leer/usar las pantallas revisadas. La QA es de presentación:
no certifica integración navegador/backend, otros navegadores, temas o breakpoints; la integración backend del
wheel se acredita separadamente en §3. No se repite la QA de la aplicación Django hija.

## 5. Dictamen, límites y parada

[Revisión de salida](P010_REVIEW.md): **siete criterios de ROADMAP cumplidos en el alcance declarado**, con
evidencia trazable y matriz de trece criterios globales conservada. Sin hallazgos de producto que exijan una tarea
correctiva previa. T009 termina y T010 queda como siguiente tarea; la fase y la primera versión no se declaran
cerradas todavía.

La autorización de T009 se agota con estas comprobaciones: cero proveedores reales, sin A/B real ni D095 real,
sin alterar configuración global, operar P009/ReferenceProject, push, publicación, tag o cambio de versión. D151 y los
límites de ARCHITECTURE §10 siguen vigentes. Las dos variantes opt-in reales siguen omitidas.

Pestaña propia cerrada y servicio de presentación detenido (puerto 50225 sin listener). El verificador termina sus
servicios y limpia su entorno temporal. Las doce SQLite sintéticas conservadas en el área, incluidas las de
preparación de fixtures, tienen cero jobs QUEUED/ACTIVE/RECOVERY_REQUIRED y cero checkout locks. No se borra el
área, el wheel ni los logs; se conservan para revisión local.

## 6. Comprobación documental

| Comprobación | Resultado |
|---|---|
| Parsers puros de ROADMAP, NEXT_STEPS y DECISIONS | 10 fases, 7 criterios de P010, 12 tareas y 152 decisiones |
| Enlaces/anclas de los siete Markdown tocados | 456 comprobados, sin rotos |
| Presupuestos | STATE 12.098/24.576 bytes; base 5.801/12.288; NEXT_STEPS 24.558/49.152 |
| Evidencia y capturas | JSON válido; doce JPEG originales del navegador, dimensiones y SHA-256 contrastados |
| Conservación respecto a `d6a69c8` | Cuerpos D001–D151, ROADMAP P001–P009, dictamen original de la matriz y archivos cerrados intactos |
| Diff y `git diff --check` | Revisados, sin errores; solo documentación y artefactos saneados |

No se repiten suites después de escribir los informes: no cambian código, esquema, API, flujos ni assets. El wheel
verificado conserva los mismos bytes de producto; el futuro commit de T009 solo registra esta evidencia documental.
