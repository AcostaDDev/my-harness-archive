# Siguiente tarea — H5.2 Backup y restauración local

H5.1 importación JUnit y detalle de tests se completó offline el 2026-10-13
(D039). Original/hash y casos conservados en el historial, declaraciones por
comando/perfil, captura/parser acotados, procedencia de run/intento/comando/Git,
consulta paginada y descarga API/UI. TypeScript genera JUnit con el reporter Node.
Ver [entrega y límites](discovery/H5.1_JUNIT.md) y
[alcance original](discovery/H5.1_SCOPE.md).

Estado verificado:

- esquema `0013_bootstrap` sin migración nueva; codec 6 y formatos 1–5 compatibles;
- 569 pruebas pytest y 121 subtests; checks de esquema/OpenAPI existentes;
- 43 casos JUnit nuevos y reporter Node real con tres casos/duraciones;
- 12 checks ligeros, cuatro pruebas del cliente Node y TypeScript/build;
- reportes válidos, truncados, inválidos, ausentes y anteriores con diagnósticos;
- XML activo, rutas externas/enlazadas, archivos especiales y límites rechazados;
- original persistido después de reiniciar y de editar/eliminar su fuente;
- revalidación y check de fase, comandos/intentos/evidencia exacta conservados;
- paginación HTTP, errores como texto en Chrome y commit exacto/invalidez por deriva.

No se usaron proveedores ni se migró la SQLite de trabajo. No se incorporó
retención, backup ni distribución. **H5.2 no está iniciado.** Los consentimientos
de smokes siguen agotados.

## Objetivo y alcance (segundo incremento del hito 5)

1. Definir y realizar una copia local consistente de la SQLite y de los artefactos
   gestionados necesarios para recuperar su historial y referencias.
2. Restaurar explícitamente en un destino nuevo, con manifiesto, hashes y
   comprobación de compatibilidad/integridad; conservar los originales.
3. Verificar offline con bases/checkouts/artefactos sintéticos y documentar el
   procedimiento y sus límites. Una restauración no autoriza a reanudar procesos.

## Criterios de aceptación

- La copia conserva historial, snapshots, reportes y referencias de artefactos
  con una política explícita de consistencia frente a actividad del servicio.
- Restaurar en un destino vacío produce una autoridad SQLite íntegra y artefactos
  verificables; corrupción, ausencia o versión incompatible producen diagnóstico.
- No sobrescribe el estado de trabajo ni supone que procesos inciertos terminaron;
  no ejecuta agentes ni repite efectos al restaurar.
- Pasa el recorrido offline copia → restauración → consultas con datos sintéticos,
  las regresiones pertinentes y se actualiza la documentación.

## Fuera de alcance

- Retención/GC, empaquetado/distribución y demás incrementos de H5.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
