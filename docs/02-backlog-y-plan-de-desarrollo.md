# Harness Local — Backlog y plan de desarrollo

11 de octubre de 2026 · Complemento de `01-especificacion-harness-local.md`

## Forma de trabajar

Desarrollar en un repositorio nuevo. El harness de ReferenceProject es una referencia de lectura; sus runs reales no son datos de prueba públicos. No ejecutar el harness para desarrollar este producto. El humano coordina manualmente las sesiones de Codex y Claude Code y revisa sus cambios.

Cada entrega debe ser pequeña, ejecutable y verificable. Mantener contratos de módulos, decisiones y estado en documentos del repositorio. Evitar que dos sesiones editen simultáneamente los mismos archivos. Utilizar branches/worktrees si se trabaja en paralelo y acordar primero los contratos compartidos.

No se estima un plazo en semanas hasta completar el primer recorrido de integración; autenticación, permisos y recuperación son las principales incertidumbres.

## Hito 0 — Contratos y prueba de viabilidad

### H0.1 Inventario reproducible

- Registrar el commit de referencia del repositorio original y hash de archivos locales relevantes; distinguir cambios sin commit.
- Clasificar código reusable, reglas ReferenceProject y formatos legacy.
- Crear fixtures sintéticos de tarea aceptada, revisión, bloqueo, interrupción y cierre.
- Criterio: los fixtures contienen los formatos necesarios y ningún secreto, prompt privado o dato de aplicación real.

### H0.2 Decisiones y compatibilidad

- Fijar versiones de Python, dependencias y herramientas de frontend compatibles.
- Comprobar las versiones instaladas de Codex/Claude y sus interfaces de salida.
- Documentar modos de autenticación por adaptador y cuentas previstas, sin extraer credenciales.
- Probar offline parsers de streams truncados, errores y campos desconocidos.
- Criterio: matriz de capacidades documentada; no se presenta permiso interactivo donde solo existe denegación.

### H0.3 Esqueleto y límites

- Crear núcleo Python, API local mínima, UI React, persistencia y adaptadores falsos.
- Definir modelos Pydantic y contratos HTTP; generar tipos frontend desde OpenAPI cuando se introduzca el cliente.
- Criterio: aplicación arranca localmente y muestra una ejecución simulada sin acceso a modelos.

## Hito 1 — Visor útil sin ejecutar agentes

### H1.1 Importación legacy

- Leer `task.json`, resultados, reviews, validaciones, stops y metadatos de fases.
- Registrar errores de importación sin abortar el inventario completo.
- Usar importación idempotente y tratar archivos parciales como pendientes.
- Criterio: segunda importación no duplica registros; ausencia de consumo o duración aparece como no registrada.

### H1.2 Navegación y evidencias

- Listado de proyectos, fases, tareas e intentos.
- Timeline, hallazgos de revisión, bloqueos, diffs y logs paginados.
- Duración por comando y consumo con origen identificado.
- Criterio: desde una tarea se puede llegar al intento, revisión y evidencia que explican su resultado.

### H1.3 Actualización incremental

- Observador de archivos con relectura controlada y reconciliación al iniciar.
- Eventos SSE persistidos y reconexión por cursor.
- Criterio: cerrar y abrir el navegador no pierde ni duplica actividad; un archivo a medio escribir no se presenta como fallo de agente.

**Salida del hito:** panel usable con históricos. Todavía no permite lanzar el motor anterior desde la web.

## Hito 2 — Núcleo reusable y ejecución gestionada

### H2.1 Extracción del motor

- Sustituir rutas globales por `ProjectContext`.
- Extraer planificación, evidencias, revisión, validación y aceptación en módulos.
- Mantener el comportamiento de sesiones nuevas y los límites de revisión.
- Trasladar dependencias Django/Docker a un perfil ReferenceProject.
- Criterio: pruebas de caracterización verifican las garantías anteriores en repositorios temporales.

### H2.2 Persistencia, cola y exclusión

- Estados y eventos atómicos, jobs persistidos, idempotencia y bloqueo por checkout.
- Snapshot de contrato, políticas, prompts y versiones por intento.
- Criterio: doble clic y solicitudes concurrentes lanzan una sola ejecución; ningún lock se mantiene mediante una transacción larga.

### H2.3 Adaptadores CLI

- Codex planificador/revisor; Claude ejecutor; captura incremental y cancelación de grupos de procesos.
- Pruebas con procesos falsos para timeout, salida inválida, error y falta de resultado final.
- Después, un smoke test real acotado en repositorio desechable con consumo autorizado.
- Criterio: un error conserva evidencias y detiene el run sin fallback ni reintento oculto.

### H2.4 Git y aceptación

- Worktree por tarea, baseline y fingerprint de contenido, diff con staged y untracked.
- Commit limitado a lo revisado; recuperación de commit creado antes de guardar resultado.
- Criterio: una modificación externa después de review invalida la aceptación; el reinicio no duplica commits.

### H2.5 Migración a gestionado

- Vista previa de importación, copia consistente y comprobación de modo exclusivo.
- Reglas de autoridad para documentos y base de datos.
- Criterio: motor legacy y nuevo no pueden gestionar simultáneamente el checkout; los históricos importados siguen accesibles.

**Salida del hito:** una tarea puede ejecutarse, revisarse y completarse desde la UI con recuperación verificable.

## Hito 3 — Personalización, bloqueos y cierre

### H3.1 Prompts versionados

