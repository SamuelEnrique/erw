"use client";
// Energy Research Warehouse (ERW) site: the one chart library (session 22, Task 1). ECharts, loaded
// once from cdnjs, so every chart has the same hover values with units, zoom and pan, legend toggles,
// a range slider on time series and a download-as-PNG control. Colors are the design tokens
// (app/tokens.css), read from CSS variables when a chart draws.
import { useEffect, useRef } from "react";

export const ECHARTS_SRC = "https://cdnjs.cloudflare.com/ajax/libs/echarts/5.6.0/echarts.min.js";
// Session 177 (docs/reviews/2026-10-10-security.md, M5): the browser runs the file only if its bytes have this SHA-384,
// so a file changed at the host is refused. Taken from the file as a page of this site received it on 10 October 2026
// (1,034,102 bytes; runs/session177/sri_echarts.out). A new version of the library needs a new hash here, or no chart
// draws: site/scripts/check-csp.mjs proves a chart still draws.
export const ECHARTS_SRI = "sha384-pPi0zxBAoDu6+JXW/C68UZLvBUUtU+7zonhif43rqj7pxsGyqyqzcian2Rj37Rss";

// A minimal view of the ECharts API the site uses (the library arrives as a global from the CDN).
export type ECInstance = {
  setOption: (o: unknown, notMerge?: boolean) => void;
  resize: () => void;
  dispose: () => void;
  on: (ev: string, cb: (p: Record<string, unknown>) => void) => void;
  off: (ev: string) => void;
  dispatchAction: (a: Record<string, unknown>) => void;
};
export type ECLib = { init: (el: HTMLElement, theme?: unknown, opts?: Record<string, unknown>) => ECInstance; registerMap: (name: string, geo: unknown) => void };

let loading: Promise<ECLib> | null = null;

export function loadECharts(): Promise<ECLib> {
  const w = window as unknown as { echarts?: ECLib };
  if (w.echarts) return Promise.resolve(w.echarts);
  if (!loading) {
    loading = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = ECHARTS_SRC;
      s.integrity = ECHARTS_SRI;
      s.crossOrigin = "anonymous";  // the integrity check needs the host's permission to read the file, which cdnjs gives
      s.async = true;
      s.onload = () => (w.echarts ? resolve(w.echarts) : reject(new Error("ECharts did not load")));
      s.onerror = () => {
        loading = null;
        reject(new Error(`could not load ${ECHARTS_SRC}`));
      };
      document.head.appendChild(s);
    });
  }
  return loading;
}

/** A design token's value: token("accent") reads --color-accent; a full "var(--x)" or "--x" is read too.
 * Session 236: `from` is the element the token is read at (a chart's own box), so that a chart inside the brand's
 * wrapper (components/Brand.tsx) takes the brand's tokens, which are scoped to it; without it, the page's root. */
export function token(name: string, from?: Element | null): string {
  const v = name.startsWith("var(") ? name.slice(4, -1) : name.startsWith("--") ? name : `--color-${name}`;
  return getComputedStyle(from ?? document.documentElement).getPropertyValue(v).trim() || "#6B665E";
}

/** Axis, grid and text styles from the tokens, shared by every chart. Session 236: with `from` (the chart's box), the
 * tokens and the text face are the ones in force there. */
export function baseStyle(from?: Element | null) {
  const muted = token("muted", from), rule = token("rule", from), ink = token("ink", from), panel = token("panel", from);
  return {
    textStyle: { fontFamily: from ? getComputedStyle(from).fontFamily : "system-ui, sans-serif", color: ink },
    axis: {
      axisLine: { lineStyle: { color: rule } },
      axisTick: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 },
      splitLine: { lineStyle: { color: rule } },
      nameTextStyle: { color: muted, fontSize: 11 },
    },
    tooltip: { backgroundColor: panel, borderColor: rule, textStyle: { color: ink, fontSize: 12 }, confine: true },
    toolbox: (name: string) => ({
      right: 4,
      top: 0,
      itemSize: 13,
      iconStyle: { borderColor: muted },
      feature: { saveAsImage: { title: "PNG", name, backgroundColor: panel, pixelRatio: 2 } },
    }),
  };
}

