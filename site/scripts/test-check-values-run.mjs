// Energy Research Warehouse (ERW) site, session 430: how check-values.mjs reads its pages on a slow database
// (scripts/check-values-run.mjs): the batches, a page's timeout and its one retry, the list of pages not read, the
// run's limit, and the state a second run resumes from. Needs no build, no network and no node_modules.
//
//   node scripts/test-check-values-run.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import * as RUN from "./check-values-run.mjs";

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
const sleep = (ms, signal) => new Promise((resolve, reject) => {
  const t = setTimeout(resolve, ms);
  signal?.addEventListener("abort", () => { clearTimeout(t); reject(signal.reason); }, { once: true });
});
const pages = (k) => Array.from({ length: k }, (_, i) => `/p${i + 1}`);
const far = () => Date.now() + 60_000;

await test("the pages are read in order, in batches, and the state is offered after each batch", async () => {
  const order = [], batches = [];
  const r = await RUN.runPages({
    pages: pages(25), batch: 10, pageMs: 1000, deadline: far(),
    readPage: async (p) => { order.push(p); return { page: p }; },
    onBatch: ({ results }) => batches.push(results.size),
  });
  assert.deepEqual(order, pages(25));
  assert.deepEqual(batches, [10, 20, 25]);
  assert.equal(r.results.size, 25);
  assert.deepEqual(r.notRead, []);
  assert.deepEqual(r.retried, []);
});

await test("a page past its limit is aborted, waits, and is tried once more after the last page", async () => {
  const order = [], aborted = [];
  let tries = 0;
  const r = await RUN.runPages({
    pages: ["/a", "/slow-once", "/b"], batch: 10, pageMs: 60, deadline: far(),
    readPage: async (p, signal) => {
      order.push(p);
      if (p === "/slow-once" && tries++ === 0) {
        signal.addEventListener("abort", () => aborted.push(p), { once: true });
        await sleep(1000, signal);
      }
      return { page: p };
    },
  });
  assert.deepEqual(order, ["/a", "/slow-once", "/b", "/slow-once"]);   // the retry comes after the last page
  assert.deepEqual(aborted, ["/slow-once"]);                         // its requests were aborted at its limit
  assert.deepEqual(r.retried, ["/slow-once"]);
  assert.equal(r.results.get("/slow-once").page, "/slow-once");
  assert.deepEqual(r.notRead, []);
});

await test("a page that times out twice is listed as not read, and only once tried again", async () => {
  let tries = 0;
  const r = await RUN.runPages({
    pages: ["/a", "/slow", "/b"], batch: 2, pageMs: 40, deadline: far(),
    readPage: async (p, signal) => { if (p === "/slow") { tries++; await sleep(1000, signal); } return { page: p }; },
  });
  assert.equal(tries, 2);
  assert.deepEqual(r.notRead, [{ page: "/slow", why: "timed out twice" }]);
  assert.ok(!r.results.has("/slow"));
  assert.deepEqual([...r.results.keys()], ["/a", "/b"]);
});

await test("an error that is not slowness is the page's result, not retried and not 'not read'", async () => {
  let tries = 0;
  const r = await RUN.runPages({
    pages: ["/broken", "/a"], pageMs: 1000, deadline: far(),
    readPage: async (p) => { if (p === "/broken") { tries++; throw new Error("/broken: HTTP 500"); } return { page: p }; },
  });
  assert.equal(tries, 1);
  assert.equal(r.results.get("/broken").error.message, "/broken: HTTP 500");
  assert.deepEqual(r.notRead, []);
});

await test("a statement timeout from Supabase or a 504 counts as slowness: the page is tried again", async () => {
  const seen = {};
  const r = await RUN.runPages({
    pages: ["/q", "/g"], pageMs: 1000, deadline: far(),
    readPage: async (p) => {
      seen[p] = (seen[p] ?? 0) + 1;
      if (seen[p] === 1) throw new Error(p === "/q" ? 'series: HTTP 500 {"code":"57014"}' : `${p}: HTTP 504`);
      return { page: p };
    },
  });
  assert.deepEqual(seen, { "/q": 2, "/g": 2 });
  assert.deepEqual(r.notRead, []);
});

await test("past the run's limit no page starts; each is listed with why", async () => {
  let clock = 0;
  const r = await RUN.runPages({
    pages: pages(5), batch: 2, pageMs: 1000, deadline: 3, now: () => clock,
    readPage: async (p) => { clock += 1; return { page: p }; },
  });
  assert.deepEqual([...r.results.keys()], ["/p1", "/p2", "/p3"]);
  assert.deepEqual(r.notRead.map((x) => x.page), ["/p4", "/p5"]);
  assert.ok(r.notRead.every((x) => x.why === "the run's limit was reached before it was read"));
});

await test("a page that timed out when the limit leaves no time for its retry is listed, not tried", async () => {
  let clock = 0, tries = 0;
  const r = await RUN.runPages({
    pages: ["/slow", "/a"], pageMs: 30, deadline: 2, now: () => clock,
    readPage: async (p, signal) => { clock += 1; if (p === "/slow") { tries++; await sleep(1000, signal); } return { page: p }; },
  });
  assert.equal(tries, 1);
  assert.deepEqual(r.notRead, [{ page: "/slow", why: "timed out once; the run's limit left no time to try it again" }]);
});

await test("the pages an earlier run read are not read again", async () => {
  const order = [];
  const r = await RUN.runPages({
    pages: pages(4), pageMs: 1000, deadline: far(), done: new Set(["/p1", "/p3"]),
    readPage: async (p) => { order.push(p); return { page: p }; },
  });
  assert.deepEqual(order, ["/p2", "/p4"]);
  assert.equal(r.results.size, 2);
});

await test("isTimeout: slowness against faults", async () => {
  const named = (name) => Object.assign(new Error("x"), { name });
  assert.ok(RUN.isTimeout(named("TimeoutError")));
  assert.ok(RUN.isTimeout(named("AbortError")));
  assert.ok(RUN.isTimeout(new Error('series: HTTP 500 {"code":"57014","message":"canceling statement due to statement timeout"}')));
  assert.ok(RUN.isTimeout(new Error("/prices: HTTP 504")));
  assert.ok(RUN.isTimeout(new Error("/prices: HTTP 503")));
  assert.ok(!RUN.isTimeout(new Error("/prices: HTTP 500")));
  assert.ok(!RUN.isTimeout(new Error("/prices: the in-review page was served")));
  assert.ok(!RUN.isTimeout(new Error("unknown key")));
});

await test("the state file: written whole, read back for the same run, refused for another", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cv430-"));
  const file = path.join(dir, "sub", "state.json");
  const key = RUN.stateKey("http://localhost:3430", ["/b", "/a"]);
  assert.equal(key, RUN.stateKey("http://localhost:3430", ["/a", "/b"]));   // the order of CHECK_VALUES_PAGES does not matter
  RUN.saveState(file, { key, pages: { "/a": { ok: 3, bad: 0, keys: ["k1"] } } });
  assert.ok(!fs.existsSync(`${file}.tmp`));
  const back = RUN.loadState(file, key);
  assert.deepEqual(back.state.pages["/a"].keys, ["k1"]);
  const other = RUN.loadState(file, RUN.stateKey("https://erw-flame.vercel.app", []));
  assert.equal(other.state, null);
  assert.match(other.why, /written for another run/);
  assert.match(RUN.loadState(path.join(dir, "none.json"), key).why, /no state file/);
  fs.rmSync(dir, { recursive: true, force: true });
});

console.log(`\n${n} tests passed`);
