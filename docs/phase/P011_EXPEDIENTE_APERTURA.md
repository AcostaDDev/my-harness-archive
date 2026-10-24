# P011 — Expediente de apertura pública

Fecha: 2026-10-24. Tarea: [P011-T017](../NEXT_STEPS.md#p011-t017--revisión-de-salida-y-expediente-para-apertura-pública).
Dictamen: [revisión de salida](P011_REVIEW.md), favorable (D181). Procedimiento de partida:
[T015 §6](P011-T015_PAQUETE_PUBLICO.md#6-procedimiento-manual-en-github-expediente-para-t017-nada-ejecutado).

**Nada de este documento se ha ejecutado.** Recomendar la apertura no autoriza crear el repositorio, hacer push,
tag o Release, ni cambiar la visibilidad: cada paso remoto exige una instrucción explícita del usuario sobre este
expediente. Por HITL, los comandos usan `<owner>/<repo>`; la visibilidad inicial se decide al autorizar.

## 1. Contenido publicable

| Elemento | Referencia |
|---|---|
| Árbol inicial | 387 archivos por lista positiva ([T015 §5](P011-T015_PAQUETE_PUBLICO.md#5-instantánea-pública-inicial)); manifiesto [`P011-T017_MANIFIESTO_PUBLICO.sha256`](P011-T017_MANIFIESTO_PUBLICO.sha256), SHA-256 `74cc9141…ea71` |
| Documentación de partida | `docs/public/**` → raíz del candidato: AGENTS/CLAUDE/GEMINI, STATE/ROADMAP/NEXT_STEPS (P001 = modo continuo, sin tareas), DECISIONS pública (79 entradas, nuevas desde D200), SPECIFICATION, ARCHITECTURE, DDBB-DIAGRAM y 14 flujos |
| Licencia y avisos | MIT, copyright 2026 David Acosta; `NOTICE.md`, `NOTICE-THIRD-PARTY.md` (58 paquetes del bundle), CONTRIBUTING y SECURITY |
| Excluido | Historia Git, `docs/` privada (fases, ADR, evidencias, manifiesto privado), ayudas reales de CLI, guiones históricos, `.local/`, `dist/` antiguo |
| Release (opcional) | wheel `46d29c20…d9d6`, sdist `79e256de…42c5`, `pylock.toml` `20a327c3…2cf9` y `SHA256SUMS` ([revisión §5](P011_REVIEW.md#5-candidato-final)); notas desde la sección `0.1.0` del CHANGELOG |

## 2. Acciones remotas propuestas

Requisitos del operador: `gh` autenticado con la cuenta propietaria y una identidad Git pública elegida para el
commit raíz (no se deduce de la configuración privada). `<dir>` es una carpeta nueva fuera de este checkout.

1. **Regenerar y comparar.** Desde este checkout, sobre el commit de T017:
   `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P011-T015_public_candidate.py --revision <commit-T017> --out <dir> --private-manifest <scratch>/priv.tsv --public-manifest <scratch>/pub.sha256`.
   `public_manifest_sha256` debe ser `74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71`; si no, parar.
2. **Repositorio vacío**, sin README, licencia ni `.gitignore` generados:
   `gh repo create <owner>/<repo> --private --description "<descripción del pyproject>"` (o `--public` si así se decide).
3. **Commit raíz único y push**, en `<dir>`:
   `git init -b main && git add -A && git -c user.name="<nombre público>" -c user.email="<correo público>" commit -m "Initial public snapshot of Harness Local 0.1.0"`,
   `git remote add origin git@github.com:<owner>/<repo>.git && git push -u origin main`. Ningún objeto, ref ni tag de
   este repositorio.
4. **CI verde.** `gh run list --repo <owner>/<repo> --workflow ci.yml` y `gh run watch --repo <owner>/<repo> <run-id>`.
   Si falla por requisitos del runner (identidad o versión de Git, cachés), corregir en el repositorio público con su
   propia tarea; no cambiar este checkout para ello. Los runners macOS consumen minutos de Actions con multiplicador.
5. **Visibilidad pública** (si se creó privado):
   `gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences`.
6. **Reporte privado de vulnerabilidades** (D160), antes de anunciar o crear Release:
   `gh api -X PUT repos/<owner>/<repo>/private-vulnerability-reporting` y verificar
   `gh api repos/<owner>/<repo>/private-vulnerability-reporting` → `"enabled": true`, o en Settings → Code security.
   GitHub lo ofrece en repositorios públicos: con el repositorio privado se activa justo después del paso 5. Comprobar
   el comportamiento vigente de GitHub al operar.
7. **Release opcional `v0.1.0`.** En el repositorio público, primero un commit que fije la fecha de `0.1.0` en el
   CHANGELOG y añada `[project.urls]` con la URL real (cambia el sdist: reconstruir y comparar con CI). Después
   `gh release create v0.1.0 --repo <owner>/<repo> --target <commit-verde> --title "Harness Local 0.1.0" --notes-file <notas-0.1.0.md> <wheel> <sdist> pylock.toml SHA256SUMS`.
   Sin PyPI ni publicación automática.

## 3. Frontera y continuidad (D157)

- Este checkout conserva su historia, ADR D001–D181 y fases privadas; no se reescribe ni se publica. La
  correspondencia origen → candidato queda en el manifiesto privado de T015, no en el repositorio público.
- Tras el paso 3, el repositorio público es la fuente principal de código, documentación, decisiones (D200+) y fases.
  Este checkout no se sincroniza por copias ni sobrescribe contribuciones públicas; los cambios posteriores, incluido
  el paso 7, se hacen allí.
- Idiomas conforme a D158: visual global y mutable, default global de trabajo e idioma de trabajo inmutable por
  proyecto; el proyecto público usa trabajo en inglés. No se exige publicar ADR ni historia privadas para cumplir.
- v0.2.0 queda reservada al modo continuo (D156), planificado como P001 de la documentación pública, sin tareas.
