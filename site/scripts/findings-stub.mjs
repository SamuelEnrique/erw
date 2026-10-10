// Energy Research Warehouse (ERW) site, session 181: a local stand-in for the database functions of migration 029,
// for /internal/findings before the migration is applied and for scripts/check-internal-findings.mjs.
//
//   node scripts/findings-stub.mjs [port]                (default 54381)
//   SUPABASE_URL=http://localhost:54381 SUPABASE_ANON_KEY=local npx next start -p 3181
//
// It answers, as PostgREST would, the functions the review list calls:
//   POST /rest/v1/rpc/scanner_drafts_list       { p_token, p_state? }             the drafts, newest and strongest first
//   POST /rest/v1/rpc/scanner_draft_set_state   { p_token, p_id, p_state, p_request_id? }
//   POST /rest/v1/rpc/analysis_request          { p_token, p_kind, p_finding, p_params }   kept in memory, answered { ok, id }
//   POST /rest/v1/rpc/analysis_requests_list    the requests queued through this stand-in, and one done request
//   POST /rest/v1/rpc/analysis_request_card     { p_token, p_id }   one request with its card (null until done)
//   POST /rest/v1/rpc/site_rate_admit           always admitted
// with the rules of the SQL: a wrong token is HTTP 403 with code 42501; an id that is not a flag's or an unknown state
// is { ok: false, reason: "input" }; a draft that is not there is "no such draft"; each change is kept with its time.
// The done request is the impact study's committed card (site/data/findings/impact_study.json, Winter Storm Uri) as
// the worker would have written it into a queue row. The drafts are the fixture tests/fixtures/session181/drafts.json: real drafts of the scanner's first run (10 October
// 2026) as the loader would write them. Every other table answers no rows. It keeps its state in memory and writes
// nothing; no page code knows it exists: the site reads it only because SUPABASE_URL points at it.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const FIXTURE = path.join(here, "..", "..", "tests", "fixtures", "session181", "drafts.json");
// One more real draft, for the check of "Ask for a full card": the scanner's own draft for ERCOT North Hub real-time
// against South Hub on its run as of 22 February 2021 (Winter Storm Uri) with the caps lifted, a series the impact
// study knows. The check adds it; the stand-in alone serves the first run's drafts.
export const BACKTEST = path.join(here, "..", "..", "tests", "fixtures", "session181", "draft_backtest_uri.json");
const STATES = ["draft", "approved", "dismissed", "full_card_asked"];
const ID = /^scan-[a-z]+-[0-9a-f]{12}$/;
const stamp = () => new Date().toISOString().slice(0, 19) + "Z";

/** The fixture's drafts as rows of public.scanner_drafts (state draft, raised now). */
export function fixtureRows(file = FIXTURE) {
  const now = stamp();
  return JSON.parse(fs.readFileSync(file, "utf-8")).map((d) => ({
    id: d.id, rule: d.rule, table_name: d.table_name, series_key: d.series_key, flag_date: d.flag_date, value: d.value, strength: d.strength,
    scanner_version: d.scanner_version, state: "draft", raised_at: now, state_at: null, state_history: [], request_id: null, card: d.card,
  }));
}

export const DONE_ID = "20261010T165000Z-uri001";
/** A done request holding the committed impact card, as the worker writes one. */
export function doneRequest() {
  const card = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "findings", "impact_study.json"), "utf-8"));
  return { id: DONE_ID, kind: "run", finding: "impact_study", params: card.params, status: "done", note: "", asked_at: "2026-10-10T16:50:00Z", started_at: "2026-10-10T16:50:20Z",
    done_at: "2026-10-10T16:50:41Z", machine: "the data machine", card_id: card.card_id, card };
}

export function startStub(port = 54381, { token = env("INTERNAL_COSTS_TOKEN") ?? "", rows = fixtureRows() } = {}) {
  const requests = [doneRequest()];
  const refuse = (res) => { res.writeHead(403, { "Content-Type": "application/json" }); res.end(JSON.stringify({ code: "42501", message: "not authorized" })); };
  const answer = (res, body) => { res.writeHead(200, { "Content-Type": "application/json", "Content-Range": "*/0" }); res.end(JSON.stringify(body)); };
  const fns = {
    scanner_drafts_list: (a) => rows
      .filter((r) => !a.p_state || r.state === a.p_state)
      .sort((x, y) => y.raised_at.slice(0, 10).localeCompare(x.raised_at.slice(0, 10)) || y.strength - x.strength || x.id.localeCompare(y.id)),
    scanner_draft_set_state: (a) => {
      if (typeof a.p_id !== "string" || !ID.test(a.p_id) || !STATES.includes(a.p_state)) return { ok: false, reason: "input" };
      const r = rows.find((x) => x.id === a.p_id);
      if (!r) return { ok: false, reason: "no such draft" };
      const at = stamp(), from = r.state;
      r.state_history = [...r.state_history, { state: a.p_state, from, at }];
      r.state = a.p_state; r.state_at = at; r.request_id = a.p_request_id ?? r.request_id;
      return { ok: true, id: r.id, state: r.state, from, at };
    },
    analysis_request: (a) => {
      const id = `${stamp().replace(/[-:]/g, "")}-stub${String(requests.length + 1).padStart(2, "0")}`;
      requests.push({ id, kind: a.p_kind, finding: a.p_finding, params: JSON.parse(a.p_params || "{}"), status: "queued", note: "", asked_at: stamp(), started_at: null, done_at: null, machine: "", card_id: null, card: null });
      return { ok: true, id };
    },
    analysis_requests_list: () => requests.filter((r) => r.kind === "run").map(({ card, ...r }) => ({ ...r, has_card: Boolean(card) })),
    analysis_request_card: (a) => (typeof a.p_id === "string" && /^[A-Za-z0-9-]{6,60}$/.test(a.p_id) ? requests.find((r) => r.id === a.p_id && r.kind === "run") ?? null : null),
  };
  const server = http.createServer((req, res) => {
    let raw = "";
    req.on("data", (c) => { raw += c; });
    req.on("end", () => {
      const m = /^\/rest\/v1\/rpc\/([a-z_]+)/.exec(req.url ?? "");
      if (req.method === "POST" && m) {
        let a = {};
        try { a = JSON.parse(raw || "{}"); } catch { /* an empty body is no argument */ }
        if (m[1] === "site_rate_admit") return answer(res, { ok: true, reason: null });
        if (!fns[m[1]]) { res.writeHead(404, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ code: "PGRST202", message: `no function ${m[1]} in the stand-in` })); }
        if (token.length < 24 || a.p_token !== token) return refuse(res);
        return answer(res, fns[m[1]](a));
      }
      return answer(res, []);          // every table: no rows
    });
  });
  return new Promise((done) => server.listen(port, "127.0.0.1", () => done({ server, rows, requests, close: () => new Promise((r) => server.close(r)) })));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.argv[2] ?? 54381);
  const s = await startStub(port);
  console.log(`findings stand-in on http://localhost:${port} with ${s.rows.length} draft(s) from ${path.relative(process.cwd(), FIXTURE)}`);
}
