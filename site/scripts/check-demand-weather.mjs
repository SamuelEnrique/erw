// Energy Research Warehouse (ERW) site, session 126: demand growth with the weather taken out, on the built site.
//
//   npm run build && npx next start -p 3126
//   node --import ./scripts/alias-loader.mjs scripts/check-demand-weather.mjs [base-url]      (default http://localhost:3126)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers    every number the page marks (data-n) equals the site's copy of eia930_demand_weather
//              (data/demand_weather.json), for every figure, and for every year of one of them
//   chart      one group of bars per grid that holds the figure, and "not held" for one that does not
//   readings   a row is called a finding only when the copy says so
//   remainder  "what the remainder is not" is on the page, above the tool, with its sentence
//   stations   the 35 stations, each with its weight, and the words on the populations
//   visitor    without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
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
  check(html.includes('data-remainder="1"') && t.includes("What the remainder is not.") && t.includes("The warehouse cannot split them") && t.indexOf("What the remainder is not.") < t.indexOf("By grid and year"), `${tag} what the remainder is not, above the tool`);
  const st = Object.keys(file.weather?.stations ?? {});
  check(st.length === 35 && st.every((c) => got[`s|${c}|w`] === file.weather.stations[c].weight.toFixed(2)) && t.includes("The populations were not retrieved"), `${tag} ${st.length} stations with their weights, and the words on the populations`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
}

const last = g.lastWholeYear(file);
for (const f of g.FIGURES) await view(f.slug, last);
for (const y of g.years(file)) await view("energy", y);
{
  const d = await get("/demand/weather?figure=mars&year=1066");
  const f = g.figureOf(file, "ERCO", last, "energy");
  check(d.status === 200 && marked(d.html)[`t|ERCO|${last}|u`] === g.signed(f.unexplained_pct) && d.html.includes(`${g.FIGURES[0].name}, ${last}`), `an address it does not understand opens the year's energy in ${last}`);
  const v = await get(g.href("energy", last), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
