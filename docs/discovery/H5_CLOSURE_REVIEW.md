# Revisión de cierre del hito 5

Revisión documental y estática del 2026-10-13 sobre `65aac62`, con Git limpio.
Continúa la tarea de NEXT_STEPS; no implementa otro incremento.

## Dictamen

Los incrementos H5.1–H5.7 cumplen su alcance offline documentado. El criterio
del backlog de instalar en entorno limpio, completar un flujo y restaurar
backup sin depender del checkout está acreditado para el flujo sintético.
Esta conclusión no acredita un piloto con proveedores ni el MVP completo.
La QA visual reciente queda pendiente por bloqueo de la herramienta.

| Requisito del hito 5 | Evidencia | Límite que se conserva |
|---|---|---|
| JUnit y detalle por test | [H5.1](H5.1_JUNIT.md), parser/original/hash/API/UI | Cobertura declarada; no cobertura de código medida |
| Backup/restauración | [H5.2](H5.2_BACKUP.md), CLI y wheel H5.7 | Escritores detenidos; copia de consulta, sin reactivar ni respaldar Git |
| Retención | [H5.3](H5.3_RETENTION.md), preview y auditoría | Solo stdout/stderr sellados; sin rotación, GC o retención de SQLite |
| Compatibilidad | [H5.4](H5.4_DIAGNOSTICS.md), preflight acotado | Versión/help no certifican auth, cuota o permisos efectivos |
| Distribución e inicio local | [H5.5](H5.5_DISTRIBUTION.md), instalación aislada H5.7 | Sin publicación ni actualización instalada de bases existentes |
| Sesión y protección | [H5.6](H5.6_SESSION.md), HTTP/cliente y paquete | Modelo local POSIX; no aislamiento frente al dueño o servicios hostiles del mismo hostname |
| Crear/importar/ejecutar/bloquear/denegar/reintentar/recuperar | [H5.7](H5.7_E2E.md), seis recorridos y regresión | Agentes/comandos falsos; navegador bloqueado, no QA visual reciente |

La suite anterior de 771 pruebas/121 subtests, seis pruebas Node, doce checks
ligeros y el verificador instalado se ejecutó en esta misma sesión durante H5.7.
Esta revisión no modifica código, dependencias ni artefactos: no repite la suite
ni convierte evidencia previa en una nueva ejecución. Se comprueban enlaces,
diff y coherencia de los documentos modificados.

## Brechas para operar con proyectos reales

1. **Ejecutor de comandos de producto ausente.** El protocolo `CommandRunner`
   existe en `src/harness_local/core/engine/validation.py`; el adaptador incluido
   es `ScriptedCommandRunner`. `FixtureCommandRunner` de
   `tests/product/test_typescript_profile.py` ejecuta comandos reales únicamente
   en fixtures confiables. H4.3/D038 excluyeron expresamente un adaptador de
   producto y la recuperación de sus procesos. No basta con conectar agentes
   reales a la demo para certificar validación real.
2. **Composición de uso real por desarrollar/verificar.** `ManagedConfig` permite
   inyectar agentes, validaciones y Git, y el adaptador CLI existe. El servicio
   instalado no descubre ni configura proyectos/proveedores por sí mismo. Una
   composición real debe fijar ejecutables, entorno, versiones, permisos,
   almacenamiento y recuperación sin reutilizar puertos falsos como validadores.
3. **UI reciente sin comprobar visualmente.** H5.6/H5.7 registraron
   `ERR_BLOCKED_BY_CLIENT`. Los checks HTTP/Node no verifican formularios,
   confirmaciones, retirada de datos y recuperación de pantalla en un navegador.
4. **Recorrido real de proveedores no acreditado.** D025 solo probó transporte
   con herramientas vacías. Tarea/validación/review/commit/check/cierre con
   proveedores requiere preparación y autorización específica de D033.8.
5. **Operación más amplia pendiente.** Rotación/límites de captura, actualización
   instalada, latencia bajo carga y métricas de un piloto figuran como objetivos
   o límites previos. No se dan por resueltos al cerrar los incrementos offline.

No se altera el diseño aceptado ni se convierte estas brechas en funcionalidades
nuevas aprobadas. Tampoco se exige nube, SDK, multiusuario o integración de ramas
para este cierre; siguen fuera del alcance acordado.

## Próximo alcance recomendado, pendiente de elección

Preparar un incremento offline para un ejecutor de validaciones reales de
producto. Antes de codificarlo, concretar:

- argv estructurado sin shell implícita, cwd acotado y entorno/ejecutables
  explícitos congelados; confianza en el repositorio y permisos separados;
- stdout/stderr acotados, exit/timeout/errores observados y persistencia de
  intención antes de efectos; ausencia de reintentos/fallback automáticos;
- propiedad de procesos/grupos y recuperación tras caída que conserve la
  exclusión del checkout mientras el validador pueda seguir vivo;
- integración con validación/JUnit/evidencia exacta, sin introducir otra cola;
- pruebas offline con procesos sintéticos y stack TypeScript de prueba, sin
  proveedores ni cambios globales.

Esto es una propuesta de alcance, no un runner implementado ni autorización
para ejecutarlo sobre proyectos reales. Alternativas: retomar QA visual cuando
el navegador permita acceso o preparar la propuesta de smoke sin ejecutarlo.
