# Matriz nueva autorizada después de los timeouts (D071)

2026-10-14. D070 terminó en planner por errores registrados de conexión Codex,
sin escritor ni commit. Se informó la causa concreta y los límites; el usuario
respondió **«Autorizar una nueva matriz»** a la propuesta de cuatro combinaciones,
máximo doce invocaciones y parada al primer fallo. No se reutiliza D070.

Nueva área `/private/tmp/harness-provider-matrix-6`. Mismo paquete corregido de
D070 en `/private/tmp/harness-provider-matrix-5-package`, instalado offline en
venv propio desde requirements por hashes y wheel sin dependencias implícitas.
Se verifica que el código de producto actual coincide byte a byte con el wheel.
No se cambian permisos, autenticación, modelos, esfuerzos, transporte, contrato
o tratamiento de errores para repetir. Historiales/evidencias previos conservados.

Se mantienen íntegros los criterios y límites de [D069](PROVIDER_MATRIX_CLI9_PROPOSAL.md)
y la corrección de [D070](PROVIDER_MATRIX_CLI9_CORRECTED_PROPOSAL.md):
Codex→Codex, Claude→Claude, Claude→Codex, Codex→Claude, secuenciales; gpt-6-luna
y claude-sonnet-4-6, planner/reviewer medium y executor low; tres invocaciones
por par como máximo, cero ciclos, sin retry/fallback. Check/test/build/JUnit,
ACCEPT por contenido exacto y commit mecánico del harness. No check/cierre/tag,
recuperación, archivado, push ni avance a H6.2.

Controlador `/private/tmp/h71_flow_check.py`, configuración/checkout/estado
nuevos. `execution-preparation.json` congela binarios, wheel/sdist/pins,
scripts, TOML, HEAD/árbol/documentos, transporte y código de contratos/prompts.
Muestras globales de config/settings/gitconfig y archivos de memoria habitual
comparadas cada segundo y antes/después. No registra contenidos privados o auth.
Cambios o fallos paran; siguientes pares requieren éxito anterior. Los límites
de este muestreo y de auth/auxiliares conservan los de D069.

```sh
python3 /private/tmp/h71_flow_check.py run codex-codex
python3 /private/tmp/h71_flow_check.py run claude-claude
python3 /private/tmp/h71_flow_check.py run claude-codex
python3 /private/tmp/h71_flow_check.py run codex-claude
```

Cada proceso real obtiene además permiso explícito de herramienta fuera del
sandbox de desarrollo. Verificador de SQLite/Git/artifacts en lectura antes de
la siguiente combinación. No se declara éxito por el stdout del driver únicamente.
