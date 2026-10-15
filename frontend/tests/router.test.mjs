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
  ['/projects/mi-web/docs', { name: 'docs', project: 'mi-web' }],
  ['/projects/mi-web/docs/README.md', { name: 'docs', project: 'mi-web', path: 'README.md' }],
  ['/projects/mi-web/docs/docs/decisions/D001-usar-git.md', { name: 'docs', project: 'mi-web', path: 'docs/decisions/D001-usar-git.md' }],
  ['/projects/mi-web/setup', { name: 'setup', project: 'mi-web' }],
  ['/projects/mi-web/setup/docs/ROADMAP.md', { name: 'setup', project: 'mi-web', path: 'docs/ROADMAP.md' }],
  ['/projects/mi-web/phases/P001/plan', { name: 'plan', project: 'mi-web', phase: 'P001' }],
  ['/projects/mi-web/phases/P001/plan/c-9', { name: 'plan', project: 'mi-web', phase: 'P001', conversation: 'c-9' }],
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

test('document paths keep each segment exact and never climb out of the checkout', () => {
  const route = { name: 'docs', project: 'mi web', path: 'docs/notas de diseño/a#b?.md' };
  const path = href(route);
  assert.equal(path, '/projects/mi%20web/docs/docs/notas%20de%20dise%C3%B1o/a%23b%3F.md');
  assert.deepEqual(parse(path), route);
  for (const bad of ['/projects/a/docs/%2E%2E/x.md', '/projects/a/docs/docs/./x.md', '/projects/a/docs/a%2Fb.md']) {
    assert.equal(parse(bad).name, 'not-found', bad);
  }
  assert.deepEqual(trail(parse('/projects/p/docs/docs/STATE.md')).map(i => [i.label, href(i.to)]), [
    ['Proyectos', '/'], ['p', '/projects/p'], ['Documentación', '/projects/p/docs'], ['STATE.md', '/projects/p/docs/docs/STATE.md']]);
  assert.equal(projectOf(parse('/projects/p/docs')), 'p');
});

test('creation and phase planning routes (H6.2 E4) keep their trail and refuse ambiguous paths', () => {
  assert.deepEqual(trail(parse('/projects/p/setup/docs/decisions/D001-x.md')).map(i => [i.label, href(i.to)]), [
    ['Proyectos', '/'], ['p', '/projects/p'], ['Creación', '/projects/p/setup'], ['D001-x.md', '/projects/p/setup/docs/decisions/D001-x.md']]);
  assert.deepEqual(trail(parse('/projects/p/phases/P001/plan/c-1')).map(i => [i.label, href(i.to)]), [
    ['Proyectos', '/'], ['p', '/projects/p'], ['Fases', '/projects/p/phases'], ['P001', '/projects/p/phases/P001'],
    ['Planificación', '/projects/p/phases/P001/plan'], ['Conversación', '/projects/p/phases/P001/plan/c-1']]);
  for (const bad of ['/projects/a/setup/../x.md', '/projects/a/setup/docs/%2E%2E/x.md', '/projects/a/setup/a%2Fb.md',
    '/projects/a/phases/P1/plan/c/extra', '/projects/a/phases/P1/plan/c%2Fd']) {
    assert.equal(parse(bad).name, 'not-found', bad);
  }
  assert.equal(projectOf(parse('/projects/p/setup')), 'p');
});
