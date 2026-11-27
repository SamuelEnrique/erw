// Energy Research Warehouse (ERW) site, session 10409 (chain 720, part E): the ERW forecast of the real-time price on
// /forecast (site/data/predict/rt_price.json; method docs/methods/predict_price.md, section 7; the contract's dated
// lines of 27 November 2026). For a place whose day-ahead price forecast is of a hub the file holds: the forecast of the
// real-time price for the day forecast now, with its band and the hub's day-ahead price beside it; a past day beside
// what happened; and the report card. The day-ahead price is the market's own forecast of the real-time price: the
// comparator, as the operator's forecast is for demand, never an ERW method. A day the file holds no forecast for is a
// blank with the file's own reason. Every figure carries its key into the file. No advice, no view.
//
// Session 10411 (the contract's lines of session 10603): one block draws a hub's forecast for either market, the
// real-time price (rt_price.json) or the day-ahead price at one more hub of a public grid (price_hubs.json): the same
// day forecast now, past day and report card, each figure with its key into its own file. The real-time block gains the
// backtest from 2016 scored by year. A cut's words are the file's own where it carries them. And a section lists the
// other hubs of the grid of each place chosen, one of which a reader can draw.
import type { ReactNode } from "react";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { ChartFrame, HeadlineNumber, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { pfKey } from "@/lib/pagefile";
import { LABEL, METRIC_WORDS, dayWords, eventHref, hourWords, isShown, localWords, methodShort, methodWords, metricUnit, monthWords, orderedKeys, placeWords, scoreWords, shortHeld, utcWords, valueWords, type Cell, type Metric, type ScoresFile, type SummaryPart } from "@/lib/predict";
import {
  HUB_METHODS, HUB_SPANS, LINE_METHOD_SHORT, LINE_METHOD_WORDS, PRICE_CUT_WORDS, RT_LABEL, RT_METHODS, RT_SPANS, gridOfHub, lineDays, lineDefaultDay, lineHours, lineScores, moreHubs, priceHubOf, rtHubOf, shareWords, wordsOfMethod,
  type BandCoverage, type LineHour, type LineScore, type LongBacktest, type MethodWords, type PriceHubsFile, type RtPriceFile,
} from "@/lib/predictlines";
import type { Slot } from "./lines";

const RT_FILE = "predict/rt_price.json";
const HUBS_FILE = "predict/price_hubs.json";
const DAY_AHEAD = "Day-ahead price";
const ACTUAL = "What happened";
const BAND = { label: "Band of the ERW forecast", color: "var(--color-rule)" };
const UNIT = "USD/MWh";

function Blank({ what, words, why, k }: { what: string; words: string; why: string; k: string }) {
  return (
    <div className="my-2 flex min-h-24 cursor-help items-center justify-center border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" title={why} data-fc-blank={k}>
      {what}: {words}
    </div>
  );
}
const NotHeld = ({ words = "not held", why }: { words?: string; why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">{words}</span>;
const lineWords = (id: string) => LINE_METHOD_WORDS[id] ?? methodWords(id);
const lineShort = (id: string) => LINE_METHOD_SHORT[id] ?? methodShort(id);
const spanWords = (p: { first_day: string | null; last_day: string | null } | null | undefined) => (p?.first_day && p?.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say");
const bandOf = (hours: LineHour[]) => (hours.some((h) => h.lo !== null && h.hi !== null) ? { lo: hours.map((h) => h.lo), hi: hours.map((h) => h.hi), name: "" } : undefined);
const real = <T,>(rows: (T | null)[]): T[] => rows.filter((r): r is T => r !== null);

/** The hub of a slot's price forecast, where the place's price is shown and the real-time file holds that hub. */
export function rtOf(slot: Slot, rt: RtPriceFile | null) {
  const ser = slot.file?.series?.price;
  return isShown(slot.file, ser) && ser ? rtHubOf(rt, ser.hub) : null;
}

/** What the two markets' blocks share of a hub's entry (an entry of rt_price.json, or of price_hubs.json). */
type HubShape = {
  hub: string; time: string; status: string; method: string | null; made_utc?: string | null; target_day?: string | null;
  band?: string | null; band_coverage_pct?: number | null; band_coverage?: BandCoverage | null;
  tomorrow_columns?: string[]; tomorrow?: Cell[][] | null; tomorrow_held?: string | null;
  history_columns?: string[]; history?: Cell[][] | null; summary?: Record<string, SummaryPart | null | undefined> | null;
  long_backtest?: LongBacktest | null;
};
/** `rt`: the real-time price, beside the hub's day-ahead price. `dah`: the day-ahead price at one more hub. The word is
 *  also the block's mark in the page's data attributes. */
type Market = "rt" | "dah";
type BlockProps = {
  market: Market; k: string; title: string; h: HubShape; file: string; hi: number;
  /** the file's score rows, and the names its rows of this hub carry */
  rowsColumns: string[] | undefined; rows: Cell[][] | undefined; rowsPlace: string; rowsSeries: string;
  methods: MethodWords[] | undefined; madeRule: string | null | undefined; methodNote: string | null | undefined;
  /** each cut's words: the file's own, else the score file's words for its price rows */
  cuts: Record<string, string> | null | undefined;
  metric: Metric; asked: string | null; tz: string; foot?: ReactNode;
};
const MARKET: Record<Market, { what: string; other: string | null; otherName: string; methods: readonly string[]; spans: [string, string][]; spanWords: string }> = {
  rt: { what: "the real-time price", other: "day_ahead", otherName: DAY_AHEAD, methods: RT_METHODS, spans: RT_SPANS, spanWords: "the last two years and the backtest" },
  dah: { what: "the day-ahead price", other: null, otherName: "", methods: HUB_METHODS, spans: HUB_SPANS, spanWords: "the last 30 days and the backtest" },
};

/** One hub and one market: the day forecast now (or a blank with the file's reason), a past day beside what happened,
 *  and the report card: the summary, the other cuts, the months and the hours of the day; for the real-time price, the
 *  backtest from 2016 by year. */
function PriceBlock({ market, k, title, h, file, hi, rowsColumns, rows, rowsPlace, rowsSeries, methods, madeRule, methodNote, cuts: cutWords, metric, asked, tz, foot }: BlockProps) {
  const M = MARKET[market];
  const mark = (name: string, value: string | number) => ({ [`data-fc-${market}${name ? `-${name}` : ""}`]: value });
  if (h.status !== "shown") {
    return <div className="min-w-0" {...mark("", k)} {...mark("hub", h.hub)}><h4 className="mb-1 text-sm font-semibold">{title}</h4><Blank what={`${LABEL} of ${M.what}, ${h.hub}`} words={h.status} why={h.tomorrow_held ?? `The file's status of this hub is "${h.status}".`} k={`${market}|${k}`} /></div>;
  }
  const key = (...rest: (string | number)[]) => pfKey(file, ["hubs", hi, ...rest]);
  const mu = metricUnit(metric, UNIT);
  const otherWords = M.other ? `${M.otherName}: ${wordsOfMethod(methods, M.other) || "the hub's day-ahead price for the hour, the market's own forecast of the real-time price"}. ` : "";
  const made = `${LABEL}: a model's output (tier derived), not a published figure${h.made_utc ? `; made ${localWords(h.made_utc, tz)} (${utcWords(h.made_utc)})` : ""}; method: ${lineWords(h.method ?? "not said")}. ${madeRule ? `The rule: ${madeRule}. ` : ""}${otherWords}Method note ${methodNote ?? "docs/methods/predict_price.md"}; site/data/${file}.`;
  const tomorrow = lineHours(h.tomorrow_columns, h.tomorrow, M.other ?? "operator");
  const tcol = (n: string) => (h.tomorrow_columns ?? []).indexOf(n);
  const fig = (x: LineHour, c: string, v: number, name: string, what: string) => <Num check={key("tomorrow", x.i, tcol(c))} raw={v} source={`${what} ${made}`}><span data-n={`fc|${k}|${market}|${name}`}>{valueWords(v, UNIT)}</span></Num>;
  const withErw = tomorrow.filter((x) => x.erw !== null);
  const top = withErw.length ? withErw.reduce((a, b) => ((b.erw as number) > (a.erw as number) ? b : a)) : null;
  const low = withErw.length ? withErw.reduce((a, b) => ((b.erw as number) < (a.erw as number) ? b : a)) : null;
  const none = (why: string, words?: string) => <span className="font-sans text-base"><NotHeld words={words} why={why} /></span>;
  const lines = (hours: LineHour[], withActual: boolean): CatSeries[] => [
    { name: LABEL, color: "accent", kind: "line", values: hours.map((x) => x.erw) },
    ...(M.other && hours.some((x) => x.other !== null) ? [{ name: M.otherName, color: "series-3", kind: "line" as const, dash: "dashed" as const, values: hours.map((x) => x.other) }] : []),
    ...(withActual && hours.some((x) => x.actual !== null) ? [{ name: ACTUAL, color: "ink", kind: "line" as const, values: hours.map((x) => x.actual) }] : []),
  ];
  const notes = (hours: LineHour[]) => hours.map((x) => `Hour beginning ${localWords(x.ts, tz)}.${x.lo !== null && x.hi !== null ? ` Band: ${valueWords(x.lo, UNIT)} to ${valueWords(x.hi, UNIT)} ${UNIT}.` : ""}`);
  // a past day: the one asked for where the file holds it, else the newest day that holds a forecast and what happened
  const history = lineHours(h.history_columns, h.history, M.other ?? "operator");
  const days = lineDays(history);
  const day = asked && days.includes(asked) ? asked : lineDefaultDay(history);
  const past = day ? history.filter((x) => x.day === day) : [];
  // the report card
  const scoreCell = (p: SummaryPart, m: string, k2: string, words: string) => {
    const v = p[metric]?.[m];
    return v === null || v === undefined ? <NotHeld key={m} why={`${lineWords(m)}: no score over ${words.toLowerCase()} is in the file.`} />
      : <Num key={m} check={k2} raw={v} source={`${lineWords(m)}, ${h.hub}, ${words.toLowerCase()} (${spanWords(p)}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. Every method of this row is scored on the same hours. site/data/${file}.`}>{scoreWords(v, metric, UNIT)}</Num>;
  };
  const hoursCell = (p: SummaryPart, k2: string) => (p.hours !== null && p.hours !== undefined ? <Num key="h" check={k2} raw={p.hours} source={`The hours scored, ${spanWords(p)}.`}>{p.hours.toLocaleString("en-US")}</Num> : <NotHeld key="h" why="No count of hours is in the file." />);
  const part = (p: SummaryPart | null | undefined, span: string, words: string) => (p ? { key: span, cells: [<span key="s" title={spanWords(p)} className="cursor-help">{words}</span>,
    hoursCell(p, key("summary", span, "hours")), ...M.methods.map((m) => scoreCell(p, m, key("summary", span, metric, m), words))] } : null);
  const cuts = lineScores(rowsColumns, rows, { place: rowsPlace, series: rowsSeries }, ["mae", "mape"]);
  const mcol = (rowsColumns ?? []).indexOf(metric);
  const heads = M.methods.map((m) => <span key={m} title={`${lineWords(m)}${wordsOfMethod(methods, m) ? `: ${wordsOfMethod(methods, m)}` : ""}`} className="cursor-help">{lineShort(m)}</span>);
  const cutRow = (cut: string, rowKey: string, name: ReactNode, words: string) => {
    const g = cuts.get(cut);
    if (!g || !g.keys.includes(rowKey)) return null;
    const cells = M.methods.map((m) => g.cells.get(`${rowKey}|${m}`));
    const hrs = cells.map((c) => c?.hours ?? null).filter((x): x is number => x !== null);
    const one = (c: LineScore | undefined, m: string) => {
      const v = c ? c.values[metric] : null;
      return !c || v === null || v === undefined ? <NotHeld key={m} words={shortHeld(c?.held)} why={c?.held ?? `${lineWords(m)}: no score is in the file for ${words}${metric === "mape" ? " (a percent error is not defined where the price is near zero)" : ""}.`} />
        : <Num key={m} check={pfKey(file, ["rows", c.i, mcol])} raw={v} source={`${lineWords(m)}, ${h.hub}, ${words}: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}${c.hours !== null ? `, over ${c.hours.toLocaleString("en-US")} hours` : ""}. site/data/${file}, row ${c.i}.`}>{scoreWords(v, metric, UNIT)}</Num>;
    };
    return { key: `${cut}|${rowKey}`, cells: [name, hrs.length ? Math.max(...hrs).toLocaleString("en-US") : <NotHeld key="h" why="No count of hours is in the file for this row." />, ...M.methods.map((m, i) => one(cells[i], m))] };
  };
  // a cut is named in the page's words for a price (the ten days are those of the highest price hour), with the file's
  // own words of the cut on hover where the file carries them
  const cutName = (cut: string) => PRICE_CUT_WORDS[cut] ?? cut;
  const named = (cut: string) => <span title={cutWords?.[cut] ? `The file's words on this cut: ${cutWords[cut]}.` : undefined} className={cutWords?.[cut] ? "cursor-help" : undefined}>{cutName(cut)}</span>;
  const other = real(["top10", "spike"].map((cut) => cutRow(cut, "", named(cut), cutName(cut).toLowerCase())));
  const events = real((cuts.get("event")?.keys ?? []).map((ev) => cutRow("event", ev, eventHref(ev) ? <SiteLink href={eventHref(ev) as string} title="An event of /events. Opens the event's page.">{`Event: ${ev.replace(/[_-]/g, " ")}`}</SiteLink> : `Event: ${ev.replace(/[_-]/g, " ")}`, `the event ${ev.replace(/[_-]/g, " ")}`)));
  const table = (cut: string, first: string, words: (rowKey: string) => string, heading: string, each: string) => {
    const keys = orderedKeys(cut, cuts.get(cut)?.keys ?? []);
    if (!keys.length) return null;
    return (
      <div className="mb-5" {...mark("cut", `${k}|${cut}`)}>
        <h4 className="mb-1 text-sm font-semibold"><span title={cutWords?.[cut] ? `The file's words on this cut: ${cutWords[cut]}.` : undefined} className={cutWords?.[cut] ? "cursor-help" : undefined}>{heading}</span>, {mu} <span className="font-normal">({keys.length} {each})</span></h4>
        <div className={keys.length > 30 ? "max-h-[30rem] overflow-y-auto border-b border-rule" : undefined}>
          <ToolTable minWidth={460} caption={`${h.hub}: ${METRIC_WORDS[metric].toLowerCase()} of each forecast of ${M.what}, ${heading.toLowerCase()}, ${mu}`} head={[first, "Hours", ...heads]}
            rows={real(keys.map((rowKey) => cutRow(cut, rowKey, <span className="whitespace-nowrap">{words(rowKey)}</span>, words(rowKey))))} />
        </div>
      </div>
    );
  };
  const long = h.long_backtest;
  const years = long?.by_year ?? [];
  const What = `${M.what[0].toUpperCase()}${M.what.slice(1)}`;
  return (
    <div className="mb-8 min-w-0" {...mark("", k)} {...mark("hub", h.hub)} {...mark("hours", withErw.length)}>
      <h4 className="mb-2 text-sm font-semibold"><span className="cursor-help" title={made}>{title}</span></h4>
      {top && low ? (
        <>
          <div className="mb-4 grid gap-4 sm:grid-cols-3">
            <HeadlineNumber label="Highest hour" unit={UNIT} value={fig(top, "erw", top.erw as number, "top", `The highest hour of the ${LABEL} of ${M.what}, the hour beginning ${localWords(top.ts, tz)}.`)} note={`${LABEL}, ${hourWords(top.hour)}`} />
            {M.other ? <HeadlineNumber label={`${M.otherName}, same hour`} unit={top.other !== null ? UNIT : undefined} value={top.other !== null ? fig(top, M.other, top.other, "datop", `The hub's day-ahead price for the hour beginning ${localWords(top.ts, tz)}.`) : none("The file holds no day-ahead price for this hour.")} note={top.other !== null ? `${M.otherName}, ${hourWords(top.hour)}` : undefined} /> : null}
            <HeadlineNumber label="Lowest hour" unit={UNIT} value={fig(low, "erw", low.erw as number, "low", `The lowest hour of the ${LABEL} of ${M.what}, the hour beginning ${localWords(low.ts, tz)}.`)} note={`${LABEL}, ${hourWords(low.hour)}`} />
          </div>
          <ChartFrame title={`${LABEL} of ${M.what}: ${dayWords(h.target_day)}`} legend={bandOf(tomorrow) ? [BAND] : undefined}
            tip={<> <Hint words="source" why={made} />{bandOf(tomorrow) ? <>, <Hint words="band" why={`${h.band ?? "The band's rule is not in the file."}${typeof h.band_coverage_pct === "number" ? ` Of the past hours scored, ${h.band_coverage_pct}% fell inside their band.` : ""}`} /></> : null}</>}>
            <CategoryChart id={`fc-${market}-${k}`} x={tomorrow.map((x) => hourWords(x.hour))} series={lines(tomorrow, false)} unit={UNIT} zero={false} height={280} every={6} band={bandOf(tomorrow)} notes={notes(tomorrow)}
              label={`${LABEL} of ${M.what} at ${h.hub} for ${dayWords(h.target_day)}${M.other ? ", with the hub's day-ahead price" : ""}, by the hour of the hub's clock (${tz})`} />
          </ChartFrame>
        </>
      ) : <Blank what={`${LABEL} of ${M.what}, ${h.hub}${h.target_day ? `, ${dayWords(h.target_day)}` : ""}`} words={shortHeld(h.tomorrow_held)} why={h.tomorrow_held ?? "The file holds no forecast for the day forecast now, and does not say why."} k={`${market}|${k}`} />}
      {day && past.length ? (
        <div className="mt-4" {...mark("day", k)} {...mark("day-of", day)} data-fc-hours={past.length}>
          <ChartFrame title={`${dayWords(day)}: ${LABEL} of ${M.what} and what happened`} legend={bandOf(past) ? [BAND] : undefined}
            tip={<> <Hint words="source" why={`${made} The file holds ${days[days.length - 1]} to ${days[0]} of the hub's clock${asked && asked !== day ? `; ${asked} is not among them, so the newest day held is drawn` : ""}.`} /></>}>
            <CategoryChart id={`fc-${market}-day-${k}`} x={past.map((x) => hourWords(x.hour))} series={lines(past, true)} unit={UNIT} zero={false} height={260} every={6} band={bandOf(past)} notes={notes(past)}
              label={`${LABEL} of ${M.what} at ${h.hub} on ${dayWords(day)}, beside ${M.other ? "the hub's day-ahead price and " : ""}what happened, by the hour of the hub's clock (${tz})`} />
          </ChartFrame>
        </div>
      ) : null}
      <div className="mb-5 mt-4" {...mark("summary", k)}>
        <h4 className="mb-1 text-sm font-semibold">{What}: {M.spanWords}, {mu}</h4>
        <ToolTable minWidth={460} caption={`${h.hub}: ${METRIC_WORDS[metric].toLowerCase()} of the ${LABEL} of ${M.what}${M.other ? ", of the day-ahead price" : ""} and of the plain rules, over ${M.spanWords}, ${mu}`}
          head={["Span", "Hours", ...heads]} rows={[...real(M.spans.map(([span, words]) => part(h.summary?.[span], span, words))), ...other, ...events]} />
      </div>
      {long && (long.all || years.length) ? (
        <div className="mb-5" {...mark("years", k)}>
          <h4 className="mb-1 text-sm font-semibold"><span className={long.what ? "cursor-help" : undefined} title={long.what ? `The file's words: ${long.what}.` : undefined}>{What} year by year, the backtest from {long.first_target ?? "its first day"}</span>, {mu}
            {typeof long.band_coverage_pct === "number" ? <span className="font-normal"> (inside the band over the whole span: <Num check={key("long_backtest", "band_coverage_pct")} raw={long.band_coverage_pct} source={`Of the hours scored over the whole span, the share on which what happened fell inside the band, in percent. site/data/${file}.`}>{shareWords(long.band_coverage_pct)}</Num>%)</span> : null}</h4>
          <ToolTable minWidth={460} caption={`${h.hub}: ${METRIC_WORDS[metric].toLowerCase()} of each forecast of ${M.what} over the backtest from ${long.first_target ?? "its first day"}, the whole span and each calendar year, ${mu}`}
            head={["Year", "Hours", ...heads]}
            rows={[...(long.all ? [{ key: "all", cells: [<span key="s" title={spanWords(long.all)} className="cursor-help">Every year</span>, hoursCell(long.all, key("long_backtest", "all", "hours")), ...M.methods.map((m) => scoreCell(long.all as SummaryPart, m, key("long_backtest", "all", metric, m), "the whole span"))] }] : []),
              ...years.map((y, i) => ({ key: String(y.year), cells: [<span key="s" title={spanWords(y)} className="cursor-help">{y.year}</span>, hoursCell(y, key("long_backtest", "by_year", i, "hours")), ...M.methods.map((m) => scoreCell(y, m, key("long_backtest", "by_year", i, metric, m), String(y.year)))] }))]} />
        </div>
      ) : null}
      {table("month", "Month", (rowKey) => monthWords(rowKey), `${What} by month`, "months")}
      {table("hour", "Hour", (rowKey) => hourWords(rowKey), `${What} by hour of day`, "hours")}
      {foot}
    </div>
  );
}

/** The page's section of the real-time price: one block a place whose hub the file holds, one place under the other
 *  (the tables keep the page's width). No place with such a hub: no section. The page's own four sections stand as
 *  they were; this one is placed after them by view.tsx, with price only. */
/** (`scores` is taken and not read since session 10411: the real-time file carries its own cuts' words.) */
export function RealTimeSection({ slots, rt, metric, asked }: { slots: Slot[]; rt: RtPriceFile | null; scores: ScoresFile | null; metric: Metric; asked: string | null }) {
  if (!slots.some((x) => rtOf(x, rt))) return null;
  return (
    <ToolSection title={RT_LABEL} id="realtime">
      {slots.map((x) => <RealTime key={x.mark} slot={x} rt={rt} metric={metric} asked={asked} />)}
    </ToolSection>
  );
}

/** The real-time price for one place: tomorrow, a past day, and the report card. */
export function RealTime({ slot, rt, metric, asked }: { slot: Slot; rt: RtPriceFile | null; metric: Metric; asked: string | null }) {
  const entry = rtOf(slot, rt);
  if (!entry || !rt) return <div className="min-w-0" data-fc-rt={slot.mark} data-fc-rt-hub="none" />;
  const h = entry.hub;
  return <PriceBlock market="rt" k={slot.mark} title={`${placeWords(slot.place)}: the real-time price at ${h.hub}`} h={h} file={RT_FILE} hi={entry.hi} rowsColumns={rt.rows_columns} rows={rt.rows} rowsPlace={`hub-${h.grid}`} rowsSeries="rt_price"
    methods={rt.methods} madeRule={rt.made_rule} methodNote={rt.method_note} cuts={rt.cuts ?? null} metric={metric} asked={asked} tz={h.time || slot.place.time} />;
}

/** Session 10411: the other hubs of the grid of each place chosen (price_hubs.json for the day-ahead price,
 *  rt_price.json for the real-time price): one row a hub with a few figures of each market, and the hub a reader
 *  chose drawn whole under the table, the day-ahead price then the real-time price. A grid with no other hub: no
 *  section. The hub in the address is drawn only when it is one of those listed here. */
export function MoreHubsSection({ slots, hubs, rt, scores, metric, asked, chosen, hrefOf }: {
  slots: Slot[]; hubs: PriceHubsFile | null; rt: RtPriceFile | null; scores: ScoresFile | null; metric: Metric; asked: string | null; chosen: string | null; hrefOf: (hub: string | null) => string;
}) {
  const ownOf = (x: Slot) => { const ser = x.file?.series?.price; return isShown(x.file, ser) && ser ? ser.hub : null; };
  // one list for the page: the hubs of each place's grid, each once (two places of one grid share it)
  const seen = new Set<string>();
  const groups = slots.map((x) => ({ x, own: ownOf(x) })).filter((g): g is { x: Slot; own: string } => !!g.own).map((g) => ({ ...g, ids: moreHubs(g.own, hubs, rt).filter((id) => (seen.has(id) ? false : (seen.add(id), true))) })).filter((g) => g.ids.length);
  if (!groups.length) return null;
  const mu = metricUnit(metric, UNIT);
  const offered = groups.flatMap((g) => g.ids);
  const drawn = chosen && offered.includes(chosen) ? chosen : null;
  const da = drawn ? priceHubOf(hubs, drawn) : null, live = drawn ? rtHubOf(rt, drawn) : null;
  const tz = da?.hub.time ?? live?.hub.time ?? groups[0].x.place.time;
  return (
    <ToolSection title="More hubs" id="hubs">
      <div data-fc-hubs={offered.length} data-fc-hub-drawn={drawn ?? "none"}>
        {groups.map((g) => (
          <div key={g.x.mark} className="mb-5" data-fc-hubs-of={g.x.mark}>
            <h4 className="mb-1 text-sm font-semibold">{placeWords(g.x.place)}: the other hubs of {gridOfHub(g.own).toUpperCase()}, {mu}</h4>
            <ToolTable minWidth={640} caption={`${placeWords(g.x.place)}: the other hubs of its grid, each with the highest and lowest hour of the ${LABEL} of its day-ahead price for the day forecast now and each market's error, ${mu}`}
              head={[<span key="h" className="cursor-help" title={`The hubs of the same grid as ${g.own}, the hub this place's own price forecast is of. Press one to draw it under this table.`}>Hub</span>,
                <span key="t" className="cursor-help" title={`The highest hour of the ${LABEL} of the hub's day-ahead price for the day forecast now, ${UNIT}, and the hour of the hub's clock it begins.`}>Day-ahead, highest hour</span>,
                <span key="l" className="cursor-help" title={`The lowest hour of the same forecast, ${UNIT}, and the hour it begins.`}>Lowest hour</span>,
                <span key="d" className="cursor-help" title={`${METRIC_WORDS[metric]} of the ${LABEL} of the hub's day-ahead price over its backtest, ${mu}.`}>Day-ahead: {LABEL}, the backtest</span>,
                <span key="r" className="cursor-help" title={`${METRIC_WORDS[metric]} of the ${LABEL} of the hub's real-time price over the last two years, ${mu}.`}>Real-time: {LABEL}, two years</span>,
                <span key="p" className="cursor-help" title={`${METRIC_WORDS[metric]} of the hub's day-ahead price as a forecast of its real-time price, on the same hours, ${mu}. The comparator, never an ERW method.`}>Real-time: day-ahead price</span>]}
              rows={g.ids.map((id) => {
                const d = priceHubOf(hubs, id), r = rtHubOf(rt, id);
                const hours = d && d.hub.status === "shown" ? lineHours(d.hub.tomorrow_columns, d.hub.tomorrow, "operator").filter((x) => x.erw !== null) : [];
                const col = (d?.hub.tomorrow_columns ?? []).indexOf("erw");
                const pick = (lowest: boolean) => (hours.length ? hours.reduce((a, b) => ((lowest ? (b.erw as number) < (a.erw as number) : (b.erw as number) > (a.erw as number)) ? b : a)) : null);
                const hourCell = (x: LineHour | null, what: string) => (x && d
                  ? <span key={what} className="whitespace-nowrap"><Num check={pfKey(HUBS_FILE, ["hubs", d.hi, "tomorrow", x.i, col])} raw={x.erw as number} source={`The ${what} hour of the ${LABEL} of the day-ahead price at ${id} for ${dayWords(d.hub.target_day)}, the hour beginning ${localWords(x.ts, d.hub.time)}. site/data/${HUBS_FILE}.`}>{valueWords(x.erw as number, UNIT)}</Num> <span className="text-xs">at {hourWords(x.hour)}</span></span>
                  : <NotHeld key={what} words={d ? shortHeld(d.hub.tomorrow_held) : "not held"} why={d ? d.hub.tomorrow_held ?? "The file holds no forecast of this hub's day-ahead price for the day forecast now." : `The day-ahead hubs file (site/data/${HUBS_FILE}) holds no entry for this hub.`} />);
                const score = (v: number | null | undefined, k2: string, what: string, why: string) => (v === null || v === undefined ? <NotHeld key={k2} why={why} /> : <Num key={k2} check={k2} raw={v} source={what}>{scoreWords(v, metric, UNIT)}</Num>);
                const back = d?.hub.summary?.backtest, two = r?.hub.summary?.last_2_years;
                return { key: id, highlight: drawn === id, cells: [
                  <SiteLink key="n" href={hrefOf(id)} className="inline-block py-1" title={`Draw ${id} under this table: its day-ahead and its real-time price`}>{id}</SiteLink>,
                  hourCell(pick(false), "highest"), hourCell(pick(true), "lowest"),
                  score(back?.[metric]?.erw, d ? pfKey(HUBS_FILE, ["hubs", d.hi, "summary", "backtest", metric, "erw"]) : "d", `${LABEL} of the day-ahead price at ${id}, the backtest (${spanWords(back)}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${HUBS_FILE}.`, d ? "No score over the backtest is in the file for this hub." : `The day-ahead hubs file holds no entry for this hub.`),
                  score(two?.[metric]?.erw, r ? pfKey(RT_FILE, ["hubs", r.hi, "summary", "last_2_years", metric, "erw"]) : "r", `${LABEL} of the real-time price at ${id}, the last two years (${spanWords(two)}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${RT_FILE}.`, r ? "No score over the last two years is in the file for this hub." : `The real-time file (site/data/${RT_FILE}) holds no entry for this hub.`),
                  score(two?.[metric]?.day_ahead, r ? pfKey(RT_FILE, ["hubs", r.hi, "summary", "last_2_years", metric, "day_ahead"]) : "p", `The day-ahead price at ${id} as a forecast of its real-time price, the last two years (${spanWords(two)}), on the same hours: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${RT_FILE}.`, r ? "No score of the day-ahead price is in the file for this hub." : `The real-time file holds no entry for this hub.`)] };
              })} />
          </div>
        ))}
        {drawn ? (
          <div data-fc-hub={drawn}>
            <p className="mb-3 text-sm"><SiteLink href={hrefOf(null)} className="inline-block py-1">Close {drawn}</SiteLink></p>
            {da && hubs ? <PriceBlock market="dah" k="hub" title={`${drawn}: the day-ahead price`} h={da.hub} file={HUBS_FILE} hi={da.hi} rowsColumns={hubs.rows_columns} rows={hubs.rows} rowsPlace={da.hub.place} rowsSeries="price"
              methods={hubs.methods} madeRule={hubs.made_rule} methodNote={hubs.method_note} cuts={hubs.cuts ?? scores?.cuts_price ?? null} metric={metric} asked={asked} tz={tz}
              foot={<p className="text-sm" data-fc-hub-download-dah={drawn}>The day-ahead price forecast at {drawn}, hour by hour:{" "}
                <a href={`/forecast/hub-price?hub=${encodeURIComponent(drawn)}`} download data-download="csv" className="inline-block py-1">CSV</a>,{" "}
                <a href={`/forecast/hub-price/python?hub=${encodeURIComponent(drawn)}`} download data-download="python" className="inline-block py-1">Python</a>,{" "}
                <a href={`/forecast/hub-price/stata?hub=${encodeURIComponent(drawn)}`} download data-download="stata" className="inline-block py-1">Stata</a></p>} /> : null}
            {live && rt ? <PriceBlock market="rt" k="hub" title={`${drawn}: the real-time price`} h={live.hub} file={RT_FILE} hi={live.hi} rowsColumns={rt.rows_columns} rows={rt.rows} rowsPlace={`hub-${live.hub.grid}`} rowsSeries="rt_price"
              methods={rt.methods} madeRule={rt.made_rule} methodNote={rt.method_note} cuts={rt.cuts ?? null} metric={metric} asked={asked} tz={tz}
              foot={<p className="text-sm" data-fc-hub-download={drawn}>The real-time price at {drawn}, hour by hour:{" "}
                <a href={`/forecast/realtime-price?hub=${encodeURIComponent(drawn)}`} download data-download="csv" className="inline-block py-1">CSV</a>,{" "}
                <a href={`/forecast/realtime-price/python?hub=${encodeURIComponent(drawn)}`} download data-download="python" className="inline-block py-1">Python</a>,{" "}
                <a href={`/forecast/realtime-price/stata?hub=${encodeURIComponent(drawn)}`} download data-download="stata" className="inline-block py-1">Stata</a></p>} /> : null}
          </div>
        ) : null}
      </div>
    </ToolSection>
  );
}
