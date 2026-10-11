"""Contexto explícito; ninguna ruta deriva de la ubicación del motor."""

from dataclasses import dataclass
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

    def __post_init__(self):
        if self.max_revision_cycles < 0 or self.planning_mode not in {"auto", "deterministic", "agent"}:
            raise ValueError("Invalid engine policy")
        if not self.executor_models or not self.executor_efforts:
            raise ValueError("Explicit executor selections required")
        if not all((self.planner_model, self.planner_effort, self.reviewer_model, self.reviewer_effort)):
            raise ValueError("Explicit planner/reviewer selections required")


@dataclass(frozen=True)
class ProjectContext:
    root: Path
    profile: ProjectProfile
    policy: EnginePolicy
    next_steps_file: str = "docs/NEXT_STEPS.md"
    state_file: str = "docs/STATE.md"

    def __post_init__(self):
        object.__setattr__(self, "root", self.root.resolve(strict=True))
        if not self.root.is_dir():
            raise ValueError("Project root must be a directory")
        relative_path(self.next_steps_file)
        relative_path(self.state_file)

    def path(self, relative: str) -> Path:
        candidate = self.root / relative_path(relative)
        # También rechaza enlaces interiores aunque apunten dentro del checkout.
        if candidate.resolve() != candidate or not candidate.is_relative_to(self.root):
            raise ValueError("Checkout path contains a symlink or escapes root")
        return candidate
