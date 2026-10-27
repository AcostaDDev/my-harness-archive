# P013 — Expediente de apertura pública

Fecha: **2026-10-27**. Tarea: [T014](../NEXT_STEPS.md#p013-t014--revisión-de-salida-y-expediente-de-apertura-actualizado).
[Revisión favorable](P013_REVIEW.md) en el alcance declarado; D231. **Preparado, sin apertura ejecutada.**
Sustituye operativamente el [expediente P012](../archive/phase-012/P012_EXPEDIENTE_APERTURA.md) y el
[suplemento D214](2026-10-26_ACTUALIZACION_CANDIDATO.md), conservados íntegros como antecedentes.

**T015/cierre de P013 sigue pendiente.** La continuación/commit autorizados de esta sesión no conceden creación
de repositorio, Git público, push/CI remota, visibilidad, reporte privado, tag o Release. Esos pasos se concretan
después del cierre conforme a D157/D181/D215; los parámetros pendientes de §2 no bloquean esta revisión local.

## 1. Candidato y paquete revisados

| Elemento | Identidad y procedencia |
|---|---|
| Fuente pública reproducible | `984c287ab9f21ba7976fc7cdb5df86b4f235b118` (T012), lista positiva congelada P012 con [adaptador P013](P013-T013_EXPORT.py). [Correspondencia privada](P013-T013_MANIFIESTO_PRIVADO.tsv), 853 fuentes/408 exclusiones. |
| Entrega y revisión privadas | T013 `a0cab9e51f6440b827825d5491313f0542e4197e`, [entrega](P013-T013_CANDIDATO.md), [contraste T014](P013-T014_COMPROBACION.json). Los cambios documentales privados posteriores no alteran el árbol exportado. |
| Árbol aprobado | `$HOME/Documents/projects/my_harness_dist_p013`, **445 archivos / 6.389.580 bytes**, sin Git, enlaces simbólicos ni extras; lista/directorios/bytes/modos verificados. No sustituye físicamente my_harness_dist. |
| Manifiesto público | [P013-T013_MANIFIESTO_PUBLICO.sha256](P013-T013_MANIFIESTO_PUBLICO.sha256), SHA-256 **`ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428`**. |
| Diferencia y originales | [Diff D214](P013-T013_DIFF_PUBLICO.json): 325 idénticos, 44 añadidos, 76 modificados; sin eliminados ni cambios de modos. D214 y originales P011/P012 en sus destinos anteriores, paquetes/snapshots intactos según [conservación](P013-T013_CONSERVACION.json). |
| Baseline pública | 26 archivos docs/public mapeados a raíz; 93 decisiones públicas, nuevas desde **D230**; P001 de modo continuo sin tareas. Inglés autocontenido, README en/es, especificación/arquitectura/datos/16 flujos y configuración guiada entregada. La numeración privada D231 no se copia. |
| Licencia y avisos | MIT, copyright 2026 David Acosta; LICENSE/NOTICE/NOTICE-THIRD-PARTY/CONTRIBUTING/SECURITY revisados en el árbol. No se deduce de ello la identidad Git pública por utilizar. |
| Exclusiones | Historia/.git/refs/tags privados; docs/ADR/fases/evidencias y manifiesto privado; ayudas CLI reales, SQLite, credenciales, streams, entornos, cachés y paquetes operativos. |
| Paquete candidato | `$HOME/Documents/projects/my_harness_p013_t013_verification/package/`, `distribution-1`: **13 archivos**, wheel/sdist/pylock/manifiesto/SHA256SUMS y ocho scripts/fixture bajo scripts/. No copiarlo dentro del árbol Git inicial. |

| Artefacto T013 | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `2416672d69b54524544d8560b41a54f49cb9747164faa1c82ac777672ad47076` |
| `harness_local-0.1.0.tar.gz` | `31c9ab33a50a196ff7c2b0852d90bdf98eeabfb3f5ead427713c4b5049b5b22c` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |
| `distribution-1.json` | `35931df4ac58bb51104edd4ed0c1b30e1730d5055d964310a0c51a02aadc6827` |
| `SHA256SUMS` | `0d7cab5e3901985962c39b95cb621d8e2024141f6b3b7d9f6e312be14bae2edb` |

[Checksums completos](P013-T013_PAQUETE.sha256) idénticos al SHA256SUMS del paquete, con rutas scripts/ conservadas.
T013 verificó instalado con agentes falsos, sin Node/fuentes de desarrollo; T014 verifica hashes/miembros sin
reinstalar. El lock conserva su hash porque no cambian dependencias. Las suites del candidato son las de T013:
2048 pytest/29 subtests, 8 unittest, 155 Node; dos opt-in omitidas, tipos/build/Alembic/distribución correctos.
QA Chrome y ambas altas guiadas Go son evidencia separada de T012. No hay nueva inferencia real de este paquete.

## 2. Parámetros pendientes y comprobación local previa

Antes de operar se necesitan cierre T015 y autorización concreta sobre:

- **Owner/repo completo**, visibilidad inicial privada/pública y descripción. No se deducen de cuentas o remotos.
- **Nombre/correo públicos** del nuevo commit raíz, y URL/transporte del remoto; no reutilizar identidad privada
  por defecto ni cambiar configuración global.
- **Pasos autorizados**: repositorio vacío, raíz Git independiente/commit/push que dispara CI, consulta de esa CI,
  eventual cambio de visibilidad y habilitación/verificación del reporte privado de vulnerabilidades.
- **Release opcional**: fecha/notas, commit/tag exactos, URLs públicas de metadatos y assets finales completos de
  distribution-1. Preparar/verificar una entrega que conserve scripts/ y revisar sus bytes antes de pedir la
  autorización final de publicación; no fijar ahora un formato de transporte nuevo ni publicar solo wheel/sdist.

No se ha comprobado cuenta autenticada, permisos/SSO, disponibilidad del nombre, políticas/coste de organización
ni condiciones efectivas del runner. Esas comprobaciones pertenecen a la operación posterior autorizada.
`<scratch>` será una carpeta absoluta nueva fuera del checkout/candidatos; `<árbol-nuevo>` no debe existir.
Los comandos siguientes son **propuestos, no ejecutados**. Sustituir placeholders y detenerse ante cualquier deriva.

Para reproducir el árbol después del archivo de T015 se usa la entrega T013, cuyo adaptador está en docs/phase,
y se exporta la fuente T012 exacta (dos commits distintos con propósitos diferentes):

```sh
git worktree add --detach <scratch>/source a0cab9e51f6440b827825d5491313f0542e4197e
python3 -B <scratch>/source/docs/phase/P013-T013_EXPORT.py \
  --revision 984c287ab9f21ba7976fc7cdb5df86b4f235b118 --out <árbol-nuevo> \
  --private-manifest <scratch>/private.tsv --public-manifest <scratch>/public.sha256
cmp <scratch>/public.sha256 <scratch>/source/docs/phase/P013-T013_MANIFIESTO_PUBLICO.sha256
```

Debe informar 445 archivos/6.389.580 bytes, cero problemas y el hash completo de §1. Comparar también nombres
exactos de archivos/directorios, bytes y modos del árbol que se va a publicar; hashes solos no acreditan modos
ni ausencia de extras. Para usar el destino ya cualificado, compararlo con esa reproducción antes de crear Git.
No renombrar/sustituir D214/P011/P012 por efecto de este expediente. Contrastar los 13 archivos del paquete,
SHA256SUMS y miembros si se va a entregar. Un árbol o paquete distinto necesita evidencia y revisión nuevas;
los manifiestos privados/worktree fuente no se publican. Este procedimiento no ejecuta servicios ni smokes.

## 3. Acciones remotas propuestas, no autorizadas por T014

1. **Crear repositorio vacío** desde fuera de este checkout, sin README/licencia/gitignore automáticos:
   `gh repo create <owner>/<repo> --private --description "<descripción aprobada>"`.
   Usar `--public` solo si se autoriza esa visibilidad inicial. No usar --source con el origen privado ni --push
   implícito. [Manual oficial](https://cli.github.com/manual/gh_repo_create).
2. **Raíz Git independiente y push.** En el árbol exacto comparado: `git init -b main`, `git add -A` y
   `git -c user.name="<nombre público>" -c user.email="<correo público>" commit -m "Initial public snapshot of Harness Local 0.1.0"`.
   Antes de push, contrastar blobs/modos de las 445 rutas con el árbol aprobado, un solo commit raíz y ninguna
   ref/tag del origen; los filtros/atributos Git tampoco deben transformar bytes. Después, remoto explícito
   `git remote add origin <URL-aprobada>` y `git push -u origin main`. Autorizar ese push incluye el disparo de
   la CI sintética del candidato, todavía no ejecutada. No copiar .git ni la historia privada.
3. **CI del commit exacto.** `gh run list --repo <owner>/<repo> --workflow ci.yml`; seleccionar el head SHA
   recién publicado y `gh run watch <run-id> --repo <owner>/<repo> --exit-status`. Workflow macos-15 con herramientas
   fijadas, cachés preparadas en runner y checks posteriores offline; sin proveedores/publicación. Registrar
   resultado real antes de continuar. Si falla, corrección en tarea del repositorio público y CI verde del
   nuevo commit; no mantener dos desarrollos sincronizados por copias. [Manual oficial](https://cli.github.com/manual/gh_run_watch).
4. **Visibilidad pública**, si nació privado y tras CI verde:
   `gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences`.
   Omitir si ya nació público. [Manual oficial](https://cli.github.com/manual/gh_repo_edit).
5. **Reporte privado de vulnerabilidades** antes de anunciar/Release: con administración y repositorio público,
   `gh api -X PUT repos/<owner>/<repo>/private-vulnerability-reporting`, después
   `gh api repos/<owner>/<repo>/private-vulnerability-reporting` debe devolver `"enabled": true`.
   [API oficial](https://docs.github.com/en/rest/repos/repos#enable-private-vulnerability-reporting-for-a-repository)
   y [condiciones de habilitación](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
6. **Release opcional v0.1.0 con autorización propia.** Preparar fecha en CHANGELOG y URLs públicas en metadatos
   mediante commit público nuevo; construir paquete desde ese commit, verificar instalación/CI y entrega completa
   de los 13 archivos con estructura scripts/. El mecanismo de descarga/entrega, notas y lista exacta de assets
   deben quedar concretos y revisables antes de la aprobación final. Wheel/sdist/pylock/SHA256SUMS siguen siendo
   assets según CHANGELOG; el instalador requiere además manifiesto/scripts/fixture coherentes. Cambiar metadatos
   invalida prometer los hashes candidatos de §1 como hashes finales de Release. Registrar los nuevos, y solo tras
   aprobarlos: `gh release create v0.1.0 --repo <owner>/<repo> --target <commit-verde-completo> --title "Harness Local 0.1.0" --notes-file <notas.md> <assets-finales-revisados>`.
   Puede crear el tag y publicar: no ejecutar como preparación ni inferir permiso de tag. Sin PyPI/publicación
   automática. [Manual oficial](https://cli.github.com/manual/gh_release_create).

Referencias oficiales leídas el **2026-10-27**, sin operar cuentas/repositorios remotos. Revalidar condiciones al
operar. Este expediente distingue lectura web de API autenticada: ningún comando gh/Git remoto se ejecutó.

## 4. Frontera y continuidad

El candidato P013 es el propuesto para la futura apertura; los anteriores quedan como evidencia, no como fuente
operativa del nuevo push. No se copia este expediente, la revisión ni las fases privadas al árbol público.
Tras el primer push, código/docs/decisiones/fases se desarrollan en el repositorio público (D157), en inglés;
este checkout conserva historia privada. Decisiones nuevas públicas desde D230, independientes de D231 privada.
Modo continuo reservado a v0.2.0; P001 pública sin tareas, sin sucesora privada asumida.

Alcance sintético P013 y evidencia real histórica P012 permanecen separados: macOS ARM64/Chrome, sin nueva
inferencia real, producción, otras parejas/plataformas ni auditoría completa de accesibilidad. La consulta de
backup no certifica muerte de escritores ni autoriza reactivar una base. Resultados parciales/fallidos originales
y consumos se conservan, sin saldos transferibles. CI remota pendiente.

**Siguiente paso: T015, cierre documental de P013.** La autorización concreta de apertura queda pendiente después.
