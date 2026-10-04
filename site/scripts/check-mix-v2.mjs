// Energy Research Warehouse (ERW) site, session 94: the energy mix, version 2, on the built site.
//
//   npm run build && npx next start -p 3094
//   node scripts/check-mix-v2.mjs [base-url]      (default http://localhost:3094)
//
// The page is drawn on the server (no script of its own), so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of the two tables (data/mix/<grid>.json),
//             for a month, a year, a second grid, and a grid with no solar
//   stack     a stack per grid: one band per source the period holds, batteries charging drawn below zero, a demand line
//   side      two grids side by side when a second is named, one when not; a period the second grid lacks says so
//   years     one line per year of the calendar month, the table's low, high and ramp from net load
//   records   each record with its value and its local hour; California's with the side it rests on
//   join      California states the join and the side of the period shown; another grid does not
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as m from "../lib/mix2.ts";

const base = (process.argv[2] ?? "http://localhost:3094").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const F = Object.fromEntries(m.GRIDS.map((g) => [g.slug, JSON.parse(fs.readFileSync(new URL(`../data/mix/${g.slug}.json`, import.meta.url), "utf-8"))]));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1].replace(/&amp;/g, "&"), x[2]]));
const stacks = (html) => [...html.matchAll(/<svg[^>]*data-stack="([^"]+)"[\s\S]*?<\/svg>/g)].map((x) => ({ name: x[1], bands: [...x[0].matchAll(/data-band="([a-z_]+)"/g)].map((b) => b[1]), demand: x[0].includes('data-line="demand"') }));

async function view(grid, period, vs) {
  const path = m.href({ grid, period, vs });
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const got = marked(html), file = F[grid], p = m.periodOf(file, period), other = vs ? F[vs] : null, po = other ? m.periodOf(other, period) : null;
  const sh = m.shares(p);
  let wrong = [];
  const want = (k, v) => { if (got[k] !== v) wrong.push(`${k}: page ${got[k]}, copy ${v}`); };
  sh.slice(0, 3).forEach((s, i) => want(`share|${i}`, m.two(s.share)));
  want("head|largest", m.two(sh[0].share));
  want("head|largest|mwh", m.whole(sh[0].mwh));
  want("head|solar", m.two(p.solar_share_pct));
  want("head|wind", m.two(p.wind_share_pct));
  const sp = m.highest(p.avg.solar);
  if (sp && sp.value > 0) { want("solar|peak", m.whole(sp.value)); want("head|solar|peak", m.whole(sp.value)); }
  for (const s of m.SOURCES) {
    want(`${grid}|${s.key}_share_pct`, m.two(p[`${s.key}_share_pct`]));
    want(`${grid}|${s.key}_mwh`, m.whole(p[`${s.key}_mwh`]));
    if (po) { want(`${vs}|${s.key}_share_pct`, m.two(po[`${s.key}_share_pct`])); want(`${vs}|${s.key}_mwh`, m.whole(po[`${s.key}_mwh`])); }
  }
  const year = period.slice(0, 4);
  for (const f of [file, ...(other ? [other] : [])]) {
    for (const row of m.RECORD_ROWS) for (const per of ["all", year]) {
      const r = m.recordOf(f, row.variable, per);
      if (r) want(`${f.grid}|${r.variable}|${r.period}`, m.two(r.value));
    }
  }
  const cal = period.length === 7 ? period.slice(5) : "04";
  for (const d of m.acrossYears(file, cal)) {
    if (d.solarPeak && d.solarPeak.value > 0) want(`duck|${d.year}|solar`, m.whole(d.solarPeak.value));
    if (d.low) want(`duck|${d.year}|low`, m.whole(d.low.value));
    if (d.evening) want(`duck|${d.year}|evening`, m.whole(d.evening.value));
    if (d.ramp !== null) want(`duck|${d.year}|ramp`, m.whole(d.ramp));
  }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const st = stacks(html);
  const model = m.stack(p);
  check(st.length === (po ? 2 : 1) && st[0].bands.join() === [...model.up, ...model.down].map((b) => b.key).join() && st[0].demand,
    `${tag} ${st.length} stack${st.length === 1 ? "" : "s"}; the first has a band per source held (${st[0]?.bands.join(", ")}) and the demand line`);
  check(html.includes(`data-side-by-side="${other ? 1 : 0}"`), `${tag} side by side: ${other ? "two grids" : "one grid"}`);
  const lines = [...html.matchAll(/data-year="(\d{4})"/g)].map((x) => x[1]);
  const duck = m.acrossYears(file, cal).map((d) => d.year);
  check(duck.every((y) => lines.includes(y)), `${tag} ${m.calName(cal)} across the years: a line for each of ${duck.join(", ")}`);
  const t = text(html);
  for (const row of m.RECORD_ROWS) {
    const r = m.recordOf(file, row.variable, "all");
    if (r && !t.includes(m.localHour(r.ts_utc, file.tz))) { check(false, `${tag} the record "${row.label}" is dated ${m.localHour(r.ts_utc, file.tz)}`); }
  }
  check(m.RECORD_ROWS.every((row) => t.includes(row.label)), `${tag} the five records are named`);
  const ca = grid === "caiso" || vs === "caiso";
  check(html.includes('data-caiso-join="1"') === ca, `${tag} the join is ${ca ? "stated" : "not mentioned"}`);
  if (ca && m.periodOf(F.caiso, period)) check(html.includes(`data-side="${m.periodOf(F.caiso, period).side}"`), `${tag} the period rests on ${m.sideName(m.periodOf(F.caiso, period).side)}, and the page says so`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
  return { html, t };
}

await view("caiso", "2026-04", "ercot");
await view("caiso", "2025-04");
await view("ercot", "2021-02");
await view("pjm", "2024");
await view("spp", "2025", "miso");
{
  const { t } = await view("nyiso", "2026-07");
  check(t.includes("EIA reports no solar output for it") && t.includes("No solar output is reported"), "New York: no solar is reported, said in words, not as a zero record");
}
{
  // a period the second grid lacks: California holds no November 2019
  const { status, html } = await get(m.href({ grid: "ercot", period: "2019-11", vs: "caiso" }));
  check(status === 200 && html.includes('data-other="none"') && stacks(html).length === 1, "a period the second grid lacks: one stack and a sentence, no filled chart");
}
{
  // an address the page does not understand opens the default
  const { status, html } = await get("/mix/v2?grid=nowhere&period=1999-01&vs=ercot&cal=44");
  const latest = Object.keys(F.ercot.months).sort().at(-1);
  check(status === 200 && html.includes(`ERCOT, ${m.periodName(latest)}`) && html.includes('data-side-by-side="0"'), `an address it does not understand opens ERCOT's latest month (${latest})`);
}
{
  const t = text((await get("/mix/v2?grid=caiso")).html);
  const miss = m.missingMonths(F.caiso);
  check(t.includes(`does not hold ${miss.length} of the months`) && t.includes("November 2019"), `what is not held: California's ${miss.length} months are named`);
}
{
  const { status, html } = await get("/mix/v2?grid=caiso&period=2026-04", false);
  check(status === 200 && html.includes('data-in-review="1"') && !html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
  const old = await get("/mix");
  check(old.status === 200 && !old.html.includes("data-stack="), "/mix is the page as it was");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
