// Energy Research Warehouse (ERW) site, session 10409 (chain 720, part E): the views of /forecast for what the
// forecast's page files gained on 27 November 2026 (lib/predictlines.ts; the dated lines of that day at the foot of
// docs/state/page_files_predict.md). Each is one plain component the page places (app/forecast/view.tsx), so that a
// test can draw it to HTML without a build:
//
//   under "Tomorrow" (demand):        wind, solar and what is left of demand after them, net demand, by the hour;
//   under "How it has done" (demand): wind and solar on a past day beside what happened; the operator's filed forecast
//                                     checked by month; the separate line "with the weather forecast";
//   under "How it has done" (both):   the band, how often what happened fell inside it.
//
// Every figure is a page file's and carries its key into its file. The ERW's lines are named "ERW forecast" on every
// chart. The separate line is never called the ERW forecast and is in no chart of one. A place whose file holds none of
// a view draws nothing of it. The page says what was forecast and how it scored: no advice, no view.
import type { ReactNode } from "react";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { ChartFrame, HeadlineNumber, ToolTable } from "@/components/tool/ToolPage";
import { pfKey } from "@/lib/pagefile";
import {
  FOUR, LABEL, METRIC_WORDS, SERIES_WORDS, dayWords, hourWords, isShown, localWords, methodShort, methodWhat, methodWords, metricUnit, monthWords, placeWords, scoreWords, scoresOf, tomorrowOf, utcWords, valueWords,
  type IndexPlace, type Metric, type PlaceFile, type ScoresFile, type SeriesKey, type SummaryPart,
} from "@/lib/predict";
import {
  BAND_SHARES, FUELS, FUEL_METHODS, FUEL_WORDS, LINE_METHOD_SHORT, LINE_METHOD_WORDS, MW_SPANS, WEATHER_FORECAST_LABEL, WEATHER_FORECAST_METHODS, WEATHER_FORECAST_WORDS,
  bandMonths, filingMonths, filingShift, fuelShown, hourValues, lineDays, lineDefaultDay, lineHours, mwMetricOf, shareWords, tooFewDays, windSolarOf, wordsOfMethod,
  type BandCoverage, type FuelKey, type FuelSeries, type LineHour, type MwPart, type WindSolarFile,
} from "@/lib/predictlines";

export type Slot = { mark: "a" | "b"; place: IndexPlace; file: PlaceFile | null };
const fileOf = (slot: Slot) => `predict/${slot.place.file}`;
const WS_FILE = "predict/wind_solar.json";
const ACTUAL = "actual";
const FUEL_COLOR: Record<FuelKey, string> = { wind: "--color-fuel-wind", solar: "--color-fuel-solar" };

