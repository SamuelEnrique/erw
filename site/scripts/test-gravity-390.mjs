// Energy Research Warehouse (ERW) site, session 1424 (chain 111): the Gravity tab's blocks at 390 pixels, from the code.
// Session 1158's rules (scripts/test-grid-390.mjs, whose count tests/test_session1158.py pins, so these are a file of their
// own) on the blocks chains 078 to 100 added under and beside the gravity shape: the gravity table (components/grid/
// NetworkFigures.tsx GravityFigures), the Exchange blocks (components/grid/ExchangeView.tsx: the seven-column ties table of
// session 1167, the twelve months, the Lower 48's seven grids), the gravity day line (components/grid/ReplayDay.tsx
// ReplayDayDemand, session 1170), the balance (NetworkFigures.tsx Balance, session 1165, on the Network tab) and the replayed
// day's table, with the download lines (session 1182). Every table is the shared ToolTable: a scroll frame a keyboard
// reaches (lib/cells.ts scrollRegion, named by the caption), a caption, header cells with a scope, the first cell of a row
// its header (the tie, the grid, the part of the balance). No fixed width above 358 pixels outside a frame; a failed read's
// reason, which can hold the database's answer without a space, breaks. The same rules on the markup as the server draws it
// are the `tables` of scripts/test-grid-render.mjs's cases. Needs no build, no network and no node_modules.
//
//   node scripts/test-gravity-390.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (...p) => fs.readFileSync(path.join(here, "..", ...p), "utf-8").replace(/\r\n/g, "\n");
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const BLOCKS = {
  ExchangeView: read("components", "grid", "ExchangeView.tsx"),
  NetworkFigures: read("components", "grid", "NetworkFigures.tsx"),
  ReplayDay: read("components", "grid", "ReplayDay.tsx"),
  NetworkView: read("components", "grid", "NetworkView.tsx"),
};

test("the shared table: a scroll frame a keyboard reaches, named by its caption; header cells with a scope; each row's first cell its header", () => {
  const t = read("components", "tool", "ToolPage.tsx");
  const tt = t.slice(t.indexOf("export function ToolTable("), t.indexOf("/** A folded section, closed by default. */"));
  assert.ok(tt.includes('<div className="overflow-x-auto" {...scrollRegion(caption)}>'), "the frame");
  assert.ok(tt.includes('{caption ? <caption className="sr-only">{caption}</caption> : null}'), "the caption");
  assert.ok(tt.includes('<th key={i} scope="col"'), "column headers");
  assert.ok(tt.includes('<th key={i} scope="row" className="px-3 py-1.5 font-normal">{c}</th>'), "row headers");
  assert.ok(tt.includes("style={{ minWidth }}"), "the table's width is inside the frame");
  const c = read("lib", "cells.ts");
  assert.ok(c.includes('return { tabIndex: 0, role: "region", "aria-label": name || "Table",'), "one keyboard stop, named");
});

