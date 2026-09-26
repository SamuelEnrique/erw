import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { MARKETS, daysAgo, latestPrices, renderTime, series, type SeriesRow } from "@/lib/data";
import { node, price, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";

export const revalidate = 900;
export const metadata: Metadata = { title: "Prices" };

/** The day-ahead row whose hour contains `now`, if the table has it. */
function daNow(rows: SeriesRow[], now: number): SeriesRow | null {
  for (const r of rows) {
    const t = new Date(r.ts_utc).getTime();
    if (t <= now && now < t + 3_600_000) return r;
  }
  return null;
}

export default async function Prices() {
  const now = renderTime();
  const latest = await attempt(latestPrices);
  const since = daysAgo(1, now);
  const da = await Promise.all(MARKETS.map(async (m) => ({ m, rows: await attempt(() => series(m.da.table, { variable: m.da.variable, since })) })));

  return (
    <>
      <h1 className="mb-1 text-3xl">Power prices</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Every public ISO hub and zone in the ERW: the newest real-time interval, and the day-ahead price for the current hour. Select a hub or zone for its
        last 30 days. PJM prices are licensed for internal use and are not shown.
      </p>
      {!latest.ok ? <NoData what="real-time prices" reason={latest.reason} /> : null}
      {da.map(({ m, rows }) => {
        const prefix = m.main.split(":")[0] + ":";
        const ents = latest.ok ? latest.data.filter((r) => r.entity.startsWith(prefix)) : [];
        const daRows = rows.ok ? rows.data : [];
        const entities = Array.from(new Set([...ents.map((e) => e.entity), ...daRows.map((r) => r.entity)])).sort();
        return (
          <Section key={m.iso} title={m.iso} id={m.iso.toLowerCase()}>
            {!rows.ok ? <NoData what={`${m.iso} day-ahead`} reason={rows.reason} /> : null}
            {entities.length === 0 ? (
              <NoData reason={`no ${m.iso} rows in latest_prices or ${m.da.table}`} />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-rule text-left text-xs text-muted">
                      <th className="py-1 pr-3 font-normal">Hub or zone</th>
                      <th className="py-1 pr-3 text-right font-normal">Real time, USD/MWh</th>
                      <th className="py-1 pr-3 font-normal">Interval start (UTC)</th>
                      <th className="py-1 pr-3 text-right font-normal">Day-ahead this hour, USD/MWh</th>
                      <th className="py-1 pr-3 font-normal">Hour start (UTC)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entities.map((e) => {
                      const rt = ents.find((r) => r.entity === e);
                      const d = daNow(daRows.filter((r) => r.entity === e), now);
                      return (
                        <tr key={e} className="border-b border-rule/60">
                          <td className="py-1 pr-3">
                            <Link href={`/prices/${encodeURIComponent(e)}`} className="font-mono">
                              {node(e)}
                            </Link>
                            {e === m.main ? <span className="ml-2 text-xs text-muted">main</span> : null}
                          </td>
                          <td className="py-1 pr-3 text-right tabular-nums">
                            {rt ? (
                              <Num check={`latest_prices|${rt.entity}|${rt.variable}`} raw={rt.value}>
                                {price(rt.value)}
                              </Num>
                            ) : (
                              <span className="text-xs text-muted">no data: not in latest_prices</span>
                            )}
                          </td>
                          <td className="py-1 pr-3 text-xs text-muted">{rt ? `${utc(rt.ts_utc).replace(" UTC", "")} (${rt.variable})` : ""}</td>
                          <td className="py-1 pr-3 text-right tabular-nums">
                            {d ? (
                              <Num check={`series|${m.da.table}|${e}|${m.da.variable}|${d.ts_utc}`} raw={d.value}>
                                {price(d.value)}
                              </Num>
                            ) : (
                              <span className="text-xs text-muted">no data: hour not in {m.da.table}</span>
                            )}
                          </td>
                          <td className="py-1 pr-3 text-xs text-muted">{d ? utc(d.ts_utc).replace(" UTC", "") : ""}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
            <Cite tables={["latest_prices", m.da.table]} />
          </Section>
        );
      })}
    </>
  );
}
