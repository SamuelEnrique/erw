// Energy Research Warehouse (ERW) site, session 5202 (chain 235): a set of questions asked through the site's own loop
// (lib/chat/ask.ts ask(), the function /api/ask calls), with no build and no server, against the live set as a visitor's
// chat reads it: every read goes with the anon key (lib/supabase.ts config(): the service key is read by writeConfig()
// only, never for a read), the model under ANTHROPIC_API_KEY. Every tool call and its result is recorded (opts.record),
// and each model call is written to the site's own cost ledger, site_api_calls, under the evaluation's step
// (site_ask_eval, strictly, as /api/ask writes an evaluation's: no spend goes unrecorded). That row is the one write
// this script makes, with the service key as the production server makes it, each under a question number drawn at
// random as the route draws it. --no-ledger leaves the key out: the row is then tried with the anon key, which the
// database refuses since migration 034, so none is written and the cost stands in the run file alone.
//
//   node --import ./scripts/eval-register.mjs scripts/eval-ask-site-loop.mjs --questions <questions.json> --run <run.json>
//        --cap <USD> [--only id1,id2] [--label "..."] [--no-ledger] [--keep-going] [--dry-run]
//
// <questions.json>: {"questions": [{id, grid, via, question}, ...]} (warehouse/chat/eval/eval_site.py writes it from a
// set's YAML). <run.json> has the shape of eval_loop.py's run files ("loop": "site" on every record), is written after
// every question and read first, so a run asked again goes on where it stopped. The cap is checked before each
// question: the run's own costs plus a reserve (USD 0.30 for the first ten questions, then the dearest so far, at least
// USD 0.15) must stay under --cap. A question that ends in an error stops the run (session 5251: an error may be a call
// that was paid for and not recorded, so no further one is made until a person or a session has read it; since session
// 5269 its record holds what the loop had counted when it threw, the cost of its model calls with it, so the cap counts it), unless
// --keep-going. --dry-run loads the loop, reads the live set's catalogue through the loop's own list_tables and asks
// nothing. warehouse/chat/eval/eval_site.py runs this and grades the run.
//
// A question named with --only that the run already holds is asked again, and its earlier record is kept under
// "superseded" with its cost (session 5256: two such records were written over, and the run file then held USD 0.45
// less than the ledger): the cap counts both lists, and so does every reader of the run's cost.
//
// The keys come from the main checkout's .env beside a worktree (never printed). No warehouse table is written.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..", "..");
const arg = (name, fallback = null) => { const i = process.argv.indexOf(name); return i > 0 && i + 1 < process.argv.length ? process.argv[i + 1] : fallback; };
const flag = (name) => process.argv.includes(name);

