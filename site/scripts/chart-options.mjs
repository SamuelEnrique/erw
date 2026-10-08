// Energy Research Warehouse (ERW) site, session 161: what every chart on the live pages draws, read in a real browser,
// and the comparison of two readings. It stands beside scripts/snapshot-live.mjs, which reads a page's numbers and
// words as served and cannot see a chart: a chart is drawn in the visitor's browser from the shared chart component
// (components/TimeChart.tsx), so a change to that component is checked here.
//
//   node scripts/chart-options.mjs take <name> [base-url]     writes runs/snapshots/<name>_charts.json
//   node scripts/chart-options.mjs compare <before> <after>   lists every difference; exit 0 none, 1 some, 2 bad input
//
// For each of the three pages open to visitors it loads the page as a visitor, waits for its charts, and keeps for
// every chart the option the chart library holds (its axes, grid, zoom, tooltip, legend and series), with each function
// written as the word "function" (a build renames what is inside one) and each series' points kept apart.
//
// The comparison reports, chart by chart: a chart on one side only; a difference in a chart's settings (the path and
// both values); and, apart, a difference in a series' points (how many, and whether the earlier points are all still
// there). It does not judge a difference in the points: EIA publishes new hours by itself. A difference in settings is
// the component's. Where a range slider starts and ends is the time of the first and last point, so a difference there
// is listed with the points (RANGE) and is not counted as a setting.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(here, "..", "..", "runs", "snapshots");
const PRODUCTION = "https://erw-flame.vercel.app";
export const CHART_PAGES = ["/cost-of-power/battery", "/network", "/storage"];

const READ = `(() => {
  const e = window.echarts;
  if (!e) return [];
  return Array.from(document.querySelectorAll("[_echarts_instance_]")).map((el) => {
    const inst = e.getInstanceByDom(el);
    const o = inst ? inst.getOption() : null;
    return { label: el.getAttribute("aria-label") || "", width: el.clientWidth, height: el.clientHeight,
      option: o ? JSON.parse(JSON.stringify(o, (k, v) => (typeof v === "function" ? "function" : v))) : null };
  });
})()`;

async function take(name, base) {
  const pages = {};
  const code = await withBrowser(async ({ go, evaluate, sleep }) => {
    for (const page of CHART_PAGES) {
      await go(`${base}${page}`);
      // the charts mount after the library loads: read until two readings a second apart hold the same number of charts
      let last = -1, charts = [];
      for (let i = 0; i < 25; i += 1) {
        await sleep(1000);
        charts = await evaluate(READ);
        if (i >= 4 && charts.length === last) break;
        last = charts.length;
      }
      pages[page] = charts.map((c) => {
        const series = (c.option?.series ?? []).map((s) => ({ name: s.name ?? "", points: s.data ?? null }));
        const settings = c.option ? { ...c.option, series: (c.option.series ?? []).map((s) => ({ ...s, data: undefined })) } : null;
        return { label: c.label, width: c.width, height: c.height, settings, series };
      });
      console.log(`${page}: ${charts.length} charts, ${pages[page].reduce((a, c) => a + c.series.reduce((b, s) => b + (Array.isArray(s.points) ? s.points.length : 0), 0), 0)} points`);
    }
    return 0;
  });
  if (code === null) { console.log("no browser on this machine: not read"); return 1; }
  fs.mkdirSync(OUT, { recursive: true });
  const file = path.join(OUT, `${name}_charts.json`);
  fs.writeFileSync(file, JSON.stringify({ name, base, taken_utc: new Date().toISOString(), pages }) + "\n");
  console.log(`${name}: ${CHART_PAGES.length} pages, ${Object.values(pages).reduce((a, p) => a + p.length, 0)} charts, from ${base} -> ${file}`);
  return 0;
}

function walk(a, b, at, out) {
  if (JSON.stringify(a) === JSON.stringify(b)) return;
  if (a && b && typeof a === "object" && typeof b === "object" && Array.isArray(a) === Array.isArray(b)) {
    for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) walk(a[k], b[k], `${at}.${k}`, out);
  } else out.push(`${at}: ${JSON.stringify(a)?.slice(0, 120)} -> ${JSON.stringify(b)?.slice(0, 120)}`);
}

function compare(x, y) {
  const read = (n) => { const f = path.join(OUT, `${n}_charts.json`); return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : null; };
  const a = read(x), b = read(y);
  if (!a || !b) { console.log("a reading is missing"); return 2; }
  let settings = 0, points = 0, charts = 0;
  for (const page of CHART_PAGES) {
    const pa = a.pages[page] ?? [], pb = b.pages[page] ?? [];
    if (pa.length !== pb.length) { settings += 1; console.log(`${page}: ${pa.length} charts before, ${pb.length} after`); }
    for (let i = 0; i < Math.min(pa.length, pb.length); i += 1) {
      charts += 1;
      const ca = pa[i], cb = pb[i], what = `${page} chart ${i + 1} (${cb.label.slice(0, 70)})`;
      const diffs = [];
      walk({ label: ca.label, height: ca.height, settings: ca.settings }, { label: cb.label, height: cb.height, settings: cb.settings }, "", diffs);
      walk(ca.series.map((s) => s.name), cb.series.map((s) => s.name), ".series_names", diffs);
      // where a range slider starts and ends is the first and last point's own time: a difference there is the points'
      const range = diffs.filter((d) => /^\.settings\.dataZoom\.\d+\.(startValue|endValue):/.test(d));
      for (const d of diffs.filter((x) => !range.includes(x))) { settings += 1; console.log(`SETTINGS ${what} ${d}`); }
      for (const d of range) console.log(`RANGE ${what} ${d} (the slider's ends follow the points)`);
      for (let j = 0; j < Math.min(ca.series.length, cb.series.length); j += 1) {
        const sa = JSON.stringify(ca.series[j].points), sb = JSON.stringify(cb.series[j].points);
        if (sa === sb) continue;
        points += 1;
        const before = new Map((ca.series[j].points ?? []).map((p) => [JSON.stringify(Array.isArray(p) ? p[0] : p), JSON.stringify(p)]));
        const after = new Map((cb.series[j].points ?? []).map((p) => [JSON.stringify(Array.isArray(p) ? p[0] : p), JSON.stringify(p)]));
        const shared = [...before.keys()].filter((k) => after.has(k));
        const changed = shared.filter((k) => before.get(k) !== after.get(k)).length;
        console.log(`POINTS ${what} series ${ca.series[j].name}: ${before.size} points before, ${after.size} after; ${shared.length} at the same place, of which ${changed} with another value; ${after.size - shared.length} new, ${before.size - shared.length} gone`);
      }
    }
  }
  console.log(`${x} -> ${y}: ${charts} charts compared; ${settings} differences in settings, ${points} series whose points differ`);
  return settings || points ? 1 : 0;
}

const [cmd, x, y] = process.argv.slice(2);
if (cmd === "take" && x) process.exit(await take(x, (y ?? PRODUCTION).replace(/\/$/, "")));
else if (cmd === "compare" && x && y) process.exit(compare(x, y));
else { console.log("usage: chart-options.mjs take <name> [base-url] | compare <before> <after>"); process.exit(2); }
