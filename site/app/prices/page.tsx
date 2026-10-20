import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { Term } from "@/components/Term";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { MARKETS, daysAgo, latestPrices, renderTime, series, type SeriesRow } from "@/lib/data";
import { node, price, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { Tabs } from "@/components/tool/Tabs";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ToolPage } from "@/components/tool/ToolPage";
import { one, tabOf } from "@/lib/tabs";
import { PeakPremiumView } from "../explorer/ercot-peak-premium/view";

export const revalidate = 900;
export const metadata: Metadata = { title: "Prices" };

/** Session 319 (session 270's fault, the "no data" day-ahead cells): the cell's words say what the table holds, the
 * newest hour of the entity's rows in the day read, or that no row of the entity was read; the hour asked is the
 * render time's, as before (the fault was the data: the day-ahead tables of four grids held no row of the last day). */
function daWhy(rows: SeriesRow[], table: string, since: string): string {
  if (!rows.length) return `no data: no ${table} row since ${since.slice(0, 16).replace("T", " ")} UTC`;
  const newest = rows.map((r) => r.ts_utc).sort().pop()!;
  return `no data: this hour is not in ${table}; its newest hour held is ${newest.slice(0, 16).replace("T", " ")} UTC`;
}
/** The day-ahead row whose hour contains `now`, if the table has it. */
function daNow(rows: SeriesRow[], now: number): SeriesRow | null {
  for (const r of rows) {
    const t = new Date(r.ts_utc).getTime();
    if (t <= now && now < t + 3_600_000) return r;
  }
  return null;
}

// Session 239: one page, two tabs (lib/tabs.ts): every hub and zone (what this page drew, below) and ERCOT, the peak
// premium explorer (what /explorer/ercot-peak-premium drew; it redirects to its tab). The tab is in the address,
// ?tab=ercot.
export default async function Prices({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = one(await searchParams);
  const tab = tabOf("/prices", sp.tab);
  return (
    <Brand>
      <ToolPage>
        <div data-prices={tab}>
          <Tabs page="/prices" active={tab} />
          {tab === "ercot" ? <PeakPremiumView /> : <NowView />}
          {/* session 328: each tab's public tables, as CSV with a Python and a Stata reader (latest_prices is the live set's
              own table, refreshed every 15 minutes, and is not an ERW table: its intervals reach the real-time tables) */}
          <TableDownloads tables={tab === "ercot" ? ["ercot_peak_premium_annual", "ercot_peak_premium_monthly"] : MARKETS.flatMap((m) => [m.rt?.table, m.da.table]).filter((t): t is string => Boolean(t))} />
          <Related href="/prices" />
        </div>
      </ToolPage>
    </Brand>
  );
}

/** The first tab: the newest price at every hub and zone (what /prices drew before session 239). */
async function NowView() {
  const now = renderTime();
  const latest = await attempt(latestPrices);
  const since = daysAgo(1, now);
  const da = await Promise.all(MARKETS.map(async (m) => ({ m, rows: await attempt(() => series(m.da.table, { variable: m.da.variable, since, market: m.da.market })) })));

  return (
    <>
      <h1 className="mb-1 text-3xl">Power prices</h1>
      <p className="mb-2 max-w-3xl">
        The newest real-time and day-ahead power prices at every public hub and zone of six <Term t="ISO" first />s, refreshed every 15 minutes, from each ISO&apos;s
        market data.
      </p>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Select a hub or zone for its last 30 days. <Term t="PJM" first /> prices are licensed for internal use and are not shown.{" "}
        <Link href="/data/methods/power_prices">Method</Link>.
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
                              <Num check={`latest_prices|${rt.entity}|${rt.variable}|${rt.ts_utc}`} raw={rt.value}>
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
                              <span className="text-xs text-muted" data-da-missing={e}>{daWhy(daRows.filter((r) => r.entity === e), m.da.table, since)}</span>
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
