import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { InlineSpark } from "@/components/InlineSpark";
import { Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { series } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { FUELS, HISTORY, MARKETS, WITHHELD, commonDay, dayWords, onDay, fuelLines, marketOf, money, powerLines, signed, signedPct, summary, withheldWords, type Line, type MarketKey, type Row } from "@/lib/board3";

// Session 104: the price board, version 3, in the battery page's layout. The prices that matter, grouped: power by
// grid, gas, oil. Each with its last value, its move on the day and on the week, and thirty days of history. MISO is
// shown as paused and PJM as licensed, in words. The older board (/board) is as it was.

export const revalidate = 3600;
export const metadata: Metadata = { title: "The price board", robots: { index: false, follow: false } };

const POWER = "price_board_latest";
const FUEL = "eia_fuel_spot_prices";

function Move({ m, unit }: { m: Line["day"]; unit: string }) {
  if (!m) return <span className="text-muted">not held</span>;
  return (
    <span title={`against ${money(m.from.v)} ${unit} on ${m.from.t}`}>
      {signed(m.change)}{m.pct !== null ? <span className="ml-1 text-xs text-muted">({signedPct(m.pct)}%)</span> : null}
    </span>
  );
}

function rowsOf(lines: Line[], what: string) {
  return lines.map((l) => ({
    key: l.key,
    cells: l.last
      ? [
          <span key="n">{l.label}{l.at ? <span className="ml-1 text-xs text-muted">{l.at}</span> : null}</span>,
          <span key="v" data-board-last={l.key}>{money(l.last.v)}</span>,
          <span key="d" className="text-xs text-muted">{l.last.t}</span>,
          <Move key="dm" m={l.day} unit={l.unit} />,
          <Move key="wm" m={l.week} unit={l.unit} />,
          <InlineSpark key="s" values={l.history} label={`${l.label}, ${what}, the last ${l.history.length} days held`} />,
        ]
      : [l.label],
    wide: l.last ? undefined : "not held: the table holds no value for it",
  }));
}

export default async function Board3({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const market: MarketKey = marketOf(typeof sp.market === "string" ? sp.market : undefined);
  const since = new Date(Date.now() - 75 * 86_400_000).toISOString().slice(0, 10);
  const [p, f] = await Promise.all([
    attempt(() => series(POWER, { variable: `${market}_daily_mean` })),
    attempt(() => series(FUEL, { variable: "spot_price", since })),
  ]);
  const power = p.ok ? powerLines(p.data as Row[], market) : [];
  const fuels = f.ok ? fuelLines(f.data as Row[]) : [];
  const sentence = summary(power, fuels, market);
  const head = (unit: string) => ["", `Last, ${unit}`, "For", "On the day", "On the week", `Last ${HISTORY} days held`];
  const gas = fuels.filter((x) => x.group === "gas");
  const oil = fuels.filter((x) => x.group === "oil");
  const common = commonDay(power);                       // the newest day every priced grid holds: the day the grids are compared on
  const ranked = common ? onDay(power, common) : [];
  const lowest = ranked[0], highest = ranked[ranked.length - 1];
  const henry = gas.find((x) => x.last);

  return (
    <ToolPage>
      <ToolHeader title="The price board" crumb={<>Version 3, in review. The board as it was: <Link href="/board" className="underline">/board</Link></>}
        lead={<>The prices that matter, in three groups: power by grid, natural gas, oil. Each with its last value, its move on the day and on the week, and its last {HISTORY} days.</>} />
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>Day-ahead is the price set the day before for each hour of the day. Real-time is the price as the day ran; its newest day is one day behind day-ahead&apos;s.</>}>
            <div className="text-xs uppercase tracking-wide text-muted">Power market</div>
            <ul className="mt-1 space-y-1 text-sm">
              {(Object.keys(MARKETS) as MarketKey[]).map((k) => (
                <li key={k}>
                  {k === market
                    ? <span className="font-semibold" aria-current="true" data-board-market={k}>{MARKETS[k]}</span>
                    : <Link href={`/board/v3?market=${k}`} className="underline">{MARKETS[k]}</Link>}
                </li>
              ))}
            </ul>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {sentence
            ? <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-board-summary="1">{sentence}</p>
            : <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The power prices could not be read, so no number is shown{p.ok ? "" : `: ${p.reason}`}.</p>}

          {lowest && highest ? (
            <HeadlineRow>
              <HeadlineNumber label={`Lowest, ${MARKETS[market].toLowerCase()}`} value={money(lowest.v)} unit="USD/MWh" note={<>{lowest.line.label}, {lowest.line.at}, {dayWords(common!)}</>} />
              <HeadlineNumber label={`Highest, ${MARKETS[market].toLowerCase()}`} value={money(highest.v)} unit="USD/MWh" note={<>{highest.line.label}, {highest.line.at}, {dayWords(common!)}</>} />
              {henry ? <HeadlineNumber label="Henry Hub gas" value={money(henry.last!.v)} unit="USD/MMBtu" note={<>{dayWords(henry.last!.t)}, EIA&apos;s daily spot price</>} /> : null}
            </HeadlineRow>
          ) : null}

          <ToolSection title="Power, by grid" id="power"
            note={<>The mean of the day&apos;s {market === "da" ? "day-ahead" : "real-time"} prices at each grid&apos;s main hub, USD per MWh; a day is used when all of its intervals are held. On the day: against the day held before it. On the week: against the newest day held seven to ten days earlier; not held when there is none.</>}>
            {p.ok
              ? <ToolTable caption={`${MARKETS[market]} power by grid`} minWidth={640} head={head("USD/MWh")}
                  rows={[...rowsOf(power, `${MARKETS[market].toLowerCase()} daily mean`),
                    ...WITHHELD.map((w) => ({ key: w.iso, cells: [w.iso], wide: <span data-board-withheld={w.iso}><strong className="text-ink">{w.status}</strong>{w.words}</span> }))]} />
              : <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {p.reason}</p>}
          </ToolSection>

          <ToolSection title="Natural gas" id="gas" note={<>EIA&apos;s daily spot price, USD per million Btu. EIA publishes it some days after the trading day, and not on weekends or holidays, so the last value is older than the power prices above.</>}>
            {f.ok
              ? <ToolTable caption="Natural gas" minWidth={640} head={head("USD/MMBtu")} rows={rowsOf(gas, "spot price")} />
              : <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {f.reason}</p>}
          </ToolSection>

          <ToolSection title="Oil" id="oil" note={<>EIA&apos;s daily spot prices, USD per barrel, published as for gas.</>}>
            {f.ok
              ? <ToolTable caption="Oil" minWidth={640} head={head("USD/bbl")} rows={rowsOf(oil, "spot price")} />
              : <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {f.reason}</p>}
          </ToolSection>

          <Fold title="What is on this board, and what is not">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li><strong>One hub a grid.</strong> ERCOT&apos;s hub average, CAISO&apos;s SP15, New York City, SPP&apos;s North hub and New England&apos;s Internal hub. A plant or a load is paid or charged at its own node, which can differ in either direction.</li>
              <li><strong>MISO and PJM carry no number.</strong> {WITHHELD.map(withheldWords).join(" ")}</li>
              <li><strong>A daily mean, not the newest interval.</strong> The home page shows the newest real-time interval, refreshed every 15 minutes; this board shows whole days.</li>
              <li><strong>A move is between two days that are held.</strong> When the earlier day is not in the table, the move is &quot;not held&quot;; nothing is filled in.</li>
              <li><strong>Gas and oil are spot prices as EIA publishes them,</strong> {FUELS.map((x) => x.label).join(", ")}: no futures, no regional gas hub, no retail price.</li>
            </ul>
          </Fold>
          <SourceLine tables={[POWER, FUEL]} note={<>Power: the ERW&apos;s daily means of each operator&apos;s published prices, rebuilt on every daily run. Gas and oil: U.S. Energy Information Administration, public domain. This page is in review.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
