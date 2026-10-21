# P009-T018 — El recibo de preparación sobrevive a un reinicio

Fecha: 2026-10-21. Decisión [D130](../DECISIONS.md#d130--p009-t018-el-recibo-de-preparación-compara-el-inodo-no-el-dispositivo).
Origen: segunda sesión de T008, parada antes de encolar ([evidencia §7](P009-T008_PILOTO_CODEX_CODEX.md#7-reanudación-2026-10-21-sesión-2-parada-antes-de-encolar)).
Sin proveedores ni piloto.

## 1. Defecto

El recibo de `django-recipe-1` (D119) guarda la identidad del checkout y de `.venv` como `{device, inode}`
(`services/project_creation.identity`), y `verify_receipt` la comparaba entera. macOS renumera `st_dev` al remontar
un volumen, por ejemplo tras un reinicio, aunque el inodo y los bytes no cambien. Tras reiniciar el Mac, el hijo del
piloto pasó de 16777230 a 16777233. La admisión de tareas y checks y cada comando nativo respondían
`preparation_required`, y el producto no tiene ninguna acción para volver a acreditar el recibo. Bloqueaba T008–T012.

## 2. Decisión: comparar el inodo

Decisión del usuario: la verificación del recibo compara el inodo del checkout y de `.venv`
(`same_directory` en `adapters/preparation.py`). No compara el dispositivo. Lo demás no cambia:

- Archivos protegidos, todos los archivos y enlaces de `.venv`, el intérprete base y los ejecutables se siguen
  verificando byte a byte. Un directorio distinto en la misma ruta tiene otro inodo y se rechaza.
- Los recibos guardan el dispositivo que registraron. No se reescriben, su hash (`project_environment_sha256`) no
  cambia, y el del piloto vuelve a valer sin tocar la SQLite.
- Alcance acotado a `verify_receipt`, que es el único punto que compara un recibo ya COMPLETED: admisión,
  lectura de la UI y `PreparedCommandRunner`. Las comprobaciones dentro de una operación en curso (pasos de la
  preparación, creación de hijos y autoridad de la carpeta de proyectos) siguen comparando `{device, inode}`.

## 3. Límite que queda

Tras un reinicio, la carpeta de proyectos guardada responde `target_identity_changed` al crear otro proyecto, y una
creación o preparación que estuviera en curso queda bloqueada o en recuperación. Ninguna de las dos afecta a
T008–T012, que no crean ni preparan. No se corrige aquí: si hace falta, será otra tarea.

## 4. Verificación

- Regresión en `test_project_preparation.py`: con `st_dev` renumerado en la lectura actual, el recibo vale, la UI
  muestra el proyecto preparado y una tarea se admite. Con otro inodo, del checkout o de `.venv`, y los mismos
  bytes, se rechaza. Un ejecutable cambiado se sigue rechazando. Sin la corrección, la prueba falla.
- Suite pytest completa: 1576 pasan y 1 se omite (Django real), en 3 min 51 s. unittest: 12 OK. Alembic check
  no procede (sin modelos ni migraciones).
- **No probado aquí:** el recibo real del piloto con el wheel nuevo. Se comprueba al reanudar T008.
