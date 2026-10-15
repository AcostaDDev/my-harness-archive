# Siguiente paso: corrección de la paginación de diffs (hallazgo de D085)

Estado al 2026-10-15:

- **Revisión de cierre de H6.2 completada (D085).** [Dictamen, evidencia y hallazgos](discovery/H6.2_CLOSURE_REVIEW.md).
  Recorrido sintético completo desde la UI, URLs en `scripts/dev` y desde el wheel, reintentos sin efectos, Markdown
  hostil inerte, QA en claro, oscuro y 386 px, y checks en verde. **Criterio parcial: los diffs no van paginados.**
- El hito H6.2 queda pendiente de que el usuario elija: corregir el hallazgo 1 (propuesta de abajo) o aceptarlo como
  límite y cerrar el hito.
- Límites que siguen abiertos: un proyecto `typescript-web` recién creado no tiene `package.json` y el ejecutor no puede
  crearlo (decisión aparte); las validaciones no guardan su hora; 2 avisos *low* de KaTeX; ningún recorrido de H6.2 con
  CLI reales.

## Tarea concreta propuesta, no iniciada

**Diffs paginados y sondeo acotado del run** (hallazgo 1 de D085; los hallazgos 2 y 3 son opcionales en la misma tarea).

1. Lectura del diff de un ciclo paginada por bytes o por líneas, con hash y tamaño. `ManagedRunRead` lleva solo el
   resumen de cada ciclo (hash, bytes y rutas), sin romper a otros consumidores del diff (documentos, exportación,
   transición).
2. La página del run carga el diff al abrirlo, página a página, y deja de sondear, o sondea más espaciado, cuando el
   run está en un estado terminal. `/runs/{id}/jobs` paginado o acotado.
3. Opcional: clave idempotente al crear conversaciones de chat y de planificación de fase (requiere migración), y
   deriva neutra sin exportación en una fase cerrada y transicionada.

Criterios: pytest de la nueva lectura (paginación, límites, hash), Node si hay lógica pura nueva, OpenAPI y tipos
regenerados, checks estándar, `tsc`, build y `alembic check` en verde; QA del run con un diff grande en claro, oscuro y
estrecho. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