test("every table of the Gravity tab's blocks and the balance is the shared table, each with its caption", () => {
  const want = { ExchangeView: 3, NetworkFigures: 4, ReplayDay: 1, NetworkView: 0 };
  for (const [f, s] of Object.entries(BLOCKS)) {
    assert.equal((s.match(/<ToolTable /g) ?? []).length, want[f], `${f}: its tables`);
    assert.equal((s.match(/<ToolTable caption=\{?["`]/g) ?? []).length, want[f], `${f}: a caption on each`);
    assert.ok(!/<table[\s>]/.test(s), `${f}: no table of its own`);
  }
  // the captions as the cases of test-grid-render.mjs read them
  const ex = BLOCKS.ExchangeView, nf = BLOCKS.NetworkFigures;
  assert.ok(ex.includes('<ToolTable caption={`${grid.label}\'s ties in the hour`} minWidth={680} head={tieHead}'), "the seven-column table");
  assert.equal((ex.match(/const tieHead = \[([^\]]*)\]/)[1].match(/"/g) ?? []).length / 2, 7, "seven columns");
  assert.ok(ex.includes('<ToolTable caption={`${grid.label}\'s neighbours over twelve months`} minWidth={560} head={supHead}'));
  assert.ok(ex.includes('<ToolTable caption="Net export of the seven grids in the hour" minWidth={360} head={head48}'));
  assert.ok(nf.includes('<ToolTable caption="The seven grids in the gravity shape, the hour shown" minWidth={460} head={gHead}'));
  assert.ok(nf.includes('<ToolTable caption={`${label}\'s balance in the hour the network shows`} minWidth={420} head={balHead}'));
});

test("no fixed width above 358 px outside a frame in these blocks", () => {
  for (const [f, s] of Object.entries(BLOCKS)) {
    assert.ok(!/style=\{\{[^}]*\b(width|minWidth)\s*:/.test(s), `${f}: no inline width`);
    for (const m of s.matchAll(/(?:^|[\s"`])((?:min-)?w-\[(\d+)px\])/g)) assert.ok(Number(m[2]) <= 358, `${f}: ${m[1]}`);
    for (const m of s.matchAll(/(?:^|[\s"`])((?:min-)?w-(\d+))(?=[\s"`])/g)) assert.ok(Number(m[2]) * 4 <= 358, `${f}: ${m[1]}`);
    assert.ok(!/(?:^|[\s"`])whitespace-nowrap/.test(s), `${f}: no line that cannot wrap`);
  }
  // every minWidth handed to the shared table sits inside its frame; the widest is the seven-column table's
  const widths = Object.values(BLOCKS).flatMap((s) => [...s.matchAll(/<ToolTable [^>]*minWidth=\{(\d+)\}/g)].map((m) => Number(m[1])));
  assert.equal(Math.max(...widths), 680);
});

test("a failed read's reason breaks at 390 px: the twelve months on the Gravity tab and the network's line", () => {
  assert.ok(BLOCKS.ExchangeView.includes(': !sup.ok ? <div className="break-words" data-reason-wraps="1"><NoData what="the twelve months" reason={sup.reason} /></div>'));
  assert.ok(BLOCKS.NetworkView.includes('{bad && !bad.ok ? <p className="mt-2 text-sm text-muted break-words" role="status" data-reason-wraps="1">The last twelve months could not be read, so the panel shows none: {bad.reason}</p> : null}'));
  // the reasons these blocks write themselves have spaces: no wrapper needed
  assert.ok(BLOCKS.ExchangeView.includes('reason={`${SUPPLY_TABLE} holds no whole month for ${ba}`}'));
});

test("the gravity day line is a line of words with its one figure, no table and no width of its own", () => {
  const r = BLOCKS.ReplayDay;
  const line = r.slice(r.indexOf("export function ReplayDayDemand("));
  assert.equal((line.match(/<p className="mt-3 max-w-3xl text-sm" data-gravity-day=\{ask.day\}>/g) ?? []).length, 2);
  assert.ok(!line.includes("<ToolTable"));
});

test("the render test holds the Gravity tab's cases and the balance's to these rules on the drawn markup", () => {
  const t = read("scripts", "test-grid-render.mjs");
  const cases = t.split("\n").filter((l) => l.startsWith('  {"name": ')).map((l) => JSON.parse(l.trim().replace(/,$/, "")));
  const mine = cases.filter((c) => /^(grid_gravity_|view_exchange|gravityday|balance_)/.test(c.block));
  assert.equal(mine.length, 13);
  for (const c of mine) assert.ok(Array.isArray(c.tables), c.name);
  assert.deepEqual(cases.find((c) => c.name === "view_exchange on /grid?grid=ercot&view=gravity").tables, ["ERCOT's ties in the hour", "ERCOT's neighbours over twelve months"]);
  assert.ok(t.includes("if (b.wide.length) why.push(`a fixed width above 358 px outside a frame: ${b.wide[0]}`);"));
  const s = read("scripts", "grid-render-standin.mjs");
  assert.ok(s.includes('if (props.role === "region" && props.tabIndex !== undefined) { FRAMES.push({ label: props["aria-label"], tabIndex: props.tabIndex }); opened.frame = true; }'));
});

console.log(`${n} tests passed`);
