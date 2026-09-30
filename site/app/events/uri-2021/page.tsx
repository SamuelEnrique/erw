import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 36B: Historical Event Analyzer v0, Winter Storm Uri in ERCOT. Every number is a row of event_window_daily
// (derived: docs/methods/events.md), which holds ERCOT's operating days 2021-02-07 to 2021-02-24 and the same calendar
// days of 2019 and 2020. The page picks rows (the highest, the lowest) and draws them; it computes no value.
export const metadata: Metadata = { title: "Winter Storm Uri, ERCOT, February 2021" };
export const revalidate = 3600;

const T = "event_window_daily";
const METHOD = "/data/methods/events";
const EIA_URL = "https://www.eia.gov/todayinenergy/detail.php?id=46836";
const YEARS = [
  { y: "2021", label: "2021 (Uri)", color: "accent" },
  { y: "2020", label: "2020", color: "var(--color-fuel-gas)" },
  { y: "2019", label: "2019", color: "muted" },
];

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

const N = ({ r }: { r?: SeriesRow }) =>
  r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;
const day = (r?: SeriesRow) => (r ? r.ts_utc.slice(0, 10) : "");

/** The three years of one variable on the 2021 calendar, so the days line up. */
function lines(rows: SeriesRow[], variable: string): Line[] {
  return YEARS.map(({ y, label, color }) => ({
    label,
    color,
    points: rows
      .filter((r) => r.variable === variable && r.ts_utc.startsWith(y))
      .sort((a, b) => a.ts_utc.localeCompare(b.ts_utc))
      .map((r) => ({ t: Date.parse(`2021${r.ts_utc.slice(4)}`) / 1000, v: r.value })),
  }));
}

function pick(rows: SeriesRow[], variable: string, years: string[], how: "max" | "min"): SeriesRow | undefined {
  const xs = rows.filter((r) => r.variable === variable && years.includes(r.ts_utc.slice(0, 4)));
  if (!xs.length) return undefined;
  return xs.reduce((a, b) => (how === "max" ? (b.value > a.value ? b : a) : b.value < a.value ? b : a));
}

export default async function Uri() {
  const got = await attempt(() => series(T, {}));
  const rows = got.ok ? got.data : [];
  const ev = ["2021"], base = ["2019", "2020"];
  const rtPeak = pick(rows, "rt_max", ev, "max"), rtBase = pick(rows, "rt_max", base, "max");
  const lowDemand = pick(rows, "demand_min_mw", ev, "min");
  const low15 = rows.find((r) => r.variable === "demand_min_mw" && r.ts_utc.slice(0, 10) === "2021-02-15");
  const fall = pick(rows, "net_generation_mwh_day_change", ev, "min");
  const short = pick(rows, "net_generation_mwh_vs_baseline", ev, "min");
  const ciPeak = pick(rows, "intensity_generation", ev, "max");
  const chart = (variable: string, unit: string, aria: string) => <LineChart lines={lines(rows, variable)} unit={unit} height={240} x="minute" ariaLabel={aria} />;
  return (
    <>
      <p className="mb-1 text-xs text-muted"><Link href="/events">Events</Link> / Winter Storm Uri</p>
      <h1 className="mb-1 text-3xl">Winter Storm Uri: ERCOT, February 2021</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <p className="mb-2">
          In February 2021 extreme winter weather disrupted energy supply and demand, particularly in Texas, and ERCOT began implementing rotating
          outages at midnight on February 15 (<a href={EIA_URL}>EIA, Today in Energy</a>). This page sets ERCOT&apos;s prices, the demand it served, its
          net generation and the carbon intensity of that generation over the operating days 2021-02-07 to 2021-02-24 against the same calendar days
          of 2019 and 2020.
        </p>
        <p className="text-muted">
          Demand here is demand served. During the rotating outages, customers whose power was cut used nothing, so demand served is less than what
          Texans would have used. Days are ERCOT operating days (Central time). <Link href={METHOD}>Method</Link>.
        </p>
      </div>
      {!got.ok || !rows.length ? (
        <NoData what="the event window" reason={got.ok ? `${T} returned no rows` : got.reason} />
      ) : (
        <>
          <Section title="Price: ERCOT hub average, real-time" aside={<Tier />}>
            {chart("rt_mean", "USD/MWh", "ERCOT hub average real-time price, daily mean, February 7 to 24 of 2019, 2020 and 2021")}
            <p className="mt-1 text-sm">
              Highest 15-minute real-time price: <N r={rtPeak} /> USD/MWh on {day(rtPeak)}; the highest on the same days of 2019 and 2020 was{" "}
              <N r={rtBase} /> USD/MWh ({day(rtBase)}).
            </p>
            <Cite tables={[T]} note="Daily mean of ERCOT's 15-minute real-time settlement point price at the hub average (HB_HUBAVG), from ercot_all_hub_prices_history" />
          </Section>

          <Section title="Demand served" aside={<Tier />}>
            {chart("demand_mwh", "MWh", "ERCOT demand served per day, February 7 to 24 of 2019, 2020 and 2021")}
            <p className="mt-1 text-sm">
              Lowest hour of demand served in the window: <N r={lowDemand} /> MW on {day(lowDemand)}, after the storm. On 2021-02-15, the
              first day of rotating outages, the lowest hour was <N r={low15} /> MW.
            </p>
            <Cite tables={[T]} note="EIA-930 hourly demand of ERCO, summed per operating day; demand served, not what customers wanted" />
          </Section>

          <Section title="Net generation" aside={<Tier />}>
            {chart("net_generation_mwh", "MWh", "ERCOT net generation per day, February 7 to 24 of 2019, 2020 and 2021")}
            <p className="mt-1 text-sm">
              Largest day-to-day fall: <N r={fall} /> MWh on {day(fall)}. Largest shortfall against the 2019 and 2020 average for the same day:{" "}
              <N r={short} /> MWh on {day(short)}, after the storm; during the outages net generation stayed above that average.
            </p>
            <Cite tables={[T]} note="EIA-930 hourly net generation of ERCO, summed per operating day; the fall is the day minus the day before, the shortfall the day minus the mean of 2019 and 2020" />
          </Section>

          <Section title="Carbon intensity of generation" aside={<Tier />}>
            {chart("intensity_generation", "kg CO2/MWh", "ERCOT carbon intensity of generation per day, February 7 to 24 of 2019, 2020 and 2021")}
            <p className="mt-1 text-sm">
              Highest daily carbon intensity in 2021&apos;s window: <N r={ciPeak} /> kg CO2 per MWh generated, on {day(ciPeak)}.
            </p>
            <Cite tables={[T]} note="EIA's CO2 estimates for ERCO (eia930_all_emissions) over its net generation, per operating day" />
          </Section>
        </>
      )}
    </>
  );
}
