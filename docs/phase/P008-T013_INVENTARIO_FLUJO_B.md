# P008-T013 — Flujo B: inventario determinista

Fecha: 2026-10-16. Base: D088 punto 11 y T008 (D095). Decisión:
[D101](../DECISIONS.md#d101--p008-t013-inventario-estático-del-flujo-b-y-propuesta-de-perfil).

## Entrega

- `adapters/project_onboarding.py`: lectura acotada del árbol de un commit Git concreto. No usa `status` ni filtros,
  no importa módulos y no ejecuta herramientas del proyecto. Usa el entorno controlado de `adapters/git.py` y la
  lectura de blobs ya existente del Flujo A, sin cambiar su comportamiento.
- `core/project_onboarding.py`: análisis puro con biblioteca estándar. Formato `harness-local/onboarding-inventory/1`,
  entradas por ruta/modo/tamaño/hash/estado, stack, entidades y campos, relaciones, rutas, tests, CI, scripts de
  paquetes, diagnósticos y límites. Huella `inventory_sha256` independiente de raíz y commit, ligada al árbol y a los
  hechos observados.
- Propuesta en la forma `local-config-4` + `profiles.<nombre>` de T008, con evidencia por argv/cwd, preparación
  vacía y confirmación obligatoria. Los perfiles con validaciones detectadas pasan el parser real de T008 en las
  pruebas. No hay TOML escrito ni composición, ejecutables o entorno inferidos.
- [Flujo documentado](../flows/project-onboarding.md); SPECIFICATION, ARCHITECTURE, STATE y NEXT_STEPS actualizados.
  Sin modelos, migraciones, dependencias, prompts, versiones congeladas, contratos API ni frontend cambiados.

## Reglas y límites

- HEAD no vacío, raíz igual al nivel superior de Git. `rev-parse`, `ls-tree` por id del árbol sellado y `cat-file
  --batch` sin filtros son las únicas operaciones Git; todas exigen `--no-lazy-fetch` para impedir descargas de
  clones parciales (un Git antiguo que no conozca el flag falla sin efectos).
  El disco puede estar sucio: se describe exclusivamente HEAD,
  igual que la instantánea del chat; T015 deberá comprobar la base antes de incorporar.
- 50.000 entradas del árbol, 1 MiB por fuente, 32 MiB en total; sin truncado silencioso. Dependencias instaladas,
  cachés, artefactos, secretos por extensiones fuera del ámbito y `.harness/` no se leen. Enlaces/submódulos dentro
  del ámbito se diagnostican sin leerlos. Binarios, UTF-8 inválido y errores de sintaxis producen diagnósticos.
- Python mediante AST: alias de imports, modelos Django (salvo abstractos), bases declarativas SQLAlchemy y
  columnas/relaciones explícitas; rutas Django y decoradores FastAPI sobre instancias locales reconocidas.
- JS/TS/Prisma mediante un subconjunto léxico, con comentarios, strings y literales regexp comunes apartados:
  entidades TypeORM y decoradores de campos, modelos Prisma y referencias a otros modelos declarados, routers
  Express desde imports/factorías locales. No es un parser completo ni un comprobador de tipos.
- No se resuelven imports, herencia entre módulos, mounts, includes ni código dinámico; no se afirma que el esquema
  runtime esté completo. Las rutas conservan prefijo local cuando se conoce y marcan expresiones dinámicas; las
  relaciones conservan el destino observado o `null`. Las anotaciones TypeScript explícitas se conservan.
- Comandos inferidos solo con evidencia: pytest, ruff y mypy declarados; unittest importado; comprobaciones Django
  con manage.py; scripts test/lint/typecheck/check/build de cada paquete; `go test` por go.mod. Siempre argv/cwd,
  nunca ejecución ni instalación. Sin validaciones: `ready=false`, pendiente de que el usuario las defina.
- Sin persistencia, API ni UI: T014 congelará el inventario para la conversación y T015 confirmará perfil y commit.

## Verificación

Resultados finales en [STATE](../STATE.md). Las 20 pruebas nuevas comprueban fixtures Django y TypeScript con
entidades, relaciones, rutas y comandos exactos; SQLAlchemy/FastAPI; requisitos Python, unittest y Go; comandos en
subdirectorios; compatibilidad con el parser de perfiles T008; hashes/procedencia y orden determinista; raíces
inválidas; límites; fuentes malformadas, binarios y no UTF-8; enlaces/submódulos; exclusión de dependencias y builds
versionados; expresiones dinámicas y falsos positivos en comentarios, cadenas y regexp.

Se comparan modo, mtime y hash del checkout completo, incluido `.git`, antes/después. Una trampa sintética de
filtros/hook/fsmonitor y un espía de procesos verifican que solo se invoca Git de lectura y nunca código del
proyecto; un cambio local y un secreto ignorado no alteran el resultado de HEAD. Los fixtures se construyen en
directorios temporales; ningún framework real se importa o arranca.

- 12 checks ligeros correctos. Pasada dirigida de inventario A/B, normalización y perfiles: 74 OK (aviso conocido
  de Starlette/httpx). Tras los ajustes finales del lector y de las expresiones dinámicas, los 20 casos del inventario
  B vuelven a pasar. Suite completa: 1.303 OK y 121 subtests, sin fallos; aviso conocido de Starlette/httpx.
- Siete Markdown con 284 enlaces/anclas válidos; DECISIONS indexa 101 decisiones sin duplicados; parsers de ROADMAP
  y NEXT_STEPS aceptan ocho fases y 15 tareas. El flowchart nuevo pasa la gramática local de Mermaid 11.17.2,
  sin renderizado DOM; diff revisado y sin errores de espacios.

Sin Node/build ni `alembic check`: no cambian UI, OpenAPI ni esquema. Sin comprobación visual, proveedores reales,
smokes, push ni publicación. No se ejecutó el harness sobre este repositorio ni se leyó ReferenceProject.
