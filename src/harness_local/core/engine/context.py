"""Contexto explícito; ninguna ruta deriva de la ubicación del motor."""

from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class Command:
    argv: tuple[str, ...]
    cwd: str = "."
    environment: tuple[tuple[str, str], ...] = ()
    timeout_seconds: int = 1800

    def __post_init__(self):
        if not self.argv or not all(isinstance(arg, str) and arg for arg in self.argv):
            raise ValueError("Empty or invalid command argv")
        if self.timeout_seconds <= 0:
            raise ValueError("Command timeout must be positive")
        relative_path(self.cwd)


@dataclass(frozen=True)
class JUnitDeclaration:
    command: Command
    path: str
    coverage: str

    def __post_init__(self):
        path = relative_path(self.path)
        if path == PurePosixPath('.') or '.git' in path.parts or not self.coverage.strip():
            raise ValueError('JUnit requires a report file and declared test coverage')


def relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError("Expected a checkout-relative path")
    return path


@dataclass(frozen=True)
class ProjectProfile:
    name: str
    preparation: tuple[Command, ...] = ()
    validations: tuple[Command, ...] = ()
    allowed_command_prefixes: tuple[tuple[str, ...], ...] = ()
    protected_paths: tuple[str, ...] = ()
    sensitive_paths: tuple[str, ...] = ()
    sensitive_allowlist: tuple[str, ...] = ()
    executor_instructions: str = ""
    # Declaración para el futuro adaptador de preparación; no ejecutada en H2.1.
    formatter_argv: tuple[str, ...] = ()
    formatter_paths: tuple[str, ...] = ()
    junit_reports: tuple[JUnitDeclaration, ...] = ()
    # D088 punto 6 (P008-T003): patrones de modelos de datos; un diff que los toca sin el diagrama de datos del
    # layout no es aceptable. Vacío: el perfil no declara persistencia que vigilar.
    data_model_paths: tuple[str, ...] = ()

    def __post_init__(self):
        if len(self.junit_reports) > 8:
            raise ValueError('At most eight JUnit reports per profile')
        if len({item.path for item in self.junit_reports}) != len(self.junit_reports):
            raise ValueError('JUnit report paths must be unique per profile')


@dataclass(frozen=True)
class EnginePolicy:
    executor_models: tuple[str, ...]
    executor_efforts: tuple[str, ...]
    planner_model: str
    planner_effort: str
    reviewer_model: str
    reviewer_effort: str
    max_revision_cycles: int = 3
    planning_mode: str = "auto"
    # D052: `catalog` limita al catálogo; `open` admite cualquier modelo con forma
    # válida y un esfuerzo del vocabulario del proveedor ejecutor. En `open` el
    # catálogo queda como selección de referencia para contratos del servidor.
    executor_mode: str = "catalog"
    executor_effort_vocabulary: tuple[str, ...] = ()

    def __post_init__(self):
        if self.max_revision_cycles < 0 or self.planning_mode not in {"auto", "deterministic", "agent"}:
            raise ValueError("Invalid engine policy")
        if not self.executor_models or not self.executor_efforts:
            raise ValueError("Explicit executor selections required")
        if not all((self.planner_model, self.planner_effort, self.reviewer_model, self.reviewer_effort)):
            raise ValueError("Explicit planner/reviewer selections required")
        if self.executor_mode not in {"catalog", "open"}:
            raise ValueError("Executor selection mode must be catalog or open")
        if self.executor_mode == "open" and not self.executor_effort_vocabulary:
            raise ValueError("Open executor selection requires the provider effort vocabulary")
        vocabulary = self.executor_effort_vocabulary
        if vocabulary and not set(self.executor_efforts) <= set(vocabulary):
            raise ValueError("Executor efforts outside the provider vocabulary")


def policy_payload(policy: EnginePolicy) -> dict:
    """Forma congelada; omite los ajustes D052 por defecto para conservar snapshots anteriores."""
    data = asdict(policy)
    if data["executor_mode"] == "catalog":
        data.pop("executor_mode")
    if not data["executor_effort_vocabulary"]:
        data.pop("executor_effort_vocabulary")
    return data


@dataclass(frozen=True)
class ProjectContext:
    root: Path
    profile: ProjectProfile
    policy: EnginePolicy
    next_steps_file: str = "docs/NEXT_STEPS.md"
    state_file: str = "docs/STATE.md"
    # D072/H6.3 y D088: contrato documental por fase. La configuración local siempre compone "v2" (layout
    # unificado obligatorio); None solo describe contextos congelados anteriores, que se siguen leyendo.
    documents: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "root", self.root.resolve(strict=True))
        if not self.root.is_dir():
            raise ValueError("Project root must be a directory")
        relative_path(self.next_steps_file)
        relative_path(self.state_file)
        if self.documents not in (None, "v2"):
            raise ValueError("Unknown document layout")
        if self.documents and (PurePosixPath(self.state_file).parent != PurePosixPath(self.next_steps_file).parent
                               or PurePosixPath(self.state_file).parent == PurePosixPath(".")):
            raise ValueError("Document layout v2 keeps STATE and NEXT_STEPS in one documentation directory")

    def path(self, relative: str) -> Path:
        candidate = self.root / relative_path(relative)
        # También rechaza enlaces interiores aunque apunten dentro del checkout.
        if candidate.resolve() != candidate or not candidate.is_relative_to(self.root):
            raise ValueError("Checkout path contains a symlink or escapes root")
        return candidate
