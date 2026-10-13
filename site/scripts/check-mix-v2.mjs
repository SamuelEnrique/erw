// Energy Research Warehouse (ERW) site, session 94: the energy mix, version 2, on the built site.
//
//   npm run build && npx next start -p 3094
//   node scripts/check-mix-v2.mjs [base-url]      (default http://localhost:3094)
//
// Session 241 (batch C): rewritten for where version 2 is today. The page /mix/v2 was retired by session 133 and its
// address redirects, since session 237 in one step, to the Mix view of the Grid tool (/grid?view=mix&mix=day, with its
// grid, period and second grid carried). Until this session the script looked for marks only the retired page wrote
// (data-n, data-stack, data-side-by-side, data-caiso-join, data-year, data-other) and could not pass on any build since
// session 133. Each thing it checked is checked where it is now, through the old address:
//   numbers   every share and MWh by source of the period, for the grid and the second grid, equals the site's copy of
//             the two tables (data/mix/<grid>.json), written as the Mix view writes them (one decimal, whole MWh); the
//             largest source and solar at its peak hour too
//   stack     one stack per grid drawn (data-chart="stack"); the bands and the demand line are drawn on a canvas now
//             and are read in a real browser by check-mix.mjs, not here
//   side      two grids side by side when a second is named, one when not
//   years     the view "Year after year": a row per year of the calendar month, with the table's solar peak, net load's
//             low and evening high and the ramp between them
//   records   the view "Records": each of version 2's five records with its value and its local hour
//   join      California's period says "from CAISO's own data" when the period rests on CAISO's side, and not otherwise
//   visitor   without the cookie the old address ends on the in-review page and carries nothing of the mix
// Gone, and so not checked: version 2's sentence for a period the second grid lacks (the Mix view draws California's
// November 2019 from CAISO's own data), its opening of ERCOT's latest month for an address it did not understand (the
// Mix view keeps the period asked and writes "not held yet"), its count of California's missing months, and New York's
// sentence about solar (the Mix view leaves the source out of the table and writes "not held yet" for its peak).
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
const get = async (path, withCookie = true, redirect = "follow") => { const r = await fetch(base + path, { redirect, headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text(), location: r.headers.get("location") ?? "", url: r.url }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const n0 = (v) => Math.round(v).toLocaleString("en-US");
const n1 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const held = (v) => typeof v === "number" && Number.isFinite(v);
const old = ({ grid, period, vs }) => `/mix/v2?grid=${grid}${period ? `&period=${period}` : ""}${vs ? `&vs=${vs}` : ""}`;

async function view(grid, period, vs) {
  const path = old({ grid, period, vs });
  const tag = `${path}:`;
  // the old address answers a permanent redirect to the Mix view, its words carried
  const first = await get(path, true, "manual");
  const [to, query = ""] = first.location.replace(/^https?:\/\/[^/]+/, "").split("?");
  const words = ["view=mix", "mix=day", `grid=${grid}`, `period=${period}`, ...(vs ? [`vs=${vs}`] : [])];
  check((first.status === 308 || first.status === 301) && to === "/grid" && words.every((w) => query.split("&").includes(w)), `${tag} redirects to the Mix view of /grid and carries its words (${first.status} ${first.location})`);
  const { status, html } = await get(path);
  check(status === 200 && html.includes('data-mix="day"') && !html.includes('data-in-review="1"'), `${tag} opens the average day in the internal view`);
  const t = text(html);
  const file = F[grid], p = m.periodOf(file, period), other = vs ? F[vs] : null, po = other ? m.periodOf(other, period) : null;
  // numbers: each source's share and MWh, for each grid drawn, as the copy has them
  const wrong = [];
  let figures = 0;
  for (const [slug, q] of [[grid, p], ...(po ? [[vs, po]] : [])]) {
    for (const s of m.SOURCES) {
      const share = q[`${s.key}_share_pct`], mwh = q[`${s.key}_mwh`];
      if (!held(share) || !held(mwh)) continue;
      figures += 2;
      if (!t.includes(`${n1(share)}% ${n0(mwh)}`)) wrong.push(`${slug} ${s.key}: ${n1(share)}% ${n0(mwh)} is not on the page`);
      if (!t.includes(s.label)) wrong.push(`${s.label}: not named`);
    }
    const sh = m.shares(q);
    if (sh.length && !t.includes(`${sh[0].label} ${n1(sh[0].share)}%`)) wrong.push(`${slug}: the largest source, ${sh[0].label} ${n1(sh[0].share)}%, is not on the page`);
    const sp = m.highest(q.avg.solar);
    if (sp && sp.value > 0) { figures += 1; if (!t.includes(n0(sp.value))) wrong.push(`${slug}: solar at its peak, ${n0(sp.value)} MW, is not on the page`); }
  }
  check(figures > 8 && wrong.length === 0, `${tag} each of the ${figures} figures of the period is the copy's${wrong.length ? `: ${wrong.slice(0, 4).join("; ")}` : ""}`);
  // a stack per grid, side by side when a second grid is named
  const stacks = (html.match(/data-chart="stack"/g) ?? []).length;
  check(stacks === (po ? 2 : 1), `${tag} ${stacks} stack${stacks === 1 ? "" : "s"} drawn: ${po ? "two grids side by side" : "one grid"}`);
  // the join: California's period, by the side it rests on
  const ca = grid === "caiso" ? p : vs === "caiso" ? po : null;
  check(t.includes("CAISO, from CAISO's own data") === (!!ca && ca.side === "caiso"), `${tag} ${ca ? `California's period rests on ${m.sideName(ca.side)}, and the page ${ca.side === "caiso" ? "says so" : "does not say CAISO's own data"}` : "no word of California's own data"}`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
  return { html, t };
}

await view("caiso", "2026-04", "ercot");
await view("caiso", "2025-04");
await view("ercot", "2021-02");
await view("pjm", "2024");
await view("spp", "2025", "miso");
await view("nyiso", "2026-07");
await view("ercot", "2019-11", "caiso");   // version 2 had no November 2019 for California; the Mix view draws it from CAISO's own data
{
  // year after year: a row per year of the calendar month, with the figures version 2's table held
  const { status, html } = await get("/grid?grid=caiso&view=mix&mix=duck&cal=04");
  const t = text(html), wrong = [];
  const duck = m.acrossYears(F.caiso, "04");
  for (const d of duck) {
    const row = [d.year, d.solarPeak && d.solarPeak.value > 0 ? n0(d.solarPeak.value) : null, d.low ? n0(d.low.value) : null, d.evening ? n0(d.evening.value) : null, d.ramp !== null ? n0(d.ramp) : null];
    const at = t.indexOf(`${d.year} ${row[1] ?? ""}`.trim() + " ");
    const line = at < 0 ? "" : t.slice(at, at + 90);
    if (at < 0 || row.slice(1).some((v) => v !== null && !line.includes(v))) wrong.push(`${d.year}: ${row.slice(1).join(", ")} (the page: "${line}")`);
  }
  check(status === 200 && html.includes('data-mix="duck"') && duck.length > 3 && wrong.length === 0, `April across the years, California: a row for each of ${duck.map((d) => d.year).join(", ")}, each with the copy's solar peak, low, evening high and ramp${wrong.length ? `: ${wrong.slice(0, 3).join("; ")}` : ""}`);
  check((html.match(/data-chart="lines"/g) ?? []).length === 2, "year after year: net load and solar, a chart of lines each");
}
{
  // the records: each of version 2's five, with its value and its local hour
  const { status, html } = await get("/grid?grid=caiso&view=mix&mix=records");
  const t = text(html), wrong = [];
  for (const row of m.RECORD_ROWS) {
    const r = m.recordOf(F.caiso, row.variable, "all");
    if (!t.includes(row.label)) wrong.push(`"${row.label}" is not named`);
    else if (r && !t.includes(`${n1(r.value)} ${m.localHour(r.ts_utc, F.caiso.tz)}`)) wrong.push(`"${row.label}": ${n1(r.value)} at ${m.localHour(r.ts_utc, F.caiso.tz)} is not on the page`);
  }
  check(status === 200 && html.includes('data-mix="records"') && wrong.length === 0, `the records, California: version 2's five are named, each with the copy's value and local hour${wrong.length ? `: ${wrong.join("; ")}` : ""}`);
}
{
  const first = await get("/mix/v2?grid=caiso&period=2026-04", false, "manual");
  const v = await get("/mix/v2?grid=caiso&period=2026-04", false);
  check((first.status === 308 || first.status === 301) && v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-chart=") && !v.html.includes('data-mix="'), "as a visitor: the old address redirects and ends on the in-review page, with nothing of the mix");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
