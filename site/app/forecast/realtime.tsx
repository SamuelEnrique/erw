// Energy Research Warehouse (ERW) site, session 10409 (chain 720, part E): the ERW forecast of the real-time price on
// /forecast (site/data/predict/rt_price.json; method docs/methods/predict_price.md, section 7; the contract's dated
// lines of 27 November 2026). For a place whose day-ahead price forecast is of a hub the file holds: the forecast of the
// real-time price for the day forecast now, with its band and the hub's day-ahead price beside it; a past day beside
// what happened; and the report card. The day-ahead price is the market's own forecast of the real-time price: the
// comparator, as the operator's forecast is for demand, never an ERW method. A day the file holds no forecast for is a
// blank with the file's own reason. Every figure carries its key into the file. No advice, no view.
import type { ReactNode } from "react";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { ChartFrame, HeadlineNumber, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { pfKey } from "@/lib/pagefile";
import { CUT_WORDS, LABEL, METRIC_WORDS, dayWords, hourWords, isShown, localWords, methodShort, methodWords, metricUnit, monthWords, orderedKeys, placeWords, scoreWords, shortHeld, utcWords, valueWords, type Metric, type ScoresFile, type SummaryPart } from "@/lib/predict";
import { LINE_METHOD_SHORT, LINE_METHOD_WORDS, RT_LABEL, RT_METHODS, RT_SPANS, lineDays, lineDefaultDay, lineHours, lineScores, rtHubOf, wordsOfMethod, type LineHour, type LineScore, type RtPriceFile } from "@/lib/predictlines";
import type { Slot } from "./lines";

const RT_FILE = "predict/rt_price.json";
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

/** The hub of a slot's price forecast, where the place's price is shown and the real-time file holds that hub. */
export function rtOf(slot: Slot, rt: RtPriceFile | null) {
  const ser = slot.file?.series?.price;
  return isShown(slot.file, ser) && ser ? rtHubOf(rt, ser.hub) : null;
}

/** The page's section of the real-time price: one block a place whose hub the file holds, one place under the other
 *  (the tables keep the page's width). No place with such a hub: no section. The page's own four sections stand as
 *  they were; this one is placed after them by view.tsx, with price only. */
export function RealTimeSection({ slots, rt, scores, metric, asked }: { slots: Slot[]; rt: RtPriceFile | null; scores: ScoresFile | null; metric: Metric; asked: string | null }) {
  if (!slots.some((x) => rtOf(x, rt))) return null;
  return (
    <ToolSection title={RT_LABEL} id="realtime">
      {slots.map((x) => <RealTime key={x.mark} slot={x} rt={rt} scores={scores} metric={metric} asked={asked} />)}
    </ToolSection>
  );
}

/** The real-time price for one place: tomorrow, a past day, and the report card. */
export function RealTime({ slot, rt, scores, metric, asked }: { slot: Slot; rt: RtPriceFile | null; scores: ScoresFile | null; metric: Metric; asked: string | null }) {
  const entry = rtOf(slot, rt);
  if (!entry || !rt) return <div className="min-w-0" data-fc-rt={slot.mark} data-fc-rt-hub="none" />;
  const h = entry.hub, k = slot.mark, tz = h.time || slot.place.time;
  const title = `${placeWords(slot.place)}: the real-time price at ${h.hub}`;
  if (h.status !== "shown") {
    return <div className="min-w-0" data-fc-rt={k} data-fc-rt-hub={h.hub}><h4 className="mb-1 text-sm font-semibold">{title}</h4><Blank what={`${LABEL} of the real-time price, ${h.hub}`} words={h.status} why={h.tomorrow_held ?? `The file's status of this hub is "${h.status}".`} k={`rt|${k}`} /></div>;
  }
  const key = (...rest: (string | number)[]) => pfKey(RT_FILE, ["hubs", entry.hi, ...rest]);
  const mu = metricUnit(metric, UNIT);
  const made = `${LABEL}: a model's output (tier derived), not a published figure${h.made_utc ? `; made ${localWords(h.made_utc, tz)} (${utcWords(h.made_utc)})` : ""}; method: ${lineWords(h.method ?? "not said")}. ${rt.made_rule ? `The rule: ${rt.made_rule}. ` : ""}${DAY_AHEAD}: ${wordsOfMethod(rt.methods, "day_ahead") || "the hub's day-ahead price for the hour, the market's own forecast of the real-time price"}. Method note ${rt.method_note ?? "docs/methods/predict_price.md"}; site/data/${RT_FILE}.`;
  const tomorrow = lineHours(h.tomorrow_columns, h.tomorrow, "day_ahead");
  const tcol = (n: string) => (h.tomorrow_columns ?? []).indexOf(n);
  const fig = (x: LineHour, c: "erw" | "day_ahead", v: number, name: string, what: string) => <Num check={key("tomorrow", x.i, tcol(c))} raw={v} source={`${what} ${made}`}><span data-n={`fc|${k}|rt|${name}`}>{valueWords(v, UNIT)}</span></Num>;
  const withErw = tomorrow.filter((x) => x.erw !== null);
  const top = withErw.length ? withErw.reduce((a, b) => ((b.erw as number) > (a.erw as number) ? b : a)) : null;
  const low = withErw.length ? withErw.reduce((a, b) => ((b.erw as number) < (a.erw as number) ? b : a)) : null;
  const none = (why: string, words?: string) => <span className="font-sans text-base"><NotHeld words={words} why={why} /></span>;
  const lines = (hours: LineHour[], withActual: boolean): CatSeries[] => [
    { name: LABEL, color: "accent", kind: "line", values: hours.map((x) => x.erw) },
    ...(hours.some((x) => x.other !== null) ? [{ name: DAY_AHEAD, color: "series-3", kind: "line" as const, dash: "dashed" as const, values: hours.map((x) => x.other) }] : []),
    ...(withActual && hours.some((x) => x.actual !== null) ? [{ name: ACTUAL, color: "ink", kind: "line" as const, values: hours.map((x) => x.actual) }] : []),
  ];
  const notes = (hours: LineHour[]) => hours.map((x) => `Hour beginning ${localWords(x.ts, tz)}.${x.lo !== null && x.hi !== null ? ` Band: ${valueWords(x.lo, UNIT)} to ${valueWords(x.hi, UNIT)} ${UNIT}.` : ""}`);
  // a past day: the one asked for where the file holds it, else the newest day that holds a forecast and what happened
  const history = lineHours(h.history_columns, h.history, "day_ahead");
  const days = lineDays(history);
  const day = asked && days.includes(asked) ? asked : lineDefaultDay(history);
  const past = day ? history.filter((x) => x.day === day) : [];
  // the report card
  const part = (p: SummaryPart | null | undefined, span: string, words: string) => (p ? { key: span, cells: [<span key="s" title={spanWords(p)} className="cursor-help">{words}</span>,
    p.hours !== null && p.hours !== undefined ? <Num key="h" check={key("summary", span, "hours")} raw={p.hours} source={`The hours scored, ${spanWords(p)}.`}>{p.hours.toLocaleString("en-US")}</Num> : <NotHeld key="h" why="No count of hours is in the file." />,
    ...RT_METHODS.map((m) => {
      const v = p[metric]?.[m];
      return v === null || v === undefined ? <NotHeld key={m} why={`${lineWords(m)}: no score over ${words.toLowerCase()} is in the file.`} />
        : <Num key={m} check={key("summary", span, metric, m)} raw={v} source={`${lineWords(m)}, ${h.hub}, ${words.toLowerCase()} (${spanWords(p)}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. Every method of this row is scored on the same hours. site/data/${RT_FILE}.`}>{scoreWords(v, metric, UNIT)}</Num>;
    })] } : null);
  const cuts = lineScores(rt.rows_columns, rt.rows, { place: `hub-${h.grid}`, series: "rt_price" }, ["mae", "mape"]);
  const mcol = (rt.rows_columns ?? []).indexOf(metric);
  const heads = RT_METHODS.map((m) => <span key={m} title={`${lineWords(m)}${wordsOfMethod(rt.methods, m) ? `: ${wordsOfMethod(rt.methods, m)}` : ""}`} className="cursor-help">{lineShort(m)}</span>);
  const cutRow = (cut: string, rowKey: string, name: ReactNode, words: string) => {
    const g = cuts.get(cut);
    if (!g || !g.keys.includes(rowKey)) return null;
    const cells = RT_METHODS.map((m) => g.cells.get(`${rowKey}|${m}`));
    const hrs = cells.map((c) => c?.hours ?? null).filter((x): x is number => x !== null);
    const one = (c: LineScore | undefined, m: string) => {
      const v = c ? c.values[metric] : null;
      return !c || v === null || v === undefined ? <NotHeld key={m} words={shortHeld(c?.held)} why={c?.held ?? `${lineWords(m)}: no score is in the file for ${words}${metric === "mape" ? " (a percent error is not defined where the price is near zero)" : ""}.`} />
        : <Num key={m} check={pfKey(RT_FILE, ["rows", c.i, mcol])} raw={v} source={`${lineWords(m)}, ${h.hub}, ${words}: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}${c.hours !== null ? `, over ${c.hours.toLocaleString("en-US")} hours` : ""}. site/data/${RT_FILE}, row ${c.i}.`}>{scoreWords(v, metric, UNIT)}</Num>;
    };
    return { key: `${cut}|${rowKey}`, cells: [name, hrs.length ? Math.max(...hrs).toLocaleString("en-US") : <NotHeld key="h" why="No count of hours is in the file for this row." />, ...RT_METHODS.map((m, i) => one(cells[i], m))] };
  };
  const real = <T,>(rows: (T | null)[]): T[] => rows.filter((r): r is T => r !== null);
  const other = real(["all", "last_2_years", "top10", "spike"].map((cut) => cutRow(cut, "", <span title={scores?.cuts?.[cut]} className={scores?.cuts?.[cut] ? "cursor-help" : undefined}>{CUT_WORDS[cut] ?? cut}</span>, (CUT_WORDS[cut] ?? cut).toLowerCase())));
  const table = (cut: string, first: string, words: (rowKey: string) => string, heading: string, each: string) => {
    const keys = orderedKeys(cut, cuts.get(cut)?.keys ?? []);
    if (!keys.length) return null;
    return (
      <div className="mb-5" data-fc-rt-cut={`${k}|${cut}`}>
        <h4 className="mb-1 text-sm font-semibold">{heading}, {mu} <span className="font-normal">({keys.length} {each})</span></h4>
        <div className={keys.length > 30 ? "max-h-[30rem] overflow-y-auto border-b border-rule" : undefined}>
          <ToolTable minWidth={460} caption={`${h.hub}: ${METRIC_WORDS[metric].toLowerCase()} of each forecast of the real-time price, ${heading.toLowerCase()}, ${mu}`} head={[first, "Hours", ...heads]}
            rows={real(keys.map((rowKey) => cutRow(cut, rowKey, <span className="whitespace-nowrap">{words(rowKey)}</span>, words(rowKey))))} />
        </div>
      </div>
    );
  };
  return (
    <div className="min-w-0" data-fc-rt={k} data-fc-rt-hub={h.hub} data-fc-rt-hours={withErw.length}>
      <h4 className="mb-2 text-sm font-semibold"><span className="cursor-help" title={made}>{title}</span></h4>
      {top && low ? (
        <>
          <div className="mb-4 grid gap-4 sm:grid-cols-3">
            <HeadlineNumber label="Highest hour" unit={UNIT} value={fig(top, "erw", top.erw as number, "top", `The highest hour of the ${LABEL} of the real-time price, the hour beginning ${localWords(top.ts, tz)}.`)} note={`${LABEL}, ${hourWords(top.hour)}`} />
            <HeadlineNumber label="Day-ahead price, same hour" unit={top.other !== null ? UNIT : undefined} value={top.other !== null ? fig(top, "day_ahead", top.other, "datop", `The hub's day-ahead price for the hour beginning ${localWords(top.ts, tz)}.`) : none("The file holds no day-ahead price for this hour.")} note={top.other !== null ? `${DAY_AHEAD}, ${hourWords(top.hour)}` : undefined} />
            <HeadlineNumber label="Lowest hour" unit={UNIT} value={fig(low, "erw", low.erw as number, "low", `The lowest hour of the ${LABEL} of the real-time price, the hour beginning ${localWords(low.ts, tz)}.`)} note={`${LABEL}, ${hourWords(low.hour)}`} />
          </div>
          <ChartFrame title={`${LABEL} of the real-time price: ${dayWords(h.target_day)}`} legend={bandOf(tomorrow) ? [BAND] : undefined}
            tip={<> <Hint words="source" why={made} />{bandOf(tomorrow) ? <>, <Hint words="band" why={`${h.band ?? "The band's rule is not in the file."}${typeof h.band_coverage_pct === "number" ? ` Of the past hours scored, ${h.band_coverage_pct}% fell inside their band.` : ""}`} /></> : null}</>}>
            <CategoryChart id={`fc-rt-${k}`} x={tomorrow.map((x) => hourWords(x.hour))} series={lines(tomorrow, false)} unit={UNIT} zero={false} height={280} every={6} band={bandOf(tomorrow)} notes={notes(tomorrow)}
              label={`${LABEL} of the real-time price at ${h.hub} for ${dayWords(h.target_day)}, with the hub's day-ahead price, by the hour of the hub's clock (${tz})`} />
          </ChartFrame>
        </>
      ) : <Blank what={`${LABEL} of the real-time price, ${h.hub}${h.target_day ? `, ${dayWords(h.target_day)}` : ""}`} words={shortHeld(h.tomorrow_held)} why={h.tomorrow_held ?? "The file holds no forecast for the day forecast now, and does not say why."} k={`rt|${k}`} />}
      {day && past.length ? (
        <div className="mt-4" data-fc-rt-day={k} data-fc-rt-day-of={day} data-fc-hours={past.length}>
          <ChartFrame title={`${dayWords(day)}: ${LABEL} of the real-time price and what happened`} legend={bandOf(past) ? [BAND] : undefined}
            tip={<> <Hint words="source" why={`${made} The file holds ${days[days.length - 1]} to ${days[0]} of the hub's clock${asked && asked !== day ? `; ${asked} is not among them, so the newest day held is drawn` : ""}.`} /></>}>
            <CategoryChart id={`fc-rt-day-${k}`} x={past.map((x) => hourWords(x.hour))} series={lines(past, true)} unit={UNIT} zero={false} height={260} every={6} band={bandOf(past)} notes={notes(past)}
              label={`${LABEL} of the real-time price at ${h.hub} on ${dayWords(day)}, beside the hub's day-ahead price and what happened, by the hour of the hub's clock (${tz})`} />
          </ChartFrame>
        </div>
      ) : null}
      <div className="mb-5 mt-4" data-fc-rt-summary={k}>
        <h4 className="mb-1 text-sm font-semibold">The real-time price: the last two years and the backtest, {mu}</h4>
        <ToolTable minWidth={460} caption={`${h.hub}: ${METRIC_WORDS[metric].toLowerCase()} of the ${LABEL} of the real-time price, of the day-ahead price and of two plain rules, over the last two years and the backtest, ${mu}`}
          head={["Span", "Hours", ...heads]} rows={real([...RT_SPANS.map(([span, words]) => part(h.summary?.[span], span, words)), ...other.filter((r) => !/^(all|last_2_years)\|/.test(r.key))])} />
      </div>
      {table("month", "Month", (rowKey) => monthWords(rowKey), "The real-time price by month", "months")}
      {table("hour", "Hour", (rowKey) => hourWords(rowKey), "The real-time price by hour of day", "hours")}
    </div>
  );
}
