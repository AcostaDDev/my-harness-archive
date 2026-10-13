# `--json-schema` tipado para el lector Claude (D058, `cli-6`) — entrega

Implementado y verificado offline el 2026-10-13. Origen: la combinación 3 de
la matriz D057 ([resultado](PROVIDER_MATRIX_RERUN.md)). Un planificador Claude
real devolvió listas y objetos como cadenas JSON
(`"allowed_paths": "[\"src/estimate.ts\"]"`) y el motor paró con
`Invalid task allowed_paths`.

## Causa

`cli-5` pasaba al lector Claude un `--json-schema` mínimo,
`{"type":"object","required":[…]}`, sin `properties`. D056 tipó el esquema que
va dentro del prompt, pero no el del argv. Sin tipos declarados, la CLI aceptó
texto en cada campo.

Lectura de cadenas del binario de Claude 2.1.296, sin ejecutarlo ni consumir
proveedor:

- `--json-schema` se usa como `input_schema` de la herramienta
  `StructuredOutput`. La raíz debe declarar `type: "object"`.
- Antes de lanzar, la CLI detecta esquemas insatisfacibles: un `required` no
  declarado con `additionalProperties: false`, `enum` o `const` incompatibles
  con el tipo, y límites cruzados.
- Admite tipos como lista (`["object","null"]`) y `nullable`.

El esquema del motor cumple estas condiciones por construcción: raíz objeto,
sin `additionalProperties: false`, sin `enum`, `const` ni límites.

## Qué cambia

- **Adaptador `cli-6`** (`adapters/cli_agents.py`). El `--json-schema` del
  lector Claude es `reader_schema(request)`:
  - El `output_schema` congelado en la instantánea del prompt del intento, el
    mismo que lee el agente. Se comprueba contra su `schema_sha256`; si falta
    o no coincide, el lanzamiento se rechaza antes de crear el proceso.
  - Sin instantánea (peticiones construidas fuera del motor), el esquema fijo
    del motor para el rol, `prompts.output_schema(role)`.
  - Se elimina la tabla `REQUIRED` de `cli-5`. Los obligatorios de chat, fase y
    bootstrap pasan a ser los del esquema del motor, que el motor ya exigía.
- **Sin cambios** en el resto del argv, en el escritor Claude ni en Codex. El
  lector Codex sigue sin `--output-schema`. La forma de ejemplo que el
  adaptador añade al prompt (`SHAPES`) se conserva.
- **Preflight** sin cambios: las flags exigidas (`--restricted`,
  `--json-schema`) son las mismas, y la ayuda caracterizada no cambia.

## Decisiones

- **`additionalProperties`: se conserva `true`**, como en el esquema del
  prompt. El argv y el prompt muestran un único contrato con un único hash.
  Los validadores del motor siguen siendo la autoridad: rechazan, por ejemplo,
  claves extra en `executor_selection`. Con `false`, la CLI rechazaría
  salidas con campos extra que el motor tolera, y el lector Claude se
  comportaría distinto del lector Codex, que no recibe esquema por argv.
- **El motor no normaliza listas u objetos serializados como texto.** Se
  siguen rechazando, como hasta ahora:
  - La causa se corrige en el transporte: con tipos, la propia CLI valida la
    forma antes de terminar.
  - A diferencia del argv de D056, una cadena JSON no es una forma
    equivalente natural del dato, sino un error de tipo.
  - `allowed_paths` y `forbidden_paths` delimitan permisos; no se reconstruyen
    a partir de texto libre.
  - Ningún lector Codex lo ha producido.
  - La salida original se conserva en el intento.

## Compatibilidad

- Un job pendiente congelado con `cli-5` no se ejecuta con el paquete nuevo:
  la composición local difiere de la congelada y entra en cuarentena
  (`RECOVERY_REQUIRED`) antes de cualquier lanzamiento, como en D052.
- Historiales, instantáneas de prompt, contratos y catálogos congelados no se
  reescriben. Esquema `0013_bootstrap`, codec 7, OpenAPI y UI sin cambios
  (solo comentarios). `local-config-2` sin cambios.

## Verificación offline

`tests/product/test_typed_json_schema.py` (6 casos):

- Para los cinco roles lectores, el `--json-schema` es el esquema tipado del
  motor, con tipo en cada obligatorio; Codex y el escritor Claude sin esquema.
- El esquema sale de la instantánea congelada (aunque difiera del actual);
  instantánea con hash incorrecto o sin esquema: lanzamiento rechazado.
- Recorrido Claude → Claude por el adaptador real: el argv de cada lector
  coincide con la instantánea de su intento, las listas llegan como listas y se
  llega a `ACCEPTANCE_READY`.
- **Reproducción de D057** con el esquema de `cli-5` y `PROBE_UNTYPED=text`:
  la CLI sintética devuelve listas y objetos como texto, el motor para en
  `planner` con `Invalid task allowed_paths`, el intento conserva el
  original, una sola invocación y el checkout intacto.
- La CLI sintética, como lector Claude, rechaza un `--json-schema` con
  obligatorios sin tipo (exit 1, sin salida).
- Un job congelado con `cli-5` entra en cuarentena sin lanzar procesos.

La CLI sintética (`tests/product/cli_process_probe.py`) exige ahora
propiedades tipadas al lector Claude y, sin tipos, emula la salida de D057.
Pruebas existentes actualizadas a `cli-6`; la de chat comprueba el esquema
tipado completo.

Regresión: 911 pytest y 121 subtests, 12 checks ligeros, 6 Node, `tsc`, build
y `alembic check`; aviso Starlette/HTTPX conocido; OpenAPI y tipos generados
sin cambios.

## Qué no se acredita

Que Claude 2.1.296 real devuelva un contrato válido con el esquema tipado.
Exige una ejecución con proveedor y consentimiento nuevo (combinaciones 3 y 4
de la matriz). Sin proveedores, red, push, configuración global ni ReferenceProject.
