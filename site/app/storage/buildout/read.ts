// Energy Research Warehouse (ERW) site, session 69: the storage build-out page's read of Supabase.
//
// Two reads of the series table through lib/supabase.ts, the site's one reader: the newest month
// storage_buildout_monthly holds, then the rows of the months the page shows (lib/buildout.ts monthsNeeded: every
// December, the newest month and the month twelve before), about 2,000 rows instead of the table's 21,000.
import "server-only";
import { DataError, HOURLY, rest } from "@/lib/supabase";
import { monthOf, monthsNeeded, TABLE, tsOf, type Row } from "@/lib/buildout";

export async function buildoutRows(): Promise<Row[]> {
  const top = await rest<{ ts_utc: string }>(
    "series",
    { select: "ts_utc", table_name: `eq.${TABLE}`, entity: "eq.us:total", variable: "eq.battery_operating_mw", order: "ts_utc.desc" },
    HOURLY,
    1,
  );
  if (top.length === 0) throw new DataError(`${TABLE} returned no rows`);
  const months = monthsNeeded(monthOf(top[0].ts_utc));
  return rest<Row>(
    "series",
    {
      select: "entity,variable,ts_utc,value",
      table_name: `eq.${TABLE}`,
      ts_utc: `in.(${months.map((m) => `"${tsOf(m)}"`).join(",")})`,
      order: "entity,variable,ts_utc",
    },
    HOURLY,
    20_000,
  );
}
