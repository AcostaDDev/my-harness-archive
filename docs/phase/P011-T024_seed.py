"""P011-T024 private browser QA: seed synthetic data in the installed package and keep the service serving.

Reuses the T016 driver (`P011-T016_rehearsal.py`): installed `harness-local`, the README minimal example, a fake
`claude` client answering from a scripted JSON and the HTTP API with session/CSRF. Seeds the states the browser QA
visits, then leaves `serve` on a random loopback port until `<area>/stop` exists:

- `alpha` created from scratch (work es), task COMMITTED and P001 closed with its archive;
- `beta` onboarded from an existing repository (work en), task COMMITTED;
- `gamma` created (work en) with a task whose validation keeps failing, so the run stops with a diagnostic;
- `delta` created (work es) with an answered definition whose drafts are not accepted;
- `epsilon` registered and then moved away, so the registry shows it unavailable.

Preferences end at en/en. `<area>/ready.json` gives the URL and the synthetic key file for the browser.

python3 docs/phase/P011-T024_seed.py --venv V --clone C --area A --python /abs/python3
"""
import importlib.util
import json
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('rehearsal', Path(__file__).with_name('P011-T016_rehearsal.py'))
t016 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t016)
check, git, existing_repository = t016.check, t016.git, t016.existing_repository


def failing_task(r, project, root, task_id='P001-T001'):
    """Same planner as T016 but the executor writes a test that fails: the run stops after its correction."""
    r.responses(
        planner={'task_id': task_id, 'phase_id': 'P001', 'title': 'Synthetic failing outcome', 'objective': 'Outcome',
                 'executor_prompt': 'Add the outcome and its test', 'allowed_paths': ['app/', 'tests/'],
                 'forbidden_paths': [], 'acceptance_criteria': ['The outcome is tested.'],
                 'validation_commands': [t016.VALIDATION],
                 'executor_selection': {'model': 'synthetic-executor', 'effort': 'medium', 'reason': 'Synthetic'}},
        edits={'app/__init__.py': '', 'app/outcome.py': 'VALUE = 41\n', 'tests/__init__.py': '',
               'tests/test_outcome.py': ('import unittest\n\nfrom app.outcome import VALUE\n\n\n'
                                         'class Outcome(unittest.TestCase):\n    def test_value(self):\n'
                                         '        self.assertEqual(VALUE, 42)\n')},
        executor={'result': f'Applied {task_id}'},
        reviewer={'task_id': task_id, 'verdict': 'ACCEPT', 'findings': [], 'blocking_questions': [],
                  'scope_grants': []})
    body = {'task_id': task_id, 'phase_id': 'P001', 'text': (root / 'docs/NEXT_STEPS.md').read_text()}
    job = r.post(f'/api/managed/projects/{project}/runs', body, 202, key=f'{project}-{task_id}')
    return r.settle(job['run_id'])


