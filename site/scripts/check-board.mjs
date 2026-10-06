// Energy Research Warehouse (ERW) site, session 132: the price board and its markets workbench, on the built site.
//
//   npm run build && npx next start -p 3132
//   node --import ./scripts/alias-loader.mjs scripts/check-board.mjs [base-url]      (default http://localhost:3132)
//
// As HTML, in the internal view (the page is in review):
//   numbers     every number the page marks (data-n) equals the site's file (data/board.json): each row's latest value,
//               its moves, its 7-day and 30-day means and the ends of its range, for the rows the default filters show
//   rows        every group is on the page with its default rows; a trend line and a range bar for each row that holds them
//   blanked     MISO rows are on the page with "paused while terms are reviewed" and no number; PJM rows with
//               "licensed source needed"; the futures curve beside the spot rows is greyed
//   no method   the page face carries no methodology words; it links to its Method note
//   retired     /markets, /board/v3 and /board/v4 redirect to /board
//   visitor     without the cookie the page is the in-review page and carries no number
// In a real browser (the machine's Chrome or Edge):
//   workbench   a click on a row opens the workbench beside the tables and writes the row to the address; a power hub
//               opens on seven days by the hour with real time against day-ahead, on-peak and off-peak and the spikes;
//               Expand makes it full width; the address alone reopens the same view; an overlay draws the spread
//   hover       a trend line answers the mouse with a value, a date and the series
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as b from "../lib/board.ts";

const base = (process.argv[2] ?? "http://localhost:3132").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true, redirect = "follow") => { const r = await fetch(base + path, { redirect, headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text(), location: r.headers.get("location"), url: r.url }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span[^>]*data-n="([^"]+)"[^>]*>([^<]*)</g)].map((x) => [x[1].replace(/&amp;/g, "&"), x[2]]));