/** KEY=value lines of a .env file (no shell expansion; quotes around a value are dropped). */
export function dotenv(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/.exec(line);
    if (m && !line.trim().startsWith("#")) out[m[1]] = m[2].replace(/^(["'])(.*)\1$/, "$2");
  }
  return out;
}

/** The reserve kept before a question: one more at the dearest cost seen, as eval_loop.py keeps it. */
export function reserve(asked, dearest) {
  return asked < 10 ? 0.3 : Math.max(0.15, dearest);
}

export const GRID_SLUG = { ERCOT: "ercot", CAISO: "caiso", NYISO: "nyiso", SPP: "spp", "ISO-NE": "isone", MISO: "miso", PJM: "pjm" };

/** Session 5271: what an answer was asked under, kept in its record: the effort of the writing turn (ASK_WRITER_EFFORT
 *  when the asking set it, as lib/chat/ask.ts effortOf reads it, else the spec's own), the output limit of a call, and
 *  the thinking switch when one is set. An asking at another effort is then told from one at the spec's by its record. */
export function askedUnder(env, spec) {
  // rules: the numbered rules of the prompt the answer was asked under (ten until session 5268, eleven with the rule to
  // stop), counted in the prompt's own part, before the briefing's first heading
  return { effort: env.ASK_WRITER_EFFORT || spec.effort, max_tokens: spec.max_tokens, rules: (String(spec.system ?? "").split(/\n# /)[0].match(/^\d+\. /gm) ?? []).length,
    ...(env.ASK_THINKING ? { thinking: env.ASK_THINKING } : {}) };
}

/** The run's cost so far: its answers and the answers they superseded. */
export function costOf(run) {
  return [...(run.questions ?? []), ...(run.superseded ?? [])].reduce((s, x) => s + Number(x.cost_usd ?? 0), 0);
}

/** The run with a new record in: an earlier record of the same question moves to "superseded", never out of the file. */
export function withRecord(run, rec, order) {
  const old = (run.questions ?? []).find((x) => x.id === rec.id);
  const kept = (run.questions ?? []).filter((x) => x.id !== rec.id).concat([rec]);
  const at = (id) => { const i = order.indexOf(id); return i < 0 ? order.length : i; };
  return { ...run, questions: kept.sort((a, b) => at(a.id) - at(b.id)), ...(old || run.superseded ? { superseded: [...(run.superseded ?? []), ...(old ? [old] : [])] } : {}) };
}

/** One answer of the site's loop as a record of the run file (the shape of eval_loop.py's). */
export function recordOf(q, r, at, error, meter = null) {
  const status = r?.status ?? (error ? "error" : null);
  // session 5269: an answer that ended in an error after model calls were made has no result, and the calls were paid
  // for: the loop's own count when it threw (ask.ts AskMeter) is the record's cost, its calls and its trace
  const counted = r ? null : meter;
  const kept = Array.isArray(r?.trace) ? r.trace : Array.isArray(counted?.trace) ? counted.trace : [];
  const trace = kept.map((t) => ({ ...t, is_error: Boolean(t.isError) }));
  return { id: q.id, grid: q.grid, via: q.via, question: q.question, asked_at_utc: at, http: null, loop: "site",
    model: r?.model ?? null, status, answer: r?.answer ?? null, why: r?.why ?? null, citations: r?.citations ?? null,
    not_in_warehouse: status === "not_in_warehouse", tool_calls: r?.tool_calls ?? counted?.tool_calls ?? null, retried: Boolean(r?.retried),
    cost_usd: Number(r?.cost_usd ?? counted?.cost_usd ?? 0), seconds: r?.seconds ?? null, error: error ?? null, refused: status === "refused_unverified",
    reads: r?.reads ?? null, nearest: r?.nearest ?? null, usage: r?.usage ?? counted?.usage ?? null, ...(counted?.stop ? { stopped_at: counted.stop } : {}), trace };
}

async function main() {
  const questionsPath = arg("--questions"), runPath = arg("--run"), cap = Number(arg("--cap", "2"));
  if (!questionsPath || !runPath || !(cap > 0)) throw new Error("--questions <file> --run <file> --cap <USD> are required");
  const only = arg("--only") ? new Set(arg("--only").split(",")) : null;
  const envFile = [path.join(root, ".env"), path.join(root, "..", "erw", ".env")].find((p) => fs.existsSync(p));
  const env = envFile ? dotenv(fs.readFileSync(envFile, "utf8")) : {};
  for (const k of ["SUPABASE_URL", "SUPABASE_ANON_KEY", "ANTHROPIC_API_KEY", "SUPABASE_SERVICE_KEY"]) if (!process.env[k] && env[k]) process.env[k] = env[k];
  // the service key writes the ledger's row and nothing else (lib/supabase.ts writeConfig); every read is the anon key's
  const ledger = !flag("--no-ledger") && Boolean(process.env.SUPABASE_SERVICE_KEY);
  if (!ledger) delete process.env.SUPABASE_SERVICE_KEY;
  for (const k of ["SUPABASE_URL", "SUPABASE_ANON_KEY", "ANTHROPIC_API_KEY"]) if (!process.env[k]) throw new Error(`${k} is not set (environment or .env)`);
  const qs = JSON.parse(fs.readFileSync(questionsPath, "utf8")).questions;
  const { ask } = await import("../lib/chat/ask.ts");
  const { runTool } = await import("../lib/chat/tools.ts");
  if (flag("--dry-run")) {
    const { out, isError } = await runTool("list_tables", {}, null);
    const tables = Array.isArray(out.tables) ? out.tables : [];
    console.log(JSON.stringify({ dry_run: true, questions: qs.length, ledger, list_tables_error: isError, n_tables: tables.length,
      in_live_set: tables.reduce((a, t) => ({ ...a, [t.in_live_set]: (a[t.in_live_set] ?? 0) + 1 }), {}) }));
    return 0;
  }
  let run = { _about: arg("--label") ?? "The questions asked through the site's own loop (site/lib/chat/ask.ts ask(), no build, the anon key), every tool call recorded, by site/scripts/eval-ask-site-loop.mjs under the ledger step site_ask_eval.",
    base: "site loop", questions: [] };
  if (fs.existsSync(runPath)) run = JSON.parse(fs.readFileSync(runPath, "utf8"));
  const done = new Map(run.questions.map((x) => [x.id, x]));
  const order = qs.map((x) => x.id);
  let dearest = Math.max(0, ...run.questions.map((x) => Number(x.cost_usd ?? 0)), ...(run.superseded ?? []).map((x) => Number(x.cost_usd ?? 0)));
  let stopped = null, failed = false;
  const under = askedUnder(process.env, JSON.parse(fs.readFileSync(path.join(here, "..", "lib", "chat", "spec.json"), "utf8")));
  for (const q of qs) {
    if (only ? !only.has(q.id) : done.has(q.id)) continue;
    const spent = costOf(run);
    const keep = reserve(done.size, dearest);
    if (spent + keep > cap) { stopped = q.id; console.log(`${q.id}: STOPPED before the call: spent ${spent.toFixed(4)} + reserve ${keep.toFixed(2)} > cap ${cap.toFixed(2)}`); break; }
    const at = new Date().toISOString().replace(/\.\d+Z$/, "Z");
    let r = null, error = null;
    const meter = {};   // session 5269: the loop's own count, read when it throws
    try {
      r = await ask(q.question, undefined, q.via === "grid" ? GRID_SLUG[q.grid] : null, null, null,
        { record: true, step: "site_ask_eval", strictLedger: ledger, questionId: crypto.randomBytes(16).toString("hex"), meter });
    } catch (e) {
      error = `${e?.name ?? "Error"}: ${e?.message ?? e}`.slice(0, 400);
    }
    const rec = { ...recordOf(q, r, at, error, meter), asked_under: under };
    dearest = Math.max(dearest, rec.cost_usd);
    done.set(q.id, rec);
    run = withRecord(run, rec, order);
    fs.writeFileSync(runPath, JSON.stringify(run, null, 1) + "\n");
    console.log(`${q.id} ${String(q.via).padEnd(7)} ${rec.status} calls ${rec.tool_calls} cost ${rec.cost_usd.toFixed(4)} ${rec.seconds}s${error ? ` ERROR ${error.slice(0, 160)}` : ""}`);
    if (error && !flag("--keep-going")) { stopped = `the question after ${q.id} (an error stops the run; --keep-going to go on)`; failed = true; break; }
  }
  const spent = costOf(run);
  console.log(`asked ${run.questions.length} of ${qs.length}${run.superseded?.length ? ` (${run.superseded.length} asked again)` : ""}; the run's cost USD ${spent.toFixed(4)}${stopped ? `; stopped before ${stopped}` : ""}`);
  return failed ? 3 : 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then((code) => process.exit(code), (e) => { console.error(`eval-ask-site-loop: ${e?.message ?? e}`); process.exit(1); });
}
