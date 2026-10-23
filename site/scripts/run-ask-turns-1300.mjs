// Energy Research Warehouse (ERW) site, session 1300: the scripted turns of tests/fixtures/session1300/turns.json run
// through the site's general chat (lib/chat/ask.ts, no grid, no profile) over the rows of
// tests/fixtures/session1112/held_reads.json, and what the loop returns printed as one JSON line, for
// tests/test_session1300.py to set beside the Python loop's (warehouse/chat/ask.py). No model is called and no request
// leaves: the model's replies are the script's, the database's the fixture's, the ledger's rows go nowhere; the key is
// not a key.
//
//   node --import ./scripts/alias-register.mjs scripts/run-ask-turns-1300.mjs
import fs from "node:fs";

const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf8"));
const FIX = read("../../tests/fixtures/session1112/held_reads.json");
const SET = read("../../tests/fixtures/session1300/turns.json");
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
process.env.ANTHROPIC_API_KEY = "a-stand-in-not-a-key";

// the database, as session 1126's test answers it
const db = (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body = [];
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/series") && !/node\.eq\./.test(q.and ?? "")) {
    const table = (q.table_name ?? "").replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."([^"]+)"/.exec(q.and ?? q.or ?? "")?.[1];
    const like = /entity\.like\.([a-z]+):\*/.exec(q.and ?? q.or ?? q.entity ?? "")?.[1];
    body = FIX.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!like || r.entity.startsWith(`${like}:`))
      && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .map((r) => ({ t: r.ts_utc, v: r.value, g: r.entity, entity: r.entity, variable: r.variable, unit: r.unit }));
  }
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};

// the model, as scripts/test-ask-ready.mjs stands in for it: one streamed reply a call, the script's turns in order
const sse = (reply) => {
  const ev = (type, data) => `event: ${type}\ndata: ${JSON.stringify({ type, ...data })}\n\n`;
  const blocks = reply.tools ? reply.tools.map((t, i) => [{ type: "tool_use", id: `toolu_fixture_${i + 1}`, name: t.name, input: {} }, { type: "input_json_delta", partial_json: JSON.stringify(t.input) }])
    : [[{ type: "text", text: "" }, { type: "text_delta", text: JSON.stringify(reply.text) }]];
  return ev("message_start", { message: { id: "msg_fixture", type: "message", role: "assistant", model: "claude-sonnet-5-5", content: [], stop_reason: null, stop_sequence: null,
    usage: { input_tokens: 100, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }) +
    blocks.map(([start, delta], index) => ev("content_block_start", { index, content_block: start }) + ev("content_block_delta", { index, delta }) + ev("content_block_stop", { index })).join("") +
    ev("message_delta", { delta: { stop_reason: reply.tools ? "tool_use" : "end_turn", stop_sequence: null }, usage: { output_tokens: 50 } }) + ev("message_stop", {});
};

let script = [], calls = 0;
globalThis.fetch = async (url, init) => {
  const u = new URL(typeof url === "string" ? url : url.url ?? String(url));
  if (u.hostname === "api.anthropic.com") {
    if (u.pathname === "/v1/models") return new Response(JSON.stringify({ data: [{ type: "model", id: "claude-sonnet-5-5", display_name: "a stand-in", created_at: "2026-01-01T00:00:00Z" }], has_more: false, first_id: "claude-sonnet-5-5", last_id: "claude-sonnet-5-5" }), { status: 200, headers: { "content-type": "application/json" } });
    const reply = script[calls] ?? script[script.length - 1];
    calls += 1;
    return new Response(sse(reply), { status: 200, headers: { "content-type": "text/event-stream", "request-id": `req_fixture_${calls}` } });
  }
  if ((init?.method ?? "GET") === "POST") return new Response("", { status: 201 });
  return db(url);
};

const ask = await import("../lib/chat/ask.ts");
const out = {};
for (const s of SET.scenarios) {
  script = s.turns;
  calls = 0;
  const r = await ask.ask(s.question, SET.today, null, null, null, {});
  out[s.id] = { status: r.status, retried: !!r.retried, tool_calls: r.tool_calls, model_calls: calls, citations: (r.citations ?? []).map((c) => c.table).sort(), answer: r.answer, why: r.why ?? "" };
}
console.log(JSON.stringify(out));
