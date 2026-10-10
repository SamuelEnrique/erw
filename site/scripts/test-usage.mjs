// Energy Research Warehouse (ERW) site, session 177: the guards, the limit and the usage counts' rules, without a server
// and without a network (lib/guard.ts, lib/usage.ts, lib/usagepath.ts).
//
//   node --import ./scripts/alias-register.mjs scripts/test-usage.mjs
//
// Exits 1 on the first failure.
import assert from "node:assert/strict";

const guard = await import("../lib/guard.ts");
const usage = await import("../lib/usage.ts");
const up = await import("../lib/usagepath.ts");
const { visitorKey, utcDay } = await import("../lib/chat/limits.ts");

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
const req = (headers = {}, url = "https://erw.example/api/x") => new Request(url, { method: "POST", headers });

await test("sameOrigin: no Origin passes; this site's passes; another site's, null and cross-site do not", () => {
  assert.equal(guard.sameOrigin(req({ host: "erw.example" })), true);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "https://erw.example" })), true);
  assert.equal(guard.sameOrigin(req({ host: "internal:3000", "x-forwarded-host": "erw.example", origin: "https://erw.example" }, "http://internal:3000/api/x")), true);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "https://evil.example" })), false);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "null" })), false);
  // a browser writes "null" on a form posted from a page whose referrer policy is no-referrer: only its own word
  // that the request is same-origin lets it through
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "null", "sec-fetch-site": "same-origin" })), true);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "null", "sec-fetch-site": "same-site" })), false);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "null", "sec-fetch-site": "none" })), false);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "null", "sec-fetch-site": "cross-site" })), false);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", "sec-fetch-site": "cross-site" })), false);
  assert.equal(guard.sameOrigin(req({ host: "erw.example", origin: "https://erw.example.evil.example" })), false);
});

