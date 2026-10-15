import { test } from 'node:test';
import assert from 'node:assert/strict';
import { unifiedDiff } from '../src/diff.ts';

/** Aplica un diff unificado a `before`; prueba que el diff describe exactamente el cambio. */
function apply(before, diff) {
  const source = before ? before.split('\n') : [];
  if (source[source.length - 1] === '') source.pop();
  const out = [];
  let cursor = 0;
  for (const line of diff.split('\n').slice(2)) {
    const hunk = /^@@ -(\d+),(\d+) \+\d+,\d+ @@$/.exec(line);
    if (hunk) {
      const start = Number(hunk[2]) ? Number(hunk[1]) - 1 : Number(hunk[1]);
      while (cursor < start) out.push(source[cursor++]);
    } else if (line.startsWith(' ')) { assert.equal(source[cursor], line.slice(1)); out.push(source[cursor++]); }
    else if (line.startsWith('-')) { assert.equal(source[cursor], line.slice(1)); cursor++; }
    else if (line.startsWith('+')) out.push(line.slice(1));
  }
  while (cursor < source.length) out.push(source[cursor++]);
  return out;
}

const lines = text => { const parts = text.split('\n'); if (parts[parts.length - 1] === '') parts.pop(); return parts; };

test('identical texts have no diff; new and deleted files are explicit', () => {
  assert.equal(unifiedDiff('a.md', 'x\n', 'x\n'), '');
  assert.equal(unifiedDiff('a.md', null, '# A\nb\n'), '--- /dev/null\n+++ b/a.md\n@@ -0,0 +1,2 @@\n+# A\n+b\n');
  assert.equal(unifiedDiff('a.md', '# A\n', null), '--- a/a.md\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-# A\n');
});

test('hunks keep three lines of context and merge when close', () => {
  const before = Array.from({ length: 30 }, (_, i) => `línea ${i + 1}`).join('\n') + '\n';
  const after = before.replace('línea 5\n', 'cinco\n').replace('línea 9\n', 'nueve\n').replace('línea 25\n', '');
  const diff = unifiedDiff('docs/STATE.md', before, after);
  const hunks = diff.split('\n').filter(l => l.startsWith('@@'));
  assert.deepEqual(hunks, ['@@ -2,11 +2,11 @@', '@@ -22,7 +22,6 @@']);
  assert.deepEqual(apply(before, diff), lines(after));
});

test('a change of the final newline is shown, never hidden', () => {
  const diff = unifiedDiff('a.md', 'a\nb\n', 'a\nb');
  assert.match(diff, /\\ Cambia el salto de línea final/);
  assert.match(unifiedDiff('a.md', 'x\na\nb\n', 'y\na\nb'), /^-x$[\s\S]*Cambia el salto/m);
});

test('random edits round-trip through the diff', () => {
  let seed = 7;
  const random = n => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed % n; };
  for (let round = 0; round < 200; round++) {
    const base = Array.from({ length: random(25) }, () => `l${random(6)}`);
    const edited = [...base];
    for (let k = random(6); k > 0; k--) {
      const at = random(edited.length + 1);
      if (random(2) && edited.length) edited.splice(Math.min(at, edited.length - 1), 1);
      else edited.splice(at, 0, `n${random(4)}`);
    }
    const before = base.length ? base.join('\n') + '\n' : '', after = edited.length ? edited.join('\n') + '\n' : '';
    const diff = unifiedDiff('x.md', before, after);
    if (before === after) { assert.equal(diff, ''); continue; }
    assert.deepEqual(apply(before, diff), lines(after), JSON.stringify({ base, edited }));
  }
});

test('documents too large to compare return null instead of an approximation', () => {
  const before = Array.from({ length: 2500 }, (_, i) => `a${i}`).join('\n');
  const after = Array.from({ length: 2500 }, (_, i) => `b${i}`).join('\n');
  assert.equal(unifiedDiff('big.md', before, after), null);
});
