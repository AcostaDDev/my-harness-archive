# P011-T001 — Inventario de fuentes y superficies

Fecha: 2026-10-22. Base: `2730f54`; **688 archivos rastreados**, 469 filas individuales y
219 archivos históricos agrupados en 11 carpetas. Inventario inicial,
no traducción completada ni auditoría de privacidad. [Contrato](P011-T001_CONTRATO_APERTURA.md),
[decisión](../DECISIONS.md#d159--p011-t001-contrato-de-idiomas-fuentes-y-corte-público).
Las tareas propietarias deben resolver cada fila afectada y registrar sus excepciones/evidencias en su entrega.

## Método y límites

Enumeración con `git ls-tree -r --name-only 2730f54`. Se examinaron textos de las filas individuales sin ejecutar
imports del proyecto. Python: `ast.parse`, docstrings por nodo y comentarios por `tokenize`; constantes de texto
separadas de docstrings. Otros formatos: búsqueda por línea y revisión de las superficies por grupo, sin afirmar
que un literal TS/HTML/JSON es comentario. Ningún reemplazo automático. Archivo histórico: solo enumeración,
sin reinterpretar sus idiomas ni abrir runs/configuración privada.

Búsqueda insensible a mayúsculas de tildes/ñ/signos y palabras también sin tildes:

```regex
[áéíóúñü¿¡]|\b(?:archivo|archivos|proyecto|proyectos|tarea|tareas|fase|fases|siguiente|pendiente|pendientes|solo|sin|con|para|desde|hasta|siempre|nunca|ninguna|permite|requiere|debe|puede|fuera|datos|salida|entrada|modelo|prueba|validar|comprobar|clave|estado|raiz|versiones|mismo|misma|cada|antes|despues|nombre|ruta|rutas|registro|pregunta|respuesta|ejecutor|revisor|objetivo|resumen|aceptar|crear|borrar|cambio|cambios|origen|destino|nuevo|nueva|fallo|error|codigo|formato|ninguno|validacion|inmutable|comando|paso|linea|escritura|lectura)\b
```

Es un detector de candidatos, no un clasificador lingüístico: `error`, `con`, `sin`, versiones o nombres pueden
ser técnicos/ingleses. «Sin candidatos» no demuestra ausencia de español ni cierra una tarea. El propietario
revisa el archivo completo, especialmente inline comments y cadenas generadas. El idioma de los identificadores
mantenidos es mayoritariamente inglés; se revisaron nombres AST con la misma lista y tokens TS por búsqueda.
No se justifica renombrar nombres públicos, formatos, rutas o campos por su idioma. Se detectó el nombre de test
`test_tarea_is_idempotent_proposal_without_snapshot_or_agent` en `tests/product/test_chat_global.py`: T006 puede
traducir su nombre interno; el comando `tarea` y sus expectativas se conservan por la gramática bilingüe.
Los demás candidatos de nombres se listan en §Identificadores; ninguna búsqueda sustituye la revisión al editar.

Señales: C = tokens de comentario Python, D = docstrings, S = constantes de texto (mensajes, documentos,
fixtures, comandos o código generado; requieren clasificación), A = líneas candidatas en otros formatos.
L = primeras ocho líneas candidatas por archivo; los conteos no son número de traducciones necesarias.
Se analizaron 236 archivos Python y 233 textos restantes; 360 archivos con candidatos;
C=612, D=618, S=1213. Los conteos se refieren a la base, no a los documentos nuevos de T001.

## Tratamientos y excepciones

| Clave | Tratamiento de la fila / excepción justificada |
|---|---|
| C | Traducir comentarios/docstrings/descripciones técnicas mantenidas (T003 o T004); prosa de generación documental/prompts → T009, mensajes propios visibles → T010. Conservar ids/protocolos/parsers bilingües y datos libres. |
| U | Comentarios y nombres internos a T005; UI, ARIA, ayudas, errores, estados vacíos y confirmaciones a catálogos T010; retirar ramas A/legacy en T019 antes de traducirlas. |
| P | Prompt base inglés/versionado, literales de ejemplo y salida V/W/T según contrato; nunca reescribir personalizaciones o snapshots pasados. T019 retira entrada A. |
| F | Comentarios/descripciones/nombres de tests a T006; separar fixtures de datos/expectativas, rutas, hashes, streams y documentos bilingües. Añadir casos nuevos para capacidades nuevas; conservar cobertura histórica necesaria. |
| G | Infraestructura compartida A/B o guardia antigua: extraer lo necesario antes de retirar A, manteniendo intención/CAS/objetos locales; luego traducir código mantenido. No borrar por el nombre `import`/`migration`. |
| R | Candidato exclusivo legacy/A: T019 verifica dependencias y retira entrypoint/módulo/cobertura exclusiva. No traducir una capacidad que se eliminará; conservar datos/migraciones/guardias necesarias. |
| D | Documentación viva española/mixta: paridad en tarea de producto, auditoría T013 y baseline pública nueva T014; conservar contexto privado, anclas y originales históricos. |
| H | Herramientas/configuración/metadatos/ejemplos: comentarios ingleses, ejemplos sintéticos; ayuda visible a catálogos, requisitos/setup a T014, distribución a T015. Revisar autorizaciones antes de ejecutar scripts. |
| E1 | Fuentes v1 de receta/lock/manifiesto ligadas a huellas: bytes y perfil efectivos congelados, solo compatibilidad. Código nuevo en v2; no traducir v1 para aparentar cobertura. |
| E2 | Fixtures congelados de streams/documentos/compatibilidad: preservar bytes/hashes y entradas en/es; legacy exclusivo puede retirarse, pero antes separar fixtures de migración/backup/guardias y regresión B. |
| E3 | OpenAPI/tipos derivados: cambiar el contrato fuente y regenerar juntos, nunca traducir artefactos a mano. Nombres técnicos del esquema no dependen del visual. |
| E4 | Artefactos privados de fase/archivo: no exportar al corte inicial ni reescribir snapshots. Los archivos de trabajo vivos pueden actualizar su seguimiento; las fases cerradas permanecen intactas. |
| E5 | ADR anteriores inmutables: añadir nuevas decisiones, sin traducción retroactiva. Índice vivo actualizable. Registro público de partida nuevo y autocontenido, sin publicar el registro privado. |
| E6 | Guiones operativos históricos: conservar bytes y excluir de la exportación; no tratarlos como setup actual ni ejecutarlos. Crear ejemplos vigentes aparte. |
| E8 | Lock de dependencias: preservar identidades/hashes/licencias; traducción de metadatos solo mediante cambio de fuente y regeneración autorizada. No es texto de interfaz. |
| B | Binario: inventario de contenido/licencia/privacidad T002, sin traducción textual. |

## Archivos de producto, herramientas, pruebas y documentación viva

Los propietarios se expresan como TNNN de P011; C/U/F delegan mensajes y generación según la tabla anterior.
La columna de idioma describe candidatos del texto, no el idioma del usuario ni una aprobación del archivo.

| Archivo | Idioma actual/señal | Propietaria | Tratamiento | Localización de candidatos |
|---|---|---|---|---|
| `.gitignore` | ES/EN (candidatos) | T002/T005/T015 | H | A1; L 20 |
| `.python-version` | EN/técnico (sin candidatos) | T002/T005/T015 | H | A0; L — |
| `AGENTS.md` | ES/EN (candidatos) | T014 | D | A27; L 1,3,4,7,9,10,11,12 (+19) |
| `CLAUDE.md` | ES/EN (candidatos) | T014 | D | A3; L 5,7,8 |
| `GEMINI.md` | ES/EN (candidatos) | T014 | D | A1; L 5 |
| `README.md` | ES/EN (candidatos) | T014 | D | A84; L 3,4,5,6,8,10,11,12 (+76) |
| `alembic.ini` | EN/técnico (sin candidatos) | T002/T005/T015 | H | A0; L — |
| `docs/ARCHITECTURE.md` | ES/EN (candidatos) | T013/T014/T019 | D | A284; L 3,4,9,11,12,13,15,17 (+276) |
| `docs/DDBB-DIAGRAM.md` | ES/EN (candidatos) | T013/T014/T019 | D | A74; L 1,3,5,6,8,10,12,58 (+66) |
| `docs/DECISIONS.md` | ES/EN (candidatos) | T014 | E5 | A3469; L 3,4,5,6,7,9,11,15 (+3461) |
| `docs/NEXT_STEPS.md` | ES/EN (candidatos) | T013/T014/T019 | D | A371; L 1,3,4,7,8,9,10,11 (+363) |
| `docs/ROADMAP.md` | ES/EN (candidatos) | T013/T014/T019 | D | A211; L 3,4,5,7,9,10,11,12 (+203) |
| `docs/SPECIFICATION.md` | ES/EN (candidatos) | T013/T014/T019 | D | A257; L 1,3,4,5,6,9,11,12 (+249) |
| `docs/STATE.md` | ES/EN (candidatos) | T013/T014/T019 | D | A100; L 1,3,7,8,10,11,12,13 (+92) |
| `docs/flows/chat.md` | ES/EN (candidatos) | T013/T014/T019 | D | A17; L 1,3,4,13,15,16,17,18 (+9) |
| `docs/flows/database-migration.md` | ES/EN (candidatos) | T013/T014/T019 | D | A29; L 1,3,4,14,15,16,17,18 (+21) |
| `docs/flows/documents.md` | ES/EN (candidatos) | T013/T014/T019 | D | A31; L 3,8,9,10,11,13,14,15 (+23) |
| `docs/flows/legacy-migration.md` | ES/EN (candidatos) | T019/T013 | R | A91; L 1,3,4,8,9,10,11,14 (+83) |
| `docs/flows/phase-lifecycle.md` | ES/EN (candidatos) | T013/T014/T019 | D | A48; L 1,5,17,18,21,25,26,27 (+40) |
| `docs/flows/project-agents.md` | ES/EN (candidatos) | T013/T014/T019 | D | A41; L 1,3,4,8,9,10,11,12 (+33) |
| `docs/flows/project-creation.md` | ES/EN (candidatos) | T013/T014/T019 | D | A71; L 1,3,4,5,6,7,8,9 (+63) |
| `docs/flows/project-definition.md` | ES/EN (candidatos) | T013/T014/T019 | D | A40; L 1,3,4,5,6,8,9,10 (+32) |
| `docs/flows/project-onboarding.md` | ES/EN (candidatos) | T013/T014/T019 | D | A124; L 1,3,4,5,6,10,11,12 (+116) |
| `docs/flows/project-preparation.md` | ES/EN (candidatos) | T013/T014/T019 | D | A77; L 1,3,5,6,7,8,9,10 (+69) |
| `docs/flows/task-run.md` | ES/EN (candidatos) | T013/T014/T019 | D | A82; L 1,3,4,5,6,16,17,19 (+74) |
| `docs/phase/P011_PLAN_APERTURA_PUBLICA.md` | ES/EN (candidatos) | T001/T018 | E4 | A203; L 1,3,4,5,6,7,8,12 (+195) |
| `examples/django-recipe.example.toml` | ES/EN (candidatos) | T005/T014/T015 | H | A19; L 1,2,4,5,6,7,8,9 (+11) |
| `examples/first_use/prepare.sh` | ES/EN (candidatos) | T002/T014 | E6 | A12; L 2,3,18,25,28,33,34,38 (+4) |
| `examples/local_config.example.toml` | ES/EN (candidatos) | T005/T014/T015 | H | A51; L 1,2,3,4,5,6,7,9 (+43) |
| `examples/managed_demo.py` | ES/EN (candidatos) | T005/T014/T015 | H | C3/D0/S0; L 59,67,75 |
| `examples/provider_matrix/drive.py` | ES/EN (candidatos) | T002/T014 | E6 | C1/D2/S3; L 1,16,56,119,120,122 |
| `examples/provider_matrix/prepare.sh` | ES/EN (candidatos) | T002/T014 | E6 | A23; L 2,3,4,5,6,16,30,33 (+15) |
| `examples/provider_matrix/run_pairing.sh` | ES/EN (candidatos) | T002/T014 | E6 | A5; L 2,3,4,5,25 |
| `examples/typescript-web-recipe.example.toml` | ES/EN (candidatos) | T005/T014/T015 | H | A23; L 1,2,3,4,5,6,7,10 (+15) |
| `frontend/.npmrc` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `frontend/index.html` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `frontend/openapi.json` | ES/EN (candidatos) | T019/T007/T008 | E3 | A433; L 118,177,216,253,256,291,339,393 (+425) |
| `frontend/package-lock.json` | Técnico/dependencias | T005/T010/T019 | E8 | A0; L — |
| `frontend/package.json` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `frontend/src/Chat.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A49; L 12,16,28,30,34,38,44,45 (+41) |
| `frontend/src/ChatCommand.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A16; L 14,15,17,18,20,23,30,32 (+8) |
| `frontend/src/Logs.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A8; L 5,6,10,17,21,22,23,27 |
| `frontend/src/Permissions.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A16; L 7,11,28,39,40,41,42,43 (+8) |
| `frontend/src/Phases.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A92; L 9,11,21,22,30,32,33,34 (+84) |
| `frontend/src/Prompts.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A29; L 7,13,22,23,24,26,27,45 (+21) |
| `frontend/src/SessionGate.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A19; L 10,13,23,29,30,40,49,62 (+11) |
| `frontend/src/Shell.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A17; L 14,25,33,35,37,38,45,46 (+9) |
| `frontend/src/Tests.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A21; L 7,10,11,14,19,22,23,24 (+13) |
| `frontend/src/api.generated.ts` | ES/EN (candidatos) | T019/T007/T008 | E3 | A292; L 310,330,384,487,525,562,582,602 (+284) |
| `frontend/src/api.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A1; L 18 |
| `frontend/src/charts.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A8; L 5,6,27,43,75,85,123,166 |
| `frontend/src/chat-commands.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A3; L 3,8,11 |
| `frontend/src/diff.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A12; L 1,2,16,46,47,54,73,78 (+4) |
| `frontend/src/legacy.tsx` | ES/EN (candidatos) | T019 | R | A65; L 80,86,87,95,97,98,104,106 (+57) |
| `frontend/src/main.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A6; L 21,23,27,38,39,42 |
| `frontend/src/managed-api.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A12; L 4,49,50,51,56,58,59,70 (+4) |
| `frontend/src/markdown.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A36; L 1,3,4,5,6,7,8,19 (+28) |
| `frontend/src/mermaid-view.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A7; L 2,3,8,14,21,36,39 |
| `frontend/src/metrics.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A27; L 1,2,7,11,15,16,20,21 (+19) |
| `frontend/src/navigation.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A2; L 6,29 |
| `frontend/src/pages/Docs.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A103; L 13,14,20,26,27,30,38,40 (+95) |
| `frontend/src/pages/Home.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A15; L 12,13,15,17,20,21,22,23 (+7) |
| `frontend/src/pages/Phases.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A24; L 16,17,18,19,20,22,45,52 (+16) |
| `frontend/src/pages/Planning.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A193; L 15,16,32,33,40,53,55,61 (+185) |
| `frontend/src/pages/Preparation.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A18; L 41,43,44,45,48,49,50,55 (+10) |
| `frontend/src/pages/Project.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A23; L 12,13,23,28,30,36,44,45 (+15) |
| `frontend/src/pages/Registry.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A126; L 8,9,12,22,23,24,26,27 (+118) |
| `frontend/src/pages/Run.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A49; L 14,21,22,23,26,27,43,70 (+41) |
| `frontend/src/pages/Settings.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A16; L 8,9,11,18,19,24,25,27 (+8) |
| `frontend/src/pages/Stats.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A104; L 11,12,28,31,49,58,59,60 (+96) |
| `frontend/src/pages/Task.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A6; L 8,19,21,25,27,30 |
| `frontend/src/pages/shared.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A28; L 12,13,14,15,16,19,21,22 (+20) |
| `frontend/src/preparation.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A8; L 6,10,11,12,13,15,19,20 |
| `frontend/src/router.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A23; L 1,2,33,46,50,56,77,102 (+15) |
| `frontend/src/session.ts` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `frontend/src/styles.css` | ES/EN (candidatos) | T005/T010/T019 | U | A18; L 1,31,138,157,192,199,221,241 (+10) |
| `frontend/src/task-sources.ts` | ES/EN (candidatos) | T005/T010/T019 | U | A4; L 1,6,12,17 |
| `frontend/src/ui.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A20; L 6,8,14,17,24,38,48,54 (+12) |
| `frontend/src/workspace.tsx` | ES/EN (candidatos) | T005/T010/T019 | U | A11; L 9,10,23,30,48,52,59,62 (+3) |
| `frontend/tests/chat-commands.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A6; L 6,7,10,13,16,17 |
| `frontend/tests/diff.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A6; L 5,33,34,43,71,92 |
| `frontend/tests/managed-api.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A4; L 124,126,130,160 |
| `frontend/tests/markdown.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A23; L 8,20,23,32,52,56,77,80 (+15) |
| `frontend/tests/metrics.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A9; L 5,6,13,18,19,23,45,49 (+1) |
| `frontend/tests/preparation.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A5; L 10,17,19,20,21 |
| `frontend/tests/router.test.mjs` | ES/EN (candidatos) | T006/T010/T019 | F | A14; L 48,67,70,83,88,96,101,102 (+6) |
| `frontend/tests/task-sources.test.mjs` | EN/técnico (sin candidatos) | T006/T010/T019 | F | A0; L — |
| `frontend/tsconfig.json` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `frontend/vite.config.ts` | EN/técnico (sin candidatos) | T005/T010/T019 | U | A0; L — |
| `pyproject.toml` | ES/EN (candidatos) | T002/T005/T015 | H | A1; L 27 |
| `scripts/build_distribution.py` | ES/EN (candidatos) | T005/T014/T015 | H | C0/D1/S0; L 1 |
| `scripts/check_distribution.py` | ES/EN (candidatos) | T005/T014/T015 | H | C4/D1/S5; L 1,47,48,92,96,115,147,246 (+2) |
| `scripts/dev` | ES/EN (candidatos) | T005/T014/T015 | H | A1; L 2 |
| `scripts/dev.py` | ES/EN (candidatos) | T005/T014/T015 | H | C1/D4/S9; L 1,67,83,119,124,141,154,168 (+6) |
| `scripts/export_openapi.py` | ES/EN (candidatos) | T005/T014/T015 | H | C0/D1/S0; L 1 |
| `scripts/smoke_cli.py` | EN/técnico (sin candidatos) | T005/T014/T015 | H | C0/D0/S0; L — |
| `scripts/toolchain.py` | ES/EN (candidatos) | T005/T014/T015 | H | C0/D1/S2; L 1,12,14 |
| `src/harness_local/__init__.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/adapters/__init__.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/adapters/bootstrap.py` | ES/EN (candidatos) | T004/T010 | C | C10/D4/S1; L 1,30,34,43,64,90,126,166 (+7) |
| `src/harness_local/adapters/chat_snapshot.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S1; L 1,32 |
| `src/harness_local/adapters/cli_agents.py` | ES/EN (candidatos) | T004/T010 | C | C4/D0/S0; L 54,60,64,68 |
| `src/harness_local/adapters/cli_diagnostics.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S11; L 37,38,39,40,41,42,43,44 (+3) |
| `src/harness_local/adapters/commands.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S1; L 231 |
| `src/harness_local/adapters/engine_fake.py` | ES/EN (candidatos) | T004/T010 | C | C0/D2/S0; L 1,47 |
| `src/harness_local/adapters/evidence.py` | ES/EN (candidatos) | T019 | R | C3/D1/S8; L 1,24,26,29,42,44,50,56 (+4) |
| `src/harness_local/adapters/fake.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S2; L 7,9 |
| `src/harness_local/adapters/git.py` | ES/EN (candidatos) | T004/T010 | C | C17/D18/S0; L 1,40,44,62,99,117,132,142 (+27) |
| `src/harness_local/adapters/legacy.py` | ES/EN (candidatos) | T019 | R | C4/D1/S14; L 1,46,67,70,75,79,89,92 (+11) |
| `src/harness_local/adapters/local_git.py` | ES/EN (candidatos) | T004/T010 | C | C5/D3/S0; L 1,8,12,13,14,21,32,45 |
| `src/harness_local/adapters/migration.py` | ES/EN (candidatos) | T019/T004 | G | C0/D8/S6; L 1,21,48,78,85,89,91,102 (+6) |
| `src/harness_local/adapters/preparation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S2; L 127,142 |
| `src/harness_local/adapters/process_gate.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/adapters/processes.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/adapters/project_import.py` | ES/EN (candidatos) | T019/T004 | G | C0/D8/S0; L 1,30,43,67,73,87,103,192 |
| `src/harness_local/adapters/project_onboarding.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,27 |
| `src/harness_local/adapters/streams.py` | ES/EN (candidatos) | T004/T010 | C | C1/D0/S1; L 26,72 |
| `src/harness_local/api/__init__.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/api/app.py` | ES/EN (candidatos) | T004/T010 | C | C0/D2/S2; L 30,74,117,130 |
| `src/harness_local/api/documents.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S1; L 1,27,37 |
| `src/harness_local/api/events.py` | ES/EN (candidatos) | T019 | R | C0/D1/S0; L 1 |
| `src/harness_local/api/legacy.py` | ES/EN (candidatos) | T019 | R | C0/D0/S2; L 58,126 |
| `src/harness_local/api/managed.py` | ES/EN (candidatos) | T004/T010 | C | C15/D47/S18; L 1,39,94,105,125,136,140,162 (+72) |
| `src/harness_local/api/schemas.py` | ES/EN (candidatos) | T004/T010 | C | C6/D8/S75; L 72,96,137,158,159,170,192,194 (+78) |
| `src/harness_local/api/security.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S4; L 1,30,33,44,46 |
| `src/harness_local/api/session.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S7; L 50,76,82,85,89,111,116 |
| `src/harness_local/cli.py` | ES/EN (candidatos) | T004/T010 | C | C2/D1/S24; L 1,20,24,25,26,28,32,36 (+19) |
| `src/harness_local/core/__init__.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/core/engine/__init__.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/core/engine/acceptance.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D3/S0; L 1,19,33 |
| `src/harness_local/core/engine/bootstrap.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/core/engine/bootstrap_discovery.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/core/engine/chat.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D4/S0; L 1,41,62,81 |
| `src/harness_local/core/engine/chat_commands.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S10; L 1,2,12,13,15,20,23 |
| `src/harness_local/core/engine/commit.py` | ES/EN (candidatos) | T003/T009/T010 | C | C4/D9/S0; L 1,27,31,48,63,68,100,142 (+5) |
| `src/harness_local/core/engine/context.py` | ES/EN (candidatos) | T003/T009/T010 | C | C10/D2/S0; L 1,51,52,56,57,80,81,82 (+4) |
| `src/harness_local/core/engine/contracts.py` | ES/EN (candidatos) | T003/T009/T010 | C | C5/D3/S1; L 1,32,47,109,135,191,193,233 (+1) |
| `src/harness_local/core/engine/definition.py` | ES/EN (candidatos) | T003/T009/T010 | C | C5/D10/S17; L 1,33,39,52,65,78,88,98 (+23) |
| `src/harness_local/core/engine/document_export.py` | ES/EN (candidatos) | T003/T009/T010 | C | C3/D5/S1; L 1,22,27,28,29,37,40,44 (+1) |
| `src/harness_local/core/engine/document_ops.py` | ES/EN (candidatos) | T003/T009/T010 | C | C10/D8/S10; L 1,30,67,97,102,107,138,139 (+18) |
| `src/harness_local/core/engine/documents.py` | ES/EN (candidatos) | T003/T009/T010 | C | C10/D23/S110; L 1,21,23,30,32,36,39,40 (+120) |
| `src/harness_local/core/engine/evidence.py` | ES/EN (candidatos) | T003/T009/T010 | C | C2/D1/S0; L 1,16,17 |
| `src/harness_local/core/engine/import_commit.py` | ES/EN (candidatos) | T019/T004 | G | C0/D3/S0; L 1,20,54 |
| `src/harness_local/core/engine/import_conversation.py` | ES/EN (candidatos) | T019 | R | C2/D4/S1; L 1,20,56,69,91,98,152 |
| `src/harness_local/core/engine/journal.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 12 |
| `src/harness_local/core/engine/junit.py` | ES/EN (candidatos) | T003/T009/T010 | C | C2/D2/S5; L 1,57,83,174,179,181,195,204 |
| `src/harness_local/core/engine/metrics.py` | ES/EN (candidatos) | T003/T009/T010 | C | C9/D5/S3; L 1,19,23,35,38,43,60,65 (+9) |
| `src/harness_local/core/engine/onboarding_commit.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S3; L 1,54,67,68 |
| `src/harness_local/core/engine/permissions.py` | EN/técnico (sin candidatos) | T003/T009/T010 | C | C0/D0/S0; L — |
| `src/harness_local/core/engine/phases.py` | ES/EN (candidatos) | T003/T009/T010 | C | C1/D8/S0; L 1,30,47,67,85,91,124,170 (+1) |
| `src/harness_local/core/engine/planning.py` | ES/EN (candidatos) | T003/T009/T010 | C | C2/D2/S8; L 1,9,15,17,19,20,21,23 (+2) |
| `src/harness_local/core/engine/prompts.py` | ES/EN (candidatos) | T003/T009/T010 | C | C11/D1/S0; L 10,11,12,26,33,34,53,54 (+4) |
| `src/harness_local/core/engine/review.py` | ES/EN (candidatos) | T003/T009/T010 | C | C4/D1/S0; L 1,12,13,14,65 |
| `src/harness_local/core/engine/serialization.py` | ES/EN (candidatos) | T003/T009/T010 | C | C1/D1/S0; L 1,60 |
| `src/harness_local/core/engine/templates/bootstrap-project.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/chat-turn.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/close-phase.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/define-project.md` | ES/EN (candidatos) | T009 | P | A4; L 5,6,7,8 |
| `src/harness_local/core/engine/templates/execute-task.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/executor-routing.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/import-project.md` | ES/EN (candidatos) | T019 | R | A3; L 14,15,16 |
| `src/harness_local/core/engine/templates/onboard-project.md` | ES/EN (candidatos) | T009 | P | A5; L 12,15,17,18,19 |
| `src/harness_local/core/engine/templates/plan-phase.md` | ES/EN (candidatos) | T009 | P | A1; L 8 |
| `src/harness_local/core/engine/templates/plan-task.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/reconcile-phase.md` | ES/EN (candidatos) | T009 | P | A1; L 9 |
| `src/harness_local/core/engine/templates/review-task.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/templates/revise-task.md` | EN/técnico (sin candidatos) | T009 | P | A0; L — |
| `src/harness_local/core/engine/validation.py` | ES/EN (candidatos) | T003/T009/T010 | C | C4/D2/S1; L 1,67,68,71,76,123,150 |
| `src/harness_local/core/engine/workflow.py` | ES/EN (candidatos) | T003/T009/T010 | C | C6/D9/S0; L 1,28,48,58,69,82,130,134 (+7) |
| `src/harness_local/core/evidence.py` | ES/EN (candidatos) | T019 | R | C0/D2/S1; L 1,8,31 |
| `src/harness_local/core/legacy.py` | ES/EN (candidatos) | T019 | R | C0/D1/S1; L 1,96 |
| `src/harness_local/core/migration.py` | ES/EN (candidatos) | T019/T004 | G | C6/D10/S14; L 1,25,28,29,30,31,45,54 (+19) |
| `src/harness_local/core/project_import.py` | ES/EN (candidatos) | T019 | R | C5/D11/S2; L 1,22,35,44,45,46,53,58 (+10) |
| `src/harness_local/core/project_normalization.py` | ES/EN (candidatos) | T019 | R | C4/D14/S0; L 1,20,41,49,62,71,81,103 (+10) |
| `src/harness_local/core/project_onboarding.py` | ES/EN (candidatos) | T003/T009/T010 | C | C12/D2/S0; L 1,32,81,82,93,164,197,209 (+6) |
| `src/harness_local/core/simulation.py` | ES/EN (candidatos) | T003/T010 | C | C1/D1/S1; L 1,35,36 |
| `src/harness_local/launcher.py` | ES/EN (candidatos) | T004/T010 | C | C3/D1/S8; L 1,16,22,25,31,44,47,49 (+4) |
| `src/harness_local/migrations/env.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/script.py.mako` | EN/técnico (sin candidatos) | T004/T010 | C | A0; L — |
| `src/harness_local/migrations/versions/0001_simulations.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0002_legacy_index.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0003_legacy_observation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0004_managed_queue.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0005_cli_processes.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0006_git_commits.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0007_managed_activation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0008_prompt_versions.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0009_permissions.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0010_phases.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,80 |
| `src/harness_local/migrations/versions/0011_phase_amendments.py` | ES/EN (candidatos) | T004/T010 | C | C3/D1/S0; L 1,19,35,36 |
| `src/harness_local/migrations/versions/0012_chat.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0013_bootstrap.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0014_attempt_metrics.py` | ES/EN (candidatos) | T004/T010 | C | C2/D1/S1; L 1,31,66,67 |
| `src/harness_local/migrations/versions/0015_planning.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0016_project_registry.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0017_chat_context.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/migrations/versions/0018_conversation_keys.py` | ES/EN (candidatos) | T004/T010 | C | C2/D1/S0; L 1,15,23 |
| `src/harness_local/migrations/versions/0019_import_conversations.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,12 |
| `src/harness_local/migrations/versions/0020_project_imports.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0021_project_creation.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,56 |
| `src/harness_local/migrations/versions/0022_project_preparation.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/migrations/versions/0023_run_projection.py` | ES/EN (candidatos) | T004/T010 | C | C1/D2/S0; L 1,16,81 |
| `src/harness_local/profiles/__init__.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/profiles/reference_project.py` | ES/EN (candidatos) | T003/T009/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/profiles/typescript_web.py` | ES/EN (candidatos) | T003/T009/T010 | C | C1/D1/S1; L 1,20,21 |
| `src/harness_local/recipes/__init__.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/recipes/django-packages.json` | EN/técnico (sin candidatos) | T004/T008/T009 | E1 | A0; L — |
| `src/harness_local/recipes/django-requirements.lock` | EN/técnico (sin candidatos) | T004/T008/T009 | E1 | A0; L — |
| `src/harness_local/recipes/django.py` | ES/EN (candidatos) | T004/T008/T009 | E1 | C0/D0/S14; L 105,122,131,208,247,249,250,251 (+6) |
| `src/harness_local/recipes/typescript_web.py` | ES/EN (candidatos) | T004/T008/T009 | E1 | C0/D0/S6; L 66,80,90,126,127,129 |
| `src/harness_local/services/__init__.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/services/local_config.py` | ES/EN (candidatos) | T004/T010 | C | C11/D1/S55; L 62,63,85,91,97,110,122,128 (+59) |
| `src/harness_local/services/managed.py` | ES/EN (candidatos) | T004/T010 | C | C9/D3/S0; L 1,81,129,148,155,219,223,276 (+4) |
| `src/harness_local/services/managed_runtime.py` | ES/EN (candidatos) | T004/T010 | C | C5/D9/S10; L 1,37,43,45,63,77,82,88 (+16) |
| `src/harness_local/services/migration.py` | ES/EN (candidatos) | T019/T004 | G | C2/D8/S10; L 1,31,47,67,74,78,86,95 (+11) |
| `src/harness_local/services/observation.py` | ES/EN (candidatos) | T019 | R | C1/D1/S2; L 1,34,43,54 |
| `src/harness_local/services/project_creation.py` | ES/EN (candidatos) | T004/T010 | C | C3/D3/S47; L 1,22,32,35,41,68,80,82 (+45) |
| `src/harness_local/services/project_preparation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S40; L 113,134,138,177,228,231,245,289 (+30) |
| `src/harness_local/services/project_registry.py` | ES/EN (candidatos) | T004/T010 | C | C5/D6/S28; L 1,22,25,40,65,67,70,72 (+31) |
| `src/harness_local/storage/__init__.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/storage/backup.py` | ES/EN (candidatos) | T004/T010 | C | C8/D5/S44; L 1,40,46,53,58,71,73,78 (+48) |
| `src/harness_local/storage/bootstrap.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,45 |
| `src/harness_local/storage/bootstrap_discovery.py` | ES/EN (candidatos) | T004/T010 | C | C0/D2/S0; L 1,44 |
| `src/harness_local/storage/chat.py` | ES/EN (candidatos) | T004/T010 | C | C1/D9/S1; L 1,42,105,124,168,211,220,223 (+3) |
| `src/harness_local/storage/closure.py` | ES/EN (candidatos) | T004/T010 | C | C1/D1/S0; L 1,27 |
| `src/harness_local/storage/command_processes.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/storage/database.py` | ES/EN (candidatos) | T004/T010 | C | C1/D0/S2; L 15,16,34 |
| `src/harness_local/storage/document_export.py` | ES/EN (candidatos) | T004/T010 | C | C4/D3/S0; L 1,33,91,121,129,222,223 |
| `src/harness_local/storage/documents.py` | ES/EN (candidatos) | T004/T010 | C | C6/D10/S2; L 1,70,84,120,173,177,223,227 (+10) |
| `src/harness_local/storage/import_drafts.py` | ES/EN (candidatos) | T019 | R | C0/D6/S0; L 1,33,42,61,93,121 |
| `src/harness_local/storage/legacy.py` | ES/EN (candidatos) | T019 | R | C0/D2/S4; L 16,20,32,44,66 |
| `src/harness_local/storage/managed.py` | ES/EN (candidatos) | T004/T010 | C | C6/D20/S1; L 1,89,104,143,155,174,191,202 (+19) |
| `src/harness_local/storage/managed_views.py` | ES/EN (candidatos) | T004/T010 | C | C1/D9/S4; L 1,52,93,94,110,122,141,184 (+6) |
| `src/harness_local/storage/metrics.py` | ES/EN (candidatos) | T004/T010 | C | C9/D12/S7; L 1,28,31,36,42,46,51,65 (+20) |
| `src/harness_local/storage/migrate.py` | ES/EN (candidatos) | T004/T010 | C | C1/D3/S16; L 1,61,63,92,98,101,109,117 (+11) |
| `src/harness_local/storage/migration.py` | ES/EN (candidatos) | T019/T004 | G | C4/D13/S19; L 1,75,76,81,85,87,98,119 (+25) |
| `src/harness_local/storage/models.py` | ES/EN (candidatos) | T004/T010 | C | C16/D21/S0; L 85,93,142,202,224,255,276,362 (+29) |
| `src/harness_local/storage/navigation.py` | ES/EN (candidatos) | T019 | R | C7/D1/S1; L 1,42,43,61,72,95,135,145 (+1) |
| `src/harness_local/storage/observation.py` | ES/EN (candidatos) | T019 | R | C0/D1/S4; L 1,26,29,42,58 |
| `src/harness_local/storage/onboarding.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/storage/onboarding_commit.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/storage/permissions.py` | ES/EN (candidatos) | T004/T010 | C | C1/D0/S0; L 50 |
| `src/harness_local/storage/phase_plan.py` | ES/EN (candidatos) | T004/T010 | C | C0/D1/S0; L 1 |
| `src/harness_local/storage/phases.py` | ES/EN (candidatos) | T004/T010 | C | C15/D26/S2; L 1,37,40,63,74,88,105,143 (+35) |
| `src/harness_local/storage/planning.py` | ES/EN (candidatos) | T004/T010 | C | C6/D21/S0; L 1,58,82,97,106,116,143,154 (+19) |
| `src/harness_local/storage/preparation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S2; L 145,153 |
| `src/harness_local/storage/project_creation.py` | ES/EN (candidatos) | T004/T010 | C | C0/D2/S4; L 1,53,70,73,76,78 |
| `src/harness_local/storage/project_import.py` | ES/EN (candidatos) | T019/T004 | G | C1/D2/S0; L 1,36,39 |
| `src/harness_local/storage/prompts.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/storage/registry.py` | ES/EN (candidatos) | T004/T010 | C | C0/D3/S13; L 1,78,85,87,89,92,101,103 (+7) |
| `src/harness_local/storage/repository.py` | EN/técnico (sin candidatos) | T004/T010 | C | C0/D0/S0; L — |
| `src/harness_local/storage/retention.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S39; L 24,27,33,45,48,56,59,63 (+30) |
| `src/harness_local/storage/run_projection.py` | ES/EN (candidatos) | T004/T010 | C | C3/D7/S7; L 1,25,27,48,105,127,132,142 (+9) |
| `src/harness_local/storage/schema.py` | ES/EN (candidatos) | T004/T010 | C | C0/D0/S1; L 14 |
| `src/harness_local/storage/transition.py` | ES/EN (candidatos) | T004/T010 | C | C1/D3/S0; L 1,27,42,145 |
| `tests/conftest.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S0; L 11 |
| `tests/fixtures/cli_help/README.md` | ES/EN (candidatos) | T006 | F | A4; L 3,4,5,6 |
| `tests/fixtures/cli_help/claude-2.1.304-help.txt` | ES/EN (candidatos) | T006 | F | A1; L 179 |
| `tests/fixtures/cli_help/codex-0.163.0-exec-help.txt` | ES/EN (candidatos) | T006 | F | A1; L 34 |
| `tests/fixtures/e2e/installed_config.py` | ES/EN (candidatos) | T006 | F | C0/D0/S4; L 23,26,28,30 |
| `tests/fixtures/junit/complete.xml` | ES/EN (candidatos) | T006 | F | A1; L 6 |
| `tests/fixtures/junit/invalid.xml` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/junit/partial.xml` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/legacy/README.md` | ES/EN (candidatos) | T019/T006 | E2/R | A29; L 1,3,5,6,8,9,11,13 (+21) |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.result.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.result.request.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.result.usage.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 5 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/claude-00.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/diff-00.patch` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/policy-00.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/review-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A4; L 4,7,9,13 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/task.json` | ES/EN (candidatos) | T019/T006 | E2/R | A7; L 4,5,6,18,21,30,34 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/validation-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/validation-00/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/accepted/.harness/runs/20000101T120000+0000_P900-T001/validation-00/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/accepted/docs/STATE.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 9 |
| `tests/fixtures/legacy/accepted/synthetic-git-log.txt` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 2 |
| `tests/fixtures/legacy/baseline.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.result.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.result.request.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.result.usage.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-00.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.result.events.jsonl` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 2 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.result.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 5 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.result.request.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.result.usage.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/claude-01.stderr.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/diff-00.patch` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/policy-00.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/resume-01.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/review-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A5; L 4,7,9,13,16 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/stop-01.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/task.json` | ES/EN (candidatos) | T019/T006 | E2/R | A6; L 4,5,6,18,21,30 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/validation-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/validation-00/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/blocked/.harness/runs/20000101T120000+0000_P900-T003/validation-00/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T110000+0000_P900-RECONCILE/reconcile.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 3 |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T120000+0000_P900-CLOSE/phase-review.json` | ES/EN (candidatos) | T019/T006 | E2/R | A6; L 5,10,15,16,18,19 |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T120000+0000_P900-CLOSE/phase-review.meta.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T120000+0000_P900-CLOSE/validation-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T120000+0000_P900-CLOSE/validation-00/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/closed-phase/.harness/runs/20000101T120000+0000_P900-CLOSE/validation-00/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/closed-phase/docs/NEXT_STEPS.md` | ES/EN (candidatos) | T019/T006 | E2/R | A2; L 1,5 |
| `tests/fixtures/legacy/closed-phase/docs/ROADMAP.md` | ES/EN (candidatos) | T019/T006 | E2/R | A2; L 1,7 |
| `tests/fixtures/legacy/closed-phase/docs/STATE.md` | ES/EN (candidatos) | T019/T006 | E2/R | A2; L 3,9 |
| `tests/fixtures/legacy/closed-phase/docs/archive/phase-900/NEXT_STEPS.md` | ES/EN (candidatos) | T019/T006 | E2/R | A2; L 7,8 |
| `tests/fixtures/legacy/closed-phase/docs/archive/phase-900/REVIEW.md` | ES/EN (candidatos) | T019/T006 | E2/R | A2; L 1,3 |
| `tests/fixtures/legacy/closed-phase/docs/archive/phase-900/SUMMARY.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 3 |
| `tests/fixtures/legacy/closed-phase/synthetic-git-log.txt` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T120000+0000_P900-T004/claude-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T120000+0000_P900-T004/claude-00.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T120000+0000_P900-T004/claude-00.result.request.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T120000+0000_P900-T004/task.json` | ES/EN (candidatos) | T019/T006 | E2/R | A7; L 4,5,6,18,21,30,34 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.result.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.result.request.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.result.usage.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 5 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/claude-00.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/diff-00.patch` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/policy-00.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/review-00.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/review-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/task.json` | ES/EN (candidatos) | T019/T006 | E2/R | A7; L 4,5,6,18,21,30,34 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/validation-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/validation-00/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/interrupted/.harness/runs/20000101T130000+0000_P900-T004/validation-00/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/manifest.json` | ES/EN (candidatos) | T019/T006 | E2/R | A6; L 3,6,13,20,30,45 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.result.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.result.request.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.result.usage.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 5 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-00.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.prompt.md` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.result.events.jsonl` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.result.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.result.request.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 4 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.result.usage.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 5 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/claude-01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/diff-00.patch` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 7 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/diff-01.patch` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/policy-00.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/policy-01.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/review-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A8; L 4,7,9,18,19,23,26,30 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/review-01.json` | ES/EN (candidatos) | T019/T006 | E2/R | A4; L 4,7,9,13 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/task.json` | ES/EN (candidatos) | T019/T006 | E2/R | A7; L 4,5,6,18,21,30,34 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-00.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-00/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-00/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-01.json` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 11 |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-01/01.stderr.log` | Vacío | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/revise/.harness/runs/20000101T120000+0000_P900-T002/validation-01/01.stdout.log` | ES/EN (candidatos) | T019/T006 | E2/R | A1; L 1 |
| `tests/fixtures/legacy/schemas/phase.schema.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/schemas/reconcile.schema.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/schemas/review.schema.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/legacy/schemas/task.schema.json` | EN/técnico (sin candidatos) | T019/T006 | E2/R | A0; L — |
| `tests/fixtures/streams/README.md` | ES/EN (candidatos) | T006/T012 | E2 | A22; L 1,3,5,6,8,9,10,13 (+14) |
| `tests/fixtures/streams/claude-error.jsonl` | ES/EN (candidatos) | T006/T012 | E2 | A1; L 2 |
| `tests/fixtures/streams/claude-no-terminal.jsonl` | EN/técnico (sin candidatos) | T006/T012 | E2 | A0; L — |
| `tests/fixtures/streams/claude-success.jsonl` | ES/EN (candidatos) | T006/T012 | E2 | A3; L 1,3,4 |
| `tests/fixtures/streams/claude-truncated.jsonl` | EN/técnico (sin candidatos) | T006/T012 | E2 | A0; L — |
| `tests/fixtures/streams/codex-error.jsonl` | ES/EN (candidatos) | T006/T012 | E2 | A1; L 2 |
| `tests/fixtures/streams/codex-no-terminal.jsonl` | EN/técnico (sin candidatos) | T006/T012 | E2 | A0; L — |
| `tests/fixtures/streams/codex-success.jsonl` | ES/EN (candidatos) | T006/T012 | E2 | A2; L 1,3 |
| `tests/fixtures/streams/codex-truncated.jsonl` | EN/técnico (sin candidatos) | T006/T012 | E2 | A0; L — |
| `tests/fixtures/streams/manifest.json` | ES/EN (candidatos) | T006/T012 | E2 | A2; L 34,41 |
| `tests/fixtures/typescript_web/.gitignore` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/README.md` | ES/EN (candidatos) | T006 | F | A15; L 3,4,6,7,8,9,10,11 (+7) |
| `tests/fixtures/typescript_web/index.html` | ES/EN (candidatos) | T006 | F | A3; L 6,9,10 |
| `tests/fixtures/typescript_web/package-lock.json` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/package.json` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/scripts/build.mjs` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/scripts/test.mjs` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/src/estimate.ts` | ES/EN (candidatos) | T006 | F | A1; L 3 |
| `tests/fixtures/typescript_web/src/main.ts` | ES/EN (candidatos) | T006 | F | A3; L 5,10,11 |
| `tests/fixtures/typescript_web/tests/estimate.test.mjs` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/tests/main.test.mjs` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/fixtures/typescript_web/tsconfig.json` | EN/técnico (sin candidatos) | T006 | F | A0; L — |
| `tests/product/cli_owner_probe.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/cli_process_probe.py` | ES/EN (candidatos) | T006/T019 | F | C1/D1/S9; L 55,86,114,168,237,238,242,244 (+2) |
| `tests/product/command_supervisor_probe.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/conftest.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S0; L 14,34 |
| `tests/product/managed_process_probe.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S0; L 1 |
| `tests/product/preparation_probe.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/session_client.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/smoke_environment_probe.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_acceptance_matrix.py` | ES/EN (candidatos) | T006/T019 | F | C1/D3/S0; L 1,26,60,85 |
| `tests/product/test_agent_roles.py` | ES/EN (candidatos) | T006/T019 | F | C1/D0/S0; L 24 |
| `tests/product/test_backup.py` | ES/EN (candidatos) | T006/T019 | F | C6/D2/S11; L 1,53,71,105,126,129,143,145 (+11) |
| `tests/product/test_bootstrap.py` | ES/EN (candidatos) | T006/T019 | F | C5/D6/S3; L 1,29,38,121,141,180,194,222 (+6) |
| `tests/product/test_chat.py` | ES/EN (candidatos) | T006/T019 | F | C21/D1/S5; L 1,51,76,86,87,89,96,102 (+19) |
| `tests/product/test_chat_global.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S14; L 114,126,131,136,144,147,149,177 (+3) |
| `tests/product/test_cli_agents.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S5; L 63,222,288,544,547 |
| `tests/product/test_cli_baseline.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_cli_diagnostics.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S3; L 19,94,107 |
| `tests/product/test_cli_memory.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_codex_workspace_write.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S1; L 30 |
| `tests/product/test_commands.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S4; L 271,303,417,420 |
| `tests/product/test_contract_shapes.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_core.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S6; L 46,50,51,63,68,69 |
| `tests/product/test_cycle_diff.py` | ES/EN (candidatos) | T006/T019 | F | C5/D1/S9; L 1,26,31,36,38,40,50,65 (+4) |
| `tests/product/test_declared_profiles.py` | ES/EN (candidatos) | T006/T019 | F | C3/D3/S2; L 1,38,69,81,82,244,261,280 |
| `tests/product/test_definition.py` | ES/EN (candidatos) | T006/T019 | F | C20/D5/S56; L 1,30,33,34,35,36,37,38 (+69) |
| `tests/product/test_definition_git_check.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S2; L 133,172 |
| `tests/product/test_dev_command.py` | ES/EN (candidatos) | T006/T019 | F | C2/D1/S0; L 1,116,129 |
| `tests/product/test_directory_paths.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_django_journey.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S4; L 34,127,128,130 |
| `tests/product/test_document_export.py` | ES/EN (candidatos) | T006/T019 | F | C6/D1/S0; L 1,126,229,268,288,322,339 |
| `tests/product/test_document_viewer.py` | ES/EN (candidatos) | T006/T019 | F | C3/D2/S22; L 1,26,39,48,60,82,125,150 (+16) |
| `tests/product/test_documentation_parity.py` | ES/EN (candidatos) | T006/T019 | F | C4/D2/S7; L 1,24,25,29,37,61,68,105 (+4) |
| `tests/product/test_documents.py` | ES/EN (candidatos) | T006/T019 | F | C15/D3/S67; L 1,33,36,43,53,58,74,85 (+73) |
| `tests/product/test_e2e_offline.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S2; L 213,228,232 |
| `tests/product/test_engine.py` | ES/EN (candidatos) | T006/T019 | F | C1/D1/S3; L 1,162,181,340,460 |
| `tests/product/test_git.py` | ES/EN (candidatos) | T006/T019 | F | C20/D3/S0; L 1,166,202,255,294,327,336,357 (+15) |
| `tests/product/test_import_commit.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S4; L 1,38,40,193,196 |
| `tests/product/test_import_conversation.py` | ES/EN (candidatos) | T006/T019 | F | C7/D3/S22; L 1,37,38,41,46,71,75,97 (+24) |
| `tests/product/test_import_git_boundary.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S0; L 1,24 |
| `tests/product/test_import_local_objects.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S0; L 1,27 |
| `tests/product/test_import_submodules.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S0; L 1,29 |
| `tests/product/test_import_writer_local_objects.py` | ES/EN (candidatos) | T006/T019 | F | C4/D2/S0; L 1,23,73,110,125,152 |
| `tests/product/test_installed_migration.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S2; L 172,196 |
| `tests/product/test_junit.py` | ES/EN (candidatos) | T006/T019 | F | C4/D1/S1; L 1,65,228,298,362,387 |
| `tests/product/test_launcher.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_legacy_import.py` | ES/EN (candidatos) | T006/T019 | F | C4/D0/S10; L 51,69,117,140,147,154,192,201 (+5) |
| `tests/product/test_legacy_navigation.py` | ES/EN (candidatos) | T006/T019 | F | C3/D0/S4; L 61,78,116,117,234,243,350 |
| `tests/product/test_legacy_observation.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S4; L 219,220,232,236 |
| `tests/product/test_local_config.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S0; L 114 |
| `tests/product/test_managed.py` | ES/EN (candidatos) | T006/T019 | F | C6/D1/S2; L 1,153,239,273,373,504,529,591 (+1) |
| `tests/product/test_managed_api.py` | ES/EN (candidatos) | T006/T019 | F | C10/D3/S10; L 1,46,84,123,257,298,327,342 (+15) |
| `tests/product/test_metrics.py` | ES/EN (candidatos) | T006/T019 | F | C19/D5/S7; L 1,48,87,101,112,130,157,168 (+21) |
| `tests/product/test_metrics_projection.py` | ES/EN (candidatos) | T006/T019 | F | C13/D4/S10; L 1,43,102,110,123,126,140,146 (+18) |
| `tests/product/test_migration.py` | ES/EN (candidatos) | T006/T019 | F | C11/D4/S16; L 1,56,60,82,110,176,199,223 (+23) |
| `tests/product/test_onboarding_commit.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S3; L 1,31,166,239 |
| `tests/product/test_onboarding_conversation.py` | ES/EN (candidatos) | T006/T019 | F | C1/D1/S12; L 1,21,39,41,42,43,44,45 (+6) |
| `tests/product/test_permissions.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_phase_adjustments.py` | ES/EN (candidatos) | T006/T019 | F | C20/D2/S3; L 1,40,62,68,77,80,100,107 (+17) |
| `tests/product/test_phase_closure.py` | ES/EN (candidatos) | T006/T019 | F | C6/D1/S12; L 1,66,70,166,167,197,224,241 (+8) |
| `tests/product/test_phases.py` | ES/EN (candidatos) | T006/T019 | F | C10/D1/S1; L 1,56,179,239,279,289,308,376 (+4) |
| `tests/product/test_profile_formatter.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S1; L 159 |
| `tests/product/test_project_agents.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S1; L 1,51,284 |
| `tests/product/test_project_creation.py` | ES/EN (candidatos) | T006/T019 | F | C5/D1/S2; L 1,145,307,312,353,505,533,549 |
| `tests/product/test_project_import.py` | ES/EN (candidatos) | T006/T019 | F | C4/D2/S3; L 1,108,113,117,174,193,231,256 (+1) |
| `tests/product/test_project_instructions.py` | ES/EN (candidatos) | T006/T019 | F | C3/D2/S2; L 1,37,85,104,121,123,152 |
| `tests/product/test_project_normalization.py` | ES/EN (candidatos) | T006/T019 | F | C2/D2/S8; L 1,49,57,114,160,186,193,195 (+4) |
| `tests/product/test_project_onboarding.py` | ES/EN (candidatos) | T006/T019 | F | C2/D1/S1; L 1,67,153,284 |
| `tests/product/test_project_preparation.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S4; L 140,398,520,525 |
| `tests/product/test_project_registry.py` | ES/EN (candidatos) | T006/T019 | F | C7/D4/S2; L 1,101,115,124,161,197,249,266 (+5) |
| `tests/product/test_prompts.py` | ES/EN (candidatos) | T006/T019 | F | C1/D0/S0; L 60 |
| `tests/product/test_retention.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S3; L 163,257,325 |
| `tests/product/test_run_projection.py` | ES/EN (candidatos) | T006/T019 | F | C10/D3/S11; L 1,46,74,110,115,122,138,139 (+14) |
| `tests/product/test_session.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_smoke_environment.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_storage_api.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S5; L 39,44,54,87,89 |
| `tests/product/test_task_sources.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S4; L 1,27,52,120,126 |
| `tests/product/test_typed_json_schema.py` | EN/técnico (sin candidatos) | T006/T019 | F | C0/D0/S0; L — |
| `tests/product/test_typescript_preparation.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S10; L 169,170,448,506,590,591,592 |
| `tests/product/test_typescript_profile.py` | ES/EN (candidatos) | T006/T019 | F | C4/D2/S4; L 1,54,92,93,122,135,203,219 (+2) |
| `tests/product/test_ui_routes.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S1; L 1,18 |
| `tests/product/typescript_preparation_probe.py` | ES/EN (candidatos) | T006/T019 | F | C0/D0/S2; L 33,52 |
| `tests/stream_probe.py` | ES/EN (candidatos) | T006/T019 | F | C0/D2/S2; L 1,9,30,79 |
| `tests/test_legacy_fixtures.py` | ES/EN (candidatos) | T006/T019 | F | C1/D1/S0; L 1,93 |
| `tests/test_stream_contracts.py` | ES/EN (candidatos) | T006/T019 | F | C0/D1/S2; L 1,38,55 |
| `uv.lock` | Técnico/dependencias | T002/T005/T015 | E8 | A0; L — |

## Grupos históricos excluidos del corte inicial

No se ha revisado su contenido en T001. No se atribuye validación nueva a sus evidencias.

| Grupo | Archivos | Idioma/tratamiento | Propietaria |
|---|---:|---|---|
| `docs/archive/phase-000/**` | 5 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-001/**` | 8 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-002/**` | 6 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-003/**` | 18 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-004/**` | 7 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-005/**` | 7 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-006/**` | 16 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-007/**` | 49 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-008/**` | 39 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-009/**` | 32 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |
| `docs/archive/phase-010/**` | 32 | Original histórico; E4, sin traducción/copia pública | T002/T014/T018 |

## Identificadores

Revisión de los candidatos AST: la palabra compartida `error` explica todos los falsos positivos de nombres;
no justifica cambios en variables, campos persistidos o tests ingleses. Se agrupan sus repeticiones para evitar
confundirlas con nombres españoles que deban traducirse.

| Candidatos | Observaciones de la base | Tratamiento |
|---|---:|---|
| Nombres `error`, `write_error`, `last_error`, `error_type`, `git_error`, `marker_error` y tests que contienen `error` | 158 ubicaciones AST | Inglés/término compartido; conservar. |
| `tests/product/test_chat_global.py:139`: `test_tarea_is_idempotent_proposal_without_snapshot_or_agent` | 1 | T006 puede traducir el nombre interno; conservar el literal/comando `tarea` y su cobertura. |

No se detectaron otros identificadores españoles con este método; las tareas T003–T006 completan la revisión
al editar cada archivo, sin asumir que una búsqueda léxica demuestra ausencia absoluta.

## Superficies y comprobaciones pendientes por grupo

| Superficie | Archivos de referencia | Destino / evidencia posterior |
|---|---|---|
| UI completa | `frontend/src/*.tsx`, `pages/*.tsx`, `index.html`, `styles.css`, módulos TS de mensajes | T007/T010: sesión, ajustes globales, altas, preparación, fases/tareas/runs, permisos, prompts, docs/chat/stats; ARIA/teclado/plurales/formatos y cuatro combinaciones |
| Mensajes API/CLI | `api/{schemas,managed,session,security,app}.py`, `cli.py`, `launcher.py`, servicios y repositorios | T007/T010: claves/parámetros y diagnósticos propios en visual; datos/estados/errores externos originales; ayuda argparse explícita |
| Prompts/salidas | `core/engine/prompts.py`, `templates/*.md`, `adapters/cli_agents.py` | T009: mapa por campo V/W/T del contrato, personalizaciones legibles y hash nuevo por plantilla; no usar flags inexistentes |
| Documentos generados | `engine/{documents,document_ops,document_export,definition,phases,bootstrap,chat,planning,onboarding_commit}.py` | T009: W para documentos/bloques/planes/ADR/commits, V para explicación; parsers bilingües intactos |
| Código/recetas/perfiles | `recipes/*`, `profiles/*`, `services/{local_config,project_preparation}.py` | T004/T008/T009: v1 congelada y v2 por W, sin idioma funcional impuesto a la app hija |
| Retirada A/legacy | Filas R/G y ramas en `api/managed.py`, `services/managed.py`, `frontend/src/pages/Planning.tsx` | T019: resolver dependencia por comportamiento, cero/B, simulaciones H0 propias y backups conservados; contrato §6 |
| Privacidad/derechos/setup | Raíz, locks, `scripts/*`, `examples/*`, docs/grupos históricos | T002/T014/T015: alcance, decisiones humanas y lista permitida del contrato §§7–8; no auditado por detectar idioma |

Validación inicial: cobertura exacta de los 688 paths de base (filas individuales + grupos), análisis estático
sin importar el producto, enlaces locales y referencias a símbolos revisadas; hashes de recetas en el contrato.
No suites, builds, Alembic, instalaciones, servicios, agentes, proveedores ni red. No auditoría completa del
historial/secretos ni dictamen de licencia, inglés final, compatibilidad CLI o primer uso.
