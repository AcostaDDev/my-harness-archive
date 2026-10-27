"""P013 export: frozen positive list, with absolute /home path matching.

The archived scanner flags prose such as logs/reports/home/temp as a personal
absolute path. Require a path boundary before /home; keep the other private
patterns, classification, manifests, and materialized-tree checks unchanged.
"""
import importlib.util
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True  # Importing frozen tools must not create archive caches.


def main():
    spec = importlib.util.spec_from_file_location('frozen_export', ROOT / 'docs/archive/phase-012/P012-T005_public_candidate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    module.PRIVATE = re.compile(module.PRIVATE.pattern.replace('/home/', r'(?<![\w/])/home/'), module.PRIVATE.flags)
    assert not module.PRIVATE.search('exclude transient logs/reports/home/temp')
    for private in ('/home/alice/project', '"/home/alice/project"', 'at /home/alice/project', '/Users/alice/project'):
        assert module.PRIVATE.search(private), private
    return module.main()


if __name__ == '__main__':
    raise SystemExit(main())
