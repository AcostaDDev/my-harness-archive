# P013 — Revisión de salida

Fecha: **2026-10-27**. Tarea: [T014](../NEXT_STEPS.md#p013-t014--revisión-de-salida-y-expediente-de-apertura-actualizado).
Base revisada: **`a0cab9e51f6440b827825d5491313f0542e4197e`**, entrega T013, checkout inicialmente limpio.
Decisión: [D231](../DECISIONS.md#d231--p013-t014-dictamen-favorable-y-expediente-de-apertura-actualizado).

**Dictamen favorable en el alcance declarado.** Los ocho criterios de ROADMAP tienen evidencia trazable y
no quedan correcciones obligatorias pendientes para el cierre manual. Habilita **T015**, todavía pendiente.
El cierre documental antes de publicar sigue siendo una puerta obligatoria, no una acción realizada por esta revisión.
El [expediente nuevo](P013_EXPEDIENTE_APERTURA.md) sustituye operativamente P012/D214 para una futura apertura,
sin modificar sus originales ni sustituir físicamente sus árboles. No autoriza acciones remotas.

## 1. Base y método

Se contrastan contrato T001/D216–D218, entregas T002–T013, matriz, especificación/arquitectura, paridad documental
de datos/flujo y candidato/paquete exactos. Se inspeccionan las puertas de autoridad/activación/consulta y sus
pruebas, sin presentar esta revisión como una nueva auditoría integral del código o de seguridad.

La fuente exportada sigue siendo `984c287ab9f21ba7976fc7cdb5df86b4f235b118`. Se comprueban lista positiva,
correspondencia privada, fuentes públicas actuales, nombres/directorios/modos/hashes de los candidatos y
miembros/metadatos/checksums del paquete. Los resultados de suites e instalación pertenecen a T013; la integración
guiada y QA visual, a sus paquetes de ensayo de T012. No se repiten suites, builds, servicios ni proveedores.

## 2. Dictamen por criterio de ROADMAP

| Nº | Criterio | Evidencia y alcance | Dictamen |
|---|---|---|---|
| 1 | Contrato previo de configuración, autoridad, activación, compatibilidad y recuperación | [T001](P013-T001_CONTRATO.md), D216–D218; [T004](P013-T004_CONFIGURACION.md). Diseño anterior a las implementaciones; bytes TOML inmutables y referencias SQLite, CAS/intenciones, reinicio global y activación entre tareas. | **Cumple.** T001 fue diseño; la implementación se acredita en T002–T011, sin reescribir la entrega original como si ya la contuviese. |
| 2 | Instalación/arranque, venv/rutas/cachés, red/offline, aislamiento y desarrollo separado | [T002](P013-T002_INSTALACION.md), [T003](P013-T003_ARRANQUE.md), [T012](P013-T012_PRIMER_USO.md#instalación-y-repetición), [T013](P013-T013_CANDIDATO.md#validación-del-candidato-exacto). Clon y caché inicialmente vacía con red de dependencias autorizada en T012; paquete/replay/arranque sin Node en T013. | **Cumple en macOS ARM64.** Offline por defecto, actualización y rutas con espacios acreditadas; caché incompleta y generaciones fallidas conservadas. No acredita otras plataformas ni una nueva primera instalación con red del paquete T013. |
| 3 | Setup autenticado sin TOML/modelos, ajustes globales, formularios/TOML/diff/confirmación | [T005](P013-T005_ASISTENTE_API.md), [T006](P013-T006_ASISTENTE_UI.md), [QA T012](P013-T012_PRIMER_USO.md#qa-visual); dos arranques UNCONFIGURED/UI 200/supervisor deshabilitado en [T013](P013-T013_RESULTS.json). | **Cumple.** Guardar/activar/reiniciar separados; sesión/Host/Origin/CSRF y no consumo sin autoridad. Preflight falso no equivale a inferencia ni a autenticación real. |
| 4 | Crear/incorporar desde contexto sin stack obligatorio, recetas opcionales | [T007](P013-T007_PROPUESTA_PERFIL.md), [T009](P013-T009_ALTA_UI.md), [altas T012](P013-T012_PRIMER_USO.md#altas-y-tareas). Documentos/arquitectura e inventario HEAD preceden propuesta/commit documental/P001. | **Cumple sintético.** Ambas entradas con perfil Go propio y original B conservado. Recorrido por HTTP protegido; formularios inspeccionados aparte en Chrome. No prueba un compilador Go ni la calidad de propuestas reales. |
| 5 | Preparación acotada, validaciones/evidencia/activación antes de tareas, agentes sin escritura global | [T008](P013-T008_PREPARACION.md), [T009](P013-T009_ALTA_UI.md), [resultados T012](P013-T012_RESULTS.json). Plan/HEAD/herramientas/documentos sellados, journal/lock/lease antes de GO, argv/JUnit/recibo exactos; intento prematuro 409 y ambas tareas COMMITTED con agentes falsos. | **Cumple en contención cooperativa.** Preparar no activa, propuesta no es entorno listo; no acredita sandbox del SO, red/instalación de Go real o nueva autorización de proveedores. |
| 6 | Edición posterior manual/asistida, impacto/recuperación y contratos congelados | [T010](P013-T010_EDICION_ASISTIDA.md), [T011](P013-T011_COMPATIBILIDAD.md), edición instalada T012. `test_configuration_editing.py`: pareja activa frente a candidata, impacto global, recibos, jobs congelados, cancelación/replay y transportes falsos. | **Cumple sintético.** Asistencia cambia borrador, no autoridad; cambio técnico exige documentos/plan/preparación nuevos. Formulario/TOML instalado comprobado; no se repite toda la asistencia o matriz de caídas en navegador. |
| 7 | Compatibilidad/backup/consulta, fallos, ambas altas, stack distinto e idiomas/QA | [T011](P013-T011_COMPATIBILIDAD.md), [backup/consulta T012](P013-T012_PRIMER_USO.md#backup-y-consulta), [capturas](P013-T012_QA/es-light-desktop-restored-run.jpg). Ocho formatos/hashes, preparación nueva de perfiles convertidos por HITL D228, backup 2/v1 compatible, consulta sin originales y mutaciones bloqueadas. | **Cumple en el alcance muestreado.** Chrome, en/es, claro/oscuro y tamaños/Tab/Enter documentados. No certifica accesibilidad completa, otros navegadores ni muerte de escritores por poder consultar una copia. |
| 8 | Guías públicas, candidato/paquete nuevos, manifiesto/checks, revisión/expediente, originales y cierre antes de publicar | README en/es, baseline pública T012; [T013](P013-T013_CANDIDATO.md), esta revisión y [expediente](P013_EXPEDIENTE_APERTURA.md); [contraste estático](P013-T014_COMPROBACION.json). | **Cumple para dictaminar y pasar a T015.** Árbol/paquete y evidencia propios, originales intactos, expediente preparado. El archivo/cierre de T015 sigue pendiente y bloquea la apertura; no se declara P013 cerrada. |

## 3. Hallazgos e incidencias conservadas

| Observación | Tratamiento | Límite que permanece |
|---|---|---|
| Resúmenes vigentes de SPECIFICATION/ARCHITECTURE aún anunciaban T011/T013 pendientes y dos referencias de esquema se detenían en 0026 | Se actualizan frases de estado/enlaces y etiquetas hasta 0027_profile_proposals, coincidentes con migraciones/diagrama y baseline pública existentes; las secciones detalladas ya describían las entregas. | Corrección editorial, sin cambio de diseño, código, datos/flujo o baseline pública. Originales T001–T013 intactos. |
| Fallos instalados T012: pin uv absoluto, configuración npm duplicada, .gitignore extra, checker desactualizado y TIME_WAIT | Correcciones/regresiones y nuevas generaciones constan en [T012](P013-T012_PRIMER_USO.md#correcciones-acotadas); suite del candidato T013 contiene las correcciones. | Fallos/instalaciones anteriores no se califican retrospectivamente READY. No se repite instalación ni se amplía soporte de herramientas. |
| Alternancia de alta con claves React duplicadas y probe falso incompleto | Correcciones acotadas, regresión y nueva QA de T012; fixtures posteriores alcanzan ambas tareas COMMITTED. | Preparación FAILED y runs STOPPED conservados. El éxito de Go falso solo acredita orquestación. |
| Exportación T013 rechazada por logs/reports/home/temp y Node antes de dependencias | Adaptador privado exige límite de ruta absoluta; build offline antes de Node. [Logs iniciales](P013-T013_LOGS/export-initial-rejected.log) y [fallo Node](P013-T013_LOGS/node-initial-missing-dependencies.log) conservados. | Sin cambiar plantillas/exportador archivado ni repetir backend válido. Las suites correctas posteriores se identifican por su ejecución propia. |
| Release antigua describía un conjunto previo a distribution-1 | Expediente nuevo exige conservar los 13 archivos del paquete, incluido scripts/, manifiesto y checksums; entrega concreta de assets se revisará antes de la autorización de Release. | No se crea ahora otro formato/paquete de transporte ni se presenta wheel/sdist solos como instalador autocontenido. Release opcional pendiente. |

No quedan hallazgos obligatorios de producto, privacidad o paridad pendientes dentro de esta tarea.
La conversión/importación de configuración y la incorporación B de código siguen siendo carriles diferentes;
la preparación nueva antes de activar el conjunto convertido ya fue resuelta por HITL D228, no queda ambigua.

## 4. Identidad, comprobaciones y omisiones

Árbol `my_harness_dist_p013`: **445 archivos / 6.389.580 bytes**, manifiesto
`ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428`.
Wheel T013 `2416672d…47076`; identidades completas y rutas en [expediente §1](P013_EXPEDIENTE_APERTURA.md#1-candidato-y-paquete-revisados).
La comparación con D214 conserva 325 archivos, añade 44 y modifica 76; sin eliminados ni cambios de modos.

Se mantienen, sin repetir, **2048 pytest/29 subtests**, **8 unittest**, **155 Node**, dos opt-in omitidas;
tipos/build, Alembic temporal y verificación instalada correctos. Los logs T013 respaldan esas cifras.
T012 aporta ambas altas Go, edición, backup/restauración y once capturas; T013 aporta la cualificación del árbol
exacto y su paquete. No se atribuye a T013 una nueva QA visual o el recorrido v9 completo de T012.

Nuevos checks de T014, exclusivamente lectura:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -B docs/phase/P013-T014_CHECK.py
git diff --check
```

[Resultado](P013-T014_COMPROBACION.json): manifiesto/correspondencia reproducidos desde la fuente exacta;
fuentes públicas actuales idénticas; candidatos/modos/directorios, 13 archivos del paquete y miembros/metadatos
verificados. Ocho inventarios protegidos de T013 y originales phase/archive preservados, cuerpos D001–D230
intactos; parsers, ocho criterios, quince tareas, enlaces/anclas y presupuestos correctos. Diff revisado.

T014 no cambia producto, API, modelos/migraciones, flujos, dependencias, README ni docs/public; no requiere
repetir suites válidas. No ejecuta servicios, fixtures, instalación, build, navegador, CLI/proveedores reales,
smokes ni acciones remotas. Solo lectura de documentación oficial de GitHub para contrastar el procedimiento.

La evidencia real acumulada de P012 conserva sus wheels/pareja/consumos y límites históricos; P013 no consume
proveedores ni transfiere consentimientos. macOS ARM64/Chrome, contención cooperativa, validaciones sin hora,
manifiestos de receta fijos y avisos low de KaTeX conservados. Sin producción, creación Django v2 real, otras
parejas actuales/plataformas, evaluación comparativa de modelos, auditoría completa de accesibilidad o CI remota.

**Siguiente: T015, cierre documental manual.** Solo después se podrá concretar y autorizar la apertura sobre
este candidato; owner/repo, identidad pública, visibilidad, push/CI, reporte privado y Release siguen pendientes.
