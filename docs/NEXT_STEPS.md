# Siguiente paso: H6.2 E4, creación y planificación de fase (D076)

Estado al 2026-10-15:

- **H6.2 E3 implementada y verificada offline (D080).** [Entrega, verificación y límites](discovery/H6.2_E3_DOCS.md).
  Incluye:
  - `markdown-it@15.0.2` (`html: false`) y `mermaid@11.17.2` (`strict`, diferido y mostrado como imagen aislada).
  - Árbol `/projects/:p/docs/*path`, visor con enlaces relativos y `http(s)` e imágenes del checkout por la API.
  - Editor con bloques gestionados bloqueados, hash base (`document_changed`), diff y confirmación idempotente.
  - Cambios locales: confirmar sus bytes o regenerar los bloques editados; deriva enlazada a la adopción de la fase.

  QA con Chrome sobre `scripts/dev` con datos sintéticos: documento hostil inerte, edición, conflicto, regeneración,
  claro, oscuro y 386 px.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): E4 creación y planificación → E5 chat global → E6 estadísticas.
- Límite conocido: 2 avisos *low* de KaTeX (dependencia de Mermaid) hasta poder fijar Mermaid 12 con dos semanas.

## Tarea concreta propuesta, no iniciada

**H6.2 E4 — Creación y planificación de fase** ([alcance §E4](discovery/H6.2_SCOPE.md#e4--creación-y-planificación-de-fase)).

1. `/projects/:p/setup` sobre la API de H6.5 (`/planning/...`): brief, turnos de `definition`, borradores (aplicar,
   descartar y editar con CAS, reutilizando el visor y el editor de E3), preguntas aplazadas con motivo y vista previa
   de la aceptación con sus bloqueos. Al aceptar, bootstrap v2 y P001.
2. `phase_planning` desde la fase cerrada y transición con `plan_proposal`.
3. Recorrido desde la UI de inicio a fin: registro de una carpeta vacía con bootstrap (E2) → creación → primera tarea.

Criterios: ninguna acción repite efectos al recargar; confirmaciones ligadas a hash y versión; turnos con agentes
falsos; QA con navegador en claro, oscuro y estrecho. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
