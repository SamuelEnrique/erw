// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): the pf| key (lib/pagefile.ts), a figure read
// from a committed page file. Two parts:
//   1. the pure resolver: keys, indexes, selectors (one field and several), escapes, and every way a path can fail;
//   2. check-values.mjs end to end against a small server of its own, on a small real file (site/data/regions/trade/car.json):
//      every pf| key and a calc| of two pf| keys pass with exit 0, and one wrong value fails with exit 1. No build, no
//      database, no network beyond 127.0.0.1.
//
//   node scripts/test-pagefile.mjs        (from site/; lib/pagefile.ts imports only node:fs and node:path)
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { escapeSegment, fileHead, parsePf, pfKey, pfValue, resolveNumber, resolvePath } from "../lib/pagefile.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(here, "..", "data");
let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };

await test("the resolver walks keys, indexes and selectors", () => {
  const doc = { a: { b: [10, 20, 30] }, rows: [{ id: "x", y: 1, v: 5 }, { id: "y", y: 1, v: 6 }, { id: "y", y: 2, v: 7 }], "w/eird": { "k=1": 9 } };
  assert.equal(resolvePath(doc, "a/b/1"), 20);
  assert.equal(resolvePath(doc, "rows/@id=x/v"), 5);
  assert.equal(resolvePath(doc, "rows/@id=y/v"), undefined, "two elements match: no figure");
  assert.equal(resolvePath(doc, "rows/@id=y+y=2/v"), 7);
  assert.equal(resolvePath(doc, "rows/@y=2+id=y/v"), 7, "the fields in any order");
  assert.equal(resolvePath(doc, `${escapeSegment("w/eird")}/${escapeSegment("k=1")}`), 9);
  assert.equal(resolvePath(doc, ""), doc);
});

await test("the resolver gives undefined, never a guess, where a path fails", () => {
  const doc = { a: [1, 2], o: { n: null, s: "7", z: 0 } };
  for (const p of ["a/2", "a/x", "a/-1", "o/m", "o/n/q", "a/@id=1", "o/@id=1", "a/0/x", "o/%E0%A4%A"]) assert.equal(resolvePath(doc, p), undefined, p);
  assert.equal(resolveNumber(doc, "o/s"), undefined, "a string is not a figure");
  assert.equal(resolveNumber(doc, "o/n"), undefined, "null is not a figure");
  assert.equal(resolveNumber(doc, "o/z"), 0, "zero is");
  assert.equal(resolvePath({ "__proto__x": 1 }, "constructor"), undefined, "only the object's own keys");
});

await test("a key is built and parsed, and a file outside site/data is refused", () => {
  const k = pfKey("regions/trade_matrix.json", ["region_pairs", { a: "MIDA", b: "TEN", year: 2019 }, "gap_mwh"]);
  assert.equal(k, "pf|regions/trade_matrix.json|region_pairs/@a=MIDA+b=TEN+year=2019/gap_mwh");
  assert.deepEqual(parsePf(k), { file: "regions/trade_matrix.json", path: "region_pairs/@a=MIDA+b=TEN+year=2019/gap_mwh" });
  assert.equal(pfKey("x.json", ["a|b~c"]), "pf|x.json|a%7Cb%7Ec", "| and ~ never reach the key");
  for (const bad of ["pf|../secret.json|a", "pf|/abs.json|a", "pf|x.txt|a", "pf|a//b.json|a", "pf|x.json", "series|x|y"]) assert.equal(parsePf(bad), null, bad);
});

await test("a real file: a figure and its header", () => {
  const t = JSON.parse(fs.readFileSync(path.join(DATA, "regions", "trade", "car.json"), "utf-8"));
  const c = Object.keys(t.neighbors)[0], i = t.months.length - 2;
  assert.equal(pfValue(pfKey("regions/trade/car.json", ["neighbors", c, "net_imports_mwh", i]), DATA), t.neighbors[c].net_imports_mwh[i]);
  assert.deepEqual(fileHead("regions/trade/car.json", DATA).tables, t.tables);
  assert.equal(fileHead("resources/manifest.json", DATA).tables.length, 0, "the list of layers names no table");
});

