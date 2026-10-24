# Revisión de cierre — P011

Fecha: 2026-10-24. Base del cierre: `4eeda84a586240a4ac51e8ad78eed2c13a7e34ad` (T017 completada, D181).
**Dictamen: diez criterios de salida cumplidos en el alcance declarado; cierre documental procedente.**
Se contrasta la [revisión favorable de T017](P011_REVIEW.md), el [expediente](P011_EXPEDIENTE_APERTURA.md), el plan
y D154–D181. T018 completa las veinticuatro tareas; no hay bloqueos ni tareas obligatorias ocultas de ese alcance.
[Decisión de cierre D182](../../DECISIONS.md#d182--cierre-documental-de-p011-y-preparación-pública-archivada).
Checks documentales actuales en [P011_CIERRE](P011_CIERRE.md); las suites de T017 son evidencia previa identificada
y no se repiten aquí.

## Criterios de ROADMAP

| # | Criterio | Estado de revisión | Evidencia y límite |
|---|---|---|---|
| 1 | Inventario por archivo; código mantenido en inglés; excepciones justificadas | Cumplido | T001, T003–T006, T019, T009, T021/T022 (D159–D165, D169, D171/D172). Recetas v1, alias bilingües, fixtures y vocabulario histórico conservados con ruta y motivo |
| 2 | Visual/default de trabajo globales en/es, visual mutable y congelado por interacción | Cumplido offline y con QA de navegador sintética | T007, T010, T021, T022, T024 (D166, D170–D172, D180). QA solo en Chrome; códigos técnicos visibles por HITL |
| 3 | Trabajo en/es inmutable al alta, prompts ingleses y directiva de ambos idiomas congelada | Cumplido con agentes falsos | T008, T020, T009, T016 (D167–D169, D179). Calidad lingüística con proveedores reales no acreditada |
| 4 | Política CLI por capacidades y mínimos, guardias y bloqueo antes del efecto | Cumplido con CLI falsas | T011, T012, T016 (D173/D174). Posteriores con compatibilidad condicionada; ninguna CLI real caracterizada en P011 |
| 5 | Diagramas, datos y arquitectura contrastados con código y pruebas | Cumplido | T013, T023 (D175/D177) y residuo «observers» cerrado en T017. Parser Mermaid local, sin render DOM |
| 6 | Documentación pública inglesa, entrada española y primer uso reproducible hasta COMMITTED | Cumplido en macOS ARM64 | T014, T023, T016, T017 (D176/D177/D179/D181). Baseline para forks/agentes sin ADR privadas |
| 7 | Licencia, contenido publicable e instantánea con Git independiente | Cumplido | T002, T015, T016, T017 (D160/D178). Historial privado conservado sin reescritura |
| 8 | Paquete coherente, CI sintética, materiales de release y QA del artefacto exacto | Cumplido localmente | T015, T016, T024, T017 (D178–D181). CI remota sin ejecutar: se comprueba en la apertura (expediente, paso 4) |
| 9 | Legacy/A retirado; solo cero y B; historia propia sin borrar datos | Cumplido | T019, T015, T016, T017 (D161). Revisiones 0001–0025 conservadas; `watch_enabled` inerte |
| 10 | Dictamen de diez y trece antes del cierre; expediente sin publicar | Cumplido | T017 (D181): dictamen favorable y expediente; ninguna acción remota ejecutada |

Los trece criterios globales de SPECIFICATION §10, en la redacción de D161, quedan acreditados por la matriz de
[P011_REVIEW §3](P011_REVIEW.md#3-criterios-globales-de-specification-10); la matriz histórica de P010 no se reescribe.
Los tres hallazgos de T017 están resueltos: H1 y H2 en T017 por HITL; H3, NEXT_STEPS sobre su presupuesto, se
resuelve con este archivo.

## Candidato y continuidad

El cierre cambia solo `docs/` privada, excluida del candidato por lista positiva. La instantánea regenerada desde el
commit de T017 y desde el árbol de este cierre da el mismo manifiesto `74cc9141…ea71` de 387 archivos, sin problemas
([P011_CIERRE](P011_CIERRE.md#verificación)). Wheel `46d29c20…d9d6`, sdist `79e256de…42c5` y `pylock.toml`
`20a327c3…2cf9` siguen siendo los de T017; no se reconstruyen.

La recomendación de abrir no ejecuta nada: crear el repositorio, push, CI remota, visibilidad, reporte privado de
vulnerabilidades y Release opcional exigen instrucción explícita del usuario sobre el expediente archivado. Tras la
apertura, el repositorio público es la fuente principal (D157); este checkout conserva su historia privada.

## Alcance real conservado

Sin CLI reales, proveedores ni inferencia en P011. B y el perfil D095 siguen con validación solo offline (D151);
A queda retirado del producto sin acreditarse como validado. Solo macOS ARM64, QA solo en Chrome y contención
cooperativa sin aislamiento del sistema operativo. El cierre manual de este repositorio queda separado de un check
READY del producto; no se opera el harness sobre él ni se crea tag o publicación. El paquete sigue en `0.1.0`.
