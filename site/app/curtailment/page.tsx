import type { Metadata } from "next";
import { Related } from "@/components/Related";
import { Term } from "@/components/Term";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { Legend, StackedArea, type Layer } from "@/components/StackedArea";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { count, price } from "@/lib/format";
import { attempt } from "@/lib/supabase";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Curtailment" };

const MONTHLY = "iso_curtailment_monthly";
const D = 86_400_000;
const exact = (v: number) => (Number.isInteger(v) ? count(v) : price(v));
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const SOLAR = "var(--color-fuel-solar)", WIND = "var(--color-fuel-wind)";

type Iso = {
  key: string;
  label: string;
  entity: string;
  daily: string;
  // [variable, label, color] stacked in the charts
  parts: [string, string, string][];
  // the share of available output curtailed: numerator variables over denominator variables
  share?: { num: string[]; den: string[]; label: string };
  meaning: React.ReactNode;
};

const ISOS: Iso[] = [
  {
    key: "caiso",
    label: "CAISO",
    entity: "caiso:ISO",
    daily: "caiso_curtailment_daily",
    parts: [["curtailed_solar_mwh", "Solar curtailed", SOLAR], ["curtailed_wind_mwh", "Wind curtailed", WIND]],
    share: {
      num: ["curtailed_solar_mwh", "curtailed_wind_mwh"],
      den: ["curtailed_solar_mwh", "curtailed_wind_mwh", "solar_generation_mwh", "wind_generation_mwh"],
      label: "curtailed MWh over curtailed plus produced MWh (wind and solar)",
    },
    meaning: (
      <>
        CAISO&apos;s own figure: wind and solar output its market dispatch or operators cut, for local congestion or system-wide oversupply,
        including self-schedules cut. Output is the ISO&apos;s wind and solar production, which does not include the curtailed energy.
      </>
    ),
  },
  {
    key: "spp",
    label: "SPP",
    entity: "spp:SPP",
    daily: "spp_curtailment_daily",
    parts: [["curtailed_wind_mwh", "Wind curtailed", WIND], ["curtailed_solar_mwh", "Solar curtailed", SOLAR]],
    meaning: (
      <>
        SPP&apos;s own figure: wind and solar curtailed by redispatch (congestion), by manual operator instruction, and &quot;curtailed for
        energy&quot; (economic dispatch), for the SPP balancing authority area. SPP&apos;s western area (SWPW) is in the table as its own entity. The
        ERW holds no SPP wind and solar output for the same intervals, so no share is computed.
      </>
    ),
  },
  {
    key: "ercot",
    label: "ERCOT",
    entity: "ercot:system",
    daily: "ercot_wind_solar_hsl_daily",
    parts: [["solar_below_hsl_mwh", "Solar below HSL", SOLAR], ["wind_below_hsl_mwh", "Wind below HSL", WIND]],
    share: {
      num: ["solar_below_hsl_mwh", "wind_below_hsl_mwh"],
      den: ["solar_hsl_mwh", "wind_hsl_mwh"],
      label: "output below HSL over HSL (wind and solar)",
    },
    meaning: (
      <>
        ERCOT publishes no curtailment figure. This is the ERW&apos;s estimate: for each hour, how far system-wide wind and solar output fell
        below the High Sustained Limit (HSL) the resources reported, summed over the day. It includes curtailment and anything else that keeps
        output under the limit. The history starts in September 2026, when the ERW began reading ERCOT&apos;s reports, which it keeps for about a week.
      </>
    ),
  },
];

function sum(rows: SeriesRow[], vars: string[]) {
  return rows.filter((r) => vars.includes(r.variable)).reduce((a, r) => a + r.value, 0);
}

