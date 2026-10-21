# Roadmap — my_harness

Fases del desarrollo de Harness Local. Formato del parser del harness (`## PNNN — título`, **Objetivo**, **Criterios de
salida**), sin bloques gestionados mientras el repositorio no esté registrado (D088). Las fases P001–P007 son los
hitos H0–H6 del backlog original; la definición inicial está en [archive/phase-000](archive/phase-000/SUMMARY.md).

| Fase | Título | Estado | Archivo |
|---|---|---|---|
| P001 | Contratos y prueba de viabilidad | completada (2026-10-11) | [phase-001](archive/phase-001/SUMMARY.md) |
| P002 | Visor útil sin ejecutar agentes | completada (2026-10-11) | [phase-002](archive/phase-002/SUMMARY.md) |
| P003 | Núcleo reusable y ejecución gestionada | completada (2026-10-12) | [phase-003](archive/phase-003/SUMMARY.md) |
| P004 | Personalización, bloqueos y cierre | completada (2026-10-13) | [phase-004](archive/phase-004/SUMMARY.md) |
| P005 | Chat y creación de proyectos | completada (2026-10-13) | [phase-005](archive/phase-005/SUMMARY.md) |
| P006 | Calidad de uso y distribución local | completada (2026-10-13) | [phase-006](archive/phase-006/SUMMARY.md) |
| P007 | Agentes configurables e interfaz de producto | completada (2026-10-15) | [phase-007](archive/phase-007/SUMMARY.md) |
| P008 | Contrato documental unificado, cierre de fase e importación de proyectos | completada (2026-10-19) | [phase-008](archive/phase-008/SUMMARY.md) |
| P009 | Proyecto Django desde cero y piloto con cuatro combinaciones de agentes | planificada | — |

## P001 — Contratos y prueba de viabilidad

**Objetivo:** Inventariar el harness de referencia, fijar versiones y capacidades de las CLI y levantar un esqueleto
local que muestre una ejecución simulada sin acceso a modelos.
**Criterios de salida:**
- Fixtures sintéticos de aceptación, revisión, bloqueo, interrupción y cierre, sin secretos ni datos reales.
- Matriz de capacidades y autenticación documentada; parsers de streams probados offline.
- La aplicación arranca localmente y muestra una ejecución simulada.
**Estado:** completada el 2026-10-11 (antes H0) — [archivo](archive/phase-001/SUMMARY.md).

## P002 — Visor útil sin ejecutar agentes

**Objetivo:** Importar y navegar el historial de un harness anterior y observarlo de forma incremental.
**Criterios de salida:**
- Una segunda importación no duplica registros; lo ausente aparece como no registrado.
- Desde una tarea se llega al intento, la revisión y la evidencia que explican su resultado.
- Cerrar y abrir el navegador no pierde ni duplica actividad.
**Estado:** completada el 2026-10-11 (antes H1) — [archivo](archive/phase-002/SUMMARY.md).

## P003 — Núcleo reusable y ejecución gestionada

**Objetivo:** Extraer el motor con contexto explícito y ejecutar, revisar y completar una tarea desde la UI con
recuperación verificable.
**Criterios de salida:**
- Motor aislado con pruebas de caracterización; persistencia, cola idempotente y exclusión por checkout.
- Adaptadores CLI con captura incremental y cancelación; un error conserva evidencias sin fallback.
- Commit limitado a lo revisado y conciliable tras una caída; migración a gestionado exclusiva y reversible.
- API y UI gestionadas hasta COMMITTED con recuperación explícita.
**Estado:** completada el 2026-10-12 (antes H2) — [archivo](archive/phase-003/SUMMARY.md).

## P004 — Personalización, bloqueos y cierre

**Objetivo:** Prompts versionados, permisos con recuperación y fases con check, cierre, lote y enmiendas.
**Criterios de salida:**
- Activar un prompt no altera intentos anteriores; variables inválidas bloquean la llamada.
- Una petición caducada o modificada no acepta una autorización previa; revalidar y reintentar son distintos.
- Un READY obsoleto no cierra la fase; las preguntas pendientes impiden avanzar.
**Estado:** completada el 2026-10-13 (antes H3) — [archivo](archive/phase-004/SUMMARY.md).

