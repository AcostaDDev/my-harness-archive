# Siguiente tarea — Salida del hito 2, parte 2: UI gestionada local

Parte 1 completada y verificada offline el 2026-10-12 (D028): API `/api/managed`
con proyectos registrados en el servidor, supervisor opt-in en el proceso Uvicorn,
`Idempotency-Key`/`expected_version`, 409 con diagnóstico y guardia Host/Origin/CSRF.
[Informe](discovery/H2_EXIT_API.md), [alcance completado](discovery/H2_EXIT_API_SCOPE.md).
306 pruebas y 121 subtests, 12 checks ligeros correctos. Sin proveedores ni smoke.

**No iniciada.** Cierra la salida del hito 2: «una tarea puede ejecutarse,
revisarse y completarse desde la UI con recuperación verificable». Esta tarea es
offline; los consentimientos de smokes anteriores están agotados.

## Objetivo

UI React que consuma solo los tipos generados de `/api/managed` para:

- consultar el modo del proyecto y migrarlo;
- encolar una tarea;
- seguir su ejecución;
- revisar el resultado;
- confirmar el commit;
- recuperar un job en cuarentena.

Todo ello sin lógica de motor en el cliente.

## Alcance acotado

1. Revisar D011, D013/D014, D027, D028 y la §12 de la especificación (experiencia
   de usuario). Señalar contradicciones materiales antes de cambiar diseño.
2. Seguridad del cliente:
   - enviar `X-Harness-Local: 1` en las mutaciones gestionadas;
   - decidir y documentar si la guardia Host/Origin/CSRF se extiende a las
     mutaciones H0/H1 (simulación y observación);
   - decidir si la sesión local se implementa ahora o queda explícitamente
     pendiente.
3. Pantallas:
   - proyectos registrados, modo y estado del supervisor;
   - vista previa, activación y reversión con confirmaciones explícitas;
   - encolar tarea con clave de idempotencia generada en el cliente y conservada
     ante reintentos de red;
   - run con historial, intentos, aceptación y commit;
   - eventos paginados por cursor, con sondeo o SSE (decidir; si se añade SSE
     gestionado, solo filas confirmadas, con id creciente y reconexión);
   - acciones revalidar, reintentar, commit y confirmar escritor detenido, con
     `expected_version` de la pantalla y recarga ante 409.
4. Configuración local de desarrollo para probar la UI con puertos falsos, mediante
   un módulo de ejemplo para `HARNESS_MANAGED_CONFIG` con datos sintéticos, sin
   proveedores. Documentar cómo se configurarían los adaptadores CLI H2.3 y Git H2.4
   sin activarlos.
5. Regresión offline: pruebas API existentes, TypeScript y build. Recorrido en
   navegador sobre la UI compilada con SQLite/Git sintéticos y fakes:
   - encolar y ver ACCEPTANCE_READY;
   - commit hasta COMMITTED;
   - doble clic sin duplicados;
   - reinicio del servicio con la página abierta;
   - cuarentena, confirmación y revalidación.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE, NEXT_STEPS,
   DECISIONS e informe.

## Criterios de aceptación

- Desde la UI, una tarea con fakes recorre ejecución, revisión y COMMITTED con
  eventos visibles y sin duplicados ante doble envío o reinicio.
- La recuperación de un job en RECOVERY_REQUIRED se completa desde la UI con
  confirmación explícita y sin repetir efectos.
- Los rechazos de modo y los conflictos de versión se muestran con su diagnóstico,
  sin estado optimista que los oculte.
- Ningún proveedor se invoca; tipos generados sin contratos duplicados a mano.

## Fuera de alcance

Proveedores reales u otro smoke (requiere propuesta y consentimiento propios),
login/refresh, secretos, recuperación de D020/D022, integración en rama destino,
push/publicación, H3 (prompts versionados, permisos interactivos, fases), chat,
SDK, distribución. No modificar ReferenceProject, configuración global ni lanzar agentes
de colaboración.
