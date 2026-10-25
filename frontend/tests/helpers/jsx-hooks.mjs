import * as runtime from 'react/jsx-runtime';
export const Fragment = runtime.Fragment;
function record(method, type, props, key) {
  if (typeof type === 'string') globalThis.__tsxHookHarness.elements.push({ type, props });
  return runtime[method](type, props, key);
}
export const jsx = (type, props, key) => record('jsx', type, props, key);
export const jsxs = (type, props, key) => record('jsxs', type, props, key);
