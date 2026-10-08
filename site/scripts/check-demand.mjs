// Energy Research Warehouse (ERW) site, session 97: the demand growth explorer, on the built site.
// Since session 152 it is the first view of the one demand page (the second is scripts/check-demand-weather.mjs).
//
//   npm run build && npx next start -p 3097
//   node --import ./scripts/alias-loader.mjs scripts/check-demand.mjs [base-url]      (default http://localhost:3097)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of eia930_demand_growth
//             (data/demand_growth.json), for every area
//   charts    a bar per whole year; a cell per month and hour the table holds; twelve months and 24 hours of change
//   ranking   the areas in the order of the measure asked for, an area that lacks it last
//   weather   "weather is not removed" is on the page, above the tool, a short placeholder whose hover holds its
//             sentence (session 152: no limitations prose on the face)
//   face      the two views' links, the Method note's link, the hours left out, no folded method prose
//   hover     in a real browser, each of the four charts answers the mouse
//   peaks     each year's peak with its local date; the Lower 48 with no peak, and the reason
//   break     California's check across December 2025, with its rows, on California's page only
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as g from "../lib/demandgrowth.ts";

const base = (process.argv[2] ?? "http://localhost:3097").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/demand_growth.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const HOVERS = [];   // [path, [[chart, what its tooltip must say]]], filled below and read in a real browser at the end
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));

async function view(slug, rankSlug) {
  const path = g.href(slug, rankSlug);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const { ba, rank } = g.choices({ area: slug, rank: rankSlug });
  const a = file.areas[ba], got = marked(html), ys = g.wholeYears(a), first = ys[0], last = ys.at(-1), ytd = g.yearToDate(file, a);
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  const maybe = (k, v, f) => { if (v === undefined) { if (k in got) wrong.push(`${k}: on the page, not in the copy`); } else want(k, f(v)); };
  want("sum|avg0", g.whole(first.row.avg_demand_mw));
  want("sum|avg1", g.whole(last.row.avg_demand_mw));
  want("sum|avg_growth", g.signed(last.row.avg_demand_growth_since_2019_pct));
  want("head|avg_growth", g.signed(last.row.avg_demand_growth_since_2019_pct));
  maybe("sum|peak1", last.row.peak_demand_mw, g.whole);
  maybe("head|peak_growth", last.row.peak_demand_growth_since_2019_pct, g.signed);
  want("sum|ytd_growth", g.signed(ytd.row.ytd_avg_demand_growth_since_2019_pct));
  want("head|ytd1", g.whole(ytd.row.ytd_avg_demand_mw));
  want("head|ytd0", g.whole(ytd.base.ytd_avg_demand_mw));
  for (const { year, row } of ys) {
    want(`y|${year}|avg`, g.whole(row.avg_demand_mw));
    maybe(`y|${year}|avg_growth`, row.avg_demand_growth_since_2019_pct, g.signed);
    maybe(`y|${year}|yoy`, row.avg_demand_growth_yoy_pct, g.signed);
    maybe(`y|${year}|peak`, row.peak_demand_mw, g.whole);
    maybe(`y|${year}|peak_growth`, row.peak_demand_growth_since_2019_pct, g.signed);
    want(`y|${year}|hours`, g.whole(row.hours_used));
  }
  want("ytd|avg", g.whole(ytd.row.ytd_avg_demand_mw));
  maybe("ytd|peak", ytd.row.ytd_peak_demand_mw, g.whole);
  const cs = g.cells(file, a), ex = g.extremes(cs);
  want("cell|most|pct", g.signed(ex.most.pct));
  want("cell|least|pct", g.signed(ex.least.pct));
  const ranked = g.ranking(file, rank);
  for (const r of ranked) { maybe(`rank|${r.ba}|avg`, r.avg, g.signed); maybe(`rank|${r.ba}|peak`, r.peak, g.signed); maybe(`rank|${r.ba}|ytd`, r.ytd, g.signed); }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const bars = [...html.matchAll(/data-year="(\d{4})"/g)].map((x) => x[1]);
  const drawn = [...html.matchAll(/data-cell="(\d+\|\d+)"/g)].length;
  check(bars.join() === ys.map((y) => y.year).join() && drawn === cs.length && html.includes('data-chart="by month"') && html.includes('data-chart="by hour"'),
    `${tag} ${bars.length} years drawn, ${drawn} month-and-hour cells, and the change by month and by hour`);
  const order = [...html.matchAll(/data-ranked="(\d+)\|([A-Z0-9]+)"/g)].map((x) => x[2]);
  check(order.join() === ranked.map((r) => r.ba).join(), `${tag} the ranking by ${rank.slug}: ${order.join(", ")}`);
  const t = text(html);
  check(html.includes('data-weather="1"') && t.includes("Weather is not removed.") && t.indexOf("Weather is not removed.") < t.indexOf("Year by year") && /title="[^"]*hot summer and cold snap included[^"]*"/.test(html) && !t.includes("hot summer and cold snap included"),
    `${tag} "weather is not removed", above the tool: a short placeholder, its sentence in the hover`);
  const hints = [...html.matchAll(/data-hint="1"/g)].length;
  check(html.includes('data-demand="metered"') && html.includes('data-view="metered"') && html.includes('data-view="weather"') && html.includes('href="/data/methods/demand_growth"') && hints >= 5 && !t.includes("How it is computed") && !t.includes("What is not here")
    && got["screen|jumps"] === g.whole(a.screened.jumps) && got["screen|zero"] === g.whole(a.screened.not_positive) && got["screen|blank"] === g.whole(a.screened.blank),
    `${tag} the two views and the Method note are linked; ${hints} placeholders with a hover; the hours left out are the copy's; no method prose folded on the face`);
  const peak = a.at[last.year]?.peak_demand_mw;
  check(peak ? t.includes(g.localHour(peak, a.tz)) : t.includes("No peak is given for the Lower 48"), `${tag} ${peak ? `the peak of ${last.year} is dated ${g.localHour(peak, a.tz)}` : "no peak for the Lower 48, and the reason"}`);
  check((ba === "CISO") === html.includes('data-break="1"'), `${tag} the check across December 2025 is ${ba === "CISO" ? "shown" : "not shown"}`);
  if (ba === "CISO") {
    const bw = [];
    for (const r of file.caiso_break.rows) { if (got[`break|${r.year}|ratio`] !== r.ratio.toFixed(4)) bw.push(r.year); if (got[`break|${r.year}|before`] !== g.whole(r.before_mw)) bw.push(r.year); }
    check(bw.length === 0 && t.includes("California's demand does not step at the break"), `${tag} the break check's ${file.caiso_break.rows.length} rows are the copy's, and its sentence`);
  }
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
}

