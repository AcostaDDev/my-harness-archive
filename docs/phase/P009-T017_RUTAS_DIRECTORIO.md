# P009-T017 — Rutas de directorio en el contrato de tarea

Fecha: 2026-10-21. Decisión [D129](../DECISIONS.md#d129--p009-t017-una-ruta-de-directorio-se-congela-como-dir).
Origen: parada de T008 ([evidencia](P009-T008_PILOTO_CODEX_CODEX.md), D128). Sin proveedores ni piloto.

## 1. Defecto

`task_contract` aceptaba `core/` como ruta relativa y la congelaba tal cual. `check_paths` y las concesiones de
ficheros (`permissions.allowed`) emparejan con `fnmatchcase`, que no casa ningún archivo con `core/`. Así, una entrada
de directorio en `allowed_paths` no permitía nada, y en `forbidden_paths` no prohibía nada. El fallo aparecía
después de ejecutar y revisar.

## 2. Decisión: normalizar al congelar

Una entrada que termina en `/` se congela como `dir/**` en `allowed_paths` y en `forbidden_paths`
(`directory_patterns` en `core/engine/contracts.py`). Se descarta rechazarla: el NEXT_STEPS del hijo, redactado por el
revisor en la definición, usa `core/`. Un planificador que lo copie pararía el run sin ejecutar nada, y
corregirlo exigiría editar los documentos del hijo.

- **Un único significado.** El ejecutor, el revisor, la política de rutas, las concesiones de ficheros y la
  comprobación de contradicciones leen el mismo contrato congelado. Ninguno reinterpreta `dir/` por su cuenta.
- **Contradicciones antes del escritor.** Con `core/private/` prohibido, permitir `core/private/key.py` se rechaza al
  congelar, igual que con `core/private/**`.
- **Idempotente.** `dir/**` no cambia. Un contrato del servidor (reconciliación), recongelado en `start`, sigue
  siendo idéntico. No se deduplica, para no alterar listas que ya traían repetidos.
- **Sin cambios en lo existente.** Las rutas exactas, los globs y una entrada sin barra (`core`) se congelan igual
  que antes. `matches` no cambia, así que los patrones de perfiles y TOML se leen como siempre.
- **Contratos ya congelados.** Conservan bytes, hashes y lectura literal. Su semántica no cambia, así que no hace
  falta versionar el motor ni el adaptador (`cli-13` sigue vigente). Los jobs pendientes no quedan en cuarentena.
- **Orientación al planificador.** `plan-task` pide `dir/**` y explica la normalización. La descripción de
  `allowed_paths` en el esquema del planificador lo repite. La plantilla integrada cambia de hash (`builtin-1:<sha>`),
  y los catálogos congelados en runs anteriores se conservan.

## 3. Consumidores contrastados

| Consumidor | Efecto |
|---|---|
| `check_paths` (evidencia, reanudación) | lee el contrato congelado; `core/**` cubre `core/models.py` |
| `permissions.allowed` (concesiones de ficheros) | igual; una concesión bajo `dir/` ya puede caer dentro del contrato |
| contradicciones en `task_contract` | se evalúan después de normalizar |
| `harness_owned_paths` | añade sus prohibiciones después; no cambia |
| planificación determinista (`planning.py`) | las rutas entre comillas invertidas del NEXT_STEPS pasan por `task_contract` |
| reconciliación (`phases.py`) | rutas de documentos exactas; no cambia |
| ejecutor y revisor (prompts) | reciben `task_json` congelado, ya con `dir/**` |
| retry y vista del run (`allowed_paths` vacío = solo lectura) | no cambia: la normalización conserva la longitud de la lista |
| chat (`_run_evidence`) | muestra el contrato congelado |
| `scope_grants` del revisor | no amplían rutas: una petición no vacía impide la aceptación; sin cambios |

## 4. Run `fc340afb`

Decisión del usuario: no se revalida. Su contrato congelado mantiene `core/` con la lectura literal, así que
«Revalidar y revisar» volvería a parar por la política de rutas. Queda BLOCKED como evidencia de T008. El producto no
tiene una acción para descartar un run de tarea. Para reanudar T008 hay que dejar el hijo limpio en `d762e77`: el
arranque de un run rechaza cambios sin confirmar en v2. Después se encola P001-T001 de nuevo, con otra clave.

- Hay que retirar exactamente las ocho rutas del diff de `fc340afb` (§3 de la evidencia de T008), sin tocar
  `.venv`, TOML ni SQLite. Después hay que comprobar «Django preparado» en la UI.
- El run nuevo consume al menos 3 invocaciones (planificador, ejecutor, revisor) de las 4 que quedan en T008. Un ciclo
  REVISE añade 2 y supera el techo de 7. La autorización nueva debe decir si lo amplía o si se para.

## 5. Verificación

- Regresiones `tests/product/test_directory_paths.py` con el contrato y los ocho archivos de T008: `core/` se congela
  como `core/**` y cubre sus archivos. Un contrato congelado con la lectura anterior sigue marcando los seis de
  `core/`. Un directorio prohibido tiene precedencia, y su contradicción se rechaza al congelar. Las rutas exactas y
  los globs no cambian. Con planificador falso, `app/` llega a ACCEPTANCE_READY y el ejecutor y el revisor reciben
  `app/**`. Sin la corrección fallan 3 de los 5 tests.
- Ensayo Django (`test_django_journey.py`, variante sintética): el NEXT_STEPS y el planificador falso usan
  `templates/`, y cada contrato congelado lleva `templates/**`. La variante con Django real se omite sin wheels
  preparados, como siempre.
- Suite pytest completa: 1575 pasan y 1 se omite (Django real), en 3 min 47 s. unittest: 12 OK. Alembic check no
  procede (sin modelos ni migraciones). Frontend sin cambios.
- **No probado:** el planificador real ante la orientación nueva de `plan-task`, ni un wheel reconstruido. Las dos
  cosas quedan para la reanudación de T008.
