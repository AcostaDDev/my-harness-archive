# Siguiente acción — H2.3: smoke real pendiente de autorización

H0, H1, H2.1 y H2.2 completados. H2.3 implementado y caracterizado offline
el 2026-10-11: [alcance original](discovery/H2.3_SCOPE.md) y
[entrega/verificaciones](discovery/H2.3_CLI.md). 204 pruebas pytest y 121 subtests,
12 checks ligeros, migraciones, OpenAPI/tipos, TypeScript y build correctos.
No se ha ejecutado ningún proveedor ni iniciado H2.4.

## Objetivo pendiente

Resolver la verificación real H2.3 con autorización específica de consumo.
La entrega offline satisface los criterios de implementación/procesos; no
acredita acceso a modelos, cuota, autenticación real, comportamiento de flags ni
retries internos de las CLI frente a los proveedores.

## Acción acotada

1. Revisar `scripts/smoke_cli.py`, D017 y los límites de la entrega. Confirmar
   modelos/esfuerzos de Codex y Claude y directorio de salida fuera del checkout.
2. **Solicitar autorización explícita de consumo antes de ejecutarlo.** La pregunta
   ya se planteó al entregar la implementación; no se ha recibido autorización.
   No inferirla de instrucciones de implementación, tests, commit o tiempo transcurrido.
3. Con autorización y selecciones, usar el script con `--authorize-consumption`:
   hasta tres invocaciones CLI de 60 s cada una, herramientas vacías, suscripciones
   propias y checkout desechable. No pasar API keys ni activar fallback/resume.
4. Conservar evidencia y registrar comportamiento real, terminales/errores,
   telemetría ausente/observada y límites de permisos/cancelación/retries. Ante fallo,
   detenerse sin relanzar ni sustituir selección/proveedor. Un smoke no demuestra
   cero retries internos ni aislamiento total.
5. Actualizar STATE/NEXT_STEPS/DECISIONS según el resultado. Si no hay autorización,
   conservar esta verificación pendiente; no presentar los fakes como CLI real.

## Criterios de aceptación de esta verificación

- Consentimiento y modelos/esfuerzos explícitos antes de consumo.
- Repositorio desechable y evidencias independientes de los datos del usuario.
- Máximo tres invocaciones CLI, timeout/cancelación y cero fallback del adaptador.
- Resultados reales separados de caracterización offline, sin aceptación/commit
  de producto inferidos. Registrar expresamente lo no demostrado.

## Fuera de alcance

No implementar H2.4: worktrees/captura Git completa/commit de producto. Tampoco
H2.5 migración de proyectos, entradas gestionadas API/CLI/UI, permisos vivos,
chat, SDKs, cierre de fase ni distribución. No ejecutar el harness para desarrollar,
lanzar otros agentes automáticamente, usar runs reales, acceder a credenciales,
modificar configuración global ni ejecutar tests/instalaciones en ReferenceProject.
