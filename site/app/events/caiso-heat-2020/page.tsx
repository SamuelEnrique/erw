import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { EventStudy } from "@/components/EventStudy";
import { EventDecisions } from "../Decisions";
import { WholeCountrySection, type PageProps } from "../WholeCountry";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 39: the August 2020 heat wave in CAISO, event caiso_heat_2020 of event_window_daily (docs/methods/events.md).
// CAISO's prices for 2020 are not held, so the page has no price chart and says so.
export const metadata: Metadata = { title: "The August 2020 heat wave, CAISO" };
export const revalidate = 3600;

const EV = "caiso_heat_2020";
const RCA = "https://www.caiso.com/Documents/Final-Root-Cause-Analysis-Mid-August-2020-Extreme-Heat-Wave.pdf";
const E = "eia930:CISO";
// Session 10225 (chain 710, the events audit, finding 3): "Not on the outage days" compares each day's highest hour of
// demand served; the rotating outages came in the evening as solar fell, and the shed load is not in demand served.
// By California's demand less solar and wind (the region file), 14 August was the highest of 14 to 19 August
// (docs/reviews/events-model-audit-2026-11-26.md). Words only; no figure moves.
const OUTAGE_HOURS_WORDS = "Read it with care: the comparison is each day's highest hour of demand served against its own baseline days. On 14 and 15 August load was being shed, and demand served leaves that load out; and CAISO's notices put the Stage 3 emergencies at 18:36 to 20:38 on the 14th and 18:27 to 18:48 on the 15th (Pacific time), in the evening as solar output fell. So these figures do not show that the grid was less stretched on the outage days: demand less solar and wind, the measure of the evening hours the outages came in, is not on this page.";
// Session 10225 (chain 710, the events audit, finding 5): EIA's file holds no hydro for CAISO from 2019-10-01 21:00 UTC
// to 2020-08-24 17:00 UTC (impossible_hours.CISO_NO_HYDRO), and its net generation leaves it out too, so every day of
// this window divides CO2 by a net generation without hydro. The window's carbon intensity averages 281.32 kg/MWh
// against 204.95 (2018) and 184.98 (2019) on the baseline days, which hold hydro. The ERW's rule leaves those hours out
// and is held (docs/methods/impossible_hours.md); the page says so. Words only; no figure moves.
const HYDRO_GAP_WORDS = "The carbon intensity on this page is too high in the event's window: EIA's figures for CAISO hold no hydro from October 2019 to the morning of 24 August 2020, and its net generation leaves the hydro out too, so every day of the window divides the CO2 by a net generation without it, while the baseline days of 2018 and 2019 hold it. The warehouse's own rule for those hours leaves them out; it is held until a person approves it.";

export default function CaisoHeat2020({ searchParams }: PageProps = {}) {
  return (
    <Brand>
    <div>
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
          warehouse, so this page has no price chart. Days are Pacific time.{" "}
          <span data-hydro-gap="1">{HYDRO_GAP_WORDS}</span>
        </>
      }
      after={(rows) => {
        const inWin = (d: string) => d >= "2020-08-10" && d <= "2020-08-24";
        const hi = pickOf(rows, E, "demand_max_pct_vs_baseline", "max", inWin);
        const d14 = find(rows, E, "demand_max_pct_vs_baseline", "2020-08-14"), d15 = find(rows, E, "demand_max_pct_vs_baseline", "2020-08-15");
        return (
          <p>
            <strong>Not on the outage days.</strong> On 2020-08-14 and 15, the days of the rotating outages, the peak hour was <N r={d14} event={EV} u="%" /> and{" "}
            <N r={d15} event={EV} u="%" /> above the baseline; the highest came later, <N r={hi} event={EV} u="%" /> on {day(hi)}. The same report says &quot;August 17 through 19
            were projected to have much higher supply shortfalls&quot;, and that without a statewide mitigation effort and consumer conservation California was at
            risk of further rotating outages on those days (<a href={RCA}>CAISO, CPUC and CEC</a>). The warehouse holds no weather or supply data to say more.{" "}
            <span data-outage-hours="1">{OUTAGE_HOURS_WORDS}</span>
          </p>
        );
      }}
    />
    {/* session 47: the event study */}
    <EventStudy event="caiso_heat_2020" grids={["eia930:CISO"]} primary="eia930:CISO" />
    {/* session 7531: the page's decisions (Decisions.tsx), each with its default and source on hover */}
    {/* session 8410 (chain 503): EIA's thirteen regions across the event, from the data machine's file (WholeCountry.tsx) */}
    <WholeCountrySection event="caiso_heat_2020" path="/events/caiso-heat-2020" first="CAL" searchParams={searchParams}
      firstWhy="California is drawn first: the page above is about CAISO, which is among California's balancing authorities." />
    <EventDecisions event="caiso_heat_2020" />
    </div>
    </Brand>
  );
}
