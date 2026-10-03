import type { Metadata } from "next";
import { EventStudy } from "@/components/EventStudy";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 36C: the Historical Event Analyzer's second event, COVID-19 in spring 2020. Every number is a row of
// event_window_daily, event covid_2020 (derived: docs/methods/events.md): each grid's local days 2020-03-01 to
// 2020-05-31 against the same weekday of 2019 (364 days earlier; the 728-day baseline of 2018 is not held). The page
// picks rows (the lowest week) and draws them; it computes no value.
export const metadata: Metadata = { title: "COVID-19: demand in the seven ISO grids, spring 2020" };
export const revalidate = 3600;

const T = "event_window_daily";
const EV = "covid_2020";
const METHOD = "/data/methods/events";
const CA_URL = "https://www.gov.ca.gov/2020/03/19/governor-gavin-newsom-issues-stay-at-home-order/";
const AFTER = "2020-03-22"; // the first whole week (Sunday to Saturday) after California's order of 2020-03-19
// The eight grids, in the categorical slots of tokens.css; the lower 48 in the accent, the highlighted series.
const GRIDS = [
  { entity: "eia930:CISO", name: "CAISO", slug: "caiso", color: "var(--color-fuel-gas)", tz: "Pacific time" },
  { entity: "eia930:ERCO", name: "ERCOT", slug: "ercot", color: "var(--color-fuel-coal)", tz: "ERCOT operating days, Central time" },
  { entity: "eia930:ISNE", name: "ISO-NE", slug: "isone", color: "var(--color-fuel-nuclear)", tz: "Eastern time" },
  { entity: "eia930:MISO", name: "MISO", slug: "miso", color: "var(--color-fuel-wind)", tz: "Eastern Standard Time all year" },
  { entity: "eia930:NYIS", name: "NYISO", slug: "nyiso", color: "var(--color-fuel-solar)", tz: "Eastern time" },
  { entity: "eia930:PJM", name: "PJM", slug: "pjm", color: "var(--color-fuel-hydro)", tz: "Eastern time" },
  { entity: "eia930:SWPP", name: "SPP", slug: "spp", color: "var(--color-fuel-storage)", tz: "Central time" },
  { entity: "eia930:US48", name: "Lower 48", slug: "", color: "accent", tz: "Eastern time" },
];

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

const N = ({ r }: { r?: SeriesRow }) =>
  r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}|${EV}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;
const day = (r?: SeriesRow) => (r ? r.ts_utc.slice(0, 10) : "");
const sec = (ts: string) => Date.parse(`${ts.slice(0, 10)}T00:00:00Z`) / 1000;

function points(rows: SeriesRow[], entity: string, keep: (ts: string) => boolean, shiftDays = 0) {
  return rows
    .filter((r) => r.entity === entity && keep(r.ts_utc))
    .sort((a, b) => a.ts_utc.localeCompare(b.ts_utc))
    .map((r) => ({ t: sec(r.ts_utc) + shiftDays * 86_400, v: r.value }));
}

function lowest(rows: SeriesRow[], entity: string, from = ""): SeriesRow | undefined {
  const xs = rows.filter((r) => r.entity === entity && r.ts_utc.slice(0, 10) >= from);
  return xs.length ? xs.reduce((a, b) => (b.value < a.value ? b : a)) : undefined;
}

