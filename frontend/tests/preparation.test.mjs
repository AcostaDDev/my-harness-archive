import { test } from 'node:test';
import assert from 'node:assert/strict';
import { isTypeScriptRecipe, pendingPreparationStep, preparationStatus, preparationStepLabel, recipeLabel, recipeModes } from '../src/preparation.ts';
import { translate } from '../src/i18n.ts';
import en from '../src/i18n/en.json' with { type: 'json' };
import es from '../src/i18n/es.json' with { type: 'json' };
import { createOnce } from '../src/managed-api.ts';

test('recovery starts at the first unaccredited step, including an uncertain spawn', () => {
  assert.equal(pendingPreparationStep([{number:0,status:'DONE'}, {number:1,status:'STARTED'}, {number:2,status:'PENDING'}]), 1);
  assert.equal(pendingPreparationStep([{number:0,status:'DONE'}]), 0); // reconcile commit if adoption was lost
  assert.equal(pendingPreparationStep([]), undefined);
  assert.equal(preparationStatus('RECOVERY_REQUIRED'), 'Requiere conciliación');
});

test('texts follow the frozen recipe: Django keeps its wording, TypeScript web names npm and the cache', () => {
  assert.equal(preparationStatus('ACTIVE', 'django-recipe-1'), 'Preparando Django');
  assert.equal(preparationStatus('COMPLETED', 'django-recipe-1'), 'Django preparado');
  assert.equal(preparationStatus('COMPLETED', 'typescript-web-recipe-1'), 'TypeScript web preparado');
  assert.equal(preparationStatus('COMPLETED'), 'Proyecto preparado');
  assert.equal(recipeLabel('typescript-web-recipe-1'), 'TypeScript web');
  assert.equal(recipeModes('django-recipe-1').offline, 'Offline: usar wheels locales y caché del hijo');
  assert.match(recipeModes('typescript-web-recipe-1').offline, /caché npm declarada por el operador/);
  assert.match(recipeModes('typescript-web-recipe-1').hint, /con red también se escribe/);
});

test('v2 recipes keep their texts and name their steps by stable id in the visual language', () => {
  assert.equal(preparationStatus('COMPLETED', 'django-recipe-2'), 'Django preparado');
  assert.equal(recipeLabel('typescript-web-recipe-2'), 'TypeScript web');
  assert.ok(isTypeScriptRecipe('typescript-web-recipe-2') && !isTypeScriptRecipe('django-recipe-2'));
  assert.deepEqual(recipeModes('typescript-web-recipe-2'), recipeModes('typescript-web-recipe-1'));
  const t = language => (key, params) => translate({ en, es }, language, key, params);
  const install = { kind: 'command', id: 'install', label: 'Install pinned wheels (no builds or transitive resolution)' };
  assert.equal(preparationStepLabel('django-recipe-2', install, t('es')), 'Instalar wheels fijados (sin builds ni resolución transitiva)');
  assert.equal(preparationStepLabel('django-recipe-2', install, t('en')), install.label);
  assert.equal(preparationStepLabel('typescript-web-recipe-2', { id: 'install' }, t('es')), 'Instalar dependencias fijadas del lock (sin scripts)');
  assert.equal(preparationStepLabel('typescript-web-recipe-2', { id: 'files' }, t('es')), 'Manifiesto empaquetado y entorno local de procesos');
  const validate = { id: 'validate-2', label: 'Validate: ruff check .', argv: ['/child/.venv/bin/ruff', 'check', '.'] };
  assert.equal(preparationStepLabel('django-recipe-2', validate, t('es')), 'Validar: ruff check .');
  assert.equal(preparationStepLabel('django-recipe-2', { id: 'commit' }, t('es')), 'Commit técnico y recibo de preparación');
  // v1 plans have no id: their frozen label is shown as confirmed; an unknown id falls back to its label.
  assert.equal(preparationStepLabel('django-recipe-1', { label: 'Crear entorno aislado' }, t('en')), 'Crear entorno aislado');
  assert.equal(preparationStepLabel('django-recipe-2', { id: 'future', label: 'Future step' }, t('es')), 'Future step');
});

test('lost preparation confirmation retains exact consent and key until acknowledged', async () => {
  const values = new Map();
  globalThis.sessionStorage = { getItem:k=>values.get(k)??null, setItem:(k,v)=>values.set(k,v), removeItem:k=>values.delete(k) };
  const calls=[];
  globalThis.fetch = async (path, options) => {
    calls.push({path,options});
    if(calls.length===1) throw new TypeError('Lost response');
    return Response.json({id:'same-preparation',status:'QUEUED'});
  };
  const body={change:{expected_version:1,mode:'offline'},preview_sha256:'confirmed-hash'};
  await assert.rejects(createOnce('/projects/demo/preparation/confirm',body));
  assert.equal((await createOnce('/projects/demo/preparation/confirm',body)).id,'same-preparation');
  assert.deepEqual(calls[0],calls[1]);
  assert.equal(calls[1].options.headers['X-Harness-Local'],'1');
});