function IsoBlock({ c, monthly, daily }: { c: Iso; monthly: SeriesRow[]; daily: SeriesRow[] }) {
  const m = monthly.filter((r) => r.entity === c.entity);
  const d = daily.filter((r) => r.entity === c.entity);
  const months = Array.from(new Set(m.map((r) => r.ts_utc))).sort();
  const days = Array.from(new Set(d.map((r) => r.ts_utc))).sort();
  const vars = c.parts.map((p) => p[0]);
  // monthly and daily rows apart: a daily row on the 1st has the same variable and time as the month
  const byMonth = new Map(m.map((r) => [`${r.variable}|${r.ts_utc}`, r.value]));
  const byDay = new Map(d.map((r) => [`${r.variable}|${r.ts_utc}`, r.value]));
  const layer = (xs: string[], by: Map<string, number>): Layer[] =>
    c.parts.map(([v, label, color]) => ({ key: v, label, color, values: xs.map((t) => by.get(`${v}|${t}`) ?? null) }));
  const last13 = months.slice(-13).reverse();
  const shareOf = (rows: SeriesRow[]) => {
    if (!c.share) return null;
    const have = new Set(rows.map((r) => r.variable));
    if (!c.share.den.every((v) => have.has(v))) return null;
    const den = sum(rows, c.share.den);
    return den > 0 ? (100 * sum(rows, c.share.num)) / den : null;
  };
  const d0 = days.length ? Date.parse(days[Math.max(0, days.length - 90)]) : 0;
  const d1 = days.length ? Date.parse(days[days.length - 1]) + D : 0;
  const last90 = d.filter((r) => Date.parse(r.ts_utc) >= d0);
  return (
    <>
      <p className="mb-3 max-w-3xl text-sm">{c.meaning}</p>
      <Legend items={c.parts.map(([v, label, color]) => ({ key: v, label, color }))} />
      <h3 className="mt-4 text-base">Daily, the last {Math.min(90, days.length)} days</h3>
      {days.length >= 2 ? (
        <>
          <StackedArea
            x={days.slice(-90).map((t) => Date.parse(t))}
            layers={layer(days.slice(-90), byDay)}
            unit="MWh"
            height={180}
            ariaLabel={`${c.label} daily curtailment, ${days[Math.max(0, days.length - 90)].slice(0, 10)} to ${days[days.length - 1].slice(0, 10)}`}
            tick={(t) => new Date(t).toISOString().slice(5, 10)}
            ticks={days.slice(-90).filter((_, i, a) => i % Math.max(1, Math.round(a.length / 6)) === 0).map((t) => Date.parse(t))}
          />
          <p className="mt-2 text-sm">
            Total over these days:{" "}
            {c.parts.map(([v, label], i) => {
              const tot = sum(last90, [v]);
              return (
                <span key={v}>
                  {i > 0 ? "; " : ""}
                  {label.toLowerCase()}{" "}
                  <Num check={`series_esum|${c.daily}|${c.entity}|${v}|${iso(d0)}|${iso(d1)}`} raw={tot}>
                    {exact(tot)}
                  </Num>{" "}
                  MWh
                </span>
              );
            })}
            {(() => {
              const s = shareOf(last90);
              return s === null ? "" : `; ${s.toFixed(2)}% of available output`;
            })()}
            .
          </p>
          <Cite tables={[c.daily]} note="Days are the ISO's local operating days" />
        </>
      ) : (
        <NoData what={`${c.label}, daily`} reason={`${c.daily} holds ${days.length} day in the live set`} />
      )}
      <h3 className="mt-6 text-base">Monthly</h3>
      {months.length >= 2 ? (
        <>
          <StackedArea
            x={months.map((t) => Date.parse(t))}
            layers={layer(months, byMonth)}
            unit="MWh"
            height={200}
            ariaLabel={`${c.label} monthly curtailment, ${months[0].slice(0, 7)} to ${months[months.length - 1].slice(0, 7)}`}
            tick={(t) => String(new Date(t).getUTCFullYear())}
            ticks={months.filter((t) => t.slice(5, 7) === "01").map((t) => Date.parse(t))}
          />
          <Cite tables={[MONTHLY]} note="Complete months only; a month with a day missing from the daily table is not written" />
        </>
      ) : months.length === 1 ? null : (
        <NoData what={`${c.label}, monthly`} reason={`${MONTHLY} holds no complete month for ${c.entity} yet`} />
      )}
      {last13.length ? (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Month</th>
                {c.parts.map(([v, label]) => (
                  <th key={v} className="py-1 pr-3 text-right font-normal">
                    {label}, MWh
                  </th>
                ))}
                {c.share ? <th className="py-1 pr-3 text-right font-normal">Share of available output</th> : null}
              </tr>
            </thead>
            <tbody>
              {last13.map((t) => (
                <tr key={t} className="border-b border-rule/60">
                  <td className="py-1 pr-3">{t.slice(0, 7)}</td>
                  {vars.map((v) => (
                    <td key={v} className="py-1 pr-3 text-right tabular-nums">
                      {byMonth.has(`${v}|${t}`) ? (
                        <Num check={`series|${MONTHLY}|${c.entity}|${v}|${t}`} raw={byMonth.get(`${v}|${t}`)!}>
                          {exact(byMonth.get(`${v}|${t}`)!)}
                        </Num>
                      ) : (
                        ""
                      )}
                    </td>
                  ))}
                  {c.share ? (
                    <td className="py-1 pr-3 text-right tabular-nums">
                      {(() => {
                        const s = shareOf(m.filter((r) => r.ts_utc === t));
                        return s === null ? "not computable" : `${s.toFixed(2)}%`;
                      })()}
                    </td>
                  ) : null}
                </tr>
              ))}
            </tbody>
          </table>
          {c.share ? <p className="mt-1 text-xs text-muted">Share: {c.share.label}. &quot;Not computable&quot;: the month lacks the output figure.</p> : null}
          <Cite tables={[MONTHLY]} />
        </div>
      ) : null}
    </>
  );
}

