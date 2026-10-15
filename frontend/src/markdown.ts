// Markdown seguro del visor de documentación (H6.2 E3, D076). Módulo puro: sin DOM ni React, probado con node --test.
//
// - markdown-it con `html: false`: el HTML del documento se muestra como texto, nunca se interpreta.
// - Enlaces: solo rutas relativas al documento (o a la raíz del checkout con `/`) y `http(s)`. Las relativas a
//   Markdown pasan a la URL del visor; las externas se abren aparte sin `opener` ni `referrer`; el resto no navega.
// - Imágenes: solo del checkout, servidas por la API de la sesión. Una imagen externa nunca se carga.
// - Mermaid: el bloque solo deja su texto escapado; el diagrama se pinta después y aislado (mermaid-view.ts).
// - Bloques gestionados: se muestran aparte y sin sus marcadores; el editor no los toca.
import MarkdownIt from "markdown-it";
import type { MarkdownIt as Engine, RendererRule } from "markdown-it";

export const BLOCK_NAMES = ["state", "roadmap", "decisions"] as const;
export type Segment = { kind: "prose"; text: string } | { kind: "block"; name: string; text: string };

const marker = (name: string, edge: "start" | "end") => `<!-- harness-local:managed-${name}:${edge} -->`;
const ANY_MARKER = /<!--\s*harness-local:managed-/g;

/**
 * Prosa y bloques gestionados, con las reglas del servidor (marcadores en líneas propias, un par por nombre).
 * Unir los textos de los segmentos reproduce el documento byte a byte. Un marcador mal formado → `error`.
 */
export function splitBlocks(text: string): { segments: Segment[]; error?: string } {
  const spans: { name: string; start: number; stop: number }[] = [];
  for (const name of BLOCK_NAMES) {
    const begin = marker(name, "start"), end = marker(name, "end");
    const starts = text.split(begin).length - 1, ends = text.split(end).length - 1;
    if (!starts && !ends) continue;
    if (starts !== 1 || ends !== 1) return { segments: [{ kind: "prose", text }], error: `Marcadores del bloque «${name}» incompletos o repetidos` };
    const start = text.indexOf(begin), endAt = text.indexOf(end), stop = endAt + end.length;
    const ownLine = (start === 0 || text[start - 1] === "\n") && /^\r?\n/.test(text.slice(start + begin.length))
      && text[endAt - 1] === "\n" && (stop === text.length || /^\r?\n/.test(text.slice(stop)));
    if (endAt < start || !ownLine) return { segments: [{ kind: "prose", text }], error: `Los marcadores del bloque «${name}» deben ocupar líneas propias` };
    spans.push({ name, start, stop });
  }
  if ((text.match(ANY_MARKER) ?? []).length !== spans.length * 2) return { segments: [{ kind: "prose", text }], error: "Hay marcadores gestionados desconocidos" };
  spans.sort((a, b) => a.start - b.start);
  if (spans.some((span, i) => i > 0 && span.start < spans[i - 1].stop)) return { segments: [{ kind: "prose", text }], error: "Bloques gestionados solapados" };
  const segments: Segment[] = [];
  let cursor = 0;
  for (const span of spans) {
    segments.push({ kind: "prose", text: text.slice(cursor, span.start) });
    segments.push({ kind: "block", name: span.name, text: text.slice(span.start, span.stop) });
    cursor = span.stop;
  }
  segments.push({ kind: "prose", text: text.slice(cursor) });
  return { segments };
}

/** Contenido de un bloque sin sus líneas de marcador. */
export function blockBody(segment: Extract<Segment, { kind: "block" }>): string {
  return segment.text.slice(marker(segment.name, "start").length, -marker(segment.name, "end").length).replace(/^\r?\n/, "");
}

/** Ruta normalizada respecto al checkout, o undefined si sale de él. */
export function resolvePath(from: string, target: string): string | undefined {
  const base = target.startsWith("/") ? [] : from.split("/").slice(0, -1);
  const parts = [...base];
  for (const part of target.split("/")) {
    if (part === "" || part === ".") continue;
    if (part === "..") { if (!parts.length) return undefined; parts.pop(); }
    else parts.push(part);
  }
  return parts.length ? parts.join("/") : undefined;
}

export function slug(value: string): string {
  return value.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "seccion";
}

const IMAGE = /\.(png|jpe?g|gif|webp|avif|svg)$/i;
const SCHEME = /^[a-z][a-z0-9+.-]*:/i;

export type LinkTarget =
  | { kind: "external"; href: string }
  | { kind: "anchor"; href: string }
  | { kind: "document"; path: string; href: string }
  | { kind: "image"; path: string; src: string }
  | { kind: "blocked"; reason: string };

const e = encodeURIComponent;
export const docHref = (project: string, path: string) => `/projects/${e(project)}/docs/${path.split("/").map(e).join("/")}`;
export const imageSrc = (project: string, path: string) => `/api/managed/projects/${e(project)}/documents/image?path=${e(path)}`;