await test("scripted: an empty or stock user agent is; a browser and Node's own fetch are not", () => {
  for (const ua of ["", "x", "curl/8.4.0", "python-requests/2.32", "Python-urllib/3.12", "Go-http-client/2.0", "Scrapy/2.11", "Wget/1.21", "axios/1.7"]) {
    assert.equal(guard.scripted(req({ "user-agent": ua })), true, ua);
  }
  for (const ua of ["node", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15"]) {
    assert.equal(guard.scripted(req({ "user-agent": ua })), false, ua);
  }
  assert.equal(guard.scripted(req({ "user-agent": "M".repeat(700) })), true);
});

await test("typed: JSON and a beacon's text are JSON; a form is a form", () => {
  assert.equal(guard.typed(req({ "content-type": "application/json" }), "json"), true);
  assert.equal(guard.typed(req({ "content-type": "text/plain;charset=UTF-8" }), "json"), true);
  assert.equal(guard.typed(req({ "content-type": "application/x-www-form-urlencoded" }), "json"), false);
  assert.equal(guard.typed(req({}), "json"), false);
  assert.equal(guard.typed(req({ "content-type": "application/x-www-form-urlencoded" }), "form"), true);
});

await test("sameSecret: equal strings only, and never the empty one", () => {
  assert.equal(guard.sameSecret("a-token-of-some-length-0000", "a-token-of-some-length-0000"), true);
  assert.equal(guard.sameSecret("a-token-of-some-length-0000", "a-token-of-some-length-0001"), false);
  assert.equal(guard.sameSecret("short", "a-token-of-some-length-0000"), false);
  assert.equal(guard.sameSecret("", ""), false);
});

await test("memoryCount: the limit, the window and the wait", () => {
  const store = new Map();
  const t0 = 1_760_000_000_000;
  for (let i = 0; i < 3; i++) assert.equal(guard.memoryCount("k", 3, 60_000, t0 + i, store).ok, true);
  const refused = guard.memoryCount("k", 3, 60_000, t0 + 10, store);
  assert.equal(refused.ok, false);
  assert.equal(refused.retryAfter, 60);
  assert.equal(guard.memoryCount("other", 3, 60_000, t0 + 10, store).ok, true);
  assert.equal(guard.memoryCount("k", 3, 60_000, t0 + 60_001, store).ok, true);   // the first has left the window
});

const SALT = "a-stand-in-salt-of-enough-length", TOKEN = "a-stand-in-token-of-enough-length";
const base = { bucket: "trial", limit: 5, windowS: 3600, now: Date.UTC(2026, 9, 10, 12), salt: SALT, token: TOKEN };

await test("decide: the database's yes and no are taken, and it is sent a hash, never an address", async () => {
  const calls = [];
  const yes = await guard.decide({ ...base, ip: "203.0.113.9", store: new Map(), call: async (a) => { calls.push(a); return { ok: true }; } });
  assert.deepEqual(yes, { ok: true, retryAfter: 0, by: "database" });
  assert.equal(calls[0].p_visitor, visitorKey("203.0.113.9", utcDay(base.now), SALT));
  assert.match(calls[0].p_visitor, /^[0-9a-f]{32}$/);
  assert.ok(!JSON.stringify(calls[0]).includes("203.0.113.9"));
  assert.equal(calls[0].p_token, TOKEN);
  const no = await guard.decide({ ...base, ip: "203.0.113.9", store: new Map(), call: async () => ({ ok: false, reason: "limit", retry_after: 77 }) });
  assert.deepEqual(no, { ok: false, retryAfter: 77, by: "database" });
});

await test("decide: when the database cannot be asked, the memory's count decides (the floor the routes had)", async () => {
  const store = new Map();
  const failing = async () => { throw new Error("Supabase rpc site_rate_admit: HTTP 404"); };
  for (let i = 0; i < 5; i++) assert.deepEqual(await guard.decide({ ...base, ip: "203.0.113.9", store, call: failing }), { ok: true, retryAfter: 0, by: "memory" });
  const sixth = await guard.decide({ ...base, ip: "203.0.113.9", store, call: failing });
  assert.equal(sixth.ok, false);
  assert.equal(sixth.by, "memory");
  // no salt, no token, an unknown address, an answer that is neither yes nor a limit: the database is not what decides
  let asked = 0;
  const count = async () => { asked += 1; return { ok: true }; };
  assert.equal((await guard.decide({ ...base, ip: "203.0.113.9", salt: null, store: new Map(), call: count })).by, "memory");
  assert.equal((await guard.decide({ ...base, ip: "203.0.113.9", token: "short", store: new Map(), call: count })).by, "memory");
  assert.equal((await guard.decide({ ...base, ip: "unknown", store: new Map(), call: count })).by, "memory");
  assert.equal(asked, 0);
  assert.deepEqual(await guard.decide({ ...base, ip: "203.0.113.9", store: new Map(), call: async () => ({ ok: false, reason: "config" }) }), { ok: true, retryAfter: 0, by: "memory" });
});

await test("decide: one count for everybody when no address is given", async () => {
  const calls = [];
  await guard.decide({ ...base, ip: null, store: new Map(), call: async (a) => { calls.push(a); return { ok: true }; } });
  assert.equal(calls[0].p_visitor, visitorKey("everybody", utcDay(base.now), SALT));
});

await test("usageVisitor: 64 hexadecimal characters, of the address and the user agent, under the secret", () => {
  const a = guard.usageVisitor("203.0.113.9", "Mozilla/5.0 A", SALT);
  assert.match(a, /^[0-9a-f]{64}$/);
  assert.equal(a, guard.usageVisitor("203.0.113.9", "Mozilla/5.0 A", SALT));
  assert.notEqual(a, guard.usageVisitor("203.0.113.10", "Mozilla/5.0 A", SALT));
  assert.notEqual(a, guard.usageVisitor("203.0.113.9", "Mozilla/5.0 B", SALT));
  assert.notEqual(a, guard.usageVisitor("203.0.113.9", "Mozilla/5.0 A", SALT + "x"));
  assert.ok(!a.includes("203"));
});

await test("optedOut: Do Not Track and Global Privacy Control send nothing", () => {
  assert.equal(usage.optedOut({ doNotTrack: "1" }), true);
  assert.equal(usage.optedOut({ doNotTrack: "yes" }), true);
  assert.equal(usage.optedOut({ globalPrivacyControl: true }), true);
  assert.equal(usage.optedOut({}, { doNotTrack: "1" }), true);
  assert.equal(usage.optedOut(undefined), true);
  assert.equal(usage.optedOut({ doNotTrack: "0" }), false);
  assert.equal(usage.optedOut({ doNotTrack: null, globalPrivacyControl: false }), false);
  assert.equal(usage.optedOut({ doNotTrack: "unspecified" }), false);
});

await test("track: never throws, and sends nothing without a browser", () => {
  assert.doesNotThrow(() => usage.track("tool opened"));
  assert.doesNotThrow(() => usage.track("scenario compared", { path: "/cost-of-power/battery" }));
});

await test("isDownload, quiet and the promise", () => {
  const o = "https://erw.example";
  assert.equal(usage.isDownload({ hasDownload: true, href: "blob:x" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/api/download?table=energy_deals" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/findings/card.csv" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/findings/card.do" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/findings/card.py" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/severance/finder/download" }, o), true);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/storage" }, o), false);
  assert.equal(usage.isDownload({ hasDownload: false, href: "/data?x=a.csv" }, o), false);
  assert.equal(usage.quiet("/battery/customer"), true);
  assert.equal(usage.quiet("/severance/lease"), true);
  assert.equal(usage.quiet("/storage"), false);
  assert.match("Computed on this device. Nothing you type here is sent or stored.", usage.PROMISE);
  assert.match("Your file is read in your browser and never sent.", usage.PROMISE);
});

await test("cleanPath: a page of this site, without its query; anything else is not counted", () => {
  assert.equal(up.cleanPath("/storage"), "/storage");
  assert.equal(up.cleanPath("/storage/?a=1#x"), "/storage");
  assert.equal(up.cleanPath("/"), "/");
  assert.equal(up.cleanPath("/grid/ercot"), "/grid/ercot");
  assert.equal(up.cleanPath("/roundup/2026-W40"), "/roundup/2026-W40");
  assert.equal(up.cleanPath("/prices/ercot%3AHB_HUBAVG"), "/prices/ercot%3AHB_HUBAVG");
  for (const bad of ["/not-a-page", "/api/ask", "/internal/costs", "/_next/static/x.js", "storage", "//evil.example/x", "/storage/../x", "/storage/<script>", "/storage/" + "a".repeat(130), 7, null, undefined, {}]) {
    assert.equal(up.cleanPath(bad), null, String(bad));
  }
});

await test("toolOf: the menu's own names, by the nearest parent", () => {
  assert.equal(up.toolOf("/storage"), "Storage");
  assert.equal(up.toolOf("/storage/buildout"), "Storage build-out");
  assert.equal(up.toolOf("/cost-of-power/battery"), "What a battery earns");
  assert.equal(up.toolOf("/cost-of-power/battery/awards"), "What a battery earns");
  assert.equal(up.toolOf("/grid/ercot"), "ERCOT");
  assert.equal(up.toolOf("/terms"), "Terms");
  assert.equal(up.toolOf("/privacy"), "");
  assert.equal(up.isEvent("tool opened") && up.isEvent("input changed") && up.isEvent("scenario compared") && up.isEvent("download"), true);
  assert.equal(up.isEvent("clicked"), false);
  assert.equal(up.EVENTS.length, 4);
});

console.log(`${n} tests passed`);
