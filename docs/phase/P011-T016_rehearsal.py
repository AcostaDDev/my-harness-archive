"""P011-T016 private rehearsal: README first use with the installed package, fake CLIs and synthetic data.

Drives the installed `harness-local` (never this checkout's code) as an operator would: the minimal example TOML with
its placeholders replaced, a fake `claude` client on the role's explicit PATH (the public probe in `recipe` mode,
answering from a scripted JSON), `check-config --preflight`, `init-db`, `serve` on a random loopback port and the HTTP
API with the session key and CSRF header. Both entries (from scratch and onboarding of an existing repository), the
four visual/work language pairs, defaults that do not change projects, immutable work language, later/older fake
clients, restart, `migrate`, backup/restore and retired routes. Stdlib only; prints a sanitized JSON summary.

python3 docs/phase/P011-T016_rehearsal.py --venv V --clone C --area A --python /abs/python3
"""
import argparse
from contextlib import contextmanager
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener

MINIMUM, LATER, OLDER = '2.1.304', '2.1.305', '2.1.200'
VALIDATION = 'python3 -m unittest discover -s tests -t .'
CRITERION = {'es': 'El flujo sintético está aceptado.', 'en': 'The synthetic flow is accepted.'}
DIRECTIVE = 'Respond to the user in {ui}. Write project documentation and code in {work}.'
NAMES = {'en': 'English', 'es': 'Spanish'}
results: dict = {}


def check(name, condition, detail=None):
    results[name] = bool(condition) if detail is None else {'ok': bool(condition), 'detail': detail}
    if not condition:
        raise AssertionError(f'{name}: {detail}')


