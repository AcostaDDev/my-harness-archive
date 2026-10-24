# P012-T008 — Corrección del lector de listas de valores del preflight CLI

Fecha: 2026-10-24. **Estado: implementada y verificada offline; T002 sigue parcial y detenida.**
Decisión: [D187](../DECISIONS.md#d187--p012-t008-listas-multilínea-en-el-preflight-cli).
[Tarea](../NEXT_STEPS.md#p012-t008--corregir-choices-multilínea-del-preflight-cli),
[hallazgo D186](P012-T002_INCORPORACION_REAL.md#8-segunda-parada-lector-de-choices-corta-en-el-salto-de-línea).
Base de trabajo: `2abf27866cc0c6da185a41444bf8b69c892e4997`, commit del registro de T002 pedido por el usuario
(`docs: record P012 validation setup and preflight blocker`). La continuación autoriza esta corrección manual
acotada; no se interpreta como reanudación del tramo real ni se ejecutan CLI de proveedores.

## 1. Causa y comportamiento corregido

`unsupported_values` reconocía la etiqueta `choices`/`possible values`, pero capturaba sus valores solo hasta
el primer salto de línea. La lista sintética con `dontAsk` en una continuación fallaba como valor ausente;
la misma lista en una línea pasaba. Una captura indiscriminada del resto de la línea también podía aceptar
una mención al valor en prosa posterior a la lista.

Se conserva el límite por opción que ya proporcionan los tokens de flags. Dentro de esa sección se lee una
**lista de valores separados por comas**, con valores simples o entre comillas simples/dobles y continuaciones
LF/CRLF. Cada valor debe acabar ante coma, cierre de paréntesis/corchete, fin de línea o sección; la lectura
solo continúa a otro valor mediante una coma. No se buscan palabras arbitrarias en el resto de la descripción.

- Una lista envuelta válida pasa igual que la misma lista en una línea, también con valores que incluyen guiones.
- Un valor realmente ausente, un nombre con sufijo diferente o un valor que solo figura en otra opción/prosa
  sigue rechazado con `unsupported_values`. Una lista anunciada sin valores reconocibles tampoco aporta el
  valor requerido; sin anuncio de lista no se inventa una observación nueva.
- No cambian `VALUES`, flags requeridos, mínimos, modelos, esfuerzo, permisos, controles del argv, códigos de
  diagnóstico, formato TOML, codec, API o esquema. `cli-14` y `cli-capabilities-1` mantienen sus identificadores;
  la huella derivada de su contenido cambia automáticamente como exige D174.

## 2. Cambios y procedencia de las pruebas

| Archivo | Cambio |
|---|---|
| `src/harness_local/adapters/cli_diagnostics.py` | Captura de lista delimitada en lugar de captura de la primera línea |
| `tests/product/test_cli_diagnostics.py` | 25 regresiones nuevas y dos modos de ayuda del cliente falso existente |
| [Flujo CLI](../flows/cli-compatibility.md) | Explicación del ámbito de la lista y de las continuaciones, sin cambiar secuencia o guardias |
| STATE, NEXT_STEPS, ROADMAP, DECISIONS | T008 completada; T002 pendiente de paquete/base y consentimiento nuevos |

Las ayudas de los tests son **sintéticas**, escritas dentro de los tests; no se leen las CLI instaladas ni se
copia ayuda real a fixtures públicos. Los ejecutables falsos aceptan solo version/help, registran sus argv y
no invocan modelos. Las pruebas integradas verifican tanto preflight lector como `diagnose`, éxito de la lista
envuelta, rechazo de la que excluye `dontAsk`, configuración inmutable y ausencia de salida privada en el informe.
Los tests puros cubren LF/CRLF, comillas, ambos proveedores, paréntesis/corchetes, lista sin envoltorio, guiones,
prosa posterior, coincidencia exacta y separación de opciones.

## 3. Validación ejecutada

| Comprobación | Resultado |
|---|---|
| Nuevas regresiones contra el código anterior, selección de 24 casos | **15 fallan y 9 pasan**: reproduce el truncamiento, la falsa aceptación de prosa y ambos diagnósticos integrados positivos |
| Selección final de las 25 regresiones tras la corrección | **25 passed**, 0,27 s |
| Cinco módulos de diagnóstico/compatibilidad/descubrimiento/transporte/memoria | **229 passed**, 16,36 s, cuatro avisos existentes FastAPI/httpx |
| Comprobaciones documentales y diff | 12 fases, 8 tareas, 187 decisiones, 565 enlaces/anclas válidos; hashes y conservación correctos; `git diff --check` sin errores |

Comando de regresión final:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 4 tests/product/test_cli_diagnostics.py tests/product/test_cli_baseline.py tests/product/test_cli_discovery.py tests/product/test_cli_agents.py tests/product/test_cli_memory.py
```

El aviso existente es `StarletteDeprecationWarning` del TestClient FastAPI/httpx; no hay fallo ni instalación.
No se amplía a la suite completa después del pase dirigido: el cambio solo toca el lector de ayuda y su cobertura;
no cambia UI, API, esquema o dependencias. No se ejecutan Node, tipos/build, Alembic, wheel/sdist,
`check_distribution`, servicios, navegador, smokes o CLI/proveedores reales. Las pruebas trabajan con procesos,
Git/SQLite temporales y clientes falsos; no operan este repositorio como proyecto del harness.

## 4. Identidad y conservación

| Contenido | SHA-256 |
|---|---|
| Política anterior derivada de la base de trabajo | `d7de794cd0799ac87ab6213249c102799aba70db0f495644a6c95c8b31bfb3b6` |
| Política corregida derivada de las fuentes actuales | `1156d0c9c8ad969c6762653eadadb5626c3d8f203d6e7ce821611d6286cc79d5` |
| `cli_diagnostics.py` corregido | `c8f1adb4beb3f82729070241711de4b6b257c5a60587666c852eafe35546e1c9` |
| `test_cli_diagnostics.py` actualizado | `c2cab767c24632eacb75c103a8ed1577d6126273fde3a628901a9f10e0d2efae` |

La política incluye hashes de las fuentes del transporte/diagnóstico: cambiarla no reescribe snapshots ni autoriza
usar observaciones de un job anterior. No se cambia manualmente el hash ni el contenido de jobs históricos.
No se accede ni se modifica el área operativa privada de P012 en T008; el wheel instalado allí conserva la versión
anterior del lector. Tampoco se opera P009/ReferenceProject ni se toca configuración global.
T001, registro de T002, manifests/locks ya registrados, D001–D186, archivos previos, ayudas originales y fuentes
congeladas de recetas permanecen intactos. No hay modelos/migraciones; DDBB-DIAGRAM sin cambios.

## 5. Propuesta concreta de continuación de T002, sin ejecutar

La corrección sintética no demuestra que el Claude instalado pase el preflight real ni que la incorporación
funcione. La siguiente tarea sigue siendo **T002**, que necesita consentimiento nuevo después de D186.
Antes de pedir ese relanzamiento, esta entrega deja concretos sus efectos y límites:

1. Identificar un **commit nuevo que contenga T008** y comprobar sus fuentes contra los hashes de §4. El commit
   actual de base no contiene la corrección; no se atribuye todavía hash de wheel ni commit final a T008.
2. Conservar por bytes `AREA/dist`, `AREA/venv`, fixture B y evidencia anterior. Proponer destinos nuevos
   **`AREA/dist-t008` y `AREA/venv-t008`**, dentro del área elegida en T001, sin enlaces ni contenido previo.
   No se crean en esta tarea. Es la enmienda de base/rutas que debe cubrir el consentimiento de continuación.
3. Bajo esa autorización, construir/verificar offline desde el commit nuevo, con las mismas toolchain/cachés,
   `TMPDIR=AREA/tmp`, npmrc vacíos y sin descargas. El verificador usa sus CLI falsas y puertos efímeros de loopback.

```sh
# Guion futuro; AREA es $HOME/Documents/harness-validation/p012-20261024.
UV_CACHE_DIR=.local/uv-cache TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist-t008"
UV_CACHE_DIR=.local/uv-cache TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist-t008"
```

4. Registrar hashes completos del wheel/sdist/pylock/SHA256SUMS, comprobarlos e instalar el wheel en el venv nuevo
   Python 3.14.4 con `uv pip sync --offline` desde el pylock y luego `uv pip install --offline --no-deps` del wheel.
   Verificar la huella de política nueva. Sin reutilizar la observación del preflight fallido.
5. Revalidar identidades/versiones y configuración completa antes de `check-config --preflight` con el ejecutable
   de `venv-t008`, siempre fuera del checkout. Las dos CLI han de pasar bajo su contrato conocido; si no, parar
   al primer fallo, conservar evidencia y no cambiar permisos, modelos o proveedor.
6. Contrastar el fixture con su baseline `f6a2d9d`, los [17 wheels verificados](P012-T002_WHEELS_VERIFICADOS.sha256)
   y las ocho comprobaciones exigidas antes del registro. Crear SQLite nueva solo si aún no existe; servicio en
   8024 bajo las guardias de T001. El registro B, incorporación y tarea continúan desde UI según T001/T002,
   sin rehacer ni reparar resultados de agentes (no hay ninguno en el tramo parcial).

Se mantienen área/raíz, fixture, autor, idiomas, Claude `sonnet`/low, catálogo único Codex `gpt-6-luna`/low y techo
**12 Claude + 3 Codex**, con **0/0** invocaciones de modelo consumidas y parada al primer fallo. No se autoriza red
adicional, T003/T004, limpieza persistente, tags/push/publicación ni configuración global. T008 no inicia ese guion,
no reconstruye el wheel operativo y no repite el preflight real para presentar éxito anticipado.
