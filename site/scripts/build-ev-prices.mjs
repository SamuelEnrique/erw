// Energy Research Warehouse (ERW) site, session 294: the prices the EV game reads (site/data/ev_prices.json).
//
//   node scripts/build-ev-prices.mjs <warehouse/output directory>
//
// The two tables are in the warehouse but not in the live set (warehouse/supabase/live_set.yaml: the price board's
// series are read from the site's own files), so the game reads a file built from them, as the price board does:
//   eia_retail_electricity_prices     each state's average residential price (entity eia:retail_price:<ST>:RES), its
//                                     newest month; USD/MWh as the table holds it, which the game shows as cents a kWh
//   eia_regional_retail_fuel_prices   regular gasoline, weekly: the state's own series where EIA publishes one (nine
//                                     states), else its PADD region's (the East Coast by its three sub-regions, the West
//                                     Coast without California), and the US average; the newest week
// Each value keeps its table, entity, date and the table's own source line. Nothing is filled: a state without a held
// price is written without it, and the game says so. Reads only; writes the one file.
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = process.argv[2];
if (!dir || !fs.existsSync(dir)) { console.error("usage: node scripts/build-ev-prices.mjs <warehouse/output directory>"); process.exit(2); }

export const STATES = {
  AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California", CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "District of Columbia",
  FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana", ME: "Maine",
  MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada",
  NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York", NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon",
  PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia",
  WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming",
};
// EIA's Petroleum Administration for Defense Districts (PADDs), as EIA's gasoline survey publishes them: the East Coast
// (PADD 1) by its three sub-regions, PADD 5 without California for the West Coast states other than California
const REGION = {
  R1X: ["CT", "ME", "MA", "NH", "RI", "VT"], R1Y: ["DE", "DC", "MD", "NJ", "NY", "PA"], R1Z: ["FL", "GA", "NC", "SC", "VA", "WV"],
  R20: ["IL", "IN", "IA", "KS", "KY", "MI", "MN", "MO", "NE", "ND", "SD", "OH", "OK", "TN", "WI"], R30: ["AL", "AR", "LA", "MS", "NM", "TX"],
  R40: ["CO", "ID", "MT", "UT", "WY"], R5XCA: ["AK", "AZ", "HI", "NV", "OR", "WA"],
};
const REGION_NAME = { R1X: "New England (PADD 1A)", R1Y: "the Central Atlantic (PADD 1B)", R1Z: "the Lower Atlantic (PADD 1C)", R20: "the Midwest (PADD 2)",
  R30: "the Gulf Coast (PADD 3)", R40: "the Rocky Mountains (PADD 4)", R5XCA: "the West Coast without California (PADD 5 except California)" };

/** The newest row of each wanted entity, and the file's source and retrieval lines. */
async function newest(file, want) {
  const best = new Map();
  const head = [];
  let cols = null;
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(dir, file), "utf-8"), crlfDelay: Infinity });
  for await (const line of rl) {
    if (line.startsWith("#")) { head.push(line.slice(2)); continue; }
    if (!cols) { cols = line.split(","); continue; }
    const comma = line.indexOf(","), e = line.slice(0, comma);
    if (!want(e)) continue;
    const v = line.split(","), r = Object.fromEntries(cols.map((c, i) => [c, v[i]]));
    if (!best.has(e) || r.ts_utc > best.get(e).ts_utc) best.set(e, r);
  }
  const src = head.find((h) => h.startsWith("Source:")) ?? "", got = head.find((h) => h.startsWith("Retrieved:")) ?? "";
  return { rows: best, source: src.replace(/^Source:\s*/, ""), retrieved: got.replace(/^Retrieved:\s*/, "") };
}

const E = "eia_retail_electricity_prices", G = "eia_regional_retail_fuel_prices";
const el = await newest(`${E}.csv`, (e) => /^eia:retail_price:[A-Z]{2}:RES$/.test(e));
const gas = await newest(`${G}.csv`, (e) => /^eia:EMM_EPMR_PTE_(S[A-Z]{2}|R1X|R1Y|R1Z|R20|R30|R40|R5XCA|NUS)_DPG$/.test(e));
const g = (code) => gas.rows.get(`eia:EMM_EPMR_PTE_${code}_DPG`);
const cell = (r, table, extra = {}) => (r ? { value: Number(r.value), unit: r.unit, ts: r.ts_utc.slice(0, 10), entity: r.entity, table, ...extra } : null);

const states = Object.entries(STATES).map(([code, name]) => {
  const own = g(`S${code}`);
  const region = Object.keys(REGION).find((k) => REGION[k].includes(code));
  const gasCell = own ? cell(own, G, { where: "state" }) : cell(g(region), G, { where: "region", region: REGION_NAME[region] });
  return { code, name, power: cell(el.rows.get(`eia:retail_price:${code}:RES`), E), gas: gasCell };
});
const usPower = el.rows.get("eia:retail_price:US:RES");
const out = {
  built_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
  note: "Built by site/scripts/build-ev-prices.mjs from the ERW warehouse tables eia_retail_electricity_prices and eia_regional_retail_fuel_prices (EIA, public domain). Electricity: each state's average residential price, its newest month, USD/MWh. Gasoline: regular, weekly, the state's own where EIA publishes it, else its PADD region's.",
  sources: { [E]: { source: el.source, retrieved: el.retrieved }, [G]: { source: gas.source, retrieved: gas.retrieved } },
  us: { power: cell(usPower, E), gas: cell(g("NUS"), G, { where: "us" }) },
  states,
};
const target = path.join(here, "..", "data", "ev_prices.json");
fs.writeFileSync(target, JSON.stringify(out, null, 1) + "\n");
console.log(`${states.length} states: ${states.filter((s) => s.power).length} with a power price (newest ${[...new Set(states.map((s) => s.power?.ts))].join(", ")}), ${states.filter((s) => s.gas?.where === "state").length} with their own gasoline price, the rest by region (week ${g("NUS")?.ts_utc.slice(0, 10)}) -> ${target}`);
