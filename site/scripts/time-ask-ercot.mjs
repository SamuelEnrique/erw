// Energy Research Warehouse (ERW) site, session 121: how long Ask ERCOT takes on the site itself, as a reader waits.
//
//   node scripts/time-ask-ercot.mjs <base-url> <out.json> [question ...]
//
// Each question is posted to <base>/api/ask as the page posts it ({profile: "ercot", stream: true}) and three times are
// taken, in seconds from the request: the first byte of the answer's body; the first thing a reader is shown (the
// first line that names a table being read, or the answer when no table was read); the whole answer. A route that does
// not stream (the site before session 121) answers in one piece: the three are then the same moment, which is what its
// reader saw. EVERY QUESTION IS A MODEL CALL THAT COSTS MONEY (the answer's own cost_usd is recorded and summed): run
// it with the few questions given, never in a loop. The route allows 10 questions an hour from one address.
import fs from "node:fs";

const [base, out, ...asked] = process.argv.slice(2);
if (!base || !out) { console.error("usage: node scripts/time-ask-ercot.mjs <base-url> <out.json> [question ...]"); process.exit(2); }
const QUESTIONS = asked.length ? asked : [
  "In August 2023, what was the load-weighted real-time price of power at the hub average, and what was the carbon intensity of ERCOT's generation that month?",
  "How much battery does Texas have?",
  "What's a normal price for electricity in ERCOT?",
  "Why did real-time prices at the ERCOT hub average come to more than 200 USD per MWh on average in 2023?",
  "What does a household in Houston pay per kWh on its electricity bill?",
  "What is the weather forecast for Dallas tomorrow?",
];
const rows = [];
for (const question of QUESTIONS) {
  const t0 = performance.now();
  const secs = () => Math.round((performance.now() - t0) / 100) / 10;
  const row = { question, http: null, first_byte: null, first_shown: null, full: null, status: null, tool_calls: null, cost_usd: null, server_seconds: null, server_seconds_first: null, streamed: false, error: null };
  try {
    const r = await fetch(`${base.replace(/\/$/, "")}/api/ask`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question, profile: "ercot", stream: true }) });
    row.http = r.status;
    row.streamed = (r.headers.get("content-type") ?? "").includes("ndjson");
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = "", result = null;
    const take = (line) => {
      if (!line.trim()) return;
      const e = JSON.parse(line);
      if (!row.streamed) { result = e; return; }
      if (e.type === "reading" && row.first_shown === null) row.first_shown = secs();
      if (e.type === "result") result = e;
      if (e.type === "error") row.error = e.error;
    };
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      if (row.first_byte === null) row.first_byte = secs();
      buf += dec.decode(value, { stream: true });
      if (row.streamed) { let i; while ((i = buf.indexOf("\n")) >= 0) { take(buf.slice(0, i)); buf = buf.slice(i + 1); } }
    }
    take(buf);
    row.full = secs();
    if (row.first_shown === null) row.first_shown = row.full;   // nothing was shown before the answer
    if (result) Object.assign(row, { status: result.status ?? null, tool_calls: result.tool_calls ?? null, cost_usd: result.cost_usd ?? null, server_seconds: result.seconds ?? null,
      server_seconds_first: result.seconds_first ?? null, error: result.error ?? row.error });
  } catch (e) {
    row.error = String(e.message ?? e);
    row.full = secs();
  }
  rows.push(row);
  console.log(`${row.http} ${row.status ?? row.error} first shown ${row.first_shown} s, full ${row.full} s, calls ${row.tool_calls}, USD ${row.cost_usd}: ${question.slice(0, 70)}`);
}
const med = (k) => { const v = rows.map((r) => r[k]).filter((x) => typeof x === "number").sort((a, b) => a - b); return v.length ? v[Math.floor((v.length - 1) / 2)] : null; };
const summary = { base, at: new Date().toISOString(), questions: rows.length, answered: rows.filter((r) => r.status).length, streamed: rows.some((r) => r.streamed),
  median_first_shown: med("first_shown"), median_full: med("full"), cost_usd: Math.round(rows.reduce((a, r) => a + (r.cost_usd ?? 0), 0) * 1e4) / 1e4 };
fs.writeFileSync(out, JSON.stringify({ summary, rows }, null, 1) + "\n");
console.log(JSON.stringify(summary));
