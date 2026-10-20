"""Adaptadores Git H2.4: captura completa, worktrees por tarea y commit idempotente.

Todo comando usa un entorno explícito y mínimo: sin configuración global/de
sistema, sin hooks, sin fsmonitor ni mantenimiento automático. La captura trabaja
con copias temporales del índice y no modifica HEAD, índice real ni archivos.
Solo se escriben objetos Git (blobs/árboles). No hay filtros definidos fuera del
repositorio ni sandbox: un worktree separa trabajo, no aísla seguridad.
"""

from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from harness_local.core.engine.commit import (
    CommitError, CommitIntent, CommitOutcome, CommitPlan, CommitUncertain, GIT_FORMAT, GitIdentity, _OBJECT_ID,
)
from harness_local.core.engine.context import ProjectContext
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.evidence import ContentEvidence

MAX_DIFF_BYTES = 4 * 1024 * 1024
_CONFIG = ("-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-c", "core.ignorecase=false", "-c", "core.quotePath=false",
           "-c", "core.excludesFile=/dev/null", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
           "-c", "advice.detachedHead=false")


class GitError(RuntimeError):
    def __init__(self, message: str, *, argv: tuple[str, ...] = (), returncode: int | None = None,
                 stderr: str = ""):
        super().__init__(message)
        self.argv, self.returncode, self.stderr = argv, returncode, stderr


class EvidenceCaptureError(RuntimeError):
    """El contenido no puede capturarse completo; el motor se detiene sin juzgar."""


