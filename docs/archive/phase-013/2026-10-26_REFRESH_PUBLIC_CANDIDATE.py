"""Export a current revision with the frozen P012 positive-list exporter.

The archived implementation stays unchanged. Only its source root is rebound to the
current repository, because its original docs/phase location was archived at closure.
Pass --revision, --out, --private-manifest and --public-manifest explicitly.
"""
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main():
    archived = ROOT / 'docs/archive/phase-012/P012-T005_public_candidate.py'
    spec = importlib.util.spec_from_file_location('p012_public_candidate', archived)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    return module.main()


if __name__ == '__main__':
    raise SystemExit(main())
