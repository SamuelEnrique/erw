import type { Metadata } from "next";
import { EventStudy } from "@/components/EventStudy";
import { EventWindow, N, day, pickOf } from "../EventWindow";

// Session 64: the January 2025 cold, event cold_2025 of event_window_daily (docs/methods/events.md): PJM, MISO, SPP,
// NYISO, ISO-NE and ERCOT on the Elliott template, with ERCOT's hub prices and, from the second year of the hub history
// (iso_hub_prices_history, 2024-09-01 on), the MISO, NYISO, ISO-NE and SPP hubs. Chosen from the data: PJM, MISO, NYISO
// and ISO-NE had their highest winter hour of demand served of 2024-09 to 2025-08 on 2025-01-21 or 2025-01-22.
export const metadata: Metadata = { title: "The January 2025 cold" };
export const revalidate = 3600;

const EV = "cold_2025";
const inWin = (d: string) => d >= "2025-01-17" && d <= "2025-01-26";

export default function Cold2025() {
  return (
    <>
    <EventWindow
      event={EV}
      title="The January 2025 cold: six grids"
      crumb="The January 2025 cold"
      start="2025-01-17"
      end="2025-01-26"
      hub="ercot:HB_HUBAVG"
      hubs={[
        { entity: "miso:INDIANA.HUB", name: "MISO Indiana Hub", rtNote: "an hour" },
        { entity: "nyiso:N.Y.C.", name: "NYISO New York City", rtNote: "15 minutes, time-weighted" },
        { entity: "isone:.H.INTERNAL_HUB", name: "ISO-NE Internal Hub", rtNote: "15 minutes" },
        { entity: "spp:SPPNORTH_HUB", name: "SPP North Hub", rtNote: "15 minutes" },
      ]}
      grids={[
        { entity: "eia930:PJM", name: "PJM", slug: "pjm", tz: "Eastern time" },
        { entity: "eia930:MISO", name: "MISO", slug: "miso", tz: "Eastern Standard Time all year" },
        { entity: "eia930:SWPP", name: "SPP", slug: "spp", tz: "Central time" },
        { entity: "eia930:NYIS", name: "NYISO", slug: "nyiso", tz: "Eastern time" },
        { entity: "eia930:ISNE", name: "ISO-NE", slug: "isone", tz: "Eastern time" },
        { entity: "eia930:ERCO", name: "ERCOT", slug: "ercot", tz: "ERCOT operating days, Central time" },
      ]}
      framing={
        <>
          <p className="mb-2">
            In the year the warehouse&apos;s second year of hub prices covers (September 2024 to August 2025), PJM, MISO, NYISO and ISO-NE each served their highest
            winter hour of demand on January 21 or 22, 2025, in EIA&apos;s hourly data. This page was chosen from that data, not from a news account: it sets the demand
            served by the six grids of the Winter Storm Elliott page, their peak hour each day and the carbon intensity of their generation over 2025-01-17 to
            2025-01-26 against the same weekdays 364 and 728 days earlier.
          </p>
          <p>
            It is the first event in the warehouse with prices beyond ERCOT&apos;s: the MISO, NYISO, ISO-NE and SPP hubs, from the second year of the hub price history
            (session 64). PJM&apos;s prices are not public in the warehouse.
          </p>
        </>
      }
      caveat={
        <>
          Demand here is demand served. The baseline weeks (the same weekdays of January 2024 and January 2023) hold cold days of their own, so a small difference
          against the baseline is not a mild week. No weather is held for this event, so no estimate controls for temperature. The hubs have no baseline days.
        </>
      }
      after={(rows) => {
        const pjm = pickOf(rows, "eia930:PJM", "demand_max_mw", "max", inWin);
        const miso = pickOf(rows, "eia930:MISO", "demand_max_mw", "max", inWin);
        const hi = pickOf(rows, "eia930:PJM", "demand_max_pct_vs_baseline", "max", inWin);
        return (
          <p>
            PJM&apos;s highest hour of the window was <N r={pjm} event={EV} /> MW on {day(pjm)}, and MISO&apos;s <N r={miso} event={EV} /> MW on {day(miso)}. PJM&apos;s
            peak hour stood furthest above the baseline on {day(hi)}, <N r={hi} event={EV} />% above the mean of the same weekdays 364 and 728 days earlier.
          </p>
        );
      }}
    />
    {/* the event study, as for every event: demand and, where it has baseline days, ERCOT's hub price */}
    <EventStudy event="cold_2025" grids={["eia930:PJM", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:SWPP"]} primary="eia930:PJM" price />
    </>
  );
}
