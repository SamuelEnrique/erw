// Energy Research Warehouse (ERW) site, session 143: Ask ERCOT's speed, measured on the 100 test questions of session
// 137 (warehouse/chat/eval_ercot_panel.json), stage by stage, under one spending cap for the whole session.
//
//   node scripts/eval-ask-speed.mjs <base-url> <out.jsonl> --run <name> --spend <spend.json> --stop <USD>
//        [--reserve USD] [--ids c01,h02,...] [--kind conceptual,...] [--skip <earlier.jsonl>] [--offset N]
//
// Each question is asked once on the running site's own route (POST /api/ask, profile ercot, streamed), one after
// another, and judged by the rule of its kind (scripts/eval-judge.mjs, the same rule as session 137). One line per
// question goes to <out.jsonl>: pass or fail with the reasons, the cost the server reported (its own model calls for
// that question, as its ledger records them), and the seconds a reader waits, taken here, at the reader's end:
//
//   seconds_first_sign  to the first thing shown (a table being read, the words, or the answer)
//   seconds_words       to the answer's words on screen (the "words" line, or the whole answer when none came first)
//   seconds             to the whole answer, with its chart or table
//
// and the server's own record of where the time went: stages_ms (planning, fetching, drawing, writing, other, summing
// to total) and its steps (each model call with its model, each turn of tool calls).
//
// THE CAP. <spend.json> holds what the session has spent so far, run by run. The runner stops BEFORE a question when
// the session's spend plus a reserve for one more question (--reserve, default 0.15) would pass --stop. It never checks
// after, and an answer already paid for is always written. A question that ends in an error has an unknown cost: the
// reserve is counted for it, so the file can only overstate the spend. The file is rewritten after every question.
// Each question is sent from its own made-up address (10.143.x.y), as session 137's runner did, so the route's
// per-address limits see one visitor a question. A local test server only: production is never asked.
// Exit 0 when it ran to the end, 3 when the cap stopped it, 1 on a transport failure, 2 on bad arguments.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { judge, words } from "./eval-judge.mjs";
import { mayAsk, sessionSpend } from "./eval-spend.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const SET = JSON.parse(fs.readFileSync(path.resolve(here, "..", "..", "warehouse", "chat", "eval_ercot_panel.json"), "utf8"));
const args = process.argv.slice(2);
const base = (args[0] ?? "").replace(/\/$/, ""), out = args[1];
const opt = (name, d) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : d; };
const run = opt("--run", ""), spendFile = opt("--spend", ""), stop = Number(opt("--stop", "NaN")), reserve = Number(opt("--reserve", "0.15"));
const kinds = opt("--kind", "") ? opt("--kind", "").split(",") : null, ids = opt("--ids", "") ? opt("--ids", "").split(",") : null;
if (!base || !out || !run || !spendFile || !Number.isFinite(stop)) { console.log("usage: eval-ask-speed.mjs <base-url> <out.jsonl> --run <name> --spend <spend.json> --stop <USD> [--reserve USD] [--ids a,b] [--kind k] [--skip earlier.jsonl]"); process.exit(2); }
if (!/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(base)) { console.log("this runner asks a local server only"); process.exit(2); }

const spend = fs.existsSync(spendFile) ? JSON.parse(fs.readFileSync(spendFile, "utf8")) : { cap_usd: 3.0, stop_usd: stop, runs: [] };
let mine = spend.runs.find((r) => r.name === run);
if (!mine) { mine = { name: run, usd: 0, questions: 0, errors: 0, started: new Date().toISOString() }; spend.runs.push(mine); }
const save = () => { spend.total_usd = Math.round(sessionSpend(spend) * 1e6) / 1e6; fs.writeFileSync(spendFile, JSON.stringify(spend, null, 1) + "\n"); };

