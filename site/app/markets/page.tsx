import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { count, price } from "@/lib/format";
import { attempt } from "@/lib/supabase";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Markets" };

const TOP = "iso_rt_top_intervals";
const D = 86_400_000;
const ISOS = [
  { key: "ercot", label: "ERCOT", tz: "America/Chicago" },
  { key: "caiso", label: "CAISO", tz: "America/Los_Angeles" },
  { key: "nyiso", label: "NYISO", tz: "America/New_York" },
  { key: "miso", label: "MISO", tz: "EST" },
  { key: "spp", label: "SPP", tz: "America/Chicago" },
  { key: "isone", label: "ISO-NE", tz: "America/New_York" },
];
const exact = (v: number) => (Number.isInteger(v) ? count(v) : price(v));
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
// the hub or zone: the entity after its ISO prefix (ercot:HB_NORTH gives HB_NORTH)
const hubOf = (entity: string) => entity.slice(entity.indexOf(":") + 1);
const signed = (v: number) => `${v >= 0.005 ? "+" : v <= -0.005 ? "−" : ""}${price(Math.abs(v))}`;

// the weekly means shown, each with the change on the week before
const MEANS: { v: string; label: string }[] = [
  { v: "da_mean_usd", label: "Day-ahead" },
  { v: "da_onpeak_mean_usd", label: "On-peak DA" },
  { v: "da_offpeak_mean_usd", label: "Off-peak DA" },
  { v: "da_rt_spread_mean_usd", label: "RT minus DA" },
  { v: "implied_heat_rate", label: "Heat rate" },
];

