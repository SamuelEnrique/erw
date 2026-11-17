// Energy Research Warehouse (ERW) site, ruling alternatives of Ask, the chat (session 7707, 17 November 2026;
// wip/alt-site-ask-* branches, not a default on main). The site chat's own tools run on rows read by a stand-in for the
// database (no request leaves the machine, no model is called). On wip/alt-site-ask-2: Ask ERCOT's scope, as
// lib/chat/ercot.ts builds it from spec_ercot.json, reads hub_price_comparison for ERCOT's hub average and SP15, and its
// compare tool gives the spread. The monthly rows' values are the live set's October 2026 figures as the impact file read
// them (SP15 USD 46.78, ERCOT's hub average 36.73); a yearly row of each is made up to show the freq filter holds.
//   node --import ./scripts/alias-register.mjs scripts/alt-site-ask-figures.mjs
import fs from "node:fs";

process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
const spec = JSON.parse(fs.readFileSync(new URL("../lib/chat/spec_ercot.json", import.meta.url), "utf8"));
const COLS = JSON.stringify(["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]);
const cat = (t) => ({ table_name: t, iso: "CAISO;ERCOT", market: "", n_nodes: 2, interval: "P1M;P1Y", ts_min: "2025-11-01T00:00:00+00:00", ts_max: "2026-10-01T00:00:00+00:00", n_rows: 10,
  source_report: "erw:hub_price_comparison", last_run: null, validator_status: "pass", license: "public", sector: "power", derived: "yes", in_live_set: "yes", columns: COLS, tier: "derived" });
const row = (entity, v, freq) => ({ entity, variable: "dam_avg_price", ts_utc: "2026-10-01T00:00:00Z", value: v, unit: "USD/MWh", freq });
const ROWS = [row("caiso:TH_SP15_GEN-APND", 46.78, "P1M"), row("ercot:HB_HUBAVG", 36.73, "P1M"), row("caiso:TH_SP15_GEN-APND", 90, "P1Y"), row("ercot:HB_HUBAVG", 10, "P1Y"),
  row("pjm:WESTERN HUB", 55, "P1M")];
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body;
  if (u.pathname.endsWith("/catalogue")) body = [cat("hub_price_comparison")];
  else if (u.pathname.endsWith("/sources") || u.pathname.endsWith("/headers")) body = [];
  else if (u.pathname.endsWith("/series")) {
    asked.push(Object.entries(q).filter(([k]) => k !== "select").map(([k, v]) => `${k}=${v}`).join("&"));
    const freq = /^in\.\("?([^")]+)"?\)$/.exec(q.freq ?? "")?.[1];
    const ents = /^in\.\((.*)\)$/.exec(q.entity ?? "")?.[1]?.split(",").map((s) => s.replace(/"/g, "")) ?? null;
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."?([^",)]+)"?/.exec(q.and ?? "")?.[1];
    if (/node\.eq\./.test(q.and ?? "")) return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
    body = ROWS.filter((r) => (!freq || r.freq === freq) && (!ents || ents.includes(r.entity)) && (!entity || r.entity === entity)
      && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit, freq: r.freq }));
  } else body = [];
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const T = await import("../lib/chat/tools.ts");
const scope = { ...T.scopeOf("ercot"), tables: spec.tables, filters: spec.filters, max_groups: spec.max_groups, dated_groups: spec.dated_groups };
const side = (entity) => ({ table: "hub_price_comparison", aggregation: "mean", entity, variable: "dam_avg_price", where: { freq: "P1M" }, start: "2026-10-01", end: "2026-11-01" });
const c = await T.runTool("compare", { a: side("ercot:HB_HUBAVG"), b: side("caiso:TH_SP15_GEN-APND") }, scope);
const pjm = await T.runTool("query", side("pjm:WESTERN HUB"), scope);
process.stdout.write(JSON.stringify({
  inScope: spec.tables.includes("hub_price_comparison"), filter: spec.filters.hub_price_comparison,
  a: c.out?.a?.result?.[0]?.value ?? null, b: c.out?.b?.result?.[0]?.value ?? null, difference: c.out?.difference_b_minus_a ?? null, isError: c.isError,
  pjm: { isError: pjm.isError, value: pjm.out?.result?.[0]?.value ?? null },
  ruleThree: /One exception: ERCOT's hub average beside California's SP15 hub/.test(spec.system),
}));