async function one(q, n) {
  const t0 = Date.now();
  const res = await fetch(`${base}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-forwarded-for": `10.143.${Math.floor(n / 250)}.${(n % 250) + 1}` },
    body: JSON.stringify({ question: q.q, profile: "ercot", stream: true, context: { view: "/ask/ercot", title: "Ask ERCOT", settings: { grid: "ERCOT" } } }),
  });
  if (!res.ok || !res.body) return { http: res.status, error: (await res.text()).slice(0, 300), seconds: (Date.now() - t0) / 1000 };
  const dec = new TextDecoder();
  let buf = "", firstSign = null, wordsAt = null, withdrawn = 0, result = null, error = null;
  const signs = [];
  for await (const chunk of res.body) {
    buf += dec.decode(chunk, { stream: true });
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      const e = JSON.parse(line);
      const at = (Date.now() - t0) / 1000;
      if (e.type !== "started" && firstSign === null) firstSign = at;
      if (e.type === "words") wordsAt = at;                       // the newest words: words taken back are not the answer's
      else if (e.type === "withdrawn") { wordsAt = null; withdrawn += 1; }
      if (e.type === "result") result = e;
      else if (e.type === "error") error = e.error;
      else if (e.type !== "started") signs.push(e.type);
    }
  }
  const seconds = (Date.now() - t0) / 1000;
  return { http: 200, result, error, first_sign: firstSign, words_at: result ? wordsAt ?? seconds : null, words_first: wordsAt !== null, withdrawn, signs, seconds };
}

const skip = new Set();
for (const f of (opt("--skip", "") || "").split(",").filter(Boolean)) if (fs.existsSync(f)) for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) skip.add(JSON.parse(l).id);
const kept = SET.questions.filter((q) => (!kinds || kinds.includes(q.kind)) && (!ids || ids.includes(q.id)) && !skip.has(q.id));
// --interleave: one question of each kind in turn (the first left of each, then the second, ...), so that a run the cap
// stops early has asked about as many of one kind as of another
const rank = new Map(), seen = {};
for (const q of kept) { seen[q.kind] = (seen[q.kind] ?? 0) + 1; rank.set(q.id, seen[q.kind]); }
const todo = args.includes("--interleave") ? [...kept].sort((a, b) => rank.get(a.id) - rank.get(b.id)) : kept;
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
let n = 0, stopped = false, failed = false;
const tally = {}, r1 = (x) => (x === null || x === undefined ? null : Math.round(x * 10) / 10);
for (const q of todo) {
  if (!mayAsk(sessionSpend(spend), reserve, stop)) { stopped = true; console.log(`STOPPED before ${q.id}: the session has spent USD ${sessionSpend(spend).toFixed(4)}; a reserve of ${reserve} for one more question would pass the stop of ${stop}. Not asked: ${todo.slice(todo.indexOf(q)).map((x) => x.id).join(",")}`); break; }
  n += 1;
  let a;
  try { a = await one(q, Number(opt("--offset", "0")) + n); } catch (e) { console.log(`${q.id}: transport failure ${e.message}`); mine.usd += reserve; mine.errors += 1; save(); failed = true; break; }
  const r = a.result ?? {};
  const known = typeof r.cost_usd === "number";
  const cost = known ? r.cost_usd : 0;
  mine.usd = Math.round((mine.usd + (known ? cost : reserve)) * 1e6) / 1e6;      // an unknown cost counts as the reserve
  mine.questions += 1; mine.errors += known ? 0 : 1;
  save();
  const why = a.result ? judge(q, r) : [a.error ? `error: ${String(a.error).slice(0, 160)}` : `HTTP ${a.http}`];
  const pass = why.length === 0;
  tally[q.kind] ??= { n: 0, pass: 0 };
  tally[q.kind].n += 1; tally[q.kind].pass += pass ? 1 : 0;
  const steps = Array.isArray(r.steps) ? r.steps : [];
  const line = { run, id: q.id, kind: q.kind, new: q.new ?? null, q: q.q, pass, why, status: r.status ?? null, form: r.form ?? null, words: words(r.answer),
    series: (r.series ?? []).map((s) => ({ table: s.table, rows: (s.rows ?? []).length, same: s.check?.same ?? null })), citations: (r.citations ?? []).map((c) => c.table),
    tool_calls: r.tool_calls ?? null, requests: r.usage?.requests ?? null, retried: r.retried ?? null, cost_usd: cost, cost_known: known, model: r.model ?? null,
    models: [...new Set(steps.filter((s) => s.what === "model").map((s) => `${s.stage}:${s.model}`))],
    // session 148: whether the read was written by rule and for which shape, and the effort each model call was given
    planned_by: r.planned_by ?? null, plan_shape: r.plan_shape ?? null, efforts: steps.filter((s) => s.what === "model").map((s) => `${s.role ?? ""}:${s.effort ?? ""}`),
    seconds_first_sign: r1(a.first_sign), seconds_words: r1(a.words_at), words_first: a.words_first ?? false, withdrawn: a.withdrawn ?? 0, seconds: r1(a.seconds),
    server_seconds: r.seconds ?? null, server_seconds_words: r.seconds_words ?? null, stages_ms: r.stages_ms ?? null, steps, answer: String(r.answer ?? a.error ?? "").slice(0, 700) };
  fs.appendFileSync(out, JSON.stringify(line) + "\n");
  const st = line.stages_ms;
  console.log(`${pass ? "pass" : "FAIL"} ${q.id} ${q.kind} USD ${cost.toFixed(4)} words ${line.seconds_words}s whole ${line.seconds}s` +
    (st ? ` [plan ${st.planning} fetch ${st.fetching} draw ${st.drawing} write ${st.writing} other ${st.other} = ${st.total} ms]` : "") + ` calls ${line.tool_calls} session USD ${sessionSpend(spend).toFixed(4)}${pass ? "" : " : " + why.join("; ")}`);
}
console.log(Object.entries(tally).map(([k, t]) => `${k} ${t.pass}/${t.n}`).join(", ") + `; run ${run} USD ${mine.usd.toFixed(4)} for ${n} questions; session USD ${sessionSpend(spend).toFixed(4)} of a stop of ${stop}`);
process.exit(failed ? 1 : stopped ? 3 : 0);