function Blank({ what, words, why, k }: { what: string; words: string; why: string; k: string }) {
  return (
    <div className="my-2 flex min-h-24 cursor-help items-center justify-center border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" title={why} data-fc-blank={k}>
      {what}: {words}
    </div>
  );
}
const NotHeld = ({ words = "not held", why }: { words?: string; why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">{words}</span>;
const lineWords = (id: string) => LINE_METHOD_WORDS[id] ?? WEATHER_FORECAST_WORDS[id] ?? methodWords(id);
const lineShort = (id: string) => LINE_METHOD_SHORT[id] ?? WEATHER_FORECAST_WORDS[id] ?? methodShort(id);
const Head = ({ m, what }: { m: string; what?: string }) => <span title={`${lineWords(m)}${what ? `: ${what}` : ""}`} className="cursor-help">{lineShort(m)}</span>;
const spanWords = (p: { first_day: string | null; last_day: string | null } | null | undefined) => (p?.first_day && p?.last_day ? `${p.first_day} to ${p.last_day}` : "days the file does not say");
const count = (v: number | null | undefined, key: string, src: string): ReactNode => (v === null || v === undefined ? <NotHeld why="No count is in the file." /> : <Num check={key} raw={v} source={src}>{v.toLocaleString("en-US")}</Num>);
/** The demand series of a slot when it is shown, else null. */
const demandOf = (slot: Slot) => { const ser = slot.file?.series?.demand; return isShown(slot.file, ser) && ser ? ser : null; };

// ---- Wind, solar and net demand: tomorrow ---------------------------------------------------------------------------

/** For one place: the ERW forecast of demand, of wind and of solar output for the day forecast now, and of what is left
 *  of demand after wind and solar (net demand), by the hour; four figures; how each line has scored; the hours as a
 *  table. The wind and solar lines are the wind and solar file's entry the place's net demand names. */
/** `part`: with two places their figures and charts stand side by side, and under them each place's tables at the
 *  page's full width (seven columns do not fit half of it), as the days after tomorrow are laid out. */
export function NetDemand({ slot, ws, metric, part }: { slot: Slot; ws: WindSolarFile | null; metric: Metric; part: "chart" | "table" }) {
  const ser = demandOf(slot);
  const net = ser?.net_demand;
  if (!ser || !net) return part === "chart" ? <div className="min-w-0" data-fc-net={slot.mark} data-fc-net-hours="none" /> : null;
  const file = fileOf(slot), tz = slot.place.time, unit = ser.unit, k = slot.mark;
  const entry = windSolarOf(ws, net.wind_solar_place ?? slot.place.place);
  const fuels = FUELS.map((fuel) => ({ fuel, f: entry?.place.fuels?.[fuel] ?? null })).map((x) => ({ ...x, shown: fuelShown(x.f), hours: fuelShown(x.f) ? lineHours(x.f.tomorrow_columns, x.f.tomorrow, "operator") : [] }));
  const nets = hourValues(net.tomorrow_columns, net.tomorrow, "erw");
  const title = `${placeWords(slot.place)}: wind, solar and net demand`;
  const what = net.what ?? "Net demand: the demand less the output of wind and solar.";
  if (net.status !== "shown" || !nets.some((x) => x.v !== null)) {
    const why = net.status !== "shown" ? `Net demand: ${net.status ?? "not held"}.` : fuels.map((x) => x.f?.tomorrow_held).find(Boolean) ?? "The file holds no net demand for the day forecast now, and does not say why.";
    if (part === "table") return <div className="min-w-0" data-fc-net-table={k}><LineScores slot={slot} ws={ws} metric={metric} /></div>;
    return (
      <div className="min-w-0" data-fc-net={k} data-fc-net-hours="0">
        <h4 className="mb-1 text-sm font-semibold">{title}</h4>
        <Blank what={`${LABEL} of net demand, ${placeWords(slot.place)}${ser.target_day ? `, ${dayWords(ser.target_day)}` : ""}`} words={net.status !== "shown" ? net.status ?? "not held" : "not held"} why={why} k={`net|${k}`} />
      </div>
    );
  }
  const demand = tomorrowOf(ser);
  const netCol = (net.tomorrow_columns ?? []).indexOf("erw");
  const byTs = <T extends { ts: string }>(rows: T[]) => new Map(rows.map((r) => [r.ts, r]));
  const dem = byTs(demand), fuelAt = fuels.map((x) => byTs(x.hours));
  const made = `${LABEL}: a model's output (tier derived), not a published figure. ${what}`;
  const netNum = (x: (typeof nets)[number], key: string, src: string) => <Num check={pfKey(file, ["series", "demand", "net_demand", "tomorrow", x.i, netCol])} raw={x.v as number} source={`${src} ${made} site/data/${file}.`}><span data-n={`fc|${k}|net|${key}`}>{valueWords(x.v as number, unit)}</span></Num>;
  const fuelKey = (fuel: FuelKey, ...rest: (string | number)[]) => pfKey(WS_FILE, ["places", entry?.pi ?? 0, "fuels", fuel, ...rest]);
  const fuelNum = (x: (typeof fuels)[number], h: LineHour, col: "erw" | "operator", key: string, src: string) => {
    const v = col === "erw" ? h.erw : h.other;
    const at = (x.f?.tomorrow_columns ?? []).indexOf(col);
    return v === null ? <NotHeld why={col === "operator" ? x.f?.operator_held ?? "No forecast of the operator is held for this hour." : "No forecast is held for this hour."} />
      : <Num check={fuelKey(x.fuel, "tomorrow", h.i, at)} raw={v} source={`${src}${h.lo !== null && h.hi !== null && col === "erw" ? ` Band: ${valueWords(h.lo, unit)} to ${valueWords(h.hi, unit)} ${unit}.` : ""} ${col === "erw" ? `${LABEL}: a model's output, not a published figure; ${x.f?.target_series ?? ""}.` : x.f?.operator ?? ""} site/data/${WS_FILE}.`}><span data-n={`fc|${k}|${x.fuel}|${key}`}>{valueWords(v, unit)}</span></Num>;
  };
  const held = nets.filter((x) => x.v !== null);
  const low = held.reduce((a, b) => ((b.v as number) < (a.v as number) ? b : a)), high = held.reduce((a, b) => ((b.v as number) > (a.v as number) ? b : a));
  const top = fuels.map((x) => { const hs = x.hours.filter((h) => h.erw !== null); return hs.length ? hs.reduce((a, b) => ((b.erw as number) > (a.erw as number) ? b : a)) : null; });
  const series: CatSeries[] = [
    // the lines' names are short, so that on a phone the plot keeps its width (each name stands at its line's right
    // end; with "ERW forecast: net demand" the names took half of 390 px): the chart's title says whose forecasts they are
    { name: "Demand", color: "accent", kind: "line", values: nets.map((x) => dem.get(x.ts)?.erw ?? null) },
    { name: "Net demand", color: "ink", kind: "line", values: nets.map((x) => x.v) },
    ...fuels.flatMap((x, i): CatSeries[] => (x.hours.length ? [{ name: FUEL_WORDS[x.fuel], color: FUEL_COLOR[x.fuel], kind: "line", values: nets.map((n) => fuelAt[i].get(n.ts)?.erw ?? null) }] : [])),
  ];
  const anyOp = fuels.some((x) => x.hours.some((h) => h.other !== null));
  const notes = nets.map((x) => `Hour beginning ${localWords(x.ts, tz)}.${fuels.map((f, i) => { const h = fuelAt[i].get(x.ts); return h && h.lo !== null && h.hi !== null ? ` ${FUEL_WORDS[f.fuel]}, band: ${valueWords(h.lo, unit)} to ${valueWords(h.hi, unit)} ${unit}${h.other !== null ? `; the operator's forecast ${valueWords(h.other, unit)} ${unit}` : ""}.` : ""; }).join("")}`);
  const none = (why: string) => <span className="font-sans text-base"><NotHeld why={why} /></span>;
  if (part === "table") return (
    <div className="min-w-0" data-fc-net-table={k}>
      <LineScores slot={slot} ws={ws} metric={metric} />
      <details className="mb-6 border-b border-rule py-2" data-fc-net-fold={k}>
        <summary className="cursor-pointer py-1 text-sm">{placeWords(slot.place)}, hour by hour, {dayWords(ser.target_day)}: demand, wind, solar, net demand</summary>
        <div className="pt-2">
          <ToolTable minWidth={anyOp ? 620 : 460} caption={`${LABEL} of demand, of wind and solar output and of net demand for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, hour by hour, ${unit}`}
            head={["Hour", "Demand", ...fuels.flatMap((x) => [FUEL_WORDS[x.fuel], ...(anyOp ? [`${FUEL_WORDS[x.fuel]}, operator`] : [])]), "Net demand"]}
            rows={nets.map((x) => {
              const d = dem.get(x.ts);
              return { key: x.ts, cells: [<span key="h" title={`The hour beginning ${localWords(x.ts, tz)} (${utcWords(x.ts)})`} className="cursor-help">{hourWords(x.hour)}</span>,
                d && d.erw !== null ? <Num key="d" check={pfKey(file, ["series", "demand", "tomorrow", d.i, ser.tomorrow_columns.indexOf("erw")])} raw={d.erw} source={`${LABEL} of demand. site/data/${file}.`}>{valueWords(d.erw, unit)}</Num> : <NotHeld key="d" why="No forecast of demand is held for this hour." />,
                ...fuels.flatMap((f, i) => {
                  const h = fuelAt[i].get(x.ts);
                  const blank = (key: string) => <NotHeld key={key} why={f.f ? f.f.tomorrow_held ?? `No forecast of ${f.fuel} output is held for this hour.` : `The wind and solar file holds no ${f.fuel} line for this place.`} />;
                  return [h ? <span key={f.fuel}>{fuelNum(f, h, "erw", `h${h.i}`, "")}</span> : blank(f.fuel), ...(anyOp ? [h ? <span key={`${f.fuel}o`}>{fuelNum(f, h, "operator", `h${h.i}|operator`, "The operator's own forecast.")}</span> : blank(`${f.fuel}o`)] : [])];
                }),
                x.v !== null ? <span key="n">{netNum(x, `h${x.i}`, "")}</span> : <NotHeld key="n" why="No net demand is held for this hour." />] };
            })} />
        </div>
      </details>
    </div>
  );
  return (
    <div className="min-w-0" data-fc-net={k} data-fc-net-hours={held.length}>
      <h4 className="mb-2 text-sm font-semibold">{title}</h4>
      <div className="mb-4 grid gap-4 sm:grid-cols-2">
        <HeadlineNumber label="Lowest net demand" unit={unit} value={netNum(low, "low", `The lowest hour of the ${LABEL} of net demand, the hour beginning ${localWords(low.ts, tz)}.`)} note={`${LABEL}, ${hourWords(low.hour)}`} />
        <HeadlineNumber label="Highest net demand" unit={unit} value={netNum(high, "high", `The highest hour of the ${LABEL} of net demand, the hour beginning ${localWords(high.ts, tz)}.`)} note={`${LABEL}, ${hourWords(high.hour)}`} />
        {fuels.map((x, i) => (
          <HeadlineNumber key={x.fuel} label={`Highest ${x.fuel} hour`} unit={top[i] ? unit : undefined}
            value={top[i] ? fuelNum(x, top[i] as LineHour, "erw", "top", `The highest hour of the ${LABEL} of ${x.fuel} output, the hour beginning ${localWords((top[i] as LineHour).ts, tz)}.`) : none(x.f ? x.f.tomorrow_held ?? `The file holds no forecast of ${x.fuel} output for the day forecast now.` : `The wind and solar file (site/data/${WS_FILE}) holds no ${x.fuel} line for this place.`)}
            note={top[i] ? `${LABEL}, ${hourWords((top[i] as LineHour).hour)}` : undefined} />
        ))}
      </div>
      <ChartFrame title={`${LABEL} of demand, wind, solar and net demand: ${dayWords(ser.target_day)}`}
        tip={<> <Hint words="source" why={`${made} Wind and solar: ${fuels.map((x) => (x.f ? `${x.fuel}, ${x.f.target_series ?? "the place's output"}, method ${lineWords(x.f.method ?? "not said")}` : `${x.fuel}, not held`)).join("; ")}; ${ws?.made_rule ?? ""}. site/data/${file} and site/data/${WS_FILE}.`} />, <Hint words="net demand" why={what} /></>}>
        <CategoryChart id={`fc-net-${k}`} x={nets.map((x) => hourWords(x.hour))} series={series} unit={unit} height={280} every={6} notes={notes}
          label={`${LABEL} of demand, of wind and solar output and of net demand for ${placeWords(slot.place)}, ${dayWords(ser.target_day)}, by the hour of the place's clock (${tz})`} />
      </ChartFrame>
    </div>
  );
}

/** How the lines of net demand, wind and solar have scored: one row a line and a span, every method the file scores
 *  on the same hours. The score is the page's own choice said for these lines: the error over the mean of the hours
 *  scored, in percent, or the error in MW. */
function LineScores({ slot, ws, metric }: { slot: Slot; ws: WindSolarFile | null; metric: Metric }) {
  const ser = demandOf(slot);
  const net = ser?.net_demand;
  if (!ser || !net) return null;
  const file = fileOf(slot), unit = ser.unit;
  const mw = mwMetricOf(metric);
  const mu = mw === "nmae_pct" ? "% of the mean" : unit;
  const entry = windSolarOf(ws, net.wind_solar_place ?? slot.place.place);
  const words = mw === "nmae_pct" ? "the mean absolute error over the mean of the same hours, in percent (a percent of each hour means nothing where an hour is near zero)" : `the mean absolute error, ${unit}`;
  const cell = (p: MwPart, m: string, key: string, who: string, span: string) => {
    const v = p[mw]?.[m];
    return v === null || v === undefined ? <NotHeld key={m} words={m === "operator" ? "not scored" : "not held"} why={`${lineWords(m)}: no score of ${who} over ${span.toLowerCase()} is in the file.`} />
      : <Num key={m} check={key} raw={v} source={`${lineWords(m)}, ${who}, ${placeWords(slot.place)}, ${span.toLowerCase()} (${spanWords(p)}): ${words}. Every method of this row is scored on the same hours.`}>{mw === "nmae_pct" ? shareWords(v) : valueWords(v, unit)}</Num>;
  };
  const lines: { name: string; who: string; parts: (span: string) => MwPart | null | undefined; key: (span: string, ...rest: string[]) => string }[] = [
    { name: "Net demand", who: "net demand", parts: (span) => net[span as "backtest"], key: (span, ...rest) => pfKey(file, ["series", "demand", "net_demand", span, ...rest]) },
    ...FUELS.flatMap((fuel) => { const f = entry?.place.fuels?.[fuel]; return fuelShown(f) ? [{ name: FUEL_WORDS[fuel], who: `${fuel} output`, parts: (span: string) => f.summary?.[span], key: (span: string, ...rest: string[]) => pfKey(WS_FILE, ["places", entry?.pi ?? 0, "fuels", fuel, "summary", span, ...rest]) }] : []; }),
  ];
  const rows = lines.flatMap((l) => MW_SPANS.flatMap(([span, spanName]) => {
    const p = l.parts(span);
    if (!p) return [];
    // the line and its span are one cell at the left (two columns of words pushed the last method out of a table 840 px wide)
    return [{ key: `${l.name}|${span}`, cells: [<span key="n" title={spanWords(p)} className="cursor-help">{l.name}, {spanName}</span>,
      count(p.hours, l.key(span, "hours"), `The hours scored, ${spanWords(p)}.`), ...FUEL_METHODS.map((m) => cell(p, m, l.key(span, mw, m), l.who, spanName))] }];
  }));
  if (!rows.length) return null;
  return (
    <div className="mb-4 mt-4" data-fc-line-scores={slot.mark}>
      <ToolTable minWidth={560} caption={`${placeWords(slot.place)}: how the ${LABEL} of net demand, of wind and of solar output has scored beside the operator's forecast and two plain rules, ${mu}`}
        head={[<span key="l" className="cursor-help" title={`${words[0].toUpperCase()}${words.slice(1)}.`}>{placeWords(slot.place)}: error, {mu}</span>, "Hours", ...FUEL_METHODS.map((m) => <Head key={m} m={m} what={wordsOfMethod(ws?.methods, m)} />)]}
        rows={rows} />
    </div>
  );
}

// ---- Wind and solar on a past day -----------------------------------------------------------------------------------

/** A past day of wind and of solar output for one place: the ERW forecast made for it beside what happened. The day is
 *  the one asked for where the wind and solar file holds it, else the newest day it holds. */
export function WindSolarDay({ slot, ws, asked }: { slot: Slot; ws: WindSolarFile | null; asked: string | null }) {
  const ser = demandOf(slot);
  const net = ser?.net_demand;
  const entry = ser && net ? windSolarOf(ws, net.wind_solar_place ?? slot.place.place) : null;
  if (!ser || !entry) return <div className="min-w-0" data-fc-wsday={slot.mark} data-fc-wsday-of="none" />;
  const tz = slot.place.time, unit = ser.unit, k = slot.mark;
  const fuels = FUELS.map((fuel) => ({ fuel, f: entry.place.fuels?.[fuel] ?? null })).filter((x): x is { fuel: FuelKey; f: FuelSeries } => fuelShown(x.f)).map((x) => ({ ...x, hours: lineHours(x.f.history_columns, x.f.history, "operator") }));
  const all = fuels.flatMap((x) => x.hours);
  const days = lineDays(all);
  const day = asked && days.includes(asked) ? asked : lineDefaultDay(all);
  if (!fuels.length || !day) return <div className="min-w-0" data-fc-wsday={k} data-fc-wsday-of="none" />;
  const of = fuels.map((x) => x.hours.filter((h) => h.day === day));
  const x = of[0].length ? of[0] : of[1] ?? [];
  const series: CatSeries[] = fuels.flatMap((f, i): CatSeries[] => [
    // short names, as in the chart of the day forecast now: the title says these are the ERW forecast's lines, and
    // what happened is the dashed line of the same color
    { name: FUEL_WORDS[f.fuel], color: FUEL_COLOR[f.fuel], kind: "line", values: of[i].map((h) => h.erw) },
    ...(of[i].some((h) => h.actual !== null) ? [{ name: `${FUEL_WORDS[f.fuel]}, ${ACTUAL}`, color: FUEL_COLOR[f.fuel], kind: "line" as const, dash: "dashed" as const, values: of[i].map((h) => h.actual) }] : []),
  ]);
  const notes = x.map((h, j) => `Hour beginning ${localWords(h.ts, tz)}.${fuels.map((f, i) => { const r = of[i][j]; return r && r.lo !== null && r.hi !== null ? ` ${FUEL_WORDS[f.fuel]}, band: ${valueWords(r.lo, unit)} to ${valueWords(r.hi, unit)} ${unit}${r.other !== null ? `; the operator's forecast ${valueWords(r.other, unit)} ${unit}` : ""}.` : ""; }).join("")}`);
  return (
    <div className="min-w-0" data-fc-wsday={k} data-fc-wsday-of={day} data-fc-hours={x.length}>
      <ChartFrame title={`${dayWords(day)}: ${LABEL} of wind and solar, and what happened`}
        tip={<> <Hint words="source" why={`${LABEL}: a model's output (tier derived), not a published figure; ${ws?.made_rule ?? "the hour it is made is not in the file"}. ${fuels.map((f) => `${FUEL_WORDS[f.fuel]}: ${f.f.target_series ?? "the place's output"}, method ${lineWords(f.f.method ?? "not said")}`).join(". ")}. What happened is drawn dashed. The file holds ${days[days.length - 1]} to ${days[0]} of this place's clock${asked && asked !== day ? `; ${asked} is not among them, so the newest day held is drawn` : ""}. site/data/${WS_FILE}.`} /></>}>
        <CategoryChart id={`fc-wsday-${k}`} x={x.map((h) => hourWords(h.hour))} series={series} unit={unit} height={260} every={6} notes={notes}
          label={`${LABEL} of wind and solar output for ${placeWords(slot.place)} on ${dayWords(day)}, beside what happened, by the hour of the place's clock (${tz})`} />
      </ChartFrame>
    </div>
  );
}

// ---- The operator's filed forecast, checked by month ----------------------------------------------------------------

/** The check of the comparator: by month, the forecast the operator filed on Form EIA-930 as a percent of the demand it
 *  forecasts. Where months are flagged the page says the filed forecast is not the operator's own in those months, and
 *  sets the scores on the months that pass beside those on every month. Every month is in a fold. */
export function FilingCheck({ slot, scores, metric }: { slot: Slot; scores: ScoresFile | null; metric: Metric }) {
  const ser = demandOf(slot);
  const f = ser?.operator_filing;
  if (!ser || !f) return <div className="min-w-0" data-fc-filing={slot.mark} data-fc-filing-months="none" />;
  const file = fileOf(slot), unit = ser.unit, mu = metricUnit(metric, unit), k = slot.mark;
  const months = filingMonths(f);
  const flagged = typeof f.months_flagged === "number" ? f.months_flagged : null;
  const held = typeof f.months_held === "number" ? f.months_held : months.length;
  const tol = typeof f.tolerance_pct === "number" ? f.tolerance_pct : null;
  const shift = filingShift(f);
  const path = ["series", "demand", "operator_filing"];
  const sound = f.sound_last_2_years;
  const g = scoresOf(scores, slot.place.place, "demand").get("last_2_years");
  const mcol = scores ? scores.rows_columns.indexOf(metric) : -1;
  const pctAt = (f.months_columns ?? []).indexOf("operator_pct_of_demand"), hoursAt = (f.months_columns ?? []).indexOf("hours");
  const every = (m: string) => {
    const c = g?.cells.get(`|${m}`), v = c ? c[metric] : null;
    return !c || v === null ? <NotHeld key={m} why={`${methodWords(m)}: no score over the last two years is in the score file.`} />
      : <Num key={m} check={pfKey("predict/scores.json", ["rows", c.i, mcol])} raw={v} source={`${methodWords(m)}, ${placeWords(slot.place)}, the last two years, every month: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/predict/scores.json, row ${c.i}.`}>{scoreWords(v, metric, unit)}</Num>;
  };
  const passing = (p: SummaryPart, m: string) => {
    const v = p[metric]?.[m];
    return v === null || v === undefined ? <NotHeld key={m} why={`${methodWords(m)}: no score on the months that pass is in the file.`} />
      : <Num key={m} check={pfKey(file, [...path, "sound_last_2_years", metric, m])} raw={v} source={`${methodWords(m)}, ${placeWords(slot.place)}, the last two years (${spanWords(p)}), on the months whose filing passes the check: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
  };
  const everyHours = g ? Math.max(...FOUR.map((m) => g.cells.get(`|${m}`)?.hours ?? 0)) : 0;
  return (
    <div className="mb-5 min-w-0" data-fc-filing={k} data-fc-filing-months={months.length} data-fc-filing-flagged={flagged ?? "none"}>
      <h4 className="mb-1 text-sm font-semibold"><span className={f.what ? "cursor-help" : undefined} title={f.what ? `The file's words: ${f.what}.` : undefined}>{placeWords(slot.place)}: the operator&apos;s filed forecast, checked by month</span>
        {shift !== null ? <span className="font-normal">, <Hint words={`its hours fit best moved by ${shift}`} why={`The filed forecast's percent error over the last two years with its hours moved by -1, 0 and 1 hour: ${["-1", "0", "1"].map((s) => (typeof f.shift_mape_last_2_years?.[s] === "number" ? `${shareWords(f.shift_mape_last_2_years[s] as number)}%` : "not held")).join(", ")}. Moved by 1, the forecast stamped an hour earlier is set against each hour's demand. The scores on this page set the filing against demand as filed, not moved.`} /></span> : null}</h4>
      {flagged !== null && flagged > 0 ? (
        <>
          <p className="mb-2 text-sm" data-fc-filing-says={k}>In {count(flagged, pfKey(file, [...path, "months_flagged"]), "The months flagged by the check, of the months held.")} of {held.toLocaleString("en-US")} months the forecast filed on Form EIA-930 is more than {tol ?? 5} percent from the demand it forecasts over the whole month. In those months the filed forecast is not the operator&apos;s own forecast.</p>
          <ToolTable minWidth={460} caption={`${placeWords(slot.place)}: ${METRIC_WORDS[metric].toLowerCase()} of each method over the last two years, on every month and on the months whose operator filing passes the check, ${mu}`}
            head={[`The last two years, ${mu}`, "Hours", ...FOUR.map((m) => <Head key={m} m={m} what={methodWhat(scores, m)} />)]}
            rows={[
              { key: "every", cells: ["Every month", everyHours ? everyHours.toLocaleString("en-US") : <NotHeld key="h" why="No count of hours is in the score file." />, ...FOUR.map(every)] },
              ...(sound ? [{ key: "sound", cells: [<span key="n" className="cursor-help" title={`The months whose filed forecast is within ${tol ?? 5} percent of the demand it forecasts.`}>The months that pass</span>, count(sound.hours, pfKey(file, [...path, "sound_last_2_years", "hours"]), `The hours scored on the months that pass, ${spanWords(sound)}.`), ...FOUR.map((m) => passing(sound, m))] }] : []),
            ]} />
        </>
      ) : null}
      <details className="border-b border-rule py-2" data-fc-filing-fold={k}>
        <summary className="cursor-pointer py-1 text-sm">The filing month by month: {held.toLocaleString("en-US")} months, {flagged === null ? "the count flagged not said" : flagged === 0 ? "none flagged" : `${flagged.toLocaleString("en-US")} flagged`}</summary>
        <div className="max-h-[24rem] overflow-y-auto pt-2">
          <ToolTable minWidth={380} caption={`${placeWords(slot.place)}: by month, the forecast the operator filed on Form EIA-930 as a percent of the demand it forecasts, over the hours both hold; a month more than ${tol ?? 5} percent from 100 is flagged`}
            head={["Month", "Hours", <span key="p" className="cursor-help" title="The filed forecast's sum as a percent of the demand's, over the hours of the month both hold: 100 is a forecast that sums to the demand.">Filed forecast, % of demand</span>, "Check"]}
            rows={months.map((m) => ({ key: m.month, highlight: m.flagged, cells: [monthWords(m.month),
              count(m.hours, pfKey(file, [...path, "months", m.i, hoursAt]), `The hours of ${monthWords(m.month)} both the filed forecast and the demand hold.`),
              m.pct === null ? <NotHeld key="p" why="No percent is in the file for this month." /> : <Num key="p" check={pfKey(file, [...path, "months", m.i, pctAt])} raw={m.pct} source={`${monthWords(m.month)}: the filed forecast's sum as a percent of the demand's. site/data/${file}.`}>{shareWords(m.pct)}</Num>,
              <span key="c" data-fc-filing-month={m.flagged ? "flagged" : "passes"}>{m.flagged ? "flagged" : "passes"}</span>] }))} />
        </div>
      </details>
    </div>
  );
}

// ---- The separate line "with the weather forecast" ------------------------------------------------------------------

/** The regression with the National Weather Service's forecast for an airport of the place: a separate line, never the
 *  ERW forecast and in no chart of one. Its scores on the days such a forecast is held, beside the same coefficients on
 *  the airport's observed weather (not a forecast) and the methods on the same hours; below the file's own minimum of
 *  days the heading says too few days to judge. Its hours for the day forecast now are behind a fold. */
export function WeatherForecastLine({ slot, scores, metric }: { slot: Slot; scores: ScoresFile | null; metric: Metric }) {
  const ser = demandOf(slot);
  const w = ser?.with_weather_forecast;
  if (!ser || !w) return <div className="min-w-0" data-fc-wwf={slot.mark} data-fc-wwf-days="none" />;
  const file = fileOf(slot), unit = ser.unit, mu = metricUnit(metric, unit), tz = slot.place.time, k = slot.mark;
  const path = ["series", "demand", "with_weather_forecast"];
  const few = tooFewDays(w);
  const p = w.all;
  const hours = hourValues(w.tomorrow_columns, w.tomorrow, "with_weather_forecast");
  const col = (w.tomorrow_columns ?? []).indexOf("with_weather_forecast");
  const erw = new Map(tomorrowOf(ser).map((h) => [h.ts, h]));
  const notForecast = `Not the ${LABEL}: a separate line. ${w.what ?? "The regression with the weather, applied with the National Weather Service's hourly forecast for an airport."}`;
  return (
    <div className="mb-5 min-w-0" data-fc-wwf={k} data-fc-wwf-days={w.days ?? "none"} data-fc-wwf-few={few ? "1" : "0"}>
      <h4 className="mb-1 text-sm font-semibold"><span className="cursor-help" title={notForecast}>{placeWords(slot.place)}: {WEATHER_FORECAST_LABEL.toLowerCase()}</span> (a separate line, not the {LABEL}){w.airport ? `, ${w.airport}` : ""}:{" "}
        {typeof w.days === "number" ? <>{count(w.days, pfKey(file, [...path, "days"]), "The days on which such a weather forecast is held and scored.")} {typeof w.min_days === "number" ? `of the ${w.min_days} days needed` : "days"}</> : "the days held are not said"}{few ? ", too few days to judge" : ""}, {mu}</h4>
      {p ? (
        <ToolTable minWidth={640} caption={`${placeWords(slot.place)}: ${METRIC_WORDS[metric].toLowerCase()} of the separate line with the weather forecast, of the same line with the airport's weather known, and of the methods on the same hours, ${mu}${few ? "; too few days to judge" : ""}`}
          head={["Days held", "Hours", ...WEATHER_FORECAST_METHODS.map((m) => <Head key={m} m={m} what={m === "with_weather_forecast" ? notForecast : m === "with_airport_weather_known" ? "the same coefficients applied to the airport's observed temperature: not a forecast, so the cost of the weather forecast's own error is seen" : methodWhat(scores, m)} />)]}
          rows={[{ key: "all", cells: [<span key="s" className="whitespace-nowrap">{spanWords(p)}</span>, count(p.hours, pfKey(file, [...path, "all", "hours"]), `The hours scored, ${spanWords(p)}.`),
            ...WEATHER_FORECAST_METHODS.map((m) => {
              const v = p[metric]?.[m];
              return v === null || v === undefined ? <NotHeld key={m} why={`${lineWords(m)}: no score on these hours is in the file.`} />
                : <Num key={m} check={pfKey(file, [...path, "all", metric, m])} raw={v} source={`${lineWords(m)}, ${placeWords(slot.place)}, ${spanWords(p)}: ${METRIC_WORDS[metric].toLowerCase()}, ${mu}, on the hours the weather forecast is held${few ? "; too few days to judge" : ""}. site/data/${file}.`}>{scoreWords(v, metric, unit)}</Num>;
            })] }]} />
      ) : <p className="text-sm"><NotHeld why="The file holds no score of this line yet." /></p>}
      {hours.some((h) => h.v !== null) ? (
        <details className="border-b border-rule py-2" data-fc-wwf-fold={k}>
          <summary className="cursor-pointer py-1 text-sm">Its line for {dayWords(ser.target_day)}, hour by hour, beside the {LABEL}</summary>
          <div className="pt-2">
            <ToolTable minWidth={380} caption={`${placeWords(slot.place)}, ${dayWords(ser.target_day)}: the separate line with the weather forecast beside the ${LABEL}, hour by hour, ${unit}`}
              head={["Hour", <span key="w" className="cursor-help" title={`${notForecast}${w.tomorrow_issue_utc ? ` The weather forecast read was issued ${utcWords(w.tomorrow_issue_utc)}.` : ""}`}>{WEATHER_FORECAST_LABEL}</span>, LABEL]}
              rows={hours.map((h) => {
                const e = erw.get(h.ts);
                return { key: h.ts, cells: [<span key="h" title={`The hour beginning ${localWords(h.ts, tz)} (${utcWords(h.ts)})`} className="cursor-help">{hourWords(h.hour)}</span>,
                  h.v === null ? <NotHeld key="w" why="No value of the line is held for this hour." /> : <Num key="w" check={pfKey(file, [...path, "tomorrow", h.i, col])} raw={h.v} source={`${WEATHER_FORECAST_LABEL}: a separate line, not the ${LABEL}. site/data/${file}.`}>{valueWords(h.v, unit)}</Num>,
                  e && e.erw !== null ? <Num key="e" check={pfKey(file, ["series", "demand", "tomorrow", e.i, ser.tomorrow_columns.indexOf("erw")])} raw={e.erw} source={`${LABEL} of demand. site/data/${file}.`}>{valueWords(e.erw, unit)}</Num> : <NotHeld key="e" why="No forecast is held for this hour." />] };
              })} />
          </div>
        </details>
      ) : null}
    </div>
  );
}

// ---- The band --------------------------------------------------------------------------------------------------------

/** `short`: the line's name at its end in the chart (the chart's title says whose bands these are). */
type BandRow = { name: string; short: string; rule: string | null | undefined; b: BandCoverage; key: (...rest: (string | number)[]) => string; color: string };
/** How often what happened fell inside the band, below it and above it: one row a line of the place (the series
 *  chosen; with demand, the wind and solar lines its net demand names), the share inside by the hour of the day as a
 *  chart, and by month in a fold. */
export function BandCheck({ slot, s, ws }: { slot: Slot; s: SeriesKey; ws: WindSolarFile | null }) {
  const ser = slot.file?.series?.[s];
  if (!isShown(slot.file, ser) || !ser) return <div className="min-w-0" data-fc-band={slot.mark} data-fc-band-rows="0" />;
  const file = fileOf(slot), k = slot.mark;
  const rows: BandRow[] = [];
  if (ser.band_coverage) rows.push({ name: `${LABEL} of ${SERIES_WORDS[s].toLowerCase()}`, short: SERIES_WORDS[s], rule: ser.band, b: ser.band_coverage, key: (...rest) => pfKey(file, ["series", s, "band_coverage", ...rest]), color: "accent" });
  const entry = s === "demand" && ser.net_demand ? windSolarOf(ws, ser.net_demand.wind_solar_place ?? slot.place.place) : null;
  if (entry) for (const fuel of FUELS) {
    const f = entry.place.fuels?.[fuel];
    if (fuelShown(f) && f.band_coverage) rows.push({ name: `${LABEL} of ${fuel}`, short: FUEL_WORDS[fuel], rule: f.band, b: f.band_coverage, key: (...rest) => pfKey(WS_FILE, ["places", entry.pi, "fuels", fuel, "band_coverage", ...rest]), color: FUEL_COLOR[fuel] });
  }
  if (!rows.length) return <div className="min-w-0" data-fc-band={k} data-fc-band-rows="0" />;
  const nominal = rows.map((r) => r.b.nominal_pct).find((v): v is number => typeof v === "number") ?? null;
  const byHour = rows.filter((r) => (r.b.by_local_hour_inside_pct ?? []).length === 24);
  const share = (r: BandRow, field: "inside_pct" | "below_pct" | "above_pct", what: string) => {
    const v = r.b[field];
    return v === null || v === undefined ? <NotHeld key={field} why="No share is in the file." /> : <Num key={field} check={r.key(field)} raw={v} source={`${r.name}, ${placeWords(slot.place)}: ${what}, in percent.${r.rule ? ` The band: ${r.rule}.` : ""}`}>{shareWords(v)}</Num>;
  };
  return (
    <div className="mb-5 min-w-0" data-fc-band={k} data-fc-band-rows={rows.length}>
      <h4 className="mb-1 text-sm font-semibold">{placeWords(slot.place)}: the band, and how often what happened fell inside it{nominal !== null ? <span className="font-normal"> (a band made to hold {nominal} percent of hours)</span> : null}</h4>
      <ToolTable minWidth={440} caption={`${placeWords(slot.place)}: of the past hours scored, the share on which what happened fell inside the band of the ${LABEL}, below it and above it, in percent`}
        head={["Band of", "Hours scored", ...BAND_SHARES.map(([field, name, what]) => <span key={field} className="cursor-help" title={`${what[0].toUpperCase()}${what.slice(1)}, in percent.`}>{name}, %</span>)]}
        rows={rows.map((r) => ({ key: r.name, cells: [<span key="n" className={r.rule ? "cursor-help" : undefined} title={r.rule ? `The band: ${r.rule}.` : undefined}>{r.name}</span>,
          count(r.b.hours, r.key("hours"), "The past hours scored: those that hold a forecast, its band and what happened."), ...BAND_SHARES.map(([field, , what]) => share(r, field, what))] }))} />
      {byHour.length ? (
        <div className="mt-3">
          <ChartFrame title={`Inside the band of the ${LABEL}, by the hour of the day`} tip={<> <Hint words="source" why={`Of the past hours scored at each hour of the place's clock, the share on which what happened fell inside the band, in percent. ${rows.map((r) => (r.rule ? `${r.name}: ${r.rule}.` : "")).filter(Boolean).join(" ")}`} /></>}>
            <CategoryChart id={`fc-band-${k}`} x={Array.from({ length: 24 }, (_, h) => hourWords(h))} unit="%" zero={false} height={200} every={6}
              series={byHour.map((r) => ({ name: r.short, color: r.color, kind: "line" as const, values: (r.b.by_local_hour_inside_pct ?? []).map((v) => (typeof v === "number" ? v : null)) }))}
              refLines={nominal !== null ? [{ value: nominal, name: `${nominal}%`, dashed: true }] : undefined}
              label={`${placeWords(slot.place)}: the share of past hours on which what happened fell inside the band of the ${LABEL}, by the hour of the place's clock, in percent`} />
          </ChartFrame>
        </div>
      ) : null}
      {rows.map((r, ri) => {
        const months = bandMonths(r.b);
        const at = (n: string) => (r.b.by_month_columns ?? []).indexOf(n);
        return months.length ? (
          <details key={r.name} className="border-b border-rule py-2" data-fc-band-fold={`${k}|${ri}`}>
            <summary className="cursor-pointer py-1 text-sm">{r.name}: inside the band month by month ({months.length} months)</summary>
            <div className="max-h-[24rem] overflow-y-auto pt-2">
              <ToolTable minWidth={320} caption={`${r.name}, ${placeWords(slot.place)}: by month, the share of the hours scored on which what happened fell inside the band, in percent`}
                head={["Month", "Hours", "Inside the band, %"]}
                rows={months.map((m) => ({ key: m.month, cells: [monthWords(m.month), count(m.hours, r.key("by_month", m.i, at("hours")), `The hours of ${monthWords(m.month)} scored.`),
                  m.inside === null ? <NotHeld key="i" why="No share is in the file for this month." /> : <Num key="i" check={r.key("by_month", m.i, at("inside_pct"))} raw={m.inside} source={`${r.name}, ${monthWords(m.month)}: the share of the hours scored inside the band, in percent.`}>{shareWords(m.inside)}</Num>] }))} />
            </div>
          </details>
        ) : null;
      })}
    </div>
  );
}
