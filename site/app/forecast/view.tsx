// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): what /forecast draws, as one plain component
// so that a test can draw it to HTML without a build (the page adds the brand's frame and the table downloads).
//
// Tomorrow: for a chosen place, the ERW forecast by hour with its band, and the operator's own forecast for the same
// hours where the file holds one; a tab for price. How it has done: any past day beside what happened, and the report
// card (the ERW, the operator, the same hour yesterday, the same hour a week ago) by month, by hour of day and for all
// places at once. Two places side by side. The hours and places where the ERW forecast lost are drawn exactly as the
// ones where it won: one table, one weight, the file's own order.
//
// Every figure is the page files' (lib/predictfiles.ts; contract docs/state/page_files_predict.md) and carries its key
// into its file. A held series is a blank that says "license needed" with the file's reason on hover. The page states
// what the model forecast and how it scored: no advice, no view.
import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { ToolTabs } from "@/components/tool/Choose";
import { ChartFrame, HeadlineNumber, InputPanel, SourceLine, ToolHeader, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { pfKey } from "@/lib/pagefile";
import {
  FOUR, LABEL, METRIC_WORDS, NONE, SERIES, SERIES_WORDS, blankWhy, blankWords, dayScore, dayWords, daysOf, defaultDay, extreme, historyOf, hourWords, hrefOf, isShown,
  localWords, methodWhat, methodWords, methodsOf, metricOf, metricUnit, monthWords, orderedKeys, placeWords, queryOf, rowHours, scoreWords, scoresOf, tomorrowOf, utcWords, valueWords,
  type Hour, type IndexPlace, type Metric, type PlaceFile, type PlaceSeries, type PredictIndex, type Query, type Score, type ScoresFile, type SeriesKey,
} from "@/lib/predict";
import { predictIndex, predictPlace, predictScores } from "@/lib/predictfiles";

type Raw = Record<string, string | string[] | undefined>;
type Slot = { mark: "a" | "b"; place: IndexPlace; file: PlaceFile | null };
const OPERATOR = "Operator's forecast";
const ACTUAL = "What happened";
const fileOf = (slot: Slot) => `predict/${slot.place.file}`;

/** A blank the size of what it stands for: the words on its face, the file's reason on hover. */
function Blank({ what, words, why, k }: { what: string; words: string; why: string; k: string }) {
  return (
    <div className="my-2 flex min-h-24 cursor-help items-center justify-center border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" title={why} data-fc-blank={k}>
      {what}: {words}
    </div>
  );
}
const NotHeld = ({ words = "not held", why }: { words?: string; why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">{words}</span>;

/** Where the model's line and the operator's come from, for a chart's hover. */
function sourceWords(slot: Slot, ser: PlaceSeries, s: SeriesKey, scores: ScoresFile | null): string {
  const made = ser.made_utc ? `made ${localWords(ser.made_utc, slot.place.time)} (${utcWords(ser.made_utc)})` : "the hour it was made is not in the file";
  const op = s === "price" ? "No operator publishes a price forecast." : `${OPERATOR}: ${methodWhat(scores, "operator") || "the operator's own day-ahead forecast, as the warehouse holds it"}.`;
  return `${LABEL}: a model's output (tier derived), not a published figure; ${made}; method: ${methodWords(ser.method ?? "not said")}. ${op} Built from the ERW's tables ${(slot.file?.tables ?? []).join(", ") || "(none named)"}; method note ${ser.method_note}.`;
}

/** The place's heading: its name, and on hover the hour the forecast was made and the method the place uses. */
function PlaceHead({ slot, s, index }: { slot: Slot; s: SeriesKey; index: PredictIndex }) {
  const ser = slot.file?.series?.[s];
  const shown = isShown(slot.file, ser);
  const why = shown && ser
    ? `${LABEL} for ${dayWords(ser.target_day)}: made ${localWords(ser.made_utc, slot.place.time) || "at an hour the file does not say"} (${utcWords(ser.made_utc)}), from the place's own figures through ${localWords(ser.inputs_through_utc, slot.place.time) || "an hour the file does not say"}. Method: ${methodWords(ser.method ?? "not said")}, last fit ${ser.fit_day ?? "on a day the file does not say"}.${index.made_rule ? ` ${index.made_rule}` : ""}${index.choice_rule ? ` ${index.choice_rule}` : ""}`
    : blankWhy(ser ?? slot.place.series?.[s], slot.file?.example === true || index.example === true);
  return (
    <h3 className="mb-2 font-serif text-xl text-accent" data-fc-place={slot.mark}>
      <span className="cursor-help border-b border-dotted border-muted" title={why}>{placeWords(slot.place)}</span>
      {s === "price" && shown && ser?.hub ? <span className="ml-2 font-sans text-sm text-ink" title={`The hub the price forecast is of, ${ser.market ?? "day-ahead"} market.`}>{ser.hub}, {ser.market ?? "day-ahead"}</span> : null}
    </h3>
  );
}

function hourNotes(hours: Hour[], unit: string, tz: string): string[] {
  return hours.map((h) => `Hour beginning ${localWords(h.ts, tz)}.${h.lo !== null && h.hi !== null ? ` Band: ${valueWords(h.lo, unit)} to ${valueWords(h.hi, unit)} ${unit}.` : ""}${h.made ? ` Made ${localWords(h.made, tz)}${h.kind ? `, ${h.kind === "live" ? "on the day" : "by the backtest"}` : ""}.` : ""}`);
}
function chartSeries(hours: Hour[], withActual: boolean): CatSeries[] {
  const out: CatSeries[] = [{ name: LABEL, color: "accent", kind: "line", values: hours.map((h) => h.erw) }];
  if (hours.some((h) => h.operator !== null)) out.push({ name: OPERATOR, color: "series-3", kind: "line", dash: "dashed", values: hours.map((h) => h.operator) });
  if (withActual && hours.some((h) => h.actual !== null)) out.push({ name: ACTUAL, color: "ink", kind: "line", values: hours.map((h) => h.actual) });
  return out;
}

/** Tomorrow for one place: three figures, the chart with its band, and the hours as a table. */
function Tomorrow({ slot, s, index, scores }: { slot: Slot; s: SeriesKey; index: PredictIndex; scores: ScoresFile | null }) {
  const ser = slot.file?.series?.[s];
  const k = `${slot.mark}|${s}`;
  if (!isShown(slot.file, ser) || !ser) {
    const of = ser ?? slot.place.series?.[s];
    const example = slot.file?.example === true || index.example === true;
    return (
      <div className="min-w-0" data-fc-tomorrow={slot.mark} data-fc-shown="0">
        <PlaceHead slot={slot} s={s} index={index} />
        <Blank what={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()}, ${placeWords(slot.place)}`} words={blankWords(of?.status, example)} why={blankWhy(of, example)} k={`tomorrow|${k}`} />
      </div>
    );
  }
  const hours = tomorrowOf(ser);
  const unit = ser.unit, tz = slot.place.time, file = fileOf(slot);
  const col = (n: string) => ser.tomorrow_columns.indexOf(n);
  const src = sourceWords(slot, ser, s, scores);
  const top = extreme(hours, "erw"), low = extreme(hours, "erw", true);
  const opAtTop = top ? top.hour.operator : null;
  const hasOp = hours.some((h) => h.operator !== null);
  const opWhy = ser.operator_held ? `${OPERATOR}: ${ser.operator_held}.` : `${OPERATOR}: not in the file for these hours yet (an operator's forecast is drawn once it is published and held).`;
  const fig = (h: Hour, c: string, v: number, key: string, what: string) =>
    <Num check={pfKey(file, ["series", s, "tomorrow", h.i, col(c)])} raw={v} source={`${what} ${src}`}><span data-n={`fc|${k}|${key}`}>{valueWords(v, unit)}</span></Num>;
  const band = hours.some((h) => h.lo !== null && h.hi !== null) ? { lo: hours.map((h) => h.lo), hi: hours.map((h) => h.hi), name: "Band" } : undefined;
  return (
    <div className="min-w-0" data-fc-tomorrow={slot.mark} data-fc-shown="1" data-fc-hours={hours.length}>
      <PlaceHead slot={slot} s={s} index={index} />
      <div className="mb-4 grid gap-4 sm:grid-cols-3">
        <HeadlineNumber label="Highest hour" unit={unit}
          value={top ? fig(top.hour, "erw", top.v, "top", `The highest hour of the ${LABEL}, the hour beginning ${localWords(top.hour.ts, tz)}.`) : <NotHeld why="No hour of the forecast is held." />}
          note={top ? `${LABEL}, ${top.hour.label}` : undefined} />
        <HeadlineNumber label="Operator, same hour" unit={opAtTop !== null ? unit : undefined}
          value={top && opAtTop !== null ? fig(top.hour, "operator", opAtTop, "optop", `The operator's own forecast for the hour beginning ${localWords(top.hour.ts, tz)}.`) : <NotHeld words={ser.operator_held ?? "not held"} why={opWhy} />}
          note={top && opAtTop !== null ? `${OPERATOR}, ${top.hour.label}` : undefined} />
        <HeadlineNumber label="Lowest hour" unit={unit}
          value={low ? fig(low.hour, "erw", low.v, "low", `The lowest hour of the ${LABEL}, the hour beginning ${localWords(low.hour.ts, tz)}.`) : <NotHeld why="No hour of the forecast is held." />}
          note={low ? `${LABEL}, ${low.hour.label}` : undefined} />
      </div>
      <ChartFrame title={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()}: ${dayWords(ser.target_day)}`}
        tip={<> <Hint words="source" why={src} />{band ? <>, <Hint words="band" why={`${ser.band ?? index.band_rule ?? "The band's rule is not in the file."}${ser.band_coverage_pct !== null && ser.band_coverage_pct !== undefined ? ` Of the past hours scored, ${ser.band_coverage_pct}% fell inside their band.` : ""}`} /></> : null}{hasOp ? null : <>, <Hint words={`operator: ${ser.operator_held ?? "not held"}`} why={opWhy} /></>}</>}>
        <CategoryChart id={`fc-tomorrow-${slot.mark}`} x={hours.map((h) => h.label)} series={chartSeries(hours, false)} unit={unit} zero={false} height={280} band={band} notes={hourNotes(hours, unit, tz)}
          label={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, by the hour of the place's clock (${tz})${hasOp ? `, with the operator's own forecast` : ""}`} />
      </ChartFrame>
      <details className="mb-6 border-b border-rule py-2" data-fc-hours-fold={slot.mark}>
        <summary className="cursor-pointer text-sm">Hour by hour, {dayWords(ser.target_day)}</summary>
        <div className="pt-2">
          <ToolTable minWidth={420} caption={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, hour by hour, ${unit}`}
            head={["Hour", LABEL, "Band, low", "Band, high", OPERATOR]}
            rows={hours.map((h) => ({ key: h.ts, cells: [<span key="h" title={`The hour beginning ${localWords(h.ts, tz)} (${utcWords(h.ts)})`} className="cursor-help">{h.label}</span>,
              h.erw !== null ? fig(h, "erw", h.erw, `h${h.i}|erw`, "") : <NotHeld key="e" why="No forecast is held for this hour." />,
              h.lo !== null ? fig(h, "lo", h.lo, `h${h.i}|lo`, "The band's low.") : <NotHeld key="l" why="No band is held for this hour." />,
              h.hi !== null ? fig(h, "hi", h.hi, `h${h.i}|hi`, "The band's high.") : <NotHeld key="u" why="No band is held for this hour." />,
              h.operator !== null ? fig(h, "operator", h.operator, `h${h.i}|operator`, "The operator's own forecast.") : <NotHeld key="o" words={ser.operator_held ?? "not held"} why={opWhy} />] }))} />
        </div>
      </details>
    </div>
  );
}

/** A past day for one place: the forecast made for it beside what happened, and the day's mean absolute errors. */
function PastDay({ slot, s, index, scores, asked }: { slot: Slot; s: SeriesKey; index: PredictIndex; scores: ScoresFile | null; asked: string | null }) {
  const ser = slot.file?.series?.[s];
  const k = `${slot.mark}|${s}`;
  if (!isShown(slot.file, ser) || !ser) {
    const of = ser ?? slot.place.series?.[s];
    const example = slot.file?.example === true || index.example === true;
    return <div className="min-w-0" data-fc-day={slot.mark}><PlaceHead slot={slot} s={s} index={index} /><Blank what={`A past day, ${placeWords(slot.place)}`} words={blankWords(of?.status, example)} why={blankWhy(of, example)} k={`day|${k}`} /></div>;
  }
  const days = daysOf(ser);
  const day = asked && days.includes(asked) ? asked : asked ? null : defaultDay(ser);
  if (!day) {
    const span = days.length ? `The file holds ${days[days.length - 1]} to ${days[0]} of this place's clock.` : "The file holds no past day yet.";
    return <div className="min-w-0" data-fc-day={slot.mark}><PlaceHead slot={slot} s={s} index={index} /><Blank what={`${asked ?? "A past day"}, ${placeWords(slot.place)}`} words="not held" why={span} k={`day|${k}`} /></div>;
  }
  const hours = historyOf(ser).filter((h) => h.day === day);
  const unit = ser.unit, tz = slot.place.time;
  const src = sourceWords(slot, ser, s, scores);
  const band = hours.some((h) => h.lo !== null && h.hi !== null) ? { lo: hours.map((h) => h.lo), hi: hours.map((h) => h.hi), name: "Band" } : undefined;
  const sc = dayScore(hours);
  const kinds = [...new Set(hours.map((h) => h.kind).filter(Boolean))];
  const made = hours.find((h) => h.made)?.made ?? null;
  const madeWords = `The forecast drawn was made ${made ? localWords(made, tz) : "at an hour the file does not say"}${kinds.length ? ` (${kinds.map((x) => (x === "live" ? "on the day, and never overwritten" : "by the walk-forward backtest, from a model fit only on days before it")).join("; ")})` : ""}.`;
  return (
    <div className="min-w-0" data-fc-day={slot.mark} data-fc-day-of={day} data-fc-hours={hours.length}>
      <PlaceHead slot={slot} s={s} index={index} />
      <ChartFrame title={`${dayWords(day)}: ${LABEL} and what happened`} tip={<> <Hint words="source" why={`${madeWords} ${src}`} /></>}>
        <CategoryChart id={`fc-day-${slot.mark}`} x={hours.map((h) => h.label)} series={chartSeries(hours, true)} unit={unit} zero={false} height={280} band={band} notes={hourNotes(hours, unit, tz)}
          label={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)} on ${dayWords(day)}, beside what happened, by the hour of the place's clock (${tz})`} />
      </ChartFrame>
      <ToolTable minWidth={420} caption={`${placeWords(slot.place)}, ${dayWords(day)}: each method's mean absolute error over the day, ${unit}`}
        head={[`${day}`, ...FOUR.map((m) => <span key={m} title={methodWhat(scores, m) || undefined} className={methodWhat(scores, m) ? "cursor-help" : undefined}>{methodWords(m)}</span>)]}
        rows={[{ key: "mae", cells: [<span key="w" className="cursor-help" title={sc ? `The mean of each hour's absolute miss, over the ${sc.hours} hours of the day where what happened and every method drawn here are held (the same hours for all, as the report card is made). Computed by the page from the file's rows of ${day}.` : "No hour of the day holds what happened and a forecast."}>Mean absolute error, {unit}</span>,
          ...FOUR.map((m) => (sc && sc.mae[m] !== undefined
            ? <span key={m} data-n={`fc|${k}|day|${m}`} data-fc-day-hours={sc.hours} title={`Over ${sc.hours} hours of ${day}.`}>{valueWords(sc.mae[m], unit)}</span>
            : <NotHeld key={m} words={m === "operator" && ser.operator_held ? ser.operator_held : "not held"} why={m === "operator" && ser.operator_held ? `${OPERATOR}: ${ser.operator_held}.` : "No forecast of this method is held for the day, or what happened is not held."} />))] }]} />
    </div>
  );
}

/** One cell of a score table: the figure with its key into the score file, or a blank with the file's reason. */
function ScoreCell({ c, metric, unit, mcol, what }: { c: Score | undefined; metric: Metric; unit: string; mcol: number; what: string }) {
  const v = c ? c[metric] : null;
  if (!c || v === null) {
    const held = c?.held ?? null;
    const words = held === "license needed" ? "license needed" : held === "not published" ? "not published" : "not held";
    return <NotHeld words={words} why={held ? `${what}: ${held}.` : `${what}: no score is in the file for this method and cut${metric === "mape" ? " (a percent error is not defined where the value is at or near zero)" : ""}.`} />;
  }
  return <Num check={pfKey("predict/scores.json", ["rows", c.i, mcol])} raw={v} source={`${what}: ${METRIC_WORDS[metric].toLowerCase()}, ${metricUnit(metric, unit)}${c.hours !== null ? `, over ${c.hours.toLocaleString("en-US")} hours` : ""}. Every method of this row is scored on the same hours. site/data/predict/scores.json, row ${c.i}, column ${metric}.`}>{scoreWords(v, metric, unit)}</Num>;
}

const CUT_TITLE: Record<string, string> = { all: "Every hour scored", top10: "The ten highest-demand days", spike: "Price spikes (hours above the grid's 99th percentile)" };

/** The report card of one place: the last 30 days and the backtest, then by month, by hour of day, and the other cuts. */
function ReportCard({ slot, s, index, scores, metric }: { slot: Slot; s: SeriesKey; index: PredictIndex; scores: ScoresFile | null; metric: Metric }) {
  const ser = slot.file?.series?.[s];
  const k = `${slot.mark}|${s}`;
  if (!isShown(slot.file, ser) || !ser) {
    const of = ser ?? slot.place.series?.[s];
    const example = slot.file?.example === true || index.example === true;
    return <div className="min-w-0" data-fc-record={slot.mark}><PlaceHead slot={slot} s={s} index={index} /><Blank what={`The record, ${placeWords(slot.place)}`} words={blankWords(of?.status, example)} why={blankWhy(of, example)} k={`record|${k}`} /></div>;
  }
  const unit = ser.unit, file = fileOf(slot);
  const methods = methodsOf(scores);
  const mu = metricUnit(metric, unit);
  const head = (first: string) => [first, "Hours", ...methods.map((m) => <span key={m} title={methodWhat(scores, m) || undefined} className={methodWhat(scores, m) ? "cursor-help" : undefined}>{methodWords(m)}</span>)];
  const cuts = scoresOf(scores, slot.place.place, s);
  const mcol = scores ? scores.rows_columns.indexOf(metric) : -1;
  const table = (cut: string, first: string, name: (key: string) => ReactNode, caption: string) => {
    const g = cuts.get(cut);
    if (!g) return <p className="mb-4 text-sm"><NotHeld words={`${caption}: not held`} why={scores ? `The score file holds no row of the cut "${cut}" for this place and series.` : "The score file (site/data/predict/scores.json) is not on the site."} /></p>;
    return (
      <div className="mb-5" data-fc-cut={`${slot.mark}|${cut}`}>
        <h4 className="mb-1 text-sm font-semibold">{caption}, {mu}</h4>
        <ToolTable minWidth={520} caption={`${placeWords(slot.place)}, ${SERIES_WORDS[s].toLowerCase()}: ${METRIC_WORDS[metric].toLowerCase()} ${caption.toLowerCase()}, ${mu}`} head={head(first)}
          rows={orderedKeys(cut, g.keys).map((key) => {
            const hrs = rowHours(g.cells, key, methods);
            return { key, cells: [name(key), hrs !== null ? hrs.toLocaleString("en-US") : <NotHeld key="h" why="No count of hours is in the file for this row." />,
              ...methods.map((m) => <ScoreCell key={m} c={g.cells.get(`${key}|${m}`)} metric={metric} unit={unit} mcol={mcol} what={`${methodWords(m)}, ${placeWords(slot.place)}, ${cut === "all" ? "every hour scored" : `${cut} ${key}`}`} />)] };
          })} />
      </div>
    );
  };
  const other = ["all", "top10", "spike", "event"].filter((c) => cuts.has(c));
  const parts: [string, string][] = [["last_30_days", "The last 30 days"], ["backtest", "The backtest"]];
  return (
    <div className="min-w-0" data-fc-record={slot.mark}>
      <PlaceHead slot={slot} s={s} index={index} />
      <div className="mb-5" data-fc-summary={slot.mark}>
        <h4 className="mb-1 text-sm font-semibold">The last 30 days and the whole backtest, {mu}</h4>
        <ToolTable minWidth={520} caption={`${placeWords(slot.place)}, ${SERIES_WORDS[s].toLowerCase()}: ${METRIC_WORDS[metric].toLowerCase()} over the last 30 days and over the backtest, ${mu}`}
          head={["Span", "Hours", ...FOUR.map((m) => <span key={m} title={methodWhat(scores, m) || undefined} className={methodWhat(scores, m) ? "cursor-help" : undefined}>{methodWords(m)}</span>)]}
          rows={parts.map(([part, words]) => {
            const p = ser.summary?.[part as "backtest"];
            const span = p?.first_day && p?.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say";
            return { key: part, cells: [<span key="w" title={span} className="cursor-help">{words}</span>,
              p?.hours !== null && p?.hours !== undefined ? <Num key="h" check={pfKey(file, ["series", s, "summary", part, "hours"])} raw={p.hours} source={`The hours scored, ${span}.`}>{p.hours.toLocaleString("en-US")}</Num> : <NotHeld key="h" why="No count of hours is in the file." />,
              ...FOUR.map((m) => {
                const v = p?.[metric]?.[m];
                return v === null || v === undefined
                  ? <NotHeld key={m} words={m === "operator" && ser.operator_held ? ser.operator_held : "not held"} why={m === "operator" && ser.operator_held ? `${OPERATOR}: ${ser.operator_held}.` : "No score is in the file for this method and span."} />
                  : <Num key={m} check={pfKey(file, ["series", s, "summary", part, metric, m])} raw={v} source={`${methodWords(m)}, ${words.toLowerCase()} (${span}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
              })] };
          })} />
      </div>
      {table("month", "Month", (key) => monthWords(key), "By month")}
      {table("hour", "Hour", (key) => <span title={`The hour from ${hourWords(key)} of the place's clock (${slot.place.time})`} className="cursor-help">{hourWords(key)}</span>, "By hour of day")}
      {other.length ? (
        <div className="mb-5" data-fc-cut={`${slot.mark}|other`}>
          <h4 className="mb-1 text-sm font-semibold">Every hour, the highest-demand days and the events, {mu}</h4>
          <ToolTable minWidth={520} caption={`${placeWords(slot.place)}, ${SERIES_WORDS[s].toLowerCase()}: ${METRIC_WORDS[metric].toLowerCase()} over every hour scored, the ten highest-demand days, the price spikes and each event, ${mu}`} head={head("Hours scored")}
            rows={other.flatMap((cut) => {
              const g = cuts.get(cut)!;
              return g.keys.map((key) => {
                const hrs = rowHours(g.cells, key, methods);
                const words = cut === "event" ? `Event: ${key.replace(/_/g, " ")}` : CUT_TITLE[cut] ?? cut;
                return { key: `${cut}|${key}`, cells: [<span key="w" title={scores?.cuts?.[cut]} className={scores?.cuts?.[cut] ? "cursor-help" : undefined}>{words}</span>,
                  hrs !== null ? hrs.toLocaleString("en-US") : <NotHeld key="h" why="No count of hours is in the file for this row." />,
                  ...methods.map((m) => <ScoreCell key={m} c={g.cells.get(`${key}|${m}`)} metric={metric} unit={unit} mcol={mcol} what={`${methodWords(m)}, ${placeWords(slot.place)}, ${words.toLowerCase()}`} />)] };
              });
            })} />
        </div>
      ) : null}
    </div>
  );
}

/** Every place at once: one row a place in the index's own order, every method, over every hour scored. */
function AllPlaces({ index, scores, s, metric, chosen }: { index: PredictIndex; scores: ScoresFile | null; s: SeriesKey; metric: Metric; chosen: string[] }) {
  const methods = methodsOf(scores);
  const mcol = scores ? scores.rows_columns.indexOf(metric) : -1;
  const unit = s === "price" ? "USD/MWh" : "MW";
  const mu = metricUnit(metric, unit);
  const example = index.example === true || scores?.example === true;
  return (
    <div data-fc-all={index.places.length}>
      <ToolTable minWidth={720} caption={`Every place: ${METRIC_WORDS[metric].toLowerCase()} of each method's forecast of ${SERIES_WORDS[s].toLowerCase()} over every hour scored, ${mu}`}
        head={["Place", "Hours", ...methods.map((m) => <span key={m} title={methodWhat(scores, m) || undefined} className={methodWhat(scores, m) ? "cursor-help" : undefined}>{methodWords(m)}</span>)]}
        rows={index.places.map((p) => {
          const ix = p.series?.[s];
          const name = <SiteLink key="n" href={hrefOf({ a: p.place, b: null, s, day: null, m: null })}>{placeWords(p)}</SiteLink>;
          if (example || !ix || ix.status !== "shown") return { key: p.place, highlight: chosen.includes(p.place), cells: [name], wide: <span className="cursor-help" title={blankWhy(ix, example)} data-fc-all-blank={p.place}>{blankWords(ix?.status, example)}</span> };
          const g = scoresOf(scores, p.place, s).get("all");
          const hrs = g ? rowHours(g.cells, "", methods) : null;
          return { key: p.place, highlight: chosen.includes(p.place), cells: [name, hrs !== null ? hrs.toLocaleString("en-US") : <NotHeld key="h" why="No score over every hour is in the file for this place." />,
            ...methods.map((m) => <ScoreCell key={m} c={g?.cells.get(`|${m}`)} metric={metric} unit={unit} mcol={mcol} what={`${methodWords(m)}, ${placeWords(p)}, every hour scored`} />)] };
        })} />
    </div>
  );
}

/** How /demand's country view writes a place in its address: a region by its code, an authority as "ba-<code>". */
const demandKey = (p: IndexPlace) => (p.kind === "ba" ? `ba-${p.eia930.toLowerCase()}` : p.eia930.toLowerCase());

export function ForecastView({ query }: { query: Raw }) {
  const index = predictIndex();
  const scores = predictScores();
  const q: Query = queryOf(query, index);
  const metric = metricOf(q);
  const places = index?.places ?? [];
  const slots: Slot[] = [q.a, q.b].map((id, i) => {
    const place = places.find((p) => p.place === id);
    return place ? { mark: i ? "b" : "a", place, file: predictPlace(place) } as Slot : null;
  }).filter((x): x is Slot => x !== null);
  const two = slots.length > 1 ? "grid gap-6 xl:grid-cols-2" : "";
  const tables = [...new Set(slots.flatMap((x) => x.file?.tables ?? []))];
  const built = index?.built ? index.built.slice(0, 10) : null;
  const lead = (
    <>The ERW&apos;s own day-ahead forecast of demand and price for each region and balancing authority, the operator&apos;s own forecast beside it, and how each has scored against what happened.{" "}
      <Hint words="What it is" why={`${LABEL} is a model's output (the warehouse's tier "derived"), never a published or official figure. The operator's forecast is the operator's own, as published. The page says what was forecast and how it scored, and nothing on what to do.`} />
      {index?.made_rule ? <>, <Hint words="when it is made" why={index.made_rule} /></> : null}
      {index?.band_rule ? <>, <Hint words="the band" why={index.band_rule} /></> : null}
      {index?.choice_rule ? <>, <Hint words="how a method is chosen" why={index.choice_rule} /></> : null}.</>
  );
  const header = (
    <ToolHeader title={LABEL} lead={lead}
      under={<p className="mt-2 text-xs text-muted" data-license-line="1">{index ? <>{LABEL}: a model&apos;s output, tier derived. {built ? `Files built ${built}.` : "No forecast has been written yet."}</> : "The forecast's files are not on the site yet."}</p>} />
  );
  if (!index || !slots.length) {
    return (
      <div data-forecast="1" data-fc-state="no-files">
        {header}
        <Blank what={LABEL} words="not built yet" why="The forecast's page files (site/data/predict/index.json and one file a place) are not on the site yet: the data machine's forecast build writes them. Nothing is drawn until they are." k="files" />
      </div>
    );
  }
  const first = slots[0];
  const serA = first.file?.series?.[q.s];
  const days = isShown(first.file, serA) && serA ? daysOf(serA) : [];
  const options = places.map((p) => ({ value: p.place, label: placeWords(p) }));
  return (
    <div data-forecast="1" data-fc-state={index.example === true ? "example" : "files"} data-fc-series={q.s} data-fc-metric={metric}>
      {header}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
        <div className="min-w-0">
          <InputPanel title="Choices" reset={{ href: "/forecast", defaults: "Texas alone, demand, the newest past day, percent error" }}>
            <form method="get" action="/forecast" className="flex flex-col gap-3 text-sm [&_label]:min-w-0 [&_label]:max-w-full [&_select]:w-full [&_select]:max-w-full" data-fc-form="1">
              <AutoSubmitSelect name="a" value={first.place.place} options={options} label="Place A" />
              <AutoSubmitSelect name="b" value={q.b ?? NONE} options={[{ value: NONE, label: "None" }, ...options.filter((o) => o.value !== first.place.place)]} label="Place B, side by side" />
              <AutoSubmitSelect name="s" value={q.s} options={SERIES.map((x) => ({ value: x, label: SERIES_WORDS[x] }))} label="Forecast of" />
              <AutoSubmitSelect name="day" value={q.day ?? ""} options={[{ value: "", label: "The newest day held" }, ...(q.day && !days.includes(q.day) ? [{ value: q.day, label: `${q.day} (not held)` }] : []), ...days.map((d) => ({ value: d, label: dayWords(d) }))]} label="Past day" />
              <AutoSubmitSelect name="m" value={metric} options={[{ value: "mape", label: "Percent error (MAPE)" }, { value: "mae", label: `Error in ${q.s === "price" ? "USD/MWh" : "MW"} (MAE)` }]} label="Score shown" />
              <button type="submit" className="self-start border border-rule bg-white px-3 py-1 text-sm">Show</button>
            </form>
          </InputPanel>
        </div>
        <div className="min-w-0">
          <ToolTabs label="Forecast of" items={SERIES.map((x) => ({ key: x, label: SERIES_WORDS[x], href: hrefOf(q, { s: x, m: null, day: null }), on: q.s === x }))} />
          <ToolSection title="Tomorrow" id="tomorrow">
            <div className={two}>{slots.map((x) => <Tomorrow key={x.mark} slot={x} s={q.s} index={index} scores={scores} />)}</div>
          </ToolSection>
          <ToolSection title="How it has done" id="record">
            <div className={two}>{slots.map((x) => <PastDay key={x.mark} slot={x} s={q.s} index={index} scores={scores} asked={q.day} />)}</div>
            <div className={`mt-6 ${two}`}>{slots.map((x) => <ReportCard key={x.mark} slot={x} s={q.s} index={index} scores={scores} metric={metric} />)}</div>
          </ToolSection>
          <ToolSection title="Every place" id="places">
            <AllPlaces index={index} scores={scores} s={q.s} metric={metric} chosen={slots.map((x) => x.place.place)} />
          </ToolSection>
          <ToolSection title="Downloads" id="downloads">
            <ul className="list-none space-y-1 p-0 text-sm" data-fc-downloads="1">
              {slots.map((x) => (
                <li key={x.mark} data-fc-download={x.place.place}>{placeWords(x.place)}, hour by hour (tomorrow and every past day held, both series):{" "}
                  <a href={`/forecast/rows?place=${x.place.place}`} download data-download="csv">CSV</a>,{" "}
                  <a href={`/forecast/rows/python?place=${x.place.place}`} download data-download="python">Python</a>,{" "}
                  <a href={`/forecast/rows/stata?place=${x.place.place}`} download data-download="stata">Stata</a></li>
              ))}
              <li data-fc-download="scores">The report card, every place, method and cut:{" "}
                <a href="/forecast/scores" download data-download="csv">CSV</a>,{" "}
                <a href="/forecast/scores/python" download data-download="python">Python</a>,{" "}
                <a href="/forecast/scores/stata" download data-download="stata">Stata</a></li>
              {q.s === "demand" ? slots.map((x) => (
                <li key={`d${x.mark}`} data-fc-operator-record={x.place.place}><SiteLink href={`/demand?view=country&a=${demandKey(x.place)}#forecast`}>{placeWords(x.place)}: the operator&apos;s own forecast against demand, every year held</SiteLink></li>
              )) : null}
            </ul>
          </ToolSection>
          {tables.length ? <SourceLine tables={tables} note={index.method_notes ? <>Methods: {Object.entries(index.method_notes).map(([name, doc], i) => <span key={name}>{i ? ", " : ""}<a href={`/data/methods/${doc.replace(/^docs\/methods\//, "").replace(/\.md$/, "")}`}>{name}</a></span>)}.</> : undefined} /> : null}
        </div>
      </div>
    </div>
  );
}

/** The tables the chosen places' files were built from, for the page's table downloads. */
export function tablesOf(query: Raw): string[] {
  const index = predictIndex();
  const q = queryOf(query, index);
  return [...new Set([q.a, q.b].flatMap((id) => predictPlace(index?.places.find((p) => p.place === id))?.tables ?? []))];
}
