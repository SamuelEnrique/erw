// Energy Research Warehouse (ERW) site, session 352: the server's read of price_years_by_window for one page's price
// point and configuration (lib/priceyears.ts says what the rows hold). A failed read offers no window: the page then
// shows its last twelve months, as before, and says the price years could not be read.
import "server-only";
import { attempt, HOURLY, rest } from "./supabase";
import { windowsOf, type PriceYear, type Row, type Tool } from "./priceyears";

export const PRICE_YEARS = "price_years_by_window";

export async function priceYears(tool: Tool, entity: string, config: string): Promise<{ ok: true; ws: PriceYear[] } | { ok: false; reason: string }> {
  const prefix = `${tool}_${config}_`;
  const r = await attempt(() => rest<Row>("series", {
    select: "entity,variable,ts_utc,value,unit,freq", table_name: `eq.${PRICE_YEARS}`, entity: `eq.${entity}`, variable: `like.${prefix}*`, order: "variable",
  }, HOURLY, 2_000));
  return r.ok ? { ok: true, ws: windowsOf(r.data, prefix) } : { ok: false, reason: r.reason };
}
