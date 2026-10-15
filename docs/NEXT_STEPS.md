# Siguiente paso: H6.2 E6, estadísticas y tests (D076)

Estado al 2026-10-15:

- **H6.2 E5 implementada y verificada offline (D083).** [Entrega, verificación y límites](discovery/H6.2_E5_CHAT.md).
  Preguntas sobre HEAD exportado, sin lock del checkout y con carril propio; recuperación sin worktrees huérfanos.
  Comandos deterministas con los controles/confirmaciones existentes y conversaciones con contexto de fase o tarea.
  QA sintética: propuesta → tarea → commit, pregunta sobre HEAD, check → READY → cierre; claro, oscuro y 386 px.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): E1–E5 completadas; E6 sin iniciar.
- Límites conocidos: 2 avisos *low* de KaTeX (dependencia de Mermaid) hasta poder fijar Mermaid 12 con dos semanas; un
  proyecto `typescript-web` recién creado no tiene `package.json` y el ejecutor no puede crearlo (ruta protegida), así
  que su preparación real fallaría. Esto último necesita una decisión aparte.
- El chat consulta archivos regulares de HEAD, sin cambios locales; los permisos de la exportación no certifican
  aislamiento OS. No se ha probado el nuevo recorrido con CLI reales.

## Tarea concreta propuesta, no iniciada

**H6.2 E6 — Estadísticas y tests** ([alcance §E6](discovery/H6.2_SCOPE.md#e6--estadísticas-y-tests)).

1. `/stats` y `/projects/:p/stats` sobre `/metrics/*`: consumo por fase, día, rol, proveedor y modelo; favoritos por rol;
   aceptación a la primera; revisiones; duraciones; paradas; tests OK/KO y su evolución.
2. En la tarea: agentes, intentos, tokens (también de fallos), turnos y la última validación. Mostrar la procedencia,
   nunca tratar null como cero y presentar el coste como «equivalente API».
3. Gráficos sin dependencia nueva (SVG propio), salvo una decisión aparte.

Criterios: URLs directas y recarga en desarrollo y wheel; consultas por recurso y evidencia paginada; datos ausentes
se distinguen de cero; QA sintética en claro, oscuro y estrecho. Mantener pytest, checks estándar, Node, `tsc`, build y
`alembic check`. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar. No iniciar otra entrega en la misma tarea.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
