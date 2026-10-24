// Energy Research Warehouse (ERW) site, session 1174 (chain 078): the read of ERCOT's grid notices for the Grid tool,
// every row of ercot_grid_notices (events, about 180 rows; in the live set under review_hold since session 322), read
// once per render of a page (React's cache, as lib/reliability.ts reads CAISO's: session 1160). ERCOT's Mix tab asks
// for them three times (the state line, the scarcity strip, the monthly mix); one request reaches the database. Only
// the three fields of extra the rules read are asked for (not x_text, ERCOT's words, which no panel draws). The rules
// over the rows are lib/ercotNotices.ts (no import, so scripts/check-values.mjs can load it); this file is apart so that
// the Clean tab, which draws lib/reliability.ts, does not read ERCOT's notices.
import { cache } from "react";
import { NOTICE_TABLE } from "@/lib/ercotNotices";
import { HOURLY, rest } from "@/lib/supabase";

export type ErcotNotice = { event_id: string; event_date: string; event_type: string; extra: Record<string, string> };
type Row = { event_id: string; event_date: string; event_type: string; x_counts: string | null; x_region: string | null; retrieved_at: string | null };

/** ERCOT's notices, oldest first, with extra's x_counts, x_region and retrieved_at. */
export const ercotNotices = cache(async (): Promise<ErcotNotice[]> => {
  const rows = await rest<Row>("events", {
    select: "event_id,event_date,event_type,x_counts:extra->>x_counts,x_region:extra->>x_region,retrieved_at:extra->>retrieved_at",
    table_name: `eq.${NOTICE_TABLE}`, order: "event_date,event_id",
  }, HOURLY, 20_000);
  return rows.map((r) => ({ event_id: r.event_id, event_date: r.event_date, event_type: r.event_type,
    extra: { x_counts: r.x_counts ?? "", x_region: r.x_region ?? "", retrieved_at: r.retrieved_at ?? "" } }));
});