export default async function CurtailmentPage() {
  const [monthly, ...dailies] = await Promise.all([
    attempt(() => series(MONTHLY, {})),
    ...ISOS.map((c) => attempt(() => series(c.daily, { since: daysAgo(100) }))),
  ]);
  return (
    <>
      <h1 className="mb-1 text-3xl">Curtailment</h1>
      <p className="mb-2 max-w-3xl">
        Wind and solar output that could have been produced and was not, daily and monthly, at <Term t="CAISO" first /> and <Term t="SPP" first /> since 2014 and at <Term t="ERCOT" first />
         since September 2026, from each <Term t="ISO" first />&apos;s own reports.
      </p>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        In MWh. Each ISO&apos;s figure means something
        different, and one ISO publishes none; read the note under each. <Link href="/data/methods/curtailment">Method</Link>.
      </p>
      {ISOS.map((c, i) => {
        const d = dailies[i];
        return (
          <Section key={c.key} title={c.label} id={c.key}>
            {!monthly.ok ? (
              <NoData what={MONTHLY} reason={monthly.reason} />
            ) : !d.ok ? (
              <NoData what={c.daily} reason={d.reason} />
            ) : (
              <IsoBlock c={c} monthly={monthly.data} daily={d.data} />
            )}
          </Section>
        );
      })}
      <Section title="MISO" id="miso">
        <p className="max-w-3xl text-sm">
          MISO publishes no wind or solar curtailment series. Its market reports list hourly wind output (&quot;Historical Hourly Wind
          Data&quot;) but no curtailed or dispatched-down energy (checked 2026-09-27, misoenergy.org market reports). MISO&apos;s independent market
          monitor reports curtailment once a year, in its State of the Market report, not as data.
        </p>
      </Section>
      <Section title="NYISO, ISO-NE and PJM" id="others">
        <p className="max-w-3xl text-sm">
          Not in the ERW. Session 18 looked for curtailment data from CAISO, ERCOT, SPP and MISO only; whether these three publish a curtailment
          series has not been checked.
        </p>
      </Section>
      <Related href="/curtailment" />
    </>
  );
}
