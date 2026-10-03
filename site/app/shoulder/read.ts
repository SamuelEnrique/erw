// Energy Research Warehouse (ERW) site, session 75: the shoulder page's read of Supabase, through lib/supabase.ts (the
// site's one reader): every row of shoulder_hours_monthly, about 20,500.
import "server-only";
import { DataError, HOURLY, rest } from "@/lib/supabase";
import { TABLE, type Row } from "@/lib/shoulder";

export async function shoulderRows(): Promise<Row[]> {
  const rows = await rest<Row>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${TABLE}`, order: "entity,variable,ts_utc" }, HOURLY, 30_000);
  if (rows.length === 0) throw new DataError(`${TABLE} returned no rows`);
  return rows.map((r) => ({ ...r, value: Number(r.value) }));
}
