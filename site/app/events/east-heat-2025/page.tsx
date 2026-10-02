import type { Metadata } from "next";
import { EventStudy } from "@/components/EventStudy";
import { EventWindow, N, day, pickOf } from "../EventWindow";

// Session 64: the June 2025 heat, event east_heat_2025 of event_window_daily (docs/methods/events.md): PJM, NYISO, ISO-NE
// and MISO, with the NYISO, ISO-NE and MISO hubs from the second year of the hub history (iso_hub_prices_history). Chosen
// from the data: PJM, NYISO and ISO-NE had their highest hour of demand served of 2024-09 to 2025-08 on 2025-06-23 or
// 2025-06-24. The warehouse's first eastern summer event.
export const metadata: Metadata = { title: "The June 2025 heat" };
export const revalidate = 3600;

const EV = "east_heat_2025";
const inWin = (d: string) => d >= "2025-06-20" && d <= "2025-06-28";

export default function EastHeat2025() {
  return (
    <>
    <EventWindow
      event={EV}
      title="The June 2025 heat: four eastern grids"
      crumb="The June 2025 heat"
      start="2025-06-20"
      end="2025-06-28"
      hubs={[
        { entity: "nyiso:N.Y.C.", name: "NYISO New York City", rtNote: "15 minutes, time-weighted" },
        { entity: "isone:.H.INTERNAL_HUB", name: "ISO-NE Internal Hub", rtNote: "15 minutes" },
        { entity: "miso:INDIANA.HUB", name: "MISO Indiana Hub", rtNote: "an hour" },
      ]}
      grids={[
        { entity: "eia930:PJM", name: "PJM", slug: "pjm", tz: "Eastern time" },
        { entity: "eia930:NYIS", name: "NYISO", slug: "nyiso", tz: "Eastern time" },
        { entity: "eia930:ISNE", name: "ISO-NE", slug: "isone", tz: "Eastern time" },
        { entity: "eia930:MISO", name: "MISO", slug: "miso", tz: "Eastern Standard Time all year" },
      ]}
      framing={
        <>
          <p className="mb-2">
            PJM, NYISO and ISO-NE each served their highest hour of demand of September 2024 to August 2025 on June 23 or 24, 2025, in EIA&apos;s hourly data. This
            page was chosen from that data, not from a news account: it sets the demand served by four eastern grids, their peak hour each day and the carbon
            intensity of their generation over 2025-06-20 to 2025-06-28 against the same weekdays 364 and 728 days earlier.
          </p>
          <p>
            The warehouse&apos;s other heat events are in California and Texas; this is its first in the East, and its prices come from the second year of the hub price
            history (session 64). PJM&apos;s prices are not public in the warehouse.
          </p>
        </>
      }
      caveat={
        <>
          Demand here is demand served. The baseline days (the same weekdays of June 2024 and June 2023) are summer days with heat of their own. No weather is held for
          this event, so no estimate controls for temperature. The hubs have no baseline days.
        </>
      }
      after={(rows) => {
        const pjm = pickOf(rows, "eia930:PJM", "demand_max_mw", "max", inWin);
        const ny = pickOf(rows, "eia930:NYIS", "demand_max_pct_vs_baseline", "max", inWin);
        const ne = pickOf(rows, "eia930:ISNE", "demand_max_pct_vs_baseline", "max", inWin);
        return (
          <p>
            PJM&apos;s highest hour of the window was <N r={pjm} event={EV} /> MW on {day(pjm)}. Against the baseline, NYISO&apos;s peak hour stood highest on {day(ny)},{" "}
            <N r={ny} event={EV} />% above it, and ISO-NE&apos;s on {day(ne)}, <N r={ne} event={EV} />%.
          </p>
        );
      }}
    />
    <EventStudy event="east_heat_2025" grids={["eia930:PJM", "eia930:NYIS", "eia930:ISNE", "eia930:MISO"]} primary="eia930:PJM" />
    </>
  );
}
