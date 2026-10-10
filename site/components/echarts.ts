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

/** A design token's value: token("accent") reads --color-accent; a full "var(--x)" or "--x" is read too. */
export function token(name: string): string {
  const v = name.startsWith("var(") ? name.slice(4, -1) : name.startsWith("--") ? name : `--color-${name}`;
  return getComputedStyle(document.documentElement).getPropertyValue(v).trim() || "#6B665E";
}

/** Axis, grid and text styles from the tokens, shared by every chart. */
export function baseStyle() {
  const muted = token("muted"), rule = token("rule"), ink = token("ink"), panel = token("panel");
  return {
    textStyle: { fontFamily: "system-ui, sans-serif", color: ink },
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
        build(chart.current, lib);
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
