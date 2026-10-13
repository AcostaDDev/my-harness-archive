# Siguiente tarea — H5.3 Retención local de logs

H5.2 backup/restauración local se completó offline el 2026-10-13 (D040).
Copia con servicio/escritores detenidos y mecanismo de backup SQLite; manifiesto,
hashes/referencias verificadas, restauración a destino nuevo y guardia persistente
de solo lectura. No se reanudan procesos ni se repiten efectos al abrir una copia.
Ver [procedimiento y límites](discovery/H5.2_BACKUP.md) y
[alcance original](discovery/H5.2_SCOPE.md).

Estado verificado:

- esquema `0013_bootstrap` y codec 6 conservados; historial 1–6 compatible;
- 612 pruebas pytest y 121 subtests, con 43 casos nuevos de backup/restauración;
- WAL real, historial/snapshots/JUnit/eventos y filas operativas conservados;
- prompts/streams CLI, rangos y colas inciertas, snapshots/exportación H2.5;
- consultas HTTP y artefactos restaurados independientes de sus originales;
- guardia SQLite/API, sin cargar configuración ni iniciar supervisor/observador;
- corrupción/ausencia/versiones/rutas/enlaces/límites/concurrencia rechazados;
- 12 checks ligeros, cuatro pruebas Node, TypeScript/build y checks de esquema/OpenAPI.

No se copió ni migró la SQLite de trabajo, no se usaron proveedores ni smokes.
No se implementaron GC, distribución ni reactivación operativa de una copia.
**H5.3 no está iniciado.** Los consentimientos de smokes siguen agotados.

## Objetivo y alcance (siguiente incremento del hito 5)

1. Definir una política local explícita de retención de logs voluminosos y sus
   límites; separar originales purgables de contratos, snapshots, permisos,
   aprobaciones y veredictos que deben conservarse.
2. Diseñar e implementar vista previa y aplicación explícita de la política sobre
   artefactos gestionados, con diagnóstico/auditoría de bytes retirados y
   referencias ausentes deliberadamente diferenciadas de pérdida/corrupción.
3. Mantener backup/restauración compatibles con la evidencia retenida y probar
   offline sobre datos sintéticos. No purgar archivos reales del usuario.

## Criterios de aceptación

- La política y sus efectos son visibles antes de eliminar bytes; no hay purga
  automática ni eliminación de artefactos de intentos activos/inciertos.
- Historial, contratos, decisiones, aprobación/veredicto y procedencia exacta se
  conservan; retirar un log no certifica éxito ni borra sus hashes observados.
- La consulta distingue purga autorizada de archivo perdido y no sirve otra
  versión de bytes como si fuera la registrada.
- Backup/restauración conserva lo retenido y representa las ausencias autorizadas
  sin admitir corrupción silenciosa. Las copias existentes permanecen intactas.
- Regresiones offline pertinentes correctas y documentación actualizada.

## Fuera de alcance

- Distribución/assets/comando único de inicio, diagnósticos CLI/SDK y otros
  incrementos de H5; reactivación operativa de restauraciones y backup de Git.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
