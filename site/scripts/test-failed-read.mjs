// Energy Research Warehouse (ERW) site, session 537: the proof, without a build, that a read which fails asks for a
// short revalidation of the page it was made for, and that a read which succeeds asks for nothing.
//
//   node --import ./scripts/alias-register.mjs scripts/test-failed-read.mjs
//
// lib/supabase.ts is imported as it is, with a stand-in for fetch (no request leaves this machine) and the alias
// loader's stand-in for next/cache, which notes every unstable_cache call in globalThis.__erwCacheCalls. NEXT_RUNTIME is
// set as Next sets it, so the mark is made where a page would make it. Each case fails a read on purpose (an HTTP 500
// with the statement timeout's code, past the request's two retries; a plain HTTP 500; a refused request; the second
// page of a large read; a count) or lets it succeed, and checks the marks: one mark of RETRY seconds, keyed
// "erw-failed-read", for each failed read; none for a read that succeeded, for a table held for a license, for a server
// with no database named, or outside Next. A required() read that fails still throws. A read that succeeds sends the
// revalidation it was given, unchanged. Prints one line a case; exit 0 when every case holds, 1 otherwise.
process.env.NEXT_RUNTIME = "nodejs";
process.env.SUPABASE_URL = "https://erw-session537.invalid/rest/v1/";
process.env.SUPABASE_ANON_KEY = "session537-test";
delete process.env.NEXT_PHASE;

const ORIGIN = "https://erw-session537.invalid";
const sent = [];
let answer = () => new Response("[]", { status: 200 });
globalThis.fetch = async (url, init) => {
  const u = new URL(String(url));
  if (u.origin !== ORIGIN) throw new Error(`a request this test does not make: ${u.origin}`);
  sent.push({ path: u.pathname, q: Object.fromEntries(u.searchParams), revalidate: init?.next?.revalidate });
  return answer(u);
};

const sb = await import("../lib/supabase.ts");
const lic = await import("../lib/license.ts");
const marks = () => (globalThis.__erwCacheCalls ?? []).length;
const json = (rows, status = 200, headers = {}) => new Response(JSON.stringify(rows), { status, headers: { "content-type": "application/json", ...headers } });
const TIMEOUT = () => new Response('{"code":"57014","message":"canceling statement due to statement timeout"}', { status: 500 });

let failures = 0;
async function check(name, f) {
  const before = marks();
  sent.length = 0;
  try {
    const why = await f(before);
    if (why) { failures++; console.log(`FAIL ${name}: ${why}`); }
    else console.log(`ok   ${name}`);
  } catch (e) {
    failures++;
    console.log(`FAIL ${name}: threw ${e?.message ?? e}`);
  }
}
const lastMark = () => (globalThis.__erwCacheCalls ?? []).at(-1);
const oneMark = (before) => {
  const n = marks() - before;
  if (n !== 1) return `${n} marks, 1 expected`;
  const m = lastMark();
  if (m.options?.revalidate !== sb.RETRY) return `the mark asked for ${m.options?.revalidate} seconds, not ${sb.RETRY}`;
  if (JSON.stringify(m.keyParts) !== '["erw-failed-read"]') return `the mark's key is ${JSON.stringify(m.keyParts)}`;
  return "";
};

await check("RETRY is a minute, shorter than either interval of the site", async () => (sb.RETRY === 60 && sb.RETRY < sb.LATEST && sb.RETRY < sb.HOURLY ? "" : `RETRY is ${sb.RETRY}`));

await check("a read that succeeds: no mark, and its own revalidation sent", async (before) => {
  answer = () => json([{ entity: "a", value: 1 }]);
  const r = await sb.attempt(() => sb.rest("series", { select: "entity,value", table_name: "eq.session537_ok" }, sb.HOURLY));
  if (!r.ok || r.data.length !== 1) return "the read did not come back";
  if (marks() !== before) return `${marks() - before} marks`;
  return sent.every((s) => s.revalidate === sb.HOURLY) ? "" : `revalidations sent: ${sent.map((s) => s.revalidate)}`;
});

