// Energy Research Warehouse (ERW) site, session 1180 (chain 091): the storage units and the network snapshot, read
// once. Without a build and without a request leaving this machine.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-units.mjs
//
// The reads are answered by a stand-in for PostgREST and for the public Storage object over a committed fixture of
// real rows (scripts/fixtures/grid_units.json: storage_capacity's battery units of PJM, SPP and MISO whole and every
// tenth of the others, read once with the anon key on 24 October 2026) and the committed snapshot
// (data/grid_network.json). It counts what it is asked. A render is a new globalThis.__erwRequestCache
// (scripts/tsx-loader.mjs keeps React's `cache` in it, as Next keeps one a request).
// Cases:
//   1. lib/gridReads.ts gridUnitsQuery: the grid's ISO only (extra->>iso), the three columns the Batteries block draws,
//      the whole read's table and order.
//   2. gridStorageUnits(iso) for each of the seven ISO grids: the units, in the order and with the values the whole
//      read (lib/data.ts storageUnits) gave once filtered by ISO as lib/grid.ts load filtered it; one request.
//   3. The Batteries block (components/grid/YourGrid.tsx GridNowParts) drawn with the units of the whole read filtered
//      and with the narrowed read's: every storage| figure the same key, value and text.
//   4. freshSnapshot: one fetch a render, the same answer to every caller; a new render fetches again; outside a
//      render each call fetches (as before); the Gravity tab's two readers (components/grid/NetworkView.tsx with
//      shape "gravity" and components/grid/ExchangeView.tsx) fetch the snapshot once a render, fresh; the Network
//      tab's reader keeps its one hourly read.
//   5. scripts/same-figures.mjs: paramsOf, figuresOf's lists and compareFigures (the same, a value moved, a component
//      that threw, a page not walked).
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";

const here = path.dirname(fileURLToPath(import.meta.url));
const ORIGIN = "https://erw-session1180.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1180-test";
process.env.ERW_PAGES_TOGETHER = "1";
delete process.env.ERW_READ_TIMING;
delete process.env.NEXT_PHASE;
delete process.env.NEXT_RUNTIME;

const fixture = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "grid_units.json"), "utf-8"));
const snapText = fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8");
const SNAP_PATH = "/storage/v1/object/public/erw-public/network/grid_network.json";

let sent = [];
/** select "a,b:extra->>c" over a fixture row that holds a, b's own name and c's alias (the fixture's columns). */
const ALIAS = { "extra->>iso": "iso", "extra->>state": "state", "extra->>planned_year": "planned_year", "extra->>energy_capacity_mwh": "mwh" };
function pick(row, select) {
  const out = {};
  for (const col of select.split(",")) {
    const [name, src] = col.includes(":") ? col.split(":") : [col, col];
    const from = ALIAS[src] ?? src;
    if (!(from in row)) throw new Error(`the stand-in does not hold the column ${src}`);
    out[name] = row[from];
  }
  return out;
}
function postgrest(u) {
  const p = u.searchParams;
  const table = (p.get("table_name") ?? "").replace(/^eq\./, "");
  if (u.pathname !== "/rest/v1/entities" || table !== "storage_capacity") {
    sent.push({ table: table || u.pathname, query: u.search, rows: 0 });
    return new Response("[]", { status: 200, headers: { "content-type": "application/json", "content-range": "*/0" } });
  }
  let rows = [...fixture.rows];
  for (const [k, v] of p) {
    if (["select", "order", "limit", "offset", "table_name"].includes(k)) continue;
    if (!v.startsWith("eq.")) throw new Error(`the stand-in does not know the filter ${k}=${v}`);
    const col = ALIAS[k] ?? k;
    rows = rows.filter((r) => r[col] !== null && String(r[col]) === v.slice(3));
  }
  if ((p.get("order") ?? "") !== "entity_id") throw new Error(`the stand-in does not know the order ${p.get("order")}`);
  // the fixture is in the warehouse's own order by entity_id (its collation, not the code points): kept as it is
  const off = Number(p.get("offset") ?? 0), lim = Number(p.get("limit") ?? 1000);
  const page = rows.slice(off, off + lim).map((r) => pick(r, p.get("select") ?? ""));
  sent.push({ table, query: u.search, rows: page.length });
  return new Response(JSON.stringify(page), { status: 200, headers: { "content-type": "application/json", "content-range": page.length ? `${off}-${off + page.length - 1}/*` : "*/0" } });
}
globalThis.fetch = async (url, init = {}) => {
  const u = new URL(String(url?.url ?? url));
  if (u.origin !== ORIGIN) throw new Error(`a request this test does not make: ${u.origin}`);
  if (u.pathname === SNAP_PATH) {
    sent.push({ table: "snapshot", query: "", rows: 1, revalidate: init?.next?.revalidate });
    return new Response(snapText, { status: 200, headers: { "content-type": "application/json" } });
  }
  return postgrest(u);
};
console.error = () => undefined;   // a read the stand-in answers empty may be logged by a reader

