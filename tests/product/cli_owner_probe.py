"""Synthetic supervisor process, deliberately killed by the H2.3 recovery test."""
import json
from pathlib import Path
import sys

from harness_local.adapters.cli_agents import CLIConfig, CLIProcessAdapter
from harness_local.adapters.engine_fake import ScriptedCommandRunner, SyntheticWorkspace
from harness_local.core.engine.serialization import restore_context
from harness_local.services.managed import LocalSupervisor
from harness_local.storage.database import make_engine
from harness_local.storage.managed import SQLiteManagedRepository


def main():
    url, specification = sys.argv[1:]
    data = json.loads(Path(specification).read_text())
    configs = [CLIConfig(**{**value, 'executable':tuple(value['executable']),
                           'environment':tuple(tuple(pair) for pair in value['environment'])})
               for value in data['configs']]
    port = CLIProcessAdapter(configs, data['artifacts'])
    context = restore_context(data['context'])
    repository = SQLiteManagedRepository(make_engine(url))
    def factory(ctx, versions):
        return port, ScriptedCommandRunner([]), SyntheticWorkspace(context, ('app/main.txt',))
    LocalSupervisor(repository, factory, lease_seconds=.6).run_once()


if __name__ == '__main__':
    main()
