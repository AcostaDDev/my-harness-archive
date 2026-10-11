# Fixtures legacy sintéticos — H0.1

Cinco escenarios independientes del proyecto **Demo**, escrito desde cero.
IDs `P900`/`P901`, fechas de 2000, textos, mediciones y SHA ficticios no pertenecen
a ejecuciones ni a datos de ReferenceProject. No se copió ningún run o transcripción.
Los únicos archivos copiados son los cuatro esquemas estáticos en `schemas/`,
vinculados por SHA-256 a [baseline.json](../../../docs/discovery/baseline.json).
Los nombres de modelos se conservan como valores del formato legacy; no son
selecciones verificadas para el nuevo producto.

| Directorio | Qué representa | Qué no se debe inferir |
|---|---|---|
| `accepted/` | Tarea con `contract_source`, resultado/consumo reportados, validación correcta, review ACCEPT y STATE actualizado | ACCEPT por sí solo no prueba commit; el extracto Git auxiliar es ficción |
| `revise/` | Fallo de validación y REVISE en 00; nueva ejecución, validación correcta y ACCEPT en 01 | No sobrescribir el intento anterior ni restablecer el límite de revisiones |
| `blocked/` | Contrato antiguo sin elección, review BLOCKED por pregunta de producto; resume explícito seguido de error de executor y stop 01 | No confundir stop con review; selección de request posterior no reconstruye selección ausente del contrato |
| `interrupted/` | Dos runs alternativos: executor con eventos sin final; otra ejecución completa cuya review quedó como JSON parcial | No inventar stop, final ni veredicto; JSON parcial no demuestra error del modelo |
| `closed-phase/` | Reconciliación previa, READY/meta sobre HEAD ficticio y documentos posteriores a cierre con fase siguiente | READY no acredita cierre aplicado; el extracto Git/tag es evidencia auxiliar ficticia |

Cada escenario es una raíz de checkout imaginario. Los artefactos conservan
`.harness/runs/<timestamp>_<id>` y sus nombres originales; las referencias de
logs/resume se resuelven desde la raíz del escenario. Los archivos
`synthetic-git-log.txt` están fuera de los runs porque el motor **no** los produce.
No son repositorios Git reales y no deben usarse para probar commits/recovery.
Los comandos de validación son strings del proyecto imaginario: no se ejecutan.

`manifest.json` es metadato exclusivo de los fixtures, no formato legacy:

- `artifacts` enumera todos los archivos de los escenarios y su formato.
- `partial_json` identifica exactamente un archivo deliberadamente truncado:
  la review del segundo run de `interrupted/`.
- `absent_files` declara evidencias que no existen; su ausencia tiene significado.
- `absent_fields` diferencia un campo no escrito de uno escrito como null.
- `null_fields` señala consumo/duración no reportados en wrappers de usage.

El primer resultado de `blocked` no tiene consumo ni duración; su validación
carece de `duration_seconds`. El segundo resultado de ese caso es un error sin
telemetría. Ninguno equivale a cero. `accepted` y `revise` contienen mediciones
**reportadas ficticias**, no estimaciones ni observaciones de proveedores reales.

Comprobación desde la raíz de `my_harness`:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Cuatro checks con biblioteca estándar: inventario/parseo y campos de contrato,
referencias/identidades, coherencia de los cinco escenarios y hashes de esquemas.
No importan el motor, ejecutan fixtures, lanzan Git/subprocesos, usan red o
instalan dependencias. La comprobación de esquemas cubre campos superiores
requeridos/adicionales, enums e identidad; **no** es un validador JSON Schema
completo. No prueba el futuro importador ni parsers de streams truncados o CLI
actuales: eso sigue en H0.2/H1.1. Formatos y límites en
[LEGACY_FORMATS.md](../../../docs/discovery/LEGACY_FORMATS.md).
