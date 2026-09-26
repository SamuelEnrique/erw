import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { MARKETS, daysAgo, latestPrices, series, type SeriesRow } from "@/lib/data";
import { count, node, price, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";

export const revalidate = 3600;

// no paths at build time: each hub or zone page renders on its first request and is then cached
export function generateStaticParams() {
  return [];
}

function decode(s: string): string {
  try {
    return decodeURIComponent(s);
  } catch {
    return s;
  }
}

export async function generateMetadata({ params }: PageProps<"/prices/[entity]">): Promise<Metadata> {
  const { entity } = await params;
  return { title: `${node(decode(entity))} prices` };
}

function stats(rows: SeriesRow[]) {
  if (rows.length === 0) return null;
  const v = rows.map((r) => r.value);
  return { n: v.length, min: Math.min(...v), max: Math.max(...v), mean: v.reduce((a, b) => a + b, 0) / v.length, first: rows[0].ts_utc, last: rows.at(-1)!.ts_utc };
}

export default async function EntityPrices({ params }: PageProps<"/prices/[entity]">) {
  const entity = decode((await params).entity);
  const m = MARKETS.find((x) => x.main.split(":")[0] === entity.split(":")[0]);
  if (!m || !/^[a-z]+:[\w .\-]+$/.test(entity)) notFound();

  const since = daysAgo(30);
  const [rt, da, latest] = await Promise.all([
    m.rt ? attempt(() => series(m.rt!.table, { entity, variable: m.rt!.variable, since })) : Promise.resolve(null),
    attempt(() => series(m.da.table, { entity, variable: m.da.variable, since })),
    attempt(latestPrices),
  ]);
  const rtRows = rt && rt.ok ? rt.data : [];
  const daRows = da.ok ? da.data : [];
  if (rt?.ok && da.ok && rtRows.length === 0 && daRows.length === 0) notFound();

  const toLine = (rows: SeriesRow[]) => rows.map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value }));
  const lines: Line[] = [];
  if (daRows.length) lines.push({ label: `Day-ahead (${m.da.variable})`, points: toLine(daRows), color: "muted", step: true });
  if (rtRows.length) lines.push({ label: `Real time (${m.rt!.variable})`, points: toLine(rtRows), color: "accent" });
  const lp = latest.ok ? latest.data.find((r) => r.entity === entity) : undefined;
  const summary = [
    { name: "Real time", src: m.rt, s: stats(rtRows) },
    { name: "Day-ahead", src: m.da, s: stats(daRows) },
  ];

  return (
    <>
      <p className="text-sm">
        <Link href="/prices">Prices</Link> / {m.iso}
      </p>
      <h1 className="mb-1 font-mono text-2xl">{node(entity)}</h1>
      <p className="mb-5 text-sm text-muted">
        {m.iso}, entity <code className="font-mono">{entity}</code>, last 30 days. Times in UTC.
      </p>

      {lp ? (
        <p className="mb-4 text-sm">
          Latest real-time interval:{" "}
          <Num check={`latest_prices|${lp.entity}|${lp.variable}`} raw={lp.value} className="text-lg tabular-nums">
            {price(lp.value)}
          </Num>{" "}
          {lp.unit}, starting {utc(lp.ts_utc)} <span className="font-mono text-xs text-muted">({lp.variable})</span>
        </p>
      ) : null}

      {lines.length ? (
        <LineChart lines={lines} unit="USD/MWh" ariaLabel={`${entity} real-time and day-ahead prices, last 30 days`} />
      ) : null}
      {!m.rt ? <NoData what="real time" reason={`the ERW has no ${m.iso} real-time series table (only the latest interval in latest_prices)`} /> : null}
      {rt && !rt.ok ? <NoData what="real time" reason={rt.reason} /> : null}
      {!da.ok ? <NoData what="day-ahead" reason={da.reason} /> : null}
      <Cite tables={[...(m.rt ? [m.rt.table] : []), m.da.table]} note="Real time is the accent line, day-ahead the stepped grey line" />

      <div className="mt-6 overflow-x-auto">
        <table className="border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-4 font-normal">Market</th>
              <th className="py-1 pr-4 font-normal">Table</th>
              <th className="py-1 pr-4 text-right font-normal">Intervals</th>
              <th className="py-1 pr-4 text-right font-normal">Min</th>
              <th className="py-1 pr-4 text-right font-normal">Mean</th>
              <th className="py-1 pr-4 text-right font-normal">Max</th>
              <th className="py-1 pr-4 font-normal">From</th>
              <th className="py-1 pr-4 font-normal">To</th>
            </tr>
          </thead>
          <tbody>
            {summary.map(({ name, src, s }) => (
              <tr key={name} className="border-b border-rule/60">
                <td className="py-1 pr-4">{name}</td>
                <td className="py-1 pr-4 font-mono text-xs">{src ? src.table : ""}</td>
                {s ? (
                  <>
                    <td className="py-1 pr-4 text-right tabular-nums">{count(s.n)}</td>
                    <td className="py-1 pr-4 text-right tabular-nums">{price(s.min)}</td>
                    <td className="py-1 pr-4 text-right tabular-nums">{price(s.mean)}</td>
                    <td className="py-1 pr-4 text-right tabular-nums">{price(s.max)}</td>
                    <td className="py-1 pr-4 text-xs">{utc(s.first)}</td>
                    <td className="py-1 pr-4 text-xs">{utc(s.last)}</td>
                  </>
                ) : (
                  <td colSpan={6} className="py-1 pr-4 text-xs text-muted">
                    no data: {src ? `no rows in ${src.table} for this entity in the last 30 days` : "no real-time series table for this ISO"}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-1 text-xs text-muted">Min, mean and max of every interval in the window, USD/MWh, computed on this page from the rows charted above.</p>
      </div>
    </>
  );
}