for (const slug of Object.keys(g.SLUGS)) await view(slug, "avg");
await view("ercot", "peak");
await view("pjm", "ytd");
{
  HOVERS.push([g.href("ercot", "avg"), [["years", /2019: average [\d,]+ MW, highest hour [\d,]+ MW/], ["heat", /January, .+: [+-][\d.]+ percent, [+-]?[\d,]+ MW/], ["by month", /January: [+-][\d.]+ percent from \d{4} to \d{4}/], ["by hour", /: [+-][\d.]+ percent from \d{4} to \d{4}/]]]);
  HOVERS.push([g.href("us48", "avg"), [["years", /2019: average [\d,]+ MW$/]]]);
  const d = await get("/demand?area=mars&rank=luck");
  check(d.status === 200 && marked(d.html)["sum|avg1"] === g.whole(g.wholeYears(file.areas.ERCO).at(-1).row.avg_demand_mw), "an address it does not understand opens ERCOT, ranked by average demand");
  const v = await get(g.href("ercot", "avg"), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
}
// ---- session 152, in a real browser: every chart answers the mouse --------------------------------------------------
// The charts are SVG drawn on the server; components/demand/Hover.tsx shows a mark's own words beside the pointer.
// A mouse move is sent to one mark of each chart and the box that appears is read.
{
  const code = await withBrowser(async ({ go, evaluate, wait, unlock: open }) => {
    await open(base);
    for (const [path, charts] of HOVERS) {
      await go(base + path);
      await wait(`document.querySelectorAll('[data-hover="1"] svg[data-chart]').length >= ${charts.length}`, 20000, `${path}: the charts`);
      for (const [id, re] of charts) {
        const tip = await evaluate(`(async () => {
          const svg = document.querySelector('svg[data-chart="${id}"]');
          const mark = svg && svg.querySelector('[data-tip]');
          if (!mark) return null;
          const r = mark.getBoundingClientRect();
          for (let i = 0; i < 20; i += 1) {
            mark.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }));
            await new Promise((ok) => setTimeout(ok, 150));
            const box = svg.closest('[data-hover="1"]').querySelector('[data-tooltip="1"]');
            if (box) return box.textContent;
          }
          return '';
        })()`);
        check(typeof tip === "string" && re.test(tip), `${path}: the chart "${id}" answers the mouse ("${String(tip).slice(0, 110)}")`);
      }
      const still = await evaluate(`[...document.querySelectorAll('svg[data-chart]')].filter((s) => !s.closest('[data-hover="1"]')).length + document.querySelectorAll('svg[data-chart] title').length`);
      check(still === 0, `${path}: no chart stands outside a hover frame, and none keeps a browser tooltip of its own`);
    }
    return 0;
  });
  if (code === null) console.log("not proven here: no Chrome or Edge on this machine, so the charts' answer to the mouse was not read");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
