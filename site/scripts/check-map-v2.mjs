// Energy Research Warehouse (ERW) site, session 105: the project map, version 2, in a real browser.
//
//   npm run build && npx next start -p 3105
//   node scripts/check-map-v2.mjs [base-url]      (default http://localhost:3105)
//
// The page's choices, map, totals and table are drawn by the browser, so they are checked in one, in the internal view
// (the page is in review). Every expected figure is computed here from the site's own copy of EIA's inventory
// (data/map_v2.json) and of the queue summary (data/queues.json):
//   opens     every unit selected: the sentence's count and MW, the three totals by status, a map with a canvas, the
//             fifty largest in the table
//   choices   a grid, then a technology, then a status, then a size: after each, the sentence, the totals, the count
//             of units drawn and the table's first row are the file's
//   queue     the queue's active MW beside the map is the queue file's for that grid; the rows that answer to the
//             technology chosen are marked
//   nothing   a choice that selects nothing says so
//   visitor   without the cookie the page is the in-review page
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";
import { queueRows, select, totals, whole, one, EVERY } from "../lib/map2.ts";

const base = (process.argv[2] ?? "http://localhost:3105").replace(/\/$/, "");
const f = JSON.parse(fs.readFileSync(new URL("../data/map_v2.json", import.meta.url), "utf-8"));
const q = JSON.parse(fs.readFileSync(new URL("../data/queues.json", import.meta.url), "utf-8"));
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const set = (name, value) => `(() => { const el = document.querySelector('[data-map-choice="${name}"]'); const proto = el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, ${JSON.stringify(String(value))}); el.dispatchEvent(new Event(el.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true })); return true; })()`;
const STATE = `(() => ({ summary: document.querySelector('[data-map-summary]')?.innerText ?? null,
  totals: Object.fromEntries([...document.querySelectorAll('[data-map-total]')].map((e) => [e.getAttribute('data-map-total'), e.innerText])),
  drawn: Number(document.querySelector('[data-map-drawn]')?.getAttribute('data-map-drawn') ?? -1), canvas: !!document.querySelector('[data-map-drawn] canvas'),
  rows: [...document.querySelectorAll('#table tbody tr')].length, first: document.querySelector('#table tbody tr')?.innerText.replace(/\\s+/g, ' ').trim() ?? null,
  queue: Object.fromEntries([...document.querySelectorAll('[data-queue-mw]')].map((e) => [e.getAttribute('data-queue-mw'), e.innerText])),
  marked: [...document.querySelectorAll('#queue tbody tr.font-semibold th')].map((e) => e.innerText.trim()) }))()`;

