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
