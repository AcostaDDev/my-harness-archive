# Siguiente tarea — H3.1: prompts versionados

Salida del hito 2, parte 2, completada offline el 2026-10-12 (D029):
[UI gestionada local](discovery/H2_EXIT_UI.md),
[alcance completado](discovery/H2_EXIT_UI_SCOPE.md).
308 pruebas pytest y 121 subtests, 3 pruebas Node, 12 checks ligeros, TypeScript
/build y recorrido Chrome con Git/SQLite/fakes correctos. COMMITTED, reinicio,
doble clic, cuarentena/revalidación y migración verificados sin proveedores.

**H3.1 no iniciado.** No se ha implementado ni diseñado en detalle esta tarea.
Los consentimientos de smokes anteriores permanecen agotados.

## Objetivo y alcance siguiente

Completar H3.1 del backlog, en una entrega offline acotada:

1. Revisar especificación §9, backlog H3.1, prompts actuales del motor y referencia
   legacy en lectura; identificar los siete prompts anteriores sin trasladar
   acoplamientos de stack al núcleo. Señalar contradicciones antes de cambiar diseño.
2. Definir e implementar versiones inmutables de prompts, variables permitidas,
   borrador/activación y rollback como nueva versión, con persistencia/migración
   explícita cuando corresponda. No alterar snapshots de intentos previos.
3. Externalizar `execute-task.md` y conservar los siete prompts anteriores;
   distinguir plantillas del núcleo, perfil y proyecto. No ejecutar ni modificar
   el harness de referencia ni copiar runs privados a fixtures.
4. Añadir editor, validación de variables y diff de versiones por API/UI con los
   tipos generados, errores visibles y confirmación de activación. Mantener las
   guardias locales y controles de versión de las mutaciones gestionadas.
5. Congelar la versión/renderizado al crear cada intento, antes de efectos.
   Caracterizar offline activación concurrente, reinicio y rollback con fakes.
6. Verificar criterios, ejecutar checks pertinentes, revisar diff y actualizar
   STATE, NEXT_STEPS, DECISIONS e informe. No avanzar a H3.2.

## Criterios de aceptación

- Activar una versión no altera prompts, contratos o resultados de intentos previos.
- Variables inválidas bloquean la llamada al agente antes de cualquier efecto.
- Borrador, diff, activación y rollback como versión nueva son verificables desde UI.
- Los prompts externalizados conservan su comportamiento caracterizado mediante
  fixtures sintéticos; versiones y procedencia quedan visibles sin datos inferidos.
- Regresión API, tipos generados, TypeScript/build y checks offline pertinentes pasan.

## Fuera de alcance

Proveedores reales, smokes, login/refresh, secretos, recuperación de D020/D022,
H3.2 (permisos interactivos), H3.3 (fases), integración de rama, push/publicación,
chat, SDK y distribución. No lanzar agentes de colaboración ni usar el harness
para desarrollar este repositorio. Sesión local, guardia H0/H1, SSE gestionado y
registro de proyectos por HTTP permanecen pendientes; no ampliarlos de forma
implícita dentro de H3.1.
