# Estado de desarrollo

Actualizado: 2026-10-11.

## Existe

- Especificación y backlog aceptados por el usuario como base de desarrollo.
- Documentación de arranque, decisiones y contratos de trabajo para Codex/Claude Code.
- Carpeta raíz: `$HOME/Documents/projects/my_harness`.
- H0.1 completado: [inventario de procedencia y separación núcleo/perfil](discovery/BASELINE.md),
  [formatos y contratos mínimos legacy](discovery/LEGACY_FORMATS.md) y
  [manifiesto SHA-256](discovery/baseline.json) de 21 archivos de referencia.
- Cinco [escenarios sintéticos](../tests/fixtures/legacy/README.md): aceptación,
  REVISE, BLOCKED, interrupción y cierre. Incluyen historial, campos no registrados,
  archivos ausentes y una review deliberadamente parcial; cuatro snapshots de esquemas.
- Cuatro comprobaciones offline con biblioteca estándar en
  `tests/test_legacy_fixtures.py`; sin dependencias instaladas para esta entrega.

## Todavía no existe

Código del producto, importador, API, UI, base de datos, adaptadores ni infraestructura
instalada. H0.2 y H0.3 no se han iniciado; ninguna integración real se ha ejecutado.

## Trabajo activo

H0 — Contratos y prueba de viabilidad. H0.1 terminado. Próxima tarea: H0.2,
detallada en `NEXT_STEPS.md`, pendiente de una nueva sesión dirigida por el usuario.

## Verificación de H0.1

- `python3 -m unittest discover -s tests -p 'test_*.py' -v`: 4 checks correctos,
  ejecución inferior a 0,1 segundos en este equipo. Parseo/inventario, campos de
  contrato, identidades/referencias, coherencia de escenarios y hashes de esquemas.
- Los 21 archivos inventariados coinciden con el commit
  `5be3b8a1328f7725a0f81c98af4f365e3528a767`; cambios de aplicación del origen
  registrados por separado. Revisados los cambios locales de esta entrega.
- Inspección estática y comprobación offline; no se abrió ningún run real ni se
  ejecutaron harness, helpers, instalaciones o tests de ReferenceProject, ni proveedores.
- Límites: no es auditoría exhaustiva ni validador JSON Schema completo. No se
  probó importador, versiones/autenticación CLI, streaming robusto, commits ni cierre real.

## Coordinación

Desarrollo manual con el usuario. Una única sesión implementadora sobre los mismos archivos a la vez. La otra herramienta puede revisar una entrega terminada.
