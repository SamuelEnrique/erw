// Energy Research Warehouse (ERW) site, session 1171 (chain 078): a revised EIA-930 hour told apart from a wrong figure
// (scripts/check-revised.mjs, the rule in docs/methods/grid_network.md, "Revisions, said and checked"), and the sentence
// every Grid tab carries (lib/gridPreliminary.ts). A revised row and a wrong row: the first is reported "revised" and
// passes, the second fails, first on the rule's own functions, then end to end: check-values run against a small server
// of this test's own that answers both as the page and as Supabase's REST API (the slow test's way, session 430). No
// build, no database, no network beyond 127.0.0.1, no node_modules.
//
//   node scripts/test-check-revised.mjs
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as REV from "./check-revised.mjs";
import { keysFromValues } from "./check-methods.mjs";
import * as P from "../lib/gridPreliminary.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const note = fs.readFileSync(path.join(here, "..", "..", "docs", "methods", "grid_network.md"), "utf-8");
const tolerated = REV.toleratedOf(note);

let n = 0;
const test = async (name, f) => { await f(); n++; console.log(`ok   ${name}`); };

// The page: a Grid tab drawn at 09:15 UTC on 24 October 2026, carrying two MISO demand hours. The daily load at 15:33 UTC
// rewrote the first (EIA revised it from 77,486 to 77,512 MW); the second was last written on 23 October, before the
// page was drawn, and its figure is wrong (the page shows 70,000 where the row holds 77,245).
const DRAWN = "2026-10-24T09:15:00.000Z";
const html = `<p>Source: ERW tables ... <span data-eia930-drawn="${DRAWN}">${P.preliminaryText(P.drawnUtc(new Date(DRAWN)))}</span></p>`;
const REVISED = { check: "series|eia930_all_demand|eia930:MISO|demand_mw|2026-10-22T23:00:00+00:00", raw: "77486", text: "77,486", value: 77512,
  row: { loaded_at: "2026-10-24T15:33:56+00:00", freq: "PT1H" } };
const WRONG = { check: "series|eia930_all_demand|eia930:MISO|demand_mw|2026-10-22T22:00:00+00:00", raw: "70000", text: "70,000", value: 77245,
  row: { loaded_at: "2026-10-23T15:33:56+00:00", freq: "PT1H" } };
const judge = (x, over = {}) => REV.judgeRevised({ check: x.check, row: x.row, drawn: REV.drawnOf(html), textHolds: true, tolerated, ...over });

await test("the method note tolerates the two tables the Grid tabs key by the hour, and no other", () => {
  assert.deepEqual([...tolerated].sort(), ["eia930_all_demand", "eia930_all_generation"]);
  assert.match(note, /^Revised hours tolerated by check-values: `eia930_all_demand`, `eia930_all_generation`\.$/m);
});

await test("the page's drawing time is read from data-eia930-drawn, the latest when there are several", () => {
  assert.equal(REV.drawnOf(html), DRAWN);
  assert.equal(REV.drawnOf(`${html}<span data-eia930-drawn="2026-10-24T09:14:00.000Z"></span><span data-eia930-drawn="2026-10-24T09:16:30.000Z"></span>`), "2026-10-24T09:16:30.000Z");
  assert.equal(REV.drawnOf("<p>no sentence</p>"), null);
  assert.equal(REV.drawnOf('<span data-eia930-drawn="not a time"></span>'), null);
});

