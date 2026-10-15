# Estado archivado — P002 Visor útil sin ejecutar agentes (antes H1)

Instantánea archivada en P008-T001 (D088): secciones de H1 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`.

## Verificación de H1.1

- `uv run --frozen --offline pytest -q`: 40 pruebas y 121 subtests correctos;
  14 casos nuevos de importación/CLI/migración y regresión completa de H0.
  Los 12 checks de biblioteca estándar continúan pasando. El nuevo núcleo
  se importa con `python -S` y conserva la frontera de dependencias.
- Cinco fixtures importados dos veces mediante CLI en SQLite sintética local:
  5 orígenes, 7 runs y 105 entradas (89 disponibles, 1 pendiente, 15 ausentes).
  Resumen idéntico tras reimportar/consultar.
- Comprobados hashes/payloads y mtime/bytes de origen sin cambios, ausencia/null/
  cero, campos futuros, JSON/UTF-8 inválidos, JSONL parcial, errores de lectura,
  enlaces no seguidos, desaparición de archivo y relectura tras completar JSON.
  La consulta no relee el origen ni oculta el carácter pendiente del índice.
- Upgrade/downgrade a H0.3/upgrade, reconstrucción de índice y `alembic check`
  correctos; claves foráneas/WAL y simulaciones conservadas. CLI exige migración
  explícita y rechaza SQLite dentro del checkout de origen antes de conectar.
- TypeScript y build Vite correctos; OpenAPI sigue sincronizado por la prueba
  existente. Regresión de API/UI estática y persistencia tras reinicio correctas
  mediante TestClient, sin arrancar servidores ni repetir el recorrido en navegador.
- Diff/whitespace revisados; decisión D012. Sin red, proveedores, agentes, harness,
  runs reales, acceso a ReferenceProject ni configuración global. Se usa `.venv` local;
  uv ignora el entorno activo externo. Persiste el aviso upstream HTTPX/Starlette.
- Límites: no hay watcher/SSE, navegación H1.2, entidades gestionadas, certificación
  de aceptación/commit, migración a modo gestionado ni prueba de escritores
  concurrentes. Solo fixtures sintéticos y relecturas manuales; H1.2 no iniciado.

## Verificación de H1.2

- `uv run --frozen --offline pytest -q`: 59 pruebas y 121 subtests correctos;
  19 casos nuevos, regresión completa H0/H1.1, núcleo con `python -S`, frontera
  de imports, OpenAPI sincronizado y checks de migración existentes correctos.
  Los 12 checks de biblioteca estándar continúan pasando sin dependencias.
- Cinco escenarios recorridos por HTTP: proyecto/fase/tarea/run/artefacto,
  paginación sin pérdidas ni duplicados, hash/contenido/mtime de copias sintéticas
  conservados. REVISE → ACCEPT, hallazgos, preguntas, stop operativo, revisión
  parcial y resultados ausentes se mantienen separados; READY no acredita cierre.
- Comprobados ausencia/null/cero, selección antigua ausente frente a request
  posterior, modelos reportados, duración al nivel del comando, logs/diffs UTF-8
  por tramos y archivo vacío. Truncamiento estructurado y límite de verificación
  explícitos; rutas desconocidas y parámetros fuera de límites rechazados.
- Cambios antes/durante lectura, desaparición, enlaces de archivo/directorio/raíz,
  FIFO y denegación local no sirven contenido nuevo ni cambian el juicio del agente.
  Consulta no reimporta; metadata/texto/JSONL no cargan cuerpos del índice al listar
  o servir bytes. Los payloads JSON estructurados se cargan por artefacto.
- OpenAPI/tipos regenerados, TypeScript y build Vite correctos. Chrome sobre UI
  compilada con SQLite/copias locales sintéticas: cinco escenarios, historial,
  revisión parcial, preguntas, telemetría, duración, documentos archivados,
  paginación de artefactos/log UTF-8 y cambio de hash visible sin bytes nuevos.
  Captura de UI inspeccionada; simulación H0.3 creada correctamente. Servicio detenido.
- Diff/whitespace revisados; decisión D013. Sin red externa, proveedores, agentes,
  harness, runs reales, acceso a ReferenceProject ni configuración global. uv sigue
  ignorando el entorno activo externo; persiste el aviso upstream HTTPX/Starlette.
- Límites: solo macOS actual y fixtures sintéticos; sin certificación frente a
  escritores concurrentes, pruebas de carga, otros sistemas ni proveedor real.
  Verificar cada tramo relee el archivo para su hash (máximo 64 MiB); no hay cache,
  watcher/SSE ni actualización automática. H1.3 no iniciado.

## Verificación de H1.3

- `uv run --frozen --offline pytest -q`: 80 pruebas y 121 subtests correctos;
  21 casos nuevos y regresión completa. Los 12 checks de biblioteca estándar,
  frontera de imports, OpenAPI/tipos, TypeScript y build Vite correctos.
- Cinco escenarios, lectura incremental sin releer disponibles idénticos,
  JSON/JSONL parcial/completado, cambios durante lectura, agrupación, desaparición,
  reaparición, raíz ausente/enlace, FIFO y diagnóstico local sin resultados inferidos.
- Persistencia opt-in, desactivación durante lectura, reconciliación antes de servir,
  actualización sin navegador y reinicio idempotente comprobados. Eventos e índice
  revierten juntos ante fallo; importaciones concurrentes idénticas publican una vez.
- Migración ida/vuelta con H1.2 y checks existentes conservan índice/simulaciones;
  `alembic check` correcto. SSE valida cursores/Last-Event-ID y recupera 10.000 filas
  por lotes sin huecos/duplicados; espera de cambio en vivo y cierre acotado correctos.
- Chrome con copias/base sintéticas en :8014: activar, partial → available sin recargar,
  selección conservada, hash nuevo en log desde byte 8192 reiniciado a byte 0,
  cerrar/abrir con actividad IDs 1–10 únicos y reconexión tras reinicio.
  Captura inspeccionada; apagado normal SIGTERM con SSE abierto y servicio detenido.
  :8013 ocupado no se tocó. Ctrl+C del ejecutor produjo cancelación, no certificó apagado.
- Diff/whitespace revisados; decisión D014. Sin agentes, harness, proveedores,
  runs reales, ReferenceProject ni configuración global. Consulta pública de documentación
  SSE; verificaciones offline. uv ignora el entorno externo; aviso HTTPX/Starlette sigue.
- Límites: macOS actual/un proceso, polling sin snapshot de varios archivos ni garantía
  de capturar versiones sobrescritas entre ciclos. Cache JSON/JSONL y feed sin retención;
  sin medición de memoria/latencia bajo carga. Restauraciones que reutilicen IDs exigen
  limpiar cursor local. No hay motor/entidades gestionadas; H2.1 no iniciado.
