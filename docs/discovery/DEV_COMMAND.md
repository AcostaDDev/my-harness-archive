# Comando único de desarrollo (`scripts/dev`)

Entregado y verificado el 2026-10-13. D053. Pedido por el usuario: un solo comando
que levante API y frontend actualizados, con migraciones. Decisiones del usuario:
modo desarrollo (API + Vite) y migración automática con backup previo.

## Uso

```sh
scripts/dev [--database /ruta/absoluta.sqlite3] [--config /ruta/harness-local.toml]
```

`scripts/dev` (sh) ejecuta `uv run --frozen --offline python scripts/dev.py`
con `UV_CACHE_DIR=.local/uv-cache`; `uv run` sincroniza `.venv` con `uv.lock`.
`scripts/dev.py`:

1. `check_tools()` (nuevo `scripts/toolchain.py`, compartido con
   `build_distribution.py`): Node v24.15.0, npm 11.12.1, uv 0.12.19.
2. Puertos 8013 y 5173 libres en 127.0.0.1; si no, termina sin efectos.
3. `npm ci --offline --ignore-scripts` en `frontend/` solo si falta
   `node_modules` o cambió el SHA-256 de `package-lock.json` (sello en
   `.local/dev/frontend-lock.sha256`).
4. `prepare_database` (nuevo `storage/migrate.py`, ver abajo).
5. Con `--config`, `load_local_config` valida el TOML antes de lanzar nada;
   incompatible con `HARNESS_MANAGED_CONFIG`, igual que `serve --config`.
6. API: uvicorn `create_app` factory, un worker, loopback, sin proxy headers ni
   access log, `HARNESS_DATABASE_URL` explícita. Espera a que escuche.
7. UI: `npm --prefix frontend run dev` (Vite 127.0.0.1:5173, `strictPort`).
8. Muestra URLs y la ruta de la clave de sesión. Cada hijo vive en su propia
   sesión/grupo; Ctrl+C o TERM detienen ambos grupos (TERM, 10 s, KILL). Si un
   hijo termina, se detiene el otro y se devuelve su código.

## Migración con instantánea previa

`harness_local.storage.migrate.prepare_database(ruta, instantáneas)`:

- Base ausente: `initialize` (init-db), `created`.
- Revisión igual a la cabeza: no toca nada, `current`.
- Pendiente: comprueba que ningún propietario de job vivo use la base, copia
  con la API de backup de SQLite a `.local/backups/<base>-<rev>-<UTC>.sqlite3`
  (creación exclusiva, 0600, `integrity_check`) y escribe su manifiesto
  `premigration-1` (SHA-256, tamaño, revisiones). Después `upgrade head` y
  `require_schema`: `migrated`.
- Rechaza sin copiar ni modificar: revisión desconocida (base más nueva),
  restauración de consulta H5.2 (`user_version`), base sin `alembic_version`,
  enlace o no regular, servicio vivo.
- Si la migración falla, conserva base e instantánea y lo indica; no restaura ni
  borra automáticamente.

No se usa el bundle H5.2: exige el esquema actual (`_integrity`) y no puede copiar
una base pendiente de migrar. Las migraciones solo cambian SQLite; los artefactos
externos no se tocan. `serve`/`init-db` del paquete conservan D043 (sin
migración automática): este comando es de desarrollo.

## Corrección del proxy de Vite

Al probar el comando, el login desde la UI de desarrollo devolvía 403
`origin_rejected`. La abreviatura de cadena `"/api": "http://127.0.0.1:8013"`
implica en Vite 8.3.4 `changeOrigin: true`, que reescribe Host al destino; la
guardia H5.6 compara Origin (`:5173`) con Host (`:8013`). `vite.config.ts` usa
ahora la forma objeto con `changeOrigin: false`, como exigía H5.6. Afectaba al
flujo documentado de desarrollo desde antes de este cambio; el paquete H5.5 (un
solo puerto) no estaba afectado.

## Verificación

- `tests/product/test_dev_command.py`, 11 casos: base nueva, al día, migración
  real 0012 → 0013 con instantánea íntegra, manifiesto/hash y datos conservados;
  cuatro rechazos sin copia ni cambios (revisión futura, restauración, sin
  Alembic, escritor vivo); sello del lock; exclusión `--config`/entorno; grupos
  de procesos (con nietos) detenidos cuando un hijo termina y al pedir parada.
- Ejecución real fuera del sandbox: npm ci por sello ausente, base de desarrollo
  `current`, API y Vite arriba, UI 200, `/api/health` por el proxy 401 sin sesión.
  Tras la corrección: login, health y proyectos 200 por el proxy con Origin
  `:5173`. SIGINT al grupo en primer plano: cierre limpio, exit 0, puertos libres,
  clave retirada y sin procesos vite/uvicorn restantes.
- Regresión: 857 pytest y 121 subtests, 12 checks ligeros, 6 Node, `tsc` del
  frontend y `build_distribution.py` (con `toolchain.py`) a un directorio temporal.

Sin QA visual con navegador (bloqueo de herramienta previo); sin proveedores,
red, push ni cambios de esquema, codec, cli-4, OpenAPI o dependencias.
