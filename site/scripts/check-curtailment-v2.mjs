// Energy Research Warehouse (ERW) site, session 98: curtailment, version 2, on the built site.
//
//   npm run build && npx next start -p 3098
//   node --import ./scripts/alias-loader.mjs scripts/check-curtailment-v2.mjs [base-url]      (default http://localhost:3098)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers    every number the page marks (data-n) equals the site's copy of caiso_curtailment_profile
//              (data/curtailment_profile.json): a year, a month, a year with no reason, a year with part, a month of 2026
//   charts     24 hours of the day; a bar per month held, by fuel and by reason
//   reason     "not published" before 2022; CAISO's three categories only from 2026
//   batteries  the comparison for a month that holds them, the month named when a year is chosen, and "not held"
//              with the months that do when the period has none
//   not located  the sentence is on the page, above the tool; the credit to the California ISO
//   visitor    without the cookie the page is the in-review page and carries no number; /curtailment is as it was
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as c from "../lib/curtailmentv2.ts";

const base = (process.argv[2] ?? "http://localhost:3098").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/curtailment_profile.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((x) => x.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));

async function view(period) {
  const path = c.href(period);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const r = c.periodOf(file, period), got = marked(html), cover = c.reasonCover(r), peak = c.peakHour(r);
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  const absent = (k) => { if (k in got) wrong.push(`${k}: on the page (${got[k]}), not in the copy`); };
  want("sum|solar", c.whole(r.curtailed_solar_mwh));
  want("sum|wind", c.whole(r.curtailed_wind_mwh));
  want("head|solar", c.whole(r.curtailed_solar_mwh));
  want("head|wind", c.whole(r.curtailed_wind_mwh));
  want("head|peak_solar", c.whole(peak.solar));
  want("days_held", c.whole(r.days_held));
  if (cover === "none") { absent("sum|local"); absent("head|local"); } else {
    want("sum|local", c.whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh));
    want("head|system", c.whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh));
  }
  if (cover === "part") want("head|unspecified", c.whole(r.curtailed_solar_unspecified_mwh + r.curtailed_wind_unspecified_mwh)); else absent("head|unspecified");
  for (const f of c.FUELS) {
    for (const x of c.REASONS) want(`reason|${f.key}|${x.key}`, c.whole(r[`curtailed_${f.key}_${x.key}_mwh`] ?? 0));
    want(`reason|${f.key}|all`, c.whole(r[`curtailed_${f.key}_mwh`]));
    for (const k of c.CATS) { if (c.hasCats(r)) want(`cat|${f.key}|${k.key}`, c.whole(r[`curtailed_${f.key}_${k.key}_mwh`] ?? 0)); else absent(`cat|${f.key}|${k.key}`); }
  }
  const bm = c.batteryMonths(file);
  const battMonth = period.length === 7 ? (c.hasBattery(r) ? period : null) : bm.filter((m) => m.startsWith(period)).at(-1) ?? null;
  if (battMonth) {
    const b = file.months[battMonth];
    want("batt|curtailed", c.whole(b.curtailed_mwh_battery_days));
    want("batt|charging", c.whole(b.battery_charging_mwh));
    want("batt|days", c.whole(b.battery_days_held));
    if (b.curtailed_while_charging_share_pct !== undefined) { want("batt|while", c.two(b.curtailed_while_charging_share_pct)); want("sum|while", c.two(b.curtailed_while_charging_share_pct)); }
  } else { absent("batt|curtailed"); absent("sum|while"); }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const hours = [...html.matchAll(/data-hour="(\d+)"/g)].length;
  const months = Object.keys(file.months).length;
  const drawn = [...html.matchAll(/data-month="(\d{4}-\d\d)"/g)].length;
  check(hours === 24 && drawn === 2 * months && html.includes('data-chart="months-fuel"') && html.includes('data-chart="months-reason"'), `${tag} 24 hours of the day, and ${months} months drawn by fuel and by reason`);
  const t = text(html);
  check((cover === "none") === t.includes("CAISO published no reason for it then") && c.hasCats(r) === html.includes('data-cats="1"'), `${tag} reason ${cover === "none" ? "not published, said so" : cover === "part" ? "published for part" : "published"}; CAISO's categories ${c.hasCats(r) ? "shown" : "not shown"}`);
  check(battMonth ? html.includes('data-chart="battery"') && (period === battMonth || html.includes(`data-battery-month="${battMonth}"`)) : html.includes('data-battery="none"') && !html.includes('data-chart="battery"'),
    `${tag} the batteries: ${battMonth ? `compared for ${battMonth}` : "not held for this period, with the months that are"}`);
  check(html.includes('data-not-located="1"') && t.indexOf("The data does not say where.") > 0 && t.indexOf("The data does not say where.") < t.indexOf("By hour of the day") && t.includes("Credit: California ISO"), `${tag} "the data does not say where", above the tool, and the credit`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
}

for (const p of ["2025", "2019", "2022", "2026", "2024-04", "2026-05", "2025-09", "2026-03"]) await view(p);
{
  const d = await get("/curtailment/v2?period=1999-13");
  const newest = Object.keys(file.years).sort().at(-1);
  check(d.status === 200 && marked(d.html)["head|solar"] === c.whole(file.years[newest].curtailed_solar_mwh), `an address it does not understand opens the newest year (${newest})`);
  const t = text(d.html);
  check(file.days_not_held.every((x) => t.includes(x)), `the day${file.days_not_held.length === 1 ? "" : "s"} not held (${file.days_not_held.join(", ")}) named on the page`);
  const v = await get(c.href("2025"), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
  const old = await get("/curtailment");
  check(old.status === 200 && !old.html.includes('data-not-located="1"') && !old.html.includes('data-chart="hours"'), "/curtailment is the page as it was");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
