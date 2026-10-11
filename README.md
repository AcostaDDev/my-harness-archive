# my_harness — Harness Local

Aplicación local para configurar, ejecutar y observar un harness modular de desarrollo con agentes.
Estado actual: H0.1 completado (inventario y fixtures); implementación del producto pendiente.

## Documentación

- [Especificación](docs/01-especificacion-harness-local.md).
- [Backlog](docs/02-backlog-y-plan-de-desarrollo.md).
- [Decisiones, Celery y Docker](docs/DECISIONS.md).
- [Estado real](docs/STATE.md) y [siguiente tarea](docs/NEXT_STEPS.md).
- [Guía de inicio con Codex](docs/START_HERE.md).
- [Instrucción inicial ampliada](docs/03-instruccion-inicial-para-codex-y-claude.md).
- [Inventario de referencia](docs/discovery/BASELINE.md) y [formatos legacy](docs/discovery/LEGACY_FORMATS.md).
- [Fixtures sintéticos y límites de verificación](tests/fixtures/legacy/README.md).

`AGENTS.md` contiene las instrucciones de Codex; `CLAUDE.md` remite al mismo contrato para Claude Code. El desarrollo es manual y no utiliza el harness como orquestador.

## Ejecución prevista

Servicio Python nativo en el Mac, UI web y almacenamiento SQLite local. Sin Celery ni Docker obligatorio en el MVP. Docker podrá usarse en perfiles de proyectos que lo necesiten. Todavía no hay comandos de aplicación o build.

## Comprobación offline disponible

Desde la raíz, con Python y su biblioteca estándar, sin instalar dependencias:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Cuatro checks ligeros de los fixtures H0.1; no ejecutan el harness ni proveedores.
La siguiente tarea es H0.2, todavía pendiente.
