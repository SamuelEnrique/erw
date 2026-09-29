import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { shown, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 32 (Part B): carbon intensity per ISO, two blocks only: the latest hour per ISO, ranked, and the last 24
// hours as one chart. Every number is a value of carbon_intensity_hourly (derived from EIA's CO2 estimates,
// eia930_all_emissions, over EIA-930 generation and demand); the page computes nothing.
export const metadata: Metadata = { title: "Emissions" };
export const revalidate = 3600;

const T = "carbon_intensity_hourly";
const METHOD = "/data/methods/emissions";
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

export default async function Emissions() {
  const got = await attempt(() => series(T, { since: daysAgo(3) }));
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
      <p className="mb-5 max-w-3xl text-sm text-muted">
        How much CO2 each ISO&apos;s power carries, from EIA&apos;s hourly CO2 estimates for EIA-930. <Link href={METHOD}>Method</Link>.
      </p>

      <Section title="Carbon intensity now, ranked" aside={<Tier />}>
        {!got.ok ? (
          <NoData what="carbon intensity" reason={got.reason} />
        ) : latest.length === 0 ? (
          <NoData what="carbon intensity" reason={`${T} has no row in the last 3 days`} />
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
        <Cite tables={[T]} note="Derived from eia930_all_emissions (EIA's CO2 estimates), eia930_all_generation and eia930_all_demand" />
      </Section>

      <Section title="The last 24 hours" aside={<Tier />}>
        {got.ok && newest ? (
          <LineChart lines={lines} unit="kg CO2/MWh" height={260} ariaLabel="Carbon intensity of generation per ISO, the last 24 hours" />
        ) : (
          <NoData what="the last 24 hours" reason={got.ok ? `${T} has no row in the last 3 days` : got.reason} />
        )}
        <Cite tables={[T]} note={newest ? `Intensity of generation, hourly, the 24 hours to ${utc(new Date(newest).toISOString())} (hour start)` : undefined} />
      </Section>
    </>
  );
}
