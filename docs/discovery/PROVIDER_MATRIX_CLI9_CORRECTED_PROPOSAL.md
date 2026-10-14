# Nueva comprobación tras el contrato contradictorio (D070)

D069 se detuvo tras tres invocaciones Codex: escritor real correcto y
validaciones aprobadas; revisor BLOCKED porque el planner produjo
allowed_paths=["src/estimate.ts"] y forbidden_paths=["**"]. Sin commit ni
cambios en las muestras globales. Servicio/procesos cerrados y cero locks;
los otros tres pares no se lanzaron. Se conserva íntegra su evidencia.

El usuario pidió completar la comprobación. Se corrige el contrato antes de
continuar: prompt/esquema explican precedencia y allowlist completa; el motor
rechaza prohibiciones que cubren una ruta concreta autorizada antes de ejecutar.
No se eliminan silenciosamente prohibiciones ni se alteran runs congelados.
Exclusiones parciales dentro de un glob permitido siguen siendo válidas.
Cinco regresiones nuevas verifican parada en planner sin escritor/validación
y conservación del original, además del caso válido y prompt congelado.

Esta es una ejecución nueva con paquete corregido, no un retry/fallback dentro
de D069. Área nueva `/private/tmp/harness-provider-matrix-5`, wheel/pins en
`/private/tmp/harness-provider-matrix-5-package`, controlador propio
`/private/tmp/h70_flow_check.py` y manifiesto execution-preparation.json.
Se conservan todos los modelos, esfuerzos, permisos, órdenes, criterios y
guardias de [D069](PROVIDER_MATRIX_CLI9_PROPOSAL.md). Máximo doce invocaciones
nuevas, una combinación a la vez; cualquier fallo detiene esta matriz sin
relanzamiento automático. Tres invocaciones previas ya consumidas en D069.
El mecanismo de herramientas autoriza expresamente cada orden real necesaria.

```sh
python3 /private/tmp/h70_flow_check.py run codex-codex
python3 /private/tmp/h70_flow_check.py run claude-claude
python3 /private/tmp/h70_flow_check.py run claude-codex
python3 /private/tmp/h70_flow_check.py run codex-claude
```

No se avanza al siguiente alcance ni se declara cerrado lo que no pase.