await check("a large read that succeeds (three pages): no mark", async (before) => {
  answer = (u) => json(Array.from({ length: Number(u.searchParams.get("offset")) < 2000 ? 1000 : 10 }, (_, i) => ({ i })));
  const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_ok" }, sb.LATEST));
  if (!r.ok || r.data.length !== 2010) return `rows ${r.ok ? r.data.length : r.reason}`;
  return marks() === before ? (sent.every((s) => s.revalidate === sb.LATEST) ? "" : "a revalidation changed") : `${marks() - before} marks`;
});

await check("the statement timeout past the retries: no data, one mark of RETRY seconds", async (before) => {
  answer = TIMEOUT;
  const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_slow" }, sb.HOURLY));
  if (r.ok) return "the read came back";
  if (!r.reason.includes("57014")) return `reason ${r.reason}`;
  if (sent.length !== 3) return `${sent.length} requests, 3 expected (the request and its two retries, as before)`;
  return oneMark(before);
});

await check("a plain HTTP 500: one mark", async (before) => {
  answer = () => new Response("bad gateway", { status: 502 });
  const r = await sb.attempt(() => sb.rest("events", { table_name: "eq.session537_down" }, sb.HOURLY));
  return r.ok ? "the read came back" : oneMark(before);
});

await check("a refused request: one mark", async (before) => {
  answer = () => { throw new Error("connect ECONNREFUSED"); };
  const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_refused" }, sb.HOURLY));
  return r.ok ? "the read came back" : (r.reason.includes("request failed") ? oneMark(before) : `reason ${r.reason}`);
});

await check("the second page of a large read fails: one mark", async (before) => {
  answer = (u) => (Number(u.searchParams.get("offset")) === 0 ? json(Array.from({ length: 1000 }, (_, i) => ({ i }))) : new Response("no", { status: 500 }));
  const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_half" }, sb.HOURLY));
  return r.ok ? "the read came back" : oneMark(before);
});

await check("a count that fails: one mark; a count that succeeds: none", async (before) => {
  answer = () => new Response("no", { status: 500 });
  const r = await sb.attempt(() => sb.restCount("series", { table_name: "eq.session537_count" }, sb.HOURLY));
  if (r.ok) return "the count came back";
  const why = oneMark(before);
  if (why) return why;
  const mid = marks();
  answer = () => json([{}], 200, { "content-range": "0-0/42" });
  const n = await sb.restCount("series", { table_name: "eq.session537_count" }, sb.HOURLY);
  return n === 42 && marks() === mid ? "" : `count ${n}, ${marks() - mid} marks`;
});

await check("required(): a failed read still throws (and the render is never cached)", async (before) => {
  answer = () => new Response("no", { status: 500 });
  try {
    await sb.required(() => sb.rest("series", { table_name: "eq.session537_required" }, sb.LATEST));
  } catch (e) {
    return e instanceof sb.DataError ? oneMark(before) : `threw ${e}`;
  }
  return "required() did not throw";
});

await check("a table held for a license: not asked, not marked", async (before) => {
  const held = lic.licenseNeededTables().find((t) => !lic.licenseByGrid(t));
  if (!held) return "";   // no table is held whole today: nothing to check
  answer = () => { throw new Error("a held table was asked for"); };
  const r = await sb.attempt(() => sb.rest("series", { table_name: `eq.${held}` }, sb.HOURLY));
  if (r.ok || !lic.isLicenseReason(r.reason)) return `reason ${r.ok ? "ok" : r.reason}`;
  return sent.length === 0 && marks() === before ? "" : `${sent.length} requests, ${marks() - before} marks`;
});

await check("no database named on the server: not a failed read, not marked", async (before) => {
  const url = process.env.SUPABASE_URL;
  delete process.env.SUPABASE_URL;
  try {
    const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_none" }, sb.HOURLY));
    if (r.ok) return "the read came back";
  } finally {
    process.env.SUPABASE_URL = url;
  }
  return marks() === before ? "" : `${marks() - before} marks`;
});

await check("outside Next (NEXT_RUNTIME unset, as in the node scripts): no mark", async (before) => {
  delete process.env.NEXT_RUNTIME;
  answer = () => new Response("no", { status: 500 });
  try {
    const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session537_script" }, sb.HOURLY));
    if (r.ok) return "the read came back";
  } finally {
    process.env.NEXT_RUNTIME = "nodejs";
  }
  return marks() === before ? "" : `${marks() - before} marks`;
});

console.log(failures ? `${failures} case(s) failed` : "every case holds");
process.exitCode = failures ? 1 : 0;
