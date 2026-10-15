// Diagramas Mermaid del visor (H6.2 E3, D076): carga diferida, `securityLevel: "strict"` y resultado aislado.
// El SVG generado se muestra como <img> desde un Blob: en una imagen no se ejecutan scripts ni se cargan recursos
// externos, así que ni una directiva `%%{init}%%` ni una etiqueta con HTML pueden actuar sobre la página.

export const MERMAID_CONFIG = {
  startOnLoad: false,
  securityLevel: "strict",
  // Etiquetas SVG de texto: sin foreignObject ni HTML dentro del diagrama.
  htmlLabels: false,
  flowchart: { htmlLabels: false },
  suppressErrorRendering: true,
  maxTextSize: 50_000,
  fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
  // Claves que una directiva del documento no puede cambiar (las de Mermaid y las etiquetas HTML).
  secure: ["secure", "securityLevel", "startOnLoad", "maxTextSize", "suppressErrorRendering", "maxEdges", "htmlLabels", "flowchart", "fontFamily"],
} as const;

type Mermaid = typeof import("mermaid")["default"];
let loader: Promise<Mermaid> | undefined;
let counter = 0;
// Mermaid comparte estado global: un diagrama cada vez.
let queue: Promise<unknown> = Promise.resolve();

export function prefersDark(): boolean {
  const theme = document.documentElement.getAttribute("data-theme");
  if (theme) return theme === "dark";
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
}

/** URL `blob:` de una imagen SVG del diagrama; el llamante la revoca al dejar de mostrarla. */
export function renderDiagram(source: string, dark: boolean): Promise<string> {
  const job = queue.then(async () => {
    const mermaid = await (loader ??= import("mermaid").then(module => module.default));
    mermaid.initialize({ ...MERMAID_CONFIG, theme: dark ? "dark" : "neutral", secure: [...MERMAID_CONFIG.secure] });
    const { svg } = await mermaid.render(`doc-mermaid-${++counter}`, source);
    // Tamaño intrínseco desde el viewBox: como imagen, un ancho del 100 % no fija el tamaño.
    const parsed = new DOMParser().parseFromString(svg, "image/svg+xml");
    const root = parsed.documentElement;
    if (root.nodeName !== "svg") throw new Error("Mermaid no devolvió un SVG");
    const box = (root.getAttribute("viewBox") ?? "").split(/[\s,]+/).map(Number);
    if (box.length === 4 && box.every(Number.isFinite)) {
      root.setAttribute("width", String(Math.ceil(box[2])));
      root.setAttribute("height", String(Math.ceil(box[3])));
      root.removeAttribute("style");
    }
    const text = new XMLSerializer().serializeToString(root);
    return URL.createObjectURL(new Blob([text], { type: "image/svg+xml" }));
  });
  queue = job.catch(() => undefined);
  return job;
}