// ---------------------------------------------------------------- check-values end to end
const FILE = "regions/trade/car.json";
const t = JSON.parse(fs.readFileSync(path.join(DATA, ...FILE.split("/")), "utf-8"));
const KEYS = [];
for (const c of Object.keys(t.neighbors)) for (const f of ["net_imports_mwh", "their_report_mwh", "gap_mwh", "hours_own"]) {
  const i = t.months.length - 2;
  if (typeof t.neighbors[c][f][i] === "number") KEYS.push([pfKey(FILE, ["neighbors", c, f, i]), t.neighbors[c][f][i]]);
}
const [ka, va] = KEYS[0], [kb, vb] = KEYS[1];
KEYS.push([`calc|ratio|${ka.replaceAll("|", "~")}|${kb.replaceAll("|", "~")}`, va / vb]);
assert.ok(KEYS.length >= 10, `at least ten keys for check-values' floor of ten (got ${KEYS.length})`);

const shown = (v) => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
let wrong = false;
const page = () => `<!doctype html><main>${KEYS.map(([k, v], i) => {
  const raw = wrong && i === 0 ? v + 1 : v;
  return `<span data-check="${k.replace(/&/g, "&amp;")}" data-raw="${raw}">${shown(raw)}</span>`;
}).join(" ")}</main>`;
const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url.startsWith("/internal/unlock")) { res.writeHead(303, { "Set-Cookie": "erw_internal=t; Path=/", Location: "/" }); return res.end(); }
  res.writeHead(200, { "Content-Type": "text/html" });
  res.end(page());
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cv8901-"));
const FLOORS = path.join(here, "check-values-floor.json");
const floorsBefore = fs.readFileSync(FLOORS, "utf-8");
const CRASH = 3221226505;  // a libuv assertion on Windows at a child's exit (see test-check-values-slow.mjs): run once more
const run1 = () => new Promise((resolve) => {
  const child = spawn(process.execPath, [path.join(here, "check-values.mjs"), base], {
    cwd: path.join(here, ".."),
    env: { ...process.env, SUPABASE_URL: "http://127.0.0.1:9", SUPABASE_ANON_KEY: "test", INTERNAL_COSTS_TOKEN: "t", CHECK_VALUES_PAGES: "/learn/problems/who-trades-with-whom",
      CHECK_VALUES_PAGE_S: "60", CHECK_VALUES_STATE: path.join(dir, "state.json"), CHECK_VALUES_WRITE_FLOOR: "", CHECK_VALUES_RESUME: "" },
  });
  let out = "";
  child.stdout.on("data", (d) => (out += d));
  child.stderr.on("data", (d) => (out += d));
  child.on("close", (code) => resolve({ code, out }));
});
const run = async () => { const r = await run1(); return r.code === CRASH ? run1() : r; };
try {
  await test("check-values recomputes every pf| key and a calc of two from the file: exit 0", async () => {
    const r = await run();
    assert.equal(r.code, 0, r.out.slice(-3000));
    for (const [k] of KEYS) assert.ok(r.out.includes(`ok   | /learn/problems/who-trades-with-whom | ${k} |`), `${k}\n${r.out.slice(-1500)}`);
  });
  await test("a value that differs from the file fails: exit 1", async () => {
    wrong = true;
    const r = await run();
    assert.equal(r.code, 1, r.out.slice(-3000));
    assert.ok(r.out.includes(`FAIL | /learn/problems/who-trades-with-whom | ${KEYS[0][0]} |`), r.out.slice(-1500));
  });
  assert.equal(fs.readFileSync(FLOORS, "utf-8"), floorsBefore, "no floor written");
} finally {
  server.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
console.log(`${n} tests passed`);
