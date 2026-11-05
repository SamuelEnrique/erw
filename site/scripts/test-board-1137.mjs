// Energy Research Warehouse (ERW) site, session 1137: the rows the board draws, as a CSV (lib/board.ts rowsCsv), from the
// site's own file after the day's hold. No request, no build.
//
//   node --import ./scripts/alias-register.mjs scripts/test-board-1137.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const b = await import("../lib/board.ts");
const lic = await import("../lib/license.ts");
const raw = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const file = b.holdRows(raw, lic.licenseHeldGrids().map(lic.gridName));
const text = b.rowsCsv(file);
const route = fs.readFileSync(new URL("../app/board/rows/route.ts", import.meta.url), "utf8");

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
// a CSV line split as rowsCsv writes it (a quoted cell may hold a comma)
const cells = (line) => { const out = []; let cur = "", q = false; for (let i = 0; i < line.length; i++) { const ch = line[i];
  if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
  else if (ch === '"') q = true; else if (ch === ",") { out.push(cur); cur = ""; } else cur += ch; } out.push(cur); return out; };
const lines = text.trimEnd().split("\n");
const head = lines.filter((l) => l.startsWith("#"));
const body = lines.filter((l) => !l.startsWith("#"));
const by = Object.fromEntries(body.slice(1).map((l) => { const c = cells(l); return [c[0], c]; }));

test("a header as the data standard writes one, then one line a row", () => {
  assert.ok(head.length >= 4 && head.some((l) => l.startsWith("# Built: ")) && head.some((l) => l.startsWith("# Source: ")) && head.some((l) => l.startsWith("# License: ")));
  assert.deepEqual(cells(body[0]), b.ROWS_HEAD);
  assert.equal(body.length - 1, file.rows.length);
});

test("every figure in the file is the board's own, as the page draws it from", () => {
  const i = b.ROWS_HEAD.indexOf("latest"), d = b.ROWS_HEAD.indexOf("day_move"), lo = b.ROWS_HEAD.indexOf("low_365d");
  for (const r of file.rows) {
    const c = by[r.id];
    assert.ok(c, r.id);
    if (r.status === "ok" && r.last) {
      assert.equal(Number(c[i]), r.last.v, r.id);
      if (r.moves?.d) assert.equal(Number(c[d]), r.moves.d.ch, r.id);
      if (r.range) assert.equal(Number(c[lo]), r.range.lo, r.id);
    } else assert.equal(c[i], "", r.id);
  }
});

test("a held grid's row carries no figure, its status says license", () => {
  const held = file.rows.filter((r) => r.status === "license");
  assert.ok(held.length >= 90);
  const figures = b.ROWS_HEAD.slice(b.ROWS_HEAD.indexOf("latest"), b.ROWS_HEAD.indexOf("source"));
  for (const r of held) for (const k of figures) assert.equal(by[r.id][b.ROWS_HEAD.indexOf(k)], "", `${r.id} ${k}`);
  assert.ok(head.some((l) => /Held for a license on the day the page was built: ISO-NE, NYISO/.test(l)));
});

test("the route serves it from the held file, gated with the page", () => {
  assert.ok(route.includes("holdRows(fileJson as unknown as BoardFile, licenseHeldGrids().map(gridName))"));
  assert.ok(route.includes('export const dynamic = "force-static";'));
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
