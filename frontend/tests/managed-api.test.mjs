import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { managed, managedApi, ManagedError, jobRequest, savePending, readPending } from '../src/managed-api.ts';
const values = new Map();
globalThis.sessionStorage = { getItem: k => values.get(k) ?? null, setItem: (k,v) => values.set(k,v), removeItem: k => values.delete(k) };
beforeEach(() => values.clear());

test('double send after an immediate acknowledgement reuses key; changed version gets another', () => {
  const first = jobRequest('/runs/r/actions', {action:'commit',expected_version:17});
  savePending(first);
  savePending(); // response acknowledged
  const second = jobRequest('/runs/r/actions', {action:'commit',expected_version:17});
  assert.deepEqual(first, second);
  assert.notEqual(jobRequest('/runs/r/actions', {action:'commit',expected_version:18}).key, first.key);
});

test('network failure preserves exact pending envelope across reload and explicit retry', async () => {
  const pending = jobRequest('/projects/demo/runs', {task_id:'T',phase_id:'P',text:'synthetic'});
  savePending(pending);
  const calls = [];
  globalThis.fetch = async (path, options) => {
    calls.push({path,options});
    if (calls.length === 1) throw new TypeError('Failed to fetch');
    return Response.json({id:1});
  };
  await assert.rejects(managed(pending.path,pending.body,pending.key));
  const restored = readPending();
  assert.deepEqual(restored,pending);
  assert.deepEqual(await managed(restored.path,restored.body,restored.key),{id:1});
  assert.deepEqual(calls[0], calls[1]);
  assert.equal(calls[0].options.headers['X-Harness-Local'],'1');
  assert.equal(calls[0].options.headers['Idempotency-Key'],pending.key);
});

test('conflicts preserve code and diagnostic; all managed mutations carry CSRF header', async () => {
  globalThis.fetch = async (path, options) => {
    assert.equal(options.headers['X-Harness-Local'],'1');
    assert.equal(JSON.parse(options.body).expected_version,8);
    return Response.json({detail:{code:'conflict',diagnostic:'Version changed'}},{status:409});
  };
  await assert.rejects(managedApi.confirm(1,{expected_version:8,owner_token:'token',reason:'stopped'}),
    e => e instanceof ManagedError && e.status === 409 && e.message.includes('conflict: Version changed'));
});

test('H0/H1 mutations carry the local CSRF header; reads do not need it', async () => {
  const { api } = await import('../src/api.ts');
  const calls = [];
  globalThis.fetch = async (path, options) => { calls.push({path, options}); return Response.json({}); };
  await api.list();
  await api.create({title: 'synthetic'});
  await api.setObservation('/api/legacy/projects/p', true);
  assert.equal(calls[0].options, undefined);
  assert.equal(calls[1].options.method, 'POST');
  assert.equal(calls[1].options.headers['X-Harness-Local'], '1');
  assert.equal(calls[1].options.headers['Content-Type'], 'application/json');
  assert.equal(calls[2].path, '/api/legacy/projects/p/observation');
  assert.equal(calls[2].options.method, 'PUT');
  assert.equal(calls[2].options.headers['X-Harness-Local'], '1');
  assert.deepEqual(JSON.parse(calls[2].options.body), {enabled: true});
});

test('401 notifies the session gate once and never retries a mutation or changes its envelope', async () => {
  const events = [];
  globalThis.window = {dispatchEvent: event => events.push(event.type)};
  const pending = jobRequest('/projects/demo/runs', {task_id:'T',phase_id:'P',text:'synthetic'});
  savePending(pending);
  let calls = 0;
  globalThis.fetch = async () => { calls++; return Response.json({detail:{code:'session_required',diagnostic:'Expired'}}, {status:401}); };
  try {
    await assert.rejects(managed(pending.path, pending.body, pending.key), e => e instanceof ManagedError && e.status === 401);
    assert.equal(calls, 1);
    assert.deepEqual(readPending(), pending);
    assert.deepEqual(events, ['harness-session-required']);
    const {api} = await import('../src/api.ts');
    await assert.rejects(api.create({title:'synthetic'}));
    assert.equal(calls, 2);
    assert.equal(events.length, 2);
  } finally { delete globalThis.window; }
});

test('lost acknowledgement then expired session keeps one identity until explicit authenticated resend', async () => {
  const pending = jobRequest('/runs/r/actions', {action:'commit', expected_version:17});
  savePending(pending);
  const calls = [];
  const jobs = new Map();
  let authenticated = true;
  globalThis.fetch = async (path, options) => {
    calls.push({path, options});
    if (!authenticated) return Response.json({detail:{code:'session_required'}}, {status:401});
    const key = options.headers['Idempotency-Key'];
    if (!jobs.has(key)) {
      jobs.set(key, {id:42}); // server admitted the action; its response was lost
      throw new TypeError('Lost acknowledgement');
    }
    return Response.json(jobs.get(key));
  };
  await assert.rejects(managed(pending.path, pending.body, pending.key));
  authenticated = false;
  const restored = readPending();
  await assert.rejects(managed(restored.path, restored.body, restored.key), e => e.status === 401);
  authenticated = true; // logging in does not call managed or discard pending state
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls.length, 2);
  assert.deepEqual(readPending(), pending);
  assert.deepEqual(await managed(restored.path, restored.body, restored.key), {id:42});
  savePending(); // explicit resend acknowledged
  assert.equal(readPending(), undefined);
  assert.equal(jobs.size, 1);
  assert.deepEqual(calls[0], calls[1]);
  assert.deepEqual(calls[1], calls[2]);
});
