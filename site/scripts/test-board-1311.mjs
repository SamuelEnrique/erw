// Energy Research Warehouse (ERW) site, session 1311: the rows' CSV (lib/board.ts rowsCsv) says the held rows as the
// page's lines do (session 1193): their count by grid in the header, the hold's words on each held line. On the site's
// own file after the day's hold. No request, no build.
//
//   node --import ./scripts/alias-register.mjs scripts/test-board-1311.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const b = await import("../lib/board.ts");
const lic = await import("../lib/license.ts");
const raw = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const file = b.holdRows(raw, lic.licenseHeldGrids().map(lic.gridName));
const lines = b.rowsCsv(file).trimEnd().split("\n");
const head = lines.filter((l) => l.startsWith("#"));
const body = lines.filter((l) => !l.startsWith("#"));

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const cells = (line) => { const out = []; let cur = "", q = false; for (let i = 0; i < line.length; i++) { const ch = line[i];
  if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
  else if (ch === '"') q = true; else if (ch === ",") { out.push(cur); cur = ""; } else cur += ch; } out.push(cur); return out; };

test("the header counts the held rows by grid, as many as the file holds", () => {
  const line = head.find((l) => l.startsWith("# Held rows by grid: "));
  assert.ok(line);
  for (const g of file.held) {
    const count = file.rows.filter((r) => r.status === "license" && b.gridOfRow(r) === g).length;
    assert.ok(count > 0 && line.includes(`${g} ${count}`), `${g} ${count}`);
  }
});

test("a held line carries the hold's words, and no other line does", () => {
  const at = b.ROWS_HEAD.indexOf("hold");
  assert.equal(at, b.ROWS_HEAD.length - 1);
  assert.equal(cells(body[0]).join(","), b.ROWS_HEAD.join(","));
  for (const l of body.slice(1)) {
    const c = cells(l), status = c[b.ROWS_HEAD.indexOf("status")], row = file.rows.find((r) => r.id === c[0]);
    assert.equal(c.length, b.ROWS_HEAD.length, c[0]);
    assert.equal(c[at], status === "license" ? b.heldNote(b.gridOfRow(row)) : "", c[0]);
  }
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
