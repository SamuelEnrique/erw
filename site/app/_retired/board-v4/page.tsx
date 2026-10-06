import type { Metadata } from "next";
import { SiteLink } from "@/components/SiteLink";
import { Fold, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/board_v4.json";
import { GROUPS, MOVES, NOT_HELD, TABLE, day, extremes, groupLines, held, pct, placeWords, shortDay, signed, value, type BoardFile, type Line } from "@/lib/board4";
import { WITHHELD } from "@/lib/board3";

// Session 127: the price board, version 4, in review (lib/release.ts). Every price the warehouse holds as a daily series:
// its latest value and day, its move over a day, a week, a month and a year, and its place in its own one-year range;
// the spreads an analyst reads, each with its formula; and, greyed, what the plan names and no free source gives. Every
// number is a row of price_board_stats (warehouse/derived/price_board_v4.py; docs/methods/price_board_v4.md), read from
// the site's own copy (data/board_v4.json). The other boards (/board, /board/v3) are untouched.
export const metadata: Metadata = { title: "The price board, version 4", robots: { index: false, follow: false } };

const file = fileJson as unknown as BoardFile;
const METHOD = "/data/methods/price_board_v4";
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;
/** The groups whose prices cannot be negative: a percent is shown beside their moves. Power and the spreads can be. */
const PERCENT = new Set(["gas", "crude", "products"]);

/** Where the last value sits between the year's low and high: a track with a mark, and the two ends in words. */
function Range({ line }: { line: Line }) {
  const r = line.range;
  if (!r || r.position === null) return NOT;
  const W = 96, x = 3 + r.position * (W - 6);
  return (
    <span className="inline-flex items-center gap-2 whitespace-nowrap" data-range={line.key} title={`${line.label}: ${value(line.last!.v, line.unit)} between ${value(r.low, line.unit)} and ${value(r.high, line.unit)} over ${r.days} days held of the last 365; ${placeWords(r.position)}`}>
      <svg viewBox={`0 0 ${W} 12`} width={W} height={12} role="img" aria-label={`${placeWords(r.position)} between ${value(r.low, line.unit)} and ${value(r.high, line.unit)}`}>
        <line x1={3} x2={W - 3} y1={6} y2={6} stroke="var(--color-rule)" strokeWidth={3} strokeLinecap="round" />
        <circle cx={x} cy={6} r={4} fill="var(--color-accent)" stroke="var(--color-surface)" strokeWidth={1.5} />
      </svg>
      <span className="text-[11px] text-muted"><N k={`${line.key}|low`}>{value(r.low, line.unit)}</N> to <N k={`${line.key}|high`}>{value(r.high, line.unit)}</N></span>
    </span>
  );
}

function Lines({ id, spread }: { id: string; spread?: boolean }) {
  const lines = groupLines(file, id);
  const units = [...new Set(lines.map((l) => l.unit))];
  return (
    <>
      <ToolTable minWidth={860} caption={`${id}: latest value, moves and one-year range`}
        head={[spread ? "Spread" : "Price", `Latest${units.length === 1 ? `, ${units[0]}` : ""}`, "Its day", ...MOVES.map(([, name]) => name), "In its one-year range"]}
        rows={lines.map((l) => ({ key: l.key, muted: !l.last, cells: [
          <span key="n" className="block text-left">{l.label}{l.at ? <span className="text-muted">, {l.at}</span> : null}</span>,
          l.last ? <span key="v"><N k={`${l.key}|last`}>{value(l.last.v, l.unit)}</N>{units.length === 1 ? null : <span className="text-[11px] text-muted"> {l.unit}</span>}</span> : NOT,
          l.last ? <span key="d" className="whitespace-nowrap" title={day(l.last.t)}>{shortDay(l.last.t)}</span> : NOT,
          ...MOVES.map(([k]) => { const m = l.moves?.[k]; return m
            ? <span key={k} className="whitespace-nowrap" title={`against ${value(m.v, l.unit)} on ${day(m.t)}`}><N k={`${l.key}|${k}`}>{signed(m.change, l.unit)}</N>{m.pct !== null && PERCENT.has(id) ? <span className="text-[11px] text-muted"> {pct(m.pct)}</span> : null}</span>
            : <span key={k}>{NOT}</span>; }),
          <Range key="r" line={l} />,
        ] }))} />
      {spread ? <p className="mt-2 max-w-3xl text-xs text-muted" data-formula={id}>Formula: {lines[0]?.formula}.</p> : null}
    </>
  );
}

export default function BoardV4() {
  const h = held(file);
  const ex = extremes(file);
  return (
    <ToolPage>
      <ToolHeader title="The price board" crumb={<>Version 4, in review. The boards as they were: <SiteLink href="/board" className="underline">/board</SiteLink> and <SiteLink href="/board/v3" className="underline">/board/v3</SiteLink></>}
        lead={<>Every energy price the warehouse holds by the day: power at each grid&apos;s main hub, natural gas, crude oil and refined products. For each, the latest value and its day, how far it moved in a day, a week, a month and a year, and where it sits between its lowest and highest day of the past year. Then the spreads an analyst reads, each with its formula.</>} />
      <p className="mb-8 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
        The board holds <N k="sum|prices">{String(h.prices)}</N> prices and <N k="sum|spreads">{String(h.spreads)}</N> spreads, the newest of them for {day(h.newest)} and the oldest for {day(h.oldest)}
        {ex ? <>; against its own past year, {ex.top.label} ({ex.top.at}) sits highest, <N k="sum|top">{String(Math.round(ex.top.range!.position! * 100))}</N> percent of the way from its low to its high, and {ex.bottom.label} ({ex.bottom.at}) lowest, at <N k="sum|bottom">{String(Math.round(ex.bottom.range!.position! * 100))}</N> percent</> : null}.
      </p>
      {GROUPS.map((g) => (
        <ToolSection key={g.id} title={g.title} id={g.id} note={<>{g.note}{g.id === "spark" ? <> The heat rate, {file.heat_rate} MMBtu per MWh, is an assumption (about a combined-cycle gas plant), and Henry Hub is in Louisiana: it is not the gas a plant in any of these grids burns. Read the spread as indicative. The gas price is the operating day&apos;s, or the newest trading day&apos;s up to {file.gas_back_days} days before it.</> : null}</>}>
          <Lines id={g.id} spread={g.spread} />
        </ToolSection>
      ))}
      <ToolSection title="Named in the plan, and not on the board" id="not-held" note="Each needs a source that is licensed, or one the warehouse may not ask. Nothing stands in for them.">
        <ToolTable minWidth={760} words caption="Prices not held, the reason, and the source that would supply each"
          head={["Price", "Why it is not here", "The source that would supply it"]}
          rows={[...NOT_HELD.map((x) => ({ key: x.name, muted: true, cells: [x.name, x.why, x.source] })),
            ...WITHHELD.map((x) => ({ key: x.iso, muted: true, cells: [`${x.iso} power prices`], wide: <span data-withheld={x.iso}>{x.status}{x.words}</span> }))]} />
      </ToolSection>
      <Fold title="How to read the columns">
        <ul className="max-w-3xl list-disc space-y-1 pl-5">
          <li>Latest is the newest day held, and &quot;its day&quot; says which. Fuels are EIA&apos;s spot prices by trading day, published about a week behind. A power price is the mean of a complete local operating day; a day short of an interval is not a day.</li>
          <li>Day is against the day held before. Week, month and year are against the newest day held at least 7, 30 and 365 days earlier, when that day is no more than {file.slack_days} days older than that; otherwise the move is not held. Hover a move for the value and the day it is measured from.</li>
          <li>The range is the lowest and the highest day of the 365 days ending on the latest, shown when at least {file.range_min_days} of them are held. The mark is where the latest value sits between the two.</li>
          <li>A percent is shown beside a move only for a price that cannot be negative. Power prices and spreads can be, so they show the move alone.</li>
          <li>Nothing is filled or estimated. The full method, with EIA&apos;s terms quoted: <SiteLink href={METHOD}>the price board, version 4</SiteLink>.</li>
        </ul>
      </Fold>
      <SourceLine tables={[TABLE, "eia_fuel_spot_prices", "eia_product_spot_prices", "iso_hub_prices_history", "ercot_hub_prices_daily"]}
        note={<>Fuel prices: U.S. Energy Information Administration, daily spot prices (EIA names Refinitiv, an LSEG business, as their source). Power prices: each grid operator&apos;s public prices. Built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the table.</>} />
    </ToolPage>
  );
}
