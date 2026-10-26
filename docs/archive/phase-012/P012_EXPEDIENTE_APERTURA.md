# P012 — Expediente de apertura pública

Fecha: **2026-10-26**. Tarea: [T006](../NEXT_STEPS.md#p012-t006--revisión-de-salida-y-expediente-de-apertura-actualizado).
Dictamen: [revisión de salida](P012_REVIEW.md), favorable en el alcance declarado (D211).
Sustituye para una apertura futura al [expediente P011](../archive/phase-011/P011_EXPEDIENTE_APERTURA.md),
que permanece congelado. El candidato P011 está conservado y ya no es el publicable.

**Expediente preparado, sin apertura ejecutada.** T005 sustituyó localmente el candidato con autorización;
T006 solo lo revisa. **T007/cierre de P012 sigue pendiente**. Crear repositorio, push, visibilidad, reporte de
vulnerabilidades y Release requieren instrucciones explícitas del usuario sobre los pasos correspondientes,
como exige D181. El dictamen y esta tarea no conceden esos permisos.

## 1. Candidato revisado

| Elemento | Identidad y procedencia |
|---|---|
| Fuente privada reproducible | Commit T005 `99b1b9954d543259a84956940ea8543035551077`; [script por lista positiva](P012-T005_public_candidate.py) y [correspondencia privada](P012-T005_MANIFIESTO_PRIVADO.tsv) |
| Árbol inicial | `$HOME/Documents/projects/my_harness_dist`, sin Git ni symlinks, **401 archivos/5.480.755 bytes**. Sustitución autorizada y [verificada en T005](P012-T005_SUSTITUCION.json); lista/hashes/modos contrastados otra vez en T006 |
| Manifiesto público de referencia | [P012-T005_MANIFIESTO_PUBLICO.sha256](P012-T005_MANIFIESTO_PUBLICO.sha256), SHA-256 **`cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a`** |
| Diferencia frente a P011 | [Diff](P012-T005_DIFF_PUBLICO.json): 14 añadidos, 38 modificados, cero eliminados, 349 iguales. P011 conservada en `my_harness_dist_p011_74cc9141`, 387 archivos, manifiesto `74cc9141…ea71` |
| Documentación pública | 25 archivos `docs/public/**` sustituyen instrucciones/documentación privadas al exportar: contexto inglés autocontenido, README inglés y entrada española, especificación/arquitectura/datos y 15 flujos; 80 decisiones públicas de partida, nuevas desde D200; P001 de modo continuo sin tareas |
| Licencia y avisos | MIT, copyright 2026 David Acosta; LICENSE, NOTICE, NOTICE-THIRD-PARTY, CONTRIBUTING y SECURITY del árbol revisado |
| Exclusiones | `.git`, objetos/refs/tags e historia de este checkout, docs/ADR/fases/evidencias privadas, manifiesto privado, ayudas reales de CLI, SQLite/credenciales/streams/cachés y distribuciones operativas |
| Paquete local de referencia | `.local/p012-t005/package/`; [checksums originales](P012-T005_PAQUETE.sha256). No copiar esta carpeta dentro del árbol inicial |

| Artefacto de T005 | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `eef56a29c268839487f23e53493fd728361e31589ce0535a1f3f01e50b4504ab` |
| `harness_local-0.1.0.tar.gz` | `0f290f05d1a93f5117d0eac01f1b6b175bad61ad1e88613580441cce3072a384` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |

SHA256SUMS es idéntico por bytes al archivo de checksums enlazado. Los hashes se verifican en T006, sin build
nuevo; su SHA-256 es `e169012c5a31938b068a2af008dcbb43e2eaf48d047b3e4b089c6902c5ff9e7b`.
No se prometen hashes binarios iguales en otra plataforma. El paquete fue verificado instalado con
agentes falsos en T005. La evidencia real de P012 corresponde a las instalaciones de cada tramo de la revisión,
no a una nueva ejecución del paquete final.

## 2. Parámetros pendientes y comprobación local previa

Al autorizar se concretan **`<owner>/<repo>`**, visibilidad inicial y nombre/correo públicos del commit raíz.
No se deducen de la cuenta autenticada o configuración Git privada. Se necesita `gh` autenticado como propietario
y permisos adecuados. No se cambia configuración global. `<scratch>` es una carpeta absoluta nueva fuera de los
dos candidatos y de este checkout; `<dir>` es el candidato nuevo que se comparará antes de inicializar Git.
Todos los comandos siguientes son **propuestos, no ejecutados en T006**; los placeholders deben sustituirse.

Antes de operar, comprobar cierre T007 y comparar el destino actual con el manifiesto, lista exacta y modos
de T005, sin tolerar extras (incluidos ocultos) ni Git/symlinks. La reproducción desde la base exacta evita que el
archivo documental de T007 cambie las rutas del script original. Desde este checkout:

```sh
git worktree add --detach <scratch>/source 99b1b9954d543259a84956940ea8543035551077
python3 <scratch>/source/docs/phase/P012-T005_public_candidate.py \
  --revision 99b1b9954d543259a84956940ea8543035551077 --out <dir> \
  --private-manifest <scratch>/private.tsv --public-manifest <scratch>/public.sha256
cmp <scratch>/public.sha256 <scratch>/source/docs/phase/P012-T005_MANIFIESTO_PUBLICO.sha256
```

El script debe informar 401 archivos/5.480.755 bytes, cero problemas y el hash de manifiesto completo de §1.
Contrastar también lista/bytes/modos con `my_harness_dist` y SHA256SUMS/artefactos si se van a usar. Parar ante
deriva; regenerar un árbol diferente no mantiene este dictamen. El manifiesto privado y el worktree de origen
no se publican. La base T005 permanece identificable tras T007; no hace falta editar archivos archivados.

## 3. Pasos remotos propuestos

Procedimiento heredado de D157/D181, ajustado al candidato P012. Autorización pendiente por paso; no ejecutarlo
como un bloque ni usar un saldo de autorización de operaciones reales anteriores.

1. **Repositorio vacío.** Crear sin README/licencia/gitignore automáticos, desde fuera de este checkout:
   `gh repo create <owner>/<repo> --private --description "<descripción del pyproject>"`.
   Usar `--public` en lugar de `--private` solo si esa es la visibilidad inicial elegida al autorizar.
   No usar `--source` con este checkout ni `--push` implícito.
   [Referencia oficial: creación](https://cli.github.com/manual/gh_repo_create).
2. **Raíz Git independiente y push.** En `<dir>`, tras la comparación de §2:
   `git init -b main`, `git add -A` y
   `git -c user.name="<nombre público>" -c user.email="<correo público>" commit -m "Initial public snapshot of Harness Local 0.1.0"`.
   Contrastar el árbol del commit con las 401 rutas/hashes/modos aprobados, un único commit raíz y ninguna ref/tag
   del origen. Después, `git remote add origin git@github.com:<owner>/<repo>.git` y `git push -u origin main`.
   Nada de `.git`, refs o tags privados se copia. La autorización de push incluye que arranque la CI sintética
   definida en el candidato, todavía sin ejecutar.
3. **CI del commit exacto.** `gh run list --repo <owner>/<repo> --workflow ci.yml`; elegir la ejecución cuyo
   head SHA sea el commit subido y verificarla con `gh run watch <run-id> --repo <owner>/<repo> --exit-status`.
   El workflow actual usa macos-15, instalación de herramientas/cachés en el runner y checks offline posteriores;
   no llama proveedores ni publica. Si falla, registrar/corregir en una tarea del repositorio público y exigir CI
   verde de ese nuevo commit antes de continuar. No trasladar esos cambios a este checkout por copias.
   [Referencia oficial: seguimiento y estado de salida](https://cli.github.com/manual/gh_run_watch).
4. **Visibilidad pública**, si se creó privado y tras CI verde:
   `gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences`.
   Omitir si ya nació público. [Referencia oficial: visibilidad](https://cli.github.com/manual/gh_repo_edit).
5. **Reporte privado de vulnerabilidades**, antes de anunciar o crear Release (D160):
   `gh api -X PUT repos/<owner>/<repo>/private-vulnerability-reporting`; después
   `gh api repos/<owner>/<repo>/private-vulnerability-reporting` debe devolver `"enabled": true`.
   Habilitarlo requiere administración y repositorio público, por lo que sigue al cambio de visibilidad si se
   creó privado. [Configuración oficial](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository)
   y [API PUT/GET](https://docs.github.com/en/rest/repos/repos#enable-private-vulnerability-reporting-for-a-repository).
6. **Release opcional `v0.1.0`, con autorización propia.** En el repositorio público, fijar fecha de `0.1.0` en
   CHANGELOG y `[project.urls]` con URL real en un commit nuevo; preparar notas exactas en un archivo y reconstruir
   paquete/checksums desde ese commit, verificar instalación y CI. Esos cambios afectan al sdist: los hashes de §1
   son la referencia candidata anterior, no los hashes prometidos de la Release. Comparar resultados, registrar
   hashes finales y adjuntar únicamente el paquete revisado de ese commit verde:
   `gh release create v0.1.0 --repo <owner>/<repo> --target <commit-verde-completo> --title "Harness Local 0.1.0" --notes-file <notas-0.1.0.md> <wheel-final> <sdist-final> <pylock-final> <SHA256SUMS-final>`.
   El comando crea el tag si no existe y publica la Release; no ejecutarlo antes de aprobar ese resultado concreto.
   Sin PyPI ni publicación automática. [Referencia oficial: Release](https://cli.github.com/manual/gh_release_create).

Fuentes oficiales consultadas el **2026-10-26** solo mediante lectura web; no se ha comprobado autenticación,
disponibilidad del nombre, políticas de organización, facturación o ejecución CI de una cuenta concreta.
Volver a comprobar las condiciones al operar si cambian. No son criterios técnicos locales pendientes de T006.

## 4. Frontera, límites y continuidad

- Este checkout conserva historia, ADR D001–D211 y fases/evidencia privadas. T007 añadirá su propio cierre sin
  alterar el árbol público de T005. El expediente, revisión y manifiestos privados quedan aquí/archivados.
- Tras el primer push, repositorio público como fuente principal de código/docs/decisiones/fases (D157);
  cambios posteriores y eventuales correcciones de CI/Release allí, sin dos desarrollos sincronizados por copias.
  Decisiones públicas nuevas desde D200, independientes de la numeración privada.
- Trabajo público en inglés; visual global mutable y trabajo inmutable por proyecto, según D158. v0.2.0 sigue
  reservada al modo continuo, P001 pública sin tareas ni sucesora privada definida por esta revisión.
- Alcance real: fixtures sintéticos, macOS ARM64 y Chrome; pareja Claude 2.1.310 → Codex 0.164.0 cli-14. Las cuatro
  parejas y receta Django históricas preceden a cli-14. Sin creación Django v2 real, producción, otras plataformas
  o matriz completa de idiomas. Los dos REVISION_LIMIT, checks rechazados, propuesta QUEUED e incertidumbre
  histórica de identidad se conservan. La consulta no autoriza reanudar trabajo ni certifica muerte de escritores.
- Suites/paquete/docs de T005 en verde; CI remota y nueva QA visual/accesibilidad no ejecutadas. T006 no consume
  proveedores, registra el repositorio con el harness, crea Git público, commit, tag, push o publicación.

**Próximo paso: T007, cierre documental de P012.** La aprobación para publicación sigue pendiente después del cierre.
