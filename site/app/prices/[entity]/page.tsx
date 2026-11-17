import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { Brand } from "@/components/Brand";  // session 242: the page takes the brand (plain markup; it carried no wrapper)
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { MARKETS, daysAgo, latestPrices, series, type SeriesRow } from "@/lib/data";
import { count, node, price, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { MONTH_TABLE, heldOf, monthLine, realLessDayAhead, variableWords, whenWords } from "@/lib/pricehub";
import { label } from "@/lib/pricecompare";

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
  // session 7539 (the read, rows 2 and 3): when the low and the high fell, the first of each
  let lo = rows[0], hi = rows[0];
  for (const r of rows) { if (r.value < lo.value) lo = r; if (r.value > hi.value) hi = r; }
  return { n: v.length, min: Math.min(...v), max: Math.max(...v), mean: v.reduce((a, b) => a + b, 0) / v.length, first: rows[0].ts_utc, last: rows.at(-1)!.ts_utc, minAt: lo.ts_utc, maxAt: hi.ts_utc };
}

export default async function EntityPrices({ params }: PageProps<"/prices/[entity]">) {
  const entity = decode((await params).entity);
  const m = MARKETS.find((x) => x.main.split(":")[0] === entity.split(":")[0]);
  if (!m || !/^[a-z]+:[\w .\-]+$/.test(entity)) notFound();

  const since = daysAgo(30);
  const [rt, da, latest, monthRead] = await Promise.all([
    m.rt ? attempt(() => series(m.rt!.table, { entity, variable: m.rt!.variable, since })) : Promise.resolve(null),
    attempt(() => series(m.da.table, { entity, variable: m.da.variable, since })),
    attempt(latestPrices),
    attempt(() => series(MONTH_TABLE, { entity })),   // wip/alt-prices-2: the hub's newest whole month
  ]);
  const rtRows = rt && rt.ok ? rt.data : [];
  const daRows = da.ok ? da.data : [];
  if (rt?.ok && da.ok && rtRows.length === 0 && daRows.length === 0) notFound();

  const toLine = (rows: SeriesRow[]) => rows.map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value }));
  const lines: Line[] = [];
  // session 7539 (the read, row 6): the legend in words, not the table's variable codes (the codes are in the table below)
  if (daRows.length) lines.push({ label: `Day-ahead, ${variableWords(m.da.variable)}`, points: toLine(daRows), color: "muted", step: true });
  if (rtRows.length) lines.push({ label: `Real time, ${variableWords(m.rt!.variable)}`, points: toLine(rtRows), color: "accent" });
  const lp = latest.ok ? latest.data.find((r) => r.entity === entity) : undefined;
  const summary = [
    { name: "Real time", src: m.rt, s: stats(rtRows), held: heldOf(rtRows, m.rt?.freq) },
    { name: "Day-ahead", src: m.da, s: stats(daRows), held: heldOf(daRows, m.da.freq) },
  ];
  // session 7539 (the read, row 5): real time less day-ahead over the hours both hold
  const dart = m.rt ? realLessDayAhead(rtRows, daRows, m.rt.freq) : null;
  const name = label({ entity, grid: m.iso, node: node(entity) });
  const month = monthRead.ok ? monthLine(monthRead.data) : null;   // wip/alt-prices-2

  return (
    <Brand>
      <p className="text-sm">
        <Link href="/prices">Prices</Link> / {m.iso}
      </p>
      <h1 className="mb-1 font-mono text-2xl">{node(entity)}</h1>
      <p className="mb-5 text-sm text-muted">
        {/* session 7539 (the read, row 6): the hub as a reader names it, beside the operator's code */}
        <span data-hub-name={entity}>{name}</span>, entity <code className="font-mono">{entity}</code>, last 30 days. Times in UTC.
      </p>

      {lp ? (
        <p className="mb-4 text-sm">
          Latest real-time interval:{" "}
          <Num check={`latest_prices|${lp.entity}|${lp.variable}|${lp.ts_utc}`} raw={lp.value} className="text-lg tabular-nums">
            {price(lp.value)}
          </Num>{" "}
          {lp.unit}, starting {utc(lp.ts_utc)} <span className="text-xs text-muted" title={lp.variable}>({variableWords(lp.variable)})</span>
        </p>
      ) : null}

      {lines.length ? (
        <LineChart lines={lines} unit="USD/MWh" ariaLabel={`${entity} real-time and day-ahead prices, last 30 days`} />
      ) : null}
      {/* session 7539 (the read, row 7): the words were "the ERW has no SPP real-time series table", untrue since the live
          set has held SPP's 15-minute real-time hub prices in iso_rtm_hub_prices (24 September 2026); site/data/markets.json
          still names none for SPP, so this page draws none (the read's ruling, row 14) */}
      {!m.rt ? <NoData what="real time" reason={`this page draws no ${m.iso} real-time series: site/data/markets.json names no real-time table for ${m.iso}, so only the latest interval (above, from latest_prices) is shown`} /> : null}
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
            {summary.map(({ name: market, src, s, held }) => (
              <tr key={market} className="border-b border-rule/60">
                <td className="py-1 pr-4"><span title={src ? `${src.variable}: ${variableWords(src.variable)}` : undefined}>{market}</span></td>
                <td className="py-1 pr-4 font-mono text-xs">{src ? src.table : ""}</td>
                {s ? (
                  <>
                    {/* session 7539 (the read, row 4): the intervals held of those the span from the first row to the last
                        holds at the table's step, and the days of the span with no row, on hover */}
                    <td className="py-1 pr-4 text-right tabular-nums" data-held={held ? `${s.n}/${held.due}` : undefined}
                      title={held ? `${count(s.n)} of the ${count(held.due)} intervals from ${utc(s.first)} to ${utc(s.last)} at the table's step (${src?.freq}).${held.missingDays.length ? ` UTC days with no row: ${held.missingDays.join(", ")}.` : " No whole day is missing."} The mean is of the intervals held.` : undefined}>
                      {count(s.n)}{held && held.due !== s.n ? <> of {count(held.due)}</> : null}
                    </td>
                    {/* session 7539 (the read, rows 2 and 3): when the low and the high fell, on hover */}
                    <td className="py-1 pr-4 text-right tabular-nums" data-at={s.minAt} title={`The lowest interval starts ${whenWords(s.minAt, m.iso)}`}>{price(s.min)}</td>
                    <td className="py-1 pr-4 text-right tabular-nums">{price(s.mean)}</td>
                    <td className="py-1 pr-4 text-right tabular-nums" data-at={s.maxAt} title={`The highest interval starts ${whenWords(s.maxAt, m.iso)}`}>{price(s.max)}</td>
                    <td className="py-1 pr-4 text-xs">{utc(s.first)}</td>
                    <td className="py-1 pr-4 text-xs">{utc(s.last)}</td>
                  </>
                ) : (
                  <td colSpan={6} className="py-1 pr-4 text-xs text-muted">
                    no data: {src ? `no rows in ${src.table} for this entity in the last 30 days` : `no real-time table named for ${m.iso} in site/data/markets.json`}
                  </td>
                )}
              </tr>
            ))}
            {dart ? (
              <tr className="border-b border-rule/60" data-dart={entity}>
                <td className="py-1 pr-4">
                  <span title="Each hour's real-time price (the mean of its intervals, taken only when every interval of the hour is held) less the same hour's day-ahead price. The two means above are over different hours, so their difference is not this figure.">Real time less day-ahead</span>
                </td>
                <td className="py-1 pr-4 text-xs">the hours both hold</td>
                <td className="py-1 pr-4 text-right tabular-nums" title={`${count(dart.n)} hours from ${utc(dart.first)} to ${utc(dart.last)}`}>{count(dart.n)} hours</td>
                <td className="py-1 pr-4 text-right tabular-nums" title={`The hour starting ${whenWords(dart.minAt, m.iso)}`}>{price(dart.min)}</td>
                <td className="py-1 pr-4 text-right tabular-nums">{price(dart.mean)}</td>
                <td className="py-1 pr-4 text-right tabular-nums" title={`The hour starting ${whenWords(dart.maxAt, m.iso)}`}>{price(dart.max)}</td>
                <td className="py-1 pr-4 text-xs">{utc(dart.first)}</td>
                <td className="py-1 pr-4 text-xs">{utc(dart.last)}</td>
              </tr>
            ) : null}
            {/* ruling alternative 2 (wip/alt-prices-2, not a default on main): the newest whole calendar month, from the monthly table */}
            {month ? ([["Real time", month.rt, month.rtHours, month.rtDue], ["Day-ahead", month.da, month.daHours, month.daDue]] as const).map(([market, v, held, due]) => v === null ? null : (
              <tr key={`month-${market}`} className="border-b border-rule/60" data-month={`${market}|${month.month}`}>
                <td className="py-1 pr-4"><span title={`The mean of every hour of ${month.month}, as ${MONTH_TABLE} holds it (the month whole: the rolling window above is about 35 days of the hourly tables). Default on the site: the rolling 30 days only; months on /prices/compare.`}>{market}, {month.month}</span></td>
                <td className="py-1 pr-4 font-mono text-xs">{MONTH_TABLE}</td>
                <td className="py-1 pr-4 text-right tabular-nums">{held !== null ? count(held) : ""}{held !== null && due !== null && held !== due ? <> of {count(due)}</> : null}</td>
                <td className="py-1 pr-4" />
                <td className="py-1 pr-4 text-right tabular-nums" data-month-mean={`${market}|${month.month}`}>{price(v)}</td>
                <td className="py-1 pr-4" colSpan={3} />
              </tr>
            )) : null}
          </tbody>
        </table>
        <p className="mt-1 text-xs text-muted">Min, mean and max of every interval in the window, USD/MWh, computed on this page from the rows charted above.</p>
      </div>
    </Brand>
  );
}
