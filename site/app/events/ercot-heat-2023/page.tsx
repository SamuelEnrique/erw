import type { Metadata } from "next";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 39: the summer 2023 heat in ERCOT, event ercot_heat_2023 of event_window_daily (docs/methods/events.md), with
// ERCOT's hub prices (real-time and day-ahead, daily mean and max).
export const metadata: Metadata = { title: "The summer 2023 heat, ERCOT" };
export const revalidate = 3600;

const EV = "ercot_heat_2023";
const EEA = "https://www.ercot.com/news/release/2023-09-06-ercot-has-initiated";
const EXIT = "https://www.ercot.com/news/release/2023-09-06-ercot-has-exited";
const E = "eia930:ERCO", HUB = "ercot:HB_HUBAVG";
const inWin = (d: string) => d >= "2023-08-01" && d <= "2023-09-10";

export default function ErcotHeat2023() {
  return (
    <EventWindow
      event={EV}
      title="The summer 2023 heat: ERCOT"
      crumb="ERCOT, summer 2023"
      start="2023-08-01"
      end="2023-09-10"
      hub={HUB}
      grids={[{ entity: E, name: "ERCOT", slug: "ercot", tz: "ERCOT operating days, Central time" }]}
      framing={
        <>
          <p className="mb-2">
            On September 6, 2023 ERCOT issued an Energy Emergency Alert Level 2 (<a href={EEA}>ERCOT</a>); that evening it exited emergency operations, and
            wrote that &quot;No power outages associated with the ERCOT power grid were necessary&quot; and that &quot;Texas set a new September peak demand record today of
            82,705 MW driven by extreme heat across the state&quot; (<a href={EXIT}>ERCOT</a>). ERCOT&apos;s chief executive named the cause: &quot;High demand, lower wind
            generation, and the declining solar generation during sunset led to lower operating reserves on the grid&quot;.
          </p>
          <p>
            This page sets ERCOT&apos;s demand served, its peak hour each day, the carbon intensity of its generation and its hub prices over 2023-08-01 to
            2023-09-10 against the same weekdays 364 and 728 days earlier.
          </p>
        </>
      }
      caveat={<>Demand here is demand served, from EIA&apos;s hourly data, which need not equal ERCOT&apos;s own peak figures. Days are ERCOT operating days (Central time).</>}
      after={(rows) => {
        const d6 = find(rows, E, "demand_max_mw", "2023-09-06");
        const top = pickOf(rows, E, "demand_max_mw", "max", inWin);
        const rt = pickOf(rows, HUB, "rt_max", "max", inWin);
        return (
          <p>
            <strong>The emergency did not come on the day of the highest demand.</strong> On 2023-09-06 EIA&apos;s highest hour was <N r={d6} event={EV} /> MW, beside
            ERCOT&apos;s September record of 82,705 MW; the highest hour of the window came on {day(top)}, <N r={top} event={EV} /> MW. The price
            tells the emergency: the highest 15-minute real-time price of the window was <N r={rt} event={EV} /> USD/MWh on {day(rt)}. ERCOT&apos;s release puts the
            cause in supply as well as demand: lower wind, and solar declining at sunset.
          </p>
        );
      }}
    />
  );
}
