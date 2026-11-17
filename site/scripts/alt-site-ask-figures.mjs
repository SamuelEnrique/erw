// Energy Research Warehouse (ERW) site, ruling alternatives of Ask, the chat (session 7707, 17 November 2026;
// wip/alt-site-ask-* branches, not a default on main). The site chat's own query tool run on rows made up here, read by
// a stand-in for the database (no request leaves the machine, no model is called). On wip/alt-site-ask-3: a mean of the
// hourly hub table over one whole calendar month is answered from the whole-month table, and a mean over part of a
// month is answered from the hourly table as on main. The monthly row's value is the live set's October 2026 figure for
// SP15 as the impact file read it (USD 46.78); the hourly rows are made up (40, 42 and 44).
//   node --import ./scripts/alias-register.mjs scripts/alt-site-ask-figures.mjs
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
const COLS = JSON.stringify(["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]);
const cat = (t, interval) => ({ table_name: t, iso: "CAISO", market: "caiso", n_nodes: 1, interval, ts_min: "2026-01-01T00:00:00+00:00", ts_max: "2026-11-01T00:00:00+00:00", n_rows: 10,
  source_report: "erw:fixture", last_run: null, validator_status: "pass", license: "public", sector: "power", derived: "yes", in_live_set: "yes", columns: COLS, tier: "derived" });
const E = "caiso:TH_SP15_GEN-APND";
const ROWS = [
  { table_name: "hub_price_comparison", entity: E, variable: "dam_avg_price", ts_utc: "2026-10-01T00:00:00Z", value: 46.78, unit: "USD/MWh", freq: "P1M" },
  { table_name: "hub_price_comparison", entity: E, variable: "dam_avg_price", ts_utc: "2026-10-01T00:00:00Z", value: 99.0, unit: "USD/MWh", freq: "P1Y" },
  ...[40, 42, 44].map((v, i) => ({ table_name: "iso_dam_hub_prices", entity: E, variable: "lmp_dam", ts_utc: `2026-10-2${i}T08:00:00Z`, value: v, unit: "USD/MWh", freq: "PT1H" })),
];
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body;
  if (u.pathname.endsWith("/catalogue")) body = [cat("hub_price_comparison", "P1M"), cat("iso_dam_hub_prices", "PT1H")];
  else if (u.pathname.endsWith("/sources") || u.pathname.endsWith("/headers")) body = [];
  else if (u.pathname.endsWith("/series")) {
    const table = (q.table_name ?? "").replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    const freq = /^in\.\("?([^")]+)"?\)$/.exec(q.freq ?? "")?.[1];
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."?([^",)]+)"?/.exec(q.and ?? "")?.[1];
    if (/node\.eq\./.test(q.and ?? "")) return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
    asked.push(table);
    body = ROWS.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!freq || r.freq === freq)
      && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit, freq: r.freq }));
  } else body = [];
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const T = await import("../lib/chat/tools.ts");
const value = (r) => r.out?.result?.[0]?.value ?? null;
const whole = await T.runTool("query", { table: "iso_dam_hub_prices", aggregation: "mean", entity: E, start: "2026-10-01", end: "2026-11-01" });
const wholeAsked = [...asked];
asked.length = 0;
const part = await T.runTool("query", { table: "iso_dam_hub_prices", aggregation: "mean", entity: E, start: "2026-10-12", end: "2026-11-01" });
process.stdout.write(JSON.stringify({
  whole: { value: value(whole), read_from: whole.out?.read_from ?? null, isError: whole.isError, asked: wholeAsked },
  part: { value: value(part), read_from: part.out?.read_from ?? null, isError: part.isError, asked: [...asked] },
  monthAsked: [T.monthAsked("2026-10-01", "2026-11-01"), T.monthAsked("2026-12-01T00:00:00Z", "2027-01-01"), T.monthAsked("2026-10-12", "2026-11-01"), T.monthAsked("2026-10-01", "2026-12-01")],
}));
