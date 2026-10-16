# P008-T015 — Flujo B: vista previa, commit y continuidad

Fecha: 2026-10-16. Base: D088, D037, D095, D100 y D102.
Decisión: [D103](../DECISIONS.md#d103--p008-t015-incorporación-confirmada-del-flujo-b).

## Entrega y motivo

- `core/engine/onboarding_commit.py` construye la vista previa documental desde el HEAD y los borradores privados:
  exige los once documentos D088 sin fallback, P001 coherente en STATE/NEXT_STEPS/ROADMAP y perfil con
  validaciones explícitas. Regenera bloques e índice de decisiones. Las preguntas bloqueantes abiertas y turnos
  pendientes impiden confirmar; los aplazamientos conservan su motivo.
- `archive/phase-000/INVENTORY.json` guarda el inventario congelado; `SUMMARY.md`, conversación, pendientes,
  preguntas/aplazamientos y perfil. Los originales sustituidos se guardan por bytes bajo
  `onboarding-originals/<ruta original>`; README sin reemplazo permanece intacto, también si no es UTF-8. Los
  destinos se comprueban contra todo HEAD, incluido código fuera de la vista documental: sin sobrescribir archivo,
  colisiones de mayúsculas ni conflictos de archivo/directorio.
- La vista previa muestra propuesta de perfil del inventario y perfil completo de la composición del operador.
  Confirmar requiere ambos hashes (`preview_sha256` y `profile_sha256`), motivo y clave idempotente. El TOML y
  sus ejecutables/entorno siguen siendo autoridad local: se editan fuera del flujo y se selecciona la composición
  en Ajustes. No se escribe el TOML ni se ejecuta preparación o validación durante la incorporación.
- `storage/onboarding_commit.py` especializa `ImportRepository`: misma tabla `project_imports` (0020), propósito
  `import_commit`, intención sellada, lock/lease y conciliación de D100. `preview.flow = onboarding` diferencia
  el Flujo B. Resultado, job terminado y P001 ACTIVE con su base documental se insertan atómicamente. La
  confirmación cierra los borradores de todas las conversaciones del checkout; una intención incierta bloquea
  nuevo trabajo. Repetir una incorporación terminada devuelve cero cambios.
- Se extraen helpers de adopción documental, colisiones y preview del Flujo A, conservando su comportamiento y
  contenido. El mensaje viene de la vista sellada: «docs: incorporar al control del harness» para B; A conserva
  «docs: normalizar al contrato documental». Los historiales, snapshots e intenciones anteriores no se reescriben.
- El supervisor comprueba filtros Git antes de ejecutar B; la vista previa los comprueba antes de capturar,
  incluidos includes. Se rechazan destinos ignorados por Git y conversiones que alteren los bytes sellados,
  evitando escrituras que el commit compartido no podría acreditar después. Se conservan los límites D083,
  documentos de 512 KiB y diff de 4 MiB, sin truncar.
- API `GET …/projects/{p}/onboarding` y `POST …/planning/{c}/onboarding/preview` / `confirm`. UI por URL
  `/projects/:p/onboarding[/:c/*borrador]`: conversación, editor CAS, vista del perfil, diff/originales, estado/run y
  enlace a P001. Reutiliza los componentes del Flujo A; mantiene las claves de ediciones privadas existentes.
- OpenAPI/tipos regenerados; `document_layout = "d088-8"` pone jobs anteriores en cuarentena antes de efectos.
  Sin cambios estructurales de modelo, migraciones o dependencias; el diagrama de datos documenta la reutilización.
  STATE compacta T001/T002 para respetar el límite de 24 KiB, con el detalle original en las entregas y decisiones.
  Extensiones técnicas de las rutas de la tarea: `frontend/openapi.json` para el contrato generado y
  `frontend/tests/router.test.mjs` para verificar URL, editor privado y rechazo de traversal.

## Verificación

- Suite completa: 1.345 pruebas y 121 subtests correctos (22 casos nuevos). Se recogieron los 56 archivos con
  `pytest --collect-only -q` y se repartieron sin solapamiento en cuatro procesos `pytest -q`, cada uno con base y
  caché temporales propias: 337, 337, 335 y 336 OK; 29 y 92 subtests en los dos lotes que los contienen. Todos
  terminaron con exit 0. Solo el aviso conocido de deprecación Starlette/httpx. Lote más largo: 9 min 23 s.
- 12 checks ligeros, 75 pruebas Node, tipos y build correctos. Build con el aviso existente de tamaño de chunks.
  Alembic al HEAD sobre una SQLite temporal: sin nuevas operaciones de upgrade.
- Nueve Markdown con 310 enlaces/anclas válidos; 103 decisiones sin duplicados, ocho fases y quince tareas válidas
  por sus parsers; presupuestos de STATE, base acumulada y NEXT_STEPS correctos. Diez diagramas (siete ER y tres
  flowcharts) válidos por parser/gramática Mermaid local, sin renderizado DOM. Diff revisado y sin errores de espacios.

- Casos nuevos: fixtures Django y TypeScript hasta commit/adopción sin modificar código, originales conservados,
  idempotencia y repetición sin cambios; caídas antes de escribir, después de escritura/commit y antes de registrar
  resultado; hash de perfil y composición obsoleta; checkout sucio/staged/untracked, HEAD y borradores cambiados;
  preguntas, documentos ausentes, límites, fase distinta, archivos ajenos, colisiones y Git ignore/filtros/atributos;
  README intacto y primera tarea de P001 hasta COMMITTED con perfil y validaciones falsos.
- La primera pasada dirigida tuvo 16 fallos de fixture al leer la propuesta como `name/profile` en vez de
  `profiles`; corregido. Los 19 casos existentes del Flujo A pasaron. La primera versión del recorrido posterior
  pedía `test-runner check`, ajeno al perfil Django: se corrigió el plan sintético a `pytest -q`, sin debilitar la
  política, y el caso pasó hasta COMMITTED. La suite completa inicial se detuvo con 308 OK para incluir estos
  ajustes y los rechazos de ignore/conversión. Las siguientes pasadas se detuvieron temprano para corregir
  README original no UTF-8 (sin exigir su sustitución) y repartir la suite completa en cuatro procesos aislados.
  Los dos casos corregidos se re-ejecutaron individualmente: ambos correctos.
- Sin comprobación visual de UI, proveedores reales, smokes, push ni publicación. No se ejecutó el harness sobre
  este repositorio, no se lanzaron subagentes ni se leyó ReferenceProject. Git/SQLite temporales, fixtures sintéticos y
  puertos falsos; no se instalaron frameworks ni ejecutaron comandos del proyecto. Commit solicitado por el usuario.

## Continuidad

Las quince tareas de P008 están implementadas. La fase sigue activa: revisión de salida y cierre quedan para una
operación posterior. El contenido inferido y el perfil de una incorporación real requieren revisión humana;
la calidad semántica de un proveedor real y el aislamiento OS no quedan acreditados por las pruebas offline.
