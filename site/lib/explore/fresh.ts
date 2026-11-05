// Energy Research Warehouse (ERW) site, session 403: how old an explorer's tables are, from the catalogue (lib/explore).
import "server-only";
import { catalogue, type CatalogueRow } from "@/lib/data";
import { attempt } from "@/lib/supabase";

export type Fresh = { table: string; lastRun: string | null; tsMax: string | null; interval: string | null; days: number | null };

/** How old each table is, from the catalogue's last run and newest timestamp (coverage.csv, loaded with the live set).
 *  `days` is whole days from the last run to `now`. A table the catalogue does not list comes back with nulls. */
export async function freshness(tables: string[], now = Date.now()): Promise<{ ok: boolean; rows: Fresh[] }> {
  const cat = await attempt(catalogue);
  const by = new Map<string, CatalogueRow>(cat.ok ? cat.data.map((r) => [r.table_name, r]) : []);
  return {
    ok: cat.ok,
    rows: tables.map((t) => {
      const r = by.get(t);
      const lastRun = r?.last_run ?? null;
      return {
        table: t,
        lastRun,
        tsMax: r?.ts_max ?? null,
        interval: r?.interval ?? null,
        days: lastRun ? Math.floor((now - new Date(lastRun).getTime()) / 86_400_000) : null,
      };
    }),
  };
}
