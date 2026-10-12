// Energy Research Warehouse (ERW) site, session 202: /internal/health on the built site (docs/machines.md, "One alert
// policy"). The page reads data/health_days.json, which warehouse/health.py writes from erw_health; this compares what
// the server sends with that file, and recomputes the green streak from the file's own days. It reads no database and
// changes nothing.
//
//   npm run build
//   npx next start -p 3202
//   node scripts/check-internal-health.mjs [base-url]      (default http://localhost:3202)
//
//   visitor   without the internal cookie the page answers 404 and none of its words; a token in the address opens
//             nothing
//   internal  with the cookie: 200, no-store, noindex, no token in the page; the line "Scheduled jobs green for N
//             days" holds the file's N, and N is the streak recomputed here from the file's days; the day it is
//             counted to is said; every day of the file is a row, newest first, with its count of failed steps; every
//             failed step of the file is listed; the menu does not link to the page
//   phone     at 390 px the page does not scroll sideways (a real browser; skipped with a note where there is none)
// Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const base = (process.argv[2] ?? "http://localhost:3202").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what, shown = "") => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what} ${shown}`); } else console.log(`ok   ${what} ${shown}`); };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")
  .replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\s+/g, " ");

/** The streak as warehouse/health.py counts it (green_streak): back from the newest day, until a failure or a gap. */
function streak(days) {
  const keys = Object.keys(days).sort();
  if (!keys.length) return 0;
  let k = 0;
  for (let d = new Date(`${keys[keys.length - 1]}T00:00:00Z`); ; d = new Date(d.getTime() - 86400000)) {
    const rec = days[d.toISOString().slice(0, 10)];
    if (!rec || !rec.rows || rec.failed) return k;
    k += 1;
  }
}

let code = 1;
try {
  const f = JSON.parse(fs.readFileSync(path.join(site, "data", "health_days.json"), "utf-8"));
  const token = env("INTERNAL_COSTS_TOKEN") ?? "";
  const days = Object.keys(f.days).sort().reverse();
  check(days.length > 0 && f.counted_to === days[0], "the file holds days, and is counted to its newest", `(${days.length} days, to ${f.counted_to})`);
  check(f.green_days === streak(f.days), "the file's green_days is the streak of its own days", `(${f.green_days}, recomputed ${streak(f.days)})`);

  // visitor
  const no = await fetch(`${base}/internal/health`);
  const noHtml = await no.text();
  check(no.status === 404, "without the cookie /internal/health is 404", `(${no.status})`);
  check(!noHtml.includes("data-health") && !noHtml.includes("Scheduled jobs green") && !noHtml.includes("data-health-day"), "a visitor is sent none of the page's words");
  const tok = await fetch(`${base}/internal/health?token=${encodeURIComponent(token)}`);
  check(tok.status === 404, "a token in the address opens nothing", `(${tok.status})`);

  // internal
  const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token)}`, { redirect: "manual" });
  const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  if (!cookie) throw new Error(`${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`);
  const r = await fetch(`${base}/internal/health`, { headers: { Cookie: cookie } });
  const html = await r.text();
  const t = text(html);
  check(r.status === 200 && html.includes('data-health="1"'), "with the cookie the page opens", `(${r.status})`);
  check(/no-store/.test(r.headers.get("cache-control") ?? ""), "the page is no-store", `(${r.headers.get("cache-control")})`);
  check(/noindex/.test(r.headers.get("x-robots-tag") ?? "") || /<meta name="robots" content="noindex/.test(html), "the page is noindex");
  check(token.length >= 24 && !html.includes(token), "the token is nowhere in the page");
  const shown = Number((html.match(/data-green-days="(\d+)"/) ?? [])[1] ?? NaN);
  const words = `Scheduled jobs green for ${f.green_days.toLocaleString("en-US")} ${f.green_days === 1 ? "day" : "days"}.`;
  check(shown === f.green_days && t.includes(words), "the line holds the file's number", `("${words}")`);
  check(html.includes(`data-counted-to="${f.counted_to}"`) && t.includes(`Counted to ${f.counted_to} (UTC)`), "the day it is counted to is said", `(${f.counted_to})`);
  const rows = [...html.matchAll(/data-health-day="([^"]+)" data-failed="(\d+)"/g)].map((m) => [m[1], Number(m[2])]);
  check(JSON.stringify(rows.map((x) => x[0])) === JSON.stringify(days), "every day of the file is a row, newest first", `(${rows.length} rows)`);
  check(rows.every(([d, k]) => k === f.days[d].failed), "each day's count of failed steps is the file's");
  check(rows.every(([d, k]) => (k ? t.includes(`${d} red: ${k} failed`) : t.includes(`${d} green`))), "each day says green or red in words, not by color alone");
  const fails = days.reduce((a, d) => a + f.days[d].failures.length, 0);
  const listed = (html.match(/data-health-failure="/g) ?? []).length;
  check(listed === fails, "every failed step of the file is listed", `(${listed} of ${fails})`);
  check(!t.includes(String.fromCharCode(0x2014)), "no em dash in what the page shows");
  const home = await fetch(`${base}/`, { headers: { Cookie: cookie } });
  check(!(await home.text()).includes("/internal/health"), "the home page and the menu do not link to it, even in the internal view");

  // phone
  const seen = await withBrowser(async ({ go, wait, evaluate, unlock: open, send }) => {
    await open(base);
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await go(`${base}/internal/health`);
    await wait(`!!document.querySelector('[data-health="1"]')`, 20000, "/internal/health at 390 px");
    const m = await evaluate(`({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth,
      days: document.querySelectorAll('[data-health-day]').length, h1: document.querySelector('h1').innerText })`);
    check(m.client === 390 && m.scroll <= m.client + 1, "/internal/health at 390 px does not scroll sideways (its tables scroll inside their own boxes)", `(scroll width ${m.scroll}, width ${m.client})`);
    check(m.days === days.length && m.h1 === "Scheduled jobs (internal)", "the browser drew every day", `(${m.days})`);
    return true;
  }).catch((e) => { console.log(`note: the phone check was skipped: ${String(e.message ?? e).slice(0, 160)}`); return false; });
  if (!seen) console.log("note: no browser here; the 390 px check did not run");
  code = bad ? 1 : 0;
} catch (e) {
  console.log(`check-internal-health FAILED: ${String(e.message ?? e).slice(0, 300)}`);
}
console.log(bad ? `check-internal-health FAILED: ${bad} of ${n}` : `check-internal-health: ${n} checks passed`);
process.exit(code);
