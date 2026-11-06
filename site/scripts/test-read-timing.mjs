// Energy Research Warehouse (ERW) site, session 580: the proof, without a build, that the reader's timing lines are
// off by default and change nothing when off, and that when ERW_READ_TIMING=1 each request prints one line with its
// table, query, status, range and time.
//
//   node --import ./scripts/alias-register.mjs scripts/test-read-timing.mjs off
//   node --import ./scripts/alias-register.mjs scripts/test-read-timing.mjs on
//
// "off" leaves ERW_READ_TIMING unset (the default of every server and build); "on" sets it to 1. lib/supabase.ts is
// imported as it is, with a stand-in for fetch (no request leaves this machine). Each case makes reads through rest(),
// restCount() and the license hold's public-rows read, and checks the rows, the requests sent and the lines printed.
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
const MODE = process.argv[2];
if (MODE !== "on" && MODE !== "off") {
  console.log("usage: test-read-timing.mjs on|off");
  process.exit(2);
}
if (MODE === "on") process.env.ERW_READ_TIMING = "1";
else delete process.env.ERW_READ_TIMING;
process.env.SUPABASE_URL = "https://erw-session580.invalid/rest/v1/";
process.env.SUPABASE_ANON_KEY = "session580-test";
delete process.env.NEXT_PHASE;
delete process.env.NEXT_RUNTIME;

const ORIGIN = "https://erw-session580.invalid";
const sent = [];
let answer = () => new Response("[]", { status: 200 });
globalThis.fetch = async (url, init) => {
  const u = new URL(String(url));
  if (u.origin !== ORIGIN) throw new Error(`a request this test does not make: ${u.origin}`);
  sent.push({ url: String(url), init: JSON.stringify(init) });
  return answer(u);
};

// the lines the reader prints: console.log is watched, everything else passes through
const lines = [];
const log = console.log;
console.log = (...a) => {
  const s = a.map(String).join(" ");
  if (s.startsWith("[erw-read] ")) lines.push(JSON.parse(s.slice("[erw-read] ".length)));
  else log(...a);
};

const sb = await import("../lib/supabase.ts");
const lic = await import("../lib/license.ts");
const ON = MODE === "on";
const json = (rows, status = 200, headers = {}) => new Response(JSON.stringify(rows), { status, headers: { "content-type": "application/json", ...headers } });

let failures = 0;
async function check(name, f) {
  sent.length = 0;
  lines.length = 0;
  try {
    const why = await f();
    if (why) { failures++; log(`FAIL ${name}: ${why}`); }
    else log(`ok   ${name}`);
  } catch (e) {
    failures++;
    log(`FAIL ${name}: threw ${e?.message ?? e}`);
  }
}
const expectLines = (n) => (ON ? (lines.length === n ? "" : `${lines.length} lines, ${n} expected`) : (lines.length === 0 ? "" : `${lines.length} lines printed with the timing off`));

await check(`readTiming: only "1" switches it on`, async () => {
  const cases = [[undefined, false], ["", false], ["0", false], ["true", false], ["1", true]];
  const bad = cases.filter(([v, want]) => sb.readTiming(v) !== want);
  return bad.length ? `wrong for ${JSON.stringify(bad)}` : "";
});

await check("a read of one page: the same rows and request; one line when on", async () => {
  answer = () => json([{ entity: "a", value: 1 }], 200, { "content-range": "0-0/*" });
  const rows = await sb.rest("series", { select: "entity,value", table_name: "eq.session580_ok", order: "ts_utc" }, sb.HOURLY);
  if (rows.length !== 1 || rows[0].entity !== "a") return `rows ${JSON.stringify(rows)}`;
  if (sent.length !== 1) return `${sent.length} requests`;
  const init = JSON.parse(sent[0].init);
  if (init.next?.revalidate !== sb.HOURLY || JSON.stringify(init.next?.tags) !== '["series"]') return `init ${sent[0].init}`;
  if (!sent[0].url.endsWith("/rest/v1/series?select=entity%2Cvalue&table_name=eq.session580_ok&order=ts_utc&limit=1000&offset=0")) return `url ${sent[0].url}`;
  const why = expectLines(1);
  if (why || !ON) return why;
  const l = lines[0];
  if (l.kind !== "rows" || l.table !== "series" || l.status !== "200" || l.range !== "0-0/*") return `line ${JSON.stringify(l)}`;
  if (l.query !== "select=entity%2Cvalue&table_name=eq.session580_ok&order=ts_utc&limit=1000&offset=0") return `query ${l.query}`;
  return Number.isInteger(l.ms) && l.ms >= 0 ? "" : `ms ${l.ms}`;
});