await test("the revised row is reported revised and passes", () => {
  const j = judge(REVISED);
  assert.equal(j.revised, true);
  assert.equal(j.pass, true);
  assert.equal(j.table, "eia930_all_demand");
  const line = REV.revisedLine({ page: "/grid?grid=miso", check: REVISED.check, text: REVISED.text, raw: REVISED.raw, value: REVISED.value, j });
  assert.match(line, /^revised \| \/grid\?grid=miso \| series\|eia930_all_demand\|eia930:MISO\|demand_mw\|2026-10-22T23:00:00\+00:00 \| page shows "77,486" \| page read 77486, drawn 2026-10-24T09:15:00\.000Z \| Supabase 77512, the row written 2026-10-24T15:33:56\.000Z, after the page was drawn: a revision of EIA-930's preliminary hour, tolerated for eia930_all_demand by docs\/methods\/grid_network\.md$/);
  // check-methods reads the revised line's key as it reads ok and FAIL lines
  assert.deepEqual(keysFromValues(line), { "/grid?grid=miso": [REVISED.check] });
});

await test("the wrong row fails: written before the page was drawn, so not a revision", () => {
  const j = judge(WRONG);
  assert.equal(j.revised, false);
  assert.equal(j.pass, undefined);
  assert.match(j.why, /^the row was last written 2026-10-23T15:33:56\.000Z, before the page was drawn 2026-10-24T09:15:00\.000Z: not a revision$/);
  // a row written in the very minute the page was drawn is the row the page read
  assert.equal(judge({ ...WRONG, row: { loaded_at: DRAWN, freq: "PT1H" } }).revised, false);
});

await test("a revision of a table the note does not name fails, and says so", () => {
  const x = { ...REVISED, check: "series|eia930_all_storage|eia930:CISO|storage_mw|2026-10-22T23:00:00+00:00" };
  const j = judge(x);
  assert.equal(j.revised, true);
  assert.equal(j.pass, false);
  assert.match(REV.revisedLine({ page: "/grid?grid=caiso", check: x.check, text: x.text, raw: x.raw, value: x.value, j }),
    /^FAIL \| \/grid\?grid=caiso \| .*: a revision, but docs\/methods\/grid_network\.md does not tolerate one for eia930_all_storage$/);
  // with the note's line gone, nothing is tolerated
  assert.equal(REV.toleratedOf(note.replace(/^Revised hours tolerated by check-values: .*$/m, "")).size, 0);
  assert.equal(judge(REVISED, { tolerated: REV.toleratedOf("") }).pass, false);
});

await test("the rule does not apply (the failure stands as it is) outside its narrow case", () => {
  assert.equal(judge(REVISED, { drawn: REV.drawnOf("<p></p>") }), null);   // a page that carries no drawing time
  assert.equal(judge(REVISED, { textHolds: false }), null);   // the page's text is not its own value
  assert.equal(judge({ ...REVISED, row: null }), null);   // the row is gone
  assert.equal(judge({ ...REVISED, row: { ...REVISED.row, freq: "P1D" } }), null);   // not an hourly row
  for (const check of [
    "series_sum|eia930_all_generation|net_generation_mw|2026-10-21T00:00:00Z|2026-10-22T00:00:00Z|eia930:MISO",   // a sum over hours
    "series_max|eia930_all_demand|demand_mw|2026-10-21T00:00:00Z|2026-10-22T00:00:00Z|eia930:MISO",
    "net|export|MISO|2026-10-21T23:00:00Z",   // the network's snapshot
    "series|eia930_all_demand|eia930:MISO|demand_mw|newest",   // not an hour
    "series|carbon_intensity_hourly|eia930:MISO|intensity_generation|2026-10-22T23:00:00+00:00",   // not an EIA-930 table
    "series|eia930_all_demand|eia930:MISO|demand_mw|2026-10-22T23:00:00+00:00|uri",   // an event's key
  ]) {
    assert.equal(REV.revisedKey(check), null, check);
    assert.equal(judge({ ...REVISED, check }), null, check);
  }
  assert.deepEqual(REV.revisedKey(REVISED.check), { table: "eia930_all_demand", entity: "eia930:MISO", variable: "demand_mw", ts: "2026-10-22T23:00:00+00:00" });
  assert.deepEqual(REV.revisedKey("series|eia930_all_generation|eia930:ERCO|net_generation_mw|2026-10-22T23:00:00Z")?.table, "eia930_all_generation");
});

await test("the sentence: the same words on every tab, the clock only where it is given, no dash", () => {
  assert.equal(P.EIA930_PRELIMINARY, "EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this page was drawn, so a later read of the same hour can differ.");
  assert.equal(P.preliminaryText(null), P.EIA930_PRELIMINARY);
  assert.equal(P.preliminaryText(P.drawnUtc(new Date(DRAWN))),
    "EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this page was drawn (2026-10-24 09:15 UTC), so a later read of the same hour can differ.");
  assert.equal(P.DRAWN_ATTR, "data-eia930-drawn");
  assert.ok(!P.EIA930_PRELIMINARY.includes(String.fromCharCode(0x2014)));
});

await test("check-values reads the rule, the note's line and the page's clock, and counts revised lines apart", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('import * as REV from "./check-revised.mjs";'));
  assert.ok(cv.includes('path.join(here, "..", "..", "docs", "methods", "grid_network.md")'));
  assert.ok(cv.includes("const drawn = REV.drawnOf(html);"));
  assert.ok(cv.includes("j.pass ? out.revised++ : out.bad++;"));
  assert.ok(cv.includes("EIA-930 hours revised after the page was drawn"));
  // every other difference still fails: the rule is asked only of a value that differs on a text that holds
  assert.ok(cv.includes("if (!pass && !ev && t !== undefined && t !== null && !same && textHolds && REV.revisedKey(check)) {"));
});

