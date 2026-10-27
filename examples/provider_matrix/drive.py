"""Recorrido HTTP de una combinación de la matriz D052 (D055, D057). Una sola vez, sin reintentos.

Uso: python -I drive.py ÁREA PAR RUTA_CLAVE, con el servicio ya escuchando en 127.0.0.1:8013.
Sesión, fase P001, run P001-T001 y, solo si queda ACCEPTANCE_READY, commit. Guarda la
instantánea de la API en ÁREA/evidence y el resumen en ÁREA/evidence/outcome.json.
Sale con 0 solo si el run queda COMMITTED. Biblioteca estándar; sin proveedores propios.
"""
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ORIGIN = 'http://127.0.0.1:8013'
LIMIT_SECONDS = 30 * 60 - 120  # 30 min por combinación, menos preflight y arranque

area, pair, keyfile = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
project = f'matrix-{pair}'
evidence = area / 'evidence'
evidence.mkdir(exist_ok=True)
deadline = time.monotonic() + LIMIT_SECONDS
cookie = None


def log(*items):
    print(time.strftime('%H:%M:%S'), *items, flush=True)


def call(method, path, body=None, key=None):
    global cookie
    headers = {'Host': '127.0.0.1:8013', 'Origin': ORIGIN, 'Content-Type': 'application/json'}
    if method != 'GET':
        headers['X-My-Harness'] = '1'
    if key:
        headers['Idempotency-Key'] = key
    if cookie:
        headers['Cookie'] = cookie
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(ORIGIN + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.headers.get('Set-Cookie'):
                cookie = response.headers['Set-Cookie'].split(';', 1)[0]
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b'null')


def save(name, value):
    (evidence / f'{name}.json').write_text(json.dumps(value, indent=1, ensure_ascii=False))


def wait(job):
    """Hasta que el job termina (`finished_at`) o pide recuperación; ACTIVE no es terminal."""
    while True:
        status, current = call('GET', f'/api/managed/jobs/{job["id"]}')
        if status != 200:
            log('job read failed', status, current)
            return job, False
        if current['finished_at'] is not None or current['status'] == 'RECOVERY_REQUIRED':
            return current, False
        if time.monotonic() > deadline:
            log('DEADLINE: 30 min exceeded with job', current['status'])
            return current, True
        time.sleep(5)


def pages(path, key):
    items, offset = [], 0
    while True:
        status, page = call('GET', f'{path}?{key}={offset}&limit=100')
        if status != 200:
            return items, status
        items += page['items']
        if key == 'after':
            offset = page['cursor']
            if not page['has_more']:
                return items, status
        else:
            if page['next_offset'] is None:
                return items, status
            offset = page['next_offset']


def snapshot(run_id):
    status, run = call('GET', f'/api/managed/runs/{run_id}')
    save('run', run)
    attempts, _ = pages(f'/api/managed/runs/{run_id}/attempts', 'offset')
    save('attempts', attempts)
    save('jobs', pages(f'/api/managed/runs/{run_id}/jobs', 'offset')[0])
    diffs = {}
    for cycle in (run.get('history') or {}).get('cycles', []) if status == 200 else []:
        text, offset = '', 0
        while offset is not None:
            page_status, page = call('GET', f'/api/managed/runs/{run_id}/cycles/{cycle["number"]}/diff'
                                            f'?offset={offset}&limit=524288&sha256={cycle["diff_sha256"]}')
            if page_status != 200:
                break
            text, offset = text + page['text'], page['next_offset']
        diffs[cycle['number']] = text
    save('diffs', diffs)
    events, _ = pages(f'/api/managed/runs/{run_id}/events', 'after')
    save('events', events)
    save('logs', {a['id']: call('GET', f'/api/managed/runs/{run_id}/attempts/{a["id"]}/logs')[1] for a in attempts})
    save('supervisor', call('GET', '/api/managed/supervisor')[1])
    return run, attempts, events


status, body = call('POST', '/api/session', {'key': keyfile.read_text()})
log('session', status)
if status != 200:
    sys.exit(2)
status, info = call('GET', f'/api/managed/projects/{project}')
save('project', info)
log('agents', json.dumps(info.get('agents') if isinstance(info, dict) else info))
status, phase = call('POST', f'/api/managed/projects/{project}/phases', {
    'code': 'P001', 'objective': 'Restaurar la estimación de treinta minutos por tarea',
    'exit_criteria': ['P001-T001 COMMITTED y alcanzable desde HEAD',
                      'npm run check, npm run test y npm run build pasan sobre HEAD',
                      'docs/STATE.md y docs/NEXT_STEPS.md sin cambios respecto a la base'],
    'tasks': ['P001-T001'], 'tag': f'{project}-p001'})
save('phase', phase)
log('phase', status)
if status != 201:
    sys.exit(2)
text = (area / 'web/docs/NEXT_STEPS.md').read_text()
status, job = call('POST', f'/api/managed/projects/{project}/runs',
                   {'task_id': 'P001-T001', 'phase_id': 'P001', 'text': text}, key=f'{project}-run')
log('run submitted', status, job.get('run_id') if isinstance(job, dict) else job)
if status != 202:
    sys.exit(2)
job, expired = wait(job)
save('job-run', job)
status, run = call('GET', f'/api/managed/runs/{job["run_id"]}')
log('run job', job['status'], job.get('diagnostic'), '| run', run['status'], run['stage'])
commit_job = None
if not expired and job['status'] == 'DONE' and run['status'] == 'ACCEPTANCE_READY':
    status, commit_job = call('POST', f'/api/managed/runs/{run["id"]}/actions',
                              {'action': 'commit', 'expected_version': run['version']}, key=f'{project}-commit')
    log('commit submitted', status)
    if status == 202:
        commit_job, expired = wait(commit_job)
        save('job-commit', commit_job)
        log('commit job', commit_job['status'], commit_job.get('diagnostic'))
else:
    log('Not ACCEPTANCE_READY: no commit; the pairing ends here')
run, attempts, events = snapshot(job['run_id'])
outcome = {'pair': pair, 'run_id': run['id'], 'run_status': run['status'], 'stage': run['stage'],
           'stop': run['history'].get('stop'), 'job': job['status'],
           'commit_job': commit_job and commit_job.get('status'), 'commit': (run.get('commit') or {}).get('commit'),
           'deadline_exceeded': expired, 'events': len(events),
           'attempts': [{'role': a['role'], 'status': a['status'], 'selection': a['selection']} for a in attempts]}
save('outcome', outcome)
log('outcome', json.dumps(outcome, ensure_ascii=False))
sys.exit(0 if run['status'] == 'COMMITTED' else 1)
