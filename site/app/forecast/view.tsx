// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): what /forecast draws, as one plain component
// so that a test can draw it to HTML without a build (the page adds the brand's frame and the table downloads).
//
// Tomorrow: for a chosen place, the ERW forecast by hour with its band, and the operator's own forecast for the same
// hours where the file holds one; a tab for price. How it has done: any past day beside what happened, and the report
// card (the ERW, the operator, the same hour yesterday, the same hour a week ago) by month, by hour of day and for all
// places at once. Two places side by side: their charts in two columns, their scores as columns of one table. The hours
// and places where the ERW forecast lost are drawn exactly as the ones where it won: one table, one weight, the months
// in the calendar's order, the hours in the clock's, the places in the index's.
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
// session 10407 (the browser read of 26 November, row FC1): the mark that opens on a hover, a tap and the keyboard
import { Tip } from "@/components/tool/ToolPage";
import { scrollRegion } from "@/lib/cells";
import { pfKey } from "@/lib/pagefile";
import {
  CUT_WORDS, FOUR, LABEL, METRIC_WORDS, NONE, OTHER_CUTS, SERIES, SERIES_WORDS, blankWhy, blankWords, dayScore, dayWords, daysOf, defaultDay, eventHref, extreme, historyOf, hourWords, hrefOf, isShown,
  localWords, methodShort, methodWhat, methodWords, methodsOf, metricDefault, metricOf, metricUnit, monthWords, orderedKeys, placeWords, queryOf, rowHours, scoreWords, scoresOf, shortHeld, tomorrowOf, utcWords, valueWords,
  type Hour, type IndexPlace, type Metric, type PlaceFile, type PlaceSeries, type PredictIndex, type Query, type Score, type ScoresFile, type SeriesKey,
} from "@/lib/predict";
// session 10405 (chain 720, part E): the day's peak and the days after tomorrow (the contract's changes of session 10601)
import { PEAK_HOURS, PEAK_SPANS, aheadDays, aheadOf, madeOffRule, pctWords, type AheadFile } from "@/lib/predict";
// session 10406 (chain 720, part E): the separate line "with the weather known" (not a forecast)
import { WEATHER_LABEL, WEATHER_METHODS, WEATHER_SPANS } from "@/lib/predict";
import { predictAhead, predictIndex, predictLedger, predictPlace, predictScores } from "@/lib/predictfiles";
// session 10409 (chain 720, part E): the views of what the files gained on 27 November 2026 (app/forecast/lines.tsx)
import { predictRtPrice, predictWindSolar } from "@/lib/predictfiles";
import { plainMethods } from "@/lib/predict";
import { RealTimeSection } from "./realtime";
import { BandCheck, FilingCheck, NetDemand, WeatherForecastLine, WindSolarDay } from "./lines";
// session 10410: wind and solar by month and hour, and the downloads of the new lines
import { WindSolarCuts } from "./lines";
import { rtOf } from "./realtime";
// session 10411 (the contract's lines of session 10603): the place a wind and solar entry is shown for
import { PRICE_CUT_WORDS, windSolarFor } from "@/lib/predictlines";
import { predictPriceHubs } from "@/lib/predictfiles";
import { MoreHubsSection } from "./realtime";

type Raw = Record<string, string | string[] | undefined>;
type Slot = { mark: "a" | "b"; place: IndexPlace; file: PlaceFile | null };
const OPERATOR = "Operator's forecast";
const ACTUAL = "What happened";
const BAND = { label: "Band of the ERW forecast", color: "var(--color-rule)" };
const fileOf = (slot: Slot) => `predict/${slot.place.file}`;

/** A blank the size of what it stands for: the words on its face, the file's reason on hover. */
function Blank({ what, words, why, k }: { what: string; words: string; why: string; k: string }) {
  return (
    <div className="my-2 flex min-h-24 cursor-help items-center justify-center border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" title={why} data-fc-blank={k}>
      {what}: {words}
    </div>
  );
}
/** Session 11402 (audit of /forecast, finding 2): the newest target day the ledger of a series holds for a place, or
 *  null. When it is later than the place file's own day, the files are behind the forecasts already made, and the day
 *  drawn under "Tomorrow" may be one that has passed: the page says so rather than draw it as tomorrow unremarked. */
