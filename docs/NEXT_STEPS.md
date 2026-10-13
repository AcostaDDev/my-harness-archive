# Siguiente tarea — H3.2: permisos y acciones de recuperación

H3.1 completado offline el 2026-10-13 (D030):
[prompts versionados](discovery/H3.1_PROMPTS.md),
[alcance completado](discovery/H3.1_SCOPE.md).
Catálogo por ámbito, editor, variables, diff, borradores, activación y rollback
como versión nueva; snapshots persistidos antes de cada invocación, con lectura
de históricos y conservación de versiones al reanudar. Migración 0008.
331 pruebas pytest (23 H3.1), 121 subtests, 12 checks ligeros, 3 pruebas Node,
tipos/TypeScript/build y recorrido Chrome con
SQLite/demo sintética correctos. No se han usado proveedores.

**H3.2 no iniciado.** Los consentimientos de smokes anteriores siguen agotados.

## Objetivo y alcance siguiente

Completar H3.2 del backlog en una entrega acotada, sin iniciar H3.3:

1. Revisar especificación de permisos/recuperación, backlog H3.2 y los contratos
   H2 existentes. Separar ficheros, herramientas, red y decisiones de producto;
   señalar contradicciones materiales antes de cambiar diseño.
2. Implementar solicitudes/concesiones/denegaciones con vigencia, identidad,
   contexto exacto y auditoría. No inferir autorizaciones de prompts ni reviews.
3. En CLI, aplicar permisos solo al siguiente intento autorizado; no conceder
   operaciones a una llamada viva ni habilitar SDK automáticamente.
4. Exponer las acciones pertinentes por API/UI, con controles de versión,
   confirmaciones y guardias locales; mantener revalidar y reintentar separados.
5. Caracterizar offline caducidad, modificación de solicitudes, concurrencia,
   reinicio y conservación de históricos con fakes y SQLite temporal.
6. Ejecutar verificaciones pertinentes, revisar diff y actualizar STATE,
   NEXT_STEPS, DECISIONS e informe.

## Criterios de aceptación

- Una solicitud caducada o modificada no acepta una autorización anterior.
- Conceder/denegar registra identidad, alcance, vigencia y motivo verificables.
- Ficheros, herramientas, red y decisiones de producto no se autorizan entre sí.
- Revalidar y reintentar conservan efectos distintos y visibles; no hay fallback
  ni llamadas adicionales silenciosas.
- Historial, exclusión de checkout, snapshots y aceptación por contenido exacto
  siguen intactos. Pruebas offline y API/tipos/TypeScript/build pertinentes pasan.

## Fuera de alcance

Proveedores reales, smokes, login/refresh, secretos, recuperación de D020/D022,
SDK/permisos interactivos vivos, fases H3.3, integración de rama, push/publicación,
chat y distribución. No lanzar agentes de colaboración ni usar el harness para
desarrollar este repositorio. Sesión local, guardia H0/H1, SSE gestionado y
registro de proyectos por HTTP permanecen pendientes, sin ampliación implícita.
