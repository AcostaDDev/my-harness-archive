# Siguiente paso — Elegir el incremento posterior al primer uso real

Primer uso real D050 ejecutado una vez y completo el 2026-10-13
([resultado](discovery/FIRST_USE_RUN.md), D050/D051). Consentimiento agotado.

- Recorrido tarea → commit → check → cierre sobre un checkout desechable:
  `COMMITTED` (`8999af8`), fase `CLOSED` y tag ligero `first-use-p001`.
- Tres invocaciones de proveedor, todas `complete`: ejecutor
  `claude-sonnet-4-6`/`low` (Read + Edit), revisor y evaluación de fase
  `gpt-6-luna`/`medium`. Nueve comandos `commands-1` con exit 0. Historial
  idéntico tras reabrir SQLite.
- D051: el uso real se opera desde el wheel construido, verificado e instalado
  en un venv propio. `serve` desde el checkout de desarrollo no tiene assets.
- Desarrollo local con un solo comando: `scripts/dev` (D053,
  [entrega](discovery/DEV_COMMAND.md)); migración con instantánea previa.

## Tarea concreta propuesta, no iniciada

**Instalación de operación reutilizable (D051).** Encapsular en una entrada
única y probada offline la construcción con `--out-dir`, la verificación
`check_distribution.py`, la creación del venv nuevo con hashes y la comprobación
de `check-config` con el binario instalado. Debe fallar sin efectos si el destino
existe o las herramientas no coinciden, y no tocar `dist/` ni la configuración
global. Reutilizarla en la próxima propuesta de uso real en lugar de los pasos
manuales de esta ejecución. Elección y alcance pendientes del usuario.

Alternativas:

- caracterizar Claude 2.1.296 y abrir `cli-5`, porque el enlace del usuario ya
  no es 2.1.295;
- estudiar el directorio vacío `~/.claude/projects/<checkout>/memory` que crea
  la CLI pese a `--no-session-persistence`;
- propuesta autorizable de ramas REVISE/BLOCKED con proveedores;
- QA visual pendiente de un navegador que permita loopback;
- endurecimientos de D048 (heartbeat y PGID).

Fuera sin nueva decisión: otros perfiles, `.harness/project.yaml`, UI de
configuración y recarga en caliente.

Consentimientos anteriores agotados, incluido D050. Sin proveedores/login,
instalaciones con red, publicación, push ni uso del harness para desarrollar
este repositorio. Este documento no autoriza iniciar otra implementación ni
otra ejecución con proveedores.
