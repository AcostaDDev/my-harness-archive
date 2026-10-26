# P013-T003 — Arranque automatizado del paquete instalado

Fecha: 2026-10-26. Base: `fdd936a`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local
en inglés. **Implementada; orquestación y señales sintéticas. Recorrido instalado pendiente T012/T013.**
[D220](../DECISIONS.md#d220--p013-t003-arranque-instalado-y-exclusión-de-instancia),
[contrato T001 §3](P013-T001_CONTRATO.md#3-arranque-sesión-y-estados-globales),
[flujo actualizado](../flows/configuration-setup.md).

## Resultado y motivo

`scripts/start` permite arrancar la generación instalada sin activar venv ni componer comandos manuales.
Verifica referencia/recibo/paquete/venv mediante T002 y ejecuta el Python instalado con `-I -B -m harness_local.cli`,
desde datos privados fuera del checkout. No construye, reinstala, descarga ni migra. `scripts/dev` conserva
su recorrido de desarrollo. Los nuevos paquetes entregan `scripts/start`/`start.py` en `distribution-1`, con
SHA256SUMS; también funcionan con los demás módulos entregados, sin fuentes ni Node/Vite.

No se encontraron incongruencias pendientes de HITL tras contrastar T001, D051/D150/D216/D219, launcher y
runtime. T003 implementa orquestación: el asistente sin configuración pertenece expresamente a T005/T006
y la autoridad versionada a T004. Sin TOML se usa hoy la UI protegida de consulta existente, con aviso de esa
limitación y sin consumidor gestionado; no se fabrica un TOML, composición o autoridad ficticios.

## Uso y rutas

Ejemplos de operación futura, **no ejecutados contra una instalación real en esta sesión**:

```sh
scripts/start --help
scripts/start --install-dir '/ruta/Harness Local/installation'
/ruta/paquete/scripts/start --install-dir '/ruta/Harness Local/installation' \
  --database '/ruta/Harness Local/data/harness.sqlite3' \
  --config '/ruta/Harness Local/configuration/global.toml' \
  --port 8013 --temp-dir '/ruta/Harness Local/data/tmp'
```

El wrapper también queda en `installation/generations/gen-<id>/distribution/scripts/start`. Busca Python
local para bootstrap (prefiere `python3.14`; alternativa `python3` >=3.11), sin uv ni descarga; el servicio
siempre usa el intérprete del venv verificado. No añade comandos al PATH ni cambia la shell del usuario.

| Opción | Default y restricciones |
|---|---|
| `--install-dir` | Sugerencia T002 de macOS; debe contener una instalación READY íntegra. |
| `--database` | `data_dir/harness.sqlite3`; dentro de datos del recibo, sin enlaces/hardlinks/especiales. |
| `--config` | `config_dir/global.toml` si existe; override dentro de configuración del recibo. Explícita ausente falla. |
| `--port` | 8013; 1–65535, solo `127.0.0.1`, un proceso. Ocupado bloquea antes de inicializar. |
| `--temp-dir` | `data_dir/tmp`; privado, fuera de checkouts y sin contener DB ni solapar instalación/configuración. |

Rutas absolutas con espacios, normalizadas antes de leer TOML; las raíces del recibo deben seguir presentes,
privadas, sin enlaces/checkouts ni solapamientos. El recibo debe pertenecer al directorio de instalación:
no se relocan venvs con shebangs absolutos ni se adopta otra base/configuración por nombre. Los overrides
eligen archivos dentro de las raíces ya autorizadas, no trasladan datos. Directorios nuevos 0700 y archivos
creados por el comando con umask 077; no se sobrescribe TOML ni cambia permisos de originales existentes.
Se filtran variables HARNESS/PYTHON/UV/PIP/GIT y entornos virtuales heredados; el Python aislado no importa
el checkout/PYTHONPATH. TMPDIR/TMP/TEMP fijan temporales de sesión/Git en el ámbito elegido; agentes siguen
con su entorno explícito ya existente. Clave de login por el canal local existente, sin nuevos logs de secretos.

## Inicialización, reinicio y recuperación

1. Excluir otro arranque/instalación; validar generación y rutas, auxiliares y puerto.
2. Preflight con dependencias del paquete instalado: esquema SQLite en modo `ro`, sin alterar bytes/WAL;
   consulta D040 antes del TOML; si procede, parsear configuración sin preflight CLI ni inferencia.
3. Solo DB ausente sin `-wal`/`-shm`/`-journal`: `init-db` exclusivo. Fallo conserva diagnóstico/archivo;
   un reinicio no lo borra ni reintenta inicializar una base parcial como nueva.
4. `serve` mantiene su validación, sesión local/Host/Origin/CSRF y loopback. En consulta D040 no recibe
   configuración operativa. TOML ausente por defecto no habilita consumidores; TOML inválido bloquea.

Base antigua/desconocida bloquea, con diagnóstico para detener servicio/escritores y ejecutar **aparte**
`harness-local migrate --database RUTA --snapshots DIRECTORIO --writers-stopped` (D150). Este wrapper no
lo ejecuta ni deduce parada por ausencia de proceso/lock. No hay rollback/restauración/borrado automáticos.
Si otro proceso ocupa el puerto entre la comprobación y `serve`, uvicorn conserva su error de bind;
no se busca otro puerto silenciosamente ni se afirma que el precheck reserve el socket.

`.start.lock` y `.install.lock` son flock del SO, retenidos también por el hijo mediante descriptores
heredados. Evitan dos servicios de la instalación o una actualización cooperativa mientras vive el hijo,
incluso con SIGKILL del wrapper; los archivos se conservan, no son indicadores de PID ni se borran como
«stale». SIGINT/SIGTERM se reenvían al grupo del hijo, se espera su salida y luego se liberan descriptores.
Salida normal conserva código; señal del wrapper devuelve 128+señal. No se mata forzosamente al vencer un
temporizador ni se liberan guardias persistidas de jobs. Perder el servicio no prueba muerte de sus escritores.

## Validación y límites

Pruebas específicas en `tests/product/test_start_command.py`, junto con regresión de instalación,
launcher y migración instalada. Herramientas/intérprete/procesos sintéticos, archivos y SQLite temporales:
reinicio sin segunda inicialización, argv/rutas con espacios, cwd/entorno, permisos, errores de configuración,
esquema antiguo, consulta D040, puerto ocupado, enlaces/especiales, recibo/venv alterados, exclusión,
propagación de fallo, SIGINT/SIGTERM y wrapper muerto con hijo vivo. Preflight real de esquema/parser sobre
SQLite sintética sin arrancar API ni cliente. Los scripts entregados se invocan separados del checkout.

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0` sobre
  `test_start_command.py`, `test_install_command.py`, `test_launcher.py`, `test_installed_migration.py`
  y `test_documents.py`: **134 correctos**. Avisos existentes de FastAPI/TestClient y ZIP duplicado
  intencionado en una prueba negativa de distribución. Repetición final de `test_start_command.py`
  tras ajustar el aviso de arranque y limitar el log sintético a variables pertinentes: **26 correctos**.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**.
- Parsers documentales: 13 fases, ocho criterios P013, quince tareas únicas y 220 decisiones consecutivas
  con estado. **748 enlaces locales/anclas** comprobados en nueve documentos; fences y presupuestos
  correctos (STATE 17.062 bytes; NEXT_STEPS 21.383).
- `scripts/start --help`, `sh -n scripts/start` y `git diff --check`: correctos. Diff revisado;
  cuerpos D001–D219, base acumulada, archivos históricos y candidatos previos conservados.

No se ha instalado/construido un paquete real, abierto servicio/API/UI del producto, lanzado smoke/agentes/
proveedores, operado el harness sobre este repositorio ni usado bases privadas. Sin cambios de esquema,
OpenAPI/tipos, frontend o formatos TOML; no corresponden Alembic/tipos/build/Node en esta tarea. QA y primer
uso instalado quedan para T012/T013 con autorización propia. Candidatos/snapshots P011/P012/D214 intactos;
sin push, CI remota, tag, publicación o cambios globales. Siguiente: **P013-T004**.
