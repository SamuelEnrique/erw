import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { shown, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { CaisoBreakNote } from "@/components/CaisoBreakNote";  // session 73

// Session 32 (Part B): carbon intensity per ISO, two blocks only: the latest hour per ISO, ranked, and the last 24
// hours as one chart. Every number is a value of carbon_intensity_hourly (derived from EIA's CO2 estimates,
// eia930_all_emissions, over EIA-930 generation and demand); the page computes nothing.
// Session 34: one more block, the monthly intensity since 2018-07 per ISO (carbon_intensity_monthly). Since session 34
// the denominators are the workbooks' own Demand and Net generation, so every table reaches back to 2018.
export const metadata: Metadata = { title: "Emissions" };
import { carbonLeftOut, carbonLeftOutMonths, monthRuns, CARBON_HYDRO_GAP } from "@/lib/carbonLeftOut";  // session 118

export const revalidate = 3600;

const T = "carbon_intensity_hourly";
const TM = "carbon_intensity_monthly"; // session 34
const METHOD = "/data/methods/emissions";
// session 118: EIA's CO2 estimates often run more than three days behind the clock. With a three-day window the two
// "now" sections said "no row in the last 3 days" while the table held hours four days old; the page looks back a week
const LOOK_BACK_DAYS = 7;
const ISOS = [
  { entity: "eia930:CISO", label: "CAISO", color: "var(--color-fuel-solar)" },
  { entity: "eia930:ERCO", label: "ERCOT", color: "accent" },
  { entity: "eia930:ISNE", label: "ISO-NE", color: "var(--color-fuel-gas)" },
  { entity: "eia930:MISO", label: "MISO", color: "var(--color-fuel-hydro)" },
  { entity: "eia930:NYIS", label: "NYISO", color: "var(--color-fuel-storage)" },
  { entity: "eia930:PJM", label: "PJM", color: "ink" },
  { entity: "eia930:SWPP", label: "SPP", color: "var(--color-fuel-coal)" },
];

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

const N = (r?: SeriesRow) =>
  r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;

function Monthly({ rows }: { rows: SeriesRow[] }) {
  // session 118: a month computed on an impossible hour, and California's months without hydro, are not shown
  // (lib/carbonLeftOut.ts): the table behind this page is held as it is until a person approves the rebuilt one
  const of = (e: string) => rows.filter((r) => r.entity === e && r.variable === "intensity_generation" && !carbonLeftOut(r.entity, r.variable, r.ts_utc)).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const out = carbonLeftOutMonths("intensity_generation");
  const lines: Line[] = ISOS.map((i) => ({ label: i.label, color: i.color, points: of(i.entity).map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })) }));
  return (
    <>
      <LineChart lines={lines} unit="kg CO2/MWh" height={280} ariaLabel="Carbon intensity of generation per ISO, monthly since 2018" />
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm tabular-nums">
        {ISOS.map((i) => {
          const first = of(i.entity)[0];
          const last = of(i.entity).at(-1);
          return last && first ? (
            <span key={i.entity}>
              {i.label}: <Num check={`series|${TM}|${first.entity}|${first.variable}|${first.ts_utc}`} raw={first.value}>{shown(first.value)}</Num>{" "}
              <span className="text-[11px] text-muted">({first.ts_utc.slice(0, 7)})</span> to{" "}
              <Num check={`series|${TM}|${last.entity}|${last.variable}|${last.ts_utc}`} raw={last.value}>{shown(last.value)}</Num>{" "}
              <span className="text-[11px] text-muted">({last.ts_utc.slice(0, 7)})</span>
            </span>
          ) : null;
        })}
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Intensity of generation, kg CO2/MWh: each month&apos;s CO2 over its net generation, for UTC months whose every day is
        complete; a month with a missing day is left out, so a line can have gaps. The first and the latest complete month
        per ISO are given in figures.
      </p>
      {out.length ? (
        <p className="mt-2 max-w-3xl border-l-2 border-accent bg-paper px-3 py-1.5 text-xs" data-carbon-left-out={out.length}>
          <strong>Left out of this chart: {out.length} months the table still holds.</strong>{" "}
          {ISOS.filter((i) => out.some((m) => m.entity === i.entity)).map((i, k, a) => (
            <span key={i.entity}>
              {i.label}: {monthRuns(out.filter((m) => m.entity === i.entity).map((m) => m.month))}
              {k < a.length - 1 ? "; " : ". "}
            </span>
          ))}
          California&apos;s months from October 2019 to July 2020 are computed on a file with no hydro in it ({CARBON_HYDRO_GAP.hours.toLocaleString("en-US")} hours
          in a row, so the intensity reads high); the others hold an hour of net generation that did not happen, and
          a month&apos;s CO2 over such an hour is not that month&apos;s intensity. Nothing is corrected or filled: the months are not drawn. <Link href="/data/faults">Known data faults</Link>;{" "}
          <Link href="/data/methods/impossible_hours">the rule</Link>.
        </p>
      ) : null}
    </>
  );
}

