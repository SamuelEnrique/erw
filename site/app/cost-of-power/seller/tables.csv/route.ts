// Energy Research Warehouse (ERW) site, session 212: GET /cost-of-power/seller/tables.csv?iso=..&asset=..&hub=..&mw=..
// The tables "What a generator earns" drew until this session and draws no longer (the owner's chain prompt of
// 12 October 2026, the battery page's layout: extra tables go into the CSV download), in one long-form CSV, a row a
// cell: `table`, `row`, `column`, `value`, `note`. The tables: the capture price at every hub and zone of the grid over
// the last twelve months (capture_last_twelve), by year at the hub chosen (capture_by_year), every public hub and zone
// of every grid by year (capture_hub_year, lib/capture.ts hubYears), the plant with a battery beside it (battery_beside:
// the co-optimized pair at day-ahead prices and the kept row at real-time prices), the stress days (stress_days,
// ERCOT) and the fleet's hours as EIA reports them (eia_hours). The same read and arithmetic as the page (model.ts). A
// value not held is blank, with its reason in `note`. In review, the address answers a visitor as the page does.
import { FUELS, MARKETS, hubName, hubYears, type Fuel, type Market } from "@/lib/capture";
import { EVENTS } from "@/lib/merchant";
import { statusOf } from "@/lib/release";
import { internalView } from "../../battery/read";
import { cell, csv, text } from "../csv";
import { CAPTURE, HYBRID, NEAR, modelOf } from "../model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const q = Object.fromEntries([...sp.entries()]) as Record<string, string | undefined>;
  if (!(await internalView()) && statusOf("/cost-of-power/seller") === "review") return text("in review: this download opens with the page it belongs to", 404);
  let M;
  try {
    M = await modelOf(q);
  } catch (e) {
    return text(`the model could not be read: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  const { x, g, hub, cg, iso, cap, mk, other, why, yearRows, pair, hf, batt, plantTotal, both, snap, sizeLabel, st, fuel, bmw, dur, pairSpan, plantName } = M;
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const f = (v: number | null | undefined, d: number) => (v === null || v === undefined || !Number.isFinite(v) ? "" : v.toFixed(d));
  const lines: string[] = [
    `# Energy Research Warehouse (ERW): the tables of "What a generator earns" beside the page, ${g.name}, ${hubName(hub.id)}, ${x.asset}, ${sizeLabel}`,
    `# long form: one row a cell (table, row, column, value, note); a value not held is blank with its reason in note`,
    `# sources: the capture prices data/seller/capture.json (warehouse/derived/capture_price.py), built ${CAPTURE.built.slice(0, 10)}; the pair with a battery data/seller/hybrid.json (warehouse/derived/seller_hybrid.py), built ${HYBRID.built.slice(0, 10)}; the model's snapshot data/merchant_snapshot.json, built ${snap.built.slice(0, 10)}; the battery beside it from the live set (battery_stack_monthly); derived by the ERW from ${g.name}'s public prices and EIA-930's hourly generation by source (${cg.workbook}); read at ${now}`,
    `# battery_beside: both rows are priced at ${g.at}, ${g.name}'s main hub, whatever hub is chosen (the battery page prices there)`,
    `# a capture price is the generation-weighted price the grid's whole fleet received by the hour, not one site's; premium is that less the flat average of every hour; pct is the premium as a percent of the flat average; hours are the hours counted`,
    `# method: /data/methods/generator_earns_algorithm (sections 4.5 to 4.7, 4.11, 4.16 and 4.17 as the page drew them until session 212); the page: /cost-of-power/seller`,
    "table,row,column,value,note",
  ];
  const put = (table: string, row: string, column: string, value: unknown, note = "") => lines.push([table, row, column, value, note].map(cell).join(","));

  // 1. the capture price at every hub and zone of the grid, last twelve months, both markets
  for (const h of cg.hubs) {
    for (const m of [mk, other] as Market[]) for (const fu of FUELS) {
      const c = cap(h, fu, m);
      const col = `${fu}_${MARKETS[m].toLowerCase().replace(/[ -]/g, "_")}`;
      if (!c) { put("capture_last_twelve", hubName(h.id), `${col}_price`, "", why(h, fu, m)); continue; }
      put("capture_last_twelve", hubName(h.id), `${col}_price`, f(c.price, 4), `${c.from} to ${c.to}`);
      put("capture_last_twelve", hubName(h.id), `${col}_flat`, f(c.flat, 4));
      put("capture_last_twelve", hubName(h.id), `${col}_premium`, f(c.premium, 4));
      put("capture_last_twelve", hubName(h.id), `${col}_pct`, f(c.pct, 2));
      put("capture_last_twelve", hubName(h.id), `${col}_hours`, String(c.hours));
    }
  }
  // 2. by year at the hub chosen, both markets
  for (const m of [mk, other] as Market[]) {
    for (const r of yearRows(m)) {
      for (const fu of FUELS) {
        const c = r[fu];
        const col = `${fu}_${MARKETS[m].toLowerCase().replace(/[ -]/g, "_")}`;
        const note = r.partial ? `${r.months} of 12 months counted: a partial year` : "";
        if (!c) { put("capture_by_year", r.label, `${col}_price`, "", r.label === "Last 12 months" ? why(hub, fu, m) : `No month of ${r.label} holds at least ${Math.round(NEAR * 100)} percent of its hours with both a price and the grid's ${fu} generation.`); continue; }
        put("capture_by_year", r.label, `${col}_price`, f(c.price, 4), note);
        put("capture_by_year", r.label, `${col}_flat`, f(c.flat, 4), note);
        put("capture_by_year", r.label, `${col}_premium`, f(c.premium, 4), note);
        put("capture_by_year", r.label, `${col}_pct`, f(c.pct, 2), note);
      }
    }
  }
  // 3. every public hub and zone of every grid, by year and over the last twelve months
  const hy = hubYears(CAPTURE);
  for (const r of hy.rows) {
    const row = `${r.gridName}: ${r.name}`;
    for (const m of ["rt", "da"] as Market[]) for (const fu of FUELS) {
      const col = `${fu}_${MARKETS[m].toLowerCase().replace(/[ -]/g, "_")}`;
      for (const y of hy.years) {
        const c = r.cells[m][fu][y];
        if (!c) { put("capture_hub_year", row, `${col}_${y}_price`, "", r.why[m][fu][y]); continue; }
        put("capture_hub_year", row, `${col}_${y}_price`, f(c.price, 4), c.whole ? "" : `${c.months} of 12 months counted: a partial year`);
        put("capture_hub_year", row, `${col}_${y}_flat`, f(c.flat, 4));
        put("capture_hub_year", row, `${col}_${y}_ratio_pct`, f(c.ratio, 2));
        put("capture_hub_year", row, `${col}_${y}_hours`, String(c.hours));
      }
      const t = r.twelve[m][fu];
      if (!t) put("capture_hub_year", row, `${col}_last_twelve_price`, "", r.whyTwelve[m][fu]);
      else { put("capture_hub_year", row, `${col}_last_twelve_price`, f(t.price, 4), `${t.from} to ${t.to}`); put("capture_hub_year", row, `${col}_last_twelve_flat`, f(t.flat, 4)); put("capture_hub_year", row, `${col}_last_twelve_hours`, String(t.hours)); }
    }
  }
  for (const b of hy.blank) put("capture_hub_year", b.name, "solar_real_time_price", "", b.words);
  // 4. the plant with a battery beside it
  if (fuel) {
    const sizes = `${x.mw} MW of ${plantName} and a ${bmw} MW, ${dur}-hour battery`;
    if (pair && hf) {
      put("battery_beside", "energy_at_day_ahead_prices", "plant_alone_usd", String(Math.round(pair.plant)), `${pairSpan}; ${sizes}. ${M.DA_PLANT}`);
      put("battery_beside", "energy_at_day_ahead_prices", "battery_alone_usd", String(Math.round(pair.battery)), M.DA_BATTERY);
      put("battery_beside", "energy_at_day_ahead_prices", "co_optimized_pair_usd", String(Math.round(pair.pair)), M.DA_PAIR);
      put("battery_beside", "energy_at_day_ahead_prices", "added_not_co_optimized_usd", String(Math.round(pair.added)), M.DA_ADDED);
      put("battery_beside", "energy_at_day_ahead_prices", "charging_from_the_plant_pct", M.fromPlant === null ? "" : String(M.fromPlant), M.fromPlant === null ? "The battery did not charge" : "");
      put("battery_beside", "energy_at_day_ahead_prices", "days_solved", String(hf.days), `${hf.left_out} of the twelve months' days left out, never filled`);
    } else {
      put("battery_beside", "energy_at_day_ahead_prices", "co_optimized_pair_usd", "", M.facts.batteryWhy);
    }
    if (batt) {
      put("battery_beside", "plant_at_real_time_prices_battery_with_ancillary", "plant_alone_usd", plantTotal === null ? "" : String(plantTotal), plantTotal === null ? `The ${plantName} plant's months are not all held over the battery's twelve months.` : `${batt.from} to ${batt.to}; this page's model at ${g.at} in real time`);
      put("battery_beside", "plant_at_real_time_prices_battery_with_ancillary", "battery_alone_usd", String(batt.total), `the figure of What a battery earns, energy and ancillary services, ${M.strat}`);
      put("battery_beside", "plant_at_real_time_prices_battery_with_ancillary", "added_not_co_optimized_usd", both === null ? "" : String(both), M.KEPT);
    } else {
      put("battery_beside", "plant_at_real_time_prices_battery_with_ancillary", "battery_alone_usd", "", M.battWhy);
    }
  } else {
    put("battery_beside", "energy_at_day_ahead_prices", "co_optimized_pair_usd", "", "A battery beside the plant is modeled for a solar or a wind plant.");
  }
  // 5. the stress days, for the reader's size
  if (st && st.length) {
    for (const e of st) {
      const row = EVENTS[e.event] ?? e.event;
      put("stress_days", row, "window", `${e.start} to ${e.end}`);
      put("stress_days", row, "days", String(e.days));
      put("stress_days", row, "per_day_usd", String(Math.round(e.windowMean)), `for ${sizeLabel}, on the local days of the event`);
      put("stress_days", row, "window_usd", String(Math.round(e.windowTotal)));
      put("stress_days", row, "normal_week_usd", String(Math.round(e.normalWeek)), "seven times the mean of the same event's baseline days: the same days or weekdays of earlier years");
      put("stress_days", row, "best_day_usd", String(Math.round(e.best.v)), e.best.day);
    }
  } else {
    put("stress_days", "none", "window_usd", "", `The stress days are ERCOT's: ${g.name}'s hub prices are held from after these events.`);
  }
  // 6. the fleet's hours as EIA reports them
  const si = snap.isos[iso];
  put("eia_hours", "hours_above_installed_nameplate", "solar", String(si.over_nameplate.solar ?? 0));
  put("eia_hours", "hours_above_installed_nameplate", "wind", String(si.over_nameplate.wind ?? 0));
  put("eia_hours", "hours_eia_reports_negative", "solar", String(si.negative.solar ?? 0));
  put("eia_hours", "hours_eia_reports_negative", "wind", String(si.negative.wind ?? 0));

  return csv(lines, `erw_generator_tables_${x.iso}_${x.asset}_${hub.id.replace(/[^A-Za-z0-9_.-]/g, "_")}.csv`);
}
