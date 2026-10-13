# Siguiente paso — Propuesta de primer uso real con la configuración local

Composición de uso real por TOML local implementada y verificada offline el
2026-10-13 (D049). Ver [entrega](discovery/LOCAL_CONFIG.md),
[alcance](discovery/LOCAL_CONFIG_SCOPE.md) y [plantilla](../examples/local_config.example.toml).

- `local-config-1`: archivo privado del operador fuera de los checkouts, esquema
  estricto, perfil `typescript-web`, CLI cli-4, comandos commands-1 y Git con
  identidad explícita; adaptadores nuevos por job.
- Versiones con hash de composición: un TOML cambiado con jobs pendientes los
  pone en cuarentena antes de efectos.
- `harness-local check-config RUTA [--preflight]` y `serve --config RUTA`.
- 846 pruebas pytest y 121 subtests, 12 checks ligeros y 6 pruebas Node
  correctos. Esquema, codec, cli-4, OpenAPI, UI y dependencias sin cambios.

## Tarea concreta propuesta, no iniciada

Preparar, sin ejecutarla, la propuesta de primer uso real (D033.8): checkout
TypeScript desechable, TOML concreto con rutas reales, modelos/esfuerzos y
herramientas del ejecutor elegidos por el usuario, recorrido tarea → commit →
check → cierre, límites de consumo y criterios de parada. Ejecutarla requiere
autorización específica y explícita del usuario.

Alternativas: QA visual pendiente de un navegador que permita loopback;
verificar `serve --config` con el wheel instalado; endurecimientos de D048
(heartbeat y PGID). Fuera sin nueva decisión: otros perfiles, `.harness/project.yaml`,
UI de configuración y recarga en caliente.

Consentimientos anteriores agotados. Sin proveedores/login, instalaciones con
red, publicación, push ni uso del harness para desarrollar este repositorio.
Este documento no autoriza iniciar otra implementación.
