// Energy Research Warehouse (ERW) site, session 1110: writes the two tool results the six answers of
// tests/fixtures/session1110/answers.json are checked against, from the saved rows of session 1109
// (tests/fixtures/session1109/battery_reads.json). No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/record-ask-1110.mjs > ../tests/fixtures/session1110/sources.json
import fs from "node:fs";

const FIX = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session1109/battery_reads.json", import.meta.url), "utf8"));
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body = [];
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/series") && !/node\.eq\./.test(q.and ?? "")) {
    const variable = (q.variable ?? "").replace(/^eq\./, "");
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."([^"]+)"/.exec(q.and ?? q.or ?? "")?.[1];
    body = FIX.rows.filter((r) => (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit }));
  }
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const { runTool } = await import("../lib/chat/tools.ts");
const q = FIX.questions.b01;
const sum = await runTool("query", { table: "battery_stack_monthly", aggregation: "sum", entity: q.entity, variable: q.variable, start: q.start, end: q.end });
const months = await runTool("query", { table: "battery_stack_monthly", aggregation: "sum", entity: q.entity, variable: q.variable, start: q.start, end: q.end, group_by: "month" });
process.stdout.write(JSON.stringify({ _about: "Session 1110: two query results of the site's tool on session 1109's saved rows (b01's twelve months), written by site/scripts/record-ask-1110.mjs", question: "For a 4-hour battery at ERCOT's hub average with perfect foresight, what was the total revenue over 2025-10 to 2026-09?", sources: [JSON.stringify(sum.out), JSON.stringify(months.out)] }, null, 1) + "\n");