function ledgerNewest(series: SeriesKey, place: string): string | null {
  const text = predictLedger(series);
  if (!text) return null;
  const lines = text.split(/\r?\n/).filter((x) => x && !x.startsWith("#"));
  const head = (lines.shift() ?? "").split(",");
  const at = { s: head.indexOf("series"), p: head.indexOf("place"), d: head.indexOf("target_day") };
  if (at.p < 0 || at.d < 0) return null;
  let best: string | null = null;
  for (const line of lines) {
    const c = line.split(",");
    if ((at.s < 0 || c[at.s] === series) && c[at.p] === place && /^\d{4}-\d{2}-\d{2}$/.test(c[at.d] ?? "") && (!best || c[at.d] > best)) best = c[at.d];
  }
  return best;
}
const NotHeld = ({ words = "not held", why }: { words?: string; why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">{words}</span>;
/** A method's name at the head of a column: short, with what the score file says of it on hover. */
const MethodHead = ({ m, scores }: { m: string; scores: ScoresFile | null }) => <span title={`${methodWords(m)}${methodWhat(scores, m) ? `: ${methodWhat(scores, m)}` : ""}`} className="cursor-help">{methodShort(m)}</span>;

/** Where the model's line and the operator's come from, for a chart's hover. */
function sourceWords(slot: Slot, ser: PlaceSeries, s: SeriesKey, scores: ScoresFile | null): string {
  const made = ser.made_utc ? `made ${localWords(ser.made_utc, slot.place.time)} (${utcWords(ser.made_utc)})` : "the hour it was made is not in the file";
  const op = s === "price" ? "No operator publishes a price forecast." : `${OPERATOR}: ${methodWhat(scores, "operator") || "the operator's own day-ahead forecast, as the warehouse holds it"}.`;
  return `${LABEL}: a model's output (tier derived), not a published figure; ${made}; method: ${methodWords(ser.method ?? "not said")}. ${op} Built from the ERW's tables ${(slot.file?.tables ?? []).join(", ") || "(none named)"}; method note ${ser.method_note}.`;
}

/** The place's heading: its name, and on hover the hour the forecast was made and the method the place uses. */
/** `tip` (session 10407; the browser read's row FC1): the same words behind a mark that a finger and the keyboard open
 *  too, beside the name. The name's own hover answers a mouse alone, so on a phone or with the keyboard a reader could
 *  not learn when the forecast was made or how old the figures it rests on are. Given once a place, where tomorrow's
 *  forecast is drawn; the value is the mark's id on the page. */
function PlaceHead({ slot, s, index, tip }: { slot: Slot; s: SeriesKey; index: PredictIndex; tip?: string }) {
  const ser = slot.file?.series?.[s];
  const shown = isShown(slot.file, ser);
  const why = shown && ser
    ? `${LABEL} for ${dayWords(ser.target_day)}: made ${localWords(ser.made_utc, slot.place.time) || "at an hour the file does not say"} (${utcWords(ser.made_utc)}), from the place's own figures through ${localWords(ser.inputs_through_utc, slot.place.time) || "an hour the file does not say"}${typeof ser.horizon_days === "number" ? `, ${ser.horizon_days} days before the day forecast (2 is the day-ahead forecast as the method note defines it; more when the warehouse's series is behind)` : ""}. Method: ${methodWords(ser.method ?? "not said")}, last fit ${ser.fit_day ?? "on a day the file does not say"}.${index.made_rule ? ` The rule: ${index.made_rule}${madeOffRule(ser.made_utc, index.made_rule, s) ? ` ${madeOffRule(ser.made_utc, index.made_rule, s)}` : ""}` : ""}${index.choice_rule ? ` ${index.choice_rule}` : ""}${ser.tomorrow_from ? ` Kept as first made: ${plainMethods(ser.tomorrow_from)}.` : ""}`
    : blankWhy(ser ?? slot.place.series?.[s], slot.file?.example === true || index.example === true);
  return (
    <h3 className="mb-2 font-serif text-xl text-accent" data-fc-place={slot.mark}>
      <span className="cursor-help border-b border-dotted border-muted" title={why}>{placeWords(slot.place)}</span>
      {tip ? <span className="font-sans" data-fc-made={slot.mark}><Tip id={tip} label={shown ? `when the ${LABEL} for ${placeWords(slot.place)} was made, from which figures and by which method` : `why nothing is drawn for ${placeWords(slot.place)}`}>{why}</Tip></span> : null}
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
/** The band between the low and the high, drawn with no name on the plot (a name at its right edge stands on the
 *  line's own, which runs through the band's middle): the chart's legend names it. */
const bandOf = (hours: Hour[]) => (hours.some((h) => h.lo !== null && h.hi !== null) ? { lo: hours.map((h) => h.lo), hi: hours.map((h) => h.hi), name: "" } : undefined);

/** Tomorrow for one place: three figures, the chart with its band, and the hours as a table. */
function Tomorrow({ slot, s, index, scores }: { slot: Slot; s: SeriesKey; index: PredictIndex; scores: ScoresFile | null }) {
  const ser = slot.file?.series?.[s];
  const k = `${slot.mark}|${s}`;
  if (!isShown(slot.file, ser) || !ser) {
    const of = ser ?? slot.place.series?.[s];
    const example = slot.file?.example === true || index.example === true;
    return (
      <div className="min-w-0" data-fc-tomorrow={slot.mark} data-fc-shown="0">
        <PlaceHead slot={slot} s={s} index={index} tip={`fc-made-${slot.mark}`} />
        <Blank what={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()}, ${placeWords(slot.place)}`} words={blankWords(of?.status, example)} why={blankWhy(of, example)} k={`tomorrow|${k}`} />
      </div>
    );
  }
  const hours = tomorrowOf(ser);
  if (!hours.some((x) => x.erw !== null)) {
    // a shown series whose target day holds no forecast (the contract's `tomorrow_held`): the blank says why
    return (
      <div className="min-w-0" data-fc-tomorrow={slot.mark} data-fc-shown="0">
        <PlaceHead slot={slot} s={s} index={index} tip={`fc-made-${slot.mark}`} />
        <Blank what={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()}, ${placeWords(slot.place)}${ser.target_day ? `, ${dayWords(ser.target_day)}` : ""}`} words={shortHeld(ser.tomorrow_held)} why={ser.tomorrow_held ?? "The file holds no forecast for the day forecast now, and does not say why."} k={`tomorrow|${k}`} />
      </div>
    );
  }
  const unit = ser.unit, tz = slot.place.time, file = fileOf(slot);
  const col = (n: string) => ser.tomorrow_columns.indexOf(n);
  const src = sourceWords(slot, ser, s, scores);
  const top = extreme(hours, "erw"), low = extreme(hours, "erw", true);
  const opAtTop = top ? top.hour.operator : null;
  const hasOp = hours.some((h) => h.operator !== null);
  const opWhy = ser.operator_held ? `${OPERATOR}: ${ser.operator_held}.` : `${OPERATOR}: not in the file for these hours yet (an operator's forecast is drawn once it is published and held).`;
  const fig = (h: Hour, c: string, v: number, key: string, what: string) =>
    <Num check={pfKey(file, ["series", s, "tomorrow", h.i, col(c)])} raw={v} source={`${what} ${src}`}><span data-n={`fc|${k}|${key}`}>{valueWords(v, unit)}</span></Num>;
  const band = bandOf(hours);
  const none = (why: string, words?: string) => <span className="font-sans text-base"><NotHeld words={words} why={why} /></span>;
  const newer = ser.target_day ? ledgerNewest(s, slot.place.place) : null;
  return (
    <div className="min-w-0" data-fc-tomorrow={slot.mark} data-fc-shown="1" data-fc-hours={hours.length}>
      <PlaceHead slot={slot} s={s} index={index} tip={`fc-made-${slot.mark}`} />
      {newer && ser.target_day && newer > ser.target_day ? (
        <p className="mb-2 text-sm" data-fc-behind={slot.mark}>The ledger already holds a newer {LABEL} for this place, for {dayWords(newer)}: these files{index.built ? `, built ${index.built.slice(0, 10)},` : ""} are behind it, and the day drawn here, {dayWords(ser.target_day)}, is the newest they hold.</p>
      ) : null}
      <div className="mb-4 grid gap-4 sm:grid-cols-3">
        <HeadlineNumber label="Highest hour" unit={top ? unit : undefined}
          value={top ? fig(top.hour, "erw", top.v, "top", `The highest hour of the ${LABEL}, the hour beginning ${localWords(top.hour.ts, tz)}.`) : none("No hour of the forecast is held.")}
          note={top ? `${LABEL}, ${top.hour.label}` : undefined} />
        <HeadlineNumber label="Operator, same hour" unit={opAtTop !== null ? unit : undefined}
          value={top && opAtTop !== null ? fig(top.hour, "operator", opAtTop, "optop", `The operator's own forecast for the hour beginning ${localWords(top.hour.ts, tz)}.`) : none(opWhy, shortHeld(ser.operator_held))}
          note={top && opAtTop !== null ? `${OPERATOR}, ${top.hour.label}` : undefined} />
        <HeadlineNumber label="Lowest hour" unit={low ? unit : undefined}
          value={low ? fig(low.hour, "erw", low.v, "low", `The lowest hour of the ${LABEL}, the hour beginning ${localWords(low.hour.ts, tz)}.`) : none("No hour of the forecast is held.")}
          note={low ? `${LABEL}, ${low.hour.label}` : undefined} />
      </div>
      <ChartFrame title={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()}: ${dayWords(ser.target_day)}`} legend={band ? [BAND] : undefined}
        tip={<> <Hint words="source" why={src} />{band ? <>, <Hint words="band" why={`${ser.band ?? index.band_rule ?? "The band's rule is not in the file."}${ser.band_coverage_pct !== null && ser.band_coverage_pct !== undefined ? ` Of the past hours scored, ${ser.band_coverage_pct}% fell inside their band.` : ""}`} /></> : null}{hasOp ? null : <>, <Hint words={`operator: ${shortHeld(ser.operator_held)}`} why={opWhy} /></>}</>}>
        <CategoryChart id={`fc-tomorrow-${slot.mark}`} x={hours.map((h) => h.label)} series={chartSeries(hours, false)} unit={unit} zero={false} height={280} every={6} band={band} notes={hourNotes(hours, unit, tz)}
          label={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, by the hour of the place's clock (${tz})${hasOp ? `, with the operator's own forecast` : ""}`} />
      </ChartFrame>
      <details className="mb-6 border-b border-rule py-2" data-fc-hours-fold={slot.mark}>
        <summary className="cursor-pointer py-1 text-sm">Hour by hour, {dayWords(ser.target_day)}</summary>
        <div className="pt-2">
          <ToolTable minWidth={400} caption={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, hour by hour, ${unit}`}
            head={["Hour", LABEL, "Band, low", "Band, high", "Operator"]}
            rows={hours.map((h) => ({ key: h.ts, cells: [<span key="h" title={`The hour beginning ${localWords(h.ts, tz)} (${utcWords(h.ts)})`} className="cursor-help">{h.label}</span>,
              h.erw !== null ? fig(h, "erw", h.erw, `h${h.i}|erw`, "") : <NotHeld key="e" why="No forecast is held for this hour." />,
              h.lo !== null ? fig(h, "lo", h.lo, `h${h.i}|lo`, "The band's low.") : <NotHeld key="l" why="No band is held for this hour." />,
              h.hi !== null ? fig(h, "hi", h.hi, `h${h.i}|hi`, "The band's high.") : <NotHeld key="u" why="No band is held for this hour." />,
              h.operator !== null ? fig(h, "operator", h.operator, `h${h.i}|operator`, "The operator's own forecast.") : <NotHeld key="o" words={shortHeld(ser.operator_held)} why={opWhy} />] }))} />
        </div>
      </details>
    </div>
  );
}

/** "Sat 28 Nov" of a day, for a chart's axis. */
const shortDay = (day: string) => { const [wd, dd, mon] = dayWords(day).split(" "); return wd && dd && mon ? `${wd.slice(0, 3)} ${dd} ${mon}` : day; };

/** Session 10405 (chain 720, part E): the days after tomorrow for one place (site/data/predict/ahead.json): the ERW
 *  forecast of demand by hour with its band over the days the file shows, and one row a day: its highest and lowest
 *  hour, and how a forecast made that many days ahead has scored over the last two years, beside the same hour a week
 *  ago and the operator's own day-ahead forecast on the same hours. The file shows a day only where the forecast beat
 *  the week-ago hour; a day it does not show is a row that says so, with the file's reason on hover. Demand only. */
function DaysAhead({ slot, ahead, metric, scores, part }: { slot: Slot; ahead: AheadFile; metric: Metric; scores: ScoresFile | null; part: "chart" | "table" }) {
  const ser = slot.file?.series?.demand;
  // two places: their charts stand side by side, and under them each place's table at the page's full width (seven
  // columns do not fit half of it); the chart's part carries the block's marks, the table's part its own
  if (!isShown(slot.file, ser) || !ser) return part === "chart" ? <div className="min-w-0" data-fc-ahead={slot.mark} data-fc-ahead-days="0" /> : null;
  const entry = aheadOf(ahead, slot.place.place);
  const title = `${placeWords(slot.place)}: the days after ${ser.target_day ? dayWords(ser.target_day) : "tomorrow"}`;
  const days = entry ? aheadDays(entry.place, ser.target_day) : [];
  if (!entry || !days.length) {
    return part === "table" ? null : (
      <div className="min-w-0" data-fc-ahead={slot.mark} data-fc-ahead-days="0">
        <h4 className="mb-1 text-sm font-semibold">{title}</h4>
        <p className="mb-4 text-sm"><NotHeld why={entry ? "The file of the days ahead holds no day after this place's day forecast now." : "The file of the days ahead (site/data/predict/ahead.json) holds no entry for this place."} /></p>
      </div>
    );
  }
  const unit = ser.unit, tz = slot.place.time, file = "predict/ahead.json";
  const mu = metricUnit(metric, unit);
  const shown = days.filter((d) => d.hours.length);
  const hours = shown.flatMap((d) => d.hours.map((h) => ({ ...h, day: d.h.target_day })));
  const key = (d: (typeof days)[number], ...rest: (string | number)[]) => pfKey(file, ["places", entry.pi, "horizons", d.hi, ...rest]);
  const col = (d: (typeof days)[number], n: string) => d.h.forecast_columns.indexOf(n);
  const made = `${LABEL}: a model's output (tier derived), not a published figure${ahead.made_utc ? `; made ${localWords(ahead.made_utc, tz)} (${utcWords(ahead.made_utc)})` : ""}. ${ahead.what ?? ""} site/data/${file}.`;
  const band = hours.some((h) => h.lo !== null && h.hi !== null) ? { lo: hours.map((h) => h.lo), hi: hours.map((h) => h.hi), name: "" } : undefined;
  const span = (d: (typeof days)[number]) => `${d.h.horizon_days} days after the last whole day of demand read${entry.place.last_whole_day ? ` (${entry.place.last_whole_day})` : ""}`;
  const extremeCell = (d: (typeof days)[number], x: (typeof days)[number]["top"], what: string) => (x
    ? <span key={what} className="whitespace-nowrap"><Num check={key(d, "forecast", x.i, col(d, "erw"))} raw={x.v} source={`The ${what} hour of the ${LABEL} for ${dayWords(d.h.target_day)}, the hour beginning ${localWords(x.ts, tz)}, made ${span(d)}. ${made}`}>{valueWords(x.v, unit)}</Num> <span className="text-xs">at {hourWords(x.hour)}</span></span>
    : <NotHeld key={what} why="No hour of this day's forecast is held." />);
  const scoreCell = (d: (typeof days)[number], m: string, words: string) => {
    const v = d.h.last_2_years?.[metric]?.[m];
    return v === null || v === undefined
      ? <NotHeld key={m} why={`No score of ${words} at this horizon is in the file.`} />
      : <Num key={m} check={key(d, "last_2_years", metric, m)} raw={v} source={`${words}, a forecast made ${span(d)}: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}, over the last two years${typeof d.h.last_2_years?.hours === "number" ? ` (${d.h.last_2_years.hours.toLocaleString("en-US")} hours)` : ""}. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
  };
  if (part === "chart") return (
    <div className="min-w-0" data-fc-ahead={slot.mark} data-fc-ahead-days={days.length} data-fc-ahead-shown={shown.length}>
      <h4 className="mb-1 text-sm font-semibold">{title}</h4>
      {hours.length ? (
        <ChartFrame title={`${LABEL} of demand: ${dayWords(shown[0].h.target_day)} to ${dayWords(shown[shown.length - 1].h.target_day)}`} legend={band ? [BAND] : undefined}
          tip={<> <Hint words="source" why={made} />, <Hint words="which days are shown" why={ahead.what ?? "A day is shown only where, over the last two years, a forecast made that many days ahead beat the same hour a week ago."} /></>}>
          <CategoryChart id={`fc-ahead-${slot.mark}`} x={hours.map((h) => (h.hour === 0 ? shortDay(h.day).split(" ").slice(0, 2).join(" ") : `${shortDay(h.day)} ${h.label}`))} series={[{ name: LABEL, color: "accent", kind: "line", values: hours.map((h) => h.erw) }]} unit={unit} zero={false} height={240} every={24} band={band}
            notes={hours.map((h) => `Hour beginning ${localWords(h.ts, tz)}.${h.lo !== null && h.hi !== null ? ` Band: ${valueWords(h.lo, unit)} to ${valueWords(h.hi, unit)} ${unit}.` : ""}`)}
            label={`${LABEL} of demand for ${placeWords(slot.place)} over the ${shown.length} days after ${ser.target_day ? dayWords(ser.target_day) : "tomorrow"}, by the hour of the place's clock (${tz})`} />
        </ChartFrame>
      ) : null}
    </div>
  );
  return (
    <div className="mb-5 min-w-0" data-fc-ahead-table={slot.mark}>
      <ToolTable minWidth={600} caption={`${title}: the highest and lowest hour of the ${LABEL} for each day, and how a forecast made that many days ahead has scored over the last two years, ${mu}`}
        head={[<span key="d" className="cursor-help" title={`${title}. Each day's errors are those of a forecast made that many days ahead, over the last two years.`}>{placeWords(slot.place)}, day</span>,
          <span key="t" className="cursor-help" title={`The highest hour of the ${LABEL} for the day, in ${unit}, and the hour of the place's clock it begins.`}>Highest hour</span>,
          <span key="l" className="cursor-help" title={`The lowest hour of the ${LABEL} for the day, in ${unit}, and the hour it begins.`}>Lowest hour</span>,
          <span key="e" className="cursor-help" title={`${METRIC_WORDS[metric]} of a forecast made this many days ahead, over the last two years, ${mu}: the file's own method for the horizon.`}>Error, {mu}: {LABEL}</span>,
          <span key="w" className="cursor-help" title={`${methodWords("week_ago")}${methodWhat(scores, "week_ago") ? `: ${methodWhat(scores, "week_ago")}` : ""}. ${METRIC_WORDS[metric]} on the same hours, ${mu}.`}>Error, {mu}: {methodShort("week_ago").toLowerCase()}</span>,
          <span key="o" className="cursor-help" title={`The operator's own forecast made one day ahead: its mean absolute error on the same hours, in ${unit}. A forecast made one day ahead is set here beside one made several days ahead; the file holds no operator's forecast at these horizons, and no percent for this column.`}>Error, {unit}: operator, day-ahead</span>,
          <span key="b" className="cursor-help" title="Of the past hours scored at this horizon, the share that fell inside the forecast's band, in percent.">In band, %</span>]}
        rows={days.map((d) => {
          const name = <span key="d" className="cursor-help whitespace-nowrap" title={`${dayWords(d.h.target_day)}: a forecast made ${span(d)}. Method: ${methodWords(d.method)}.`}>{shortDay(d.h.target_day)}</span>;
          if (!d.h.shown || !d.hours.length) return { key: d.h.target_day, cells: [name], wide: <span className="cursor-help" title={d.h.held ?? "The file does not show this day, and does not say why."} data-fc-ahead-blank={d.h.target_day}>not shown</span> };
          const op = d.h.last_2_years?.operator_day_ahead_mae_same_hours, cov = d.h.band_coverage_pct;
          return { key: d.h.target_day, cells: [name, extremeCell(d, d.top, "highest"), extremeCell(d, d.low, "lowest"), scoreCell(d, d.method, LABEL), scoreCell(d, "week_ago", methodWords("week_ago")),
            op === null || op === undefined ? <NotHeld key="o" why="The file holds no operator's forecast on these hours." />
              : <Num key="o" check={key(d, "last_2_years", "operator_day_ahead_mae_same_hours")} raw={op} source={`The operator's own day-ahead forecast: its mean absolute error on the hours this horizon is scored on, ${unit}. site/data/${file}.`}>{valueWords(op, unit)}</Num>,
            cov === null || cov === undefined ? <NotHeld key="b" why="No share is in the file for this horizon." />
              : <Num key="b" check={key(d, "band_coverage_pct")} raw={cov} source={`Of the past hours scored at this horizon, the share inside the band, percent. site/data/${file}.`}>{pctWords(cov)}</Num>] };
        })} />
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
  const band = bandOf(hours);
  const sc = dayScore(hours);
  const kinds = [...new Set(hours.map((h) => h.kind).filter(Boolean))];
  const made = hours.find((h) => h.made)?.made ?? null;
  const madeWords = `The forecast drawn was made ${made ? localWords(made, tz) : "at an hour the file does not say"}${kinds.length ? ` (${kinds.map((x) => (x === "live" ? "on the day, and never overwritten" : "by the walk-forward backtest, from a model fit only on days before it")).join("; ")})` : ""}.`;
  return (
    <div className="min-w-0" data-fc-day={slot.mark} data-fc-day-of={day} data-fc-hours={hours.length}>
      <PlaceHead slot={slot} s={s} index={index} />
      <ChartFrame title={`${dayWords(day)}: ${LABEL} and what happened`} legend={band ? [BAND] : undefined} tip={<> <Hint words="source" why={`${madeWords} ${src}`} /></>}>
        <CategoryChart id={`fc-day-${slot.mark}`} x={hours.map((h) => h.label)} series={chartSeries(hours, true)} unit={unit} zero={false} height={280} every={6} band={band} notes={hourNotes(hours, unit, tz)}
          label={`${LABEL} of ${SERIES_WORDS[s].toLowerCase()} for ${placeWords(slot.place)} on ${dayWords(day)}, beside what happened, by the hour of the place's clock (${tz})`} />
      </ChartFrame>
      <ToolTable minWidth={360} caption={`${placeWords(slot.place)}, ${dayWords(day)}: each method's mean absolute error over the day, ${unit}`}
        head={[<span key="d" className="cursor-help" title={sc ? `The mean of each hour's absolute miss, over the ${sc.hours} hours of the day where what happened and every method drawn here are held (the same hours for all, as the report card is made). Computed by the page from the file's rows of ${day}.` : "No hour of the day holds what happened and a forecast."}>Error on the day, {unit}</span>, ...FOUR.map((m) => <MethodHead key={m} m={m} scores={scores} />)]}
        rows={[{ key: "mae", cells: [day,
          ...FOUR.map((m) => (sc && sc.mae[m] !== undefined
            ? <span key={m} data-n={`fc|${k}|day|${m}`} data-fc-day-hours={sc.hours} title={`${methodWords(m)}: the mean absolute error over ${sc.hours} hours of ${day}.`}>{valueWords(sc.mae[m], unit)}</span>
            : <NotHeld key={m} words={m === "operator" ? shortHeld(ser.operator_held) : "not held"} why={m === "operator" && ser.operator_held ? `${OPERATOR}: ${ser.operator_held}.` : "No forecast of this method is held for the day, or what happened is not held."} />))] }]} />
    </div>
  );
}

/** One cell of a score table: the figure with its key into the score file, or a blank with the file's reason. */
function ScoreCell({ c, metric, unit, mcol, what }: { c: Score | undefined; metric: Metric; unit: string; mcol: number; what: string }) {
  const v = c ? c[metric] : null;
  if (!c || v === null) {
    const held = c?.held ?? null;
    // the cell says the reason's first words ("not published"); the whole reason is its hover
    const words = shortHeld(held);
    return <NotHeld words={words} why={held ? `${what}: ${held}.` : `${what}: no score is in the file for this method and cut${metric === "mape" ? " (a percent error is not defined where the value is at or near zero)" : ""}.`} />;
  }
  return <Num check={pfKey("predict/scores.json", ["rows", c.i, mcol])} raw={v} source={`${what}: ${METRIC_WORDS[metric].toLowerCase()}, ${metricUnit(metric, unit)}${c.hours !== null ? `, over ${c.hours.toLocaleString("en-US")} hours` : ""}. Every method of this row is scored on the same hours. site/data/predict/scores.json, row ${c.i}, column ${metric}.`}>{scoreWords(v, metric, unit)}</Num>;
}

// ---- A score table whose columns are the places chosen, each with its hours and its methods -------------------------
type Group = { key: string; name: string; heads: ReactNode[]; held?: { words: string; why: string } };
type GroupRow = { key: string; name: ReactNode; cells: (ReactNode[] | null)[] };
/** The look is ToolTable's (a cardinal header, thin rules); with two places a first header row names each over its
 *  columns, and a place whose series is held is one column that says so. Every row is the same kind of row. */
/** `tall`: a table of many rows (a month a row since 2019) keeps to a frame of its own height and scrolls inside it
 *  under its header, so the sections after it stay within reach; every row is in the page, none is folded away. */
function ScoreTable({ caption, first, groups, rows, k, nowrap, tall }: { caption: string; first: string; groups: Group[]; rows: GroupRow[]; k: string; nowrap?: boolean; tall?: boolean }) {
  const two = groups.length > 1;
  // two places: the cells stand closer, so that both places' columns are in view at 1280 px
  const px = two ? "px-2" : "px-3";
  const edge = (i: number, light: boolean) => (two && i === 0 ? (light ? "border-l border-white/40" : "border-l border-rule") : "");
  return (
    <div className={`overflow-x-auto ${tall ? "max-h-[30rem] overflow-y-auto border-b border-rule" : ""}`} {...scrollRegion(caption)} data-fc-table={k} {...(tall ? { "data-fc-tall": rows.length } : {})}>
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: two ? 760 : 420 }}>
        <caption className="sr-only">{caption}</caption>
        <thead className={tall ? "sticky top-0 z-[1] bg-white" : undefined}>
          {two ? (
            <tr className="bg-accent text-white">
              <td data-empty-head="1" className={`${px} pt-1.5`} />
              {groups.map((g) => <th key={g.key} scope="colgroup" colSpan={g.held ? 1 : g.heads.length} className={`border-l border-white/40 ${px} pt-1.5 text-left font-semibold`} data-fc-group={g.key}>{g.name}</th>)}
            </tr>
          ) : null}
          <tr className="bg-accent text-white">
            <th scope="col" className={`${px} py-1.5 font-normal`}>{first}</th>
            {groups.flatMap((g) => (g.held
              ? [<td key={g.key} data-empty-head="1" className={`border-l border-white/40 ${px} py-1.5`} />]
              : g.heads.map((h, i) => <th key={`${g.key}${i}`} scope="col" className={`${px} py-1.5 text-right font-normal ${edge(i, true)}`}>{h}</th>)))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className="border-b border-rule">
              <th scope="row" className={`${px} py-1.5 font-normal ${nowrap ? "whitespace-nowrap" : ""}`}>{r.name}</th>
              {groups.flatMap((g, gi) => (g.held
                ? [<td key={g.key} className={`border-l border-rule ${px} py-1.5 text-left`}><NotHeld words={g.held.words} why={g.held.why} /></td>]
                : (r.cells[gi] ?? g.heads.map((_, i) => <NotHeld key={i} why="The score file holds no row of this cut for this place." />)).map((c, i) => <td key={`${g.key}${i}`} className={`${px} py-1.5 text-right ${edge(i, false)}`}>{c}</td>)))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** The report card of the places chosen: the last 30 days and the backtest, then by month, by hour of day, and the
 *  other cuts, each one table with a place's hours and methods as its columns. */
function ReportCard({ slots, s, index, scores, metric }: { slots: Slot[]; s: SeriesKey; index: PredictIndex; scores: ScoresFile | null; metric: Metric }) {
  const example = index.example === true;
  const info = slots.map((slot) => {
    const ser = slot.file?.series?.[s];
    const shown = isShown(slot.file, ser) && !!ser;
    const of = ser ?? slot.place.series?.[s];
    const ex = example || slot.file?.example === true;
    return { slot, ser: shown ? (ser as PlaceSeries) : null, held: shown ? undefined : { words: blankWords(of?.status, ex), why: blankWhy(of, ex) }, cuts: shown ? scoresOf(scores, slot.place.place, s) : new Map<string, { keys: string[]; cells: Map<string, Score> }>() };
  });
  if (info.every((x) => !x.ser)) {
    return <div className={slots.length > 1 ? "grid gap-6 xl:grid-cols-2" : ""}>{info.map((x) => <div key={x.slot.mark} className="min-w-0" data-fc-record={x.slot.mark}><PlaceHead slot={x.slot} s={s} index={index} /><Blank what={`The record, ${placeWords(x.slot.place)}`} words={x.held!.words} why={x.held!.why} k={`record|${x.slot.mark}|${s}`} /></div>)}</div>;
  }
  const unit = info.find((x) => x.ser)!.ser!.unit;
  const mu = metricUnit(metric, unit);
  const methods = methodsOf(scores, s);
  const mcol = scores ? scores.rows_columns.indexOf(metric) : -1;
  const names = slots.length > 1 ? "" : `${placeWords(slots[0].place)}: `;
  const groups = (ms: readonly string[]): Group[] => info.map((x) => ({ key: x.slot.mark, name: placeWords(x.slot.place), held: x.held, heads: ["Hours", ...ms.map((m) => <MethodHead key={m} m={m} scores={scores} />)] }));
  const hoursCell = (n: number | null) => (n !== null ? n.toLocaleString("en-US") : <NotHeld why="No count of hours is in the file for this row." />);
  // a table's columns are the methods the score file holds a row of in that table's cuts, for a place chosen: a method
  // with no row there (the operator in a price's months and hours: no operator publishes a price forecast, which the
  // table above says once) is not a column of blanks. A row the file holds with no number and a reason keeps its column.
  const methodsIn = (cutNames: readonly string[]) => methods.filter((m) => info.some((x) => cutNames.some((cut) => { const g = x.cuts.get(cut); return !!g && g.keys.some((key) => g.cells.has(`${key}|${m}`)); })));
  const cutCells = (x: (typeof info)[number], cut: string, key: string, words: string, ms: readonly string[]): ReactNode[] | null => {
    const g = x.cuts.get(cut);
    if (!x.ser || !g || !g.keys.includes(key)) return null;
    return [hoursCell(rowHours(g.cells, key, ms)), ...ms.map((m) => <ScoreCell key={m} c={g.cells.get(`${key}|${m}`)} metric={metric} unit={unit} mcol={mcol} what={`${methodWords(m)}, ${placeWords(x.slot.place)}, ${words}`} />)];
  };
  const keysOf = (cut: string) => orderedKeys(cut, [...new Set(info.flatMap((x) => x.cuts.get(cut)?.keys ?? []))]);
  const table = (cut: string, first: string, name: (key: string) => ReactNode, title: string, words: (key: string) => string, each: string) => {
    const keys = keysOf(cut);
    if (!keys.length) return <p className="mb-5 text-sm" data-fc-cut-none={cut}><NotHeld words={`${title}: not held`} why={scores ? `The score file holds no row of the cut "${cut}" for ${slots.length > 1 ? "these places" : "this place"} and series.` : "The score file (site/data/predict/scores.json) is not on the site."} /></p>;
    const over = cutWhy(cut);
    const ms = methodsIn([cut]);
    return (
      <div className="mb-5" data-fc-cut={cut}>
        <h4 className="mb-1 text-sm font-semibold"><span title={over ? `The score file's words on this cut: ${over}.` : undefined} className={over ? "cursor-help" : undefined}>{title}</span>, {mu} <span className="font-normal">({keys.length} {each})</span></h4>
        <ScoreTable k={cut} nowrap tall={keys.length > 30} first={first} groups={groups(ms)} caption={`${names}${METRIC_WORDS[metric].toLowerCase()} of each method's forecast of ${SERIES_WORDS[s].toLowerCase()}, ${title.toLowerCase()}, ${mu}`}
          rows={keys.map((key) => ({ key, name: name(key), cells: info.map((x) => cutCells(x, cut, key, words(key), ms)) }))} />
      </div>
    );
  };
  const eventWords = (key: string) => `Event: ${key.replace(/[_-]/g, " ")}`;
  // session 10411 (the contract's line of session 10603, in answer to this window's request 12): for a price the ten days
  // are those of the highest price hour, not of the highest demand. A price row's cut is named so, and its hover is the
  // score file's `cuts_price` where the file carries it; `cuts` names the cut by demand, so it is not quoted for a price
  const cutWords = (cut: string) => (s === "price" ? PRICE_CUT_WORDS[cut] : undefined) ?? CUT_WORDS[cut] ?? cut;
  const cutWhy = (cut: string): string | undefined => (s === "price" ? scores?.cuts_price?.[cut] ?? (cut === "top10" || cut === "spike" ? undefined : scores?.cuts?.[cut]) : scores?.cuts?.[cut]);
  const other = OTHER_CUTS.flatMap((cut) => keysOf(cut).map((key) => ({ cut: cut as string, key, words: cut === "event" ? eventWords(key) : cutWords(cut) })));
  const otherMethods = methodsIn(OTHER_CUTS);
  const parts: [string, string][] = [["last_30_days", "The last 30 days"], ["backtest", "The backtest"]];
  // session 10405 (chain 720, part E): the day's peak (a place file's series.demand.peak; the contract's change of
  // session 10601). One table in the form of the others: the size of each method's miss of the day's highest hour (the
  // score chosen), and how often its highest hour was the day's, exactly and within one. Every method the same weight.
  const peaked = s === "demand" && info.some((x) => PEAK_SPANS.some(([span]) => !!x.ser?.peak?.[span]));
  const peakWhat = info.map((x) => x.ser?.peak?.what).find(Boolean);
  const peakCells = (x: (typeof info)[number], span: (typeof PEAK_SPANS)[number][0], field: "mae" | "mape" | "hour_exact_pct" | "hour_within_1_pct", words: string, what: string): ReactNode[] | null => {
    const p = x.ser?.peak?.[span];
    if (!x.ser || !p) return null;
    const file = fileOf(x.slot);
    const when = p.first_day && p.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say";
    return [p.days !== null && p.days !== undefined
      ? <Num key="d" check={pfKey(file, ["series", "demand", "peak", span, "days"])} raw={p.days} source={`The days scored, ${when}: the days whose every hour is held by every method.`}>{p.days.toLocaleString("en-US")}</Num>
      : <NotHeld key="d" why="No count of days is in the file." />,
      ...FOUR.map((m) => {
        const v = p.methods?.[m]?.[field];
        return v === null || v === undefined
          ? <NotHeld key={m} words={m === "operator" ? shortHeld(x.ser!.operator_held) : "not held"} why={m === "operator" && x.ser!.operator_held ? `${OPERATOR}: ${x.ser!.operator_held}.` : "No score of the peak is in the file for this method and span."} />
          : <Num key={m} check={pfKey(file, ["series", "demand", "peak", span, "methods", m, field])} raw={v} source={`${methodWords(m)}, ${placeWords(x.slot.place)}, ${words.toLowerCase()} (${when}): ${what}. site/data/${file}.`}>{field === "mae" || field === "mape" ? scoreWords(v, field, unit) : pctWords(v)}</Num>;
      })];
  };
  // session 10406 (chain 720, part E): the separate line "with the weather known" (a place file's
  // series.demand.with_weather_known; the contract's change of session 10601). It reads the target day's own observed
  // temperature, so it is not a forecast: it has a table of its own under those words, is in no chart and no other
  // table, and is never called the ERW forecast. Beside it, the regression and the operator on the same hours.
  const weathered = s === "demand" && info.some((x) => WEATHER_SPANS.some(([span]) => !!x.ser?.with_weather_known?.[span]));
  const weatherWhat = info.map((x) => x.ser?.with_weather_known?.what).find(Boolean);
  const weatherCells = (x: (typeof info)[number], span: (typeof WEATHER_SPANS)[number][0], words: string): ReactNode[] | null => {
    const p = x.ser?.with_weather_known?.[span];
    if (!x.ser || !p) return null;
    const file = fileOf(x.slot);
    const when = p.first_day && p.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say";
    return [p.hours !== null && p.hours !== undefined
      ? <Num key="h" check={pfKey(file, ["series", "demand", "with_weather_known", span, "hours"])} raw={p.hours} source={`The hours scored, ${when}: the hours the region's temperature, what happened and all three lines are held.`}>{p.hours.toLocaleString("en-US")}</Num>
      : <NotHeld key="h" why="No count of hours is in the file." />,
      ...WEATHER_METHODS.map((m) => {
        const v = p[metric]?.[m];
        return v === null || v === undefined
          ? <NotHeld key={m} why={`No score of ${methodWords(m).toLowerCase()} on these hours is in the file.`} />
          : <Num key={m} check={pfKey(file, ["series", "demand", "with_weather_known", span, metric, m])} raw={v} source={`${m === "with_weather_known" ? `${WEATHER_LABEL} (not a forecast: it reads the day's own weather)` : methodWords(m)}, ${placeWords(x.slot.place)}, ${words.toLowerCase()} (${when}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}, on the hours the weather is held. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
      })];
  };
  return (
    <div data-fc-record={slots.map((x) => x.mark).join("")}>
      <div className="mb-5" data-fc-summary="1">
        <h4 className="mb-1 text-sm font-semibold">The last 30 days and the whole backtest, {mu}</h4>
        <ScoreTable k="summary" first="Span" groups={groups(FOUR)} caption={`${names}${METRIC_WORDS[metric].toLowerCase()} of each method's forecast of ${SERIES_WORDS[s].toLowerCase()} over the last 30 days and over the backtest, ${mu}`}
          rows={parts.map(([part, words]) => ({ key: part, name: words, cells: info.map((x) => {
            if (!x.ser) return null;
            const p = x.ser.summary?.[part as "backtest"], file = fileOf(x.slot);
            const span = p?.first_day && p?.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say";
            return [p?.hours !== null && p?.hours !== undefined ? <Num key="h" check={pfKey(file, ["series", s, "summary", part, "hours"])} raw={p.hours} source={`The hours scored, ${span}.`}>{p.hours.toLocaleString("en-US")}</Num> : <NotHeld key="h" why="No count of hours is in the file." />,
              ...FOUR.map((m) => {
                const v = p?.[metric]?.[m];
                return v === null || v === undefined
                  ? <NotHeld key={m} words={m === "operator" ? shortHeld(x.ser!.operator_held) : "not held"} why={m === "operator" && x.ser!.operator_held ? `${OPERATOR}: ${x.ser!.operator_held}.` : "No score is in the file for this method and span."} />
                  : <Num key={m} check={pfKey(file, ["series", s, "summary", part, metric, m])} raw={v} source={`${methodWords(m)}, ${placeWords(x.slot.place)}, ${words.toLowerCase()} (${span}): ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
              })];
          }) }))} />
      </div>
      {peaked ? (
        <div className="mb-5" data-fc-peak="1">
          <h4 className="mb-1 text-sm font-semibold"><span className={peakWhat ? "cursor-help" : undefined} title={peakWhat ? `The file's words: ${peakWhat}.` : undefined}>The day&apos;s peak</span>: the error of its size, {mu}, and how often its hour was the day&apos;s, % of days</h4>
          <ScoreTable k="peak" first="Span" caption={`${names}the day's highest hour of demand: ${METRIC_WORDS[metric].toLowerCase()} of each method's own highest hour, ${mu}, and the share of days on which the hour was the same or one away, percent`}
            groups={info.map((x) => ({ key: x.slot.mark, name: placeWords(x.slot.place), held: x.held, heads: ["Days", ...FOUR.map((m) => <MethodHead key={m} m={m} scores={scores} />)] }))}
            rows={PEAK_SPANS.flatMap(([span, words]) => [
              { key: `${span}|size`, name: <span className="cursor-help" title={`${METRIC_WORDS[metric]} of each method's highest hour of a day against the day's highest hour of demand, ${mu}.`}>{words}: error of its size, {mu}</span>,
                cells: info.map((x) => peakCells(x, span, metric, words, `${METRIC_WORDS[metric].toLowerCase()} of the method's highest hour of a day against the day's highest hour of demand, ${mu}`)) },
              ...PEAK_HOURS.map(([field, name, what]) => ({ key: `${span}|${field}`, name: <span className="cursor-help" title={`${what[0].toUpperCase()}${what.slice(1)}.`}>{words}: {name}, %</span>,
                cells: info.map((x) => peakCells(x, span, field, words, what)) })),
            ])} />
        </div>
      ) : null}
      {weathered ? (
        <div className="mb-5" data-fc-weather="1">
          <h4 className="mb-1 text-sm font-semibold"><span className="cursor-help" title={`Not a forecast, and never the ${LABEL}: ${weatherWhat ?? "the regression with the target day's own observed temperature added"}.${scores && (scores as { separate_lines?: Record<string, string> | null }).separate_lines?.with_weather_known ? ` The score file's words: ${(scores as { separate_lines?: Record<string, string> | null }).separate_lines!.with_weather_known}.` : ""}`}>{WEATHER_LABEL}</span> (not a forecast), beside the regression and the operator on the same hours, {mu}</h4>
          <ScoreTable k="weather" first="Span" caption={`${names}with the weather known, which is not a forecast: ${METRIC_WORDS[metric].toLowerCase()} of the regression with the day's own observed temperature added, of the regression and of the operator's forecast, on the hours the weather is held, ${mu}`}
            groups={info.map((x) => ({ key: x.slot.mark, name: placeWords(x.slot.place), held: x.held, heads: ["Hours", ...WEATHER_METHODS.map((m) => (m === "with_weather_known"
              ? <span key={m} className="cursor-help" title={`${WEATHER_LABEL}: not a forecast. ${weatherWhat ?? ""}`}>{WEATHER_LABEL}</span>
              : <MethodHead key={m} m={m} scores={scores} />))] }))}
            rows={WEATHER_SPANS.map(([span, words]) => ({ key: span, name: words, cells: info.map((x) => weatherCells(x, span, words)) }))} />
        </div>
      ) : null}
      {table("month", "Month", (key) => monthWords(key), "By month", (key) => monthWords(key), "months")}
      {table("hour", "Hour", (key) => <span title={`The hour from ${hourWords(key)} of the place's own clock`} className="cursor-help">{hourWords(key)}</span>, "By hour of day", (key) => `the hour from ${hourWords(key)}`, "hours")}
      {other.length ? (
        <div className="mb-5" data-fc-cut="other">
          <h4 className="mb-1 text-sm font-semibold">{s === "price" ? "Every hour, the last two years, the days of the highest prices, the spikes and the events" : "Every hour, the last two years, the highest-demand days and the events"}, {mu}</h4>
          <ScoreTable k="other" first="Hours scored" groups={groups(otherMethods)} caption={`${names}${METRIC_WORDS[metric].toLowerCase()} of each method's forecast of ${SERIES_WORDS[s].toLowerCase()} over every hour scored, ${s === "price" ? "the ten days with the highest price hour" : "the ten highest-demand days"}, the price spikes and each event, ${mu}`}
            rows={other.map(({ cut, key, words }) => ({ key: `${cut}|${key}`,
              name: cut === "event" && eventHref(key) ? <SiteLink href={eventHref(key)!} title={`${scores?.cuts?.event ?? "An event of /events"}. Opens the event's page.`}>{words}</SiteLink> : <span title={cutWhy(cut)} className={cutWhy(cut) ? "cursor-help" : undefined}>{words}</span>,
              cells: info.map((x) => cutCells(x, cut, key, words.toLowerCase(), otherMethods)) }))} />
        </div>
      ) : null}
    </div>
  );
}

/** Every place at once: one row a place in the index's own order, every method, over every hour scored. */
function AllPlaces({ index, scores, s, metric, chosen }: { index: PredictIndex; scores: ScoresFile | null; s: SeriesKey; metric: Metric; chosen: string[] }) {
  const methods = methodsOf(scores, s);
  const mcol = scores ? scores.rows_columns.indexOf(metric) : -1;
  const unit = s === "price" ? "USD/MWh" : "MW";
  const mu = metricUnit(metric, unit);
  const example = index.example === true || scores?.example === true;
  return (
    <div data-fc-all={index.places.length}>
      <ToolTable minWidth={560} caption={`Every place: ${METRIC_WORDS[metric].toLowerCase()} of each method's forecast of ${SERIES_WORDS[s].toLowerCase()} over every hour scored, ${mu}`}
        head={[`Place (${mu})`, "Hours", ...methods.map((m) => <MethodHead key={m} m={m} scores={scores} />)]}
        rows={index.places.map((p) => {
          const ix = p.series?.[s];
          const name = <SiteLink key="n" href={hrefOf({ a: p.place, b: null, s, day: null, m: null })} className="inline-block py-1 -my-1">{placeWords(p)}</SiteLink>;
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
  // session 10405: the days after tomorrow; null while the file is not on the site, an example or a test's fixture
  const aheadFile = predictAhead();
  const ahead = aheadFile && aheadFile.example !== true && index?.example !== true ? aheadFile : null;
  // session 10409: the wind and solar file; null while it is not on the site, an example or a test's fixture
  const windSolarFile = predictWindSolar();
  const windSolar = windSolarFile && windSolarFile.example !== true && index?.example !== true ? windSolarFile : null;
  const rtFile = predictRtPrice();
  const rtPrice = rtFile && rtFile.example !== true && index?.example !== true ? rtFile : null;
  // session 10411: the day-ahead price at more hubs; null while the file is not on the site, an example or a fixture
  const hubsFile = predictPriceHubs();
  const priceHubs = hubsFile && hubsFile.example !== true && index?.example !== true ? hubsFile : null;
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
  const dflt = metricDefault(q.s), alt: Metric = dflt === "mape" ? "mae" : "mape";
  const metricLabel = (m: Metric) => (m === "mape" ? "Percent error (MAPE)" : `Error in ${q.s === "price" ? "USD/MWh" : "MW"} (MAE)`);
  return (
    <div data-forecast="1" data-fc-state={index.example === true ? "example" : "files"} data-fc-series={q.s} data-fc-metric={metric}>
      {header}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
        <div className="min-w-0 lg:sticky lg:top-2 lg:self-start">
          <InputPanel title="Choices" reset={{ href: "/forecast", defaults: "Texas alone, demand, the newest past day, percent error" }}>
            <form method="get" action="/forecast" className="flex flex-col gap-3 text-sm [&_label]:min-w-0 [&_label]:max-w-full [&_select]:w-full [&_select]:max-w-full" data-fc-form="1">
              <AutoSubmitSelect name="a" value={first.place.place} options={options} label="Place A" />
              <AutoSubmitSelect name="b" value={q.b ?? NONE} options={[{ value: NONE, label: "None" }, ...options.filter((o) => o.value !== first.place.place)]} label="Place B, side by side" />
              <AutoSubmitSelect name="s" value={q.s} options={SERIES.map((x) => ({ value: x, label: SERIES_WORDS[x] }))} label="Forecast of" />
              <AutoSubmitSelect name="day" value={q.day ?? ""} options={[{ value: "", label: "The newest day held" }, ...(q.day && !days.includes(q.day) ? [{ value: q.day, label: `${q.day} (not held)` }] : []), ...days.map((d) => ({ value: d, label: dayWords(d) }))]} label="Past day" />
              <AutoSubmitSelect name="m" value={q.m ?? ""} options={[{ value: "", label: metricLabel(dflt) }, { value: alt, label: metricLabel(alt) }]} label="Score shown" />
              {/* session 10411: the hub drawn under "More hubs" stays drawn through another choice of the form */}
              {q.hub ? <input type="hidden" name="hub" value={q.hub} /> : null}
              <button type="submit" className="self-start border border-rule bg-white px-3 py-1 text-sm">Show</button>
            </form>
          </InputPanel>
        </div>
        <div className="min-w-0">
          <ToolTabs label="Forecast of" items={SERIES.map((x) => ({ key: x, label: SERIES_WORDS[x], href: hrefOf(q, { s: x, m: null, day: null }), on: q.s === x }))} />
          <ToolSection title="Tomorrow" id="tomorrow">
            <div className={two}>{slots.map((x) => <Tomorrow key={x.mark} slot={x} s={q.s} index={index} scores={scores} />)}</div>
            {/* session 10405: the days after tomorrow, demand only, once the file of them is on the site */}
            {q.s === "demand" && ahead ? (
              <div data-fc-ahead-block="1">
                <div className={two}>{slots.map((x) => <DaysAhead key={x.mark} slot={x} ahead={ahead} metric={metric} scores={scores} part="chart" />)}</div>
                {slots.map((x) => <DaysAhead key={x.mark} slot={x} ahead={ahead} metric={metric} scores={scores} part="table" />)}
              </div>
            ) : null}
            {/* session 10409: wind, solar and what is left of demand after them, demand only */}
            {q.s === "demand" ? (
              <div data-fc-net-block="1">
                <div className={two}>{slots.map((x) => <NetDemand key={x.mark} slot={x} ws={windSolar} metric={metric} part="chart" />)}</div>
                {slots.map((x) => <NetDemand key={x.mark} slot={x} ws={windSolar} metric={metric} part="table" />)}
              </div>
            ) : null}
          </ToolSection>
          <ToolSection title="How it has done" id="record">
            <div className={two}>{slots.map((x) => <PastDay key={x.mark} slot={x} s={q.s} index={index} scores={scores} asked={q.day} />)}</div>
            {q.s === "demand" ? <div className={two} data-fc-wsday-block="1">{slots.map((x) => <WindSolarDay key={x.mark} slot={x} ws={windSolar} asked={q.day} />)}</div> : null}
            <div className="mt-6"><ReportCard slots={slots} s={q.s} index={index} scores={scores} metric={metric} /></div>
            {/* session 10409: the check of the operator's filing, the separate line with the weather forecast (demand
                only), and the band's record (either series); each after the report card, which stands as it was. With
                two places each place's tables keep the page's full width, one place under the other (six and seven
                columns do not fit half of it) */}
            {/* session 10410: wind and solar by month and by hour of day, from the wind and solar file's rows, behind folds */}
            {q.s === "demand" ? <div data-fc-ws-cuts-block="1">{slots.map((x) => <WindSolarCuts key={x.mark} slot={x} ws={windSolar} metric={metric} />)}</div> : null}
            {q.s === "demand" ? <div data-fc-filing-block="1">{slots.map((x) => <FilingCheck key={x.mark} slot={x} scores={scores} metric={metric} />)}</div> : null}
            {q.s === "demand" ? <div data-fc-wwf-block="1">{slots.map((x) => <WeatherForecastLine key={x.mark} slot={x} scores={scores} metric={metric} />)}</div> : null}
            <div data-fc-band-block="1">{slots.map((x) => <BandCheck key={x.mark} slot={x} s={q.s} ws={windSolar} rt={rtPrice} />)}</div>
          </ToolSection>
          {/* session 10409: the real-time price, with price, for a place whose hub the real-time file holds */}
          {q.s === "price" ? <RealTimeSection slots={slots} rt={rtPrice} scores={scores} metric={metric} asked={q.day} /> : null}
          {/* session 10411: the other hubs of each place's grid, and the one a reader chose drawn whole */}
          {q.s === "price" ? <MoreHubsSection slots={slots} hubs={priceHubs} rt={rtPrice} scores={scores} metric={metric} asked={q.day} chosen={q.hub ?? null} hrefOf={(hub) => hrefOf(q, { hub }, "#hubs")} /> : null}
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
              {predictLedger(q.s) !== null ? (
                <li data-fc-download="ledger">The ledger of {SERIES_WORDS[q.s].toLowerCase()}, every place: each forecast as it was made on its day, never rewritten:{" "}
                  <a href={`/forecast/ledger?s=${q.s}`} download data-download="csv">CSV</a>,{" "}
                  <a href={`/forecast/ledger/python?s=${q.s}`} download data-download="python">Python</a>,{" "}
                  <a href={`/forecast/ledger/stata?s=${q.s}`} download data-download="stata">Stata</a></li>
              ) : null}
              {q.s === "demand" && ahead ? (
                <li data-fc-download="ahead">The days after tomorrow, every place, hour by hour:{" "}
                  <a href="/forecast/ahead" download data-download="csv">CSV</a>,{" "}
                  <a href="/forecast/ahead/python" download data-download="python">Python</a>,{" "}
                  <a href="/forecast/ahead/stata" download data-download="stata">Stata</a></li>
              ) : null}
              {/* session 10410: the lines of 27 November, where the place holds them */}
              {q.s === "demand" ? slots.filter((x) => isShown(x.file, x.file?.series?.demand) && (!!x.file?.series?.demand?.net_demand || !!windSolarFor(windSolar, x.place.place))).map((x) => (
                <li key={`n${x.mark}`} data-fc-download="net">{placeWords(x.place)}, net demand, wind and solar, hour by hour (the day forecast now and every past day of wind and solar held):{" "}
                  <a href={`/forecast/net?place=${x.place.place}`} download data-download="csv">CSV</a>,{" "}
                  <a href={`/forecast/net/python?place=${x.place.place}`} download data-download="python">Python</a>,{" "}
                  <a href={`/forecast/net/stata?place=${x.place.place}`} download data-download="stata">Stata</a></li>
              )) : null}
              {q.s === "price" ? [...new Map(slots.map((x) => rtOf(x, rtPrice)).filter((e): e is NonNullable<typeof e> => !!e).map((e) => [e.hub.hub, e.hub])).values()].map((hub) => (
                <li key={`r${hub.hub}`} data-fc-download="realtime">The real-time price at {hub.hub}, hour by hour (the day forecast now and every past day held, beside the day-ahead price):{" "}
                  <a href={`/forecast/realtime-price?hub=${encodeURIComponent(hub.hub)}`} download data-download="csv">CSV</a>,{" "}
                  <a href={`/forecast/realtime-price/python?hub=${encodeURIComponent(hub.hub)}`} download data-download="python">Python</a>,{" "}
                  <a href={`/forecast/realtime-price/stata?hub=${encodeURIComponent(hub.hub)}`} download data-download="stata">Stata</a></li>
              )) : null}
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