class Rehearsal:
    def __init__(self, args):
        self.venv, self.clone, self.area, self.python = args.venv, args.clone, args.area, args.python
        self.cli = self.venv / 'bin/harness-local'
        self.script = self.area / 'responses.json'
        self.record = self.area / 'calls.jsonl'
        for name in ('client-bin', 'client-later', 'client-older', 'agent-home', 'command-home', 'harness-state',
                     'projects', 'state', 'private-tmp'):
            (self.area / name).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.env = {'PATH': f'{self.venv}/bin:/usr/bin:/bin', 'LANG': 'en_US.UTF-8', 'PYTHONNOUSERSITE': '1',
                    'TMPDIR': str(self.area / 'private-tmp'), 'HOME': str(self.area / 'agent-home')}
        self.db = self.area / 'state/harness.sqlite3'
        self.opener = None
        self.keys = 0

    # --- operator files -----------------------------------------------------------------------------------------
    def client(self, folder, version):
        """Fake Claude Code: fixed version line, then the public probe in `recipe` mode (scripted answers)."""
        probe = self.clone / 'tests/product/cli_process_probe.py'
        path = self.area / folder / 'claude'
        path.write_text(f'''#!{self.python}
import os, runpy, sys
if sys.argv[1:] == ['--version']:
    print({f"{version} (Claude Code)"!r}); sys.exit(0)
os.environ.update(PROBE_SCRIPT={str(self.script)!r}, PROBE_RECORD={str(self.record)!r})
sys.argv = [{str(probe)!r}, 'claude', 'recipe', *sys.argv[1:]]
runpy.run_path({str(probe)!r}, run_name='__main__')
''')
        path.chmod(0o700)

    def config(self, client_bin='client-bin', name='harness-local.toml'):
        """The README's minimal example with every placeholder replaced; nothing else changes."""
        text = (self.clone / 'examples/local_config.minimal.example.toml').read_text()
        user = pwd.getpwuid(os.getuid()).pw_name
        for old, new in (('/ABSOLUTE/PATH/harness-state', self.area / 'harness-state'),
                         ('/ABSOLUTE/PATH/client-bin', self.area / client_bin),
                         ('/ABSOLUTE/PATH/projects', self.area / 'projects'),
                         ('/ABSOLUTE/PATH/python3', self.python),
                         ('/ABSOLUTE/PATH/command-home', self.area / 'command-home'),
                         ('/Users/USER', self.area / 'agent-home'), ('"USER"', f'"{user}"'),
                         ('REVIEWER-MODEL', 'synthetic-reviewer')):
            text = text.replace(old, str(new))
        values = '\n'.join(line.split('#', 1)[0] for line in text.splitlines())  # comments keep the placeholders
        assert not re.search(r'/ABSOLUTE/PATH|"USER"|/Users/USER|REVIEWER-MODEL', values), values
        path = self.area / name
        path.write_text(text)
        path.chmod(0o600)
        return path

    def run(self, *argv, ok=True, ui=None):
        language = ('--ui-language', ui) if ui else ()
        result = subprocess.run([str(self.cli), *language, *map(str, argv)], cwd=self.area, env=self.env,
                                capture_output=True, text=True, timeout=120)
        assert (result.returncode == 0) == ok, (argv, result.stdout[-800:], result.stderr[-800:])
        return result

    def responses(self, **payloads):
        self.script.write_text(json.dumps(payloads))

    # --- HTTP -----------------------------------------------------------------------------------------------------
    def request(self, path, data=None, method=None, key=None, raw=False):
        body = json.dumps(data).encode() if data is not None else None
        headers = {'Content-Type': 'application/json', 'X-Harness-Local': '1'}
        if key:
            headers['Idempotency-Key'] = key
        try:
            with self.opener.open(Request(self.base + path, body, headers=headers, method=method), timeout=10) as r:
                status, payload = r.status, r.read()
        except HTTPError as error:
            status, payload = error.code, error.read()
        if raw:
            return status, payload
        return status, (json.loads(payload) if payload.strip().startswith((b'{', b'[')) else payload)

    def post(self, path, data, expected=200, key=None):
        if key is True:
            self.keys += 1
            key = f'rehearsal-{self.keys}'
        status, body = self.request(path, data, 'POST', key)
        assert status == expected, (path, status, body)
        return body

    def get(self, path):
        status, body = self.request(path)
        assert status == 200, (path, status, body)
        return body

    @contextmanager
    def server(self, database, config=None):
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        with socket.socket() as bound:
            bound.bind(('127.0.0.1', 0))
            port = bound.getsockname()[1]
        self.base = f'http://127.0.0.1:{port}'
        log = (self.area / 'server.log').open('w+')
        argv = [str(self.cli), 'serve', '--database', str(database), '--port', str(port)]
        process = subprocess.Popen(argv + (['--config', str(config)] if config else []), cwd=self.area, env=self.env,
                                   stdout=log, stderr=log)
        try:
            for _ in range(150):
                if process.poll() is not None:
                    log.seek(0)
                    raise AssertionError(log.read())
                try:
                    if self.request('/api/health')[0] == 401:
                        break
                except (URLError, TimeoutError, ConnectionError):
                    pass
                time.sleep(.1)
            log.flush()
            log.seek(0)
            key = Path(re.search(r'access key at (.+)', log.read())[1]).read_text()
            assert self.request('/api/session', {'key': key}, 'POST')[0] == 200
            yield self
            assert self.request('/api/session', method='DELETE')[0] == 204
        finally:
            process.terminate()
            process.wait(timeout=20)
            log.close()

    def settle(self, run_id, done=('COMMITTED', 'ACCEPTANCE_READY', 'COMPLETED', 'STOPPED', 'FAILED')):
        for _ in range(600):
            jobs = self.get(f'/api/managed/runs/{run_id}/jobs?limit=100')['items']
            if jobs and all(job['status'] not in ('QUEUED', 'ACTIVE') for job in jobs):
                return self.get(f'/api/managed/runs/{run_id}')
            time.sleep(.05)
        raise AssertionError(f'run {run_id} did not settle')

    def prompts(self):
        return [json.loads(line)['prompt'] for line in self.record.read_text().splitlines()] if self.record.exists() else []

    # --- journeys -------------------------------------------------------------------------------------------------
    def preferences(self, ui, work):
        current = self.get('/api/managed/preferences')
        status, body = self.request('/api/managed/preferences', {'expected_version': current['version'],
                                    'ui_language': ui, 'default_work_language': work}, 'PUT',
                                    key=f"preferences-{current['version']}-{ui}-{work}")
        assert status == 200 and (body['ui_language'], body['default_work_language']) == (ui, work), (status, body)
        return body

    def drafts(self, work):
        es = work == 'es'
        tests = f'`{VALIDATION}`'
        markers = lambda name: (f'<!-- harness-local:managed-{name}:start -->', f'<!-- harness-local:managed-{name}:end -->')
        (sb, se), (rb, re_), (db, de) = markers('state'), markers('roadmap'), markers('decisions')
        return {
            'README.md': '# Sintético\n\nHerramienta local sintética.\n' if es else '# Synthetic\n\nSynthetic tool.\n',
            'docs/SPECIFICATION.md': '# Especificación\n\n## Problema\n\nFlujo sintético.\n' if es else
                                     '# Specification\n\n## Problem\n\nSynthetic flow.\n',
            'docs/ARCHITECTURE.md': '# Arquitectura\n\n## Stack\n\nPython estándar.\n' if es else
                                    '# Architecture\n\n## Stack\n\nStandard Python.\n',
            'docs/DDBB-DIAGRAM.md': '# Modelo de datos\n\n```mermaid\nerDiagram\n  ITEM ||--o{ STEP : has\n```\n',
            'docs/flows/flow.md': '# Flow\n\n```mermaid\nflowchart LR\n  item --> step\n```\n',
            'docs/ROADMAP.md': (f'# Roadmap\n\n{rb}\n{re_}\n\n## P001 — Fundamentos\n\n'
                                f'**Objetivo:** Entregar el flujo sintético.\n**Criterios de salida:**\n'
                                f'- {CRITERION[work]}\n**Tag:** `p001`\n'),
            'docs/DECISIONS.md': (f'# Decisions\n\nSingle record.\n\n{db}\n{de}\n\n## D001 — Standard library\n\n'
                                  '**Estado:** aceptada\n**Fecha:** 2026-10-23\n**Fase:** P000\n'),
            'docs/STATE.md': (f'# State\n\n{sb}\n{se}\n\n## Base acumulada\n\nNothing accepted yet.\n\n'
                              '## Fase activa — P001 Fundamentos\n\nNo notes yet.\n'),
            'docs/NEXT_STEPS.md': (f'# P001 — Fundamentos\n\nGoal in [ROADMAP](ROADMAP.md).\n\n{sb}\n{se}\n\n'
                                   '## P001-T001 — Synthetic outcome\n\n**Objetivo:** Record the outcome.\n'
                                   '**Rutas permitidas:** `app/**`, `tests/**`\n**Criterios de aceptación:**\n'
                                   f'- The outcome is tested.\n**Comandos de validación:** {tests}\n'),
        }

    def answer(self, work, kind='definition'):
        drafts = self.drafts(work)
        if kind == 'onboarding':  # creation takes the instruction files from the template; onboarding drafts them
            drafts |= {'AGENTS.md': '# Rules\n\nRead docs/STATE.md and docs/NEXT_STEPS.md before working.\n',
                       'CLAUDE.md': '@AGENTS.md\n', 'GEMINI.md': '@AGENTS.md\n'}
        return {'answer': 'Synthetic drafts', 'questions': [], 'pending': [],
                'drafts': [{'path': p, 'content': c, 'reason': 'Synthetic'} for p, c in drafts.items()]}

    def conversation(self, project, kind, work, title='Synthetic'):
        base = f'/api/managed/projects/{project}/planning'
        body = {'kind': kind, 'title': title, **({'brief': '# Brief\n\nSynthetic outcome.\n'} if kind == 'definition' else {})}
        cid = self.post(base, body, 201, key=True)['id']
        self.responses(definition=self.answer(work, kind))
        before = len(self.prompts())
        turn = self.post(f'{base}/{cid}/messages', {'expected_version': 0, 'text': 'Draft'}, 202, key=True)
        self.settle(turn['run_id'])
        detail = self.get(f'{base}/{cid}')
        assert detail['turns'][-1]['status'] == 'ANSWERED', detail['turns'][-1]
        for proposal in detail['proposals']:
            self.post(f"{base}/{cid}/proposals/{proposal['id']}/apply", {
                'expected_version': self.get(f'{base}/{cid}')['version'],
                'proposal_sha256': proposal['proposal_sha256'], 'confirmed': True})
        return f'{base}/{cid}', self.prompts()[before:]

    def task(self, project, root, task_id='P001-T001'):
        self.responses(
            planner={'task_id': task_id, 'phase_id': 'P001', 'title': 'Synthetic outcome', 'objective': 'Outcome',
                     'executor_prompt': 'Add the outcome and its test', 'allowed_paths': ['app/', 'tests/'],
                     'forbidden_paths': [], 'acceptance_criteria': ['The outcome is tested.'],
                     'validation_commands': [VALIDATION],
                     'executor_selection': {'model': 'synthetic-executor', 'effort': 'medium', 'reason': 'Synthetic'}},
            edits={'app/__init__.py': '', 'app/outcome.py': 'VALUE = 42\n', 'tests/__init__.py': '',
                   'tests/test_outcome.py': ('import unittest\n\nfrom app.outcome import VALUE\n\n\n'
                                             'class Outcome(unittest.TestCase):\n    def test_value(self):\n'
                                             '        self.assertEqual(VALUE, 42)\n')},
            executor={'result': f'Applied {task_id}'},
            reviewer={'task_id': task_id, 'verdict': 'ACCEPT', 'findings': [], 'blocking_questions': [],
                      'scope_grants': []})
        before = len(self.prompts())
        body = {'task_id': task_id, 'phase_id': 'P001', 'text': (root / 'docs/NEXT_STEPS.md').read_text()}
        job = self.post(f'/api/managed/projects/{project}/runs', body, 202, key=f'{project}-{task_id}')
        accepted = self.settle(job['run_id'])
        assert accepted['status'] == 'ACCEPTANCE_READY', accepted['history'].get('stop')
        self.commit_body = {'action': 'commit', 'expected_version': accepted['version']}
        commit = self.post(f"/api/managed/runs/{job['run_id']}/actions", self.commit_body, 202, key=f'{project}-commit')
        committed = self.settle(job['run_id'])
        assert committed['status'] == 'COMMITTED', committed['history'].get('stop')
        return job, commit, committed, self.prompts()[before:]

    def close(self, project, root, work):
        phase = next(p for p in self.get(f'/api/managed/projects/{project}/phases') if p['code'] == 'P001')
        path = f"/api/managed/phases/{phase['id']}"
        self.responses(phase={'phase_id': 'P001', 'verdict': 'READY', 'summary': 'Synthetic phase accepted',
                              'exit_criteria_results': [{'criterion': CRITERION[work], 'passed': True,
                                                         'evidence': 'One exact accepted commit'}],
                              'required_actions': [], 'blocking_questions': []})
        checked = self.post(path + '/actions', {'action': 'check', 'expected_version': self.get(path)['version']},
                            202, key=f'{project}-check')
        self.settle(checked['run_id'])
        detail = self.get(path)
        assert detail['status'] == 'READY_TO_CLOSE', detail['status']
        closed = self.post(path + '/actions', {'action': 'close', 'expected_version': detail['version'],
                           'binding_sha256': detail['ready']['binding_sha256'], 'reason': 'Close synthetic P001',
                           'confirmed': True}, 202, key=f'{project}-close')
        self.settle(closed['run_id'])
        return self.get(path)['status'], git(root, 'tag', '--list'), (root / 'docs/archive/phase-001/STATE.md').is_file()


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True,
                          env={'PATH': '/usr/bin:/bin', 'GIT_CONFIG_GLOBAL': '/dev/null',
                               'GIT_CONFIG_NOSYSTEM': '1'}).stdout.strip()


