// Energy Research Warehouse (ERW) site, session 143: one question through the loop itself (lib/chat/ask.ts with the
// ERCOT profile), printing every tool call with its arguments and the head of its result, to see what a question reads.
//
//   node --env-file=.env.local --import ./scripts/alias-register.mjs scripts/probe-ask-ercot.mjs <spend.json> "question"
//
// EVERY RUN IS MODEL CALLS THAT COST MONEY. Each call is written to the site's cost ledger (step site_ask_ercot) as
// the route's are, and the answer's cost is added to the run "probes" of <spend.json>, the session's spending file,
// which is read first: the probe does not start when the session's spend plus a reserve of 0.15 would pass its stop.
// The route's ceilings are not asked here (no visitor is counted): a tool for a session's own diagnosis, never a page.
import fs from "node:fs";
import { mayAsk, sessionSpend } from "./eval-spend.mjs";

const [spendFile, question] = process.argv.slice(2);
if (!spendFile || !question) { console.log("usage: probe-ask-ercot.mjs <spend.json> \"question\""); process.exit(2); }
const spend = JSON.parse(fs.readFileSync(spendFile, "utf8"));
if (!mayAsk(sessionSpend(spend), 0.15, spend.stop_usd)) { console.log(`STOPPED before the probe: USD ${sessionSpend(spend).toFixed(4)} spent of a stop of ${spend.stop_usd}`); process.exit(3); }
let mine = spend.runs.find((r) => r.name === "probes");
if (!mine) { mine = { name: "probes", usd: 0, questions: 0, errors: 0, started: new Date().toISOString() }; spend.runs.push(mine); }
const save = () => { spend.total_usd = Math.round(sessionSpend(spend) * 1e6) / 1e6; fs.writeFileSync(spendFile, JSON.stringify(spend, null, 1) + "\n"); };

const { ask } = await import("../lib/chat/ask.ts");
const { ercotProfile } = await import("../lib/chat/ercot.ts");
const { questionId } = await import("../lib/chat/limits.ts");
const profile = ercotProfile();
const finish = profile.finish;
profile.finish = (status, draft, records) => {
  for (const r of records) console.log(`TOOL ${r.tool} ${JSON.stringify(r.input)}\n   -> ${r.isError ? "ERROR " : ""}${JSON.stringify(r.out).slice(0, 420)}`);
  return finish(status, draft, records);
};
let r;
try {
  r = await ask(question, undefined, null, profile, { view: "/ask/ercot", title: "Ask ERCOT", settings: { grid: "ERCOT" } }, { questionId: questionId(), onEvent: (e) => console.log(`EVENT ${JSON.stringify(e).slice(0, 200)}`),
    ...(process.env.PROBE_THINKING ? { thinking: (t) => console.log(`THINKING ${t.slice(0, 1500)}`) } : {}) });
} catch (e) {
  mine.usd = Math.round((mine.usd + 0.15) * 1e6) / 1e6; mine.errors += 1; save();        // an unknown cost counts as the reserve
  console.log(`ERROR ${e.message}`); process.exit(1);
}
mine.usd = Math.round((mine.usd + (r.cost_usd ?? 0.15)) * 1e6) / 1e6; mine.questions += 1; save();
for (const s of r.steps ?? []) console.log(`STEP ${s.stage} ${s.what} ${s.ms} ms ${JSON.stringify(Object.fromEntries(Object.entries(s).filter(([k]) => !["stage", "what", "ms", "calls"].includes(k))))}`);
console.log(JSON.stringify({ status: r.status, form: r.form, answer: r.answer, series: (r.series ?? []).length, followups: r.followups, cost_usd: r.cost_usd, seconds: r.seconds, seconds_words: r.seconds_words, stages_ms: r.stages_ms, usage: r.usage, retried: r.retried }, null, 1));
console.log(`session USD ${sessionSpend(spend).toFixed(4)}`);
