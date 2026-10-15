# Siguiente paso: revisión de cierre de H6.2 (D076)

Estado al 2026-10-15:

- **H6.2 E6 implementada y verificada offline (D084).** [Entrega, verificación y límites](discovery/H6.2_E6_STATS.md).
  `/stats` y `/projects/:p/stats` sobre `/metrics/*`: resumen, consumo por fase/proyecto, día, rol, proveedor, modelo y
  esfuerzo, favoritos por rol, calidad por tarea, evolución de tests OK/KO por fase (`/metrics/validations`), paradas e
  intentos con procedencia. Métricas en la página de la tarea. Gráficos SVG propios, sin dependencias.
  QA sintética con Chrome: claro, oscuro y 386 px.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): **E1–E6 completadas**. Falta comprobar los criterios del hito en conjunto.
- Límites conocidos: las validaciones no guardan su hora, así que la evolución de los tests es por fase y no por día;
  2 avisos *low* de KaTeX (dependencia de Mermaid) hasta poder fijar Mermaid 12 con dos semanas; un proyecto
  `typescript-web` recién creado no tiene `package.json` y el ejecutor no puede crearlo (ruta protegida), así que su
  preparación real fallaría. Esto último necesita una decisión aparte.
- Ningún recorrido de H6.2 se ha probado con CLI reales.

## Tarea concreta propuesta, no iniciada

**Revisión de cierre de H6.2** ([criterios del hito](discovery/H6.2_SCOPE.md#criterios-de-aceptación-del-hito)).

1. Recorrido sintético completo desde la UI, sin editar archivos a mano: alta → creación → primera tarea → revisión →
   commit → cierre → transición con plan propuesto, y sus estadísticas.
2. Cada URL por enlace directo y por recarga, en `scripts/dev` y desde el wheel instalado en un venv propio (D051).
3. Repasar idempotencia y confirmaciones ligadas a hash y versión, carga por recurso y paginación, y los casos hostiles
   de Markdown.
4. Dictamen con lo cubierto, lo no cubierto y los hallazgos; corregir solo defectos acotados con prueba.

Criterios: dictamen escrito en `docs/discovery/`, pytest, checks estándar, Node, `tsc`, build y `alembic check` en verde;
QA en claro, oscuro y estrecho. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar. No iniciar otro hito en la misma
tarea.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
