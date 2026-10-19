import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { EventStudy } from "@/components/EventStudy";
import { EventWindow, N, day, pickOf } from "../EventWindow";

// Session 319: the late January 2026 cold, event cold_2026 of event_window_daily (docs/methods/events.md, "Session 308":
// the data machine's window of 23 January to 2 February 2026, landed in session 308), built as the other eight are:
// the cold_2025 template (the six grids of the Elliott page, ERCOT's hub in full and the four hubs of the history
// table), the baseline the same weekdays 364 and 728 days earlier, and the charts through the shared components.
// Chosen from the data: the highest winter hour of demand served (EIA-930, November 2025 to March 2026) came on
// 2026-01-26 in ERCOT and SPP, 2026-01-25 in ISO-NE, 2026-01-27 in MISO and 2026-01-29 in PJM.
export const metadata: Metadata = { title: "The late January 2026 cold" };
export const revalidate = 3600;

const EV = "cold_2026";
const inWin = (d: string) => d >= "2026-01-23" && d <= "2026-02-02";

export default function Cold2026() {
  return (
    <Brand>
    <div>
    <EventWindow
      event={EV}
      title="The late January 2026 cold: six grids"
      crumb="The late January 2026 cold"
      start="2026-01-23"
      end="2026-02-02"
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
            In the winter of 2025 to 2026 (November to March in EIA&apos;s hourly data), five of the six grids served their highest winter hour of demand inside
            this window: ERCOT and SPP on 26 January 2026, ISO-NE on 25 January, MISO on 27 January and PJM on 29 January; NYISO&apos;s came on 7 February,
            outside it. The window opens on 23 January, when MISO&apos;s and SPP&apos;s demand rose, and closes on 2 February, PJM&apos;s and ERCOT&apos;s
            last high day. It was chosen from that data on the data machine (session 308), not from a news account, and it sets the demand served by the six
            grids, their peak hour each day and the carbon intensity of their generation against the same weekdays 364 and 728 days earlier.
          </p>
          <p>
            The prices are ERCOT&apos;s hub in full and the MISO, NYISO, ISO-NE and SPP hubs of the hub price history (session 64). PJM&apos;s prices are not
            public in the warehouse.
          </p>
        </>
      }
      caveat={
        <>
          Demand here is demand served. The baseline weeks (the same weekdays of late January 2025 and 2024) hold cold days of their own, the January 2025
          cold among them, so a small difference against the baseline is not a mild week. No weather is held for this event, so no estimate controls for
          temperature. The hubs have no baseline days.
        </>
      }
      after={(rows) => {
        const pjm = pickOf(rows, "eia930:PJM", "demand_max_mw", "max", inWin);
        const ercot = pickOf(rows, "eia930:ERCO", "demand_max_mw", "max", inWin);
        const hi = pickOf(rows, "eia930:PJM", "demand_max_pct_vs_baseline", "max", inWin);
        return (
          <p>
            PJM&apos;s highest hour of the window was <N r={pjm} event={EV} /> MW on {day(pjm)}, and ERCOT&apos;s <N r={ercot} event={EV} /> MW on {day(ercot)}. PJM&apos;s
            peak hour stood furthest above the baseline on {day(hi)}, <N r={hi} event={EV} />% above the mean of the same weekdays 364 and 728 days earlier.
          </p>
        );
      }}
    />
    {/* the event study, as for every event: demand and, where it has baseline days, ERCOT's hub price */}
    <EventStudy event="cold_2026" grids={["eia930:PJM", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:SWPP"]} primary="eia930:PJM" price />
    </div>
    </Brand>
  );
}
