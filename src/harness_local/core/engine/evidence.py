"""Evidencia suministrada por puerto; política sin restauraciones de archivos."""

from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import Protocol

from harness_local.core.engine.context import ProjectContext, relative_path


@dataclass(frozen=True)
class ContentEvidence:
    base_revision: str
    fingerprint: str
    changed_paths: tuple[str, ...]
    diff: str


class EvidenceCapture(Protocol):
    def capture(self, context: ProjectContext) -> ContentEvidence: ...


@dataclass(frozen=True)
class PathPolicyResult:
    violations: tuple[str, ...]

    @property
    def hard_failure(self) -> bool:
        return bool(self.violations)


def matches(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    return any(fnmatchcase(path, pattern) for pattern in patterns)


def check_paths(context: ProjectContext, task: dict, evidence: ContentEvidence) -> PathPolicyResult:
    violations = []
    for path in evidence.changed_paths:
        try:
            relative_path(path)
            context.path(path)
        except ValueError:
            violations.append(path)
            continue
        sensitive = (matches(path, context.profile.sensitive_paths)
                     and not matches(path, context.profile.sensitive_allowlist))
        if (sensitive or matches(path, context.profile.protected_paths)
                or matches(path, task["forbidden_paths"]) or not matches(path, task["allowed_paths"])):
            violations.append(path)
    return PathPolicyResult(tuple(sorted(set(violations))))
