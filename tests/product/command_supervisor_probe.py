"""Separate synthetic supervisor, killed after a persisted validator byte event."""
import json
import os
import sys

from harness_local.adapters.commands import CommandConfig, ManagedCommandRunner
from harness_local.adapters.engine_fake import ScriptedAgentAdapter, SyntheticWorkspace
from harness_local.core.engine.serialization import restore_command
from harness_local.services.managed import LocalSupervisor
from harness_local.storage.database import make_engine
from harness_local.storage.managed import SQLiteManagedRepository


def main():
    data = json.loads(open(sys.argv[2]).read())
    data['authorized_commands'] = tuple(restore_command(c) for c in data['authorized_commands'])
    for key in ('executables', 'environment'):
        data[key] = tuple(tuple(p) for p in data[key])
    config = CommandConfig(**data)
    class CrashingRepository(SQLiteManagedRepository):
        def command_process_event(self, claim, command_id, kind, payload):
            super().command_process_event(claim, command_id, kind, payload)
            if kind == 'bytes':
                os._exit(90)
    repository = CrashingRepository(make_engine(sys.argv[1]))
    def ports(context, versions):
        return ScriptedAgentAdapter([]), ManagedCommandRunner(config), SyntheticWorkspace(context, ())
    LocalSupervisor(repository, ports, lease_seconds=0.3).run_once()


if __name__ == '__main__':
    main()
