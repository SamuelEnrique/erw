import type { Metadata } from "next";
import { AskErcotLink } from "@/components/AskErcotLink";
import { Related } from "@/components/Related";
import { Term } from "@/components/Term";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { headers, series, seriesVariables } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { Explorer, type Row } from "./Explorer";

export const revalidate = 3600;
export const metadata: Metadata = { title: "ERCOT peak premium" };

const ANNUAL = "ercot_peak_premium_annual";
const MONTHLY = "ercot_peak_premium_monthly";
const MONTHLY_VARS = ["peak_median", "midday_median", "overnight_median", "peak_iqr"];

export default async function PeakPremium() {
  const [annual, monthly, hdr] = await Promise.all([
    attempt(() => series(ANNUAL, {})),
    attempt(() => seriesVariables(MONTHLY, MONTHLY_VARS)),
    attempt(() => headers(ANNUAL)),
  ]);
  const compact = (rows: { entity: string; variable: string; ts_utc: string; value: number }[]): Row[] =>
    rows.map((r) => ({ e: r.entity, v: r.variable, t: r.ts_utc.slice(0, 7), x: r.value }));
  const lastInput = hdr.ok ? hdr.data.find((l) => l.startsWith("Last input interval:")) : undefined;

  return (
    <>
      <p className="text-sm">Explorer</p>
      <h1 className="mb-1 text-3xl">ERCOT peak premium</h1>
      <AskErcotLink context={{ view: "/explorer/ercot-peak-premium", title: "ERCOT peak premium", settings: { grid: "ERCOT", table: "ercot_peak_premium_annual" } }} />
      <p className="mb-2 max-w-3xl">
        How <Term t="ERCOT" first /> real-time prices spread across the day, for each hub and each year since 2015, from ERCOT&apos;s settlement point prices.
      </p>
      <p className="mb-2 max-w-3xl text-sm text-muted">
        By hub and year: the spread of the 16:00 to 21:00 peak block against midday and
        overnight, the tail of the distribution, and scarcity and negative-price intervals. Computed from every 15-minute settlement interval since
        2015, with no cap or exclusion. <Link href="/data/methods/ercot_peak_premium">Method</Link>.
      </p>
      {lastInput ? <p className="mb-6 text-xs text-muted">{lastInput}</p> : null}
      {!annual.ok ? (
        <NoData what={ANNUAL} reason={annual.reason} />
      ) : annual.data.length === 0 ? (
        <NoData what={ANNUAL} reason="the table returned no rows" />
      ) : (
        <Explorer
          annual={compact(annual.data)}
          monthly={monthly.ok ? compact(monthly.data) : []}
          monthlyError={monthly.ok ? (monthly.data.length ? null : "the table returned no rows") : monthly.reason}
          citeAnnual={<Cite tables={[ANNUAL]} note="Blocks by the local (America/Chicago) hour an interval starts: overnight 21:00 to 12:00, midday 12:00 to 16:00, peak 16:00 to 21:00" />}
          citeMonthly={<Cite tables={[MONTHLY]} note="Calendar months in America/Chicago" />}
        />
      )}
      <Related href="/explorer/ercot-peak-premium" />
    </>
  );
}
