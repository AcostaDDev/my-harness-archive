# Supresión específica de confianza Codex por transporte (D068)

2026-10-14, Git inicialmente limpio sobre `1d2de43`. El usuario pide comprobar
el flujo hasta cerrarlo. Esta entrega resuelve el prerrequisito D067 y aplica
la corrección acotada antes de la matriz nueva D069.
[Procedencia y hashes](CODEX_TRUST_SUPPRESSION.json).

## Fuente del pin y condición exacta

La API pública de `openai/codex` resuelve `rust-v0.162.1` al objeto de etiqueta
`7a078f6bb4ce0dc2a81408b334ce52979d92c603`, cuyo commit es
`092d3acd6bec3e3a14bdc7e7a2810ab628ab759d`. La etiqueta es unsigned: no se
afirma verificación criptográfica de su firma. El nativo existente conserva
SHA-256 D059/D062 `74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0`
y contiene ese commit como literal en offset 187264787. Esto enlaza versión,
fuente y binario; no demuestra una build reproducible. No se ejecutó código
descargado ni se actualizó/instaló una CLI.

En [thread_processor.rs, líneas 1340–1414](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server/src/request_processors/thread_processor.rs#L1340)
el arranque escribe confianza únicamente si se cumplen las cuatro condiciones:

1. El cliente pidió un cwd explícito.
2. El proyecto efectivo tiene `trust_level` ausente.
3. La configuración no es projectless.
4. Los permisos efectivos, tras restricciones gestionadas, permiten escribir
   el cwd (o son Disabled/External).

El modo ephemeral no figura en esa guardia. El destino es el checkout Git
raíz, o cwd si no existe, y `set_project_trust_level` escribe en CODEX_HOME
mediante ConfigEditsBuilder/apply_blocking. El fallo de escritura incluso
provoca una recarga con confianza en memoria; no se usa ese fallo como remedio.

En [exec/src/lib.rs](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/exec/src/lib.rs#L537),
los overrides CLI se conservan en InProcessClientStartArgs (líneas 731–736).
El selector [ConfigToml::get_active_project](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/config/src/config_toml.rs#L907)
busca cwd antes que raíz Git. Una entrada explícita para el cwd elimina la
segunda condición, sin importar que su valor sea trusted o untrusted.

## Corrección mínima

Solo el ejecutor Codex 0.162.1 recibe `-c projects={"<checkout canónico>"={trust_level="untrusted"}}`.
Se elige untrusted para conservar desactivadas las capas de configuración/
hooks locales implícitas. Los permisos explícitos workspace-write, raíces D059,
red desactivada y aprobación never permanecen: el valor de confianza influye
en los defaults cuando faltan permisos, no reemplaza los permisos explícitos.
La confianza de repositorio del motor y la confianza de carga de configuración
de la CLI son controles distintos.

Se reemplaza la tabla `projects` mediante un único valor TOML. El
[parser del pin](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/config/src/overrides.rs#L18)
divide las claves por puntos sin interpretar comillas: usar una ruta entre
comillas en una clave dotted sería incorrecto, particularmente con puntos,
comillas o separadores en la ruta. La tabla inline conserva la ruta como clave
literal; tests cubren Unicode, comillas, backslash y salto de línea.

El transporte pasa a cli-9; la comparación existente pone jobs cli-8 y anteriores
en cuarentena antes del preflight, sin reescribir historia. Lectores Codex y
Claude conservan argv/entorno. local-config-2, esquema/codec/API/UI/dependencias,
modelos, esfuerzos, HOME/USER/auth y permisos no cambian. No se redirigen
CODEX_HOME ni credenciales, no se precrea/restaura confianza personal.

## Verificación y límites

**217 pytest pertinentes pasan**, incluidos los cuatro recorridos sintéticos
con memoria desactivada y la guardia nueva del escritor. Dos casos adicionales:
cuarentena cli-8 sin proceso y control omitido que falla una vez antes de editar.
El fixture nuevo se corrigió tras detectar proveedor equivocado y luego versión
preflight incoherente; los fallos iniciales no se atribuyen al producto.
Build frontend y wheel/sdist offline correctos; distribución instalada verifica
sesión/UI/API y tarea/commit/reinicio/restauración con proveedores falsos.
La primera comprobación de distribución fue bloqueada al hacer bind dentro del
sandbox; la repetición exterior autorizada pasa. pip install con resolver no
localiza un pin offline; pip sync --require-hashes instala los 18 pins desde
caché sin red. Diff/whitespace y composición TOML revisados.

Esta evidencia acredita la condición y la supresión específica en la fuente
del pin. La nueva matriz D069 comprobará efectos reales. No es una frontera OS
ni certificado de ausencia de toda escritura auxiliar. El pin inicializa su
SQLite auxiliar sin guardia ephemeral; logs/cachés/auth/refresh no se equiparan
a memoria automática ni se dan por ausentes. El comportamiento de claves
nuevas en el lector histórico 0.161.0 tampoco queda certificado por este ensayo.
El archivado y la continuidad documental por fase siguen siendo otro alcance.