## P005 — Chat y creación de proyectos

**Objetivo:** Chat contextual que crea tareas trazables, bootstrap guiado desde carpeta vacía y un segundo perfil.
**Criterios de salida:**
- «Ajusta X» genera una tarea vinculada y ejecutada por el motor, sin ruta lateral.
- Crear desde carpeta vacía termina con una primera tarea acotada y verificable.
- Un perfil TypeScript web funciona sin condiciones nuevas en el núcleo.
**Estado:** completada el 2026-10-13 (antes H4) — [archivo](archive/phase-005/SUMMARY.md).

## P006 — Calidad de uso y distribución local

**Objetivo:** JUnit, backup, retención, diagnósticos, distribución, sesión local y recorridos E2E; después, validaciones
nativas, configuración TOML y primer uso real.
**Criterios de salida:**
- Instalar en un entorno limpio, completar un flujo y restaurar un backup sin el checkout de desarrollo.
- Validaciones del producto con captura acotada y recuperación; composición de uso real por TOML.
**Estado:** completada el 2026-10-13 (antes H5) — [archivo](archive/phase-006/SUMMARY.md).

## P007 — Agentes configurables e interfaz de producto

**Objetivo:** Revisor y ejecutor con proveedor elegible, contrato documental por fase, métricas, creación conversacional
e interfaz de producto por URL.
**Criterios de salida:**
- Cuatro combinaciones revisor/ejecutor verificadas, con historiales anteriores legibles.
- Contrato documental v2, métricas por intento y creación conversacional implementados offline.
- UI: recorrido completo por URL con QA en claro, oscuro y móvil; diffs paginados.
**Estado:** completada el 2026-10-15 (antes H6, D087) — [archivo](archive/phase-007/SUMMARY.md).

## P008 — Contrato documental unificado, cierre de fase e importación de proyectos

**Objetivo:** Que todo proyecto gestionado, incluido este repositorio, siga la estructura documental de D088, que el
cierre de fase archive y reinicie de forma determinista y que se puedan incorporar proyectos de un harness anterior o
sin harness.
**Criterios de salida:**
- Este repositorio sigue la estructura de D088, con enlaces y diagramas validados.
- Plantilla, contratos, prompts y API usan solo la estructura unificada, obligatoria para todo proyecto; creación v1
  retirada.
- Cerrar una fase tras READY archiva STATE, NEXT_STEPS, REVIEW, SUMMARY y `docs/phase/`, reinicia STATE y NEXT_STEPS y
  marca ROADMAP con enlace al archivo, en un commit conciliable.
- Cada intento recibe `AGENTS.md` del checkout en su contexto congelado.
- Perfiles declarativos en el TOML local, incluido Python/Django con pytest, ruff y mypy.
- Los flujos A y B llevan repositorios sintéticos de cada origen al contrato documental con un commit confirmado, sin
  escritura del agente ni pérdida de historial.