function IsoBlock({ table, rows, top, tz }: { table: string; rows: SeriesRow[]; top: SeriesRow[]; tz: string }) {
  const days = Array.from(new Set(rows.map((r) => r.ts_utc))).sort((a, b) => Date.parse(a) - Date.parse(b));
  if (days.length < 7) return <NoData what={table} reason={`${table} holds ${days.length} days in the live set; a week needs 7`} />;
  const week = days.slice(-7), prev = days.slice(-14, -7);
  const hubs = Array.from(new Set(rows.map((r) => hubOf(r.entity)))).sort();
  const byKey = new Map(rows.map((r) => [`${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`, r.value]));
  const entityOf = new Map(rows.map((r) => [hubOf(r.entity), r.entity]));
  // a week's mean needs the metric on all 7 days; on-peak needs every weekday that is not a holiday, so it averages the days it has
  const wmean = (e: string, v: string, ds: string[]) => {
    const vals = ds.map((d) => byKey.get(`${e}|${v}|${Date.parse(d)}`)).filter((x): x is number => x !== undefined);
    const need = v === "da_onpeak_mean_usd" ? 1 : ds.length;
    return vals.length >= need && ds.length === 7 ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
  };
  const wlist = (e: string, v: string) => week.map((d) => byKey.get(`${e}|${v}|${Date.parse(d)}`));
  const w0 = Date.parse(week[0]), w1 = Date.parse(week[6]) + D;
  const last = week[6];
  return (
    <>
      <p className="mb-2 text-xs text-muted">
        This week: the operating days {week[0].slice(0, 10)} to {last.slice(0, 10)} ({tz}); change on {prev.length === 7 ? `${prev[0].slice(0, 10)} to ${prev[6].slice(0, 10)}` : "the week before (not all in the live set)"}.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3 font-normal">Hub or zone</th>
              <th className="py-1 pr-3 text-right font-normal">DA, {last.slice(5, 10)}</th>
              {MEANS.map((m) => (
                <th key={m.v} className="py-1 pr-3 text-right font-normal">
                  {m.label} (week, change)
                </th>
              ))}
              <th className="py-1 pr-3 text-right font-normal">Largest RT minus DA</th>
              <th className="py-1 pr-3 text-right font-normal">Hours RT &gt; DA + 50</th>
              <th className="py-1 pr-3 text-right font-normal">30-day volatility</th>
            </tr>
          </thead>
          <tbody>
            {hubs.map((h) => {
              const e = entityOf.get(h)!;
              const lastDa = byKey.get(`${e}|da_mean_usd|${Date.parse(last)}`);
              const mx = wlist(e, "da_rt_spread_max_usd");
              const hrs = wlist(e, "hours_rt_over_da_50");
              const vols = days.map((d) => ({ d, v: byKey.get(`${e}|da_volatility_30d_usd|${Date.parse(d)}`) })).filter((x) => x.v !== undefined);
              const vol = vols.at(-1);
              return (
                <tr key={h} className="border-b border-rule/60">
                  <td className="py-1 pr-3 font-mono text-xs">{h}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">
                    {lastDa !== undefined ? (
                      <Num check={`series|${table}|${e}|da_mean_usd|${iso(Date.parse(last))}`} raw={lastDa}>
                        {exact(lastDa)}
                      </Num>
                    ) : (
                      "no data"
                    )}
                  </td>
                  {MEANS.map((m) => {
                    const a = wmean(e, m.v, week), b = wmean(e, m.v, prev);
                    return (
                      <td key={m.v} className="py-1 pr-3 text-right tabular-nums">
                        {a === null ? (m.v.startsWith("da_rt") && !rows.some((r) => r.variable === m.v) ? "no RT table" : "no data") : price(a)}
                        {a !== null && b !== null ? <span className="text-xs text-muted"> ({signed(a - b)})</span> : null}
                      </td>
                    );
                  })}
                  <td className="py-1 pr-3 text-right tabular-nums">
                    {mx.every((x) => x !== undefined) ? price(Math.max(...(mx as number[]))) : rows.some((r) => r.variable === "da_rt_spread_max_usd") ? "no data" : "no RT table"}
                  </td>
                  <td className="py-1 pr-3 text-right tabular-nums">
                    {hrs.every((x) => x !== undefined) ? (
                      <Num check={`series_esum|${table}|${e}|hours_rt_over_da_50|${iso(w0)}|${iso(w1)}`} raw={(hrs as number[]).reduce((a, b) => a + b, 0)}>
                        {count((hrs as number[]).reduce((a, b) => a + b, 0))}
                      </Num>
                    ) : rows.some((r) => r.variable === "hours_rt_over_da_50") ? (
                      "no data"
                    ) : (
                      "no RT table"
                    )}
                  </td>
                  <td className="py-1 pr-3 text-right tabular-nums">
                    {vol ? (
                      <>
                        <Num check={`series|${table}|${e}|da_volatility_30d_usd|${iso(Date.parse(vol.d))}`} raw={vol.v!}>
                          {exact(vol.v!)}
                        </Num>
                        <span className="text-xs text-muted"> ({vol.d.slice(5, 10)})</span>
                      </>
                    ) : (
                      "needs 31 days"
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs text-muted">
        USD/MWh, except the heat rate (MMBtu/MWh: the day-ahead average over Henry Hub) and the hours. A week&apos;s mean needs the metric on all 7 days,
        except on-peak, which weekends and NERC holidays do not have. Volatility: the standard deviation of the 30 day-over-day changes in the daily
        day-ahead average, as of the day in brackets.
      </p>
      <Cite tables={[table]} />
      <h3 className="mt-5 text-base">Top 10 real-time intervals of the week</h3>
      {top.length ? (
        <>
          <ol className="mt-1 grid gap-x-8 text-sm sm:grid-cols-2">
            {top
              .slice()
              .sort((a, b) => b.value - a.value || Date.parse(a.ts_utc) - Date.parse(b.ts_utc))
              .map((r) => (
                <li key={`${r.entity}${r.ts_utc}`} className="flex justify-between border-b border-rule/60 py-0.5">
                  <span className="font-mono text-xs">
                    {hubOf(r.entity)}{" "}
                    {new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(r.ts_utc))}
                  </span>
                  <span className="tabular-nums">
                    <Num check={`series|${TOP}|${r.entity}|rt_price_top10_week|${iso(Date.parse(r.ts_utc))}`} raw={r.value}>
                      {exact(r.value)}
                    </Num>
                  </span>
                </li>
              ))}
          </ol>
          <Cite tables={[TOP]} note="Interval start in the ISO's local time; USD/MWh. The ISO's latest 7 local days with every real-time interval" />
        </>
      ) : (
        <NoData what="top intervals" reason={`${TOP} holds no row for this ISO (no real-time table, or no 7 complete days)`} />
      )}
    </>
  );
}

export default async function MarketsPage() {
  const results = await Promise.all(
    ISOS.map(async (i) => {
      const table = `${i.key}_trader_daily`;
      return { i, table, r: await attempt(() => series(table, { since: daysAgo(20) })) };
    }),
  );
  const top = await attempt(() => series(TOP, {}));
  return (
    <>
      <h1 className="mb-1 text-3xl">Markets</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Day-ahead against real-time, by hub: the week&apos;s averages and their change on the week before, on-peak and off-peak day-ahead prices,
        the implied heat rate against Henry Hub, how often real-time ran more than 50 USD/MWh above day-ahead, 30-day volatility, and the
        highest real-time intervals. PJM is absent: the ERW has no licensed PJM price data. SPP has day-ahead only. <Link href="/data/methods/trader_view">Method</Link>.
      </p>
      {results.map(({ i, table, r }) => (
        <Section key={i.key} title={i.label} id={i.key}>
          {!r.ok ? (
            <NoData what={table} reason={r.reason} />
          ) : (
            <IsoBlock table={table} rows={r.data} top={top.ok ? top.data.filter((x) => x.entity.startsWith(`${i.key}:`)) : []} tz={i.tz} />
          )}
        </Section>
      ))}
    </>
  );
}
