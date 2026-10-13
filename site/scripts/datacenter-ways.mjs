// Energy Research Warehouse (ERW) site, session 194: what /cost-of-power hands its scenarios, computed a second time
// from the page's own files with lib/datacenter.ts, for scripts/test-datacenter-finance.mjs and
// scripts/check-datacenter-scenarios.mjs. It repeats, outside the page, the steps of LoadView in
// app/cost-of-power/page.tsx: the load under "Your load", the same months run flat, and, for a flat load, the load
// off in the form's default number of hours a year. No server, no network.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as L from "../lib/datacenter.ts";
import { FLAT, FLEX } from "../lib/datacenter/finance.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(here, "..", "data", "datacenter");
export const INDEX = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf-8"));
const cache = new Map();
export function yearFiles(grid) {
  if (!cache.has(grid)) cache.set(grid, INDEX.grids[grid].years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${grid}_${y}.json`), "utf-8"))));
  return cache.get(grid);
}
const FLAT_LOAD = { run: "flat", n: 0, pct: 0, shift: 0 };
export const ALT = { run: "hours", n: L.DEFAULTS.n, pct: 0, shift: 0 };
export const flatMonths = (ms) => ms.map((r) => ({ ...r, cost: r.flat, energy: r.held, down: 0, tightDown: 0 }));
export function wayOf(ms) {
  const l = L.lastTwelve(ms);
  if (!l) return null;
  const s = L.span(l), w = L.last36(ms), b = L.badMonth(w?.months ?? []);
  if (s.per === null) return null;
  return { per: s.per, cost: s.cost, energy: s.energy, held: s.held, flatCost: s.flatCost, down: s.down, bad: b ? { m: b.m, per: b.cost / b.energy, cost: b.cost } : null, of: w?.months.length ?? 0 };
}
/** The page for an address (its query as an object): the inputs in force, the months of the load, its last twelve
 * months, its bad month, and the two ways of running the scenarios compare. */
export function pageOf(q = {}) {
  let x = L.inputsOf(q, INDEX);
  const g = INDEX.grids[x.grid], files = yearFiles(x.grid), region = g.regions.find((r) => r.id === x.region);
  const flex = x.run !== "flat";
  let ms = region?.[x.buy] ? L.monthsRuled(files, x.region, x.buy, x, "forecast").months : [];
  if (q.buy === undefined && x.buy === "rt" && !L.lastTwelve(ms) && region?.da) {
    const da = L.monthsRuled(files, x.region, "da", x, "forecast").months;
    if (L.lastTwelve(da)) { x = { ...x, buy: "da" }; ms = da; }
  }
  const l12 = L.lastTwelve(ms), s12 = l12 ? L.span(l12) : null, w36 = L.last36(ms), bad = L.badMonth(w36?.months ?? []);
  let ways = [null, null];
  if (region?.[x.buy]) {
    ways = flex ? [wayOf(ms.length ? flatMonths(ms) : L.monthsOf(files, x.region, x.buy, FLAT_LOAD)), wayOf(ms)]
      : [wayOf(ms), region.da ? wayOf(L.monthsRuled(files, x.region, x.buy, ALT, "forecast").months) : null];
  }
  return { x, files, region, flex, ms, l12, s12, bad, ways, load: { run: flex ? FLEX : FLAT, gpu: x.gpu, pue: x.pue } };
}

/** Session 228: the three ways of running the answers hold (lib/datacenter/reads.ts, waysOf), each with its months,
 * weights and prices under the rule, from the page's own files. */
export async function ruledWays(page) {
  const R = await import("../lib/datacenter/answers.ts");
  const specs = R.waysOf(page.x, { n: L.DEFAULTS.n, shift: L.DEFAULTS.shift });
  const out = {};
  for (const k of ["flat", "flex", "shift"]) out[k] = L.monthsRuled(page.files, page.x.region, page.x.buy, specs[k], "forecast");
  return out;
}
