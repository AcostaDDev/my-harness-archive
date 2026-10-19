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
| P008 | Contrato documental unificado, cierre de fase e importación de proyectos | activa | — |

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
**Estado:** activa desde el 2026-10-15; T001–T015 completadas el 2026-10-16. Revisión de salida completada el
2026-10-17 con tres hallazgos funcionales del Flujo A y referencias vigentes desactualizadas
([D104](DECISIONS.md#d104--revisión-de-salida-de-p008-con-hallazgos-en-el-flujo-a),
[registro](phase/P008_REVISION_SALIDA.md)). T016 corrige los tres hallazgos funcionales el 2026-10-17 (D105).
T017 sincroniza las referencias vigentes el 2026-10-17 (D106). Segunda revisión de salida completada el mismo día
([D107](DECISIONS.md#d107--segunda-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_2.md)):
H1–H4 resueltos y dos referencias residuales corregidas; H5 reproduce ejecución de lazy-fetch durante el inventario
A con un blob prometido ausente. T018 corrige H5 el 2026-10-17
([D108](DECISIONS.md#d108--p008-t018-lecturas-de-importación-sin-lazy-fetch),
[registro](phase/P008-T018_OBJETOS_LOCALES.md)). Tercera revisión completada el mismo día
([D109](DECISIONS.md#d109--tercera-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_3.md)):
H1–H5 resueltos; H6 reproduce filtros de submódulos ejecutados por el inventario A. T019 corrige H6 el 2026-10-19
([D110](DECISIONS.md#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout),
[registro](phase/P008-T019_SUBMODULOS.md)). Cuarta revisión completada el mismo día
([D111](DECISIONS.md#d111--cuarta-revisión-de-salida-de-p008), [registro](phase/P008_REVISION_SALIDA_4.md)):
H1–H6 resueltos; H7 reproduce transportes por lazy-fetch del escritor A/B al consultar el commit futuro.
P008 sigue activa y no lista para cerrar: siguiente P008-T020 y después otra revisión de salida.
El cierre y archivo serán posteriores; no se ha ejecutado un check READY del producto sobre este repositorio.
Plan y entregas en [NEXT_STEPS](NEXT_STEPS.md).

## Candidatas sin fase asignada

- Piloto real del producto con CLI reales y las métricas de objetivo (requiere propuesta y consentimiento nuevos).
- `package.json` inicial de un proyecto `typescript-web` nuevo (límite de E4); revisar tras los perfiles de P008.
- Hora de cada validación (cambia el formato del historial) y lectura del run sin decodificar el historial completo.
- Avisos *low* de KaTeX en Mermaid 11; App Server o Agent SDK; `project.yaml` portable.
