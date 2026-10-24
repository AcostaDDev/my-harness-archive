// P011-T024 browser QA: page audit run in the QA tab after each load. Returns a compact JSON summary.
// Raw catalog keys, leftover placeholders, horizontal overflow, unnamed controls and WCAG AA text contrast.
(() => {
  const visible = el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const rgba = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const [r, g, b, a = 1] = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [r, g, b, a]; };
  const lum = ([r, g, b]) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; };
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const blend = (top, under) => top[3] >= 1 ? top : [0, 1, 2].map(i => top[i] * top[3] + under[i] * (1 - top[3])).concat(1);
  const background = el => { const layers = [];
    for (let n = el; n; n = n.parentElement) { const c = rgba(getComputedStyle(n).backgroundColor); if (c && c[3] > 0) layers.push(c);
      if (c && c[3] >= 1) break; }
    let base = [255, 255, 255, 1]; if (!layers.length || layers[layers.length - 1][3] < 1) {
      const root = rgba(getComputedStyle(document.body).backgroundColor); if (root && root[3] >= 1) base = root; }
    return layers.reverse().reduce((under, top) => blend(top, under), base); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
  const short = el => (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''));
  const out = { url: location.pathname, lang: document.documentElement.lang, theme: document.documentElement.dataset.theme || 'system',
    width: innerWidth, title: document.title, rawKeys: [], placeholders: [], overflow: [], unnamed: [], contrast: [] };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let node; (node = walker.nextNode());) {
    const text = node.nodeValue.trim(); const el = node.parentElement;
    if (!text || !el || !visible(el) || el.closest('pre, code, .mono, svg, textarea')) continue;
    if (/^[a-z][a-z0-9_]*(\.[a-z0-9_]+){1,}$/.test(text) && !/\.(md|py|json|toml|ts|tsx|js|css|txt|sqlite3|lock)$/.test(text))
      out.rawKeys.push(text);
    if (/\{[a-z_]+\}|\{\{|undefined|NaN|\[object Object\]/.test(text)) out.placeholders.push(text.slice(0, 80));
    if (seen.has(el)) continue; seen.add(el);
    const s = getComputedStyle(el); const fg = rgba(s.color); if (!fg || el.closest('[disabled], [aria-disabled="true"]')) continue;
    const bg = background(el); const value = ratio(blend(fg, bg), bg);
    const size = parseFloat(s.fontSize); const large = size >= 24 || (size >= 18.66 && Number(s.fontWeight) >= 700);
    if (value < (large ? 3 : 4.5)) out.contrast.push(`${short(el)} ${value.toFixed(2)} "${text.slice(0, 30)}"`);
  }
  const doc = document.documentElement;
  out.scroll = [doc.scrollWidth, doc.clientWidth];
  if (doc.scrollWidth > doc.clientWidth + 1)
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect(); if (r.right > doc.clientWidth + 1 && visible(el) && !el.closest('pre, .scroll, table'))
        out.overflow.push(`${short(el)} ${Math.round(r.right)}`); if (out.overflow.length > 6) break; }
  for (const el of document.querySelectorAll('input, select, textarea, button, a[href], [role="button"]')) {
    if (!visible(el) || el.type === 'hidden') continue;
    const name = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.title || (el.labels && el.labels.length)
      || (['BUTTON', 'A'].includes(el.tagName) && el.textContent.trim()) || el.getAttribute('placeholder');
    if (!name) out.unnamed.push(short(el) + (el.name ? `[${el.name}]` : ''));
  }
  for (const k of ['rawKeys', 'placeholders', 'overflow', 'unnamed', 'contrast']) out[k] = [...new Set(out[k])].slice(0, 8);
  return JSON.stringify(out);
})()
