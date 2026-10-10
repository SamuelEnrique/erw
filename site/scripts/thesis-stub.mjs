// Energy Research Warehouse (ERW) site, session 135: a local stand-in for the four database functions of Thesis
// Builder (migration 024), so /thesis can be seen and checked with a report in it without a run being paid for.
//
//   node scripts/thesis-stub.mjs [port]                (default 54435)
//   SUPABASE_URL=http://localhost:54435 SUPABASE_ANON_KEY=local npx next start -p 3135
//   node --import ./scripts/alias-register.mjs scripts/check-thesis.mjs http://localhost:3135
//
// It answers POST /rest/v1/rpc/thesis_list, thesis_get, thesis_submit and thesis_pitchbook_accept as the functions do
// (the internal token checked, the one-time key checked and erased when used), from runs it keeps in memory. Every
// other request answers with no rows. It writes nothing, and no page code knows it exists: the site reads it only
// because SUPABASE_URL points at it.
//
// Session 150: it also answers thesis_provider_accept and thesis_provider_results (migration 025) as the functions
// do: behind the internal token, for a finished run, one answer a provider and run, PitchBook's row holding no
// payload. The answers it is given are the made-up ones of scripts/thesis-providers-fixtures.mjs.
//
// Session 158: one company of the fixture report carries reason_vendor (the sentence under "Why it is here" comes from a
// data vendor's public page), and when the stand-in is started with the alias loader,
//   node --import ./scripts/alias-register.mjs scripts/thesis-stub.mjs [port]
// it also holds a fourth run, "fixture-three", that already holds the answers of all three providers, each read by
// the site's own readers from the made-up answers. Since this session the page's route refuses a Crunchbase answer,
// so the check can no longer paste one: this run is how it still sees a run that holds one drawn as before. Started
// without the loader the stand-in says that this run is not there, and the check says what it could not prove.
//
// THE RUNS BELOW ARE A FIXTURE. Every company, figure, source and date in them is made up for the check and is no
// company's: nothing here is data of the warehouse, and none of it is ever loaded, published or shown on the site.
// The fixture is shaped to exercise the page: a cell of each missing kind, a row a chart must leave out, a source with
// no address, a source whose address is not a web address, a tab with nothing in it, and words that would be markup
// if the page wrote them as HTML.
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env } from "./browser.mjs";

export const DONE = "fixture-done", QUEUED = "fixture-queued", FAILED = "fixture-failed", THREE = "fixture-three";
/** Session 169: a finished run started with "Run anyway", its report flagged (the runner copies thesis_runs.gate onto it). */
export const FORCED = "fixture-forced";
/** Session 169: a finished run of the market research (report version 2): no company of the ERW's own, five trends of
 * which two are drawn with a series, the timing and the references; and the same run once a PitchBook answer is pasted. */
export const MARKET = "fixture-market", MARKET_PB = "fixture-market-pb";