/** Destino admitido de un enlace o una imagen; nada fuera de esta tabla llega al HTML. */
export function classify(url: string, context: { project: string; path: string }, image = false): LinkTarget {
  const value = url.trim();
  if (!value) return { kind: "blocked", reason: "Enlace vacío" };
  if (value.startsWith("//")) return { kind: "blocked", reason: "Enlace sin esquema a otro servidor" };
  if (SCHEME.test(value)) {
    if (!/^https?:\/\//i.test(value)) return { kind: "blocked", reason: "Solo se admiten enlaces http(s) y rutas relativas" };
    return image ? { kind: "blocked", reason: "Las imágenes externas no se cargan" } : { kind: "external", href: value };
  }
  const hashAt = value.indexOf("#");
  const rawHash = hashAt >= 0 ? value.slice(hashAt + 1) : "";
  const rawPath = (hashAt >= 0 ? value.slice(0, hashAt) : value).split("?")[0];
  let decodedHash = rawHash;
  let decoded: string;
  try { decoded = decodeURIComponent(rawPath); decodedHash = decodeURIComponent(rawHash); }
  catch { return { kind: "blocked", reason: "Ruta mal codificada" }; }
  const anchor = rawHash ? `#doc-${slug(decodedHash)}` : "";
  if (!decoded) return image ? { kind: "blocked", reason: "Imagen sin ruta" } : rawHash ? { kind: "anchor", href: anchor } : { kind: "blocked", reason: "Enlace vacío" };
  if (decoded.includes("\\") || decoded.includes("\0")) return { kind: "blocked", reason: "Ruta no admitida" };
  let resolved = resolvePath(context.path, decoded);
  if (!resolved) return { kind: "blocked", reason: "La ruta sale del checkout" };
  if (image) return IMAGE.test(resolved) ? { kind: "image", path: resolved, src: imageSrc(context.project, resolved) } : { kind: "blocked", reason: "Formato de imagen no admitido" };
  if (decoded.endsWith("/")) resolved = `${resolved}/README.md`;
  if (!resolved.toLowerCase().endsWith(".md")) return { kind: "blocked", reason: "Solo se enlazan documentos Markdown del checkout" };
  return { kind: "document", path: resolved, href: docHref(context.project, resolved) + anchor };
}

type Env = { project: string; path: string; slugs: Map<string, number>; mermaid: string[] };
const reasonOf = (target: LinkTarget) => target.kind === "blocked" ? target.reason : "";

function engine(): Engine {
  const md = new MarkdownIt({ html: false, linkify: false, typographer: false });
  // Primer filtro: un destino fuera de la tabla no llega a ser enlace ni imagen (queda como texto).
  md.validateLink = (url: string) => { const v = url.trim(); return !v.startsWith("//") && (!SCHEME.test(v) || /^https?:/i.test(v)); };
  const fallback: RendererRule = (tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options);
  const fence = md.renderer.rules.fence ?? fallback;

  md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    const target = classify(String(token.attrGet("href") ?? ""), env as Env);
    token.attrs = (token.attrs ?? []).filter(([name]) => name === "title");
    if (target.kind === "external") {
      token.attrSet("href", target.href);
      token.attrSet("target", "_blank");
      token.attrSet("rel", "noopener noreferrer nofollow");
      token.attrSet("class", "doc-external");
    } else if (target.kind === "anchor") token.attrSet("href", target.href);
    else if (target.kind === "document") { token.attrSet("href", target.href); token.attrSet("data-internal", "true"); }
    else { token.attrSet("class", "doc-unlinked"); token.attrSet("title", reasonOf(target)); }
    return self.renderToken(tokens, idx, options);
  };

  md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    const alt = self.renderInlineAsText(token.children ?? [], options, env);
    const target = classify(String(token.attrGet("src") ?? ""), env as Env, true);
    if (target.kind !== "image") {
      const label = md.utils.escapeHtml(alt || "imagen"), reason = md.utils.escapeHtml(reasonOf(target));
      return `<span class="doc-image-blocked" title="${reason}">[${label}: ${reason}]</span>`;
    }
    const title = token.attrGet("title");
    return `<img src="${md.utils.escapeHtml(target.src)}" alt="${md.utils.escapeHtml(alt)}"${title ? ` title="${md.utils.escapeHtml(String(title))}"` : ""} loading="lazy">`;
  };

  md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
    const { slugs } = env as Env;
    const base = `doc-${slug(tokens[idx + 1]?.content ?? "")}`;
    const seen = slugs.get(base) ?? 0;
    slugs.set(base, seen + 1);
    tokens[idx].attrSet("id", seen ? `${base}-${seen}` : base);
    return self.renderToken(tokens, idx, options);
  };

  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    if (token.info.trim().split(/\s+/)[0].toLowerCase() !== "mermaid") return fence(tokens, idx, options, env, self);
    const { mermaid } = env as Env;
    mermaid.push(token.content);
    return `<figure class="doc-mermaid" data-mermaid="${mermaid.length - 1}"><pre class="doc-mermaid-source">${md.utils.escapeHtml(token.content)}</pre></figure>\n`;
  };
  return md;
}

const md = engine();
const LABELS: Record<string, string> = { state: "Estado de la fase", roadmap: "Fases del roadmap", decisions: "Índice de decisiones" };

/**
 * HTML del documento y fuentes Mermaid en orden. `path` es la ruta del documento en el checkout: los enlaces
 * relativos se resuelven desde su carpeta.
 */
export function renderMarkdown(source: string, context: { project: string; path: string }): { html: string; mermaid: string[]; error?: string } {
  const env: Env = { ...context, slugs: new Map(), mermaid: [] };
  const { segments, error } = splitBlocks(source);
  const html = segments.map(segment => segment.kind === "prose" ? md.render(segment.text, env)
    : `<section class="doc-managed" data-block="${segment.name}"><p class="doc-managed-label">Bloque gestionado · ${md.utils.escapeHtml(LABELS[segment.name] ?? segment.name)} · lo regenera el harness</p>\n${blockBody(segment).trim() ? md.render(blockBody(segment), env) : '<p class="doc-managed-empty">Vacío: se rellena en el próximo commit del harness.</p>\n'}</section>\n`).join("");
  return { html, mermaid: env.mermaid, ...(error ? { error } : {}) };
}
