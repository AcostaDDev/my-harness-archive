# Streams sintéticos — H0.2

Ocho muestras inventadas a partir de los envelopes documentados; ninguna procede
de una llamada real. [Manifest](manifest.json) indica proveedor, exit code
simulado, estado esperado y número de eventos completos. Son independientes de
los fixtures legacy H0.1 y no prueban qué emiten hoy las cuentas del usuario.

Por proveedor: éxito con campos y evento desconocidos, stream truncado, error
de autenticación sintético y salida sin terminal. Las muestras de éxito omiten
telemetría deliberadamente. Las truncadas terminan a mitad de JSON, sin newline.

La [sonda](../../stream_probe.py) recibe bytes incrementales, conserva registros
originales, cola parcial y campos desconocidos. `complete` solo certifica un fin
de stream conocido con exit code cero: no significa aceptación, commit ni
validación del contrato de respuesta. Codex requiere `turn.completed`; Claude,
`result` con `subtype: success` e `is_error: false`. Un mensaje de agente o un
evento futuro llamado «completed» no sustituyen esos terminales.

Un registro terminado malformado invalida la salida sin borrar eventos posteriores.
Una cola no decodificable al EOF se conserva como incompleta; sin newline no se
puede distinguir con certeza un corte de un JSON malformado. El EOF con JSON
válido se procesa. Un terminal duplicado es inválido. Un error o exit code
distinto de cero impide éxito; el diagnóstico de formato tiene prioridad cuando
ambos fallan. El lector no abre procesos/red ni reintenta o elige modelos.

Los checks también cubren UTF-8 dividido/cortado, JSON no objeto, constante NaN,
final sin newline, terminal seguido de error/corte, terminal Claude desconocido,
ausencia/null/cero observados y chunks de 1, 7 o todos los bytes.

Límites: sonda finita en memoria bajo `tests/`, no adaptador de producción,
validador JSON Schema completo, parser App Server/SDK ni lector acotado de logs.
La validación del resultado de tarea, denegaciones de herramientas y aislamiento
de stdout/stderr se resolverán al implementar los adaptadores; estos datos no
otorgan permisos. Ejecutar desde la raíz con el comando unittest del README.
