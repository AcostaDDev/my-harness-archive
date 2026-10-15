# Plan archivado — P004 Personalización, bloqueos y cierre (antes H3)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 3 — Personalización, bloqueos y cierre

#### H3.1 Prompts versionados

- Editor, variables, diff, borrador/activación y rollback como nueva versión.
- Externalizar `execute-task.md` y conservar los siete prompts anteriores.
- Criterio: activar una versión no altera intentos anteriores; variables inválidas bloquean la llamada al agente.

#### H3.2 Permisos y acciones de recuperación

- Separar alcance de ficheros, herramientas, red y decisiones de producto.
- Implementar conceder/denegar con vigencia, identidad y auditoría.
- En CLI, autorizar el siguiente intento; evaluar SDK para petición interactiva viva en un incremento separado.
- Criterio: petición caducada o modificada no acepta una autorización previa; revalidar y reintentar tienen efectos distintos y visibles.

#### H3.3 Fases

- Checks, reconciliación documental, preguntas bloqueantes, cierre y tags.
- Separar autorización de lote y cierre automático.
- Criterio: una revisión READY obsoleta no cierra la fase; preguntas pendientes impiden avanzar.

## Alcances conservados

### Siguiente tarea — H3.1: prompts versionados

_Origen: `docs/discovery/H3.1_SCOPE.md`._

Salida del hito 2, parte 2, completada offline el 2026-10-12 (D029):
[UI gestionada local](../phase-003/H2_EXIT_UI.md),
[alcance completado](../phase-003/NEXT_STEPS.md).
308 pruebas pytest y 121 subtests, 3 pruebas Node, 12 checks ligeros, TypeScript
/build y recorrido Chrome con Git/SQLite/fakes correctos. COMMITTED, reinicio,
doble clic, cuarentena/revalidación y migración verificados sin proveedores.

**H3.1 no iniciado.** No se ha implementado ni diseñado en detalle esta tarea.
Los consentimientos de smokes anteriores permanecen agotados.

#### Objetivo y alcance siguiente

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

#### Criterios de aceptación

- Activar una versión no altera prompts, contratos o resultados de intentos previos.
- Variables inválidas bloquean la llamada al agente antes de cualquier efecto.
- Borrador, diff, activación y rollback como versión nueva son verificables desde UI.
- Los prompts externalizados conservan su comportamiento caracterizado mediante
  fixtures sintéticos; versiones y procedencia quedan visibles sin datos inferidos.
- Regresión API, tipos generados, TypeScript/build y checks offline pertinentes pasan.

#### Fuera de alcance

Proveedores reales, smokes, login/refresh, secretos, recuperación de D020/D022,
H3.2 (permisos interactivos), H3.3 (fases), integración de rama, push/publicación,
chat, SDK y distribución. No lanzar agentes de colaboración ni usar el harness
para desarrollar este repositorio. Sesión local, guardia H0/H1, SSE gestionado y
registro de proyectos por HTTP permanecen pendientes; no ampliarlos de forma
implícita dentro de H3.1.
