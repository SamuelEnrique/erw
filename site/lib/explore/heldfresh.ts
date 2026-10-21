// Energy Research Warehouse (ERW) site, session 404: how old an explorer's tables are when a table is held for review.
// The shared reader (./fresh.ts) reads the public catalogue (lib/data.ts catalogue), which leaves out the rows the loader
// writes with in_live_set "review" (warehouse/supabase/live_set.yaml, review_hold): eia930_demand_growth is one, and
// iso_queue_statistics another. This reader reads the catalogue's rows of the tables named, held or not, for the
// explorers in review that draw them, and answers in the shared reader's form. Added beside ./fresh.ts, not in it, so
// the explorers built in parallel on the shared parts merge without touching one another's lines.
import "server-only";
import { attempt, HOURLY, rest } from "@/lib/supabase";
import type { Fresh } from "./fresh";

type Cat = { table_name: string; last_run: string | null; ts_max: string | null; interval: string | null; license: string; in_live_set: string | null };

/** As freshness() in ./fresh.ts, with a table held for review read too. `held` names the tables the catalogue holds
 *  for review, so the page can say so. A table not in the catalogue at all comes back with nulls. */
export async function freshnessHeld(tables: string[], now = Date.now()): Promise<{ ok: boolean; rows: Fresh[]; held: string[] }> {
  const cat = await attempt(() => rest<Cat>("catalogue", {
    select: "table_name,last_run,ts_max,interval,license,in_live_set", table_name: `in.(${tables.join(",")})`, order: "table_name",
  }, HOURLY));
  const by = new Map<string, Cat>(cat.ok ? cat.data.filter((r) => r.license === "public").map((r) => [r.table_name, r]) : []);
  return {
    ok: cat.ok,
    held: tables.filter((t) => by.get(t)?.in_live_set === "review"),
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
