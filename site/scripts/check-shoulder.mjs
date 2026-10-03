// Energy Research Warehouse (ERW) site, session 75: /shoulder as rendered, against shoulder_hours_monthly as built.
//
//   node scripts/check-shoulder.mjs [base-url]     (default http://localhost:3075; see scripts/shoulder-stub.mjs)
//
// For both grids and a spread of months: the page answers 200 with no "no data", "undefined" or "NaN" and no em dash;
// every number's data-raw equals the table's row under its check key and its text is that value as the site writes it;
// the summary sentence, three headline numbers, both charts and the table by year are there. The page is in review, so
// it is read with the internal cookie (the token from the environment or site/.env.local, never printed). Exits 1 on a
// failure.
import fs from "node:fs";
import { shown } from "../lib/shoulder.ts";
import { tableRows, TABLE } from "./shoulder-stub.mjs";

const base = process.argv[2] ?? "http://localhost:3075";
const token = process.env.INTERNAL_COSTS_TOKEN ?? (() => {
  try { return (fs.readFileSync(new URL("../.env.local", import.meta.url), "utf-8").match(/^INTERNAL_COSTS_TOKEN=(.*)$/m)?.[1] ?? "").trim().replace(/^"|"$/g, ""); } catch { return ""; }
})();
const unlock = token ? await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token)}`, { redirect: "manual" }) : null;
const cookie = unlock ? (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ") : "";
let bad = 0, n = 0, values = 0;
const check = (ok, what) => { n++; if (!ok) { bad++; console.log(`FAIL ${what}`); } };
// session 80: a row's key carries its own date (a month's and a year's rows are dated the first of the month; a worst
// day's rows the day)
const truth = new Map(tableRows().map((r) => [`series|${TABLE}|${r.entity}|${r.variable}|${r.ts_utc.slice(0, 10)}T00:00:00Z`, r.value]));
const hasOwn = tableRows().some((r) => r.entity === "iso:caiso_own");
const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
const visible = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
for (const page of ["/shoulder", "/shoulder?grid=ercot&month=2019-07", "/shoulder?grid=ercot&month=2024-01", "/shoulder?grid=caiso&month=2025-07", "/shoulder?grid=caiso&month=2021-04", "/shoulder?grid=caiso",
  ...(hasOwn ? ["/shoulder?grid=caiso-own", "/shoulder?grid=caiso-own&month=2025-09", "/shoulder?grid=caiso-own&month=2026-08"] : [])]) {
  const res = await fetch(base + page, { headers: cookie ? { Cookie: cookie } : {} });
  const html = await res.text();
  const text = visible(html);
  check(res.status === 200, `${page}: status ${res.status}`);
  check(!/\bno data\b/.test(text) && !/\bundefined\b/.test(text) && !/\bNaN\b/.test(text), `${page}: no "no data", "undefined" or "NaN"`);
  check(!html.includes("—"), `${page}: no em dash`);
  const spans = [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)];
  check(spans.length >= 40, `${page}: ${spans.length} checked numbers`);
  for (const m of spans) {
    const key = decode(m[1]), raw = Number(m[2]), t = decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim();
    values++;
    check(truth.has(key) && Math.abs(truth.get(key) - raw) < 1e-9, `${page}: ${key} page read ${m[2]}, table ${truth.get(key)}`);
    check(t.startsWith(shown(raw)) || t.startsWith(String(raw).padStart(2, "0")), `${page}: ${key} shown "${t}", expected "${shown(raw)}"`);
  }
  check(/data-summary="1"/.test(html) && /evening shoulder lasted/.test(text), `${page}: the summary sentence`);
  check(text.includes("The evening shoulder") && text.includes("Hours the battery fleet covers") && text.includes("The midday surplus"), `${page}: three headline numbers`);
  check((html.match(/<svg /g) ?? []).length >= 2, `${page}: both charts`);
  check(text.includes("The shoulder hours by year") || /By year/.test(text), `${page}: the table by year`);
  // session 80: the second section, and the summary's average day and worst days together
  check(text.includes("A shoulder that ends inside the evening, and the worst days") && text.includes("The shoulder, second measure"), `${page}: the second section`);
  check(/on the average day/.test(text) && (/on the ten worst days of \d{4}/.test(text) || /the worst days of \d{4} are not held/.test(text)), `${page}: the summary names the average day and the worst days`);
  const ranked = spans.filter((m) => decode(m[1]).includes("|worst_rank|")).length;
  check(ranked === 10 || (ranked === 0 && /data-worst="none"/.test(html)), `${page}: ten ranked days, or the page says none are held (${ranked})`);
  if (page.includes("caiso-own")) check(ranked === 10, `${page}: California's own data has its ten worst days`);
}
console.log(`/shoulder as rendered: ${n - bad} of ${n} checks pass, ${values} numbers against the table's rows`);
process.exit(bad ? 1 : 0);