function expected(c) {
  const picked = select(f, c);
  const t = totals(f, picked);
  const drawn = picked.filter((i) => f.la[i] !== null && !(f.states[f.s[i]] === "PR")).length;
  const i = picked[0];
  return { picked, t, drawn, first: i === undefined ? null : `${f.names[f.n[i]]} ${f.states[f.s[i]]} ${f.grids[f.g[i]].name} ${f.techs[f.t[i]].name} ${f.statuses[f.st[i]].name} ${one(f.mw[i])} ${f.y[i] || "not stated"}` };
}
async function compare(evaluate, wait, c, label) {
  const e = expected(c);
  const want = e.t.units === 0 ? "No unit of the inventory matches these choices." : null;
  const s = await wait(`(() => { const s = ${STATE}; return s.summary && (${JSON.stringify(want)} ? s.summary === ${JSON.stringify(want)} : s.summary.includes(${JSON.stringify(`${whole(e.t.units)} `)}) && s.summary.includes(${JSON.stringify(`${whole(e.t.mw)} MW`)})) ? s : null; })()`,
    15000, `${label}: the sentence to say ${whole(e.t.units)} units and ${whole(e.t.mw)} MW`).catch(() => null);
  check(!!s, `${label}: the sentence gives the file's ${whole(e.t.units)} units and ${whole(e.t.mw)} MW`);
  if (!s) return null;
  check(f.statuses.every((st, i) => s.totals[st.slug] === whole(e.t.byStatus[i].mw)), `${label}: the three totals by status are the file's (${f.statuses.map((st, i) => `${st.name} ${whole(e.t.byStatus[i].mw)} MW`).join(", ")})`);
  check(s.drawn === e.drawn, `${label}: ${whole(e.drawn)} units are drawn (${s.drawn})`);
  check(s.rows === Math.min(50, e.picked.length), `${label}: the table shows ${Math.min(50, e.picked.length)} rows (${s.rows})`);
  if (e.first) check((s.first ?? "").replace(/\s+/g, " ") === e.first.replace(/\s+/g, " "), `${label}: the table's first row is the largest unit selected (${e.first})`);
  return s;
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock }) => {
  // visitor first: a fresh profile holds no cookie
  await go(`${base}/map/v2`);
  check(await evaluate(`!!document.querySelector('[data-in-review="1"]') && !document.querySelector('[data-map-summary]')`), "a visitor gets the in-review page, with no figure of the map");
  await unlock(base);
  await go(`${base}/map/v2`);
  await wait(`!!document.querySelector('[data-map-summary]')`, 30000, "the page to be ready");
  await wait(`!!document.querySelector('[data-map-drawn] canvas')`, 30000, "the map's canvas");
  const all = { ...EVERY };
  let s = await compare(evaluate, wait, all, "opens");
  check(!!s && s.canvas, "opens: the map is a canvas");
  check(await evaluate(`document.querySelector('[data-map-units]')?.innerText === ${JSON.stringify(whole(f.counts.units))}`), `the header counts the file's ${whole(f.counts.units)} units`);
  const us = queueRows(q.views, "all", "all");
  check(!!s && s.queue[`All regions|all`] === whole(us[0].mw), `opens: the queue beside it is every region's, ${whole(us[0].mw)} MW active`);

  const gi = f.grids.findIndex((g) => g.slug === "ercot"), ti = f.techs.findIndex((t) => t.slug === "battery"), si = f.statuses.findIndex((x) => x.slug === "under_construction");
  await evaluate(set("grid", gi));
  s = await compare(evaluate, wait, { ...all, grid: gi }, "ERCOT");
  const er = queueRows(q.views, "ercot", "all");
  check(!!s && s.queue[`ERCOT|all`] === whole(er[0].mw) && s.marked.length === 0, `ERCOT: the queue beside it is ERCOT's, ${whole(er[0].mw)} MW active, no row marked`);
  await evaluate(set("tech", ti));
  s = await compare(evaluate, wait, { ...all, grid: gi, tech: ti }, "ERCOT, batteries");
  const eb = queueRows(q.views, "ercot", "battery").filter((r) => r.marked).map((r) => r.tech);
  check(!!s && JSON.stringify(s.marked) === JSON.stringify(eb), `ERCOT, batteries: the queue's rows marked are ${eb.join(" and ")} (${s?.marked.join(" and ")})`);
  await evaluate(set("status", si));
  s = await compare(evaluate, wait, { ...all, grid: gi, tech: ti, status: si }, "ERCOT, batteries, under construction");
  await evaluate(set("min", 200));
  s = await compare(evaluate, wait, { ...all, grid: gi, tech: ti, status: si, min: 200 }, "ERCOT, batteries, under construction, 200 MW and more");
  await evaluate(set("max", 0.001));
  await evaluate(set("min", ""));
  s = await compare(evaluate, wait, { ...all, grid: gi, tech: ti, status: si, max: 0.001 }, "a size no unit has");

  // outside the seven ISOs: the queue's two regions, apart
  await evaluate(set("max", ""));
  await evaluate(set("status", -1));
  await evaluate(set("tech", -1));
  const oi = f.grids.findIndex((g) => g.slug === "outside");
  await evaluate(set("grid", oi));
  s = await compare(evaluate, wait, { ...all, grid: oi }, "outside the seven ISOs");
  const out = queueRows(q.views, "outside", "all");
  check(!!s && s.queue[`West, outside the ISOs|all`] === whole(out.find((r) => r.region.startsWith("West") && r.slug === "all").mw)
    && s.queue[`Southeast, outside the ISOs|all`] === whole(out.find((r) => r.region.startsWith("Southeast") && r.slug === "all").mw), "outside the seven ISOs: the queue's West and Southeast are shown apart");
  return bad;
});
if (code === null) { console.log("check-map-v2: NOT PROVEN (no browser on this machine)"); process.exit(0); }
console.log(`the project map, version 2, in a browser: ${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
