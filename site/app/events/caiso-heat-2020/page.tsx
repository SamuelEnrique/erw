import type { Metadata } from "next";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 39: the August 2020 heat wave in CAISO, event caiso_heat_2020 of event_window_daily (docs/methods/events.md).
// CAISO's prices for 2020 are not held, so the page has no price chart and says so.
export const metadata: Metadata = { title: "The August 2020 heat wave, CAISO" };
export const revalidate = 3600;

const EV = "caiso_heat_2020";
const RCA = "https://www.caiso.com/Documents/Final-Root-Cause-Analysis-Mid-August-2020-Extreme-Heat-Wave.pdf";
const E = "eia930:CISO";

export default function CaisoHeat2020() {
  return (
    <EventWindow
      event={EV}
      title="The August 2020 heat wave: CAISO"
      crumb="CAISO, August 2020"
      start="2020-08-10"
      end="2020-08-24"
      grids={[{ entity: E, name: "CAISO", slug: "caiso", tz: "Pacific time" }]}
      framing={
        <p>
          CAISO, the CPUC and the California Energy Commission wrote a Final Root Cause Analysis of &quot;the two rotating outages in the CAISO footprint on
          August 14 and 15, 2020&quot; (<a href={RCA}>CAISO, CPUC and CEC, January 13, 2021</a>). This page sets CAISO&apos;s demand served, its peak hour each day and
          the carbon intensity of its generation over 2020-08-10 to 2020-08-24 against the same weekdays 364 and 728 days earlier.
        </p>
      }
      caveat={
        <>
          Demand here is demand served: during the rotating outages, customers whose power was cut used nothing. CAISO&apos;s prices for 2020 are not in the
          warehouse, so this page has no price chart. Days are Pacific time.
        </>
      }
      after={(rows) => {
        const inWin = (d: string) => d >= "2020-08-10" && d <= "2020-08-24";
        const hi = pickOf(rows, E, "demand_max_pct_vs_baseline", "max", inWin);
        const d14 = find(rows, E, "demand_max_pct_vs_baseline", "2020-08-14"), d15 = find(rows, E, "demand_max_pct_vs_baseline", "2020-08-15");
        return (
          <p>
            <strong>Not on the outage days.</strong> On 2020-08-14 and 15, the days of the rotating outages, the peak hour was <N r={d14} event={EV} />% and{" "}
            <N r={d15} event={EV} />% above the baseline; the highest came later, <N r={hi} event={EV} />% on {day(hi)}. The same report says &quot;August 17 through 19
            were projected to have much higher supply shortfalls&quot;, and that without a statewide mitigation effort and consumer conservation California was at
            risk of further rotating outages on those days (<a href={RCA}>CAISO, CPUC and CEC</a>). The warehouse holds no weather or supply data to say more.
          </p>
        );
      }}
    />
  );
}