await check("a read of three pages: 2,010 rows; one line a page when on", async () => {
  answer = (u) => json(Array.from({ length: Number(u.searchParams.get("offset")) < 2000 ? 1000 : 10 }, (_, i) => ({ i })));
  const rows = await sb.rest("series", { table_name: "eq.session580_big" }, sb.LATEST);
  if (rows.length !== 2010) return `rows ${rows.length}`;
  return expectLines(sent.length);
});

await check("the statement timeout, retried twice: the same three requests and failure; three lines when on", async () => {
  answer = () => new Response('{"code":"57014","message":"canceling statement due to statement timeout"}', { status: 500 });
  const r = await sb.attempt(() => sb.rest("series", { table_name: "eq.session580_slow" }, sb.HOURLY));
  if (r.ok || !r.reason.includes("57014")) return `result ${JSON.stringify(r)}`;
  if (sent.length !== 3) return `${sent.length} requests, 3 expected`;
  const why = expectLines(3);
  if (why || !ON) return why;
  return lines.every((l) => l.status === "500") ? "" : `statuses ${lines.map((l) => l.status)}`;
});

await check("a refused request: the same failure; a line with status failed when on", async () => {
  answer = () => { throw new Error("connect ECONNREFUSED"); };
  const r = await sb.attempt(() => sb.rest("events", { table_name: "eq.session580_refused" }, sb.HOURLY));
  if (r.ok || !r.reason.includes("request failed")) return `result ${JSON.stringify(r)}`;
  const why = expectLines(1);
  if (why || !ON) return why;
  return lines[0].status === "failed" ? "" : `status ${lines[0].status}`;
});

await check("a count: the same number; a line of kind count with its range when on", async () => {
  answer = () => json([{}], 200, { "content-range": "0-0/42" });
  const n = await sb.restCount("series", { table_name: "eq.session580_count" }, sb.HOURLY);
  if (n !== 42) return `count ${n}`;
  if (!JSON.parse(sent[0].init).headers?.Prefer) return "the count lost its Prefer header";
  const why = expectLines(1);
  if (why || !ON) return why;
  return lines[0].kind === "count" && lines[0].range === "0-0/42" ? "" : `line ${JSON.stringify(lines[0])}`;
});

await check("a table held by row (session 499): its public rows only, filtered again; the line shows the filter when on", async () => {
  const held = lic.licenseNeededTables().find((t) => lic.licenseByRow(t));
  log(`     the table held by row: ${held ?? "none today"}`);
  if (!held) return "";   // no table is held by row today: nothing to check
  answer = () => json([{ entity: "p", extra: { row_license: lic.ROW_LICENSE_PUBLIC } }]);
  const rows = await sb.rest("events", { table_name: `eq.${held}` }, sb.HOURLY);
  if (rows.length !== 1) return `rows ${rows.length}`;
  if (!decodeURIComponent(sent[0].url).includes(`${lic.ROW_LICENSE_FILTER}=eq.${lic.ROW_LICENSE_PUBLIC}`)) return `url ${sent[0].url}`;
  const why = expectLines(1);
  if (why || !ON) return why;
  return decodeURIComponent(lines[0].query).includes(lic.ROW_LICENSE_FILTER) ? "" : `query ${lines[0].query}`;
});

if (failures) {
  log(`${failures} case(s) failed (timing ${MODE})`);
  process.exit(1);
}
log(`every case holds (timing ${MODE})`);
