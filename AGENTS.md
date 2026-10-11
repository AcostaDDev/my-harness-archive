# Instrucciones de desarrollo — my_harness

## Contexto y modo de trabajo

Este repositorio desarrolla Harness Local, una aplicación local de orquestación con interfaz web. El desarrollo de este producto es manual, asistido por Codex y Claude Code. Ambos pueden implementar código cuando el usuario lo pide. No confundir esta forma de desarrollar con los roles Codex revisor / Claude ejecutor que tendrá el producto.

No ejecutar el harness para desarrollar este repositorio ni lanzar sesiones de otros agentes automáticamente. El usuario coordina las herramientas.

## Contexto duradero

Al iniciar, leer `docs/STATE.md` y `docs/NEXT_STEPS.md`. Consultar las secciones relevantes de:

- `docs/01-especificacion-harness-local.md`: alcance y diseño aceptados como base.
- `docs/02-backlog-y-plan-de-desarrollo.md`: hitos y criterios de aceptación.
- `docs/DECISIONS.md`: decisiones y aclaraciones operativas.

Si se encuentra una contradicción material, señalarla antes de cambiar el diseño. Resolver detalles reversibles de implementación con criterio, sin pedir confirmación rutinaria.

## Referencia anterior

`$HOME/Documents/projects/reference_project/.harness` es referencia de lectura. No modificar ReferenceProject, ejecutar su harness ni lanzar allí agentes, instalaciones o tests. Sus reglas de producto no se trasladan a este repositorio. No copiar runs reales, credenciales ni datos privados a fixtures; usar datos sintéticos.

## Arquitectura

- Núcleo Python independiente de web, proveedores y stacks de proyectos.
- FastAPI/Pydantic/Uvicorn, SQLite/SQLAlchemy/Alembic, React/TypeScript/Vite.
- Ejecución nativa local; sin Celery, broker ni Docker obligatorio para el servicio en el MVP.
- CLI primero; App Server / Agent SDK solo tras comprobar compatibilidad y autenticación.
- Versiones y comandos reales se fijan al crear el esqueleto; no documentar scripts inexistentes como disponibles.
- Detalles específicos de Django/Docker pertenecen a perfiles, no al núcleo.

## Invariantes

- Una sola ejecución escritora por checkout.
- Contratos, prompts, políticas y metadatos congelados por intento.
- Historial de intentos conservado; reanudar trabajo no exige reanudar conversación.
- Permisos de archivos, herramientas, red y decisiones de producto separados.
- Validación y revisión vinculadas al contenido exacto antes del commit.
- Fallos no provocan fallback de modelo ni llamadas adicionales silenciosas.
- Datos solicitados, observados, estimados y ausentes se distinguen.
- Estado operativo gestionado en SQLite; importación legacy de lectura sin doble autoridad.

## Trabajo y verificación

Completar una tarea acotada cada vez con comprobaciones proporcionales. Se permiten edición local, fixtures sintéticos y tests offline pertinentes a la tarea. No lanzar smoke tests con proveedores, compras, publicación, push ni acciones externas sin autorización explícita. No modificar configuración global del usuario.

No descartar cambios ajenos. Si otra sesión trabaja en el mismo checkout, revisar el estado antes de editar y no asumir propiedad de sus cambios. No hacer commits automáticamente salvo que el usuario los pida.

Antes de dar una tarea por terminada: verificar criterios, ejecutar checks disponibles relevantes, revisar el diff y actualizar `docs/STATE.md` y `docs/NEXT_STEPS.md`. Registrar decisiones duraderas en `docs/DECISIONS.md`. Indicar qué se probó, qué no y la siguiente tarea concreta. Nunca marcar como implementado algo que solo está diseñado.

## Comandos actuales

H0.1 completado: inventario y fixtures sintéticos. Comprobación offline ligera,
solo biblioteca estándar, desde la raíz:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Todavía no hay aplicación, dependencias del producto ni comandos de build.
Al incorporar código ejecutable del producto, añadir aquí y al README los comandos comprobados.