// Session 238 (the brand rule: a chart takes its colors from the tokens). The finding cards' charts and the weekly
// templates' options were written with color literals (lib/findingchart.ts, lib/chartforms.ts, lib/discoverychart.ts,
// components/analysis/MultiChart.tsx; warehouse/analysis/style.py), and the renderer's photographs and three tests hold
// those in place. Inside an element marked data-chart-tokens a chart is therefore drawn through this: each literal of
// the old palettes is replaced by the value of a token of app/tokens.css, read from the element when the chart draws,
// and the font by the element's own. The brand has five series colors (docs/brand.md, section 2); a sixth series falls
// to the fifth's, and is told by its name in the legend and the hover card. Outside such an element nothing changes.
// Session 267: a chart warehouse/analysis/style.py draws with more than five series is written in the eight colors of
// "Many series" (--chart-series-1 to -8), and each is read here from its token.
export const LITERAL_TOKENS: Record<string, string> = {   // session 318: lib/svgoption.ts reads the same map
  "#1a1a1a": "--chart-ink", "#2e2d29": "--chart-ink", "#6b6b6b": "--color-muted", "#6b665e": "--color-muted", "#e5e5e5": "--color-rule", "#d9d2c3": "--color-rule",
  "#fbf8f2": "--color-panel",
  "#1f5f8b": "--chart-ink", "#c4541c": "--color-accent", "#2e7d4f": "--chart-blue", "#8a6d3b": "--chart-grey", "#6a4c93": "--chart-light", "#9a9a9a": "--chart-light",
  "#8c1515": "--color-accent", "#007c92": "--chart-ink", "#e98300": "--chart-blue", "#175e54": "--chart-grey", "#620059": "--chart-light",
  // session 267: the old palette's sixth to tenth series take the first five of the eight a chart of many series has
  "#6fa287": "--chart-series-1", "#4298b5": "--chart-series-2", "#b6b1a9": "--chart-series-3", "#8f993e": "--chart-series-4", "#651c32": "--chart-series-5",
  // session 267: warehouse/analysis/style.py now writes the brand's own values (docs/brand.md, section 2); each is read
  // here from the token that holds it, the eight of "Many series" (session 268) among them
  "#6b675f": "--color-muted", "#e3ded1": "--color-rule", "#f7f3ea": "--color-paper", "#3c6e9e": "--chart-blue", "#8f8a80": "--chart-light",
  "#4477aa": "--chart-series-1", "#66ccee": "--chart-series-2", "#228833": "--chart-series-3", "#ccbb44": "--chart-series-4",
  "#ee6677": "--chart-series-5", "#aa3377": "--chart-series-6", "#bbbbbb": "--chart-series-7", "#eeaa44": "--chart-series-8",
};
function inTokens(chart: ECInstance, scope: HTMLElement): ECInstance {
  const cs = getComputedStyle(scope);
  const swap = (v: unknown, key?: string): unknown => {
    if (typeof v === "string") {
      if (key === "fontFamily") return cs.fontFamily || v;
      const t = LITERAL_TOKENS[v.toLowerCase()];
      return t ? cs.getPropertyValue(t).trim() || v : v;
    }
    if (Array.isArray(v)) return v.map((x) => swap(x, key));
    if (v && typeof v === "object" && Object.getPrototypeOf(v) === Object.prototype) return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, swap(x, k)]));
    return v;
  };
  return {
    setOption: (o, notMerge) => chart.setOption(swap(o), notMerge), resize: () => chart.resize(), dispose: () => chart.dispose(),
    on: (ev, cb) => chart.on(ev, cb), off: (ev) => chart.off(ev), dispatchAction: (a) => chart.dispatchAction(a),
  };
}

/** Mount a chart: build(lib, el) returns the option (and may register handlers); redrawn when deps change. */
export function useEChart(build: (chart: ECInstance, lib: ECLib) => void, deps: unknown[]) {
  const box = useRef<HTMLDivElement>(null);
  const chart = useRef<ECInstance | null>(null);
  useEffect(() => {
    let alive = true;
    let ro: ResizeObserver | null = null;
    loadECharts()
      .then((lib) => {
        if (!alive || !box.current) return;
        if (!chart.current) chart.current = lib.init(box.current, undefined, { renderer: "canvas" });
        const scope = box.current.closest<HTMLElement>("[data-chart-tokens]");   // session 238: the tokens, where a page asks for them
        build(scope ? inTokens(chart.current, scope) : chart.current, lib);
        ro = new ResizeObserver(() => chart.current?.resize());
        ro.observe(box.current);
      })
      .catch((e) => {
        if (box.current) box.current.textContent = `The chart could not load: ${(e as Error).message}. The table below holds the same data.`;
      });
    return () => {
      alive = false;
      ro?.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => () => chart.current?.dispose(), []);
  return box;
}

/** A number as the site writes it: thousands commas, at most two decimals. */
export const num = (v: number) => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { maximumFractionDigits: 2 }));
