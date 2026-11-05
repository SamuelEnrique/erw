// Energy Research Warehouse (ERW) site, session 430: check-values.mjs on a slow site, end to end, against a small server
// of its own. The pages carry `lic|` keys, which check-values judges from warehouse/metadata alone (no Supabase), so the
// test needs no build, no database and no network beyond 127.0.0.1. It proves:
//   1. a page slower than CHECK_VALUES_PAGE_S is tried twice, listed as not read, and the run ends with exit 3 (not 0);
//   2. a second run with CHECK_VALUES_RESUME=1 reads only the pages the first left, and passes with exit 0;
//   3. a value that differs still fails with exit 1, and a floor still fails on a page read;
//   4. CHECK_VALUES_WRITE_FLOOR=1 writes nothing from an incomplete run.
//
//   node scripts/test-check-values-slow.mjs
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const meta = (f) => fs.readFileSync(path.join(here, "..", "..", "warehouse", "metadata", f), "utf-8");

// license_status.csv as check-values reads it (its licCsv: quoted cells, doubled quotes)
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
const held = csv(meta("license_status.csv")).filter((r) => r.status === "license needed");
const pubs = [...new Set(held.flatMap((r) => r.publishers.split(";").map((x) => x.trim())).filter(Boolean))].sort().slice(0, 11);
const KEYS = [["lic|held|count", held.length], ...pubs.map((p) => [`lic|held|pub|${p}`, held.filter((r) => r.publishers.split(";").map((x) => x.trim()).includes(p)).length])];
assert.ok(KEYS.length >= 10, "at least ten keys to pass check-values' floor of ten a run");

const page = (keys, wrong = false) => `<!doctype html><main>${keys.map(([k, v], i) => {
  const raw = wrong && i === 0 ? String(v + 1) : String(v);
  return `<span data-check="${k.replace(/&/g, "&amp;")}" data-raw="${raw}">${raw}</span>`;
}).join(" ")}</main>`;