export function marketReport() {
  const series = (n, id, title) => ({ id, source: "EIA", title, unit: "fixture units", freq: "annual", url: "https://www.eia.gov/opendata/browser/fixture", retrieved: "2026-10-09",
    points: 3, cut: false, source_line: `Source: U.S. Energy Information Administration (9 October 2026), ${title}.`, source_id: "S9" });
  const drawn = (n, title) => ({ n, title: `Fixture market trend ${n}`, fact: T(`Fixture fact ${n}: the series rose to 12.5 in 2025.`, "S1", "S9"), sources: ["S1", "S9"],
    table: { columns: ["Period", title], rows: [["2023", "10"], ["2024", "11.25"], ["2025", "12.5"]] }, chart: { kind: "line", title, category: 0, values: [1], unit: "fixture units" },
    series: series(n, `eia:fixture:${n}`, title), no_series: "" });
  const bare = (n) => ({ n, title: `Fixture market trend ${n}`, fact: T(`Fixture fact ${n}, from a cited page.`, "S1"), sources: ["S1"], table: { columns: [], rows: [] },
    chart: { kind: "none", title: "", category: 0, values: [1], unit: "" }, series: null, no_series: "Fixture: no real series measures this trend, so it is not drawn." });
  return {
    version: 2, niche: "fixture: a market run", stage: "", geography: "", built: "2026-10-09T07:15:00Z",
    sources: [{ id: "S1", kind: "web", title: "Fixture market source", url: "https://example.com/market", retrieved: "2026-10-09" },
      { id: "S9", kind: "web", title: "EIA API v2: fixture series", url: "https://www.eia.gov/opendata/browser/fixture", retrieved: "2026-10-09" }],
    scope: { definition: T("Fixture definition of the market.", "S1"), value_chain: [], excluded: [{ niche: "Fixture out", why: "Fixture reason." }], definitions: [],
      in_scope: [T("Fixture in scope.", "S1")], sub_segments: [{ name: "Fixture segment", what: T("Fixture segment text.", "S1") }] },
    trends: [drawn(1, "Fixture series one"), bare(2), drawn(3, "Fixture series three"), bare(4), bare(5)],
    landscape: { fact: T(""), rule: "", companies: [] }, funnel: { stages: [], companies: [] }, pipeline: { companies: [] },
    capital: { fact: T("Fixture capital fact.", "S1"), rounds: [] }, incumbents: { fact: T("Fixture incumbents fact.", "S1"), players: [] }, risks: [], policy: { fact: "", actions: [] },
    timing: { stage: "being installed", text: T("Fixture timing text.", "S1"), evidence: [T("Fixture evidence.", "S1")] },
    connector_tabs: { note: "Connect PitchBook or Harmonic to fill this", columns: {
      landscape: ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"],
      funnel: ["Company", "What it sells", "Stage", "Funnel stage", "Date sourced", "Sourced by", "Next step", "Status", "Notes", "Source"],
      pipeline: ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"],
      success: ["Company", "What it sells", "Outcome", "Date", "Raised before", "Investors", "Source"],
      investors: ["Investor", "Companies backed in this niche", "Lead in", "Latest round seen", "Source"] } },
  };
}
/** A PitchBook answer to the market run, as the site's validator leaves it: made up for the check, no company's. */
export const MARKET_ANSWER = { format: "erw-pitchbook-1", run_id: "fixture-market-pb", pulled_on: "2026-10-09", label: "PitchBook", received_note: "Figures as returned from PitchBook through the user's own account; not checked by the ERW.", companies: [],
  additional_companies: [
    { name: "Fixture Seed Co", found: true, why: "keyword: fixture", description: "Fixture sensors", hq: "Austin, TX", founded_year: 2021, financing_status: "Venture Capital-Backed", last_round: { date: "2025-03", type: "Seed", size_usd_m: 3 }, total_raised_usd_m: 4, investors: ["Fund One", "Fund Two"], lead_investors: ["Fund One"], founders: ["A. Fixture"] },
    { name: "Fixture Exit Co", found: true, why: "keyword: fixture", description: "Fixture software", financing_status: "Acquired/Merged", last_round: { date: "2024-06", type: "Merger/Acquisition" }, total_raised_usd_m: 20, investors: ["Fund One"] },
    { name: "Not Found Co", found: false, why: "keyword: fixture" },
  ] };
export const VENDOR_NOTE = "Fixture: this sentence is from a public page of a data vendor (Fixture Vendor), not from the company or the press.";
// Session 160: one company of the fixture report carries reason_kept (its sentence is from a page's kept text, with
// the day that text was retrieved) and also (its other names as written). Made up for the check, like the rest.
export const KEPT_MARK = "retrieved 7 October 2026";
export const KEPT_NOTE = "Fixture: this sentence is from the page as it was read on 7 October 2026. The page did not give its text when it was asked again on 8 October 2026.";
export const ALSO = ["Unasked Example", "UnaskedExample (UE)"];
export const KEY = "fixture-key-0123456789abcdefghijklmnopqrstu";      // 43 characters, as the database writes them
export const PROBE = "<img src=x onerror=window.__thesis_probe=1>";

const T = (text, ...sources) => ({ text, sources });
const gap = (missing, note) => ({ missing, note });
const pending = () => gap("pitchbook_pending", "");