def existing_repository(root):
    """Small committed Python repository without harness documents, for the onboarding entry."""
    (root / 'calc').mkdir(parents=True)
    (root / 'calc/__init__.py').write_text('def add(a, b):\n    return a + b\n')
    (root / 'tests').mkdir()
    (root / 'tests/__init__.py').write_text('')
    (root / 'tests/test_calc.py').write_text('import unittest\n\nfrom calc import add\n\n\n'
                                             'class Add(unittest.TestCase):\n    def test_add(self):\n'
                                             '        self.assertEqual(add(2, 3), 5)\n')
    (root / 'README.md').write_text('# calc\n\nExisting synthetic library.\n')
    identity = {'GIT_AUTHOR_NAME': 'Synthetic', 'GIT_AUTHOR_EMAIL': 'synthetic@example.invalid',
                'GIT_COMMITTER_NAME': 'Synthetic', 'GIT_COMMITTER_EMAIL': 'synthetic@example.invalid'}
    for argv in (['init', '-q', '-b', 'main'], ['add', '.'], ['commit', '-qm', 'Existing code']):
        subprocess.run(['git', '-C', str(root), *argv], check=True, env={'PATH': '/usr/bin:/bin', **identity,
                       'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ('--venv', '--clone', '--area', '--python'):
        parser.add_argument(name, type=Path, required=True)
    args = parser.parse_args()
    r = Rehearsal(args)
    policy = {'planning_mode': 'agent', 'executor_mode': 'catalog', 'executor_models': ['synthetic-executor'],
              'executor_efforts': ['medium'], 'max_revision_cycles': 1}

    # 1. Configuration and fake clients: minimum, later candidate and older client.
    for folder, version in (('client-bin', MINIMUM), ('client-later', LATER), ('client-older', OLDER)):
        r.client(folder, version)
    config = r.config()
    for ui in ('en', 'es'):
        out = r.run('check-config', config, '--preflight', ui=ui).stdout
        check(f'check_config_preflight_{ui}', 'python-unittest' in out and str(r.area / 'agent-home') not in out)
    later = r.run('check-config', r.config('client-later', 'later.toml'), '--preflight').stdout
    check('later_client_admitted', LATER in later or 'candidate' in later.lower(), later[-300:])
    older = r.run('check-config', r.config('client-older', 'older.toml'), '--preflight', ok=False)
    check('older_client_refused', MINIMUM in older.stdout + older.stderr, (older.stdout + older.stderr)[-300:])
    check('no_model_called_by_preflight', not r.record.exists())
    for command in ('legacy-import', 'legacy-summary'):
        check(f'retired_cli_{command}', r.run(command, ok=False).returncode == 2)

    # 2. First run: init-db, serve with the TOML; supervisor consumes the queue with the fake client.
    r.run('init-db', '--database', r.db)
    r.run('init-db', '--database', r.db, ok=False)
    projects = r.area / 'projects'
    with r.server(r.db, config):
        check('ui_served', b'<div id="root">' in r.request('/', raw=True)[1])
        retired = ['/api/legacy/projects', '/api/legacy/events', '/api/managed/projects/x/import',
                   '/api/managed/projects/x/migration/preview']
        check('retired_routes_404', all(r.request(p)[0] == 404 for p in retired))
        prefs = r.get('/api/managed/preferences')
        check('preferences_default_en', (prefs['ui_language'], prefs['default_work_language']) == ('en', 'en'))
        r.preferences('en', 'es')
        # From scratch: alpha (visual en during definition, work es).
        selected = {'action': 'select', 'expected_version': 0, 'path': str(projects)}
        shown = r.post('/api/managed/project-creation-root/preview', selected)
        r.post('/api/managed/project-creation-root/apply', {'change': selected, 'preview_sha256': shown['preview_sha256'],
               'confirm_path': str(projects)}, key=True)

        def create(project, work):
            change = {'project_id': project, 'directory_name': project, 'root_version': 1, 'composition': 'python',
                      'policy': policy, 'work_language': work}
            shown = r.post('/api/managed/project-creations/preview', change)
            r.post('/api/managed/project-creations/confirm', {'change': change, 'preview_sha256': shown['preview_sha256'],
                   'trust_root': str(projects / project)}, key=f'create-{project}')
            planning, prompts = r.conversation(project, 'definition', work)
            accept = r.post(planning + '/accept/preview', {})
            assert accept['ready'], accept['blockers']
            done = r.post(planning + '/accept', {'preview_sha256': accept['preview_sha256'], 'confirmed': True,
                          'reason': 'Reviewed synthetic preview', 'resume_operation_id': None, 'expected_version': None},
                          202, key=f'accept-{project}')
            r.settle(done['run_id'])
            return prompts

        alpha_root = projects / 'alpha'
        prompts = create('alpha', 'es')
        check('pair_en_es_definition', DIRECTIVE.format(ui='English', work='Spanish') in prompts[-1])
        agents = (alpha_root / 'AGENTS.md').read_text()
        check('alpha_template_in_spanish', 'instrucciones' in agents.lower() or 'agentes' in agents.lower(),
              agents.splitlines()[0])
        r.preferences('es', 'es')
        job, commit, committed, prompts = r.task('alpha', alpha_root)
        commit_body = r.commit_body
        check('pair_es_es_task', all(DIRECTIVE.format(ui='Spanish', work='Spanish') in p for p in prompts)
              and len(prompts) == 3)
        check('alpha_committed', committed['status'] == 'COMMITTED' and git(alpha_root, 'status', '--porcelain') == '')
        frozen = r.get(f"/api/managed/jobs/{job['id']}").get('language_context')
        status, tags, archived = r.close('alpha', alpha_root, 'es')
        check('alpha_closed', status == 'CLOSED' and 'p001' in tags.split() and archived, (status, tags))

        # Onboarding an existing repository: beta (visual es, work en).
        beta_root = projects / 'beta'
        existing_repository(beta_root)
        register = {'action': 'register', 'project_id': 'beta', 'expected_version': 0, 'root': str(beta_root),
                    'composition': 'python', 'policy': policy, 'work_language': 'en'}
        shown = r.post('/api/managed/registry/preview', register)
        body = {'change': register, 'preview_sha256': shown['preview_sha256']}
        if shown.get('trust_required'):
            body['trust_root'] = shown['row']['root']
        r.post('/api/managed/registry/apply', body, key='register-beta')
        planning, prompts = r.conversation('beta', 'onboarding', 'en')
        check('pair_es_en_onboarding', DIRECTIVE.format(ui='Spanish', work='English') in prompts[-1])
        shown = r.post(planning + '/onboarding/preview', {})
        done = r.post(planning + '/onboarding/confirm', {'preview_sha256': shown['preview_sha256'],
                      'profile_sha256': shown['profile_sha256'], 'reason': 'Reviewed onboarding', 'confirmed': True},
                      202, key='onboard-beta')
        r.settle(done['run_id'])
        check('beta_onboarded', (beta_root / 'AGENTS.md').is_file() and (beta_root / 'calc/__init__.py').is_file()
              and int(git(beta_root, 'rev-list', '--count', 'HEAD')) == 2)
        _, _, beta_committed, _ = r.task('beta', beta_root)
        check('beta_committed', beta_committed['status'] == 'COMMITTED')

        # gamma: visual en, work en (definition only); defaults never change existing projects.
        r.preferences('en', 'en')
        prompts = create('gamma', 'en')
        check('pair_en_en_definition', DIRECTIVE.format(ui='English', work='English') in prompts[-1])
        r.preferences('es', 'es')
        languages = {p: r.get(f'/api/managed/projects/{p}')['work_language']['work_language']
                     for p in ('alpha', 'beta', 'gamma')}
        check('defaults_do_not_change_projects', languages == {'alpha': 'es', 'beta': 'en', 'gamma': 'en'}, languages)
        change = {'action': 'update', 'project_id': 'beta', 'expected_version': 1, 'composition': 'python',
                  'policy': policy, 'work_language': 'es'}
        status, body = r.request('/api/managed/registry/preview', change, 'POST')
        check('work_language_immutable', status in (409, 422), (status, str(body)[:200]))
        alpha_run = r.get(f"/api/managed/runs/{job['run_id']}")
        # The visual language changed after the task; its frozen pair stays as admitted (es/es).
        after = r.get(f"/api/managed/jobs/{job['id']}").get('language_context')
        check('frozen_pair_unchanged', frozen == after and (frozen or {}).get('ui_language') == 'es'
              and frozen.get('work_language') == 'es', frozen)
    # 3. Restart: the same evidence, replayed actions, nothing new invoked.
    calls = r.record.read_bytes()
    with r.server(r.db, config):
        check('restart_same_run', r.get(f"/api/managed/runs/{job['run_id']}") == alpha_run)
        replay = r.post(f"/api/managed/runs/{job['run_id']}/actions", commit_body, 202, key='alpha-commit')
        check('restart_replay_idempotent', replay['id'] == commit['id'])
        time.sleep(.3)
        check('restart_no_new_calls', r.record.read_bytes() == calls)
    # 4. Operation commands as the README writes them.
    migrated = json.loads(r.run('migrate', '--database', r.db, '--snapshots', r.area / 'pre-migration',
                                '--writers-stopped').stdout)
    check('migrate_current', migrated['action'] == 'current', migrated)
    backup, restored = r.area / 'new-backup', r.area / 'restored'
    r.run('backup-create', r.db, backup, '--artifact-root', r.area / 'harness-state', '--writers-stopped')
    r.run('backup-verify', backup)
    r.run('backup-restore', backup, restored)
    with r.server(restored / 'state.sqlite3'):
        check('restored_read_only_same_run', r.get(f"/api/managed/runs/{job['run_id']}")['history']
              == alpha_run['history'])
        status, _ = r.request(f"/api/managed/runs/{job['run_id']}/actions",
                              {'action': 'commit', 'expected_version': committed['version']}, 'POST', 'restored')
        check('restored_refuses_mutation', status == 409, status)
    results['calls_by_prompt'] = len(r.prompts())
    results['frozen_language_context'] = frozen
    print(json.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    try:
        main()
    except AssertionError:
        print(json.dumps(results, indent=2, default=str))
        raise
