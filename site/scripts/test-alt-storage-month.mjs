// Energy Research Warehouse (ERW) site, ruling alternative 1 of /storage (wip/alt-storage-1, not a default on main),
// session 8401 (chain 503), browser row 363: every cell of "Discharged, newest whole month" read "no whole month". The
// column was summed from the panel's own read, the last 45 days of storage_daily_cycle: on 17 November that read starts
// on 3 October, so October lacks its first two days and no calendar month is whole in it, whatever the table holds.
// The column has a read of its own now, from the first day of the month two before (lib/storagemonth.ts, monthSince).
//
// /storage is drawn whole to HTML by its own page function at a fixed render time, its reads answered by a stand-in
// for fetch. The rows are made up (10 MWh every day for every grid; no row of any table is in this file); the other
// tables of the page are not answered, and the page says so in their place. No server, no network, nothing written.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-alt-storage-month.mjs
// Exit 1 on a failure.
import { prerenderToNodeStream } from "react-dom/static";

const S = await import("../lib/storagemonth.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };

const NOW = Date.UTC(2026, 10, 17, 12);   // 17 November 2026, 12:00 UTC: the day of the browser read
const GRIDS = { us48: "eia930:US48", erco: "eia930:ERCO", isne: "eia930:ISNE", miso: "eia930:MISO", swpp: "eia930:SWPP", ciso: "caiso:ISO" };
const VARIABLES = ["mwh_discharged", "mwh_charged", "round_trip_ratio", "peak_discharge_hour", "peak_charge_hour"];

// made-up rows: every local day from 1 August to 15 November 2026, 10 of each variable; CAISO has no 20 October
const made = [];
for (let t = Date.UTC(2026, 7, 1); t <= Date.UTC(2026, 10, 15); t += 86_400_000) {
  const ts = new Date(t).toISOString().replace(".000Z", "+00:00");
  for (const entity of Object.values(GRIDS)) {
    if (entity === "caiso:ISO" && ts.startsWith("2026-10-20")) continue;
    for (const variable of VARIABLES) made.push({ entity, variable, ts_utc: ts, value: 10, unit: "MWh", freq: "P1D" });
  }
}

// ---- the rule, on the rows each window gives
const from = (iso) => made.filter((r) => Date.parse(r.ts_utc) >= Date.parse(iso));
const since45 = new Date(NOW - 45 * 86_400_000).toISOString();
ok(since45.startsWith("2026-10-03") && S.monthTotal(from(since45), GRIDS.erco) === null, "the fault: the panel's 45 days start on 3 October on 17 November, and no calendar month is whole in them");
const has = typeof S.monthSince === "function";
ok(has && S.monthSince(NOW) === "2026-09-01T00:00:00Z", "the column's own read starts on the first day of the month two before (1 September on 17 November)");
ok(has && S.monthSince(Date.UTC(2027, 0, 31, 23)) === "2026-11-01T00:00:00Z" && S.monthSince(Date.UTC(2026, 2, 1)) === "2026-01-01T00:00:00Z", "across a year's end, and on a month's first day");
const m = has ? S.monthTotal(from(S.monthSince(NOW)), GRIDS.erco) : null;
ok(m !== null && m.month === "2026-10" && m.days === 31 && m.mwh === 310 && m.perDay === 10, "on that read October 2026 is whole: 31 days");
const c = has ? S.monthTotal(from(S.monthSince(NOW)), GRIDS.ciso) : null;
ok(c !== null && c.month === "2026-09" && c.days === 30, "a grid whose October lacks a day reads its September: a month missing a day is not summed, and the read reaches the month before");

// ---- the page drawn
function standIn(asked, refuse) {
  return async (url) => {
    const u = new URL(String(url));
    const q = u.searchParams;
    const table = (q.get("table_name") ?? "").replace(/^eq\./, "");
    const variable = (q.get("variable") ?? "").replace(/^eq\./, "");
    const since = (q.get("ts_utc") ?? "").replace(/^gte\./, "");
    if (!u.pathname.endsWith("/series") || table !== "storage_daily_cycle" || refuse(variable)) return new Response("stand-in: not answered", { status: 404 });
    const offset = Number(q.get("offset") ?? 0), limit = Number(q.get("limit") ?? 1000);
    if (offset === 0) asked.push({ variable, since });
    const rows = made.filter((r) => (!variable || r.variable === variable) && (!since || Date.parse(r.ts_utc) >= Date.parse(since)));
    rows.sort((a, b) => (a.entity < b.entity ? -1 : a.entity > b.entity ? 1 : a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : 1));
    return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
}

async function draw(refuse = () => false) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const realFetch = globalThis.fetch, realNow = Date.now, log = console.error;
  globalThis.fetch = standIn(asked, refuse);
  Date.now = () => NOW;
  console.error = () => {};
  try {
    const { default: Storage } = await import("../app/storage/page.tsx");
    const { prelude } = await prerenderToNodeStream(await Storage({ searchParams: Promise.resolve({}) }));
    const parts = [];
    for await (const p of prelude) parts.push(Buffer.from(p));
    return { html: Buffer.concat(parts).toString("utf-8").replace(/<!-- -->/g, ""), asked };
  } finally {
    globalThis.fetch = realFetch;
    Date.now = realNow;
    console.error = log;
  }
}
const cell = (html, code) => (new RegExp(`<td[^>]*data-month="${code}"[^>]*>([\\s\\S]*?)</td>`).exec(html) ?? ["", ""])[1];

const { html, asked } = await draw();
ok(/data-month-head="1"/.test(html) && Object.keys(GRIDS).every((g) => cell(html, g) !== ""), "the daily cycle is drawn with the column, a cell for each of the six rows");
ok(asked.some((a) => a.variable === "" && a.since.startsWith("2026-10-03")), "the panel's own read stands: every variable, the last 45 days");
ok(asked.some((a) => a.variable === "mwh_discharged" && a.since === "2026-09-01T00:00:00Z") && asked.length === 2, `the column has a read of its own: the discharge alone, from 1 September (${JSON.stringify(asked)})`);
ok(!html.includes("no whole month"), "browser row 363: no cell reads \"no whole month\" when the table holds a whole month");
for (const g of ["us48", "erco", "isne", "miso", "swpp"]) {
  const h = cell(html, g);
  ok(/data-month-mwh="310"/.test(h) && />2026-10</.test(h) && h.includes('title="31 days, 10 MWh a day"'), `${g}: October's total with "2026-10" beside it and, on hover, "31 days, 10 MWh a day"`);
}
ok(/data-month-mwh="300"/.test(cell(html, "ciso")) && />2026-09</.test(cell(html, "ciso")) && cell(html, "ciso").includes('title="30 days, 10 MWh a day"'), "ciso (no 20 October in these rows): September's total, named 2026-09");
ok(html.includes('data-check="series|storage_daily_cycle|eia930:ERCO|mwh_discharged|2026-11-15T00:00:00+00:00"'), "the newest day's figure stands as it was, from the panel's own read");

// the column's read refused: the cells say so, and do not say that no month is whole
const refused = await draw((variable) => variable === "mwh_discharged");
ok(Object.keys(GRIDS).every((g) => /data-month-unread="1"/.test(cell(refused.html, g)) && cell(refused.html, g).includes("not read")) && !refused.html.includes("no whole month"),
  "when the column's read fails each cell reads \"not read\", with the reason on hover, and the rest of the panel is drawn");

console.log(`\n${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