const { status, html } = await get("/board");
check(status === 200 && html.includes('data-board="1"') && !html.includes('data-in-review="1"'), "/board opens in the internal view");
const got = marked(html), wrong = [];
const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, file ${val}`); };
let shown = 0, sparks = 0, ranges = 0;
for (const g of file.groups) {
  const rows = b.rowsOf(file, g, {});
  const m = html.match(new RegExp(`data-count="${g.id}"[^>]*>(\\d+)`));
  if (!m || Number(m[1]) !== rows.length) wrong.push(`${g.id}: the page counts ${m?.[1]} rows, the file's default filters give ${rows.length}`);
  for (const r of rows) {
    if (r.group !== g.id) continue;          // a row listed in a second group is checked in its own
    if (!html.includes(`data-row="${r.id}"`)) { wrong.push(`${r.id}: no row`); continue; }
    if (r.status !== "ok") continue;
    shown += 1;
    want(`${r.id}|last`, b.fmt(r.last.v, r.unit));
    for (const [k] of b.MOVES) { const mv = r.moves[k]; if (mv) want(`${r.id}|${k}`, b.signed(mv.ch, r.unit)); else if (`${r.id}|${k}` in got) wrong.push(`${r.id}|${k}: on the page, not in the file`); }
    if (r.avg7) want(`${r.id}|avg7`, b.fmt(r.avg7.v, r.unit));
    if (r.avg30) want(`${r.id}|avg30`, b.fmt(r.avg30.v, r.unit));
    if (r.range && r.range.pos !== null) { ranges += 1; want(`${r.id}|lo`, b.fmt(r.range.lo, r.unit)); want(`${r.id}|hi`, b.fmt(r.range.hi, r.unit)); }
    if (r.spark && r.spark.v.length > 1) sparks += 1;
  }
}
check(wrong.length === 0, `every marked number of the ${shown} rows shown is the file's (${Object.keys(got).length} marked)${wrong.length ? `: ${wrong.slice(0, 6).join("; ")}` : ""}`);
check([...html.matchAll(/data-spark="/g)].length === sparks + [...new Set(file.rows.filter((r) => r.also).map((r) => r.id))].length, `${sparks} trend lines drawn, one for each row shown that holds two points`);
check([...html.matchAll(/data-range="/g)].length >= ranges, `${ranges} one-year range bars drawn`);
const t = text(html);
const blank = (id) => { const m = html.match(new RegExp(`<tr[^>]*data-row="${id}"[\\s\\S]*?</tr>`)); return m ? m[0] : ""; };
const miso = blank("miso-indiana-hub-da"), pjm = blank("pjm-western-hub-da");
check(miso.includes("paused while terms are reviewed") && !/data-n=/.test(miso) && t.includes("MISO Indiana hub"), "MISO's rows are on the page, blank, with \"paused while terms are reviewed\"");
check(pjm.includes("licensed source needed") && !/data-n=/.test(pjm) && t.includes("PJM Western hub"), "PJM's rows are on the page, blank, with \"licensed source needed\"");
check(!Object.keys(got).some((k) => /^(miso|pjm)-/.test(k)) && !file.rows.some((r) => /^(miso|pjm)-/.test(r.id) && (r.last || r.spark)), "no figure of MISO's or PJM's prices, on the page or in the file");
const greyed = file.rows.filter((r) => r.status === "licensed" && !/^(miso|pjm)-/.test(r.id));
check(greyed.length >= 14 && greyed.every((r) => r.note && /supply|Source|permission/.test(r.note)), `${greyed.length} greyed rows, each naming the source that would supply it`);
check([...html.matchAll(/data-curve="/g)].length >= 4 && html.includes("5 April 2024"), "the futures curve beside the spot rows is greyed, with its reason on hover");
check(file.rows.filter((r) => r.formula).every((r) => !html.includes(`data-row="${r.id}"`) || html.includes("Formula: ")), "a spread's formula is on hover");
const face = /\b(methodology|limitations?|disputed|What is on this board|How to read)\b|not held:/i.exec(t);
check(!face && t.includes("Method, sources and gaps"), `no methodology on the page face; the Method note is named in the header${face ? ` (found "${face[0]}")` : ""}`);
check(t.includes("ERCOT since 2015: the peak premium explorer") && !t.includes("Real-time annual mean, HB_HUBAVG"), "ERCOT since 2015 is a link to the explorer, not a section");
check(/WTI crude oil/.test(t) && /Brent crude oil/.test(t) && /Brent minus WTI/.test(t), "WTI, Brent and the gap between them are three rows");
check(!/\bundefined\b|NaN/.test(t), 'no "undefined" and no NaN in the text');
for (const old of ["/markets", "/board/v3", "/board/v4"]) {
  const r = await get(old, true, "manual");
  check((r.status === 308 || r.status === 301) && /\/board$/.test(r.location ?? ""), `${old} redirects to /board (${r.status})`);
}
const v = await get("/board", false);
check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the board");

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open }) => {
  await open(base);
  await go(`${base}/board`);
  await wait(`!!document.querySelector('[data-board][data-ready="1"]')`, 15000, "the board");
  await evaluate(`document.querySelector('tr[data-row="ercot-hb-hubavg-da"]').click()`);
  await wait(`!!document.querySelector('[data-workbench="ercot-hb-hubavg-da"] [data-chart="price"] canvas')`, 30000, "the workbench's chart");
  check((await evaluate("location.search")).includes("s=ercot-hb-hubavg-da"), "a click on a row opens the workbench and writes the row to the address");
  check(await evaluate(`(() => { const w = document.querySelector('[data-workbench]').getBoundingClientRect(), tb = document.querySelector('[data-group="power"]').getBoundingClientRect(); return innerWidth < 1280 || w.left >= tb.right - 4; })()`), "the workbench sits beside the tables");
  await wait(`document.querySelectorAll('[data-stats] tbody tr').length >= 3`, 15000, "the window's table");
  const stats = await evaluate(`[...document.querySelectorAll('[data-stats] tbody tr')].map((r) => r.innerText.replace(/\\s+/g, ' '))`);
  check(stats.length === 3 && /day-ahead/.test(stats[0]) && /real time/.test(stats[1]) && /minus/.test(stats[2]), `a power hub opens on day-ahead against real time with the spread between them (${stats.length} lines)`);
  const hours = await evaluate(`[...document.querySelectorAll('[data-stats] tbody tr')].map((r) => Number(r.lastElementChild.innerText.replace(/,/g, '')))`);
  check(hours[0] > 100 && hours[0] <= 168 && await evaluate(`[...document.querySelectorAll('[data-stats] thead th')].some((x) => /on-peak/i.test(x.innerText))`), `seven days by the hour (${hours[0]} hours), with on-peak and off-peak means`);
  check(await evaluate(`document.querySelectorAll('[data-spikes] li').length`) === 10 && await evaluate(`!!document.querySelector('[data-week="ercot-hb-hubavg"]')`), "the ten highest hours and the week's table are shown");
  await evaluate(`[...document.querySelectorAll('[data-workbench] button')].find((x) => x.innerText === 'Expand').click()`);
  await wait(`location.search.includes('x=1')`, 5000, "the expanded address");
  check(await evaluate(`(() => { const w = document.querySelector('[data-workbench]').getBoundingClientRect(), bd = document.querySelector('[data-board]').getBoundingClientRect(); return w.width > bd.width * 0.9; })()`), "Expand makes the workbench full width");
  // an address alone reopens a view: Henry Hub over five years with WTI laid over it and the ratio between them
  await go(`${base}/board?s=eia-wti-cushing-spot&o=eia-henry-hub-spot&m=ratio&w=5y`);
  await wait(`!!document.querySelector('[data-workbench="eia-wti-cushing-spot"] [data-chart="price"] canvas') && document.querySelectorAll('[data-stats] tbody tr').length === 3`, 30000, "the shared view");
  const shared = await evaluate(`[...document.querySelectorAll('[data-stats] tbody tr')].map((r) => r.innerText.replace(/\\s+/g, ' '))`);
  check(/WTI/.test(shared[0]) && /Henry Hub/.test(shared[1]) && / over /.test(shared[2]), "an address alone reopens the view: two series and the ratio between them");
  await go(`${base}/board?s=eia-henry-hub-spot&v=season`);
  await wait(`!!document.querySelector('[data-chart="season"] canvas')`, 30000, "the prior-years chart");
  check(true, "this year against prior years is drawn");
  await go(`${base}/board?s=ercot-hb-hubavg-rt&v=dist&w=1m&th=100`);
  await wait(`!!document.querySelector('[data-dist]') && !!document.querySelector('[data-chart="dist"] canvas')`, 30000, "the distribution");
  const dist = await evaluate(`document.querySelector('[data-dist]').innerText.replace(/\\s+/g, ' ')`);
  check(/above 100/i.test(dist) && /below zero/i.test(dist) && /On-peak mean/i.test(dist) && /volatility/i.test(dist), "the distribution block: hours above the threshold, below zero, on-peak and off-peak, volatility");
  // a trend line answers the mouse
  await go(`${base}/board`);
  await wait(`!!document.querySelector('[data-board][data-ready="1"] [data-spark="eia-henry-hub-spot"] svg')`, 15000, "a trend line");
  const tip = await evaluate(`(() => { const s = document.querySelector('[data-spark="eia-henry-hub-spot"] svg'); const r = s.getBoundingClientRect(); s.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: r.left + r.width / 2, clientY: r.top + 5 })); return new Promise((ok) => setTimeout(() => ok(document.querySelector('[data-spark="eia-henry-hub-spot"] [role=tooltip]')?.innerText ?? ''), 200)); })()`);
  check(/Henry Hub/.test(tip) && /\d+\.\d\d/.test(tip) && /20\d\d/.test(tip), `a trend line answers the mouse with the series, a value and a date ("${tip.replace(/\s+/g, " ")}")`);
  await evaluate(`document.querySelector('[data-filter="power.scope.all"]').click()`);
  await wait(`document.querySelectorAll('[data-group="power"] tbody tr').length > 60`, 5000, "every hub and zone");
  check((await evaluate("location.search")).includes("power.scope=all"), "a filter shows every hub and zone and is kept in the address");
  return 0;
});
if (code === null) console.log("not proven here: no browser on this machine (the HTML checks above stand)");
console.log(`${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