const { storageUnits } = await import("../lib/data.ts");
const R = await import("../lib/gridReads.ts");
const { GRIDS, gridOf } = await import("../lib/grid.ts");
const { GridNowParts } = await import("../components/grid/YourGrid.tsx");
const { NetworkView } = await import("../components/grid/NetworkView.tsx");
const { ExchangeView } = await import("../components/grid/ExchangeView.tsx");
const { GRID_CHOICES } = await import("../lib/gridtool.ts");
const S = await import("./same-figures.mjs");

let failed = 0;
const check = (name, ok, detail = "") => { console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? `: ${detail}` : ""}`); if (!ok) failed++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const render = () => { globalThis.__erwRequestCache = new Map(); };
const done = () => { delete globalThis.__erwRequestCache; };
const asked = (t) => sent.filter((s) => s.table === t);
const project = (u) => ({ capacity_mw: u.capacity_mw, status: u.status, mwh: u.mwh });

// 1. the query
{
  const q = R.gridUnitsQuery("ISO-NE");
  check("gridUnitsQuery: the ISO, the three columns drawn, the table and the order",
    same(q, { select: "capacity_mw,status,mwh:extra->>energy_capacity_mwh", table_name: "eq.storage_capacity", "extra->>iso": "eq.ISO-NE", order: "entity_id" }), JSON.stringify(q));
}

// 2. the narrowed read, grid by grid
const isos = GRIDS.map((g) => g.iso);
const whole = await storageUnits();
{
  check("the seven ISO grids, and the fixture whole through storageUnits", isos.length === 7 && whole.length === fixture.rows.length, `${isos.join(", ")}; ${whole.length} units`);
  let ok = true;
  const sizes = [];
  for (const iso of isos) {
    sent = [];
    const narrow = await R.gridStorageUnits(iso);
    const reqs = asked("storage_capacity").length;
    const before = whole.filter((u) => u.iso === iso).map(project);
    sizes.push(`${iso} ${narrow.length}`);
    if (!same(narrow, before) || reqs !== 1 || !narrow.length) ok = false;
  }
  check("gridStorageUnits: each grid's units, in the whole read's order and values, in one request", ok, sizes.join(", "));
  const counts = Object.fromEntries(isos.map((i) => [i, whole.filter((u) => u.iso === i).length]));
  check("gridStorageUnits: the units held whole in the fixture are the warehouse's counts (PJM, SPP, MISO)",
    counts.PJM === fixture.whole_table_by_iso.PJM && counts.SPP === fixture.whole_table_by_iso.SPP && counts.MISO === fixture.whole_table_by_iso.MISO, JSON.stringify(counts));
  check("gridStorageUnits: a unit with no ISO is no grid's", (await R.gridStorageUnits("")).length === 0 && whole.some((u) => !u.iso));
  const rows = (await R.gridStorageUnits("PJM"))[0];
  check("gridStorageUnits: the three columns and no other", same(Object.keys(rows).sort(), ["capacity_mw", "mwh", "status"]));
}

// 3. the Batteries block, drawn both ways
{
  const empty = { demand: [], gen: [], cycle: [], ci: [], monthly: [], prices: [], peak: [], queue: [], dcs: [], news: [], newsSince: "2026-10-10", errors: {} };
  let ok = true, n = 0;
  const lines = [];
  for (const g of GRIDS) {
    const old = await S.figuresOf(h(GridNowParts, { g, d: { ...empty, units: whole.filter((u) => u.iso === g.iso) } }));
    const now = await S.figuresOf(h(GridNowParts, { g, d: { ...empty, units: await R.gridStorageUnits(g.iso) } }));
    const a = old.nums.filter((x) => x.check.startsWith("storage|")), b = now.nums.filter((x) => x.check.startsWith("storage|"));
    n += a.length;
    lines.push(`${g.iso} ${a.length}`);
    if (!same(a, b) || a.length !== 4 || old.errors.length || now.errors.length || !same(old.nums, now.nums)) ok = false;
  }
  check("the Batteries block: every storage| figure the same key, value and text, both ways", ok, `${n} figures (${lines.join(", ")})`);
  const pjm = await S.figuresOf(h(GridNowParts, { g: gridOf("pjm"), d: { ...empty, units: await R.gridStorageUnits("PJM") } }));
  const op = whole.filter((u) => u.iso === "PJM" && u.status === "operating");
  const mw = Math.round(op.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
  const drawn = pjm.nums.find((x) => x.check === "storage|iso_mw|PJM|operating");
  check("the Batteries block: PJM's operating MW is the sum of its operating units", op.length > 0 && Number(drawn?.raw) === mw, `${drawn?.raw} drawn, ${mw} summed over ${op.length} units`);
}

// 4. the snapshot, once a render
{
  sent = [];
  render();
  const a = R.freshSnapshot(), b = R.freshSnapshot();
  const [x, y] = await Promise.all([a, b]);
  check("freshSnapshot: one fetch a render, fresh, the same answer to both callers", asked("snapshot").length === 1 && asked("snapshot")[0].revalidate === 0 && x === y && x && x.hours.length > 0, `${asked("snapshot").length} fetch(es)`);
  done();
  render();
  await R.freshSnapshot();
  check("freshSnapshot: a new render fetches again", asked("snapshot").length === 2);
  done();
  sent = [];
  await R.freshSnapshot();
  await R.freshSnapshot();
  check("freshSnapshot: outside a render each call fetches, as fetchHourly(0) did", asked("snapshot").length === 2);

  const grid = GRID_CHOICES.find((g) => g.slug === "ercot");
  sent = [];
  render();
  const gravity = await S.figuresOf([h(NetworkView, { keep: "?grid=ercot&view=gravity", node: null, shape: "gravity", grid, day: null }), h(ExchangeView, { grid })]);
  done();
  const snaps = asked("snapshot");
  check("the Gravity tab: the network component and the Exchange blocks fetch the snapshot once, fresh",
    snaps.length === 1 && snaps[0].revalidate === 0 && !gravity.errors.length && gravity.nums.length > 0, `${snaps.length} fetch(es), ${gravity.nums.length} figures, errors ${gravity.errors.join("; ")}`);
  sent = [];
  render();
  const network = await S.figuresOf(h(NetworkView, { keep: "?grid=ercot&view=network", node: null, grid, day: null }));
  done();
  const ns = asked("snapshot");
  check("the Network tab: its one read keeps the hourly revalidation", ns.length === 1 && ns[0].revalidate === 3600 && !network.errors.length, `${ns.length} fetch(es), revalidate ${ns[0]?.revalidate}`);
}

// 5. the comparison of scripts/same-figures.mjs
{
  check("paramsOf: an address of /grid to its query", same(S.paramsOf("/grid?grid=ercot&view=mix&mixp=month"), { grid: "ercot", view: "mix", mixp: "month" }) && same(S.paramsOf("/grid"), {}));
  let threw = false;
  try { S.paramsOf("/storage"); } catch { threw = true; }
  check("paramsOf: another page is refused", threw);
  const Panel = ({ v }) => h("div", { "data-grid-panel": "grid_test_x" }, h("span", { "data-check": `k|${v}`, "data-raw": v }, `${v} MW`), h("span", { "data-license-held": "t" }, "license needed"));
  const Bad = () => { throw new Error("no rows"); };
  const f1 = await S.figuresOf(h(Panel, { v: 1 }));
  check("figuresOf: a figure's key, value and text, the held figure and the panel, in order",
    same(f1, { nums: [{ check: "k|1", raw: 1, text: "1 MW" }], held: ["t"], panels: ["grid_test_x"], errors: [] }), JSON.stringify(f1));
  const f2 = await S.figuresOf(h(Panel, { v: 2 }));
  const f3 = await S.figuresOf([h(Panel, { v: 1 }), h(Bad)]);
  const c0 = S.compareFigures({ a: f1 }, { a: await S.figuresOf(h(Panel, { v: 1 })) });
  const c1 = S.compareFigures({ a: f1 }, { a: f2 });
  const c2 = S.compareFigures({ a: f1 }, { a: f3 });
  const c3 = S.compareFigures({ a: f1, b: f1 }, { a: f1 });
  check("compareFigures: the same walk is the same", c0.differ === 0 && c0.figures === 1 && c0.pages[0].line.startsWith("same a:"));
  check("compareFigures: a value moved is a difference, shown", c1.differ === 1 && c1.pages[0].diffs.length === 1 && c1.pages[0].diffs[0].after.raw === 2);
  check("compareFigures: a component that threw is a difference", c2.differ === 1 && f3.errors.length === 1);
  check("compareFigures: a page not walked after is a difference", c3.differ === 1 && c3.pages[1].line.includes("not walked after"));
}

console.log(failed ? `${failed} case(s) failed` : "every case holds");
process.exit(failed ? 1 : 0);