export default async function Emissions() {
  const [got, monthly] = await Promise.all([
    attempt(() => series(T, { since: daysAgo(LOOK_BACK_DAYS) })),
    attempt(() => series(TM, { variable: "intensity_generation" })),
  ]);
  const rows = got.ok ? got.data : [];
  const of = (e: string, v: string) => rows.filter((r) => r.entity === e && r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const latest = ISOS.map((i) => {
    const g = of(i.entity, "intensity_generation").at(-1);
    const d = g ? of(i.entity, "intensity_demand").find((r) => r.ts_utc === g.ts_utc) : undefined;
    return { ...i, g, d };
  })
    .filter((x) => x.g)
    .sort((a, b) => a.g!.value - b.g!.value);
  const newest = rows.length ? Math.max(...rows.map((r) => new Date(r.ts_utc).getTime())) : 0;
  const lines: Line[] = ISOS.map((i) => ({
    label: i.label,
    color: i.color,
    points: of(i.entity, "intensity_generation")
      .filter((r) => new Date(r.ts_utc).getTime() > newest - 24 * 3_600_000)
      .map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })),
  }));
  return (
    <>
      <h1 className="mb-1 text-3xl">Emissions</h1>
      <CaisoBreakNote />
      <p className="mb-5 max-w-3xl text-sm text-muted">
        How much CO2 each ISO&apos;s power carries, from EIA&apos;s hourly CO2 estimates for EIA-930. <Link href={METHOD}>Method</Link>.
      </p>

      <Section title="Carbon intensity now, ranked" aside={<Tier />}>
        {!got.ok ? (
          <NoData what="carbon intensity" reason={got.reason} />
        ) : latest.length === 0 ? (
          <NoData what="carbon intensity" reason={`${T} has no row in the last ${LOOK_BACK_DAYS} days`} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[460px] text-sm tabular-nums">
              <thead>
                <tr className="border-b border-rule text-left text-[11px] text-muted">
                  <th className="py-0.5 font-normal">ISO, lowest first</th>
                  <th className="pr-2 font-normal">Latest hour (start, UTC)</th>
                  <th className="pr-2 text-right font-normal">Of generation, kg CO2/MWh</th>
                  <th className="pr-2 text-right font-normal">Of demand, kg CO2/MWh</th>
                </tr>
              </thead>
              <tbody>
                {latest.map((x, i) => (
                  <tr key={x.entity} className="border-b border-rule">
                    <td className="py-0.5 pr-2">
                      <span className="text-muted">{i + 1}.</span> {x.label}
                    </td>
                    <td className="pr-2 text-xs text-muted">{utc(x.g!.ts_utc)}</td>
                    <td className="pr-2 text-right font-semibold">{N(x.g)}</td>
                    <td className="pr-2 text-right">{N(x.d)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-1 text-[11px] text-muted">
              Of generation: the CO2 EIA estimates for the power made in the ISO, over its net generation. Of demand: the CO2 of
              the power used there, imports counted and exports taken out, over its demand; the two differ by trade. EIA
              publishes generation a day or more late, so the latest hour is not the current one.
            </p>
          </div>
        )}
        <Cite tables={[T]} note="Derived from eia930_all_emissions (EIA's CO2 estimates) over the Demand and Net generation columns of the same EIA workbooks" />
      </Section>

      <Section title="The last 24 hours" aside={<Tier />}>
        {got.ok && newest ? (
          <LineChart lines={lines} unit="kg CO2/MWh" height={260} ariaLabel="Carbon intensity of generation per ISO, the last 24 hours" />
        ) : (
          <NoData what="the last 24 hours" reason={got.ok ? `${T} has no row in the last ${LOOK_BACK_DAYS} days` : got.reason} />
        )}
        <Cite tables={[T]} note={newest ? `Intensity of generation, hourly, the 24 hours to ${utc(new Date(newest).toISOString())} (hour start)` : undefined} />
      </Section>

      <Section title="Monthly since 2018" aside={<Tier />}>
        {monthly.ok && monthly.data.length ? (
          <Monthly rows={monthly.data} />
        ) : (
          <NoData what="the monthly intensity" reason={monthly.ok ? `${TM} returned no rows` : monthly.reason} />
        )}
        <Cite tables={[TM]} note="Derived from eia930_all_emissions over the Demand and Net generation columns of the same EIA workbooks, from 2018-07, when EIA's CO2 estimates start" />
      </Section>
    </>
  );
}