export function fixtureReport() {
  return {
    version: 1, niche: "fixture: storage for example loads", stage: "Seed to Series B", geography: "United States", built: "2026-10-06T14:20:00Z",
    sources: [
      { id: "S1", kind: "web", title: "Fixture source one", url: "https://example.com/one", retrieved: "2026-10-06" },
      { id: "S2", kind: "web", title: "Fixture source two", url: "https://example.org/two?x=1", retrieved: "2026-10-05" },
      { id: "S3", kind: "web", title: "Fixture source with no web address", url: "javascript:window.__thesis_probe=2", retrieved: "2026-10-05" },
      { id: "E1", kind: "erw", title: "ERW table fixture_table", url: "", retrieved: "2026-10-06" },
    ],
    scope: {
      definition: T("Fixture definition of the niche.", "S1", "E1"),
      value_chain: [{ stage: "Cells", what: T("Fixture stage one.", "S1") }, { stage: "Integration", what: T("Fixture stage two.", "S2") }],
      excluded: [{ niche: "Fixture neighbour", why: "Fixture reason it is left out." }],
      definitions: [{ term: "Fixture term", meaning: T("Fixture meaning.", "S2") }],
    },
    trends: [
      { n: 1, title: "Fixture trend one", fact: T("Fixture fact of trend one.", "S1"), sources: ["S1", "E1"],
        table: { columns: ["Year", "Installed", "Planned"], rows: [["2023", "10 GW", "4 GW"], ["2024", gap("not_held", "Fixture: not published for 2024."), "about 6"], ["2025", "18.5 GW", gap("not_disclosed", "Fixture: the planner does not disclose it.")], [PROBE, "1,024 GW", "7 GW"]] },
        chart: { kind: "bar", title: "Fixture capacity", category: 0, values: [1, 2], unit: "GW" } },
      { n: 2, title: "Fixture trend two", fact: T("Fixture fact of trend two.", "S2"), sources: ["S2"],
        table: { columns: ["Quarter", "Price"], rows: [["Q1", "$120"], ["Q2", "$98.5"], ["Q3", "$101"]] },
        chart: { kind: "line", title: "Fixture price", category: 0, values: [1], unit: "USD/kWh" } },
      { n: 3, title: "Fixture trend three", fact: T("Fixture fact of trend three.", "S9"), sources: [],
        table: { columns: ["Item", "Reading"], rows: [["One", "rising"], ["Two", "flat"]] },
        chart: { kind: "bar", title: "Fixture readings", category: 0, values: [1], unit: "" } },
      { n: 4, title: "Fixture trend four", fact: T("Fixture fact of trend four."), sources: [], table: { columns: [], rows: [] }, chart: { kind: "none", title: "", category: 0, values: [], unit: "" } },
    ],
    landscape: {
      fact: T("Fixture fact of the landscape.", "S1"), rule: "Fixture rule: a company is on this map when a fixture source ties it to a fixture trend.",
      companies: [
        { name: "Example Storage Inc.", website: "https://www.example.com", description: "Fixture description one.", founders: pending(), stage: "Series A", raised: pending(), location: pending(),
          signal: "Fixture signal one.", trends: [1, 2], reason: "Fixture reason one.", sources: ["S1", "S3"], confidence: 72, confidence_note: "Fixture note: two sources agree.", sourcing: ["fixture channel"] },
        { name: "Sample Grid Co", website: "javascript:window.__thesis_probe=3", description: "Fixture description two.", founders: gap("not_disclosed", "Fixture: the company names no founder."), stage: gap("not_confirmed", "Fixture: one source only."),
          raised: gap("not_held", "Fixture: no round is held."), location: "Austin, TX", signal: "Fixture signal two.", trends: [1], reason: "Fixture reason two.", reason_vendor: { mark: "vendor page", note: VENDOR_NOTE }, sources: ["S2"], confidence: 41, confidence_note: "Fixture note: one source.", sourcing: [] },
        { name: "Unasked Example LLC", website: "", description: "", founders: "A. Fixture", stage: "Seed", raised: "USD 2 million", location: "Reno, NV", signal: "", trends: [], reason: "Fixture reason three.", reason_kept: { mark: KEPT_MARK, note: KEPT_NOTE, retrieved: "2026-10-07" }, also: ALSO, sources: [], confidence: 55, confidence_note: "", sourcing: ["fixture channel", "second fixture channel"] },
      ],
    },
    funnel: {
      stages: [{ id: "found", label: "Found", n: 14 }, { id: "sourced", label: "Sourced", n: 9 }, { id: "scored", label: "Scored", n: 4 }, { id: "kept", label: "Kept", n: 3 }],
      companies: [
        { name: "Example Storage Inc.", reached: "kept", stopped: "", score: 72, sourcing: ["fixture channel"], sources: ["S1"] },
        { name: "Sample Grid Co", reached: "kept", stopped: "", score: 41, sourcing: [], sources: ["S2"] },
        { name: "Dropped Example", reached: "sourced", stopped: "Fixture: no second source.", score: null, sourcing: ["fixture channel"], sources: [] },
      ],
    },
    pipeline: { companies: [
      { name: "Example Storage Inc.", founders: pending(), signal: "Fixture signal one.", access: gap("not_held", "Fixture: no route in is held."), tam: "USD 4 billion", trends: [1, 2], confidence: 72, sources: ["S1"] },
      { name: "Sample Grid Co", founders: "B. Fixture", signal: "Fixture signal two.", access: "Fixture access.", tam: pending(), trends: [1], confidence: 41, sources: ["S2"] },
    ] },
    capital: { fact: T("Fixture fact of capital.", "S2"), rounds: [
      { date: "2025-03", company: "Example Storage Inc.", kind: "Series A", amount: "USD 12.5 million", investors: "Fixture Fund One", sources: ["S1"] },
      { date: gap("not_confirmed", "Fixture: the date is given by one source."), company: "Sample Grid Co", kind: "Seed", amount: pending(), investors: gap("not_disclosed", "Fixture: investors not named."), sources: ["S2"] },
    ] },
    // incumbents is left out on purpose: its tab must say that nothing was found
    risks: [{ risk: "Fixture risk.", how: "Fixture: how it would bite.", not_known: "Fixture: what is not known.", sources: ["S1"] }],
    policy: { fact: "Fixture fact of policy.", actions: [{ date: "2026-09-30", agency: "Fixture agency", title: "Fixture rule", why: "Fixture why.", url: "https://example.com/rule", read: "Fixture read." }] },
  };
}

