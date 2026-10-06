// Energy Research Warehouse (ERW) site, session 137: the 100 test questions of Ask ERCOT as the answer panel.
//
//   node scripts/eval-ask-panel.mjs <base-url> <out.jsonl> [--budget USD] [--kind conceptual,chart,...] [--ids c01,h02,...]
//
// Asks each question of warehouse/chat/eval_ercot_panel.json once on the running site's own route (POST /api/ask,
// profile ercot, streamed), one after another, and judges the answer by the rule of its kind, the same rule whatever
// version of the tool is running. One line per question goes to <out.jsonl>: the kind, pass or fail with the reasons,
// the status, the form, the series, the cost the server reported (its own model calls for that question, as its
// ledger records them), the seconds to the first sign a reader sees (the first event after "started"), to the model's
// first reply, and to the answer. The run stops BEFORE a question when the cost so far plus a reserve for one more
// question (--reserve, default 0.20) would pass --budget: the budget is never passed by starting a question.
// Each question is sent with its own made-up address in x-forwarded-for, so the route's per-address limits (ten an
// hour in memory, and the database's per-visitor count) see 100 visitors of one question, not one of 100. A local
// test server only: production's limits are not touched by this script.
// Exit 0 when it ran to the end, 3 when the budget stopped it, 1 on a transport failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { judge, words } from "./eval-judge.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const SET = JSON.parse(fs.readFileSync(path.resolve(here, "..", "..", "warehouse", "chat", "eval_ercot_panel.json"), "utf8"));
const args = process.argv.slice(2);
const base = (args[0] ?? "").replace(/\/$/, ""), out = args[1];
const opt = (name, d) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : d; };
const budget = Number(opt("--budget", "1")), reserve = Number(opt("--reserve", "0.20"));
const kinds = opt("--kind", "") ? opt("--kind", "").split(",") : null, ids = opt("--ids", "") ? opt("--ids", "").split(",") : null;
if (!base || !out) { console.log("usage: eval-ask-panel.mjs <base-url> <out.jsonl> [--budget USD] [--kind k1,k2] [--ids a,b]"); process.exit(2); }

async function one(q, n) {
  const t0 = Date.now();
  const res = await fetch(`${base}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-forwarded-for": `10.137.${Math.floor(n / 250)}.${(n % 250) + 1}` },
    body: JSON.stringify({ question: q.q, profile: "ercot", stream: true, context: { view: "/ask/ercot", title: "Ask ERCOT", settings: { grid: "ERCOT" } } }),
  });
  if (!res.ok || !res.body) return { http: res.status, error: (await res.text()).slice(0, 300), seconds: (Date.now() - t0) / 1000 };
  const dec = new TextDecoder();
  let buf = "", firstSign = null, result = null, error = null;
  const signs = [];
  for await (const chunk of res.body) {
    buf += dec.decode(chunk, { stream: true });
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      const e = JSON.parse(line);
      if (e.type !== "started" && firstSign === null) firstSign = (Date.now() - t0) / 1000;
      if (e.type === "result") result = e;
      else if (e.type === "error") error = e.error;
      else if (e.type !== "started") signs.push(e.type);
    }
  }
  return { http: 200, result, error, first_sign: firstSign, signs, seconds: (Date.now() - t0) / 1000 };
}

const todo = SET.questions.filter((q) => (!kinds || kinds.includes(q.kind)) && (!ids || ids.includes(q.id)));
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
let spent = 0, n = 0, stopped = false, failed = false;
const tally = {};
for (const q of todo) {
  if (spent + reserve > budget) { stopped = true; console.log(`STOPPED before ${q.id}: USD ${spent.toFixed(4)} spent, a reserve of ${reserve} would pass the budget of ${budget}`); break; }
  n += 1;
  let a;
  try { a = await one(q, Number(opt("--offset", "0")) + n); } catch (e) { console.log(`${q.id}: transport failure ${e.message}`); failed = true; break; }
  const r = a.result ?? {};
  const cost = typeof r.cost_usd === "number" ? r.cost_usd : 0;
  spent += cost;
  const why = a.result ? judge(q, r) : [a.error ? `error: ${String(a.error).slice(0, 120)}` : `HTTP ${a.http}`];
  const pass = why.length === 0;
  tally[q.kind] ??= { n: 0, pass: 0 };
  tally[q.kind].n += 1; tally[q.kind].pass += pass ? 1 : 0;
  const line = { id: q.id, kind: q.kind, new: q.new ?? null, q: q.q, pass, why, status: r.status ?? null, form: r.form ?? null, words: words(r.answer),
    series: (r.series ?? []).map((s) => ({ table: s.table, rows: (s.rows ?? []).length, same: s.check?.same ?? null })), citations: (r.citations ?? []).map((c) => c.table), 
    tool_calls: r.tool_calls ?? null, requests: r.usage?.requests ?? null, cost_usd: cost, question_id: r.question_id ?? null, seconds_first_sign: a.first_sign, seconds_first_reply: r.seconds_first ?? null,
    seconds: Math.round(a.seconds * 10) / 10, answer: String(r.answer ?? a.error ?? "").slice(0, 600) };
  fs.appendFileSync(out, JSON.stringify(line) + "\n");
  console.log(`${pass ? "pass" : "FAIL"} ${q.id} ${q.kind} USD ${cost.toFixed(4)} ${line.seconds}s${pass ? "" : " : " + why.join("; ")}`);
}
console.log(Object.entries(tally).map(([k, t]) => `${k} ${t.pass}/${t.n}`).join(", ") + `; USD ${spent.toFixed(4)} for ${n} questions`);
process.exit(failed ? 1 : stopped ? 3 : 0);
