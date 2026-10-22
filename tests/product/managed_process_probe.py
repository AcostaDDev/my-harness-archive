"""Offline test worker in separate processes, synthetic only."""
import json
import sys

from harness_local.adapters.engine_fake import ScriptedAgentAdapter, ScriptedCommandRunner, SyntheticWorkspace
from harness_local.core.engine.serialization import restore_context
from harness_local.services.managed import LocalSupervisor
from harness_local.storage.database import make_engine
from harness_local.storage.managed import SQLiteManagedRepository


def main():
    data = json.load(sys.stdin)
    context = restore_context(data["context"])
    engine = make_engine(data["database"])
    try:
        repository = SQLiteManagedRepository(engine)
        if data["action"] == "submit":
            job = repository.submit(context, "P001-T001", "P001", data["plan"], data["versions"], key="start")
            print(json.dumps({"job_id": job.id}))
            return

        def factory(frozen, versions):
            assert frozen == context and versions == data["versions"]

            def execute(context, request):
                with context.path("app/invocations.txt").open("a", encoding="utf-8") as output:
                    output.write("executor\n")
                context.path("app/main.txt").write_text("implemented", encoding="utf-8")
                return {"result": "synthetic"}

            return (ScriptedAgentAdapter([execute, {"task_id": "P001-T001", "verdict": "ACCEPT"}]),
                    ScriptedCommandRunner(), SyntheticWorkspace(context, ("app/main.txt", "app/invocations.txt")))

        job = LocalSupervisor(repository, factory).run_once()
        print(json.dumps({"executed": job is not None}))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