- Checks offline en verde; ningún proveedor real sin consentimiento específico.
**Dependencias:** P007.
**Fuera de alcance:** Rediseño visual de la UI; recorridos con CLI reales; publicación del paquete.
**Estado:** completada el 2026-10-19 por la continuación solicitada por el usuario
([D114](DECISIONS.md#d114--cierre-documental-manual-de-p008)) — [archivo](archive/phase-008/SUMMARY.md).
T001–T020 completadas; la quinta revisión de salida (D113) acredita los siete criterios cumplidos offline
y H1–H7 resueltos en sus comprobaciones. Dictamen en [REVIEW](archive/phase-008/REVIEW.md);
entregas, revisiones previas y límites conservados en el [estado archivado](archive/phase-008/STATE.md)
y el [plan archivado](archive/phase-008/NEXT_STEPS.md).

Cierre documental manual, sin registro ni check READY del producto sobre este repositorio y sin tag de fase.
STATE y NEXT_STEPS se reiniciaron sin sucesora en ese cierre. El usuario define después P009 (D115);
la instantánea de P008 conserva el estado original. Plan vigente en [NEXT_STEPS](NEXT_STEPS.md).

## P009 — Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

**Objetivo:** Crear desde la UI un proyecto Django pequeño en una carpeta de proyectos elegida por el usuario,
y desarrollar cuatro tareas del mismo proyecto alternando revisor/ejecutor, con validaciones y commits reales.
**Criterios de salida:**
- «Elegir carpeta de proyectos» permite guardar y retirar una raíz explícita; el servicio puede crear proyectos
  hijos sin volver a pedir ese permiso de carpeta. La IA no decide la ubicación ni obtiene escritura en la raíz padre.
- Crear un proyecto desde cero muestra raíz, nombre y destino exacto; no requiere crear la carpeta hija,
  el esqueleto Django o el entorno a mano. Rechaza destinos existentes y escapes, con recuperación idempotente.
- El proyecto tiene documentación D088, Django, SQLite, plantillas, dependencias fijadas y validaciones reales
  de pytest/JUnit, ruff, mypy, comprobaciones Django y migraciones. Instalación/red solo dentro del plan autorizado.
- La UI permite elegir por proyecto los proveedores de ambos roles y modelo/esfuerzo del revisor, desde
  configuración del servicio. El revisor decide modelo/esfuerzo del ejecutor y deja el motivo congelado por tarea.
- Cuatro tareas distintas llegan a COMMITTED en un único proyecto/id/checkout: Codex→Codex, Codex→Claude,
  Claude→Claude y Claude→Codex (revisor→ejecutor). Cambiar ajustes conserva el historial y no altera jobs congelados.
- El pequeño gestor de tareas permite crear/listar, editar/borrar, completar/reabrir/filtrar y buscar. QA en
  navegador, tests y cierre READY/archivo de su primera fase; evidencia con procedencia y métricas por tarea.
- Checks offline de los cambios del harness y ensayo sin proveedores correctos antes del piloto autorizado.
  Revisión de salida de P009 con resultados y límites; el cierre documental del harness queda separado.
**Dependencias:** P008; D051, D052, D078, D095 y D115.
**Fuera de alcance:** Despliegue, autenticación de usuarios, API REST, frontend separado, base externa, terminal
web genérica, edición de credenciales/ejecutables/TOML desde la UI, agentes con acceso a toda la carpeta padre,
evaluación estadística de modelos y ejecución del harness sobre este repositorio.
**Estado:** T001–T011 y T013–T020 completadas. El Django hijo tiene cuatro tareas COMMITTED: Codex→Codex
(D131), Codex→Claude (D134), Claude→Claude (D136) y Claude→Codex (D137), con 27 tests y las seis validaciones
verdes en T011. Pendiente T012 (QA funcional y cierre del hijo). Incidencias, correcciones y evidencia en
[NEXT_STEPS](NEXT_STEPS.md); alcance y autorizaciones en [docs/phase](phase/P009_PLAN_DJANGO.md);
[contrato T001](phase/P009-T001_CONTRATO_CREACION.md). La siguiente tarea es P009-T012. Las invocaciones de
proveedores reales se limitan a la [propuesta de T006](phase/P009-T006_PROPUESTA_PILOTO.md); no se reutilizan
consentimientos anteriores. Consumo del piloto: 24 de 60; el cierre documental de P009 queda separado.

## Candidatas sin fase asignada

- Pilotos adicionales después del Django de P009; cada operación real conserva propuesta y consentimiento propios.
- `package.json` inicial de un proyecto `typescript-web` nuevo (límite de E4); revisar tras los perfiles de P008.
- Hora de cada validación (cambia el formato del historial) y lectura del run sin decodificar el historial completo.
- Avisos *low* de KaTeX en Mermaid 11; App Server o Agent SDK; `project.yaml` portable.
