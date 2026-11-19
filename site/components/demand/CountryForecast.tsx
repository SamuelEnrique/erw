// Session 8013 (chain 505, part D3, 19 November 2026): "Forecast against actual", a section of the country view of
// /demand (components/demand/Country.tsx, ?view=country). For each of the two places chosen: the day-ahead demand
// forecast its balancing authorities file on Form EIA-930 beside the demand that came (the data machine's
// forecast/<region>.json and forecast/ba/<code>.json, contract section 11, warehouse/derived/forecast_error.py), and,
// for California and Texas, the grid operator's own wind and solar forecasts beside the output (forecast/renewables.json,
// section 12). Every figure is read from those files and carries its source on hover; a file not on the site says so and
// draws nothing. No forecast of the ERW's own. Add, never change: the sections before it are not touched.
import { Hint } from "@/components/demand/Hint";
import { TimeChart } from "@/components/TimeChart";
import { ChartFrame, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { readRegionFile } from "@/lib/countryfiles";
import type { Place } from "@/lib/countrydemand";

type Stats = { hours: number; mape_pct: number | null; wape_pct: number | null; bias_pct: number | null; mae_mw: number | null; bias_mw: number | null };
type DayRow = { day: string; temp_f?: number; mape_pct: number; bias_mw: number; peak_forecast_mw: number; peak_demand_mw: number; peak_miss_pct: number };
type EventRow = Stats & { event: string; title: string; start: string; end: string; peak_miss_pct?: number };
export type ForecastFile = {
  code: string; name: string; level: string; tz: string; first_hour: string; last_hour: string; license?: string; tables?: string[];
  overall: Stats & { screened_hours: number; screen: string };
  by_hour: { mape_pct: (number | null)[]; bias_pct: (number | null)[]; hours: number[] };
  by_season: Record<string, Stats & { words: string }>;
  by_year: Record<string, Stats>;
  daily: { days: string[]; mape_pct: number[]; bias_mw: number[] };
  hottest_days: DayRow[] | null; coldest_days: DayRow[] | null; weather?: { why?: string };
  events: EventRow[];
};
type RStats = { hours: number; mae_mw: number | null; bias_mw: number | null; wape_pct: number | null; bias_pct: number | null; forecast_mean_mw: number | null; actual_mean_mw: number | null };
type RSeries = { first_hour: string; last_hour: string; overall: RStats };
type RenewGrid = { grid: string; region: string; code: string; table: string; forecast: string; actual: string; series: Record<"wind" | "solar", RSeries> };
type RenewFile = { grids: RenewGrid[]; not_held: { grid: string; why: string }[] };
export type ForecastSlot = { mark: "a" | "b"; place: Place; name: string };

const SRC = "Source: EIA, Form EIA-930: each balancing authority's day-ahead demand forecast beside its demand for the same hour (table eia930_forecast_error_hourly, through the place's page file; method docs/methods/forecast_error.md).";
const f1 = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? null : v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }));
const w0 = (v: number | null | undefined) => (v === null || v === undefined ? null : Math.round(v).toLocaleString("en-US"));
const sg = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? null : `${v > 0 ? "+" : v < 0 ? "-" : ""}${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })}`);
const N = ({ k, why, children }: { k: string; why: string; children: string | null }) =>
  children === null ? <span className="cursor-help text-muted" title={`Not held. ${why}`} data-not-held="1">not held</span> : <span data-n={k} title={why} className="cursor-help">{children}</span>;
const path = (p: Place) => (p.level === "region" ? `forecast/${p.code.toLowerCase()}.json` : `forecast/ba/${p.code.toLowerCase()}.json`);
/** The operator grid whose wind and solar forecasts belong to a place: California and CAISO, Texas and ERCOT. */
const renewOf = (p: Place, r: RenewFile | null) => r?.grids.find((g) => (p.level === "region" ? g.region === p.code : g.code === p.code)) ?? null;