// ---- end to end: check-values against a page and a Supabase of this test's own ----

// license_status.csv as check-values reads it (its licCsv), for ten lic| keys judged from warehouse/metadata alone, so the
// run has check-values' floor of ten values beside the two EIA-930 hours (the slow test's keys)
function csv(text) {
  const rows = [];
  let row = [], cell = "", q = false;
  text = text.replace(/\r\n/g, "\n");
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') q = false; else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(cell); cell = ""; }
    else if (ch === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows;
  return body.filter((r) => r.length >= head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}
const held = csv(fs.readFileSync(path.join(here, "..", "..", "warehouse", "metadata", "license_status.csv"), "utf-8")).filter((r) => r.status === "license needed");
const pubs = [...new Set(held.flatMap((r) => r.publishers.split(";").map((x) => x.trim())).filter(Boolean))].sort().slice(0, 11);
const LIC = [["lic|held|count", held.length], ...pubs.map((p) => [`lic|held|pub|${p}`, held.filter((r) => r.publishers.split(";").map((x) => x.trim()).includes(p)).length])];
assert.ok(LIC.length >= 10);

let withWrong = true;
const span = (k, raw, text) => `<span data-check="${k.replace(/&/g, "&amp;")}" data-raw="${raw}">${text}</span>`;
const pageHtml = () => `<!doctype html><main>${LIC.map(([k, v]) => span(k, String(v), String(v))).join(" ")} ${span(REVISED.check, REVISED.raw, REVISED.text)}${
  withWrong ? ` ${span(WRONG.check, WRONG.raw, WRONG.text)}` : ""}</main>${html}`;
const ROWS = new Map([REVISED, WRONG].map((x) => [x.check.split("|")[4], x]));
const server = http.createServer((req, res) => {
  const u = new URL(req.url, "http://x");
  if (req.method === "POST" && u.pathname === "/internal/unlock") {
    res.writeHead(303, { "Set-Cookie": "erw_internal=t; Path=/", Location: "/" });
    return res.end();
  }
  if (u.pathname === "/rest/v1/series") {   // Supabase's REST API, for the two hours' rows only
    const at = (u.searchParams.get("ts_utc") ?? "").replace(/^eq\./, "");
    const x = u.searchParams.get("table_name") === "eq.eia930_all_demand" && u.searchParams.get("entity") === "eq.eia930:MISO" ? ROWS.get(at) : null;
    const body = !x ? [] : (u.searchParams.get("select") ?? "").includes("loaded_at") ? [x.row] : [{ value: x.value, ts_utc: at }];
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(body));
  }
  res.writeHead(200, { "Content-Type": "text/html" });
  res.end(pageHtml());
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cv1171-"));
const FLOORS = path.join(here, "check-values-floor.json");
const floorsBefore = fs.readFileSync(FLOORS, "utf-8");
const CRASH = 3221226505;   // node on Windows, a libuv assertion at exit (scripts/test-check-values-slow.mjs): run once more
let runs = 0;
const run1 = () => new Promise((resolve) => {
  const child = spawn(process.execPath, [path.join(here, "check-values.mjs"), base], {
    cwd: path.join(here, ".."),
    env: { ...process.env, SUPABASE_URL: base, SUPABASE_ANON_KEY: "test", INTERNAL_COSTS_TOKEN: "t", CHECK_VALUES_PAGES: "/data/licenses",
      CHECK_VALUES_STATE: path.join(dir, `state-${++runs}.json`), CHECK_VALUES_WRITE_FLOOR: "", CHECK_VALUES_RESUME: "" },
  });
  let out = "";
  child.stdout.on("data", (d) => (out += d));
  child.stderr.on("data", (d) => (out += d));
  child.on("close", (code) => resolve({ code, out }));
});
const run = async () => { const r = await run1(); return r.code === CRASH && r.out.includes("UV_HANDLE_CLOSING") ? run1() : r; };
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&");

try {
  await test("end to end: the revised hour is a revised line, the wrong one fails, the run exits 1", async () => {
    const r = await run();
    assert.equal(r.code, 1, r.out);
    assert.match(r.out, new RegExp(`^${esc(`revised | /data/licenses | ${REVISED.check} | page shows "77,486" | page read 77486, drawn ${DRAWN} | Supabase 77512, the row written 2026-10-24T15:33:56.000Z, after the page was drawn: a revision of EIA-930's preliminary hour, tolerated for eia930_all_demand by docs/methods/grid_network.md`)}$`, "m"));
    assert.match(r.out, new RegExp(`^${esc(`FAIL | /data/licenses | ${WRONG.check} | page shows "70,000" | page read 70000 | Supabase 77245 | the row was last written 2026-10-23T15:33:56.000Z, before the page was drawn ${DRAWN}: not a revision`)}$`, "m"));
    assert.match(r.out, new RegExp(`^${esc(`${LIC.length} of ${LIC.length + 2} values match Supabase; 1 EIA-930 hours revised after the page was drawn (the lines marked revised; tolerated by docs/methods/grid_network.md for eia930_all_demand, eia930_all_generation); 1 FAILED`)}`, "m"));
  });
  await test("end to end: with the wrong figure gone, the revised hour passes and the run exits 0", async () => {
    withWrong = false;
    const r = await run();
    assert.equal(r.code, 0, r.out);
    assert.match(r.out, new RegExp(`^${esc(`revised | /data/licenses | ${REVISED.check} |`)}`, "m"));
    assert.doesNotMatch(r.out, /^FAIL /m);
    assert.match(r.out, new RegExp(`^${esc(`${LIC.length} of ${LIC.length + 1} values match Supabase; 1 EIA-930 hours revised after the page was drawn`)}`, "m"));
  });
  await test("end to end: the same figure, its row written before the page was drawn, fails (the row the page read)", async () => {
    ROWS.set(REVISED.check.split("|")[4], { ...REVISED, row: { ...REVISED.row, loaded_at: "2026-10-24T09:00:00+00:00" } });
    const r = await run();
    assert.equal(r.code, 1, r.out);
    assert.match(r.out, new RegExp(`^${esc(`FAIL | /data/licenses | ${REVISED.check} | page shows "77,486" | page read 77486 | Supabase 77512 | the row was last written 2026-10-24T09:00:00.000Z, before the page was drawn ${DRAWN}: not a revision`)}$`, "m"));
    assert.doesNotMatch(r.out, /^revised /m);
  });
  await test("no floor was written", async () => {
    assert.equal(fs.readFileSync(FLOORS, "utf-8"), floorsBefore);
  });
} finally {
  server.close();
  fs.rmSync(dir, { recursive: true, force: true });
}

console.log(`\n${n} of ${n} passed`);
