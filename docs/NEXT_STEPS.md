# Siguiente paso — Ejecutar el primer uso real, solo con consentimiento específico

Propuesta de primer uso real (D033.8) preparada y ensayada offline el
2026-10-13 (D050). Ver [propuesta](discovery/FIRST_USE_PROPOSAL.md) y
[script de preparación](../examples/first_use/prepare.sh). **No ejecutada.**

- Selecciones del usuario: ejecutor `claude-sonnet-4-6`/`low` con `Read`,
  `Edit`, `Write`, `Glob`, `Grep`; revisor y evaluación de fase
  `gpt-6-luna`/`medium`; planificación determinista (planificador no invocado).
- Checkout desechable desde la fixture `typescript_web` con regresión
  deliberada; TOML concreto con rutas reales bajo `/private/tmp/harness-first-use`.
- Claude fijado al binario versionado 2.1.295 (el enlace del usuario apunta a
  2.1.296, no admitido por `cli-4`).
- Ensayo offline: preparación, `check-config` sin preflight, `init-db`,
  admisión en proceso sin supervisor (contrato, fase y job `QUEUED`) y comandos
  del perfil con el entorno exacto (`test` falla por la regresión). Sin CLI de
  proveedores, `serve`, red ni consumo.

## Tarea concreta propuesta, no iniciada

Ejecutar una sola vez la propuesta D050 tal como está escrita: preparación,
preflight, servicio con `--config`, fase P001, tarea P001-T001 → commit →
check → cierre con tag `first-use-p001`; como máximo tres invocaciones de
proveedor y parada al primer resultado inesperado. Requiere que el usuario
autorice explícitamente esa ejecución y su consumo; se hace fuera del sandbox.

Antes de ejecutar: comprobar que `~/.local/share/claude/versions/2.1.295` sigue
existiendo y que la ruta `BASE` no existe. Cualquier cambio de modelos,
esfuerzos, herramientas, límites o entorno exige actualizar antes la propuesta.

Alternativas: QA visual pendiente de un navegador que permita loopback;
admitir Claude 2.1.296 en el baseline como tarea propia (caracterización y
`cli-5`); verificar `serve --config` con el wheel instalado; endurecimientos de
D048 (heartbeat y PGID). Fuera sin nueva decisión: otros perfiles,
`.harness/project.yaml`, UI de configuración y recarga en caliente.

Consentimientos anteriores agotados. Sin proveedores/login, instalaciones con
red, publicación, push ni uso del harness para desarrollar este repositorio.
Este documento no autoriza ejecutar la propuesta ni iniciar otra implementación.