- Editor, variables, diff, borrador/activación y rollback como nueva versión.
- Externalizar `execute-task.md` y conservar los siete prompts anteriores.
- Criterio: activar una versión no altera intentos anteriores; variables inválidas bloquean la llamada al agente.

### H3.2 Permisos y acciones de recuperación

- Separar alcance de ficheros, herramientas, red y decisiones de producto.
- Implementar conceder/denegar con vigencia, identidad y auditoría.
- En CLI, autorizar el siguiente intento; evaluar SDK para petición interactiva viva en un incremento separado.
- Criterio: petición caducada o modificada no acepta una autorización previa; revalidar y reintentar tienen efectos distintos y visibles.

### H3.3 Fases

- Checks, reconciliación documental, preguntas bloqueantes, cierre y tags.
- Separar autorización de lote y cierre automático.
- Criterio: una revisión READY obsoleta no cierra la fase; preguntas pendientes impiden avanzar.

## Hito 4 — Chat y creación de proyectos

### H4.1 Chat contextual

- Adaptador Codex App Server o, si la prueba de viabilidad lo exige, turnos nuevos con contexto explícito.
- Herramientas de lectura y propuestas estructuradas; conversación separada del flujo de ejecución.
- Criterio: «Ajusta X» genera una tarea vinculada y ejecutada por el motor; no modifica aplicación por una ruta lateral.

### H4.2 Bootstrap guiado

- Brief, decisiones, plantilla versionada, preview, documentos y primera fase.
- Directorio no vacío exige un flujo de importación y no una sobrescritura.
- Criterio: crear desde carpeta vacía termina con primera tarea acotada y verificable.

### H4.3 Segundo perfil

- Añadir un stack distinto del Django original, preferentemente un proyecto web TypeScript sencillo.
- Criterio: preparación y tests funcionan mediante perfil sin condiciones específicas nuevas en el núcleo.

## Hito 5 — Calidad de uso y distribución local

- Importación de reportes JUnit y detalle por test con cobertura declarada por perfil.
- Backup/restore, retención de logs y diagnósticos de compatibilidad.
- Assets web empaquetados y comando único de inicio.
- Sesión local, protección de endpoints, rutas y renderizado seguro de logs.
- Recorridos E2E: crear, importar, ejecutar, bloquear, denegar, reintentar y recuperar.
- Criterio: instalar en entorno limpio, completar un flujo y restaurar backup sin depender del checkout de desarrollo.

## Hito 6 — Agentes configurables e interfaz de producto

Añadido el 2026-10-13 por decisión del usuario (D052, D054). Orden: H6.1 antes que la UI.

### H6.1 Revisor y ejecutor con proveedor elegible (D052)

Completado offline el 2026-10-13 (`cli-5`, `local-config-2`); comprobación funcional
real de las cuatro combinaciones completada el 2026-10-14 (`cli-9`, D071).
[Resultado y límites](discovery/PROVIDER_MATRIX_CLI9_RUN.md). Consentimiento agotado.

- Revisor y ejecutor Codex o Claude, en cualquier combinación. El usuario fija el revisor; el revisor fija modelo y esfuerzo del ejecutor (catálogo o libre).
- Planificación `agent` | `deterministic` como ajuste por proyecto.
- Criterio: matriz de las cuatro combinaciones verificada offline por el adaptador real, con historiales anteriores legibles.

### H6.2 Interfaz de producto (D054)

- Arquitectura de información y sistema de diseño de dashboard: navegación, cabecera con sesión, estados vacíos útiles, tablas y estados consistentes.
- Alta de proyectos desde la UI con registro en SQLite y confirmación explícita de confianza; el bootstrap de proyectos nuevos, accesible desde el inicio.
- Configuración de agentes (H6.1) y chat accesibles desde la UI.
- Criterio: QA visual con navegador sobre `scripts/dev` y recorridos de alta → tarea → revisión → commit sin editar archivos a mano.

## Matriz de pruebas prioritarias

| Situación | Evidencia exigida |
|---|---|
| Tests obligatorios fallan | No hay aceptación ni commit |
| Respuesta LLM fuera de esquema | Run detenido con diagnóstico y salida conservada |
| CLI cae durante stream | Eventos parciales preservados, intento incompleto |
| Reinicio con proceso vivo | No se lanza un escritor duplicado |
| Caída después de commit | Se identifica el commit existente y se reconcilia |
| Aprobación doble o vencida | Solo una resolución válida; no se reutiliza |
| Permisos de alcance ampliados | No se amplían herramientas ni red automáticamente |
| Ciclos sin cambios | Detención con motivo, sin gastar indefinidamente |
| Edición externa tras revisión | Se exige nueva evidencia |
| SSE reconecta | Timeline sin huecos recuperables ni duplicados |
| Perfil no Django | Núcleo permanece intacto |
| Backup restaurado | Referencias y hashes válidos |

Reutilizar pruebas de comportamiento existentes tras desacoplarlas; no reescribirlas por estética. La documentación de [Vitest](https://vitest.dev/guide/) y [Playwright](https://playwright.dev/docs/intro) sirve de referencia para las verificaciones de UI propuestas.

## Métricas para decidir si el producto cumple su objetivo

Medir desde el primer piloto: tiempo de configuración, tiempo hasta primera tarea aceptada, intervenciones manuales, errores recuperados, coste/consumo por tarea incluyendo fallos y tareas que requieren correcciones tras aceptación. Comparar proyectos similares; una mejora de velocidad sin calidad equivalente no demuestra reducción efectiva del time to market.