// the server: /data/licenses is quick; every /storage page is slow while `slow` is set; hits are counted
let slow = true, wrong = false;
const hits = {};
const server = http.createServer((req, res) => {
  const u = new URL(req.url, "http://x");
  if (req.method === "POST" && u.pathname === "/internal/unlock") {
    res.writeHead(303, { "Set-Cookie": "erw_internal=t; Path=/", Location: "/" });
    return res.end();
  }
  const p = u.pathname + u.search;
  hits[p] = (hits[p] ?? 0) + 1;
  const send = () => { res.writeHead(200, { "Content-Type": "text/html" }); res.end(page(KEYS, wrong)); };
  if (slow && u.pathname.startsWith("/storage")) {
    const t = setTimeout(send, 2500);
    res.on("close", () => clearTimeout(t));
    return;
  }
  send();
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cv430-"));
const STATE = path.join(dir, "state.json");
const FLOORS = path.join(here, "check-values-floor.json");
const floorsBefore = fs.readFileSync(FLOORS, "utf-8");

// Node on Windows can end a child that calls process.exit with 0xC0000409 (3221226505, "UV_HANDLE_CLOSING", a libuv
// assertion while a socket closes): seen once in six runs on a loaded machine on 21 October. A run that ends so is run
// once more, and only for that signature; any other code is the run's own.
const CRASH = 3221226505;
async function run(extra = {}) {
  const r = await run1(extra);
  return r.code === CRASH && r.out.includes("UV_HANDLE_CLOSING") ? run1(extra) : r;
}
function run1(extra = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [path.join(here, "check-values.mjs"), base], {
      cwd: path.join(here, ".."),
      env: {
        ...process.env, SUPABASE_URL: "http://127.0.0.1:9", SUPABASE_ANON_KEY: "test", INTERNAL_COSTS_TOKEN: "t",
        CHECK_VALUES_PAGES: "/data/licenses,/storage", CHECK_VALUES_PAGE_S: "1", CHECK_VALUES_BATCH: "2",
        CHECK_VALUES_STATE: STATE, CHECK_VALUES_WRITE_FLOOR: "", CHECK_VALUES_RESUME: "", ...extra,
      },
    });
    let out = "";
    child.stdout.on("data", (d) => (out += d));
    child.stderr.on("data", (d) => (out += d));
    child.on("close", (code) => resolve({ code, out }));
  });
}

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
try {
  let first;
  await test("a slow page is tried twice, listed as not read, and the run ends with exit 3", async () => {
    first = await run({ CHECK_VALUES_WRITE_FLOOR: "1" });
    assert.equal(first.code, 3, first.out);
    assert.match(first.out, /^not read \| \/storage \| timed out twice \| its numbers and its floor are not judged$/m);
    assert.match(first.out, /^retry \| \/storage \| timed out once; tried again$/m);
    assert.match(first.out, /^ok   \| \/data\/licenses \| lic\|held\|count \|/m);
    assert.match(first.out, /check-values INCOMPLETE: \d+ pages not read; every value read matched/);
    assert.equal(hits["/storage"], 2);
    assert.equal(hits["/data/licenses"], 1);
    assert.doesNotMatch(first.out, /^FAIL \| \/storage[^|]* \| the floor/m);   // a page not read: its floor (10) is not judged
  });
  await test("an incomplete run writes no floor", async () => {
    assert.match(first.out, /the floor file was not written: the run did not pass \(not every page was read\)/);
    assert.equal(fs.readFileSync(FLOORS, "utf-8"), floorsBefore);
  });
  await test("a second run with CHECK_VALUES_RESUME=1 reads only what the first left, and passes", async () => {
    slow = false;
    const second = await run({ CHECK_VALUES_RESUME: "1" });
    assert.equal(second.code, 0, second.out);
    assert.match(second.out, /^resumed from /m);
    assert.equal(hits["/data/licenses"], 1);   // not read again
    assert.equal(hits["/storage"], 3);
    assert.doesNotMatch(second.out, /^not read \|/m);
    assert.match(second.out, /^ok   \| \/data\/licenses \| lic\|held\|count \|/m);   // the first run's lines are reported whole
  });
  await test("a value that differs still fails, exit 1", async () => {
    wrong = true;
    const r = await run();
    assert.equal(r.code, 1, r.out);
    assert.match(r.out, /^FAIL \| \/[^|]* \| lic\|held\|count \|/m);   // judged on the first page in check-values' order that carries it
    wrong = false;
  });
  await test("a floor still fails on a page read", async () => {
    const thin = http.createServer((req, res) => {
      if (req.method === "POST") { res.writeHead(303, { "Set-Cookie": "erw_internal=t; Path=/", Location: "/" }); return res.end(); }
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(page(req.url.startsWith("/storage") ? KEYS.slice(0, 2) : KEYS));
    });
    await new Promise((r) => thin.listen(0, "127.0.0.1", r));
    const b2 = `http://127.0.0.1:${thin.address().port}`;
    const thinRun = () => new Promise((resolve) => {
      const child = spawn(process.execPath, [path.join(here, "check-values.mjs"), b2], {
        cwd: path.join(here, ".."),
        env: { ...process.env, SUPABASE_URL: "http://127.0.0.1:9", SUPABASE_ANON_KEY: "test", INTERNAL_COSTS_TOKEN: "t", CHECK_VALUES_PAGES: "/data/licenses,/storage", CHECK_VALUES_STATE: path.join(dir, "thin.json"), CHECK_VALUES_WRITE_FLOOR: "", CHECK_VALUES_RESUME: "" },
      });
      let out = "";
      child.stdout.on("data", (d) => (out += d));
      child.stderr.on("data", (d) => (out += d));
      child.on("close", (code) => resolve({ code, out }));
    });
    let r = await thinRun();
    if (r.code === CRASH && r.out.includes("UV_HANDLE_CLOSING")) r = await thinRun();
    thin.close();
    assert.equal(r.code, 1, r.out);
    assert.match(r.out, /^FAIL \| \/storage \| the floor \| the page carries 2 checked numbers; its floor is 10/m);
  });
} finally {
  server.close();
  fs.rmSync(dir, { recursive: true, force: true });
  assert.equal(fs.readFileSync(FLOORS, "utf-8"), floorsBefore, "the floor file is as it was");
}
console.log(`\n${n} tests passed`);
