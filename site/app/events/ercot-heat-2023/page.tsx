import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { EventStudy } from "@/components/EventStudy";
import { EventDecisions } from "../Decisions";
import { WholeCountrySection, type PageProps } from "../WholeCountry";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 39: the summer 2023 heat in ERCOT, event ercot_heat_2023 of event_window_daily (docs/methods/events.md), with
// ERCOT's hub prices (real-time and day-ahead, daily mean and max).
export const metadata: Metadata = { title: "The summer 2023 heat, ERCOT" };
export const revalidate = 3600;

const EV = "ercot_heat_2023";
const EEA = "https://www.ercot.com/news/release/2023-09-06-ercot-has-initiated";
const EXIT = "https://www.ercot.com/news/release/2023-09-06-ercot-has-exited";
const RECORDS = "https://www.ercot.com/news/release/09142023-ercot-provides-new";  // session 7531
const E = "eia930:ERCO", HUB = "ercot:HB_HUBAVG";
const inWin = (d: string) => d >= "2023-08-01" && d <= "2023-09-10";

export default function ErcotHeat2023({ searchParams }: PageProps = {}) {
  return (
    <Brand>
    <div>
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
          {/* session 7531 (fault 4 of docs/reviews/events-faults-2026-11-16.md): ERCOT's later release raised the September record twice
              inside this window, so the 82,705 MW of September 6 is named as what ERCOT announced that day, not as the month's record */}
          <p className="mb-2" data-ercot-records="2023-09-14">
            Eight days later ERCOT wrote that it &quot;set an all-time peak demand record of 85,464 MW on August 10, 2023&quot; and a September record of
            84,182 MW on September 8, &quot;surpassing the previous September peak of 83,911 MW&quot; set on September 7; it adds that the records are
            unofficial until settlement and that it counts &quot;the integrated system load for the full hour&quot; (<a href={RECORDS}>ERCOT, September 14, 2023</a>).
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
            the 82,705 MW ERCOT announced that evening as its September record; the highest hour of the window came on {day(top)}, <N r={top} event={EV} /> MW. The price
            tells the emergency: the highest 15-minute real-time price of the window was <N r={rt} event={EV} /> USD/MWh on {day(rt)}. ERCOT&apos;s release puts the
            cause in supply as well as demand: lower wind, and solar declining at sunset.
          </p>
        );
      }}
    />
    {/* session 47: the event study */}
    <EventStudy event="ercot_heat_2023" grids={["eia930:ERCO"]} primary="eia930:ERCO" price />
    {/* session 7531: the page's decisions (Decisions.tsx), each with its default and source on hover */}
    {/* session 8410 (chain 503): EIA's thirteen regions across the event, from the data machine's file (WholeCountry.tsx) */}
    <WholeCountrySection event="ercot_heat_2023" path="/events/ercot-heat-2023" first="TEX" searchParams={searchParams}
      firstWhy="Texas is drawn first: the page above is about ERCOT, which is among Texas's balancing authorities." />
    <EventDecisions event="ercot_heat_2023" />
    </div>
    </Brand>
  );
}