export function CountryForecast({ slots, two }: { slots: ForecastSlot[]; two: string }) {
  const files = slots.map((s) => ({ s, f: readRegionFile<ForecastFile>(path(s.place)) }));
  const renew = readRegionFile<RenewFile>("forecast/renewables.json");
  const k = (s: ForecastSlot, x: string) => `cdf|${s.mark}|${x}`;
  const notOn = (s: ForecastSlot) => `The forecast file of ${s.name} (site/data/regions/${path(s.place)}) is not on the site: either the place files no day-ahead forecast with EIA, or the data machine has not written it. No figure is drawn.`;
  const summary = files.map(({ s, f }) => {
    if (!f) return { key: s.mark, cells: [s.name], wide: <span className="cursor-help text-muted" title={notOn(s)} data-cdf-none={s.mark}>not held</span> };
    const o = f.overall;
    const span = `${f.first_hour.slice(0, 10)} to ${f.last_hour.slice(0, 10)}`;
    return {
      key: s.mark,
      cells: [s.name,
        <N key="h" k={k(s, "hours")} why={`${SRC} Hours with both a forecast and a demand, ${span}; ${o.screened_hours} left out by the screen (${o.screen}).`}>{w0(o.hours)}</N>,
        <span key="sp" title={`${SRC} UTC hours ${f.first_hour} to ${f.last_hour}.`} className="cursor-help">{span}</span>,
        <N key="m" k={k(s, "mape")} why={`${SRC} The mean of each hour's miss as a percent of that hour's demand.`}>{f1(o.mape_pct, 2)}</N>,
        <N key="w" k={k(s, "wape")} why={`${SRC} The absolute misses summed over the demand summed, percent.`}>{f1(o.wape_pct, 2)}</N>,
        <N key="b" k={k(s, "bias")} why={`${SRC} The mean miss (forecast less demand) as a percent of the mean demand; above zero, the forecast ran high.`}>{sg(o.bias_pct, 2)}</N>,
        <N key="a" k={k(s, "mae")} why={`${SRC} The mean absolute miss, MW.`}>{w0(o.mae_mw)}</N>,
        <N key="bm" k={k(s, "biasmw")} why={`${SRC} The mean miss, MW.`}>{sg(o.bias_mw, 0)}</N>],
    };
  });
  const drawn = files.filter((x): x is { s: ForecastSlot; f: ForecastFile } => !!x.f);
  const seasons = ["DJF", "MAM", "JJA", "SON"];
  return (
    <ToolSection title="Forecast against actual" id="forecast"
      note={<><Hint words="What is compared" why="Every balancing authority files with EIA, for each hour, its forecast of demand made the day before (Form EIA-930). Here that forecast is set beside the demand that came for the same hour; a region's forecast is the sum of its authorities' forecasts for an hour every one of them holds. A miss is the forecast less the demand. No forecast of the ERW's own." />.{" "}
        <Hint words="Wind and solar" why="For California and Texas, the grid operator's own day-ahead forecasts of wind and solar output beside the output (CAISO's OASIS report SLD_REN_FCST; ERCOT's NP4-732-CD and NP4-745-CD). The other grids' forecasts are not drawn: each reason is in the file and on the row's hover." /></>}>
      <div data-cdf="1">
        <ToolTable minWidth={900} caption="The day-ahead demand forecast against the demand that came, every hour held"
          head={["Place", "Hours", "Span", "Mean miss, % of demand", "Absolute misses over demand, %", "Bias, %", "Mean absolute miss, MW", "Bias, MW"]}
          rows={summary} />
        {drawn.length ? (
          <>
            <div className={two}>
              {drawn.map(({ s, f }) => {
                const pts = f.daily.days.map((d, i) => [Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10)), f.daily.mape_pct[i] ?? null] as [number, number | null]);
                return (
                  <div key={s.mark} className="min-w-0" data-cdf-daily={s.mark} data-cdf-points={pts.length}>
                    <ChartFrame title={`${s.name}: the day's mean miss, % of demand`} tip={SRC}>
                      <TimeChart x="day" unit="%" height={220} ariaLabel={`${s.name}: each whole local day's mean hourly miss of the day-ahead forecast, percent of demand`}
                        series={[{ name: "Mean miss, % of demand", color: "accent", points: pts }]} />
                    </ChartFrame>
                  </div>
                );
              })}
            </div>
            <ToolTable minWidth={720} caption="By season (local months), every year held: mean miss and bias, % of demand"
              head={["Season", ...drawn.flatMap(({ s }) => [`${s.name}: mean miss, %`, `${s.name}: bias, %`])]}
              rows={seasons.map((z) => ({ key: z, cells: [drawn[0].f.by_season[z]?.words ?? z, ...drawn.flatMap(({ s, f }) => [
                <N key={`${s.mark}m`} k={k(s, `season|${z}|mape`)} why={`${SRC} ${f.by_season[z]?.hours ?? 0} hours.`}>{f1(f.by_season[z]?.mape_pct, 2)}</N>,
                <N key={`${s.mark}b`} k={k(s, `season|${z}|bias`)} why={SRC}>{sg(f.by_season[z]?.bias_pct, 2)}</N>])] }))} />
            <ToolTable minWidth={720} caption="By the local hour of the day: mean miss, % of demand (17:00 is the hour from 17:00 to 18:00)"
              head={["Hour", ...drawn.map(({ s }) => `${s.name}: mean miss, %`)]}
              rows={Array.from({ length: 24 }, (_, h) => ({ key: String(h), cells: [`${String(h).padStart(2, "0")}:00`, ...drawn.map(({ s, f }) =>
                <N key={s.mark} k={k(s, `hour|${h}|mape`)} why={`${SRC} ${f.by_hour.hours[h] ?? 0} hours at this local hour (${f.tz}).`}>{f1(f.by_hour.mape_pct[h], 2)}</N>)] }))} />
            {drawn.map(({ s, f }) => (
              <div key={s.mark} className="mb-6" data-cdf-extremes={s.mark}>
                <h3 className="mb-1 text-base">{s.name}: the hottest and coldest days, and the nine events</h3>
                {f.hottest_days && f.coldest_days ? (
                  <ToolTable minWidth={720} caption={`${s.name}: the three hottest and three coldest whole days by the region's daily mean temperature`}
                    head={["Day", "Mean temperature, F", "Mean miss, %", "Peak forecast, MW", "Peak demand, MW", "Peak miss, %"]}
                    rows={[...f.hottest_days.slice(0, 3), ...f.coldest_days.slice(0, 3)].map((d, i) => ({ key: `${i}${d.day}`, cells: [d.day,
                      <N key="t" k={k(s, `day|${d.day}|temp`)} why="The daily mean of the region's population-weighted hourly temperature (table region_weather_hourly).">{f1(d.temp_f, 1)}</N>,
                      <N key="m" k={k(s, `day|${d.day}|mape`)} why={SRC}>{f1(d.mape_pct, 2)}</N>,
                      <N key="f" k={k(s, `day|${d.day}|pf`)} why={SRC}>{w0(d.peak_forecast_mw)}</N>,
                      <N key="d" k={k(s, `day|${d.day}|pd`)} why={SRC}>{w0(d.peak_demand_mw)}</N>,
                      <N key="p" k={k(s, `day|${d.day}|pm`)} why={`${SRC} The day's highest forecast hour less its highest demand hour, percent of the highest demand.`}>{sg(d.peak_miss_pct, 2)}</N>] }))} />
                ) : <p className="text-sm"><span className="cursor-help text-muted" title={f.weather?.why ?? "No weather is held for this place."}>Hottest and coldest days: not held</span></p>}
                <ToolTable minWidth={720} caption={`${s.name}: the nine events of /events, over each event's local days`}
                  head={["Event", "Hours", "Mean miss, %", "Bias, MW", "Peak miss, %"]}
                  rows={f.events.map((e) => ({ key: e.event, cells: [<span key="e" title={`${e.start} to ${e.end}`} className="cursor-help">{e.title}</span>,
                    <N key="h" k={k(s, `event|${e.event}|hours`)} why={SRC}>{w0(e.hours)}</N>,
                    <N key="m" k={k(s, `event|${e.event}|mape`)} why={SRC}>{e.hours ? f1(e.mape_pct, 2) : null}</N>,
                    <N key="b" k={k(s, `event|${e.event}|bias`)} why={SRC}>{e.hours ? sg(e.bias_mw, 0) : null}</N>,
                    <N key="p" k={k(s, `event|${e.event}|peak`)} why={SRC}>{e.hours ? sg(e.peak_miss_pct, 2) : null}</N>] }))} />
              </div>
            ))}
          </>
        ) : null}
        {slots.map((s) => {
          const g = renewOf(s.place, renew);
          if (!g) return null;
          const why = (kind: string) => `Source: ${g.forecast}, beside ${g.actual} (table ${g.table}; method docs/methods/renewable_forecast_error.md). The ${kind} hours holding both.`;
          return (
            <div key={`r${s.mark}`} className="mb-6" data-cdf-renew={g.grid}>
              <h3 className="mb-1 text-base">{s.name}: {g.grid}&apos;s own wind and solar forecasts against the output</h3>
              <ToolTable minWidth={720} caption={`${g.grid}: the day-ahead forecast of wind and solar output against the output, every hour holding both`}
                head={["Source", "Hours", "Span", "Absolute misses over output, %", "Bias, MW", "Mean forecast, MW", "Mean output, MW"]}
                rows={(["wind", "solar"] as const).map((kind) => { const x = g.series[kind]; const o = x.overall; return { key: kind, cells: [kind === "wind" ? "Wind" : "Solar",
                  <N key="h" k={k(s, `renew|${kind}|hours`)} why={why(kind)}>{w0(o.hours)}</N>,
                  <span key="sp" title={`${x.first_hour} to ${x.last_hour}, UTC`} className="cursor-help">{x.first_hour.slice(0, 10)} to {x.last_hour.slice(0, 10)}</span>,
                  <N key="w" k={k(s, `renew|${kind}|wape`)} why={why(kind)}>{f1(o.wape_pct, 2)}</N>,
                  <N key="b" k={k(s, `renew|${kind}|bias`)} why={`${why(kind)} A miss is the forecast less the output.`}>{sg(o.bias_mw, 0)}</N>,
                  <N key="f" k={k(s, `renew|${kind}|fc`)} why={why(kind)}>{w0(o.forecast_mean_mw)}</N>,
                  <N key="a" k={k(s, `renew|${kind}|act`)} why={why(kind)}>{w0(o.actual_mean_mw)}</N>] }; })} />
            </div>
          );
        })}
        {renew ? <p className="text-xs text-muted" data-cdf-not-held={renew.not_held.length}>Wind and solar forecasts not drawn: {renew.not_held.map((n, i) => <span key={n.grid}>{i ? ", " : ""}<span className="cursor-help border-b border-dotted border-muted" title={n.why}>{n.grid}</span></span>)}.</p> : null}
      </div>
    </ToolSection>
  );
}
