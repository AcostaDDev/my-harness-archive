# Siguiente tarea — H2.1 (pendiente)

H0 y H1 completados el 2026-10-11. [Alcance original de H1.3](discovery/H1.3_SCOPE.md)
y [entrega/verificaciones](discovery/H1.3_OBSERVATION.md) conservados para revisión.
Esta entrega no inicia H2.1.

## Objetivo

Extraer el motor reusable con `ProjectContext`, separando planificación, evidencias,
revisión, validación y aceptación de reglas específicas de proyectos. Conservar
sesiones nuevas y límites de revisión mediante caracterización offline.

## Alcance de la siguiente sesión

1. Revisar H2.1 del backlog, arquitectura/invariantes de la especificación y
   D006/D009/D010/D012–D014. Consultar la referencia anterior solo en lectura.
2. Delimitar `ProjectContext` y las dependencias del motor antes de trasladar
   comportamiento; sustituir rutas globales y mantener el núcleo independiente
   de web, proveedores y stacks. Señalar contradicciones materiales antes de cambiar diseño.
3. Extraer módulos de planificación, evidencias, revisión, validación y aceptación,
   usando checkouts sintéticos y adaptadores falsos. Mantener sesiones nuevas,
   historial, límites de revisión, stop operativo y ausencia de fallback silencioso.
4. Trasladar reglas Django/Docker a un perfil ReferenceProject sin modificar el proyecto
   de referencia ni ejecutar su harness. No activar el motor desde la web ni
   introducir escritores sin la persistencia/exclusión futura de H2.2.
5. Añadir pruebas de caracterización offline en repositorios temporales,
   conservar H0/H1, ejecutar checks pertinentes, actualizar STATE/NEXT_STEPS
   y registrar decisiones duraderas.

## Criterios de aceptación

- El motor extraído usa contexto explícito y módulos independientes del stack
  de proyecto; las reglas Django/Docker permanecen en un perfil.
- Pruebas offline caracterizan las garantías anteriores: sesiones nuevas,
  historial, límites de revisión y separación de revisión/validación/aceptación.
- H0.3 y observación H1.1–H1.3 siguen funcionando; contratos/checks/build pasan.
- No se presenta como ejecución gestionada una extracción aislada del motor.

## Fuera de alcance

H2.2 cola/persistencia gestionada/bloqueo escritor, H2.3 adaptadores reales,
chat, permisos interactivos, SDKs y distribución. No ejecutar harness/agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global. No usar runs
reales; smoke con proveedores requiere autorización explícita de consumo posterior.
