# P013-T011 — Compatibilidad, recuperación y backup de configuración

Entrega manual de 2026-10-26. Base: `e393944`.
[D228](../DECISIONS.md#d228--p013-t011-conversión-explícita-y-backup-de-configuración),
[contrato T001](P013-T001_CONTRATO.md), [flujo](../flows/configuration-setup.md#compatibilidad-y-backup-entregados-en-t011).

## Alcance y HITL

T011 trata la conversión de **configuración de my_harness**, distinta de la incorporación B de código existente.
El usuario aclaró esa distinción y confirmó expresamente «Sí, validar/preparar antes de activar»: los perfiles
convertidos no adquieren autoridad por disponer de código, documentos o recibos anteriores. Se conserva la
configuración antigua hasta preparar, confirmar el conjunto y reiniciar seleccionando el almacén gestionado.
La incorporación B conserva su conversación/inventario y commits documentales; no se ha sustituido por este carril.

## Implementación

- `configuration_import.py`: preview protegida sobre el TOML externo seleccionado, usando el loader original,
  sin procesos, escritura, chmod ni descubrimiento. Convierte global a v9 y copia perfiles/herramientas/argv/
  autorizaciones/entorno/política/agentes efectivos a proyectos v1 **DRAFT**, con procedencia por hash.
  Los presets elegidos se materializan en contenido propio. V1 explicita la selección del revisor de la primera
  fila en el candidato global visible; cada perfil conserva su selección efectiva. Sus selecciones anteriores
  de planificación siguen en los snapshots legacy, sin atribuirles identidad v9.
- Guardar confirma el hash de la preview completa y reutiliza SAVE/CAS/lock/publicación/fsync/recuperación.
  El journal sella `legacy_import`: fuente/hash/formato, versiones legacy, filas TOML y snapshot del registro.
  Conflictos de id/raíz, registros retirados o techos de permisos sin resolver rechazan la conversión, sin
  preferencia silenciosa. Los proyectos TOML sin registro reciben fila y evento en la finalización del mismo
  guardado; el runtime legacy no los carga por segunda vez. Filas registradas existentes conservadas hasta activar.
- Leer, arrancar o guardar nunca activa. El editor permite cargar HEAD/documentos actuales, completar el plan
  y entorno privado, guardar VALIDATED y preparar explícitamente con T008 y la pareja todavía activa. La
  configuración global guardada es la referencia candidata durante esta transición, sin hacerse activa para jobs.
  No se convierte un recibo v1/v2 ni se presenta como recibo de perfil propio. Falta documental/herramienta/plan,
  validación fallida, deriva o escritor incierto mantienen la puerta de activación cerrada.
- Activación global exige todos los proyectos importados, referencias vigentes, recibos nuevos y barrera D118;
  también verifica que el registro no cambió desde el snapshot. Un TOML original modificado invalida la
  confirmación HTTP. RESTART_REQUIRED cierra admisión. Reiniciar con el almacén gestionado y sin la fuente
  externa revalida y promueve todas las referencias, convirtiendo las filas al contexto documental v9 con evento.
  Originales, eventos previos, trabajos, snapshots y recibos conservan bytes/autoridad o su bloqueo compatible.
- API/UI en/es: revisión y confirmación de conversión, perfiles importados enlazados, editor manual/plan,
  preparación y activación conjunta. Reenvíos usan sobre/clave existentes; GET/montaje no importan ni preparan.
  OpenAPI/tipos en paridad. No hay migración, tabla, dependencia ni versión de producto nueva: **0027/54 tablas**.
- Backup **formato 2**: inventario exacto de ámbitos/revisiones/operaciones, TOML inmutables y copias de trabajo,
  archivos parciales de intenciones y evidencias CLI de asistencia/preparación referenciadas. Roots explícitos,
  parada declarada y exclusión SQLite; no copia recursiva de cachés/venv/login ni ejecución de rutas almacenadas.
  TOML con guardias privadas del editor y 64 KiB; inmutables por hash, cambios durante copia rechazados,
  ausencias parciales explícitas, COMPLETE solo después del conjunto. Deriva de copia editable se conserva como
  evidencia, sin hacerla activa ni conciliarla. La base conserva candidatos/estados inciertos tal cual.
- Verificación reconstruye inventario/referencias desde SQLite y comprueba correspondencia y bytes. Bundles
  formato 1 sin configuración versionada siguen verificables/restaurables; uno que omita configuración no se
  acepta como completo. Restore mantiene consulta persistente, no remapea destinos ni repara intenciones.
  Lectura autenticada de revisiones usa el bundle, sin TOML original, checkout ni agentes; mutaciones bloqueadas.

## Validación y límites

Pruebas solo con archivos, Git/SQLite temporales, ejecutores/CLI falsos y transporte nativo sintético;
ningún proveedor real.

- Suite completa offline: **2042 pytest y 29 subtests correctos**, dos opt-in omitidas. Primera pasada:
  2039 correctos y un fallo en una aserción genérica de retirada que confundía `/configuration/import/` con
  la importación antigua retirada; se acotó la comprobación sin restaurar ningún endpoint retirado.
- Tras las últimas guardias de rutas/estado/recibo: **33 regresiones de importación/backup** correctas y
  **una regresión de receta/backup** correcta. El recibo genérico posterior no desplaza al de una receta aún
  activa; la selección exige receta/hash exactos. Evidencia CLI de preparación y asistencia conservada sin originales;
  propietario de asistencia vivo rechaza backup antes de crear destino.
- **153 Node y 8 unittest correctos**; UI de conversión en/es con montaje pasivo, diff, confirmación/hash/clave,
  perfiles DRAFT visibles y ausencia de activación/detección implícitas. Tipos/build correctos, aviso conocido de chunks.
- OpenAPI generado idéntico a `create_app().openapi()` y tipos regenerados. Alembic en SQLite temporal:
  `upgrade head` y `check` sin diferencias, **0027/54 tablas**. Sin migración nueva ni bases de operación.
- [Checker reproducible](P013-T011_CHECK_DOCS.py): 13 fases, 15 tareas, 228 decisiones, 874 enlaces/anclas en
  once documentos; presupuestos e históricos D001–D227 intactos. STATE compactado con referencias conservadas.
  Mermaid: cuatro flowcharts, dos secuencias y trece ER, cero fallos con el checker archivado citado en T001
  (solo parseo con stub DOMPurify, sin renderizado/QA visual). `git diff --check` y revisión de diff correctos;
  ningún cambio en `docs/archive/` ni `docs/public/`.

Casos propios: ocho formatos con hashes antes/después idénticos; arranque/GET pasivos; importación/replay y
conflicto de fuente/registro; cinco fronteras de caída y recuperación con declaración de parada; recorrido de
perfil convertido → preparación nueva → activación conjunta → reinicio sin original. Backup con global activa,
pendiente y borrador posterior; cuatro fronteras de intención parcial, ausencia/corrupción/permisos/enlaces,
carrera durante copia y manifiesto resealado incompleto; bundle v1 y consulta HTTP sin originales.

La preparación de proyectos importados exige documentación D088 ya comprometida y un plan técnico explícito.
No genera documentos por inferencia ni autoriza instalar/descargar automáticamente. Una configuración con
techo de permisos anterior sin resolver o requisitos nuevos incumplidos conserva su operación legacy y requiere
resolver el candidato antes de convertir/activar. Autenticación de proveedores sigue siendo externa.

Sin navegador/QA visual, servicio instalado, smokes, harness sobre este checkout, proveedores/red, datos P012,
cambios globales del equipo, candidato/distribución, tag, push, CI remota o publicación. T012 verificará primer
uso instalado/QA y documentación de usuario; T013–T015, candidato/revisión/cierre.
