import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { EventStudy } from "@/components/EventStudy";
import { gridNotices } from "@/lib/reliability";
import { attempt } from "@/lib/supabase";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 58: the September 2022 heat wave in CAISO, event caiso_heat_2022 of event_window_daily (docs/methods/events.md,
// docs/methods/california_reliability.md), on the template of the August 2020 page: CAISO's demand served, its peak hour
// and the carbon intensity of its generation against the same weekdays 364 and 728 days earlier, the weather at
// Sacramento and Los Angeles (noaa_isd_hourly, SAC and LAX), the event-study estimates with and without temperature,
// and CAISO's own notices of those days (caiso_grid_emergencies).
export const metadata: Metadata = { title: "The September 2022 heat wave, CAISO" };
export const revalidate = 3600;

const EV = "caiso_heat_2022";
const E = "eia930:CISO";
const START = "2022-08-31", END = "2022-09-09";
const GEHR = "https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf";
const NAMES: Record<string, string> = {
  flex_alert: "Flex Alert", rmo: "Restricted Maintenance Operations", eea_watch: "EEA Watch", eea1: "Energy Emergency Alert 1", eea2: "Energy Emergency Alert 2",
  eea3: "Energy Emergency Alert 3", transmission_emergency: "Transmission Emergency",
};

export default async function CaisoHeat2022() {
  const got = await attempt(() => gridNotices(START, END));
  const notices = got.ok ? got.data : [];
  const byDay = new Map<string, string[]>();
  for (const n of notices) byDay.set(n.event_date.slice(0, 10), [...new Set([...(byDay.get(n.event_date.slice(0, 10)) ?? []), n.event_type])]);
  return (
    <>
      <EventWindow
        event={EV}
        title="The September 2022 heat wave: CAISO"
        crumb="CAISO, September 2022"
        start={START}
        end={END}
        grids={[{ entity: E, name: "CAISO", slug: "caiso", tz: "Pacific time" }]}
        framing={
          <p>
            Ten days of heat across the West, 2022-08-31 to 2022-09-09. CAISO called Flex Alerts, asking Californians to conserve, and on one evening
            declared its highest emergency, an Energy Emergency Alert 3 (<a href={GEHR}>California ISO, Grid Emergencies History Report</a>). This page sets CAISO&apos;s
            demand served, its peak hour each day and the carbon intensity of its generation against the same weekdays 364 and 728 days earlier, with
            the temperature at Sacramento and Los Angeles.
          </p>
        }
        caveat={
          <>
            Demand here is demand served (EIA-930, CAISO&apos;s balancing authority). CAISO&apos;s prices for 2022 are not in the warehouse, so this page has no
            price chart. Days are Pacific time.
          </>
        }
        after={(rows) => {
          const inWin = (d: string) => d >= START && d <= END;
          const hi = pickOf(rows, E, "demand_max_mw", "max", inWin);
          const hiPct = pickOf(rows, E, "demand_max_pct_vs_baseline", "max", inWin);
          const d6 = find(rows, E, "demand_max_pct_vs_baseline", "2022-09-06");
          return (
            <p>
              <strong>The peak.</strong> CAISO&apos;s highest hour of demand served in the window was <N r={hi} event={EV} /> MW on {day(hi)}; against the baseline,
              the peak hour rose most on {day(hiPct)}, <N r={hiPct} event={EV} />% above it, and on 2022-09-06 it was <N r={d6} event={EV} />% above.
            </p>
          );
        }}
      />
      {/* session 58: CAISO's own notices of the window's days (caiso_grid_emergencies), each day with its types */}
      <section className="mb-10">
        <div className="mb-3 border-b border-rule pb-1"><h2 className="text-xl">CAISO&apos;s notices, day by day</h2></div>
        {notices.length ? (
          <ul className="max-w-3xl text-sm">
            {[...byDay.entries()].sort().map(([d, ts]) => (
              <li key={d}><span className="font-mono">{d}</span>: {ts.map((t) => NAMES[t] ?? t).join(", ")}</li>
            ))}
          </ul>
        ) : <p className="text-sm text-muted">The notices of these days could not be read{got.ok ? "" : `: ${got.reason}`}.</p>}
        <p className="mt-2 max-w-3xl text-xs text-muted">
          From the warehouse&apos;s <code className="font-mono">caiso_grid_emergencies</code>, read from the <a href={GEHR}>California ISO, Grid Emergencies History
          Report</a>. Every notice since 1998: <Link href="/grid/caiso#reliability">CAISO&apos;s grid page, Reliability</Link>.
        </p>
      </section>
      <EventStudy event={EV} grids={[E]} primary={E} />
    </>
  );
}
