# Siguiente tarea — Salida del hito 2, parte 1: API gestionada local

H2.5 completado y verificado offline el 2026-10-12 (D027): vista previa sin
escrituras, copia consistente con manifiesto, activación atómica y reanudable,
exclusión legacy/gestionado por marcador y deriva, y reversión verificada.
Migración `0007_managed_activation`. [Informe](discovery/H2.5_MIGRATION.md),
[alcance completado](discovery/H2.5_SCOPE.md). 288 pruebas y 121 subtests, 12
checks ligeros correctos. Sin proveedores ni smoke nuevo.

**No iniciada.** El backlog no numera esta tarea: la salida del hito 2 exige que
«una tarea pueda ejecutarse, revisarse y completarse desde la UI con recuperación
verificable», y hoy motor, supervisor, commit y migración solo tienen entradas de
biblioteca. Se propone dividirla en API (esta tarea) y UI (la siguiente).
Los consentimientos de smokes anteriores están agotados; esta tarea es offline.

## Objetivo

Exponer por HTTP local (loopback) las operaciones gestionadas existentes, con
contratos Pydantic como fuente de OpenAPI y tipos generados, sin lógica nueva de
motor: el servicio delega en `SQLiteManagedRepository`, `LocalSupervisor` y
`MigrationService`, y conserva sus garantías (idempotencia, versiones esperadas,
exclusión, recuperación explícita).

## Alcance acotado

1. Revisar especificación (API, supervisor local, seguridad local), D010/D011,
   D016/D017, D026 y D027. Señalar contradicciones materiales antes de cambiar diseño.
2. Decidir y documentar cómo se ejecutan los jobs desde el servicio: supervisor
   opt-in en el proceso Uvicorn (como la observación H1.3) o acción explícita
   «ejecutar siguiente job». Sin autoarranque implícito ni proveedores por defecto.
3. Endpoints de migración: vista previa, activar, reanudar/abandonar, revertir y
   estado de un checkout. Endpoints gestionados: encolar tarea, listar runs/jobs/
   intentos/eventos paginados, revalidar/reintentar, encolar commit y confirmar
   escritor detenido. Claves de idempotencia y versiones esperadas obligatorias;
   409 con diagnóstico ante conflicto o rechazo de modo.
4. Puertos por configuración explícita: fakes en pruebas; adaptadores CLI H2.3 y
   Git H2.4 solo si se configuran expresamente, sin invocarlos en esta entrega.
5. Regresión offline con TestClient, SQLite/Git sintéticos y fakes: recorrido
   completo hasta COMMITTED, rechazos de modo, doble envío, reinicio y
   recuperación. OpenAPI y tipos regenerados; TypeScript y build correctos.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

## Criterios de aceptación

- Un recorrido HTTP con fakes encola, ejecuta, revisa y deja COMMITTED una tarea,
  con eventos consultables y sin duplicados ante doble envío o reinicio.
- Los rechazos de modo (legacy no activado, deriva, marcador) y los conflictos de
  versión se devuelven con diagnóstico, sin efectos parciales.
- Migración por HTTP con las mismas garantías que la biblioteca (vista previa sin
  escrituras, activación reanudable, reversión verificada).
- Ningún endpoint invoca proveedores por defecto; tests offline pertinentes pasan
  y contratos/versiones documentados; no presentar diseño como implementación.

## Fuera de alcance

UI gestionada (parte 2), proveedores reales u otro smoke, login/refresh, secretos,
recuperación de D020/D022, integración en rama destino, push/publicación, H3
(prompts versionados, permisos, fases), SDK, chat o distribución. No modificar
ReferenceProject, configuración global ni lanzar agentes de colaboración.
