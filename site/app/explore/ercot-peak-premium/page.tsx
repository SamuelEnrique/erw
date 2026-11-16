import type { Metadata } from "next";
import { BoxChart } from "@/components/BoxChart";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ExploreFrame, FilterForm, Freshness, type DrawnRows } from "@/components/explore/Explore";
import { ChartFrame, HeadlineNumber, HeadlineRow, Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { headers } from "@/lib/data";
import { MONTHS, choose, isoKey, longTime, type Params } from "@/lib/explore";
import {
  ANNUAL, BLOCKS, FIGURES, MONTHLY, SIDE, STATS, THESIS_HUB, fullYear, lastInput, partialMonth, periodTs, valueOf, type Row,
} from "@/lib/explore/peakpremium";
import { sourceOf } from "@/lib/explore/source";
import { node, price } from "@/lib/format";
import { HOURLY, attempt, rest } from "@/lib/supabase";
// by the site's alias, not "./": tests/test_session403.py holds this page to no private import (no chart of its own)
import { PeakPremiumDecisions } from "@/app/explore/ercot-peak-premium/Decisions";

// Session 403: the ERCOT peak premium explorer (platform tool 5, the first signature explorer), in review. The thesis
// chart made live: the distribution of ERCOT's real-time price by time of day, two years side by side, for any hub, for
// the whole year or one calendar month, from ercot_peak_premium_annual and ercot_peak_premium_monthly as they stand.
// The filters are a GET form, so every figure is drawn on the server from one row of a table and carries that row's
// check key (scripts/check-values.mjs reads it again). Nothing is computed here. The same tables are drawn one year at a
// time on the ERCOT tab of /prices (app/explorer/ercot-peak-premium/view.tsx), where /explorer/ercot-peak-premium
// redirects; this page leaves that one as it is.
// Session 2200 (chain 086): every figure carries its source in its hover (Num's `source`, the words of
// lib/explore/source.ts read from the figure's own key: the table, the hub, the variable, the period and ERCOT's two
// reports), and each headline number a Tip with the same words, reachable by keyboard. The thesis chart (BoxPlot) and the
// two line charts (TimeChart) draw their hover cards on fog with every figure in mono; scripts/check-explorers.mjs reads
// the page in a browser and proves the tips and the cards.
export const metadata: Metadata = { title: "ERCOT peak premium explorer" };
export const dynamic = "force-dynamic";

const PATH = "/explore/ercot-peak-premium";
const SELECT = "entity,variable,ts_utc,value";

// Session 7507 (chain 304): a price or a ratio is always written with two decimals. Until then a value that happened to
// be a whole number of dollars was written without them ("509" in a column of "1,538.66": lib/format.ts, shown).
function fig(v: number, unit: string): string {
  return unit === "count" ? Math.round(v).toLocaleString("en-US") : price(v);
}

export default async function PeakPremiumExplorer({ searchParams }: { searchParams: Promise<Params> }) {
  const sp = await searchParams;
  // what the filters can be: the hubs and years the annual table holds, with each year's interval count
  const [counts, header] = await Promise.all([
    attempt(() => rest<Row>("series", { select: SELECT, table_name: `eq.${ANNUAL}`, variable: "eq.n_intervals", order: "entity,ts_utc" }, HOURLY)),
    attempt(() => headers(ANNUAL)),
  ]);
  const input = header.ok ? lastInput(header.data) : null;
  const fresh = (
    <Freshness
      tables={[ANNUAL, MONTHLY]}
      detail={input ? <>The newest 15-minute interval the tables were computed from starts {longTime(input)} (the tables&apos; header); the year and the month it falls in are partial, and are marked so below.</> : null}
    />
  );
  const frame = (filters: React.ReactNode, body: React.ReactNode, rows?: DrawnRows) => (
    <ExploreFrame
      rows={rows}
      id="ercot-peak-premium"
      title="ERCOT peak premium"
      definition={<>The peak premium is how much higher and how much wider ERCOT&apos;s real-time price runs from 16:00 to 21:00 than at midday: the peak median minus the midday median, and the peak block&apos;s interquartile range (Q3 minus Q1), for each hub and each year or month since 2015.</>}
      fresh={fresh}
      filters={filters}
      method={{ href: "/data/methods/ercot_peak_premium", label: "ERCOT peak premium" }}
      tables={[ANNUAL, MONTHLY]}
      sourceNote={<>ERCOT real-time settlement point prices (NP6-785-ER, NP6-905-CD), every 15-minute interval with no cap or exclusion, blocks by the local (America/Chicago) hour an interval starts.</>}
    >
      {body}
    </ExploreFrame>
  );
  if (!counts.ok || counts.data.length === 0) {
    return frame(null, <NoData what={ANNUAL} reason={counts.ok ? "the table returned no rows" : counts.reason} />);
  }

  const hubs = Array.from(new Set(counts.data.map((r) => r.entity))).sort();
  const [hub, badHub] = choose(sp, "hub", hubs, hubs.includes(THESIS_HUB) ? THESIS_HUB : hubs[0]);
  // Session 7516 (chain 304, part B): a second hub beside the first (`vs` in the address; none by default), for the
  // reader who sets two hubs side by side for one period. The same hub twice is no second hub.
  const [vsS, badVs] = choose(sp, "vs", ["", ...hubs], "");
  const vs = vsS !== hub ? vsS : "";
  const hubRows = counts.data.filter((r) => r.entity === hub);
  const years = Array.from(new Set(hubRows.map((r) => new Date(r.ts_utc).getUTCFullYear()))).sort((a, b) => a - b);
  const [monthS, badMonth] = choose(sp, "month", ["", ...MONTHS.map((_, i) => String(i + 1))], "");
  const month = monthS ? Number(monthS) : null;
  const table = month ? MONTHLY : ANNUAL;

  // the hub's rows of the table the filters name: every year of the annual table, or the one month in every year
  const hubRead = (e: string) => attempt(() => rest<Row>("series", {
    select: SELECT, table_name: `eq.${table}`, entity: `eq.${e}`, order: "variable,ts_utc",
    ...(month ? { ts_utc: `in.(${years.map((y) => `"${periodTs(y, month)}"`).join(",")})` } : {}),
  }, HOURLY));
  const [read, monthly, vsRead] = await Promise.all([
    hubRead(hub),
    attempt(() => rest<Row>("series", { select: SELECT, table_name: `eq.${MONTHLY}`, entity: `eq.${hub}`, variable: "in.(peak_median,midday_median,overnight_median)", order: "variable,ts_utc" }, HOURLY)),
    vs ? hubRead(vs) : Promise.resolve(null),
  ]);
  const rows = read.ok ? read.data : [];
  const vsRows = vsRead && vsRead.ok ? vsRead.data : [];
  const held = (y: number) => valueOf(rows, "n_intervals", periodTs(y, month));
  const partial = (y: number) => {
    const n = held(y);
    return n !== undefined && (month ? partialMonth(y, month, n) : n !== fullYear(y));
  };
  const heldYears = years.filter((y) => held(y) !== undefined);
  const complete = heldYears.filter((y) => !partial(y));
  const ys = years.map(String);
  const [fromS, badFrom] = choose(sp, "from", ys, String(heldYears[0] ?? years[0]));
  const [toS, badTo] = choose(sp, "to", ys, String(complete[complete.length - 1] ?? heldYears[heldYears.length - 1] ?? years[years.length - 1]));
  const from = Number(fromS), to = Number(toS);
  const pair = from === to ? [to] : [from, to];
  const when = (y: number) => (month ? `${MONTHS[month - 1]} ${y}` : String(y));
  // session 7516: a period not yet over carries its mark wherever it heads a figure (the headline numbers, the tables'
  // period cells and column heads), not only in the filters and the chart's note: 2026 so far is not 2025's twelve months
  const mark = (y: number) => `${when(y)}${partial(y) ? " (partial)" : ""}`;
  // one figure writer, made once a hub (session 7516: the second hub's figures are written by the same lines as the first's)
  const writer = (hub: string, rows: Row[]) => {
    const key = (variable: string, y: number) => `series|${table}|${hub}|${variable}|${isoKey(periodTs(y, month))}`;
    const N = ({ v, y, unit }: { v: string; y: number; unit: string }) => {
      const x = valueOf(rows, v, periodTs(y, month));
      return x === undefined ? <span className="text-muted">not held</span> : <Num check={key(v, y)} raw={x} source={sourceOf(key(v, y), node(hub))}>{fig(x, unit)}</Num>;
    };
    return { key, N };
  };
  const { key, N } = writer(hub, rows);
  const Nvs = writer(vs, vsRows).N;
  // session 7507: a figure the table does not hold is "not held" alone: its unit is drawn only beside a figure
  const has = (v: string, y: number) => valueOf(rows, v, periodTs(y, month)) !== undefined;
  const yearOpt = (y: number) => ({ value: String(y), label: `${y}${held(y) === undefined ? " (not held)" : partial(y) ? " (partial)" : ""}` });
  const asked = [badHub && "hub", badMonth && "month", badFrom && "first year", badTo && "second year", badVs && "second hub"].filter(Boolean);

  const filters = (
    <FilterForm
      action={PATH}
      fields={[
        { name: "hub", label: "Hub", value: hub, options: hubs.map((h) => ({ value: h, label: node(h) })) },
        { name: "month", label: "Period", value: monthS, options: [{ value: "", label: "Whole year" }, ...MONTHS.map((m, i) => ({ value: String(i + 1), label: m }))] },
        { name: "from", label: "First year", value: fromS, options: years.map(yearOpt) },
        { name: "to", label: "Second year", value: toS, options: years.map(yearOpt) },
        { name: "vs", label: "Beside hub", value: vs, options: [{ value: "", label: "None" }, ...hubs.filter((h) => h !== hub).map((h) => ({ value: h, label: node(h) }))] },
      ]}
      reset={{ href: PATH, defaults: `${node(THESIS_HUB)}, the whole year, the first year held against the newest complete one (the thesis's comparison)` }}
      note={asked.length ? <span data-asked-unknown="1">The address asked for a {asked.join(" and a ")} the tables do not hold; the page shows the default in its place.</span> : undefined}
    />
  );
  if (!read.ok || rows.length === 0) {
    return frame(filters, <NoData what={table} reason={read.ok ? `no row for ${node(hub)}` : read.reason} />);
  }

  const name = node(hub);
  const boxes = BLOCKS.flatMap((b) => pair.map((y) => {
    const s = STATS.map((k) => valueOf(rows, `${b.key}_${k}`, periodTs(y, month)));
    return { b, y, s, ok: s.every((v) => v !== undefined) };
  }));
  const drawn = boxes.filter((x) => x.ok);
  const along = (variable: string): Line["points"] => heldYears
    .map((y) => ({ t: Date.UTC(y, (month ?? 1) - 1, 1) / 1000, v: valueOf(rows, variable, periodTs(y, month)) }))
    .filter((p): p is { t: number; v: number } => p.v !== undefined);
  const byMonth = (variable: string): Line["points"] => (monthly.ok ? monthly.data : [])
    .filter((r) => r.variable === variable)
    .map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value }));
  const lastHeld = heldYears[heldYears.length - 1];

  const body = (
    <>
      <HeadlineRow>
        {[["peak_iqr", "Peak-block IQR"], ["peak_minus_midday_median", "Peak median minus midday median"], ["all_median", "Median, all intervals"]].map(([v, label]) => (
          <HeadlineNumber key={v} label={`${label}, ${name}, ${mark(to)}`} value={<N v={v} y={to} unit="USD/MWh" />} unit={has(v, to) ? "USD/MWh" : undefined}
            tip={<Tip id={`source-${v}`} label={`where ${label.toLowerCase()} comes from`}>{sourceOf(key(v, to), name)}</Tip>}
            note={from !== to ? <>{mark(from)}: <N v={v} y={from} unit="USD/MWh" />{has(v, from) ? " USD/MWh" : null}</> : undefined} />
        ))}
      </HeadlineRow>

      <ChartFrame title={`The thesis chart: ${name}, ${when(from)}${from !== to ? ` against ${when(to)}` : ""}`}
        note={<>Each box runs from Q1 to Q3 with the median marked in the accent, its whiskers to the minimum and the maximum, one box a block and a year. The price axis is drawn around the boxes; a whisker that reaches past it stops at its edge, and every value is in the table below.{pair.some(partial) ? <> {pair.filter(partial).map(when).join(" and ")} is partial: its figures cover the intervals held so far.</> : null}</>}>
        {drawn.length === 0 ? <NoData what={table} reason={`no block summaries for ${name} in ${pair.map(when).join(" or ")}`} /> : (
          <div className="border border-rule bg-panel p-3" data-thesis-chart="1">
            <BoxChart rows={drawn.map(({ b, y, s }) => ({ name: `${b.label}, ${month ? MONTHS[month - 1].slice(0, 3) + " " : ""}${y}`, stats: s as [number, number, number, number, number] }))}
              unit="USD/MWh" ariaLabel={`${name}, real-time price by time-of-day block, ${pair.map(when).join(" and ")}`} file={`erw-explore-peak-premium-${name}-${month ?? "year"}-${from}-${to}`} />
          </div>
        )}
      </ChartFrame>

      <ToolSection title={`The five numbers of each block, USD/MWh`}>
        <ToolTable caption={`${name}: minimum, Q1, median, Q3 and maximum of each block`} minWidth={560}
          head={["Block", "Period", "Min", "Q1", "Median", "Q3", "Max"]}
          rows={boxes.map(({ b, y }) => ({
            key: `${b.key}-${y}`, highlight: b.key === "peak",
            cells: [<span key="b">{b.label} <span className="text-xs font-normal text-muted">{b.hours}</span></span>, mark(y), ...STATS.map((k) => <N key={k} v={`${b.key}_${k}`} y={y} unit="USD/MWh" />)],
          }))} />
      </ToolSection>

      <ToolSection title={`The thesis's figures, ${name}`} note="Each figure is one row of the table, as the method note defines it; the page computes none of them.">
        <ToolTable caption={`${name}: the thesis's figures in ${pair.map(when).join(" and ")}`} minWidth={360}
          head={["Figure", ...pair.map(mark)]}
          rows={FIGURES.map((f) => ({ key: f.v, cells: [f.label, ...pair.map((y) => <N key={y} v={f.v} y={y} unit={f.unit} />)] }))} />
      </ToolSection>

      {vs ? (
        <ToolSection id="two-hubs" title={`Two hubs side by side: ${name} and ${node(vs)}`}>
          <p className="mb-2 max-w-3xl text-sm" data-two-hubs={`${hub}|${vs}`}>
            The same rows for each hub, {pair.map(mark).join(" and ")}.
            <Tip id="two-hubs" label="how the two hubs are set side by side">
              Each figure is one row of the table for its own hub. The page takes no difference between the two: the difference of two hubs&apos; medians is not the median of the price difference between them from interval to interval, which these tables do not hold.
            </Tip>
          </p>
          {vsRows.length === 0 ? <NoData what={table} reason={vsRead && !vsRead.ok ? vsRead.reason : `no row for ${node(vs)}`} /> : (
            <ToolTable caption={`${name} and ${node(vs)}: the peak block and the thesis's figures in ${pair.map(when).join(" and ")}`} minWidth={pair.length > 1 ? 640 : 420}
              head={["Figure", ...pair.flatMap((y) => [`${name}, ${mark(y)}`, `${node(vs)}, ${mark(y)}`])]}
              rows={SIDE.map((f) => ({
                key: f.v, highlight: f.v === "peak_median" || f.v === "peak_iqr",
                cells: [f.label, ...pair.flatMap((y) => [<N key={`a${y}`} v={f.v} y={y} unit={f.unit} />, <Nvs key={`b${y}`} v={f.v} y={y} unit={f.unit} />])],
              }))} />
          )}
        </ToolSection>
      ) : null}

      <ChartFrame title={`${name} ${month ? `in ${MONTHS[month - 1]} of each year` : "by year"}: the peak premium`}
        note={<>One point a {month ? "year's " + MONTHS[month - 1] : "year"}{lastHeld !== undefined && partial(lastHeld) ? `; ${when(lastHeld)} is partial` : ""}.</>}>
        <LineChart x="year" unit="USD/MWh" height={260} ariaLabel={`${name}: peak-block IQR, peak minus midday median and the median, ${month ? MONTHS[month - 1] + " of each year" : "by year"}`}
          lines={[
            { label: "Peak-block IQR", points: along("peak_iqr"), color: "accent" },
            { label: "Peak minus midday median", points: along("peak_minus_midday_median"), color: "ink" },
            { label: "Median, all intervals", points: along("all_median"), color: "muted" },
          ]} />
      </ChartFrame>

      <ChartFrame title={`${name} by month: the median of each block`}
        note="Calendar months in America/Chicago, every month the monthly table holds; the newest is partial.">
        {!monthly.ok ? <NoData what={MONTHLY} reason={monthly.reason} /> : (
          <LineChart x="month" unit="USD/MWh" height={280} ariaLabel={`${name}: monthly median real-time price by block`}
            lines={[
              { label: "Peak median", points: byMonth("peak_median"), color: "accent" },
              { label: "Midday median", points: byMonth("midday_median"), color: "muted" },
              { label: "Overnight median", points: byMonth("overnight_median"), color: "ink" },
            ]} />
        )}
      </ChartFrame>

      <p className="max-w-3xl text-sm" data-related-view="1">
        The same two tables are drawn one hub and one year at a time on the <Link href="/prices?tab=ercot">ERCOT tab of Prices</Link>; this
        explorer sets two years side by side, as the thesis does, and reads one calendar month across the years.
        {" "}<span data-nodes-elsewhere="1">It holds the six hubs and no node: ERCOT&apos;s storage nodes are set against the hub average, month by month, on
        the <Link href="/cost-of-power/battery">battery page</Link> (ERCOT, HB_HUBAVG).</span>
      </p>
      <PeakPremiumDecisions />
    </>
  );
  // session 1496 (chain 158): the hub's rows of the table drawn, over the years drawn, as a download of their own
  return frame(filters, body, {
    table, entity: hub, start: `${Math.min(from, to)}-01-01`, end: `${Math.max(from, to) + 1}-01-01`,
    words: `${table}, ${node(hub)}, ${Math.min(from, to)} to ${Math.max(from, to)}${month ? " (every month of those years: the download does not filter by month)" : ""}`,
  });
}
