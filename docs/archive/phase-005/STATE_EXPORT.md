# Exportación mecánica de STATE/NEXT_STEPS

Entrega offline del 2026-10-13. Alcance: D033 punto 1 y especificación §7.
Decisión duradera: [D036](../../DECISIONS.md#d036--exportación-documental-separada-diff-confirmado-e-intención-de-commit-conciliable).
Git inicial limpio en `main`, `233cb51`.

## Resultado

El núcleo `core/engine/document_export.py` renderiza bloques JSON estables y un
diff completo de las dos rutas del contexto. Conserva bytes UTF-8 fuera de los
marcadores, incluidos CRLF, y rechaza marcadores malformados, enlaces, documentos
fuera de la base adoptada, rutas protegidas/sensibles y documentos de más de
512 KiB. Un documento sin bloque recibe uno al final; no se reescribe su prosa.

SQLite aporta fase/estado, última ejecución y aceptación de cada tarea,
aceptación con commit (incluido el run de procedencia), preguntas abiertas,
último check con su validación y lotes registrados. NEXT_STEPS incluye tareas sin
commit. Las exportaciones/eventos propios y el reloj actual se excluyen para que
el mismo estado genere los mismos bytes. El bloque es una proyección de lectura;
el plan/contrato humano fuera de él sigue siendo producto documental.

La revisión es humana y confirma todo el diff, incluidos los bytes exteriores
que se conservarán, los hashes y el fingerprint Git limpio. No utiliza un
planificador, ejecutor ni revisor de proveedor. Una deriva documental externa se
detiene con diagnóstico: revisar y adoptar mediante la reconciliación por hash
existente, o crear la tarea de reconciliación normal antes de volver a exportar.

## API y UI

- `GET /api/managed/phases/{id}/export`: diff, contenido completo, hashes,
  snapshot SQLite, HEAD/fingerprint/árbol/índice, versión y SHA-256 de preview.
- `POST` en la misma ruta: `expected_version`, `preview_sha256`, motivo,
  `confirmed: true`, `resume_operation_id` (null inicialmente) e Idempotency-Key.
- Previsualizar no cambia archivos, referencias, índice ni filas SQLite; la
  captura/seal Git puede escribir objetos sin referencias, como H2.4.
- Repetir la misma clave/cuerpo devuelve el mismo job, incluso después del commit
  o reinicio. Cuerpo diferente con la misma clave → 409.
- Guardia Host/Origin y `X-Harness-Local: 1`; los proyectos/contextos/escritores
  proceden del servidor. Sin escritor configurado → 409.
- En Documentos de la fase: previsualizar, revisar diff, motivo y confirmación.
  El consentimiento se limpia si cambia la versión/hash. Un diff vacío deshabilita
  el commit. La UI usa las solicitudes conservadas del cliente gestionado.
- Historial de fase: snapshot, intención, commit/árbol y resultado. Historial de
  runs: `document_export`, jobs y recuperación, sin acciones de ejecución/review.

## Efectos y recuperación

La exportación es separada del cierre. Se permite únicamente sobre la última fase
del checkout, también CLOSED/ABANDONED. Exige parada operativa sin jobs pendientes
y sin lote ACTIVE (revocarlo primero), documentos adoptados y Git limpio. No
modifica tags, definiciones, contratos ni preguntas. Un READY previo conserva su
historial pero queda obsoleto por los nuevos hashes/HEAD; cerrar lo rechaza.

La operación `document_export` vive en `phase_operations`, bajo un run/job y el
lock existentes; no hay tabla, migración, codec ni cola nueva. El supervisor fija
antes de efectos el CommitIntent H2.4 y reutiliza GitWorkspace/CAS. La fecha e
identidad del commit quedan congeladas en esa intención. Los resultados y hashes
adoptados se confirman con el evento y fin del job, después del commit verificado.

Ante caída: RECOVERY_REQUIRED conserva el lock; confirmar escritor detenido con
job/token/versión/evidencia libera la cuarentena. GET devuelve el diff original y
el id de operación pendiente; volver a confirmarlo con una clave nueva reencola
el mismo run y reutiliza exactamente su intención. No hay reanudación automática.
Cada archivo parcial debe tener su hash anterior o sellado; el árbol al completar
los bloques y el índice deben coincidir con los sellados. Un commit ya alcanzable
se concilia, sin duplicarlo. Una edición ajena permanece intacta.

## Verificación

`tests/product/test_document_export.py` caracteriza 32 casos con SQLite/Git
temporales, sin proveedores: determinismo, prosa/CRLF y marcadores; diff exacto,
adopción posterior, confirmación/versiones/hashes, guardias HTTP e idempotencia;
concurrencia; deriva antes de preview/admisión/ejecución y en otros documentos;
índice staged/untracked/rutas/enlaces; lote activo; READY obsoleto; exportar CLOSED
sin mover el tag y rechazar fases antiguas; caídas antes de escritura, entre los
documentos, después del commit y dentro de la transacción de adopción; preservar
ediciones externas posteriores a una caída.

Comandos desde la raíz:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test frontend/tests/managed-api.test.mjs
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
npm --prefix frontend run check
npm --prefix frontend run build
```

OpenAPI y tipos regenerados. `alembic check` sin operaciones nuevas sobre SQLite
temporal; esquema `0012_chat` conservado. Persiste el aviso Starlette/HTTPX.
Chrome sobre build compilado en `127.0.0.1:8021`, checkout/base nuevos bajo
`/private/tmp`: preview → confirmación → COMMITTED → preview vacío, prosa intacta,
base documental adoptada y ninguna invocación de agente. La recarga conserva el
resultado SQLite. Servidor/pestaña de prueba detenidos al terminar.

## Límites

Exclusión cooperativa contra escritores externos y comprobaciones entre efectos;
no se promete aislamiento físico ni atomicidad de los dos archivos. Un cambio
ajeno después del commit incierto requiere restauración manual de los bytes
sellados antes de adoptar; no se sobrescribe, fusiona ni revierte automáticamente.
Los temporales de una caída durante el propio rename pueden exigir diagnóstico
manual; no hay limpieza/retención automática. Documentos existentes UTF-8, 512 KiB
por documento; sin benchmark de grandes históricos. La última fase cerrada se
puede exportar antes de definir otra. No se instala ni inicia la fase siguiente.

Sin proveedores/smokes, red externa, login, ReferenceProject, configuración global,
colaboración automática, harness de desarrollo ni push. No se migra la SQLite de
trabajo. H4.2 queda siguiente y no se inicia.
