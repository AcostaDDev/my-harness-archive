"""Installed v9 rehearsal with fake Claude/Go, synthetic Git roots and protected HTTP only.

Run --seed once, start the installation with scripts/start, configure it in the UI, restart,
then run --journeys. Stop writers before --backup; restart with the restored DB for --consult.
All writes stay under --area. Never selects an operator CLI or modifies global settings.
"""
import argparse
from http.cookiejar import CookieJar
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener


class Journey:
    def __init__(self, args):
        self.area, self.source, self.port = args.area.resolve(), args.source.resolve(), args.port
        self.operating = self.area / 'Harness Local verified'
        self.install = self.operating / 'installation'
        current = json.loads((self.install / 'current.json').read_text())
        self.generation = self.install / 'generations' / current['generation']
        self.cli = self.generation / 'venv/bin/harness-local'
        self.root = self.area / 'Synthetic projects'
        self.base = f'http://127.0.0.1:{self.port}'
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.suffix = args.suffix
        self.keys = 0
        self.token = str(time.time_ns())

    def request(self, path, data=None, method=None, key=None, expected=200):
        headers = {'X-Harness-Local': '1', 'Content-Type': 'application/json'}
        if key is True:
            self.keys += 1
            key = f't012-{self.token}-{self.keys}'
        if key:
            headers['Idempotency-Key'] = key
        payload = json.dumps(data).encode() if data is not None else None
        try:
            with self.opener.open(Request(self.base + path, payload, headers, method=method), timeout=20) as response:
                status, body = response.status, response.read()
        except HTTPError as response:
            status, body = response.code, response.read()
        assert status == expected, (path, status, body.decode()[:3000])
        return json.loads(body) if body else None

    def get(self, path):
        return self.request(path)

    def post(self, path, data, expected=200, key=True):
        return self.request(path, data, 'POST', key, expected)

    def login(self):
        keys = list((self.operating / 'data/tmp').glob('harness-session-*/login-key'))
        assert len(keys) == 1
        self.post('/api/session', {'key': keys[0].read_text()}, key=None)

    def settle(self, run):
        for _ in range(600):
            jobs = self.get(f'/api/managed/runs/{run}/jobs?limit=100')['items']
            if jobs and all(row['status'] not in ('QUEUED', 'ACTIVE') for row in jobs):
                return self.get(f'/api/managed/runs/{run}')
            time.sleep(.1)
        raise AssertionError('Synthetic job did not settle')

    def seed(self):
        self.root.mkdir(mode=0o700)
        for name in ('fake-bin', 'fake-home'):
            (self.area / name).mkdir(mode=0o700)
        probe = self.area / 'cli_process_probe.py'
        shutil.copy2(self.source / 'tests/product/cli_process_probe.py', probe)
        client = self.area / 'fake-bin/claude'
        client.write_text(f'#!{shutil.which("python3.14")}\nimport runpy,sys,os\n'
            f'os.environ.update(PROBE_SCRIPT={str(self.area / "responses.json")!r}, PROBE_RECORD={str(self.area / "calls.jsonl")!r})\n'
            f'sys.argv=[{str(probe)!r},"claude","recipe",*sys.argv[1:]]\nrunpy.run_path({str(probe)!r},run_name="__main__")\n')
        client.chmod(0o700)
        go = self.area / 'fake-bin/go'
        go.write_text(f'#!{shutil.which("python3.14")}\nfrom pathlib import Path\n'
            'root=Path.cwd()\nassert "package main" in (root/"app/main.go").read_text()\n'
            'assert (root/"go.mod").is_file()\n'
            '(root/".prepare/tests.xml").write_text(\'<testsuite><testcase name="synthetic-go"/></testsuite>\')\n')
        go.chmod(0o700)
        env = {'HOME': str(self.area / 'fake-home'), 'USER': pwd.getpwuid(os.getuid()).pw_name,
               'PATH': str(self.area / 'fake-bin') + ':/usr/bin:/bin'}
        form = {'format': 'local-config-9', 'service': {'state_dir': str(self.operating / 'data'), 'supervisor': True},
                'git': {'executable': shutil.which('git'), 'author_name': 'Synthetic QA', 'author_email': 'qa@example.invalid'},
                'agents': {'reviewer': {'provider': 'claude', 'model': 'synthetic-reviewer', 'effort': 'high',
                            'environment': env, 'timeout_seconds': 30},
                           'executor': {'provider': 'claude', 'environment': env, 'timeout_seconds': 30,
                            'tools': ['Read', 'Edit', 'Write', 'Glob', 'Grep'],
                            'allowed_tools': ['Read', 'Edit', 'Write', 'Glob', 'Grep']}},
                'registration': {'roots': [str(self.root)], 'bootstrap_enabled': True}}
        (self.area / 'global-form.json').write_text(json.dumps(form, indent=2))
        # TOML is pasted into the authenticated UI, never saved directly as product configuration.
        def value(v):
            if isinstance(v, bool): return str(v).lower()
            if isinstance(v, str): return json.dumps(v)
            if isinstance(v, list): return '[' + ', '.join(value(x) for x in v) + ']'
            if isinstance(v, dict): return '{' + ', '.join(json.dumps(k)+' = '+value(x) for k,x in v.items()) + '}'
            return str(v)
        (self.area / 'global-candidate.toml').write_text(''.join(f'{json.dumps(k)} = {value(v)}\n' for k,v in form.items()))
        print('Synthetic clients, paths and UI candidate ready; no configuration saved or activated.')

    def responses(self, **data):
        (self.area / 'responses.json').write_text(json.dumps(data))

    def drafts(self):
        def mark(name): return f'<!-- harness-local:managed-{name}:start -->\n<!-- harness-local:managed-{name}:end -->'
        return {
            'README.md': '# Synthetic Go project\n\nOffline fixture only.\n',
            'AGENTS.md': '# Rules\n\nRead documentation. Validate with go test ./....\n',
            'CLAUDE.md': '@AGENTS.md\n', 'GEMINI.md': '@AGENTS.md\n',
            'docs/DDBB-DIAGRAM.md': '# Data model\n\nNo persistent application data.\n',
            'docs/flows/main.md': '# Flow\n\n```mermaid\nflowchart LR\n    input --> outcome\n```\n',
            'docs/SPECIFICATION.md': '# Specification\n\nSynthetic Go calculator.\n',
            'docs/ARCHITECTURE.md': '# Architecture\n\nGo modules, go test ./..., no persistence.\n',
            'docs/ROADMAP.md': f'# Roadmap\n\n{mark("roadmap")}\n\n## P001 — Foundation\n\n**Objective:** Synthetic Go outcome.\n**Exit criteria:**\n- The outcome is accepted.\n',
            'docs/DECISIONS.md': f'# Decisions\n\n{mark("decisions")}\n\n## D001 — Go\n\nStatus: accepted.\n',
            'docs/STATE.md': f'# State\n\n{mark("state")}\n\n## Accumulated baseline\n\nNone.\n\n## Active phase — P001 Foundation\n\nNo notes.\n',
            'docs/NEXT_STEPS.md': f'# P001 — Foundation\n\n{mark("state")}\n\n## P001-T001 — Synthetic Go outcome\n\n**Objective:** Add the outcome.\n**Allowed paths:** `app/**`\n**Acceptance criteria:**\n- The outcome exists.\n**Validation commands:** `go test ./...`\n**Executor:** synthetic-executor / medium — Synthetic selection\n',
        }

    def proposal(self, docs):
        source = {'path': 'docs/ARCHITECTURE.md', 'sha256': hashlib.sha256(docs['docs/ARCHITECTURE.md'].encode()).hexdigest()}
        return {'name': 'own-go', 'rationale': 'The documented stack is Go.',
                'profile': {'preparation': [], 'validations': [{'argv': ['go','test','./...'], 'timeout_seconds': 30,
                    'junit': {'path': '.prepare/tests.xml', 'coverage': 'Synthetic Go packages'}}],
                    'allowed_command_prefixes': [['go','test']], 'protected_paths': ['go.mod','go.sum'],
                    'sensitive_paths': ['.env*'], 'data_model_paths': [], 'executor_instructions': 'Implement the Go outcome.'},
                'tools': [{'name': 'go', 'requirement': 'Synthetic Go tool for offline QA only.'}],
                'evidence': [{'kind': 'validation', 'index': 0, 'purpose': 'test', 'sources': [source], 'reason': 'Check synthetic packages.'},
                    {'kind': 'prefix', 'index': 0, 'purpose': 'test', 'sources': [source], 'reason': 'Allow the documented task validation.'}],
                'preparation_plan': {'write_paths': ['app/main.go','go.mod','.prepare/**','.gitignore'],
                    'local_paths': ['.prepare/**'], 'environment_paths': [], 'dependencies': [], 'network': [], 'scripts': False,
                    'executor_selection': {'model': 'synthetic-executor', 'effort': 'medium', 'reason': 'Synthetic preparation'},
                    'instructions': 'Write only the confirmed synthetic Go fixture.'}}

    def journeys(self):
        self.login()
        assert self.get('/api/managed/configuration')['mode'] == 'READY'
        results = []
        for kind in ('definition', 'onboarding'):
            project = ('created' if kind == 'definition' else 'existing') + '-' + self.suffix
            root = self.root / project
            policy = {'planning_mode': 'deterministic', 'executor_mode': 'catalog',
                      'executor_models': ['synthetic-executor'], 'executor_efforts': ['medium']}
            if kind == 'definition':
                change = {'action': 'select', 'expected_version': self.get('/api/managed/project-creation-root')['version'], 'path': str(self.root)}
                selected = self.post('/api/managed/project-creation-root/preview', change)
                self.post('/api/managed/project-creation-root/apply', {'change': change, 'preview_sha256': selected['preview_sha256'], 'confirm_path': str(self.root)})
                change = {'project_id': project, 'directory_name': project, 'root_version': self.get('/api/managed/project-creation-root')['version'], 'composition': None,
                          'policy': policy, 'work_language': 'en'}
                shown = self.post('/api/managed/project-creations/preview', change)
                self.post('/api/managed/project-creations/confirm', {'change': change, 'preview_sha256': shown['preview_sha256'], 'trust_root': shown['target']})
            else:
                root.mkdir()
                (root/'original.txt').write_text('Synthetic original preserved.\n')
                env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='Synthetic',
                    GIT_AUTHOR_EMAIL='qa@example.invalid', GIT_COMMITTER_NAME='Synthetic', GIT_COMMITTER_EMAIL='qa@example.invalid')
                for args in (['init','-q'], ['add','.'], ['commit','-qm','Synthetic source']):
                    subprocess.run(['git', '-C', str(root), *args], env=env, check=True)
                change = {'action':'register','expected_version':0,'project_id': project, 'root': str(root), 'composition': None, 'policy': policy, 'work_language': 'en'}
                shown = self.post('/api/managed/registry/preview', change)
                self.post('/api/managed/registry/apply', {'change': change, 'preview_sha256': shown['preview_sha256'], 'trust_root': str(root)})
            base = f'/api/managed/projects/{project}'
            conv = self.post(base+'/planning', {'kind': kind, 'title': 'Synthetic Go intake', **({'brief': 'Synthetic Go outcome'} if kind=='definition' else {})}, 201)
            plan = base+'/planning/'+conv['id']
            docs = self.drafts()
            self.responses(definition={'answer': 'Synthetic documents and profile', 'questions': [], 'pending': [],
                'drafts': [{'path': p, 'content': c, 'reason': 'Synthetic'} for p,c in docs.items()], 'profile': self.proposal(docs)})
            turn = self.post(plan+'/messages', {'expected_version': 0, 'text': 'Draft documents then propose a Go profile'}, 202)
            self.settle(turn['run_id'])
            detail = self.get(plan)
            assert detail['turns'][-1]['status'] == 'ANSWERED', detail['turns'][-1]
            for p in detail['proposals']:
                if p['kind'] == 'draft':
                    self.post(plan+'/proposals/'+p['id']+'/apply', {'expected_version': self.get(plan)['version'], 'proposal_sha256': p['proposal_sha256'], 'confirmed': True})
            p = next(p for p in self.get(plan)['proposals'] if p['kind']=='profile')
            body = {'proposal_id': p['id'], 'proposal_sha256': p['proposal_sha256'], 'expected_version': self.get(plan)['version']}
            shown = self.post(plan+'/profile/preview', body)
            self.post(plan+'/profile/confirm', {**body, 'preview_sha256': shown['preview_sha256'], 'confirmed': True, 'reason': 'Reviewed synthetic profile'})
            end = '/accept' if kind=='definition' else '/onboarding'
            shown = self.post(plan+end+'/preview', {})
            body = {'preview_sha256': shown['preview_sha256'], 'confirmed': True, 'reason': 'Reviewed documents'}
            if kind=='onboarding': body['profile_sha256'] = shown['profile_sha256']
            job = self.post(plan+end+('/confirm' if kind=='onboarding' else ''), body, 202)
            self.settle(job['run_id'])
            state = self.get(base+'/configuration')
            form = state['form']
            form['commands']['executables']['go'] = str(self.area/'fake-bin/go')
            body = {'form': form, 'validated': True, 'expected_version': state['version'], 'base_sha256': state['working_sha256'], 'active_sha256': None, 'reason': 'Reviewed tool mapping'}
            shown = self.post(base+'/configuration/preview', body)
            self.post(base+'/configuration/save', {**body, 'preview_sha256': shown['sha256']})
            state = self.get(base+'/configuration')
            self.post(base+'/runs', {'task_id':'P001-T001','phase_id':'P001','text':'Premature'}, 409)
            self.responses(edits={'app/main.go':'package main\nfunc main() {}\n','go.mod':'module example.invalid/synthetic\n\ngo 1.25\n','.gitignore':'.prepare/\n'}, executor={'result':'Prepared synthetic Go'})
            change = {'contract':'project-profile-preparation-1','expected_version':1,'mode':'offline',
                'configuration_revision':state['saved']['revision'],'configuration_sha256':state['saved']['sha256'],
                'proposal_id':state['proposal_id'],'proposal_sha256':state['proposal_sha256']}
            shown = self.post(base+'/preparation/preview', change)
            op = self.post(base+'/preparation/confirm', {'change':change,'preview_sha256':shown['preview_sha256'],'confirmed':True,'reason':'Reviewed preparation'})
            for _ in range(600):
                prepared = self.get(base+'/preparation')
                if prepared['operation']['status'] not in ('QUEUED','ACTIVE','PENDING','PREPARING'):
                    break
                time.sleep(.1)
            assert prepared['operation']['status']=='COMPLETED', prepared
            state = self.get(base+'/configuration')
            body = {'revision':state['saved']['revision'],'sha256':state['saved']['sha256'],'expected_version':state['version'],'reason':'Activate verified Go'}
            shown = self.post(base+'/configuration/activation/preview', body)
            self.post(base+'/configuration/activate', {**body,'preview_sha256':shown['sha256']})
            self.responses(edits={'app/main.go':'package main\nconst Outcome = 42\nfunc main() {}\n'}, executor={'result':'Implemented synthetic outcome'},
                reviewer={'task_id':'P001-T001','verdict':'ACCEPT','findings':[],'blocking_questions':[],'scope_grants':[]})
            task = self.post(base+'/runs', {'task_id':'P001-T001','phase_id':'P001','text':docs['docs/NEXT_STEPS.md']}, 202)
            ready = self.settle(task['run_id'])
            assert ready['status']=='ACCEPTANCE_READY', ready
            self.post('/api/managed/runs/'+task['run_id']+'/actions', {'action':'commit','expected_version':ready['version']}, 202)
            committed = self.settle(task['run_id'])
            assert committed['status']=='COMMITTED', committed
            if kind=='onboarding': assert (root/'original.txt').read_text()=='Synthetic original preserved.\n'
            results.append({'entry':kind,'project':project,'run_id':task['run_id'],'status':committed['status'],'preparation_id':op['id']})
            (self.area/'journey-results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(results,indent=2))

    def backup(self):
        env = dict(os.environ, TMPDIR=str(self.operating/'data/tmp'))
        for argv in (['backup-create',str(self.operating/'data/harness.sqlite3'),str(self.area/'backup'),'--artifact-root',str(self.operating/'data'),'--artifact-root',str(self.operating/'configuration'),'--writers-stopped'],
                     ['backup-verify',str(self.area/'backup')],['backup-restore',str(self.area/'backup'),str(self.operating/'data/restored')]):
            subprocess.run([str(self.cli),*argv],cwd=self.area,env=env,check=True)

    def consult(self):
        self.login()
        for run in json.loads((self.area/'journey-results.json').read_text()):
            assert self.get('/api/managed/runs/'+run['run_id'])['status']=='COMMITTED'
        assert self.get('/api/managed/configuration')['mode']=='READ_ONLY_ARCHIVE'
        assert 'local-config-9' in self.get('/api/managed/configuration/revisions/global/1')['text']
        for run in json.loads((self.area/'journey-results.json').read_text()):
            assert 'project-config-1' in self.get('/api/managed/configuration/revisions/project:'+run['project']+'/1')['text']
        self.post('/api/managed/configuration/check-clients', {'form':{}}, 409)
        print('Restored runs and configuration readable; mutations rejected without original roots.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--area',type=Path,required=True)
    parser.add_argument('--source',type=Path,default=Path.cwd())
    parser.add_argument('--port',type=int,default=8823)
    parser.add_argument('--suffix',default='final',help='Unique project suffix for this rehearsal; never reuse after failure')
    actions=parser.add_mutually_exclusive_group(required=True)
    for name in ('seed','journeys','backup','consult'): actions.add_argument('--'+name,action='store_true')
    args=parser.parse_args()
    action=next(name for name in ('seed','journeys','backup','consult') if getattr(args,name))
    getattr(Journey(args),action)()
