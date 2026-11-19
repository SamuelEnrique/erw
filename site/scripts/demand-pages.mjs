// Energy Research Warehouse (ERW) site, session 8420 (chain 503, part C): /demand drawn to HTML without a build, at any
// address, by the page's own function (app/demand/page.tsx) from the site's committed copies (data/demand_growth.json,
// data/demand_weather.json). The consumption view's two live-set reads are answered by a stand-in for fetch with made-up
// rows (three areas, five sectors, 25 months, each value made by a rule; no real row of any table is in this file), as
// scripts/test-demand-read.mjs does. No server, no network, no table written, no click.
//
// What session 8420 added to the views the page already had is one tab in the row of tabs, "The whole country"
// (lib/tabs.ts): an anchor that carries data-tab="country" from its opening tag to its closing tag. `withoutAdded` cuts
// it, so a test can hold the rest of each address to what it was (scripts/test-demand-pin.mjs). The new view itself
// (?view=country) is a new address: before the session that address drew the page as metered.
//
//   import { ADDRESSES, drawDemand, withoutAdded, figuresOf } from "./demand-pages.mjs"   (under battery-awards-page-register.mjs)
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { prerenderToNodeStream } from "react-dom/static";

const here = (p) => new URL(p, import.meta.url);
const MONTHS = Array.from({ length: 25 }, (_, i) => new Date(Date.UTC(2024, 7 + i, 1)).toISOString().replace(/\.\d{3}Z$/, "Z"));
/** The consumption view's stand-in rows: area a (1 to 3), sector s (1 to 5), month i (0 to 24): 1,000,000 a + 10,000 s + 1,000 i MWh. Not data. */
const MADE_UP = [];
["US", "TX", "NM"].forEach((st, a) => ["ALL", "RES", "COM", "IND", "TRA"].forEach((sec, s) => MONTHS.forEach((ts, i) => {
  MADE_UP.push({ entity: `eia:retail_sales:${st}:${sec}`, variable: "retail_sales", ts_utc: ts, value: 1_000_000 * (a + 1) + 10_000 * (s + 1) + 1000 * i, unit: "MWh", freq: "P1M" });
})));

const AREAS = ["ercot", "caiso", "pjm", "miso", "spp", "nyiso", "isone", "us48"];
const RANKS = ["avg", "peak", "ytd"];
const FIGURES = ["energy", "summer", "winter", "night"];
const weather = JSON.parse(fs.readFileSync(here("../data/demand_weather.json"), "utf-8"));
const YEARS = [...new Set(Object.values(weather.grids).flatMap((g) => Object.keys(g.years)))].sort();

/** Every address the page answered before session 8420, by a short name: the page with nothing chosen; each of the
 *  eight areas under each of the three rankings; the weather view with nothing chosen and at each of its four figures
 *  in each year held; the consumption view; and three addresses the page does not understand (it draws its first view,
 *  or its first choice). */
export const ADDRESSES = [
  ["plain", {}],
  ...AREAS.flatMap((a) => RANKS.map((r) => [`metered-${a}-${r}`, { area: a, rank: r }])),
  ["weather", { view: "weather" }],
  ...FIGURES.flatMap((f) => YEARS.map((y) => [`weather-${f}-${y}`, { view: "weather", figure: f, year: y }])),
  ["consumption", { view: "consumption" }],
  ["odd-view", { view: "mars" }],
  ["odd-area", { area: "mars", rank: "mars" }],
  ["odd-year", { view: "weather", figure: "mars", year: "1999" }],
];

let page = null;
/** The page at one address, as the server would first send it. */
export async function drawDemand(query) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const real = globalThis.fetch, log = console.error;
  globalThis.fetch = async (url) => {
    const q = new URL(String(url)).searchParams;
    const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
    const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
    const rows = name === "eia_retail_sales_monthly" ? MADE_UP : name === "eia_sector_energy_consumption_monthly" ? [] : null;
    if (rows === null) return new Response("stand-in: not held", { status: 404 });
    return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
  console.error = () => {};
  try {
    page ??= (await import("../app/demand/page.tsx")).default;
    const { prelude } = await prerenderToNodeStream(await page({ searchParams: Promise.resolve(query) }));
    let html = "";
    for await (const c of prelude) html += c;
    return html;
  } finally {
    globalThis.fetch = real;
    console.error = log;
  }
}

/** The data files the page's code reads as modules: every .json under site/data that app/demand/page.tsx imports,
 *  itself or through what it imports (the imports are read from the source, "@/..." and relative ones followed), each
 *  with the sha256 of its text (line ends as LF). The pin keeps these beside the pages' hashes: a page's HTML is its
 *  code and its data, so the pin can hold the code only while the data is what it was when the pin was written. Files
 *  the build generates (site/content/) are left out: they are not data. */
export function dataFilesOf(entry = "app/demand/page.tsx") {
  const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
  const seen = new Set(), data = {};
  const resolve = (from, spec) => {
    const base = spec.startsWith("@/") ? path.join(site, spec.slice(2)) : /^\.\.?\//.test(spec) ? path.resolve(path.dirname(from), spec) : null;
    if (!base) return null;
    return [base, `${base}.ts`, `${base}.tsx`, path.join(base, "index.ts")].find((p) => fs.existsSync(p) && fs.statSync(p).isFile()) ?? null;
  };
  const walk = (file) => {
    if (seen.has(file)) return;
    seen.add(file);
    const rel = path.relative(site, file).split(path.sep).join("/");
    if (file.endsWith(".json")) {
      if (rel.startsWith("data/")) data[rel] = crypto.createHash("sha256").update(fs.readFileSync(file, "utf-8").replace(/\r\n/g, "\n")).digest("hex");
      return;
    }
    if (!/\.(ts|tsx|mjs|js)$/.test(file)) return;
    const text = fs.readFileSync(file, "utf-8");
    for (const m of text.matchAll(/(?:import|export)\s[^'"`;]*?from\s*["']([^"']+)["']|import\s*["']([^"']+)["']|import\(\s*["']([^"']+)["']\s*\)/g)) {
      const next = resolve(file, m[1] ?? m[2] ?? m[3]);
      if (next) walk(next);
    }
  };
  walk(path.join(site, ...entry.split("/")));
  return Object.fromEntries(Object.entries(data).sort(([a], [b]) => (a < b ? -1 : 1)));
}

/** The page without what session 8420 added to the views it already had: the tab of the new view. */
export function withoutAdded(html) {
  return html.replace(/<a [^>]*data-tab="country"[^>]*>[^<]*<\/a>/g, "");
}

/** How many figures a page prints through its checked-number marks (data-n, and the consumption view's data-check). */
export function figuresOf(html) {
  return (html.match(/ data-n="/g) ?? []).length + (html.match(/ data-check="/g) ?? []).length;
}

/** The words of a page: tags out, entities read, a hover's words kept in square brackets after what carries them. */
export function wordsOf(html) {
  const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
  return ent(html.replace(/<(?:script|style)[\s\S]*?<\/(?:script|style)>/g, " ").replace(/<[^>]*\btitle="([^"]*)"[^>]*>/g, " [title: $1] ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
}
