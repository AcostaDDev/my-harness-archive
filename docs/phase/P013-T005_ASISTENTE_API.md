# P013-T005 — API de configuración inicial sin TOML completo

Fecha: 2026-10-26. Base: `8d81e75`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
**Implementada la API inicial y su arranque global; UI pendiente T006, perfiles/altas T007–T009 e importación/backup T011.**
[D222](../DECISIONS.md#d222--p013-t005-asistente-api-y-arranque-con-autoridad-global-versionada),
[contrato T001](P013-T001_CONTRATO.md), [primitivas T004](P013-T004_CONFIGURACION.md),
[flujo actualizado](../flows/configuration-setup.md).

## Resultado y motivo

`ConfigurationSetup` conecta las autoridades de T004 con el servicio instalado. Una instalación nueva ya
puede recibir un formulario JSON sin composición de stack ni TOML redactado a mano. Validación, diff, guardado
y activación son operaciones distintas: guardar conserva la activa, confirmar agenda reinicio y el siguiente
arranque promueve el conjunto validado antes de componer consumidores. Se conserva el cargador legacy 1–8.

Se contrastaron D216/D217/D221, D040/D150/D174 y el contrato de T001. No quedan incongruencias de diseño que
requieran HITL. Los DTO y el alcance global inicial concretan las rutas propuestas; no se añade importación
implícita ni se anticipa la admisión de perfiles propios. La restricción de AGENTS sobre operación sigue vigente.

## Contrato HTTP efectivo

Todas las rutas siguientes tienen prefijo `/api/managed/configuration` y usan la sesión local existente,
Host/Origin/cross-site y cabecera CSRF. El TOML/diff completo solo se entrega en este editor autenticado.
Los códigos de conflicto son estables; diagnósticos propios en inglés/español, sin incluir excepciones crudas,
contenido del candidato, credenciales ni entorno heredado. OpenAPI y tipos TypeScript regenerados.

| Método y ruta | Resultado y guardias |
|---|---|
| `GET /` | Modo, CAS, referencias guardada/activa/pendiente, hashes de copia, id de activación pendiente, ids de recuperación y TOML guardado disponible. No ejecuta procesos ni publica archivos. |
| `POST /detect` | `path` absoluto explícito → candidatos Git/Codex/Claude, cuenta del servicio, directorios fijados y vocabulario de esfuerzos. Solo busca en ese PATH; no lee home, Git config, modelos o credenciales. |
| `POST /check-clients` | Un `form` o `text` validado → preflight version/help de cada rol con su entorno explícito y D174. Devuelve informes saneados e indicadores de que no se hizo inferencia ni se verificaron efectos internos. No guarda ni activa. |
| `POST /preview` | Un `form` JSON o `text` TOML, DRAFT/VALIDATED, versión/hashes base, elección de cambio externo y motivo → candidato TOML, diff, revisión, impacto y hash exacto T004. |
| `POST /save` | Mismo candidato/base y hash de preview, más `Idempotency-Key` → intención y guardado T004. Replay conserva id/resultado; otra petición con esa clave rechaza. No activa. |
| `POST /activation/preview` | Referencia global guardada exacta, CAS y motivo → impacto y hash separado; exige VALIDATED y guardias T004 de trabajo pendiente. |
| `POST /activate` | Referencia, hash exacto e `Idempotency-Key` → `RESTART_REQUIRED`. Nunca promueve dentro de la petición. |
| `POST /cancel` | Id pendiente, CAS global, motivo e `Idempotency-Key` → cancelación auditada T004. No cambia la configuración ya cargada del proceso. |
| `GET /operations/{id}` | Identidad, estado y resultado durable de la operación; no expone el journal de candidatos. |
| `POST /operations/{id}/recovery/preview` | Observaciones por hash de bytes base/candidatos y hash de conciliación T004; bytes desconocidos bloquean. |
| `POST /operations/{id}/recovery/confirm` | Hash exacto y declaración explícita `writers_stopped` → terminar la misma intención, con auditoría/replay T004. No se presume parada por timeout. |

Los DTO de entrada rechazan claves desconocidas y coerciones de booleanos/versiones. `text` y `form` son
excluyentes. El formulario añade `format = "local-config-9"` y `service.state_dir` fijado solo cuando faltan;
un valor diferente no traslada datos y se rechaza por T004. La serialización trata cadenas como valores,
no como sintaxis TOML. Se conservan límites de 64 KiB, claves estrictas, ausencia de secretos reconocibles,
validación de identidad Git, entorno CLI explícito, raíces/techo de bootstrap y catálogos/presets opcionales.
No se exige composición, receta ni perfil de stack. Guardar DRAFT no habilita activación.

Esta entrega configura solo la global inicial. Bases con registro previo o autoridad legacy rechazan edición
inicial con `configuration_import_required`: conversión/importación por conjunto en T011. La global v9 cargada
no se presenta como registro legacy utilizable; `registrable` permanece cerrado para v9 hasta conectar altas/
perfiles propios en T007–T009. No se fabrican proyectos/perfiles ejecutables para habilitar esa puerta.

## Arranque, reinicio y exclusión

`serve` recibe `--configuration-dir` y `--state-dir`; sin opciones usa `configuration` bajo el directorio de
la base y ese directorio como estado. `scripts/start` transmite las rutas del recibo, incluso sin TOML.
`--config` conserva una entrada legacy explícita; no se convierte ni reescribe su original. El modo embebido
`create_app(..., configuration_dir=..., state_dir=..., config_source=...)` habilita esta integración; sin esos
parámetros conserva la composición explícita anterior y la exportación de OpenAPI sin conexión a SQLite.

El preflight del wrapper sigue validando esquema en consulta, sin migrar, y deja la validación TOML al servicio.
Ausencia, sintaxis inválida, ruta inaccesible o autoridad incierta conservan sesión/editor y cierran trabajo.
No se sustituyen archivos inválidos por ejemplos. La validación de composición/runtime y su preflight también
conservan el editor ante rechazo; archivos inaccesibles mantienen visibles sus referencias durables de SQLite. D040 se resuelve primero: no crea directorios operativos,
lee TOML original, detecta clientes, promueve pendientes o permite mutaciones en la consulta restaurada.

Con referencia activa se lee/verifica el TOML inmutable, se valida y compone una global v9 nativa. La lectura
legacy sigue rechazando v9: no se autoriza una copia de trabajo por existir. Pendiente global se promueve
por `promote_pending` al reiniciar, con el mismo id durable; fallo conserva referencia anterior/pendiente y
bloqueo. Cancelar no abre un proceso que no cargó la activa. Las versiones históricas no se modifican.

HTTP rechaza mutaciones gestionadas sin READY antes de resolver clientes o ejecutar servicios. Además,
`SQLiteManagedRepository._write` permite inyectar la puerta de autoridad: se revalida bajo su barrera SQLite,
con la misma sesión/conexión, cerrando la carrera entre comprobar HTTP y una activación concurrente. El
repositorio de configuración usa su carril T004; preferencias usa otro para poder cambiar idioma durante
setup/reinicio. Sin autoridad, arranque tampoco concilia altas/preparaciones ni inicia supervisor consumidor.
Cambios externos de copia o deriva inmutable bloquean antes de escrituras, sin hot reload ni fallback.

No hay modelos ni migración nuevos: sigue `0026_configuration` y el diagrama de datos T004. Las constantes
operativas del compositor admiten v9 solo por la entrada interna validada del editor; las formas de carga y
huellas 1–8 no cambian. Recetas v9 conservan la generación v2, sin modificar módulos/recibos congelados.

## Validación y límites

Pruebas nuevas: `tests/product/test_configuration_api.py`, con SQLite/archivos temporales, TestClient y clientes
sintéticos. Cubren primer uso sin procesos, guardado/replay, activación/reinicio, lectura de operaciones,
Host/Origin/cross-site/CSRF/sesión, detección por PATH acotado, preflight real contra script falso que solo admite
version/help, borrador, stale CAS, reutilización de clave, candidato manual/formulario, almacenamiento fijo,
legacy/importación, preferencias en/es, edición externa, deriva inmutable, promoción fallida, conciliación
con declaración de parada, configuración inválida y restore sin originales. Las pruebas de `scripts/start`
se actualizan para fijar directorios y entregar el TOML inválido al servicio conservando schema gate/señales.

La primera pasada completa encontró una colisión entre el nombre nuevo `Activation` y la comprobación que
protege la retirada legacy (D161). Se prefijan los nuevos DTO con `Configuration`; se conserva la comprobación
anterior. Comparación estructural de OpenAPI: **11 rutas y 16 esquemas nuevos; ninguna ruta ni esquema anterior
cambia de contenido**. La regeneración mueve parte del texto del archivo generado, sin cambiar su contrato previo.

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: **1875 correctos y 29 subtests**,
  dos opt-in omitidas. Avisos conocidos de TestClient y ZIP duplicado deliberado en prueba negativa.
- Refuerzo final de composición inválida y lectura con permisos ajenos: suite focalizada de configuración API,
  TOML, runtime/API gestionada, arranque, retirada legacy y catálogo: **123 correctos**. Incluye los **16 casos
  nuevos** de API; la pasada completa anterior contenía 14 de esos casos. Sin fallos pendientes.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**.
- `node --test frontend/tests/*.test.mjs`: **119 correctos**.
- OpenAPI exportado y tipos regenerados; `npm --prefix frontend run check` y `npm --prefix frontend run build`,
  correctos. Build con aviso conocido de chunks grandes; sin cambios visuales ni QA de navegador.
- Alembic `upgrade head` y `check` en SQLite temporal: **sin diferencias con metadata**; no bases operativas.
- Parsers: **13 fases, ocho criterios P013, quince tareas únicas y 222 decisiones consecutivas con estado**.
  Enlaces/anclas, fences y presupuestos comprobados. Cuerpos D001–D221 conservados; diagramas Mermaid sin cambios.
- `git diff --check` correcto; diff de producto/documentación y paridad estructural OpenAPI revisados.
  Archivos originales de fases cerradas/candidatos fuera del diff.

Sin instalaciones reales, servicios en puertos, navegador/QA visual, harness sobre este checkout, agentes/
proveedores/smokes, acceso a bases privadas, red o configuración global del equipo. No se construye/verifica
un wheel nuevo ni se modifica candidato/paquete/snapshots P001–P012/D214. La evidencia instalada/visual es T012/
T013, no se atribuye a TestClient. UI T006, altas/perfiles/recibos T007–T009 e importación/backup T011 pendientes.
Sin push, CI remota, tag o publicación. Commit local solicitado en inglés; siguiente **P013-T006**.