export default async function Covid() {
  const got = await attempt(async () => {
    const [weeks, demand, prices] = await Promise.all([
      series(T, { event: EV, variable: "demand_pct_vs_baseline_week" }),
      series(T, { event: EV, variable: "demand_mwh" }),
      series(T, { event: EV, entity: "ercot:HB_HUBAVG" }),
    ]);
    return { weeks, demand, prices };
  });
  const d = got.ok ? got.data : { weeks: [], demand: [], prices: [] };
  const in2020 = (ts: string) => ts.startsWith("2020");
  const in2019 = (ts: string) => ts.startsWith("2019");
  const weekly: Line[] = GRIDS.map((g) => ({ label: g.name, color: g.color, points: points(d.weeks, g.entity, () => true) }));
  const price = (variable: string, keep: (ts: string) => boolean, shift: number) => points(d.prices.filter((r) => r.variable === variable), "ercot:HB_HUBAVG", keep, shift);
  return (
    <>
      <p className="mb-1 text-xs text-muted"><Link href="/events">Events</Link> / COVID-19, spring 2020</p>
      <h1 className="mb-1 text-3xl">COVID-19: demand in the seven ISO grids, spring 2020</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <p className="mb-2">
          On 2020-03-19 California&apos;s Governor &quot;issued a stay at home order to protect the health and well-being of all Californians&quot;
          (<a href={CA_URL}>Office of the Governor of California</a>; Executive Order N-33-20).
          This page sets the electricity demand that each of the seven ISO grids, and the lower 48 states, served each day from 2020-03-01 to
          2020-05-31 against the same weekday of 2019, 364 days earlier.
        </p>
        <p className="text-muted">
          The baseline is one year, 2019: the method also asks for 2018 (728 days earlier), and EIA&apos;s hourly files the warehouse holds start in
          July 2018. So 2019&apos;s weather is in every comparison, and the warehouse holds no weather to separate it from the pandemic. Demand here is
          demand served. Easter falls on different weeks (2019-04-21, 2020-04-12). <Link href={METHOD}>Method</Link>.
        </p>
      </div>
      {!got.ok || !d.weeks.length ? (
        <NoData what="the event window" reason={got.ok ? `${T} returned no rows for ${EV}` : got.reason} />
      ) : (
        <>
          <Section title="Weekly demand against the same weeks of 2019, all grids" aside={<Tier />}>
            <LineChart lines={weekly} unit="% vs 2019" height={300} ariaLabel="Weekly demand served against the same weekdays of 2019, in percent, for CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP and the lower 48, weeks starting 2020-03-01 to 2020-05-24" />
            <p className="mt-1 text-sm text-muted">
              Each point is a week, Sunday to Saturday, dated by its Sunday: the week&apos;s demand served over the demand of the same seven weekdays of
              2019, minus one, in percent. A week with a missing day, in either year, has no point.
            </p>
            <Cite tables={[T]} note="EIA-930 hourly demand per balancing authority, summed over each grid's local days; variable demand_pct_vs_baseline_week" />
          </Section>

          <Section title="Each grid: daily demand served, 2020 and the same weekday of 2019" aside={<Tier />}>
            <p className="mb-3 max-w-3xl text-sm text-muted">
              Under each grid, its deepest weekly drop against 2019. Where that week comes before the week of {AFTER}, the first whole week after
              California&apos;s order, the line also gives the deepest week from then on: a drop before any order is not the pandemic&apos;s, and the
              warehouse holds no weather to say what it was.
            </p>
            <div className="grid gap-6 md:grid-cols-2">
              {GRIDS.map((g) => {
                const deep = lowest(d.weeks, g.entity);
                const deepAfter = lowest(d.weeks, g.entity, AFTER);
                return (
                  <div key={g.entity}>
                    <h3 className="mb-1 text-base">{g.slug ? <Link href={`/grid/${g.slug}`}>{g.name}</Link> : g.name}</h3>
                    <LineChart
                      lines={[
                        { label: "2020", color: "accent", points: points(d.demand, g.entity, in2020) },
                        { label: "2019, same weekday", color: "muted", points: points(d.demand, g.entity, in2019, 364) },
                      ]}
                      unit="MWh"
                      height={180}
                      ariaLabel={`${g.name} demand served per day, 2020-03-01 to 2020-05-31, and the same weekday of 2019`}
                    />
                    <p className="mt-1 text-sm">
                      Deepest weekly drop against 2019: <N r={deep} />% in the week of {day(deep)}
                      {deep && deepAfter && day(deep) !== day(deepAfter) ? (
                        <>; from the week of {AFTER} on, <N r={deepAfter} />% in the week of {day(deepAfter)}</>
                      ) : null}
                      .
                    </p>
                    <p className="text-xs text-muted">Days: {g.tz}.</p>
                  </div>
                );
              })}
            </div>
            <Cite tables={[T]} note="EIA-930 hourly demand per balancing authority, summed per local day (demand_mwh); 2019's days are drawn 364 days later, on the 2020 weekday they are compared with" />
          </Section>

          <Section title="Price context: ERCOT hub average" aside={<Tier />}>
            <LineChart
              lines={[
                { label: "Real-time, 2020", color: "accent", points: price("rt_mean", in2020, 0) },
                { label: "Day-ahead, 2020", color: "var(--color-fuel-gas)", points: price("da_mean", in2020, 0) },
                { label: "Real-time, 2019, same weekday", color: "muted", points: price("rt_mean", in2019, 364) },
              ]}
              unit="USD/MWh"
              height={240}
              ariaLabel="ERCOT hub average daily mean real-time and day-ahead price, 2020-03-01 to 2020-05-31, and real-time on the same weekday of 2019"
            />
            <Cite tables={[T]} note="Daily means of ERCOT's 15-minute real-time and hourly day-ahead settlement point prices at the hub average (HB_HUBAVG), from ercot_all_hub_prices_history" />
          </Section>
        </>
      )}
      {/* session 47: the event study */}
      <EventStudy event="covid_2020" grids={["eia930:US48", "eia930:CISO", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:PJM", "eia930:SWPP"]} primary="eia930:US48" price />
    </>
  );
}
