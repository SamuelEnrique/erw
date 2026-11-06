// Energy Research Warehouse (ERW) site, session 1193: a group's held rows said once a grid (lib/board.ts heldLines), on
// the site's own file after the day's hold, and drawn so by the board (components/board/BoardView.tsx). No request, no build.
//
//   node --import ./scripts/alias-register.mjs scripts/test-board-1193.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const b = await import("../lib/board.ts");
const lic = await import("../lib/license.ts");
const raw = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const file = b.holdRows(raw, lic.licenseHeldGrids().map(lic.gridName));
const view = fs.readFileSync(new URL("../components/board/BoardView.tsx", import.meta.url), "utf8");

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const split = file.groups.map((g) => ({ g, rows: b.rowsOf(file, g, {}), ...b.heldLines(b.rowsOf(file, g, {})) }));

test("every row is kept: the shown rows and the held lines' rows are the group's rows, none twice", () => {
  for (const { g, rows, shown, held } of split) {
    const ids = [...shown, ...held.flatMap((h) => h.rows)].map((r) => r.id);
    assert.deepEqual([...ids].sort(), rows.map((r) => r.id).sort(), g.id);
    assert.equal(new Set(ids).size, ids.length, g.id);
  }
});

test("a held line is one grid's rows only, every one of them \"license\", and no shown row is a held grid's", () => {
  const heldGrids = new Set(file.held ?? []);
  assert.ok(heldGrids.size >= 1);
  let lines = 0;
  for (const { g, shown, held } of split) {
    assert.ok(shown.every((r) => r.status !== "license"), g.id);
    for (const h of held) {
      lines += 1;
      assert.ok(heldGrids.has(h.grid), `${g.id}: ${h.grid}`);
      assert.ok(h.rows.every((r) => r.status === "license" && b.gridOfRow(r) === h.grid), `${g.id}: ${h.grid}`);
    }
    assert.equal(new Set(held.map((h) => h.grid)).size, held.length, g.id);
  }
  assert.ok(lines >= 2, `${lines} held lines`);
});

test("the shown rows keep their order, and the held lines come in the order their grid first appears", () => {
  for (const { g, rows, shown, held } of split) {
    assert.deepEqual(shown.map((r) => r.id), rows.filter((r) => r.status !== "license").map((r) => r.id), g.id);
    const first = [...new Set(rows.filter((r) => r.status === "license").map((r) => b.gridOfRow(r)))];
    assert.deepEqual(held.map((h) => h.grid), first, g.id);
  }
});

test("the board draws a held line with its count, the hold's words for a screen reader and a toggle, its rows hidden until asked", () => {
  assert.match(view, /data-held-line=\{`\$\{group\.id\}\|\$\{grid\}`\}/);
  assert.match(view, /data-held-count=\{hs\.length\}/);
  assert.match(view, /<span className="sr-only">: \{heldNote\(grid\)\}<\/span>/);
  assert.match(view, /aria-expanded=\{!!named\[grid\]\}/);
  assert.match(view, /hidden=\{!named\[grid\]\}/);
});

test("a group with no held row is drawn as before", () => {
  const plain = split.filter((s) => !s.held.length);
  assert.ok(plain.length >= 1);
  for (const { g, rows, shown } of plain) assert.deepEqual(shown, rows, g.id);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
