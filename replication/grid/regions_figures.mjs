// ERW, the Grid tool's thirteen regions: the figures the page draws, read from the page (session 8606, chain 504).
//
// For each region of site/data/regions/index.json this opens the region's Mix tab and its trade tab on a built
// site, in the internal view, and writes down what a reader sees: the latest hour held and its three figures, the
// eight sources of that hour, the period drawn and its shares, the days held, the lines on months not held, the
// table of one calendar month across the years, and the trade of the newest month with its line on a part of a
// month. replicate_regions.py computes the same figures from the files, without the page's code, and compares.
//
//   node replication/grid/regions_figures.mjs <base-url> [out.json]
//
// It reads the page only. INTERNAL_COSTS_TOKEN opens the internal view, as for the site's own browser checks.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const [base, out = path.join(here, "regions_page_figures.json")] = process.argv.slice(2);
if (!base) { console.error("usage: node replication/grid/regions_figures.mjs <base-url> [out.json]"); process.exit(2); }
const index = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "site", "data", "regions", "index.json"), "utf-8"));

// session 8613: when each region's two files were built, kept beside the figures. The data machine rebuilt the mix
// files on 19 November without rebuilding the index, so the index's own stamp does not say that a file changed.
function filesBuilt() {
  const dir = path.join(here, "..", "..", "site", "data", "regions");
  const built = (kind, code) => { try { return JSON.parse(fs.readFileSync(path.join(dir, kind, `${code.toLowerCase()}.json`), "utf-8")).built ?? null; } catch { return null; } };
  return Object.fromEntries(index.regions.map((r) => [r.code, { mix: built("mix", r.code), trade: built("trade", r.code) }]));
}

const MIX = `(() => { const v = document.querySelector('[data-region-view="mix"]'); if (!v) return null;
  const t = (e) => (e ? e.innerText.replace(/\\s+/g, ' ').trim() : null);
  const rows = (name) => [...document.querySelectorAll('[data-region-table="' + name + '"] tbody tr')].map((r) => [...r.children].map((c) => t(c)));
  return { state: v.getAttribute('data-region-mix'), now: document.querySelector('[data-region-now]')?.getAttribute('data-region-now') ?? null,
    figures: Object.fromEntries([...document.querySelectorAll('[data-region-figure]')].map((e) => [e.getAttribute('data-region-figure'), t(e)])),
    now_rows: rows('now'), period: v.getAttribute('data-region-period'), shares_rows: rows('shares'), days_line: t(document.querySelector('#shares p')),
    months_not_held: t(document.querySelector('[data-months-not-held]')), months_after: t(document.querySelector('[data-months-after]')),
    hours_drawn: Number(document.querySelector('[data-region-hours]')?.getAttribute('data-region-hours') ?? 0),
    cal: t(document.querySelector('#years h2, #years h3')), years_rows: rows('years'), net_load_without: document.querySelector('[data-net-load-without]')?.getAttribute('data-net-load-without') ?? null }; })()`;
const TRADE = `(() => { const v = document.querySelector('[data-region-view="trade"]'); if (!v) return null;
  const t = (e) => (e ? e.innerText.replace(/\\s+/g, ' ').trim() : null);
  return { state: v.getAttribute('data-region-trade'), month: v.getAttribute('data-region-month'), rows: [...document.querySelectorAll('[data-region-table="trade"] tbody tr')].map((r) => [...r.children].map((c) => t(c))),
    part_month: t(document.querySelector('[data-part-month]')), part_month_chart: t(document.querySelector('[data-part-month-chart]')) }; })()`;

await withBrowser(async ({ go, evaluate, unlock, sleep, send, errors }) => {
  await unlock(base);
  await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  const regions = {};
  for (const r of index.regions) {
    const slug = r.code.toLowerCase();
    await go(`${base}/grid?region=${slug}`);
    await sleep(1200);
    const mix = await evaluate(MIX);
    await go(`${base}/grid?region=${slug}&view=gravity`);
    await sleep(900);
    const trade = await evaluate(TRADE);
    regions[r.code] = { name: r.name, mix, trade };
    console.log(`${r.code}: now ${mix?.now ?? "none"}, period ${mix?.period ?? "none"}, ${mix?.now_rows.length ?? 0} sources, ${mix?.years_rows.length ?? 0} years; trade ${trade?.month ?? "none"}, ${trade?.rows.length ?? 0} rows`);
  }
  fs.writeFileSync(out, `${JSON.stringify({ what: "the figures the Grid tool's region tabs draw, read from the page", base: base.replace(/^https?:\/\/localhost:\d+/, "a local build"), taken: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
    index_built: index.built, files_built: filesBuilt(), regions }, null, 1)}\n`);
  console.log(`${Object.keys(regions).length} regions written to ${path.relative(process.cwd(), out)}; errors in the pages: ${JSON.stringify(errors.slice(0, 4))}`);
  return errors.length ? 1 : 0;
});
