// Energy Research Warehouse (ERW) site, session 7541 (chain 304, part C): the read of /supply as a utility planner or a
// fund analyst (docs/reviews/supply-read-2026-11-16.md). The page drawn whole by its own function on the site's own
// file (scripts/supply-read-page.mjs), and each site row of the read held:
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-supply-read.mjs
// Exit 1 on a failure. Nothing is written.
import assert from "node:assert/strict";
import fs from "node:fs";
import { drawSupply, rowHtml } from "./supply-read-page.mjs";
import { CLEARED_GRID, fmt, placeWords } from "../lib/supply.ts";
import { licenseHeldGrids } from "../lib/license.ts";

const raw = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf-8"));
const board = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf-8"));
const html = await drawSupply("");
const plain = (h) => h.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const titleOf = (h, attr) => { const m = new RegExp(`title="([^"]*)"[^>]*${attr}|${attr}[^>]*title="([^"]*)"`).exec(h); return m ? (m[1] ?? m[2]).replace(/&#x27;/g, "'") : ""; };
const byId = Object.fromEntries(raw.rows.map((r) => [r.id, r]));
const held = new Set(licenseHeldGrids());
let n = 0;
const test = async (name, fn) => { await fn(); n += 1; console.log(`ok   ${name}`); };

// the figures of a row held on the day, in the forms a page or a note could write them
const heldIds = Object.entries(CLEARED_GRID).filter(([id, g]) => held.has(g) && byId[id]?.status === "ok").map(([id]) => id);
const forms = (v) => [fmt(v, "MWh/d"), String(Math.round(v)), v.toFixed(1), String(v)];

await test("row 1: a grid held for a license on the day has its cleared row drawn \"license needed\", with no figure anywhere on the page", () => {
  assert.ok(heldIds.length >= 1, "NYISO's cleared table is held on the day (license_status.json)");
  for (const id of heldIds) {
    const h = rowHtml(html, id);
    assert.ok(h.includes('data-status="held"') && plain(h).includes("license needed") && !/data-n=/.test(h), id);
    assert.ok(/asks for permission/.test(h), `${id}: the publisher's words on hover`);
    for (const f of forms(byId[id].last.v)) assert.ok(!html.includes(f), `${id}: ${f} is not in the page`);
  }
  for (const [id, g] of Object.entries(CLEARED_GRID)) if (!held.has(g) && byId[id]?.status === "ok") assert.ok(/data-n=/.test(rowHtml(html, id)), `${id} keeps its figure`);
});

await test("row 2: the year column says its base (52 weeks back, the same week) and how the price board's differs", () => {
  const t = titleOf(html, 'data-head="year"');
  assert.ok(/52 weeks before/.test(t) && /price board/.test(t) && /365 days/.test(t), t);
  const r = byId["eia-nw2-epg0-swo-r48-bcf"];
  const days = (Date.parse(r.last.t) - Date.parse(r.year.t)) / 86400000;
  assert.equal(days, 364, "the page's year base is the same week a year before, as EIA's report sets it");
  const b = board.rows.find((x) => x.id === r.id);
  assert.ok(b && (Date.parse(b.last.t) - Date.parse(b.moves.y.t)) / 86400000 >= 365, "the board's base is the newest value at least 365 days back (data request, row 3)");
});

await test("row 4: the Last 52 column says it is the last 52 values held, which can span more than 52 weeks", () => {
  assert.ok(/last 52 values held/.test(titleOf(html, 'data-head="last52"')));
  const all = byId["burn-all-natural-gas"];
  assert.ok((Date.parse(all.spark.t.at(-1)) - Date.parse(all.spark.t[0])) / 86400000 > 51 * 7, "the seven grids' line spans more than 52 weeks");
});

await test("row 5: the burn table links each grid's whole mix and its trade with its neighbours on the Grid page", () => {
  for (const g of ["ercot", "caiso", "pjm", "miso", "nyiso", "isone", "spp"]) {
    assert.ok(html.includes(`href="/grid?grid=${g}"`) && html.includes(`href="/grid?grid=${g}&amp;view=network"`), g);
  }
});

await test("row 6: a burn row older than another grid's names on hover the grids that hold the newer week", () => {
  for (const fuel of ["natural-gas", "coal", "oil"]) {
    const rows = raw.rows.filter((r) => r.group === "burn" && r.status === "ok" && r.id.endsWith(`-${fuel}`) && r.id !== `burn-all-${fuel}`);
    const newest = rows.map((r) => r.last.t).sort().at(-1);
    for (const r of [...rows, byId[`burn-all-${fuel}`]].filter(Boolean)) {
      const h = rowHtml(html, r.id);
      assert.equal(/data-week-behind=/.test(h), r.last.t < newest, r.id);
    }
  }
  const t = titleOf(rowHtml(html, "burn-all-natural-gas"), 'data-week-behind="burn-all-natural-gas"');
  const behind = raw.rows.filter((r) => /^burn-(?!all)[a-z]+-natural-gas$/.test(r.id) && r.status === "ok" && r.last.t < byId["burn-ercot-natural-gas"].last.t).map((r) => r.at);
  assert.ok(behind.length && behind.every((g) => t.includes(g)) && t.includes("ERCOT"), t);
});

await test("row 7: every unit the page writes short has its words on hover", () => {
  const units = [...html.matchAll(/title="([^"]*)" data-unit="([^"]*)"/g)];
  assert.ok(units.length > 50);
  for (const [, t, u] of units) assert.ok(t !== u && t.length > u.length, `${u}: ${t}`);
});

await test("row 11: a monthly gas trade figure gives the month's volume, equal to the price board's MMcf for the same month", () => {
  let k = 0;
  for (const r of raw.rows.filter((x) => x.group === "gastrade" && x.status === "ok")) {
    const b = board.rows.find((x) => x.id === r.id && x.unit === "MMcf");
    if (!b || b.last?.t !== r.last.t.slice(0, 10)) continue;
    const t = titleOf(rowHtml(html, r.id), `data-latest-title="${r.id}"`);
    const m = /: ([\d,.]+) Bcf in the month/.exec(t);
    assert.ok(m, `${r.id}: ${t}`);
    assert.ok(Math.abs(Number(m[1].replace(/,/g, "")) - b.last.v / 1000) <= 0.051, `${r.id}: ${m[1]} Bcf against the board's ${b.last.v} MMcf`);
    k += 1;
  }
  assert.ok(k >= 10, `${k} rows set beside the board`);
});

await test("row 12: the states are written in full in each place, as the price board names the same terminals", () => {
  assert.equal(placeWords("Sabine Pass, LA, monthly"), "Sabine Pass, Louisiana, monthly");
  assert.ok(!/, (LA|TX|MD|GA),/.test(plain(html)) && plain(html).includes("Sabine Pass, Louisiana"));
});

await test("row 14: a net import below zero says on hover that it is a net export", () => {
  for (const id of ["eia-wrpntus2", "eia-wttntus2"]) {
    const t = titleOf(rowHtml(html, id), `data-latest-title="${id}"`);
    assert.ok(byId[id].last.v < 0 && /Below zero/.test(t) && t.includes(fmt(-byId[id].last.v, "kb/d")), `${id}: ${t}`);
  }
  assert.ok(!/data-latest-title="eia-wcrntus2"/.test(html), "a net import above zero carries no such hover");
});

await test("no figure of a row held on the day is in what this session commits", () => {
  const files = ["../../docs/reviews/supply-read-2026-11-16.md", "../../archive/sessions/SESSION_7541_REPORT.md", "./test-supply-read.mjs", "./supply-read-page.mjs"];
  for (const f of files) {
    const u = new URL(f, import.meta.url);
    if (!fs.existsSync(u)) continue;
    const t = fs.readFileSync(u, "utf-8");
    for (const id of heldIds) for (const s of forms(byId[id].last.v)) assert.ok(!t.includes(s), `${f}: ${id}'s ${s}`);
  }
});

console.log(`${n} tests pass`);
