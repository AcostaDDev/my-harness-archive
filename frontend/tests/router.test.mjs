import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parse, href, trail, runRoute, projectOf } from '../src/router.ts';

const valid = [
  ['/', { name: 'home' }],
  ['/legacy', { name: 'legacy' }],
  ['/projects/new', { name: 'project-new' }],
  ['/projects/mi-web', { name: 'project', project: 'mi-web' }],
  ['/projects/mi-web/phases', { name: 'phases', project: 'mi-web' }],
  ['/projects/mi-web/phases/P001', { name: 'phase', project: 'mi-web', phase: 'P001' }],
  ['/projects/mi-web/phases/P001/tasks/P001-T003', { name: 'task', project: 'mi-web', phase: 'P001', task: 'P001-T003' }],
  ['/projects/mi-web/phases/P001/tasks/P001-T003/runs/0f1e', { name: 'run', project: 'mi-web', phase: 'P001', task: 'P001-T003', run: '0f1e' }],
  ['/projects/mi-web/chat', { name: 'chat', project: 'mi-web' }],
  ['/projects/mi-web/chat/c-1', { name: 'chat', project: 'mi-web', conversation: 'c-1' }],
  ['/projects/mi-web/settings', { name: 'settings', project: 'mi-web' }],
  ['/runs/abc', { name: 'run-short', run: 'abc' }],
];

test('every route of D072 §7 parses and round-trips through href', () => {
  for (const [path, route] of valid) {
    assert.deepEqual(parse(path), route, path);
    assert.equal(href(route), path);
  }
});

test('trailing and repeated slashes do not change the route', () => {
  assert.deepEqual(parse('/projects/mi-web/phases/'), { name: 'phases', project: 'mi-web' });
  assert.deepEqual(parse('//projects//mi-web'), { name: 'project', project: 'mi-web' });
});

test('codes with spaces, dots or unicode are encoded and decoded exactly', () => {
  const route = { name: 'task', project: 'proyecto ñ', phase: 'v1.2', task: 'P#1?x' };
  const path = href(route);
  assert.ok(!path.includes(' ') && !path.includes('#') && !path.includes('?'));
  assert.deepEqual(parse(path), route);
});

test('unknown, malformed or ambiguous paths are not found instead of guessed', () => {
  for (const path of ['/projects', '/projects/a/unknown', '/projects/a/phases/P1/tasks', '/projects/a/phases/P1/x/T',
    '/projects/a/phases/P1/tasks/T/runs', '/projects/a/chat/c/extra', '/legacy/x', '/runs', '/simulations',
    '/projects/%E0%A4%A', '/projects/a%2Fb', '/projects/a/phases/P1%2F..%2F..']) {
    assert.equal(parse(path).name, 'not-found', path);
  }
  assert.equal(href(parse('/nada/aqui')), '/nada/aqui');
});

test('trail links each level to its own page and ends at the current one', () => {
  const route = parse('/projects/mi-web/phases/P001/tasks/P001-T003/runs/0123456789');
  const items = trail(route);
  assert.deepEqual(items.map(i => i.label), ['Proyectos', 'mi-web', 'Fases', 'P001', 'P001-T003', 'Run 01234567']);
  assert.deepEqual(items.map(i => href(i.to)), ['/', '/projects/mi-web', '/projects/mi-web/phases',
    '/projects/mi-web/phases/P001', '/projects/mi-web/phases/P001/tasks/P001-T003', href(route)]);
  assert.deepEqual(trail(parse('/')).map(i => i.label), ['Proyectos']);
});

test('run reads map to their canonical URL; runs outside a registered project have none', () => {
  assert.equal(href(runRoute({ id: 'r', project_id: 'p', phase_id: 'P001', task_id: 'P001-T001' })),
    '/projects/p/phases/P001/tasks/P001-T001/runs/r');
  assert.equal(runRoute({ id: 'r', project_id: null, phase_id: 'P001', task_id: 'T' }), undefined);
  assert.equal(projectOf(parse('/projects/p/settings')), 'p');
  assert.equal(projectOf(parse('/legacy')), undefined);
});

test('the registration page is not a project and keeps its own trail', () => {
  assert.equal(projectOf(parse('/projects/new')), undefined);
  assert.deepEqual(trail({ name: 'project-new' }).map(item => item.label), ['Proyectos', 'Registrar proyecto']);
  assert.deepEqual(parse('/projects/new/settings'), { name: 'settings', project: 'new' });
});
