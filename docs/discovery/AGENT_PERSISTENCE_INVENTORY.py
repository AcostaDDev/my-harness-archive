"""D066 static inventory. Reads only pinned public executable bytes, never runs them.

No auth/config files, provider CLI, subprocess, login, model or global writes.
Prints numeric metadata and literal offsets. Run with Python's standard library.
"""
import hashlib
import json
import mmap
from pathlib import Path
import sys

CODEX = Path('$HOME/.nvm/versions/node/v24.15.0/lib/node_modules/@openai/codex')
PINS = (
    ('codex', '0.162.1', CODEX/'node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex',
     '74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0',
     ('MemoriesToml', 'generate_memories', 'use_memories', 'HistoryPersistence', 'save-all',
      'memory_tool', 'set_project_trust_level', 'sqlite_home', 'log_dir', 'cli_auth_credentials_store')),
    ('claude', '2.1.295', Path('$HOME/.local/share/claude/versions/2.1.295'),
     '0116ee2e0a513900b633d9951367f18747686478e2b462805b8c31609f047f70',
     ('autoMemoryEnabled', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY', 'disabled_by_setting',
      'disabled_by_env_var', 'autoMemoryDirectory', 'CLAUDE_CONFIG_DIR', '--no-session-persistence')),
    ('claude', '2.1.296', Path('$HOME/.local/share/claude/versions/2.1.296'),
     'c9b5341637becbd423ddffc5b254afb645682a3868cb708bbc6cc0e7bb419937',
     ('autoMemoryEnabled', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY', 'disabled_by_setting',
      'disabled_by_env_var', 'autoMemoryDirectory', 'CLAUDE_CONFIG_DIR', '--no-session-persistence')),
)


def inventory():
    results = []
    for provider, version, path, expected, literals in PINS:
        with path.open('rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
            actual = hashlib.sha256(data).hexdigest()
            if actual != expected:
                raise ValueError('Pinned executable hash mismatch: ' + provider + '/' + version)
            offsets = {value: data.find(value.encode()) for value in literals}
            if any(offset < 0 for offset in offsets.values()):
                raise ValueError('Required public literal missing: ' + provider + '/' + version)
            results.append({'provider': provider, 'version_from_prior_baseline': version,
                            'path': str(path), 'size': len(data), 'sha256': actual,
                            'literal_offsets': offsets})
    return results


def main():
    result = {'decision': 'D066', 'inventory_kind': 'static literal presence, not runtime semantics',
              'provider_invocations': 0, 'real_cli_processes': 0, 'auth_files_read': False,
              'user_config_read': False, 'global_writes': False,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        result['binaries'] = inventory()
        result['completed'] = True
    except (OSError, ValueError):
        result['completed'] = False
        result['diagnostic'] = 'binary_unavailable_or_uncharacterized'
    print(json.dumps(result, indent=2))
    return 0 if result['completed'] else 1


if __name__ == '__main__':
    sys.exit(main())