class Git:
    """Invoca el ejecutable Git con entorno controlado; nunca usa shell."""

    def __init__(self, cwd: Path, *, executable: str = "git", timeout: float = 120.0):
        self.cwd = Path(cwd)
        self.executable = executable
        self.timeout = timeout

    def _environment(self, extra: dict[str, str] | None) -> dict[str, str]:
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
               "GIT_OPTIONAL_LOCKS": "0"}
        if os.environ.get("DEVELOPER_DIR"):
            env["DEVELOPER_DIR"] = os.environ["DEVELOPER_DIR"]
        env.update(extra or {})
        return env

    def _completed(self, args: tuple[str, ...], input: bytes | None,
                   env: dict[str, str] | None) -> tuple[tuple[str, ...], subprocess.CompletedProcess]:
        """Ejecuta Git y captura su salida; un fallo al lanzarlo o el timeout son GitError.

        D125: con ruta absoluta, `-C` en lugar de cwd y sin cerrar descriptores, subprocess usa
        posix_spawn en vez de fork (varias veces más barato desde un proceso grande). Los
        descriptores de Python no son heredables (PEP 446) y SQLite abre con O_CLOEXEC, así que el
        hijo recibe lo mismo que con close_fds. Un directorio inaccesible falla antes de lanzar Git,
        igual que el chdir de subprocess: nunca se convierte en un código de salida de Git.
        """
        argv = (self.executable, *_CONFIG, *args)
        environment = self._environment(env)
        executable = self.executable
        if not os.path.isabs(executable) and os.sep not in executable:
            executable = shutil.which(executable, path=environment["PATH"]) or executable
        try:
            if os.path.isabs(executable):
                if not (os.path.isdir(self.cwd) and os.access(self.cwd, os.X_OK)):
                    raise NotADirectoryError(f"cannot change to {self.cwd}")
                completed = subprocess.run((executable, "-C", str(self.cwd), *argv[1:]), input=input,
                                           capture_output=True, env=environment, close_fds=False,
                                           timeout=self.timeout, check=False)
            else:
                completed = subprocess.run(argv, cwd=self.cwd, input=input, capture_output=True,
                                           env=environment, timeout=self.timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitError(f"git {args[0] if args else ''} could not run: {exc}", argv=argv) from exc
        return argv, completed

    def run(self, *args: str, input: bytes | None = None, env: dict[str, str] | None = None,
            ok: tuple[int, ...] = (0,)) -> bytes:
        argv, completed = self._completed(args, input, env)
        if completed.returncode not in ok:
            stderr = completed.stderr.decode("utf-8", "replace").strip()
            raise GitError(f"git {args[0] if args else ''} failed with exit {completed.returncode}: {stderr[:500]}",
                           argv=argv, returncode=completed.returncode, stderr=stderr)
        return completed.stdout

    def code(self, *args: str, env: dict[str, str] | None = None) -> int:
        """Código de salida sin interpretar; permite preguntas booleanas (is-ancestor)."""
        return self._completed(args, None, env)[1].returncode

    def text(self, *args: str, input: bytes | None = None, env: dict[str, str] | None = None) -> str:
        try:
            return self.run(*args, input=input, env=env).decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise GitError(f"git {args[0] if args else ''} produced non-UTF-8 output") from exc


def _split0(data: bytes) -> list[str]:
    try:
        return [item.decode("utf-8") for item in data.split(b"\0") if item]
    except UnicodeDecodeError as exc:
        raise EvidenceCaptureError("Non-UTF-8 paths cannot be recorded as evidence") from exc


def _raw_entries(data: bytes) -> list[tuple[str, str, str, str]]:
    """`diff-tree --raw -z` sin renombrados: (estado, modo anterior, modo nuevo, ruta)."""
    tokens = data.split(b"\0")
    entries, index = [], 0
    while index < len(tokens) and tokens[index]:
        meta = tokens[index].decode("ascii").lstrip(":").split(" ")
        try:
            path = tokens[index + 1].decode("utf-8")
        except (IndexError, UnicodeDecodeError) as exc:
            raise EvidenceCaptureError("Non-UTF-8 or malformed path in Git diff") from exc
        entries.append((meta[4][0], meta[0], meta[1], path))
        index += 2
    return entries


def _exact_path(root: Path, path: str) -> bool:
    """La grafía de una ruta Git es exacta, también en sistemas de archivos sin distinción de mayúsculas."""
    parent = root
    for part in path.split('/'):
        if not parent.is_dir() or part not in {item.name for item in parent.iterdir()}:
            return False
        parent = parent / part
    return True


class GitWorkspace:
    """Captura Git completa y escritor de commit; puede reemplazar a SyntheticWorkspace."""

    def __init__(self, identity: GitIdentity, *, max_diff_bytes: int = MAX_DIFF_BYTES,
                 executable: str = "git", timeout: float = 120.0):
        if not isinstance(identity, GitIdentity) or max_diff_bytes <= 0:
            raise ValueError("Explicit GitIdentity and positive diff limit required")
        self.identity = identity
        self.max_diff_bytes = max_diff_bytes
        self.executable = executable
        self.timeout = timeout
        self.marker_reader = None
        self.local_objects_only = False

    def _git(self, root: Path) -> Git:
        git_class = Git
        if self.local_objects_only:
            from harness_local.adapters.local_git import LocalGit
            git_class = LocalGit
        return git_class(root, executable=self.executable, timeout=self.timeout)

    def _require_root(self, git: Git, root: Path) -> None:
        try:
            top = Path(git.text("rev-parse", "--show-toplevel")).resolve()
        except GitError as exc:
            raise EvidenceCaptureError(f"Not a Git checkout: {exc}") from exc
        if top != root:
            raise EvidenceCaptureError("Project root must be the top level of its Git checkout")

    def _index_path(self, git: Git) -> Path:
        return Path(git.text("rev-parse", "--path-format=absolute", "--git-path", "index"))

    def _scratch_index(self, git: Git, target: Path, real: Path | None = None) -> dict[str, str]:
        """Copia del índice real; no se escribe nunca en el índice del usuario."""
        real = real or self._index_path(git)
        env = {"GIT_INDEX_FILE": str(target)}
        if real.is_file():
            shutil.copy2(real, target)
        else:
            git.run("read-tree", "--empty", env=env)
        return env

    def _index_tree(self, git: Git) -> str:
        with tempfile.TemporaryDirectory(prefix="harness-git-") as scratch:
            env = self._scratch_index(git, Path(scratch) / "index")
            return git.text("write-tree", env=env)

    def capture(self, context: ProjectContext) -> ContentEvidence:
        root = context.root
        git = self._git(root)
        self._require_root(git, root)
        try:
            head = git.text("rev-parse", "--verify", "HEAD^{commit}")
            base_tree = git.text("rev-parse", "--verify", f"{head}^{{tree}}")
            ref = git.run("symbolic-ref", "-q", "HEAD", ok=(0, 1)).decode("utf-8").strip() or None
            with tempfile.TemporaryDirectory(prefix="harness-git-") as scratch:
                real_index = self._index_path(git)
                staged_env = self._scratch_index(git, Path(scratch) / "staged", real_index)
                work_env = self._scratch_index(git, Path(scratch) / "work", real_index)
                # Un índice con conflictos falla aquí: nunca se resuelve implícitamente.
                index_tree = git.text("write-tree", env=staged_env)
                untracked = sorted(_split0(git.run("ls-files", "--others", "--exclude-standard", "-z",
                                                   env=staged_env)))
                paths = ["."]
                # D099: exclusion only while SQLite and the filesystem agree on a live activation.
                if self.marker_reader is not None:
                    from harness_local.core.migration import MARKER_PATH
                    if self.marker_reader(root) is not None:
                        if git.run("ls-files", "--", MARKER_PATH).strip():
                            raise EvidenceCaptureError('The managed marker must remain untracked (D099)')
                        if MARKER_PATH in untracked:
                            paths.append(":(exclude,literal)" + MARKER_PATH)
                            untracked.remove(MARKER_PATH)
                if untracked:
                    tracked = _split0(git.run('ls-files', '-z', env=work_env))
                    spellings = {path.lower() for path in untracked}
                    for path in tracked:
                        if path.lower() in spellings and path not in untracked and not _exact_path(root, path):
                            git.run('update-index', '--force-remove', '--', path, env=work_env)
                git.run("add", "-A", "--", *paths, env=work_env)
                worktree_tree = git.text("write-tree", env=work_env)
            diff_args = ("diff-tree", "-r", "--no-renames", "--no-ext-diff", "--no-textconv", "--no-color")
            raw = _raw_entries(git.run(*diff_args, "-z", "--raw", "--full-index", base_tree, worktree_tree))
            staged = _raw_entries(git.run(*diff_args, "-z", "--raw", "--full-index", base_tree, index_tree))
            patch = git.run(*diff_args, "-p", "--binary", "--full-index", base_tree, worktree_tree)
        except GitError as exc:
            raise EvidenceCaptureError(f"Git evidence could not be captured: {exc}") from exc
        if any("160000" in (old, new) for _, old, new, _ in raw + staged):
            raise EvidenceCaptureError("Submodule/gitlink changes are not supported as reviewable evidence")
        if len(patch) > self.max_diff_bytes:
            raise EvidenceCaptureError(f"Diff exceeds the {self.max_diff_bytes}-byte review limit; "
                                       "it is not truncated silently")
        changed = tuple(sorted({path for _, _, _, path in raw}))
        provenance = freeze({
            "format": GIT_FORMAT, "head_ref": ref, "base_tree": base_tree, "worktree_tree": worktree_tree,
            "index_tree": index_tree, "staged_paths": sorted({path for _, _, _, path in staged}),
            "untracked_paths": untracked, "deleted_paths": sorted(path for status, _, _, path in raw if status == "D"),
            "diff_sha256": hashlib.sha256(patch).hexdigest(), "diff_bytes": len(patch),
            "git_version": git.text("--version"),
        })
        fingerprint = hashlib.sha256(freeze({
            "format": GIT_FORMAT, "base_revision": head, "worktree_tree": worktree_tree,
            "index_tree": index_tree}).encode("utf-8")).hexdigest()
        return ContentEvidence(head, fingerprint, changed, patch.decode("utf-8", "replace"), provenance)

    # --- commit -----------------------------------------------------------------

    @staticmethod
    def _commit_text(tree: str, base: str, message: str, name: str, email: str, timestamp: int) -> bytes:
        who = f"{name} <{email}> {timestamp} +0000"
        return (f"tree {tree}\nparent {base}\nauthor {who}\ncommitter {who}\n\n{message}").encode("utf-8")

    def _tree_with(self, git: Git, tree: str, plan_updates) -> str:
        updates = sorted(plan_updates, key=lambda item: item.path)
        # Un único listado del árbol (rutas exactas, sin pathspec) para todos los modos.
        modes = {}
        for record in git.run("ls-tree", "-r", "-t", "-z", "--full-tree", tree).split(b"\0"):
            if record:
                header, _, path = record.partition(b"\t")
                modes[path.decode("utf-8", "surrogateescape")] = header.split(b" ", 1)[0].decode()
        for update in updates:
            if update.content is not None and modes.get(update.path, "100644") not in {"100644", "100755"}:
                raise CommitError("Mechanical update target is not a regular file")
        with tempfile.TemporaryDirectory(prefix="harness-git-") as scratch:
            env = {"GIT_INDEX_FILE": str(Path(scratch) / "index")}
            git.run("read-tree", tree, env=env)
            # hash-object sigue siendo por ruta: `--path` aplica los atributos de cada destino.
            # Las altas consecutivas comparten un update-index (cada --cacheinfo se aplica en orden
            # y falla igual que por separado); las bajas conservan su posición en el orden.
            additions = []
            for update in updates:
                if update.content is None:
                    if additions:
                        git.run("update-index", "--add", *additions, env=env)
                        additions = []
                    git.run('update-index', '--force-remove', '--', update.path, env=env)
                    continue
                blob = git.text("hash-object", "-w", f"--path={update.path}", "--stdin",
                                input=update.bytes())
                additions += ["--cacheinfo", f"{modes.get(update.path, '100644')},{blob},{update.path}"]
            if additions:
                git.run("update-index", "--add", *additions, env=env)
            return git.text("write-tree", env=env)

    def seal(self, context: ProjectContext, plan: CommitPlan) -> tuple[str, str]:
        git = self._git(context.root)
        try:
            tree = self._tree_with(git, plan.reviewed_tree, plan.mechanical) if plan.mechanical else plan.reviewed_tree
            git.run("cat-file", "-e", f"{tree}^{{tree}}")
            text = self._commit_text(tree, plan.base_revision, plan.message, plan.author_name,
                                     plan.author_email, plan.committed_at)
            # Sin -w: solo calcula el identificador determinista del commit.
            commit = git.text("hash-object", "-t", "commit", "--stdin", input=text)
        except GitError as exc:
            raise CommitError(f"Commit could not be sealed: {exc}") from exc
        return tree, commit

    def check_tree_diff(self, context, before, after):
        """Rechaza una vista previa que la captura no podría verificar tras escribirla."""
        patch = self._git(context.root).run('diff-tree', '-r', '-p', '--binary', '--full-index',
            '--no-ext-diff', '--no-textconv', '--no-color', before, after)
        if len(patch) > self.max_diff_bytes:
            raise EvidenceCaptureError(f'Import diff exceeds the {self.max_diff_bytes}-byte review limit')

    def _write_mechanical(self, context: ProjectContext, intent: CommitIntent) -> None:
        # Todos los destinos se validan antes de escribir ninguno: sin estado parcial propio.
        targets = []
        for update in intent.mechanical:
            target = context.path(update.path)
            if target.exists() and (target.is_symlink() or not target.is_file()):
                raise CommitError("Mechanical update target is not a regular file")
            targets.append((update, target))
        for update, target in targets:
            if update.content is None:
                target.unlink(missing_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
            temporary = target.with_name(f".{target.name}.{intent.operation_id}.tmp")
            temporary.write_bytes(update.bytes())
            os.chmod(temporary, mode)
            os.replace(temporary, target)

    def _reachable(self, git: Git, intent: CommitIntent, head: str) -> bool:
        if head == intent.expected_commit:
            return True
        if git.code("cat-file", "-e", f"{intent.expected_commit}^{{commit}}") != 0:
            return False
        code = git.code("merge-base", "--is-ancestor", intent.expected_commit, head)
        if code not in (0, 1):
            raise CommitUncertain("Ancestry of the expected commit could not be determined")
        return code == 0

    def _refresh_index(self, git: Git, intent: CommitIntent) -> str:
        current = self._index_tree(git)
        if current == intent.expected_tree:
            return "already_current"
        if current != intent.reviewed_index_tree:
            return "left_untouched"  # contenido staged posterior a la revisión: no se descarta
        git.run("read-tree", intent.expected_tree)
        git.run("update-index", "-q", "--refresh", ok=(0, 1))
        return "refreshed"

    def _reconciled(self, git: Git, intent: CommitIntent, head: str, *, status: str) -> CommitOutcome:
        expected = self._commit_text(intent.expected_tree, intent.base_revision, intent.message,
                                     intent.author_name, intent.author_email, intent.committed_at)
        if git.run("cat-file", "commit", intent.expected_commit) != expected:
            raise CommitUncertain("Commit object with the expected id has unexpected content")
        return CommitOutcome(status, intent.operation_id, commit=intent.expected_commit,
                             tree=intent.expected_tree, head=head, index=self._refresh_index(git, intent))

    def inspect_bootstrap(self, context):
        from harness_local.adapters.bootstrap import inspect_target
        try:
            self._git(context.root).text('version')  # entorno Git comprobado en lectura
            return inspect_target(context, self._git(context.root))
        except GitError as exc:
            raise ValueError(f'Bootstrap Git environment unavailable: {exc}') from exc

    def inspect_definition(self, context, *, texts=False):
        """H6.5: borradores, archivos ajenos e inválidos del destino de una definición v2."""
        from harness_local.adapters.bootstrap import inspect_drafts
        try:
            self._git(context.root).text('version')
            return inspect_drafts(context, self._git(context.root), texts=texts)
        except GitError as exc:
            raise ValueError(f'Bootstrap Git environment unavailable: {exc}') from exc

    def write_draft(self, context, path, content, base_sha256):
        from harness_local.adapters.bootstrap import write_draft
        return write_draft(self, context, path, content, base_sha256)

    def seal_bootstrap(self, shown, operation_id, committed_at):
        from harness_local.adapters.bootstrap import seal
        return seal(self, shown, operation_id, committed_at)

    def execute_bootstrap(self, context, shown, intent):
        from harness_local.adapters.bootstrap import execute
        return execute(self, context, shown, intent)

    def execute(self, context: ProjectContext, intent: CommitIntent) -> CommitOutcome:
        git = self._git(context.root)
        self._require_root(git, context.root)
        text = self._commit_text(intent.expected_tree, intent.base_revision, intent.message,
                                 intent.author_name, intent.author_email, intent.committed_at)
        try:
            if git.text("hash-object", "-t", "commit", "--stdin", input=text) != intent.expected_commit:
                raise CommitError("Persisted commit intent is internally inconsistent")
            head = git.text("rev-parse", "--verify", "HEAD^{commit}")
            if self._reachable(git, intent, head):
                return self._reconciled(git, intent, head, status="reconciled")
            if head != intent.base_revision:
                if git.code("cat-file", "-e", f"{intent.expected_commit}^{{commit}}") == 0:
                    raise CommitUncertain(
                        f"HEAD moved from {intent.base_revision} to {head}; the expected commit object exists "
                        "but is not reachable. Recover manually with the recorded evidence")
                return CommitOutcome(
                    "invalidated", intent.operation_id, head=head,
                    diagnostic=f"HEAD moved from reviewed base {intent.base_revision} to {head} and no commit "
                               f"of operation {intent.operation_id} exists; revalidate")
            observed = self.capture(context)
            tree = json.loads(observed.provenance_json)
            if observed.fingerprint != intent.reviewed_fingerprint:
                already = (intent.mechanical and tree["worktree_tree"] == intent.expected_tree
                           and tree["index_tree"] == intent.reviewed_index_tree)
                if not already:
                    return CommitOutcome(
                        "invalidated", intent.operation_id, head=head,
                        observed_fingerprint=observed.fingerprint,
                        diagnostic=f"Content changed after review; reviewed fingerprint "
                                   f"{intent.reviewed_fingerprint}, observed {observed.fingerprint}")
            elif intent.mechanical:
                self._write_mechanical(context, intent)
                observed = self.capture(context)
                tree = json.loads(observed.provenance_json)
                if tree["worktree_tree"] != intent.expected_tree or tree["index_tree"] != intent.reviewed_index_tree:
                    return CommitOutcome(
                        "invalidated", intent.operation_id, head=head, observed_fingerprint=observed.fingerprint,
                        diagnostic="Mechanical updates did not produce the sealed tree; content changed concurrently")
            if tree["worktree_tree"] != intent.expected_tree:
                raise CommitError("Verified content does not match the sealed tree")
            written = git.text("hash-object", "-t", "commit", "-w", "--stdin", input=text)
            if written != intent.expected_commit:
                raise CommitError("Written commit id differs from the sealed id")
            update = ("update-ref", "-m", f"harness: commit {intent.operation_id}", "HEAD",
                      intent.expected_commit, intent.base_revision)
            try:
                git.run(*update)
            except GitError:
                # Un CAS fallido no demuestra por sí mismo qué ocurrió: se vuelve a observar.
                head = git.text("rev-parse", "--verify", "HEAD^{commit}")
                if self._reachable(git, intent, head):
                    return self._reconciled(git, intent, head, status="reconciled")
                if head != intent.base_revision:
                    return CommitOutcome(
                        "invalidated", intent.operation_id, head=head,
                        diagnostic=f"HEAD moved to {head} before the commit could be recorded; revalidate")
                raise
            return self._reconciled(git, intent, intent.expected_commit, status="committed")
        except GitError as exc:
            raise CommitUncertain(f"Git state could not be reconciled: {exc}") from exc

    def read_blob(self, context: ProjectContext, revision: str, path: str) -> bytes | None:
        """Bytes de un archivo en una revisión exacta; None si no existe en ella. Solo lecturas."""
        from harness_local.core.engine.context import relative_path
        relative_path(path)
        if not _OBJECT_ID.fullmatch(revision):
            raise ValueError("Expected a full Git object id")
        git = self._git(context.root)
        self._require_root(git, context.root)
        spec = f"{revision}:{path}"
        if git.code("cat-file", "-e", spec) != 0:
            return None
        if git.text("cat-file", "-t", spec) != "blob":
            raise ValueError(f"{path} is not a regular file at {revision}")
        return git.run("cat-file", "blob", spec)

    def execute_documents(self, context: ProjectContext, intent: CommitIntent, documents: list[dict]) -> CommitOutcome:
        """H2.4 con recuperación de una escritura parcial de documentos por hashes antiguo/nuevo.

        Nunca adopta bytes externos. Incluso tras una caída, el árbol al completar los
        documentos debe ser exactamente el árbol sellado y el índice debe seguir intacto.
        D072: un documento nuevo (archivo de fase) tiene hash anterior null y debe seguir ausente
        o contener ya sus bytes sellados.
        """
        git = self._git(context.root)
        head = git.text("rev-parse", "--verify", "HEAD^{commit}")
        if self._reachable(git, intent, head):
            return self.execute(context, intent)
        if head != intent.base_revision:
            return self.execute(context, intent)
        for doc in documents:
            sha = self._document_sha(context, doc)
            if sha is False:
                return CommitOutcome('invalidated', intent.operation_id, diagnostic='Export document is no longer regular')
            # `disk_sha256`: bytes locales que la vista previa confirmada sustituye (bloques regenerados, H6.2 E3).
            allowed = {doc['before_sha256'], doc['after_sha256']}
            if doc.get('disk_sha256') is not None:
                allowed.add(doc['disk_sha256'])
            if sha not in allowed:
                return CommitOutcome('invalidated', intent.operation_id,
                                     diagnostic='Document changed externally after export preview: ' + doc['path'])
        observed = self.capture(context)
        provenance = json.loads(observed.provenance_json)
        plan = CommitPlan(intent.base_revision, provenance['worktree_tree'], intent.mechanical, intent.message,
                          intent.author_name, intent.author_email, intent.committed_at)
        tree, commit = self.seal(context, plan)
        if (tree != intent.expected_tree or commit != intent.expected_commit
                or provenance['index_tree'] != intent.reviewed_index_tree):
            return CommitOutcome('invalidated', intent.operation_id, diagnostic='Checkout changed outside export blocks')
        # Cada reemplazo es atómico. Tras una caída entre documentos, se aceptan solo hashes
        # originales o sellados; no se genera otra intención/identidad de commit.
        for update in intent.mechanical:
            doc = next(d for d in documents if d['path'] == update.path)
            sha = self._document_sha(context, doc)
            if sha == doc['after_sha256']:
                continue
            allowed = {doc['before_sha256']}
            if doc.get('disk_sha256') is not None:
                allowed.add(doc['disk_sha256'])
            if sha is False or sha not in allowed:
                return CommitOutcome('invalidated', intent.operation_id, diagnostic='Document changed during export')
            self._write_mechanical(context, replace(intent, mechanical=(update,)))
        return self.execute(context, intent)

    execute_export = execute_documents  # D036: nombre conservado

    @staticmethod
    def _document_sha(context: ProjectContext, doc: dict):
        """Hash del documento; None si falta (el CAS decide si se admite); False si no es regular."""
        target = context.path(doc['path'])
        if doc.get('exact_path') and not _exact_path(context.root, doc['path']):
            return None
        if not target.exists() and not target.is_symlink():
            return None
        if not target.is_file() or target.is_symlink():
            return False
        return hashlib.sha256(target.read_bytes()).hexdigest()

    # --- H3.3: puertas y tag de fase ----------------------------------------------

    def contains(self, context: ProjectContext, commit: str) -> bool:
        """¿El commit aceptado es alcanzable desde HEAD? Solo lecturas."""
        if not isinstance(commit, str) or not _OBJECT_ID.fullmatch(commit):
            raise ValueError("Expected a full Git object id")
        git = self._git(context.root)
        self._require_root(git, context.root)
        if git.code("cat-file", "-e", f"{commit}^{{commit}}") != 0:
            return False
        code = git.code("merge-base", "--is-ancestor", commit, "HEAD")
        if code not in (0, 1):
            raise EvidenceCaptureError("Ancestry of an accepted task commit could not be determined")
        return code == 0

    @staticmethod
    def _tag_text(intent: dict) -> bytes:
        """Objeto tag anotado: mensaje, identidad y fecha fijados en la intención → id determinista."""
        GitIdentity(intent["tagger_name"], intent["tagger_email"])  # sin marcado ni saltos de línea
        if type(intent["tagged_at"]) is not int or not isinstance(intent["message"], str) or "\0" in intent["message"]:
            raise ValueError("Annotated tag intent requires an integer date and a NUL-free message")
        name = intent["ref"][len("refs/tags/"):]
        who = f"{intent['tagger_name']} <{intent['tagger_email']}> {intent['tagged_at']} +0000"
        return (f"object {intent['target']}\ntype commit\ntag {name}\ntagger {who}\n\n{intent['message']}").encode("utf-8")

    def _tag_git(self, context: ProjectContext, intent: dict) -> Git:
        ref, target = intent["ref"], intent["target"]
        if not ref.startswith("refs/tags/") or not _OBJECT_ID.fullmatch(target):
            raise ValueError("Phase tag intent must name refs/tags/<name> and a full commit id")
        if intent.get("kind", "lightweight") not in ("lightweight", "annotated"):
            raise ValueError("Unknown tag kind")
        git = self._git(context.root)
        self._require_root(git, context.root)
        if git.code("check-ref-format", ref) != 0:
            raise ValueError("Invalid tag name")
        return git

    def seal_tag(self, context: ProjectContext, intent: dict) -> str:
        """Solo calcula el id del objeto anotado (sin -w); ningún efecto antes de la intención."""
        git = self._tag_git(context, intent)
        try:
            git.run("cat-file", "-e", f"{intent['target']}^{{commit}}")
            return git.text("hash-object", "-t", "tag", "--stdin", input=self._tag_text(intent))
        except GitError as exc:
            raise CommitError(f"Phase tag could not be sealed: {exc}") from exc

    def tag(self, context: ProjectContext, intent: dict) -> dict:
        """Tag ligero o anotado determinista: crear solo si no existe (CAS); nunca mover ni sobrescribir."""
        git = self._tag_git(context, intent)
        ref, target = intent["ref"], intent["target"]
        annotated = intent.get("kind", "lightweight") == "annotated"
        # Valor esperado de la referencia: el commit (ligero) o el objeto tag sellado (anotado).
        expected = intent["object"] if annotated else target
        if annotated and not _OBJECT_ID.fullmatch(expected or ""):
            raise ValueError("Annotated tag intent requires its sealed object id")

        def observed():
            return git.run("rev-parse", "-q", "--verify", ref, ok=(0, 1)).decode("utf-8").strip() or None

        def outcome(status, **extra):
            return {"status": status, "ref": ref, "target": target, **extra}

        try:
            existing = observed()
            if existing == expected:
                return outcome("reconciled", **({"object": expected} if annotated else {}))
            if existing is not None:
                wanted = f"the sealed annotated tag {expected} for {target}" if annotated else f"the READY commit {target}"
                return outcome("conflict", observed=existing, diagnostic=(
                    f"{ref} already points to {existing}, not to {wanted}; "
                    "it is never moved automatically. Recover manually with the recorded evidence"))
            if annotated:
                written = git.text("hash-object", "-t", "tag", "-w", "--stdin", input=self._tag_text(intent))
                if written != expected:
                    raise CommitError("Annotated tag object differs from the sealed intent; nothing was referenced")
            try:
                git.run("update-ref", "-m", f"harness: close phase {intent['operation_id']}", ref, expected,
                        "0" * len(expected))
            except GitError:
                # Un CAS fallido no demuestra qué ocurrió: se vuelve a observar.
                if observed() == expected:
                    return outcome("reconciled", **({"object": expected} if annotated else {}))
                raise
            return outcome("created", **({"object": expected} if annotated else {}))
        except GitError as exc:
            raise CommitUncertain(f"Phase tag state could not be reconciled: {exc}") from exc


@dataclass(frozen=True)
class WorktreeInfo:
    path: Path
    branch: str
    base_revision: str
    head: str
    created: bool


class GitWorktrees:
    """Un worktree por tarea, conservado entre revisiones; nunca se limpia ni elimina."""

    def __init__(self, *, executable: str = "git", timeout: float = 120.0):
        self.executable = executable
        self.timeout = timeout

    def _registered(self, git: Git) -> dict[Path, dict[str, str]]:
        found: dict[Path, dict[str, str]] = {}
        current: dict[str, str] | None = None
        for line in git.run("worktree", "list", "--porcelain", "-z").decode("utf-8").split("\0"):
            key, _, value = line.partition(" ")
            if key == "worktree":
                current = {}
                found[Path(value).resolve()] = current
            elif current is not None and key:
                current[key] = value
        return found

    def prepare(self, repository: Path, destination: Path, *, branch: str, base: str = "HEAD") -> WorktreeInfo:
        repository, destination = Path(repository).resolve(strict=True), Path(destination)
        git = Git(repository, executable=self.executable, timeout=self.timeout)
        if not destination.is_absolute() or not destination.parent.is_dir():
            raise GitError("Worktree destination must be absolute with an existing parent")
        destination = destination.parent.resolve() / destination.name
        if destination == repository or destination.is_relative_to(repository):
            raise GitError("Worktree must live outside the checkout it derives from")
        if branch.startswith("-") or base.startswith("-"):
            raise GitError("Branch and base revision must not look like options")
        git.run("check-ref-format", "--branch", branch)
        base_sha = git.text("rev-parse", "--verify", f"{base}^{{commit}}")
        existing = self._registered(git).get(destination)
        if existing is not None:
            if existing.get("branch") != f"refs/heads/{branch}":
                raise GitError("A different branch is already checked out at this worktree path")
            head = existing["HEAD"]
            if git.code("merge-base", "--is-ancestor", base_sha, head) != 0:
                raise GitError("Existing task worktree does not descend from the requested base")
            return WorktreeInfo(destination, branch, base_sha, head, created=False)
        if destination.exists() or destination.is_symlink():
            raise GitError("Worktree path exists and is not a registered worktree; nothing is overwritten")
        if git.code("show-ref", "--verify", "--quiet", f"refs/heads/{branch}") == 0:
            raise GitError("Task branch already exists outside this worktree; refusing to reuse silently")
        try:
            git.run("worktree", "add", "--quiet", "-b", branch, str(destination), base_sha)
        except GitError:
            # Una carrera con otra preparación idéntica es idempotente; otro fallo se propaga.
            raced = self._registered(git).get(destination)
            if raced is not None and raced.get("branch") == f"refs/heads/{branch}":
                return WorktreeInfo(destination, branch, base_sha, raced["HEAD"], created=False)
            raise
        return WorktreeInfo(destination, branch, base_sha, base_sha, created=True)
