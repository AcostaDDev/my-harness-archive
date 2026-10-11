import ast
from pathlib import Path
import subprocess
import sys

import pytest

from harness_local.adapters.fake import FakeSimulationAdapter
from harness_local.core.simulation import SimulationService


class MemoryRepository:
    def __init__(self):
        self.saved = []

    def save(self, simulation):
        self.saved.append(simulation)


def test_core_imports_with_standard_library_only():
    source = Path(__file__).resolve().parents[2] / "src"
    result = subprocess.run([
        sys.executable, "-S", "-c",
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from harness_local.core.simulation import SimulationService; "
        "from harness_local.core.legacy import LegacyImportService; "
        "from harness_local.core.evidence import evidence_entries",
        str(source),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for path in (source / "harness_local/core").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            assert all(module.split(".")[0] in sys.stdlib_module_names
                       or module.startswith("harness_local.core") for module in modules)


def test_fake_result_is_local_and_does_not_launch_processes(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("La simulación no debe lanzar procesos.")
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    repository = MemoryRepository()
    service = SimulationService(repository, FakeSimulationAdapter())
    result = service.create("  Datos sintéticos  ")
    assert result.title == "Datos sintéticos"
    assert result.created_at.utcoffset().total_seconds() == 0
    assert len(result.events) == 3
    assert repository.saved == [result]


def test_adapter_error_is_not_saved_or_retried():
    class FailingAdapter:
        calls = 0

        def execute(self):
            self.calls += 1
            raise RuntimeError("Fallo sintético")

    repository = MemoryRepository()
    adapter = FailingAdapter()
    service = SimulationService(repository, adapter)
    with pytest.raises(RuntimeError, match="Fallo sintético"):
        service.create("Datos sintéticos")
    assert adapter.calls == 1
    assert repository.saved == []


def test_core_rejects_blank_titles_before_execution():
    repository = MemoryRepository()
    with pytest.raises(ValueError):
        SimulationService(repository, FakeSimulationAdapter()).create("  ")
    assert repository.saved == []
