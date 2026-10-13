# Siguiente tarea — H4.2 Bootstrap guiado

La exportación mecánica de STATE/NEXT_STEPS se completó offline el 2026-10-13
(D036, punto 1 de D033). Genera bloques delimitados desde SQLite, conserva la prosa,
previsualiza el diff y exige confirmación del contenido exacto. Su commit y la
adopción de hashes son conciliables tras caídas, sin agentes ni duplicación.
El cierre sigue siendo una acción separada. Ver [informe](discovery/STATE_EXPORT.md).

Estado verificado:

- esquema `0012_chat` conservado, sin migración ni codec nuevos;
- 462 pruebas pytest y 121 subtests (32 nuevas de exportación);
- 12 checks ligeros y 4 pruebas Node;
- OpenAPI/tipos, TypeScript/build y `alembic check`;
- recorrido Chrome con Git/SQLite sintéticos: preview → commit → preview vacío.

No se usaron proveedores ni se migró la SQLite de trabajo. El orden de D033 queda
satisfecho hasta la exportación. **H4.2 no está iniciado.** Los consentimientos de
smokes anteriores siguen agotados.

## Objetivo y alcance (backlog H4.2)

1. Bootstrap guiado desde un brief y decisiones explícitas del usuario.
2. Plantilla versionada, previsualización y documentos del proyecto.
3. Definición de la primera fase y una primera tarea acotada y verificable.
4. Una carpeta no vacía requiere un flujo de importación; nunca sobrescribirla.
5. Reutilizar contratos, permisos, prompts y autoridad SQLite/Git existentes,
   con verificaciones offline proporcionales y entradas bajo la guardia local.

## Criterios de aceptación

- Crear desde carpeta vacía termina con la primera fase y una primera tarea
  acotada y verificable, según el backlog aceptado.
- Brief, decisiones y preview permiten revisar el resultado antes de los efectos.
- Un directorio no vacío conduce a importación, sin sobrescritura silenciosa.
- Pasan las pruebas offline y los checks de API/tipos/TypeScript/build pertinentes.

## Fuera de alcance

- H4.3 segundo perfil y tareas posteriores.
- Proveedores reales/smokes: requieren autorización específica (D033 punto 8).
- App Server/SDK para el chat, sesión local, SSE gestionado.
- Push y publicación: los hace el usuario.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
