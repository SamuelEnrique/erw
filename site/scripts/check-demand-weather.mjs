// Energy Research Warehouse (ERW) site, session 126: demand growth with the weather taken out, on the built site.
// Since session 152 it is the second view of the one demand page (/demand?view=weather); the address it was built at
// (/demand/weather) redirects there.
//
//   npm run build && npx next start -p 3126
//   node --import ./scripts/alias-loader.mjs scripts/check-demand-weather.mjs [base-url]      (default http://localhost:3126)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers    every number the page marks (data-n) equals the site's copy of eia930_demand_weather
//              (data/demand_weather.json), for every figure, and for every year of one of them
//   chart      one group of bars per grid that holds the figure, and "not held" for one that does not
//   readings   a row is called a finding only when the copy says so
//   remainder  "what the remainder is not" is on the page, above the tool, a short placeholder whose hover holds its
//              sentence (session 152: no limitations prose on the face)
//   face       the two views' links, the Method note's link, no folded method prose, the old address redirecting
//   hover      in a real browser, the chart answers the mouse with the grid, the year and the figure
//   stations   the 35 stations, each with its weight, and the words on the populations
//   visitor    without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as g from "../lib/demandweather.ts";

const base = (process.argv[2] ?? "http://localhost:3126").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/demand_weather.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const HOVERS = [];   // [path, [[chart, what its tooltip must say]]], filled below and read in a real browser at the end
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));

async function view(slug, year) {
  const path = g.href(slug, year);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const { figure } = g.choices(file, { figure: slug, year: String(year) });
  const got = marked(html), wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  let rows = 0, findings = 0;
  for (const ba of g.ORDER) for (const y of g.years(file)) {
    const f = g.figureOf(file, ba, y, figure.key), k = `t|${ba}|${y}`;
    if (!f) { if (`${k}|u` in got) wrong.push(`${k}: on the page, not in the copy`); continue; }
    rows += 1;
    findings += f.finding ? 1 : 0;
    want(`${k}|mw`, g.whole(f.actual)); want(`${k}|g`, g.signed(f.growth_pct)); want(`${k}|w`, g.signed(f.weather_pct)); want(`${k}|u`, g.signed(f.unexplained_pct));
    if (f.uncertainty_pct !== null) want(`${k}|pm`, g.one(f.uncertainty_pct));
  }
  const { found, not } = g.split(file, String(year), figure.key);
  want("sum|found", String(found.length));
  for (const x of found) { want(`sum|${x.ba}|u`, g.signed(x.g.unexplained_pct)); want(`sum|${x.ba}|pm`, g.one(x.g.uncertainty_pct)); }
  if (not.length) want("sum|not", String(not.length));
  for (const ba of g.ORDER) for (const y of file.train) { const h = file.grids[ba].holdout[String(y)]?.[figure.key]; if (h) want(`h|${ba}|${y}`, g.signed(h.unexplained_pct)); }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page, ${rows} rows of the table)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const drawn = [...html.matchAll(/data-grid="([A-Z]+)"/g)].map((x) => x[1]);
  const held = g.ORDER.filter((ba) => g.figureOf(file, ba, String(year), figure.key));
  check(html.includes('data-chart="explained"') && drawn.join() === held.join(), `${tag} the chart draws ${drawn.length} grids (${g.ORDER.length - held.length} not held)`);
  const said = [...html.matchAll(/data-reading="finding"/g)].length;
  check(said === findings, `${tag} ${said} rows are called a finding, ${findings} in the copy`);
  const t = text(html);
  const hints = [...html.matchAll(/data-hint="1"/g)].length;
  check(html.includes('data-remainder="1"') && t.includes("What the remainder is not.") && !t.includes("The warehouse cannot split them") && /title="[^"]*The warehouse cannot split them[^"]*"/.test(html) && t.indexOf("What the remainder is not.") < t.indexOf("By grid and year"),
    `${tag} what the remainder is not, above the tool: a short placeholder, its sentence in the hover`);
  check(html.includes('data-demand="weather"') && html.includes('data-view="metered"') && html.includes('data-view="weather"') && html.includes('data-method="1"') && t.includes("Method, sources and gaps") && hints >= 5 && !t.includes("How it is computed") && !t.includes("What is not here"),
    `${tag} the two views are linked and the Method note is named; ${hints} placeholders with a hover; no method prose folded on the face`);
  const st = Object.keys(file.weather?.stations ?? {});
  check(st.length === 35 && st.every((c) => got[`s|${c}|w`] === file.weather.stations[c].weight.toFixed(3)) && t.includes("Census Bureau") && st.every((c) => got[`s|${c}|p`] === g.whole(file.weather.stations[c].population)), `${tag} ${st.length} stations with their weights and the Census Bureau's counts`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
}

const last = g.lastWholeYear(file);
for (const f of g.FIGURES) await view(f.slug, last);
for (const y of g.years(file)) await view("energy", y);
{
  const old = await fetch(`${base}/demand/weather?figure=night&year=2026`, { redirect: "manual", headers: { Cookie: cookie } });
  const to = old.headers.get("location") ?? "";
  check([307, 308].includes(old.status) && /\/demand\?/.test(to) && to.includes("view=weather") && to.includes("figure=night") && to.includes("year=2026"), `the address it was built at redirects to the view, its choices kept (${old.status} to ${to})`);
  HOVERS.push([g.href("energy", last), [["explained", new RegExp(`${file.grids.ERCO.name}, ${last}: the weather explains [+-]?\\d`)]]]);
  const d = await get("/demand?view=weather&figure=mars&year=1066");
  const f = g.figureOf(file, "ERCO", last, "energy");
  check(d.status === 200 && marked(d.html)[`t|ERCO|${last}|u`] === g.signed(f.unexplained_pct) && d.html.includes(`${g.FIGURES[0].name}, ${last}`), `an address it does not understand opens the year's energy in ${last}`);
  const v = await get(g.href("energy", last), false);
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
      const method = await evaluate(`(document.querySelector('[data-method="1"] a') || { getAttribute: () => '' }).getAttribute('href')`);
      check(/^\/data\/methods\/demand_(growth|weather)$/.test(String(method)), `${path}: the Method note is linked (${method})`);
      const still = await evaluate(`[...document.querySelectorAll('svg[data-chart]')].filter((s) => !s.closest('[data-hover="1"]')).length + document.querySelectorAll('svg[data-chart] title').length`);
      check(still === 0, `${path}: no chart stands outside a hover frame, and none keeps a browser tooltip of its own`);
    }
    return 0;
  });
  if (code === null) console.log("not proven here: no Chrome or Edge on this machine, so the charts' answer to the mouse was not read");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