export function fixtureAnswer(runId = DONE) {
  return {
    format: "erw-pitchbook-1", run_id: runId, pulled_on: "2026-10-06",
    companies: [
      { name: "Example Storage Inc.", found: true, pitchbook_name: "Example Storage", hq: "Austin, TX", founded_year: 2019, employees: 42, financing_status: "Venture Capital-Backed",
        last_round: { date: "2025-03", type: "Series A", size_usd_m: 12.5 }, total_raised_usd_m: 18, investors: ["Fixture Fund One", "Fixture Fund Two"], founders: ["A. Fixture", "C. Fixture"] },
      { name: "Sample Grid Co", found: false },
    ],
    additional_companies: [{ name: "Found Later LLC", found: true, why: "Fixture: named under the same keywords.", total_raised_usd_m: 3.25 }],
  };
}

function fixtureRuns() {
  const report = fixtureReport();
  const request = {
    format: "erw-pitchbook-1", run_id: DONE,
    companies: [{ name: "Example Storage Inc.", website: "https://www.example.com", lookups: ["total raised", "last round"] }, { name: "Sample Grid Co", website: "", lookups: ["founders"] }],
    discover: { keywords: ["fixture"], hq: "United States" }, paste_text: `FIXTURE REQUEST for run ${DONE}: answer in the format erw-pitchbook-1.`,
  };
  const base = { stage: "Seed to Series B", geography: "United States", note: "", started_at: null, finished_at: null, report: null, pitchbook_request: null, pitchbook_key: null, pitchbook: null, pitchbook_received_at: null, gets: 0 };
  return [
    { ...base, run_id: DONE, niche: report.niche, status: "done", requested_at: "2026-10-06T14:05:12.000000+00:00", started_at: "2026-10-06T14:06:00+00:00", finished_at: "2026-10-06T14:20:00+00:00", report, pitchbook_request: request, pitchbook_key: KEY },
    { ...base, run_id: QUEUED, niche: "fixture: a run that waits", status: "queued", requested_at: "2026-10-06T13:00:00+00:00" },
    { ...base, run_id: FAILED, niche: "fixture: a run that failed", stage: "", geography: "", status: "failed", note: "Fixture: the run stopped because the fixture says so.", requested_at: "2026-10-06T12:00:00+00:00", finished_at: "2026-10-06T12:04:00+00:00" },
  ];
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.argv[2] ?? 54435);
  const token = env("INTERNAL_COSTS_TOKEN") ?? "";
  const runs = fixtureRuns();
  let made = 0;
  const provided = [];          // the rows of thesis_provider_results
  // session 158: a finished run that already holds the three providers' answers, read by the site's own readers
  try {
    const crypto = await import("node:crypto");
    const pb = await import("../lib/thesis/pitchbook.ts");
    const pv = await import("../lib/thesis/providers.ts");
    const fx = await import("./thesis-providers-fixtures.mjs");
    const sha = (s) => crypto.createHash("sha256").update(s, "utf8").digest("hex");
    const need = (r, what) => { if (!r.ok) throw new Error(`${what}: ${r.reason}`); return r.payload; };
    const done = runs[0];
    const answers = { pitchbook: fixtureAnswer(THREE), harmonic: fx.harmonicAnswer(THREE), crunchbase: fx.crunchbaseAnswer(THREE) };
    const payloads = { pitchbook: need(pb.validatePitchbook(answers.pitchbook, THREE, 2026), "PitchBook"), harmonic: need(pv.PROVIDERS.harmonic.read(answers.harmonic, THREE), "Harmonic"),
      crunchbase: need(pv.PROVIDERS.crunchbase.read(answers.crunchbase, THREE), "Crunchbase") };
    runs.push({ ...done, run_id: THREE, niche: "fixture: a run that holds three providers' answers", requested_at: "2026-10-05T10:00:00+00:00", started_at: "2026-10-05T10:01:00+00:00", finished_at: "2026-10-05T10:15:00+00:00",
      pitchbook_request: { ...done.pitchbook_request, run_id: THREE, paste_text: `FIXTURE REQUEST for run ${THREE}: answer in the format erw-pitchbook-1.` }, pitchbook_key: null,
      pitchbook: payloads.pitchbook, pitchbook_received_at: "2026-10-05T11:00:00+00:00" });
    for (const [id, at] of [["pitchbook", "2026-10-05T11:00:01+00:00"], ["harmonic", "2026-10-05T12:00:00+00:00"], ["crunchbase", "2026-10-05T13:00:00+00:00"]]) {
      provided.push({ run_id: THREE, provider: id, format: pv.PROVIDERS[id].format, pasted_at: at, pasted_sha256: sha(JSON.stringify(answers[id])), payload: id === "pitchbook" ? null : payloads[id] });
    }
  } catch (e) {
    console.log(`thesis stub: the run "${THREE}" is not held (${String(e?.message ?? e).split(/[\r\n]/)[0].slice(0, 160)}); start the stand-in with --import ./scripts/alias-register.mjs to hold it`);
  }
  // session 169: a finished run of the market research, and the same with a PitchBook answer pasted
  runs.push({ ...runs[0], run_id: MARKET, niche: "fixture: a market run", stage: "", geography: "", requested_at: "2026-10-03T10:00:00+00:00", report: marketReport(), pitchbook_key: null,
    pitchbook_request: { ...runs[0].pitchbook_request, run_id: MARKET, companies: [] } });
  runs.push({ ...runs[0], run_id: MARKET_PB, niche: "fixture: a market run with a PitchBook answer", stage: "", geography: "", requested_at: "2026-10-02T10:00:00+00:00", report: marketReport(), pitchbook_key: null,
    pitchbook_request: { ...runs[0].pitchbook_request, run_id: MARKET_PB, companies: [] }, pitchbook: MARKET_ANSWER, pitchbook_received_at: "2026-10-09T08:00:00+00:00" });
  // session 169: a finished run started with "Run anyway" on a niche the gate refused
  runs.push({ ...runs[0], run_id: FORCED, niche: "oil & gas demand", stage: "", geography: "", requested_at: "2026-10-04T10:00:00+00:00", pitchbook_key: null,
    report: { ...runs[0].report, niche: "oil & gas demand", gate: { forced: true, why: "sector_only", topic: "oil_gas", at: "2026-10-04T10:00:00.000Z" } } });
  const fns = {
    thesis_list: () => runs.map((r) => ({ run_id: r.run_id, niche: r.niche, stage: r.stage, geography: r.geography, status: r.status, note: r.note, requested_at: r.requested_at, started_at: r.started_at, finished_at: r.finished_at,
      companies: r.report?.landscape?.companies?.length ?? 0, pitchbook: r.pitchbook ? "received" : r.pitchbook_request ? "pending" : "none" })),
    thesis_get: (a) => {
      const r = runs.find((x) => x.run_id === a.p_run_id);
      if (!r) return null;
      // a run this stub queued moves on as it is read, so the page's own re-reading can be seen: running, then failed
      if (r.made) {
        r.gets += 1;
        if (r.gets >= 4) { r.status = "failed"; r.note = r.forced_note ?? "Fixture: a run queued on the stub stops here."; r.finished_at = new Date().toISOString(); }
        else if (r.gets >= 2) { r.status = "running"; r.started_at = r.started_at ?? new Date().toISOString(); }
      }
      return Object.fromEntries(Object.entries(r).filter(([k]) => k !== "gets" && k !== "made" && k !== "forced_note"));
    },
    thesis_submit: (a) => {
      const niche = String(a.p_niche ?? "").trim();
      if (niche.length < 8 || niche.length > 400) return { ok: false, reason: "input" };
      if (made >= 2) return { ok: false, reason: "day", runs_today: made };
      made += 1;
      const run = { ...runs[1], run_id: `fixture-new-${made}`, niche, stage: String(a.p_stage ?? ""), geography: String(a.p_geography ?? ""), requested_at: new Date().toISOString(), gets: 0, made: true };
      runs.unshift(run);
      return { ok: true, run_id: run.run_id, dispatched: false };
    },
    // session 169, migration 026: a run started with "Run anyway" is queued by thesis_submit and its gate kept on the row
    // (the real function does not hand the gate back; this stand-in says it in the note the queued run ends with)
    thesis_submit_forced: (a) => {
      const g = a.p_gate;
      if (!g || typeof g !== "object" || Array.isArray(g) || g.forced !== true || JSON.stringify(g).length > 2000) return { ok: false, reason: "input" };
      const r = fns.thesis_submit(a);
      const run = r.ok ? runs.find((x) => x.run_id === r.run_id) : null;
      if (run) run.forced_note = `Fixture: a run started with Run anyway (${String(g.why)}) and kept with its gate; it stops here.`;
      return r;
    },
    // session 150, migration 025: the answers of the providers, kept beside the runs
    thesis_provider_accept: (a) => {
      const want = { pitchbook: "erw-pitchbook-1", harmonic: "erw-harmonic-1", crunchbase: "erw-crunchbase-1" }[a.p_provider];
      if (!want || a.p_format !== want || typeof a.p_sha256 !== "string" || !/^[0-9a-f]{64}$/.test(a.p_sha256)) return { ok: false, reason: "shape" };
      const r = runs.find((x) => x.run_id === a.p_run_id);
      if (!r || r.status !== "done") return { ok: false, reason: "run" };
      const p = a.p_payload ?? null;
      if (a.p_provider === "pitchbook") {
        if (!r.pitchbook || p !== null) return { ok: false, reason: "shape" };
      } else if (!p || typeof p !== "object" || Array.isArray(p) || !Array.isArray(p.companies) || p.companies.length > 300 || JSON.stringify(p).length > 400000 || p.format !== want || p.run_id !== a.p_run_id) {
        return { ok: false, reason: "shape" };
      }
      if (provided.some((x) => x.run_id === a.p_run_id && x.provider === a.p_provider)) return { ok: false, reason: "held" };
      provided.push({ run_id: a.p_run_id, provider: a.p_provider, format: want, pasted_at: new Date().toISOString(), pasted_sha256: a.p_sha256, payload: p });
      return { ok: true, companies: p ? p.companies.length : 0 };
    },
    thesis_provider_results: (a) => provided.filter((x) => x.run_id === a.p_run_id).map((x) => ({ provider: x.provider, format: x.format, pasted_at: x.pasted_at, pasted_sha256: x.pasted_sha256, payload: x.payload })),
  };
  http.createServer((req, res) => {
    const send = (status, body) => { res.writeHead(status, { "Content-Type": "application/json" }); res.end(JSON.stringify(body)); };
    const m = /^\/rest\/v1\/rpc\/([a-z_]+)$/.exec(new URL(req.url, `http://localhost:${port}`).pathname);
    if (req.method !== "POST" || !m) return send(200, []);
    let raw = "";
    req.on("data", (d) => { raw += d; });
    req.on("end", () => {
      let a;
      try { a = JSON.parse(raw || "{}"); } catch { return send(400, { message: "bad JSON" }); }
      if (m[1] === "thesis_pitchbook_accept") {
        const r = runs.find((x) => x.run_id === a.p_run_id);
        if (typeof a.p_key !== "string" || a.p_key.length < 32 || !r || !r.pitchbook_key || r.pitchbook_key !== a.p_key) return send(200, { ok: false, reason: "key" });
        const p = a.p_payload;
        if (!p || typeof p !== "object" || Array.isArray(p) || !Array.isArray(p.companies) || p.companies.length > 300 || JSON.stringify(p).length > 400000) return send(200, { ok: false, reason: "shape" });
        Object.assign(r, { pitchbook: p, pitchbook_received_at: new Date().toISOString(), pitchbook_key: null });
        return send(200, { ok: true, companies: p.companies.length });
      }
      if (!(m[1] in fns)) return send(404, { code: "PGRST202", message: `no function ${m[1]}` });
      if (!token || a.p_token !== token) return send(403, { code: "42501", message: "not authorized" });
      return send(200, fns[m[1]](a));
    });
  }).listen(port, () => console.log(`thesis stub: ${runs.length} fixture runs on http://localhost:${port} (made up for the check; no company's)`));
}
