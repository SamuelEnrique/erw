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
// THE RUNS BELOW ARE A FIXTURE. Every company, figure, source and date in them is made up for the check and is no
// company's: nothing here is data of the warehouse, and none of it is ever loaded, published or shown on the site.
// The fixture is shaped to exercise the page: a cell of each missing kind, a row a chart must leave out, a source with
// no address, a source whose address is not a web address, a tab with nothing in it, and words that would be markup
// if the page wrote them as HTML.
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env } from "./browser.mjs";

export const DONE = "fixture-done", QUEUED = "fixture-queued", FAILED = "fixture-failed";
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
          raised: gap("not_held", "Fixture: no round is held."), location: "Austin, TX", signal: "Fixture signal two.", trends: [1], reason: "Fixture reason two.", sources: ["S2"], confidence: 41, confidence_note: "Fixture note: one source.", sourcing: [] },
        { name: "Unasked Example LLC", website: "", description: "", founders: "A. Fixture", stage: "Seed", raised: "USD 2 million", location: "Reno, NV", signal: "", trends: [], reason: "Fixture reason three.", sources: [], confidence: 55, confidence_note: "", sourcing: ["fixture channel", "second fixture channel"] },
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
  const fns = {
    thesis_list: () => runs.map((r) => ({ run_id: r.run_id, niche: r.niche, stage: r.stage, geography: r.geography, status: r.status, note: r.note, requested_at: r.requested_at, started_at: r.started_at, finished_at: r.finished_at,
      companies: r.report?.landscape?.companies?.length ?? 0, pitchbook: r.pitchbook ? "received" : r.pitchbook_request ? "pending" : "none" })),
    thesis_get: (a) => {
      const r = runs.find((x) => x.run_id === a.p_run_id);
      if (!r) return null;
      // a run this stub queued moves on as it is read, so the page's own re-reading can be seen: running, then failed
      if (r.made) {
        r.gets += 1;
        if (r.gets >= 4) { r.status = "failed"; r.note = "Fixture: a run queued on the stub stops here."; r.finished_at = new Date().toISOString(); }
        else if (r.gets >= 2) { r.status = "running"; r.started_at = r.started_at ?? new Date().toISOString(); }
      }
      return Object.fromEntries(Object.entries(r).filter(([k]) => k !== "gets" && k !== "made"));
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