def main():
    parser = t016.argparse.ArgumentParser(description=__doc__,
                                          formatter_class=t016.argparse.RawDescriptionHelpFormatter)
    for name in ('--venv', '--clone', '--area', '--python'):
        parser.add_argument(name, type=Path, required=True)
    r = t016.Rehearsal(parser.parse_args())
    policy = {'planning_mode': 'agent', 'executor_mode': 'catalog', 'executor_models': ['synthetic-executor'],
              'executor_efforts': ['medium'], 'max_revision_cycles': 1}
    r.client('client-bin', t016.MINIMUM)
    config = r.config()
    r.run('init-db', '--database', r.db)
    projects = r.area / 'projects'
    with r.server(r.db, config):
        selected = {'action': 'select', 'expected_version': 0, 'path': str(projects)}
        shown = r.post('/api/managed/project-creation-root/preview', selected)
        r.post('/api/managed/project-creation-root/apply', {'change': selected, 'preview_sha256': shown['preview_sha256'],
               'confirm_path': str(projects)}, key=True)

        def create(project, work, accept=True):
            change = {'project_id': project, 'directory_name': project, 'root_version': 1, 'composition': 'python',
                      'policy': policy, 'work_language': work}
            shown = r.post('/api/managed/project-creations/preview', change)
            r.post('/api/managed/project-creations/confirm', {'change': change, 'preview_sha256': shown['preview_sha256'],
                   'trust_root': str(projects / project)}, key=f'create-{project}')
            if not accept:  # answered definition, drafts left for review in the browser
                base = f'/api/managed/projects/{project}/planning'
                cid = r.post(base, {'kind': 'definition', 'title': 'Synthetic definition',
                                    'brief': '# Brief\n\nSynthetic outcome.\n'}, 201, key=True)['id']
                r.responses(definition=r.answer(work))
                turn = r.post(f'{base}/{cid}/messages', {'expected_version': 0, 'text': 'Draft'}, 202, key=True)
                r.settle(turn['run_id'])
                return
            planning, _ = r.conversation(project, 'definition', work)
            accepted = r.post(planning + '/accept/preview', {})
            assert accepted['ready'], accepted['blockers']
            done = r.post(planning + '/accept', {'preview_sha256': accepted['preview_sha256'], 'confirmed': True,
                          'reason': 'Reviewed synthetic preview', 'resume_operation_id': None,
                          'expected_version': None}, 202, key=f'accept-{project}')
            r.settle(done['run_id'])

        def register(project, root, work):
            change = {'action': 'register', 'project_id': project, 'expected_version': 0, 'root': str(root),
                      'composition': 'python', 'policy': policy, 'work_language': work}
            shown = r.post('/api/managed/registry/preview', change)
            body = {'change': change, 'preview_sha256': shown['preview_sha256']}
            if shown.get('trust_required'):
                body['trust_root'] = shown['row']['root']
            r.post('/api/managed/registry/apply', body, key=f'register-{project}')

        r.preferences('en', 'es')
        alpha = projects / 'alpha'
        create('alpha', 'es')
        r.preferences('es', 'es')
        *_, committed, _ = r.task('alpha', alpha)
        check('alpha_committed', committed['status'] == 'COMMITTED')
        status, tags, archived = r.close('alpha', alpha, 'es')
        check('alpha_closed', status == 'CLOSED' and 'p001' in tags.split() and archived, (status, tags))

        beta = projects / 'beta'
        existing_repository(beta)
        register('beta', beta, 'en')
        planning, _ = r.conversation('beta', 'onboarding', 'en')
        shown = r.post(planning + '/onboarding/preview', {})
        done = r.post(planning + '/onboarding/confirm', {'preview_sha256': shown['preview_sha256'],
                      'profile_sha256': shown['profile_sha256'], 'reason': 'Reviewed onboarding', 'confirmed': True},
                      202, key='onboard-beta')
        r.settle(done['run_id'])
        _, _, beta_committed, _ = r.task('beta', beta)
        check('beta_committed', beta_committed['status'] == 'COMMITTED')

        r.preferences('en', 'en')
        create('gamma', 'en')
        stopped = failing_task(r, 'gamma', projects / 'gamma')
        check('gamma_stopped', stopped['status'] not in ('COMMITTED', 'ACCEPTANCE_READY'), stopped['status'])
        create('delta', 'es', accept=False)

        epsilon = projects / 'epsilon'
        existing_repository(epsilon)
        register('epsilon', epsilon, 'en')
        epsilon.rename(projects / 'epsilon-moved')

        r.preferences('en', 'en')
        key = next(line for line in (r.area / 'server.log').read_text().splitlines() if 'access key at' in line)
        ready = {'base': r.base, 'key_file': key.split('access key at ', 1)[1].strip(), 'results': t016.results,
                 'gamma_status': stopped['status']}
        (r.area / 'ready.json').write_text(json.dumps(ready, indent=2))
        print(json.dumps(ready, indent=2), flush=True)
        while not (r.area / 'stop').exists():
            time.sleep(.5)


if __name__ == '__main__':
    main()
