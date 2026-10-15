# Ensayos cli-9 detenidos antes del cierre (D069/D070)

2026-10-14. El usuario pidió comprobar el flujo para dejarlo cerrado. Se
prepararon matrices funcionales nuevas, sin reutilizar consentimientos previos,
desde wheels instalados fuera del checkout, con propuestas y permisos de
herramientas explícitos. [Manifiesto/evidencias](PROVIDER_MATRIX_CLI9_STOPS.json).
Ninguno de estos ensayos cierra las cuatro combinaciones.

## D069: contrato contradictorio

Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_PROPOSAL.md`). Área
`/private/tmp/harness-provider-matrix-4`, paquete cli-9 con D068. Solo se lanzó
Codex→Codex: run `00659184-7044-4d10-85f6-a3020859251b`, tres COMPLETE,
gpt-6-luna medium/low/medium. Escritor hizo el cambio real únicamente en
src/estimate.ts; check/test/build aprobados y JUnit completo con tres casos.

El planner devolvió allowed_paths=["src/estimate.ts"] y forbidden_paths=["**"].
El contrato aceptaba ambas listas sin detectar su contradicción. La validación
posterior detectó la violación y el revisor emitió BLOCKED correctamente: el
deny tiene precedencia, no se puede interpretar como "todo lo demás". No hay
ACCEPT/aceptación/commit; el cambio queda en el checkout sacrificial.

La supresión D068 funciona en este escritor real: el argv tiene tabla projects
inline untrusted y las muestras de configuración/memorias permanecen iguales.
El muestreo no es auditoría completa. Jobs DONE, owners cerrados, cero locks,
procesos/servicio ausentes, clave retirada, docs intactos. Tres pares restantes
con áreas vacías y no lanzados. No hay retry ni recuperación de este run.

Se corrige el motor para rechazar una ruta concreta autorizada que también
esté prohibida, una prohibición universal o un patrón idéntico permitido/denegado
antes del escritor. Globs con exclusiones parciales válidas permanecen admitidos;
no se pretende resolver toda intersección de patrones. Nunca se quita una
prohibición para permitir trabajo. Prompt/esquema explican allowlist completa
y precedencia. Cinco regresiones nuevas pasan; originales e historiales intactos.

## D070: errores de conexión, no fallo de edición

Propuesta corregida (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_CORRECTED_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_CORRECTED_PROPOSAL.md`). Área nueva
`/private/tmp/harness-provider-matrix-5`, paquete corregido instalado. Solo
Codex→Codex inició: run `9dff069b-90e2-4292-8687-5414ef05aceb`, un planner.

Codex registra timeout al refrescar modelos y conexiones MCP internas fallidas,
y tres eventos stdout error de reconexión por workspace routing discovery.
Después entrega un plan JSON válido (allowed src/estimate.ts, forbidden []) y
turn.completed, exit 0. El adaptador existente mantiene cualquier evento error
como fallo del stream: FAILED / CLI failed, run STOPPED en planner. No se
interpreta un terminal posterior como permiso para ocultar errores previos.
Esto no demuestra que la corrección del contrato falle ni que Codex no escriba.
Tampoco se afirma cuota/auth rota: la evidencia observada son timeouts.

No se lanzó ejecutor/revisor ni commit. Git limpio con HEAD inicial, docs sin
cambios, muestras globales iguales, job DONE/owner cerrado, procesos muertos,
cero locks, servicio cerrado y clave retirada. Tres pares no lanzados, estado
vacío. Retries internos de Codex son visibles en el stream y siguen fuera del
control del harness; el harness no hizo retry/fallback. No se cambia el parser,
red/permisos/modelos/auth ni se consume más dentro de este ensayo.

El usuario autoriza expresamente después una matriz nueva: «Autorizar una nueva
matriz», máximo doce invocaciones/parada al primer fallo. D071 es esa comprobación
separada, conservando D069/D070. No se usa el consentimiento agotado de ninguno.

## Verificación de implementación

217 tests de transporte y 155 de contratos/motor/permisos/prompts pasan, además
de 12 checks estándar. El primer pase completo produjo 947 passed y una
aserción antigua que exigía el esquema sin descripción; se corrige para verificar
tipos y la descripción nueva. No se modifica el producto para ocultar ese fallo.
Suite completa posterior y resultado D071 se registran en su informe final.
Dos builds offline y dos verificaciones de wheel aislado correctos, con agentes
falsos. No hay cambios de API/UI/migraciones/dependencias ni nuevas versiones
de CLI. cli-9/local-config-2, congelados históricos y núcleo independiente de
proveedores conservados. No se avanza a H6.2/archivado.
