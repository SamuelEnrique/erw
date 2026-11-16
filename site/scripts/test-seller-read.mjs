// Chain 304, part B (sessions 7520 and 7523): "What a generator earns" (/cost-of-power/seller) read as a fund analyst
// underwriting a solar or a wind plant, for five cases (docs/reviews/generator-read-2026-11-16.md). The page itself is
// drawn to HTML without a build (scripts/tsx-register.mjs), from its committed files alone (data/merchant_snapshot.json,
// data/seller/), as a visitor's address would draw it; nothing is asked of a server. Each site fault the read found is
// held here as fixed, the row numbers the read's, and each figure is recomputed from the files by this script's own
// arithmetic, not the page's.
//   node --import ./scripts/tsx-register.mjs scripts/test-seller-read.mjs
import fs from "node:fs";
import path from "node:path";
import { register } from "node:module";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

register(`data:text/javascript,${encodeURIComponent(`
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stub:google") return { format: "module", shortCircuit: true, source:
    "const f = () => ({ className: '', variable: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;" };
  return next(url, context);
}`)}`);

const here = path.dirname(fileURLToPath(import.meta.url));
const json = (...p) => JSON.parse(fs.readFileSync(path.join(here, "..", ...p), "utf-8"));
const { default: Seller } = await import("../app/cost-of-power/seller/page.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
async function draw(query) {
  const q = Object.fromEntries(new URLSearchParams(query));
  return renderToStaticMarkup(await Seller({ searchParams: Promise.resolve(q) }));
}
/** The attribute `name` of the first element carrying `mark` (a data attribute with its value). */
function attrOf(html, mark, name) {
  const i = html.indexOf(mark);
  if (i < 0) return null;
  const tag = html.slice(html.lastIndexOf("<", i), html.indexOf(">", i));
  const m = tag.match(new RegExp(` ${name}="([^"]*)"`));
  return m ? ent(m[1]) : null;
}
const cellOf = (html, mark) => { const i = html.indexOf(mark); return i < 0 ? null : words(html.slice(html.indexOf(">", i) + 1, html.indexOf("</span>", i))); };

// ---- the files, read here: ERCOT's West hub as the page prices it there, and the curtailment page's free energy file
const index = json("data", "seller", "hubs", "index.json");
const grid = json("data", "seller", "hubs", index.grids.ercot.file);
const west = json("data", "seller", "hubs", index.grids.ercot.hubs.HB_WEST.file);
const snap = json("data", "merchant_snapshot.json");
const free = json("data", "curtailment", "free_energy.json");
const belowIn = (hub, m) => { const ix = grid.months[m]; return hub.price.slice(ix[0], ix[1]).filter((p) => p !== null && p < 0).length; };
const monthsFrom = (a, b) => Object.keys(west.months).filter((m) => grid.months[m] && m >= a && m <= b).sort();
const l12 = monthsFrom("2025-10", "2026-09");
const westTwelve = l12.reduce((s, m) => s + belowIn(west, m), 0);

// ---- case 1, rows 1 and 2: a 200 MW solar plant at the West hub; the hours priced below zero are on the page
const c1 = await draw("iso=ercot&asset=solar&hub=HB_WEST&mw=200");
ok(words(c1).includes("Hours priced below zero, a year"), "rows 1 and 2: the spans table has a row of the hours priced below zero");
const t12 = Number(attrOf(c1, 'data-below-zero="twelve"', "data-raw"));
ok(l12.length === 12 && t12 === westTwelve, `rows 1 and 2: the last twelve months' count is the hub file's own, ${t12} against ${westTwelve} recomputed (Oct 2025 to Sep 2026)`);
const loc = free.grids.ercot.locations.find((l) => l.id === "HB_WEST");
const freeBy = Object.fromEntries(free.year_months.map((m, i) => [m, loc.heat.negative[i].reduce((a, v) => a + v, 0)]));
const overlap = l12.filter((m) => m in freeBy);
ok(overlap.length === 11 && overlap.every((m) => freeBy[m] === belowIn(west, m)), `rows 1 and 2: the curtailment page's free energy file counts the same hours below zero in each of the ${overlap.length} months both hold`);
ok(/over the twelve months/.test(attrOf(c1, 'data-below-zero="twelve"', "title") ?? "") && /a year, the mean of 3 years, 2023 to 2025/.test(attrOf(c1, 'data-below-zero="three"', "title") ?? ""), "rows 1 and 2: each count says its span on hover");
const three = ["2023", "2024", "2025"].reduce((s, y) => s + monthsFrom(`${y}-01`, `${y}-12`).reduce((a, m) => a + belowIn(west, m), 0), 0) / 3;
ok(Number(attrOf(c1, 'data-below-zero="three"', "data-raw")) === Math.round(three), `rows 1 and 2: the three-year mean is ${Math.round(three)} hours a year, recomputed`);

// ---- row 9 (case 5): a long-run capture rate gives each year's own on hover
const tip = attrOf(c1, 'data-rate-years="three"', "title") ?? "";
const rateOf = (y) => {   // the table's way: the fleet's revenue over its energy, over the mean of the months' flat prices
  const ms = monthsFrom(`${y}-01`, `${y}-12`).map((m) => west.months[m]);
  const sales = ms.reduce((a, r) => a + r.solar.sales_per_mw, 0), energy = ms.reduce((a, r) => a + r.solar.energy_per_mw, 0);
  const flat = ms.reduce((a, r) => a + r.flat, 0) / ms.length;
  return Math.round((100 * (sales / energy)) / flat);
};
ok(["2023", "2024", "2025"].every((y) => tip.includes(`${y} ${rateOf(y)}`)), `row 9: the three-year rate's hover lists each year's own rate (${["2023", "2024", "2025"].map((y) => `${y} ${rateOf(y)}`).join(", ")})`);
ok(cellOf(c1, 'data-rate-years="three"') === "101" && /weighs by generation/.test(tip), "row 9: the long-run rate itself is unchanged, and the hover says why the chart's years can differ by a point");

// ---- case 1, CAISO: one full year held, so the long-run span is that year
const c1b = await draw("iso=caiso&asset=solar&hub=TH_SP15_GEN-APND&mw=200");
ok(/ in 2025:/.test(attrOf(c1b, 'data-below-zero="every"', "title") ?? ""), "rows 1 and 2: a span of one full year says the year, not \"the twelve months\"");
const sp15 = snap.isos.caiso;
const sp15Below = (m) => { const r = sp15.months[m]; return sp15.price.slice(r.i0, r.i1).filter((p) => p !== null && p < 0).length; };
const y2025 = Object.keys(sp15.months).filter((m) => m.startsWith("2025")).reduce((a, m) => a + sp15Below(m), 0);
ok(Number(attrOf(c1b, 'data-below-zero="every"', "data-raw")) === y2025, `rows 1 and 2: SP15's 2025 count is the snapshot's own, ${y2025}`);

// ---- case 4: a peaker's page draws no such row (its spans are of the hours it runs)
const c4 = await draw("iso=ercot&asset=peaker&hub=HB_HOUSTON&mw=100");
ok(!c4.includes("data-below-zero") && words(c4).includes("Price while running over every hour's, percent"), "rows 1 and 2: the peaker's table is as it was");

// ---- case 3, row 6: scenario B under a contract for all the energy at USD 38 finds its own worst month
const c3 = await draw("iso=ercot&asset=solar&hub=HB_WEST&mw=200&bn=100&bp=38&by=15&v=b");
const near = snap.defaults.near;
const held = Object.keys(west.months).filter((m) => grid.months[m] && west.months[m].solar && west.months[m].solar.hours / grid.months[m][2] >= near - 1e-9).sort();
const worst = held.map((m) => ({ m, usd: west.months[m].solar.energy_per_mw * 200 * 38 })).reduce((lo, r) => (r.usd < lo.usd ? r : lo));
const usd0 = (v) => `USD ${Math.round(v).toLocaleString("en-US")}`;
const t3 = words(c3);
ok(worst.m === "2018-12" && t3.includes(`${usd0(worst.usd)} December 2018, of ${held.length} months, with the contract (100 percent at USD 38 per MWh`), `row 6: B's worst month is ${worst.m} at ${usd0(worst.usd)}, recomputed from the hub file's energy`);
ok(t3.includes("In the market alone: March 2026, USD 213,111"), "row 6: the market's worst month stays beside it");
ok((t3.match(/USD 213,111 March 2026, of \d+ months; coverage that month 0\.00 times, in the market/g) ?? []).length === 1, "row 6: scenario A, with no contract, draws the market's worst month as before");
const c3b = await draw("iso=ercot&asset=solar&hub=HB_WEST&mw=200&bn=100&bp=38&by=15&v=b&ps=block");
ok(!words(c3b).includes("with the contract (100 percent"), "row 6: a flat block keeps the market's worst month (its monthly volume is not held here)");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
