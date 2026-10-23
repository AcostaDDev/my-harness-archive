// P011-T013: parses every ```mermaid fence of the given Markdown files with the local Mermaid parser.
// Usage from the repository root: node docs/phase/P011-T013_mermaid_check.mjs frontend docs/flows/*.md docs/DDBB-DIAGRAM.md
// DOMPurify needs a DOM, so it is replaced by an inert stub: syntax only, no label sanitization or rendering.
import { register } from 'node:module';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const stub = 'data:text/javascript,' + encodeURIComponent(
  'const p={addHook(){},removeHook(){},removeAllHooks(){},sanitize:(s)=>s,isSupported:true};export default p;');
register('data:text/javascript,' + encodeURIComponent(
  `export async function resolve(s,c,n){if(s==='dompurify')return{url:${JSON.stringify(stub)},shortCircuit:true};return n(s,c);}`));

const [frontend, ...files] = process.argv.slice(2);
const require = createRequire(pathToFileURL(frontend + '/package.json'));
const mermaid = (await import(pathToFileURL(require.resolve('mermaid')).href)).default;
let failures = 0;
const counts = {};
for (const file of files) {
  const text = readFileSync(file, 'utf8');
  const fences = [...text.matchAll(/^```mermaid\n([\s\S]*?)^```/gm)];
  for (const [index, match] of fences.entries()) {
    try {
      const result = await mermaid.parse(match[1]);
      counts[result.diagramType] = (counts[result.diagramType] ?? 0) + 1;
    } catch (error) {
      failures += 1;
      console.log(`FAIL ${file}#${index + 1}: ${String(error.message).split('\n').slice(0, 3).join(' | ')}`);
    }
  }
}
console.log(JSON.stringify({ files: files.length, counts, failures }));
process.exit(failures ? 1 : 0);
