import Link from "next/link";
import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { ChangeBars, DOWN, Heat, UP, YearsChart } from "@/components/demand/Growth";
import { Hint } from "@/components/demand/Hint";
import { Hover } from "@/components/demand/Hover";
import { Explained } from "@/components/demand/Weather";
import { SiteLink } from "@/components/SiteLink";
import { TimeChart } from "@/components/TimeChart";
import { ChartFrame, Fold, ToolHeader, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  FIRST_A, FIRST_B, FIRST_WHY, NEWEST_DAYS, alikeRows, areaOf, baOf, countryHref, dailyPoints, dailySummary, dailyYears, dayWords, demandPlaceFile, gridWords,
  isNewRegion, newestDays, noWeather, periodOf, placeFilePath, placeKey, placeName, placeOf, regionOfIndex, regionRows, regionsIndex, samePlace, sentence, trainOf, utcHourWords,
  type DemandPlaceFile, type IndexFile, type Place,
} from "@/lib/countrydemand";
import { GRID_NAME, NEW_REGIONS, REGION_NAME, gwh } from "@/lib/countryfiles";
import { byHour, byMonth, cells, extremes, hourName, localHour, monthName, signed, slugOf, whole, wholeYears, yearToDate, type Area, type Period } from "@/lib/demandgrowth";
import { METHODS } from "@/lib/demandpage";
import { FIGURES, figureOf, lastWholeYear, one, reading, signed as signed1, years as weatherYears, type Figure, type Grid } from "@/lib/demandweather";
import { LICENSE_NEEDED, licenseNeeded, licenseTitle } from "@/lib/license";

// Session 8420 (chain 503, part C): "The whole country", the fourth view of /demand (lib/demandpage.ts, ?view=country).
// The three views before it draw seven grids and the Lower 48; this one draws any of EIA's thirteen regions of the lower
// 48 and any balancing authority that files with EIA, two side by side (place A and place B), from the data machine's
// page files (site/data/regions/index.json, demand/<region>.json, demand/ba/<code>.json; the contract is
// docs/state/page_files_regions.md, read by lib/countrydemand.ts): demand by day, year by year, where the growth sits
// by month and hour, a region's growth with the weather taken out, and a region beside the grid that covers nearly its
// ground. The charts are the page's own (components/demand/Growth.tsx, Weather.tsx, components/TimeChart.tsx), and the
// figures are read with the page's own functions (lib/demandgrowth.ts, lib/demandweather.ts). Add, never change: the
// other views are not touched (scripts/test-demand-pin.mjs). Until a file is on the site its place says so and draws
// no figure. Facts and no view; nothing filled, interpolated or scaled.

type Q = Record<string, string | undefined>;
type State = "drawn" | "held" | "not-built" | "no-demand";
type Row = { key: string; cells: ReactNode[]; highlight?: boolean; muted?: boolean; wide?: ReactNode };
type Slot = { mark: "a" | "b"; place: Place; key: string; name: string; file: DemandPlaceFile | null; state: State; why: string; area: Area | null; period: Period | null };

/** Why a file is held, or null: its own license line is not "public", or a table it names is "license needed" in the
 *  status file (data/license_status.json). The rule of the events pages' section (app/events/WholeCountry.tsx, heldWhy). */
export function heldWhyOf(file: { tables?: string[]; license?: string }): string | null {
  const t = (file.tables ?? []).find((x) => licenseNeeded(x));
  if (t) return `${LICENSE_NEEDED}: ${licenseTitle(t)}`;
  if (file.license && file.license !== "public") return `${LICENSE_NEEDED}: the file's license line reads "${file.license}"`;
  return null;
}

const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = ({ why }: { why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">not held</span>;
const Held = ({ why }: { why: string }) => <span className="inline-block min-w-8 cursor-help" title={why} data-license-held="1" aria-label={LICENSE_NEEDED}>&nbsp;</span>;
const Head = ({ words, why, mark }: { words: string; why: string; mark: string }) => <span title={why} data-cd-head={mark} className="cursor-help border-b border-dotted border-white">{words}</span>;
const two = "grid gap-x-6 md:grid-cols-2";

/** What a place is, for the hover of its name. */
function placeWords(s: { place: Place; name: string; file: DemandPlaceFile | null }, index: IndexFile | null): string {
  const { place, name, file } = s;
  if (place.level === "region") {
    const r = regionOfIndex(index, place.code);
    const summed = file?.bas_summed ?? [];
    const grids = gridWords(r?.grids ?? regionRows(null).find((x) => x.code === place.code)?.grids);
    return `${name}, EIA's region ${place.code} of Form EIA-930.${summed.length === 1 ? ` Its demand is that of the one balancing authority in it that files demand (${summed[0]}).` : summed.length ? ` Its demand is the sum of the ${summed.length} balancing authorities that file demand (${summed.join(", ")}), written for an hour only when every one of them holds it.` :" Its demand is the sum of its balancing authorities that file demand, written for an hour only when every one of them holds it."}${grids.length ? ` ${grids.join(" and ")} ${grids.length > 1 ? "are" : "is"} among its balancing authorities.` : ""}${isNewRegion(place.code) ? " No page of the site drew this region before 19 November 2026: none of the seven grids is in it." : ""}${file?.tz ? ` Days, months and years are counted in ${file.tz}.` : ""}`;
  }
  const b = baOf(index, place.code);
  const region = b?.region ? ` EIA places it in its region ${REGION_NAME[b.region] ?? b.region}.` : "";
  return `${name} (${place.code}), a balancing authority that files Form EIA-930.${region}${b?.grid ? ` It is ${GRID_NAME[b.grid] ?? b.grid}, one of the seven grids of the other views.` : ""}${b?.retired ? ` EIA gives it as retired on ${b.retired}.` : ""}${file?.tz ?? b?.tz ? ` Days, months and years are counted in ${file?.tz ?? b?.tz}.` : ""}`;
}

/** One place of the address, with its file read and what state it is in. */
function slotOf(mark: "a" | "b", place: Place, index: IndexFile | null, fileOf: (p: Place) => DemandPlaceFile | null): Slot {
  const file = fileOf(place);
  const name = placeName(place, index, file);
  const key = placeKey(place);
  if (!file) {
    const b = place.level === "ba" ? baOf(index, place.code) : null;
    if (b && (b.generation_only || (b.files && !b.files.includes("demand")))) {
      return { mark, place, key, name, file: null, state: "no-demand", why: `${b.generation_only ? `EIA lists ${name} (${place.code}) as a generation-only balancing authority: it files no demand` : `The index lists no demand file for ${name} (${place.code})`}, so there is no demand to draw for it.`, area: null, period: null };
    }
    return { mark, place, key, name, file: null, state: "not-built", why: `The file of ${name} (site/data/regions/${placeFilePath(place)}) is written by the data machine from EIA's Form EIA-930 and is not on the site yet; until it is, no figure is drawn here.`, area: null, period: null };
  }
  const why = heldWhyOf(file);
  return { mark, place, key, name, file, state: why ? "held" : "drawn", why: why ?? "", area: areaOf(file), period: file.growth ? periodOf(file.growth) : null };
}

/** True when a place's file holds what the charts of the years read: the base year, the last whole year, a whole year. */
const hasGrowth = (s: Slot) => !!s.area && !!s.period && Number.isFinite(s.period.base) && Number.isFinite(s.period.last_year) && wholeYears(s.area).length > 0;
/** The month the year so far runs to, by name, or null when the file does not say. */
const throughOf = (p: Period) => (typeof p.ytd_through === "string" && /^\d{4}-\d{2}$/.test(p.ytd_through) ? monthName(Number(p.ytd_through.slice(5))) : null);

/** Session 8450 (the reader's read, row 3): a balancing authority that is one of the seven grids is drawn on two views
 *  from two files, this one's (demand/ba/<code>.json) and the as-metered view's own (data/demand_growth.json). Its name
 *  as the other views write it, or null for any other place. */
export const gridOf = (p: Place): string | null => (p.level === "ba" && GRID_NAME[p.code] && slugOf(p.code) ? GRID_NAME[p.code] : null);
/** The hover beside that link: which file each view reads, and that both figures stand. */
export const gridFileWhy = (p: Place, name: string) => `The as-metered view draws ${GRID_NAME[p.code]} from the page's own file of the seven grids (EIA's Form EIA-930, read for that one authority; docs/methods/demand_growth.md). This view draws ${name} from the file written for every balancing authority (site/data/regions/${placeFilePath(p)}). The two files are built apart, so a figure here can stand apart from the same figure there. Both stand; neither is corrected to the other.`;

/** The summary of one place, in the form of the as-metered view's first sentence. */
function Lead({ s, index }: { s: Slot; index: IndexFile | null }) {
  const k = (x: string) => `cd|${s.mark}|sum|${x}`;
  let body: ReactNode;
  if (s.state === "held") body = <p className="text-sm" data-cd-held={s.mark}><Held why={s.why} /> {LICENSE_NEEDED}</p>;
  else if (s.state !== "drawn") body = <p className="text-sm"><Hint words={s.state === "not-built" ? "not built yet" : "not held"} why={s.why} /></p>;
  else if (!s.area || !s.period || !hasGrowth(s)) body = <p className="text-sm"><NOT why={`The file of ${s.name} holds no whole year of demand.`} /></p>;
  else {
    const ys = wholeYears(s.area), first = ys[0], last = ys[ys.length - 1];
    const through = throughOf(s.period);
    const ytd = through ? yearToDate(s.period, s.area) : null;
    const g = last.row.avg_demand_growth_since_2019_pct, pg = last.row.peak_demand_growth_since_2019_pct, yg = ytd?.row.ytd_avg_demand_growth_since_2019_pct;
    body = (
      <p className="max-w-3xl font-serif text-lg leading-snug" data-cd-summary={s.mark}>
        From {first.year} to {last.year}, average demand went from <N k={k("avg0")}>{whole(first.row.avg_demand_mw)}</N> MW to <N k={k("avg1")}>{whole(last.row.avg_demand_mw)}</N> MW
        {g !== undefined && Number(first.year) === s.period.base ? <>, a change of <N k={k("avg_growth")}>{signed(g)}</N> percent</> : null}
        {first.row.peak_demand_mw !== undefined && last.row.peak_demand_mw !== undefined ? <>, and the highest hour from <N k={k("peak0")}>{whole(first.row.peak_demand_mw)}</N> MW to <N k={k("peak1")}>{whole(last.row.peak_demand_mw)}</N> MW{pg !== undefined && Number(first.year) === s.period.base ? <> (<N k={k("peak_growth")}>{signed(pg)}</N> percent)</> : null}</> : null}.
        {ytd && yg !== undefined ? <>{" "}January to {through} of {ytd.year} ran <N k={k("ytd_growth")}>{signed(yg)}</N> percent against the same months of {s.period.base}.</> : null} Weather is not removed.
        {/* session 8450 (the reader's read, row 4): a sentence with no percent says why it has none */}
        {Number(first.year) !== s.period.base ? <>{" "}<span className="font-sans text-xs" data-cd-no-base={s.mark}><Hint words={`no growth since ${s.period.base}`} why={`The file of ${s.name} holds no whole year ${s.period.base}: its first whole year is ${first.year}. A growth since ${s.period.base} needs the same measure in ${s.period.base}, so none is written here; the table of years gives each year's growth on the year before.`} /></span></> : null}
      </p>
    );
  }
  return (
    <div data-cd-place={s.mark} data-cd-code={s.key} data-cd-state={s.state} className="mb-6 min-w-0 border-t-2 border-accent pt-2">
      <div className="text-xs uppercase tracking-wide text-muted">Place {s.mark.toUpperCase()}</div>
      <h2 className="mb-1 font-serif text-xl text-accent">
        <span title={placeWords(s, index)} className="cursor-help" data-cd-name={s.mark}>{s.name}</span>
        {s.place.level === "region" && isNewRegion(s.place.code) ? <span className="ml-2 font-sans text-xs" data-cd-new={s.place.code}><Hint words="new to the site" why={`${s.name} is one of the six regions no page of the site drew before 19 November 2026 (${NEW_REGIONS.map((c) => REGION_NAME[c]).join(", ")}): none of the seven grids is in them.`} /></span> : null}
        {gridOf(s.place) ? <span className="ml-2 font-sans text-xs" data-cd-grid={s.place.code}><Link href={`/demand?area=${slugOf(s.place.code)}`}>{gridOf(s.place)} as metered</Link>{" "}<Hint words="another file" why={gridFileWhy(s.place, s.name)} /></span> : null}
      </h2>
      {body}
    </div>
  );
}

/** What stands where a place's chart would: license needed, not built yet, or not held, each with why on hover. */
function Blank({ s, what }: { s: Slot; what: string }) {
  if (s.state === "held") return <p className="text-sm"><Held why={s.why} /> {LICENSE_NEEDED}</p>;
  if (s.state === "not-built") return <p className="text-sm"><Hint words="not built yet" why={s.why} /></p>;
  return <p className="text-sm"><NOT why={s.state === "no-demand" ? s.why : `The file of ${s.name} holds no ${what}.`} /></p>;
}

/** The view as drawn from an index and the files of the places the address names (or from none). */
export function Country({ q, index, fileOf }: { q: Q; index: IndexFile | null; fileOf: (p: Place) => DemandPlaceFile | null }) {
  const a = placeOf(q.a, index) ?? FIRST_A;
  const bAsked = q.b === undefined ? FIRST_B : placeOf(q.b, index);
  const b = bAsked && !samePlace(bAsked, a) ? bAsked : null;
  const slots: Slot[] = [slotOf("a", a, index, fileOf), ...(b ? [slotOf("b", b, index, fileOf)] : [])];
  const drawn = slots.filter((s) => s.state === "drawn");
  const withFile = slots.filter((s) => s.file);
  const cols = slots.length > 1 ? two : "";

  // ---- what the address chooses besides the two places
  const yearsHeld = [...new Set(drawn.flatMap((s) => dailyYears(s.file!.daily)))].sort().reverse();
  const days = q.days && yearsHeld.includes(q.days) ? q.days : "all";
  const wSlots = drawn.filter((s) => s.file!.weather && trainOf(s.file!.weather).length);
  const grids: Record<string, Grid> = Object.fromEntries(drawn.map((s) => [s.key, wSlots.includes(s) ? s.file!.weather! : noWeather(s.name, s.file!.tz)]));
  const train = wSlots.length ? trainOf(wSlots[0].file!.weather) : [];
  const wf = { train, grids };
  const wOrder = wSlots.map((s) => s.key);
  // the weather view's own choice (lib/demandweather.ts, choices), over the places that hold a weather object
  const figure = FIGURES.find((f) => f.slug === q.figure) ?? FIGURES[0];
  const wAll = wSlots.length ? weatherYears(wf, wOrder) : [];
  const wc = wSlots.length ? { figure, year: q.year && wAll.includes(q.year) ? q.year : lastWholeYear(wf, wOrder) } : null;
  const carried = { days, figure: q.figure && FIGURES.some((f) => f.slug === q.figure) ? q.figure : undefined, year: q.year && /^\d{4}$/.test(q.year) ? q.year : undefined };
  const pick = (p: Place) => countryHref({ a: p, b: b && !samePlace(b, p) ? b : "none", ...carried });
  const cell = (s: Slot, v: ReactNode | null | undefined, missing: string): ReactNode => (s.state === "held" ? <Held why={s.why} /> : v ?? <NOT why={missing} />);
  const wide = (s: Slot) => (s.state === "not-built" ? <Hint words="not built yet" why={s.why} /> : <NOT why={s.why} />);

  // ---- the two lists of the form: the thirteen regions, then every balancing authority the index lists
  const options = [
    ...regionRows(index).map((r) => ({ value: r.code.toLowerCase(), label: `${r.name} (region)` })),
    ...(index?.bas ?? []).map((x) => ({ value: `ba-${x.code.toLowerCase()}`, label: `${x.code}: ${x.name}${x.generation_only ? ", generation only" : ""}` })),
  ];
  for (const s of slots) if (!options.some((o) => o.value === s.key)) options.push({ value: s.key, label: s.place.level === "ba" ? `${s.place.code}: ${s.name}` : s.name });
  const zones = withFile.map((s) => `${s.name}: ${s.file!.tz}`).join("; ");
  const HOUR = `Each place's own clock time, daylight saving included${zones ? ` (${zones})` : ""}. An hour is named by its start: 17:00 is the hour from 17:00 to 18:00.`;

  // ---- demand by day
  const dayRows = slots.map((s): Row => {
    const sum = s.file ? dailySummary(s.file.daily, days) : null;
    const k = (x: string) => `cd|${s.mark}|day|${x}`;
    const none = `The file of ${s.name} holds no day${days === "all" ? "" : ` of ${days}`}.`;
    if (!s.file) return { key: s.mark, cells: [s.name], wide: wide(s) };
    return {
      key: s.mark,
      cells: [
        s.name,
        cell(s, sum ? <span><N k={k("held")}>{whole(sum.held)}</N> of <N k={k("days")}>{whole(sum.days)}</N></span> : null, none),
        cell(s, sum ? dayWords(sum.first) : null, none),
        cell(s, sum ? dayWords(sum.last) : null, none),
        cell(s, sum?.topDay ? <span title={`${s.name}: the day of most demand among the days drawn, ${dayWords(sum.topDay.day)}, ${whole(sum.topDay.mwh)} MWh.`}><N k={k("top_gwh")}>{gwh(sum.topDay.mwh)}</N></span> : null, `No day drawn holds a whole day's demand for ${s.name}.`),
        cell(s, sum?.topDay ? dayWords(sum.topDay.day) : null, `No day drawn holds a whole day's demand for ${s.name}.`),
        cell(s, sum?.lowDay ? <span title={`${s.name}: the day of least demand among the days drawn, ${dayWords(sum.lowDay.day)}, ${whole(sum.lowDay.mwh)} MWh.`}><N k={k("low_gwh")}>{gwh(sum.lowDay.mwh)}</N></span> : null, `No day drawn holds a whole day's demand for ${s.name}.`),
        cell(s, sum?.lowDay ? dayWords(sum.lowDay.day) : null, `No day drawn holds a whole day's demand for ${s.name}.`),
        cell(s, sum?.topHour ? <N k={k("top_mw")}>{whole(sum.topHour.mw)}</N> : null, `No day drawn holds a highest hour for ${s.name}.`),
        cell(s, sum?.topHour ? (sum.topHour.at ? localHour(sum.topHour.at, s.file.tz) : dayWords(sum.topHour.day)) : null, `No day drawn holds a highest hour for ${s.name}.`),
      ],
    };
  });
  const newest = [...new Set(drawn.flatMap((s) => newestDays(s.file!.daily, NEWEST_DAYS).map((r) => r.day)))].sort().reverse().slice(0, NEWEST_DAYS);
  const newestRows = newest.map((day): Row => ({
    key: day,
    cells: [
      day,
      ...slots.flatMap((s): ReactNode[] => {
        const r = s.file ? newestDays(s.file.daily, NEWEST_DAYS * 2).find((x) => x.day === day) : undefined;
        const k = (x: string) => `cd|${s.mark}|new|${day}|${x}`;
        const part = r && r.hours !== null ? `${s.name}, ${day}: ${whole(r.hours)} of the day's hours are used, so no demand of the whole day is given.` : `The file of ${s.name} does not hold ${day}.`;
        if (!s.file) return [wide(s), ""];
        return [
          cell(s, r && r.mwh !== null ? <N k={k("gwh")}>{gwh(r.mwh)}</N> : null, part),
          cell(s, r && r.peak_mw !== null ? <span title={r.peak_at ? `${s.name}: the highest hour of ${day} began at ${localHour(r.peak_at, s.file.tz)}, local time.` : undefined}><N k={k("mw")}>{whole(r.peak_mw)}</N></span> : null, part),
        ];
      }),
    ],
  }));

  // ---- year by year: one row a place and year, in the form of the as-metered view's table
  const yearRows = slots.flatMap((s): Row[] => {
    if (!s.file) return [{ key: s.mark, cells: [s.name], wide: wide(s) }];
    const ar = s.area, p = s.period;
    if (!ar || !p || !hasGrowth(s)) return [{ key: s.mark, cells: [s.name], wide: s.state === "held" ? <><Held why={s.why} /> {LICENSE_NEEDED}</> : <NOT why={`The file of ${s.name} holds no whole year of demand.`} /> }];
    const through = throughOf(p);
    const ys = wholeYears(ar), ytd = through ? yearToDate(p, ar) : null;
    const k = (y: string, x: string) => `cd|${s.mark}|y|${y}|${x}`;
    const peakAt = (y: string, key = "peak_demand_mw") => (ar.at[y]?.[key] ? localHour(ar.at[y][key], ar.tz) : null);
    const g = (y: string, v: number | undefined, x: string) => (v === undefined && Number(y) === p.base && s.state !== "held"
      ? <span className="text-muted">the base year</span>
      : cell(s, v !== undefined ? <N k={k(y, x)}>{signed(v)}</N> : null, `The file of ${s.name} holds no such figure for ${y}: a growth needs the same measure in ${p.base}${x === "yoy" ? " or in the year before" : ""}.`));
    const rows: Row[] = ys.map(({ year, row }) => ({
      key: `${s.mark}|${year}`, highlight: false,
      cells: [s.name, year, cell(s, <N k={k(year, "avg")}>{whole(row.avg_demand_mw)}</N>, ""), g(year, row.avg_demand_growth_since_2019_pct, "avg_growth"), g(year, row.avg_demand_growth_yoy_pct, "yoy"),
        cell(s, row.peak_demand_mw !== undefined ? <N k={k(year, "peak")}>{whole(row.peak_demand_mw)}</N> : null, `The file of ${s.name} holds no highest hour for ${year}.`),
        cell(s, peakAt(year), `The file of ${s.name} does not say when the highest hour of ${year} was.`), g(year, row.peak_demand_growth_since_2019_pct, "peak_growth"),
        cell(s, row.hours_used !== undefined ? <span><N k={k(year, "hours")}>{whole(row.hours_used)}</N>{row.hours_in_year !== undefined ? <> of {whole(row.hours_in_year)}</> : null}</span> : null, `The file of ${s.name} does not count the hours used in ${year}.`)],
    }));
    if (ytd) rows.push({
      key: `${s.mark}|ytd`, highlight: true,
      cells: [s.name, `${ytd.year}, to ${through}`, cell(s, <N k={k("ytd", "avg")}>{whole(ytd.row.ytd_avg_demand_mw)}</N>, ""), g("ytd", ytd.row.ytd_avg_demand_growth_since_2019_pct, "avg_growth"), <span key="n" className="text-muted">same months</span>,
        cell(s, ytd.row.ytd_peak_demand_mw !== undefined ? <N k={k("ytd", "peak")}>{whole(ytd.row.ytd_peak_demand_mw)}</N> : null, `The file of ${s.name} holds no highest hour for ${ytd.year} so far.`),
        cell(s, peakAt(ytd.year, "ytd_peak_demand_mw"), `The file of ${s.name} does not say when the highest hour of ${ytd.year} so far was.`), g("ytd", ytd.row.ytd_peak_demand_growth_since_2019_pct, "peak_growth"),
        cell(s, ytd.row.ytd_hours_used !== undefined ? <span><N k={k("ytd", "hours")}>{whole(ytd.row.ytd_hours_used)}</N>{ytd.row.ytd_hours_in_window !== undefined ? <> of {whole(ytd.row.ytd_hours_in_window)}</> : null}</span> : null, `The file of ${s.name} does not count the hours used in ${ytd.year} so far.`)],
    });
    return rows;
  });
  const bases = [...new Set(slots.filter((s) => s.period && Number.isFinite(s.period.base)).map((s) => s.period!.base))];
  const base = bases.length === 1 ? String(bases[0]) : "the base year";
  const grown = drawn.filter(hasGrowth);
  const counted = (s: Slot) => { const x = s.file?.screened; return !!x && [x.jumps, x.not_positive, x.blank].every((v) => typeof v === "number"); };

  // ---- with the weather taken out: the weather view's own chart and table, for the regions that hold it
  const t0 = train[0], t1 = train[train.length - 1];
  const wYears = wAll;
  const degrees = wSlots[0]?.file?.weather?.degrees_from ?? "";
  const wHref = (f: string, y: string) => countryHref({ a, b: b ?? "none", days, figure: f, year: y }, "weather");
  const noWeatherWhy = (s: Slot) => (s.state !== "drawn" ? s.why
    : s.place.level === "ba" ? `The weather view is built for EIA's regions, not for a single balancing authority: the file of ${s.name} holds none.`
    : `The file of ${s.name} holds no weather view${s.file?.weather ? " whose fit names its years" : ""}.`);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const weatherRows = slots.flatMap((s): Row[] => {
    if (!wc || !wSlots.includes(s)) return [{ key: s.mark, cells: [s.name], wide: s.state === "held" ? <><Held why={s.why} /> {LICENSE_NEEDED}</> : s.state === "not-built" ? <Hint words="not built yet" why={s.why} /> : <NOT why={noWeatherWhy(s)} /> }];
    const w = s.file!.weather!;
    return wYears.map((y): Row => {
      const g: Figure | null = figureOf(wf, s.key, y, figure.key), k = `cd|${s.mark}|w|${y}`;
      const part = Number(y) === w.newest && w.through < "12-31";
      const none = `The file of ${s.name} holds no figure of ${figure.name.toLowerCase()} for ${y}. A figure is written only when nearly all its hours hold both demand and weather (the file's method note gives the share).`;
      if (!g) return { key: `${s.mark}|${y}`, highlight: y === wc.year, muted: true, cells: [s.name, y, <NOT key="a" why={none} />, <NOT key="g" why={none} />, <NOT key="w" why={none} />, <NOT key="u" why={none} />, <NOT key="p" why={none} />, ""] };
      const m = s.area?.years[y];
      const on = `${whole(g.used)} of ${whole(g.wanted)} ${figure.key === "overnight_min" ? "days" : "hours"}`;
      const why = `${s.name}, ${y}: ${whole(g.actual)} MW, read on the ${on} the fit holds (the hours whose weather is held${w.weather_table ? `, table ${w.weather_table}` : ""}).${figure.key === "energy" && m?.avg_demand_mw !== undefined ? ` The table above gives ${whole(m.avg_demand_mw)} MW for ${y}, over the ${whole(m.hours_used)} hours it uses (every hour that passes the screen, weather or not).` : ""}`;
      return {
        key: `${s.mark}|${y}`, highlight: y === wc.year, muted: false,
        cells: [s.name, part && g.window !== "the season" ? `${y}, part` : y, <span key="a" title={why} data-cd-metered-why={`${s.mark}|${y}`}><N k={`${k}|mw`}>{whole(g.actual)}</N></span>, <N key="g" k={`${k}|g`}>{signed1(g.growth_pct)}</N>, <N key="w" k={`${k}|w`}>{signed1(g.weather_pct)}</N>,
          <N key="u" k={`${k}|u`}>{signed1(g.unexplained_pct)}</N>, typeof g.uncertainty_pct !== "number" ? <NOT key="p" why={`No year left out of the fit gives ${s.name} an uncertainty for this figure.`} /> : <N key="p" k={`${k}|pm`}>{one(g.uncertainty_pct)}</N>,
          <span key="r" data-reading={g.finding ? "finding" : "no"} title={reading(g)}>{g.finding ? "yes" : g.outside ? "beyond" : "no"}</span>],
      };
    });
  });

  // ---- a region beside the grid that covers nearly its ground
  const alike = drawn.filter((s) => s.file!.alike && alikeRows(s.file!.alike).length);

  // ---- the files' own lines, for the source
  const tables = [...new Set(withFile.flatMap((s) => s.file!.tables ?? []))];
  const notes = [...new Set([...withFile.map((s) => s.file!.method), index?.method].filter((m): m is string => !!m))];
  const regions = regionRows(index);

  return (
    <div data-view-body="country" data-cd-a={slots[0].key} data-cd-b={slots[1]?.key ?? ""} data-cd-days={days}>
      <ToolHeader title="Demand growth"
        lead={<>Demand in each of EIA&apos;s thirteen regions of the lower 48 and in every balancing authority that files with EIA: day by day, year by year since {bases.length === 1 ? bases[0] : "the base year"}, by month and hour of the day, and for a region with the weather taken out. Any two places side by side, from EIA&apos;s hourly record.</>} />
      <p className="mb-6 text-xs text-muted" data-method="1"><SiteLink href={METHODS.country.href}>Method, sources and gaps</SiteLink></p>

      {/* session 8450 (the reader's read, row 1): a list is as wide as its longest name, and EIA's names of the balancing
          authorities are longer than a phone's window; each list is held to the form's width */}
      <form method="get" action="/demand" className="mb-3 flex flex-wrap items-end gap-3 bg-paper px-4 py-3 text-sm [&_label]:min-w-0 [&_label]:max-w-full [&_select]:max-w-full" data-cd-form="1">
        <input type="hidden" name="view" value="country" />
        <AutoSubmitSelect name="a" value={slots[0].key} options={options} label="Place A" />
        <AutoSubmitSelect name="b" value={slots[1]?.key ?? "none"} options={[{ value: "none", label: "None" }, ...options]} label="Place B" />
        <AutoSubmitSelect name="days" value={days} options={[{ value: "all", label: "Every day held" }, ...yearsHeld.map((y) => ({ value: y, label: y }))]} label="Days drawn" />
        {carried.figure ? <input type="hidden" name="figure" value={carried.figure} /> : null}
        {carried.year ? <input type="hidden" name="year" value={carried.year} /> : null}
        <button type="submit" className="border border-rule bg-panel px-3 py-1 text-sm">Show</button>
        <a href="/demand?view=country" className="text-xs" data-cd-reset="1">Reset to the defaults</a>
      </form>
      <p className="mb-8 text-sm" data-cd-lead="1">
        <Hint words="The places drawn first" why={FIRST_WHY} />.{" "}
        <Hint words="What a region is" why="EIA places each balancing authority of the lower 48 in one of thirteen regions (Form EIA-930). A region's demand here is the sum of its balancing authorities that file demand, written for an hour only when every one of them holds it; generation-only authorities file none. A region is not one of the seven grids of the other views, even where the two cover nearly the same ground: where they do, the section 'A region beside its grid' sets both figures side by side." />.{" "}
        <Hint words="Six regions are new to the site" why={`${NEW_REGIONS.map((c) => REGION_NAME[c]).join(", ")}: none of the seven grids of the other views is in them, so no page drew them before 19 November 2026.`} />.{" "}
        <Hint words="How a figure here is formed" why="Every figure is read from the place's file, which the data machine writes with the measures and the screen of hours of the as-metered view (docs/methods/demand_growth.md). This view computes three things only: a day's average (its MWh over the hours used), the days of most and least demand among the days drawn, and the highest hour among them. Nothing is filled, interpolated or scaled; what a file does not hold reads not held. Weather is not removed, except in the section that says so." />
        {index ? null : <>.{" "}<span data-cd-index="not-built">The list of balancing authorities: <Hint words="not built yet" why="The index of regions and balancing authorities (site/data/regions/index.json) is written by the data machine from EIA's reference tables and is not on the site yet. Until it is, the two lists offer the thirteen regions, and a balancing authority can be named in the address (for the Tennessee Valley Authority: a=ba-tva)." /></span></>}
      </p>

      <div className={cols} data-cd-places="1">
        {slots.map((s) => <Lead key={s.mark} s={s} index={index} />)}
      </div>

      {withFile.length ? (
        <>
          <ToolSection title="Demand by day" id="by-day"
            note={<><Hint words="What is drawn" why="For each local day of the place: the highest hour of the day's used hours, and the day's average, which is the day's demand in MWh over the hours used (a day of 23 or 25 hours when the clocks change). A day's demand is held only when all its hours are used; a day that is not held is a break in the line, never a filled point. Point at a chart for a day's figures, or switch it to a table." />{" "}
              <Hint words="Days drawn" why={`Every day the files hold, or the days of one year: the list "Days drawn" above. Default: every day held, this page's own choice (session 8420). The table under the charts counts the days drawn. Shown now: ${days === "all" ? "every day held" : days}.`} /></>}>
            <div className={cols}>
              {slots.map((s) => {
                const peak = s.state === "drawn" ? dailyPoints(s.file!.daily, "peak", days) : [], avg = s.state === "drawn" ? dailyPoints(s.file!.daily, "average", days) : [];
                return (
                  <div key={s.mark} className="min-w-0" data-cd-daily={s.mark} data-cd-points={peak.length}>
                    <ChartFrame title={`${s.name}: demand by day, MW`}>
                      {peak.some((p) => p[1] !== null) || avg.some((p) => p[1] !== null)
                        ? <TimeChart x="day" unit="MW" height={260} ariaLabel={`${s.name}: the highest hour and the average of each day, MW, ${days === "all" ? "every day held" : days}`}
                            series={[{ name: "Highest hour", color: "accent", points: peak }, { name: "Average over the day", color: "ink", points: avg }]} />
                        : <Blank s={s} what={`day${days === "all" ? "" : ` of ${days}`}`} />}
                    </ChartFrame>
                  </div>
                );
              })}
            </div>
            <ToolTable minWidth={980} caption="The days drawn, for each place: how many, the days of most and least demand, and the highest hour"
              head={["Place",
                <Head key="d" mark="days" words="Days with a whole day's demand" why="How many of the days drawn hold a whole day's demand (every hour of the day used), of the days drawn." />,
                <Head key="f" mark="from" words="From" why="The first day drawn: the first local day the file holds, or the first of the year chosen." />,
                <Head key="t" mark="to" words="To" why="The last day drawn: the last local day the file holds, or the last of the year chosen." />,
                <Head key="m" mark="top" words="Most in a day, GWh" why="The day of most demand among the days drawn that hold a whole day's demand, in GWh (1,000 MWh). Computed here from the file's days." />,
                <Head key="mo" mark="topon" words="On" why="That day, a local day of the place." />,
                <Head key="l" mark="low" words="Least in a day, GWh" why="The day of least demand among the days drawn that hold a whole day's demand. Computed here from the file's days." />,
                <Head key="lo" mark="lowon" words="On" why="That day, a local day of the place." />,
                <Head key="h" mark="hour" words="Highest hour, MW" why="The highest of the days' highest hours among the days drawn. Source: EIA Form EIA-930, hourly demand, through the place's file." />,
                <Head key="w" mark="when" words="When, local time" why={HOUR} />]}
              rows={dayRows} />
            {newestRows.length ? (
              <div className="mt-6" data-cd-newest="1">
                <h3 className="mb-1 text-base">The newest days</h3>
                <ToolTable minWidth={slots.length > 1 ? 620 : 420} caption={`The newest ${NEWEST_DAYS} days the files hold, for each place`}
                  head={[<Head key="d" mark="newday" words="Day" why={`The newest ${NEWEST_DAYS} local days the files hold, newest first. Default: ${NEWEST_DAYS} days, this page's own choice (session 8420); every day is in the chart above and in the file.`} />,
                    ...slots.flatMap((s) => [
                      <Head key={`${s.mark}g`} mark={`new-${s.mark}-gwh`} words={`${s.name}: demand, GWh`} why={`${s.name}: the day's demand, held only when every hour of the day is used.`} />,
                      <Head key={`${s.mark}m`} mark={`new-${s.mark}-mw`} words={`${s.name}: highest hour, MW`} why={`${s.name}: the highest of the day's used hours. Hover a figure for when it was.`} />])]}
                  rows={newestRows} />
              </div>
            ) : null}
          </ToolSection>

          <ToolSection title="Year by year" id="years"
            note={<>{grown.filter(counted).map((s) =><span key={s.mark} data-cd-screened={s.mark}>Hours left out for {s.name}: <N k={`cd|${s.mark}|screen|jumps`}>{whole(s.file!.screened!.jumps)}</N> that stand apart from their neighbours, <N k={`cd|${s.mark}|screen|zero`}>{whole(s.file!.screened!.not_positive)}</N> at or below zero, <N k={`cd|${s.mark}|screen|blank`}>{whole(s.file!.screened!.blank)}</N> blank.{" "}</span>)}
              <Hint words="Which hours are used" why="From EIA-930's hourly demand, by the screen of the as-metered view (docs/methods/demand_growth.md): an hour is used when its demand is above zero and does not stand apart from the hours around it, because EIA's file holds faulty hours and a faulty high hour would otherwise be a year's peak. A region's hour needs every one of its balancing authorities that file demand. A year is written when nearly all its hours are used; its average is the mean of those hours. Nothing is filled. The hours left out are counted from 1 January of the base year to the file's last hour." />{" "}
              <Hint words="The last row of a place" why="The last row of each place compares January to the last whole month of the newest year with the same months of the base year: its growth is against those months, not against the whole base year." /></>}>
            <div className={cols}>
              {slots.map((s) => (
                <div key={s.mark} className="min-w-0" data-cd-years={s.mark}>
                  <ChartFrame title={`${s.name}: demand, MW`} legend={[{ label: "Average over the year", color: "var(--color-accent)" }, { label: "The year's highest hour", color: "var(--color-ink)" }]}>
                    {grown.includes(s) ? <Hover><YearsChart area={s.area!} /></Hover> : <Blank s={s} what="whole year of demand" />}
                  </ChartFrame>
                </div>
              ))}
            </div>
            <ToolTable minWidth={900} caption="Average and peak demand by year, for each place"
              head={["Place", "Year", "Average, MW",
                <Head key="s" mark="since" words={`Since ${base}, percent`} why={`The year's average demand against the average of ${base}, the base year of the file${bases.length > 1 ? " (each place's own)" : ""}, percent.`} />,
                <Head key="y" mark="yoy" words="On the year before, percent" why="A calendar year's average over the year before's, percent." />,
                "Peak, MW",
                <Head key="w" mark="yearwhen" words="When, local time" why={HOUR} />,
                <Head key="p" mark="peaksince" words={`Peak since ${base}, percent`} why={`The year's highest hour against the highest hour of ${base}, percent.`} />,
                <Head key="h" mark="hours" words="Hours used" why="The hours of the year that pass the screen, of the hours in the year." />]}
              rows={yearRows} />
          </ToolSection>

          <ToolSection title="Where the growth is" id="where"
            note={<Hint words="How to read the cells" why={`Each cell is one hour of the day in one month: the average demand of that hour over the month in the last whole year, against the same in the base year. Red is growth, dark grey a fall; the deeper, the larger. One hot or mild month colors a whole row, which is the weather and not a trend. ${HOUR}`} />}>
            <div className={cols}>
              {slots.map((s) => {
                const ok = grown.includes(s);
                const ex = ok ? extremes(cells(s.period!, s.area!)) : null;
                return (
                  <div key={s.mark} className="min-w-0" data-cd-where={s.mark}>
                    <ChartFrame title={ok ? `${s.name}: change from ${s.period!.base} to ${s.period!.last_year}, percent, by month and hour of the day` : `${s.name}: change by month and hour of the day`} legend={[{ label: "Growth", color: UP }, { label: "Fall", color: DOWN }]}>
                      {ok ? <Hover><Heat area={s.area!} file={s.period!} /></Hover> : <Blank s={s} what="whole year of demand" />}
                    </ChartFrame>
                    {ex ? <p className="mb-6 max-w-3xl text-sm" data-cd-extremes={s.mark}>Largest: {monthName(ex.most.month)} at {hourName(ex.most.hour)}, <N k={`cd|${s.mark}|cell|most|pct`}>{signed(ex.most.pct)}</N> percent (<N k={`cd|${s.mark}|cell|most|mw`}>{whole(ex.most.mw)}</N> MW). Smallest: {monthName(ex.least.month)} at {hourName(ex.least.hour)}, <N k={`cd|${s.mark}|cell|least|pct`}>{signed(ex.least.pct)}</N> percent (<N k={`cd|${s.mark}|cell|least|mw`}>{whole(ex.least.mw)}</N> MW).</p> : null}
                    {ok ? (
                      <>
                        <ChartFrame title={`${s.name}: by month`}><Hover><ChangeBars file={s.period!} items={byMonth(s.period!, s.area!).map((m) => ({ label: monthName(m.month), pct: m.pct }))} what="by month" /></Hover></ChartFrame>
                        <ChartFrame title={`${s.name}: by hour of the day`}><Hover><ChangeBars file={s.period!} items={byHour(s.period!, s.area!).map((h) => ({ label: hourName(h.hour), pct: h.pct }))} what="by hour" /></Hover></ChartFrame>
                      </>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </ToolSection>

          <ToolSection title="With the weather taken out" id="weather"
            note={wc ? <><Hint words="How to read the bars" why={`${figure.name}: ${figure.what}. Growth is against the mean of ${t0} to ${t1}, the years the fit was made on. The grey bar is what the year's weather explains; the red bar is the rest, and the black line across it is its uncertainty: the largest miss the method made on a year it had not seen. A red bar shorter than half its black line is not a finding. The remainder is growth the weather does not explain: more people, electric heating and vehicles, new industry and datacenters are all in it together, and so are rooftop solar, efficiency and a recession. The page does not say which it is.`} />{" "}
              <Hint words="Which places hold it" why={`The data machine builds the weather view for EIA's regions, from each region's own weather table; a single balancing authority holds none.${degrees ? ` The file's own words on its heating and cooling degrees: ${degrees}.` : ""} Defaults: the year's energy, in the last whole year held, as the weather view of the seven grids opens.`} /></> : undefined}>
            {wc ? (
              <>
                <div className="mb-4 flex flex-wrap gap-x-8 gap-y-2 text-sm" data-cd-weather-choice="1">
                  <nav aria-label="Figure" className="flex flex-wrap gap-x-3"><span className="text-xs uppercase tracking-wide text-muted">Figure</span>{FIGURES.map((f) => <Link key={f.slug} href={wHref(f.slug, wc.year)} aria-current={f.slug === figure.slug ? "true" : undefined} className={item(f.slug === figure.slug)} title={f.what}>{f.name}</Link>)}</nav>
                  <nav aria-label="Year" className="flex flex-wrap gap-x-3"><span className="text-xs uppercase tracking-wide text-muted">Year in the chart</span>{wYears.map((y) => <Link key={y} href={wHref(figure.slug, y)} aria-current={y === wc.year ? "true" : undefined} className={item(y === wc.year)}>{y}</Link>)}</nav>
                </div>
                <ChartFrame title={`${figure.name}, ${wc.year}: growth against the average of ${t0} to ${t1}, percent`} legend={[{ label: "Explained by the weather", color: "var(--color-muted)" }, { label: "Not explained, with its uncertainty", color: "var(--color-accent)" }]}>
                  <Hover><Explained year={wc.year} fig={figure} of={wf} order={drawn.map((s) => s.key)} by="place" /></Hover>
                </ChartFrame>
              </>
            ) : null}
            <ToolTable minWidth={640} caption={`${figure.name}: growth, the part the weather explains and the part it does not, by place and year`}
              head={["Place", "Year",
                <Head key="m" mark="metered" words="Metered, MW" why="The figure from metered demand, read on the hours whose weather the place's weather table holds: the hours the fit is read on. Each cell's hover sets it beside the table of years above." />,
                <Head key="g" mark="growth" words="Growth" why={wc ? `Percent of the mean of ${t0} to ${t1}. Growth is the sum of the two columns after it.` : "Percent of the mean of the years the fit was made on. Growth is the sum of the two columns after it."} />,
                <Head key="t" mark="temperature" words="Weather" why="The growth the year's weather explains, percent." />,
                <Head key="u" mark="unexplained" words="Not explained" why="The growth the weather does not explain, percent." />,
                <Head key="p" mark="pm" words="Give or take" why="The largest miss, in absolute value, the method made on a year left out of the fit. In percent, as the column before it." />,
                <Head key="f" mark="finding" words="Finding" why="Yes only when the part not explained is larger than its give or take. Beyond: the peak hour was hotter (summer) or colder (winter) than any hour of the fit's years, so the fit is reaching past what it was made on and the figure is not called a finding." />]}
              rows={weatherRows} />
            {wc ? (
              <Fold title="The check: years the fit had not seen">
                <p className="mb-3"><Hint words="What this check is" why={`Each of ${train.join(", ")} is left out in turn; the fit is made on the others and the left-out year is read against them. A place whose customers did not change comes back near zero. What comes back is the method's miss plus whatever really changed that year. The largest of them, in absolute value, is the uncertainty in the table above.`} /></p>
                <ToolTable minWidth={640} caption={`${figure.name}: growth the weather does not explain in a year left out of the fit, percent`}
                  head={["Place",
                    ...train.map((y) => <Head key={y} mark={`out-${y}`} words={`${y} left out`} why={`The growth of ${figure.name.toLowerCase()} in ${y} that the weather does not explain when the fit is made on the other years and ${y} is read against them, percent.`} />),
                    <Head key="e" mark="out-hour" words="Error on an hour left out, percent" why="The fit's mean absolute error on an hour of a year it was not made on, as a percent of the hour's demand: each of the fit's years is predicted by a fit made on the others. Source: the fit of the place's file." />,
                    <Head key="d" mark="out-day" words="On a day left out" why="The same error on a day in place of an hour: mean absolute error, as a percent of the day's demand. Source: the fit of the place's file." />]}
                  rows={wSlots.map((s) => { const w = s.file!.weather!; const none = `The file of ${s.name} does not hold it.`; return { key: s.mark, cells: [s.name,
                    ...train.map((y) => { const h = w.holdout[String(y)]?.[figure.key]; return h ? <N key={y} k={`cd|${s.mark}|h|${y}`}>{signed1(h.unexplained_pct)}</N> : <NOT key={y} why={none} />; }),
                    typeof w.fit?.oos_mape_pct === "number" ? <N key="e" k={`cd|${s.mark}|h|hour`}>{one(w.fit.oos_mape_pct)}</N> : <NOT key="e" why={none} />,
                    typeof w.fit?.oos_daily_mape_pct === "number" ? <N key="d" k={`cd|${s.mark}|h|day`}>{one(w.fit.oos_daily_mape_pct)}</N> : <NOT key="d" why={none} />] }; })} />
              </Fold>
            ) : null}
          </ToolSection>

          {alike.length ? (
            <ToolSection title="A region beside its grid" id="alike"
              note={<Hint words="What is set side by side" why="Where one of EIA's regions covers nearly the ground of one of the seven grids of the other views (Texas and ERCOT, New York and NYISO, New England and ISO-NE, the Mid-Atlantic and PJM), the region's file gives both averages for each year and the data machine's own sentence on why the two can differ. Both figures stand: neither is corrected to the other." />}>
              <div className={alike.length > 1 ? two : ""}>
                {alike.map((s) => {
                  const al = s.file!.alike!, grid = GRID_NAME[al.grid] ?? al.grid, why = sentence(al.why);
                  const slug = slugOf(al.grid);
                  const rows = alikeRows(al), both = rows.filter((r) => r.region !== null && r.grid !== null);
                  const apart = both.filter((r) => whole(r.region!) !== whole(r.grid!) || (r.pct !== null && r.pct !== 0));
                  return (
                    <div key={s.mark} className="mb-6 min-w-0" data-cd-alike={s.mark} data-cd-alike-grid={al.grid}>
                      <h3 className="mb-1 text-base">{s.name} and {grid}</h3>
                      <ToolTable minWidth={460} caption={`${s.name}, EIA's region, beside ${grid}, the grid: average demand by year`}
                        head={["Year",
                          <Head key="r" mark="alike-region" words={`${s.name}, the region, MW`} why={`The average demand of the year for EIA's region ${s.place.code}, as the region's file gives it.`} />,
                          <Head key="g" mark="alike-grid" words={`${grid}, the grid, MW`} why={`The average demand of the same year for ${grid}, the balancing authority ${al.grid} of the other views, as the region's file gives it.`} />,
                          <Head key="d" mark="alike-diff" words="Difference, percent" why={`The region's average less the grid's, as a percent of the grid's, as the file gives it. ${why}`} />]}
                        rows={rows.map((r) => ({ key: r.year, cells: [r.year,
                          r.region !== null ? <N key="r" k={`cd|${s.mark}|alike|${r.year}|region`}>{whole(r.region)}</N> : <NOT key="r" why={`The file gives no average of ${s.name} for ${r.year}.`} />,
                          r.grid !== null ? <N key="g" k={`cd|${s.mark}|alike|${r.year}|grid`}>{whole(r.grid)}</N> : <NOT key="g" why={`The file gives no average of ${grid} for ${r.year}.`} />,
                          r.pct !== null ? <span key="d" title={why || undefined} className={why ? "cursor-help" : undefined} data-cd-alike-why={`${s.mark}|${r.year}`}><N k={`cd|${s.mark}|alike|${r.year}|pct`}>{signed(r.pct)}</N></span> : <NOT key="d" why={`The file gives no difference for ${r.year}.`} />] }))} />
                      <p className="mt-2 text-sm">
                        <span data-cd-alike-apart={s.mark}>{both.length ? (apart.length
                          ? <>The two differ in <N k={`cd|${s.mark}|alike|apart`}>{String(apart.length)}</N> of the {both.length} years held.</>
                          : <>The two are equal in each of the <N k={`cd|${s.mark}|alike|years`}>{String(both.length)}</N> years held.</>) : null}</span>{" "}
                        {why ? <Hint words={apart.length ? "Why they differ" : "Why they can differ"} why={why} /> : <NOT why="The file gives no sentence on why the two differ." />}.{" "}
                        {slug ? <><Link href={`/demand?area=${slug}`}>{grid} as metered</Link>.{" "}</> : null}
                        <Link href={countryHref({ a: s.place, b: { level: "ba", code: al.grid }, ...carried })} data-cd-alike-pair={s.mark}>{s.name} beside {grid}, as two places</Link>.
                      </p>
                    </div>
                  );
                })}
              </div>
            </ToolSection>
          ) : null}
        </>
      ) : null}

      <ToolSection title="Every region and balancing authority" id="places"
        note={<Hint words="How to choose" why="A name in either table puts that place in place A and keeps place B. The two lists at the top of the view hold the same places." />}>
        <ToolTable minWidth={index ? 860 : 420} words caption="EIA's thirteen regions of the lower 48"
          head={index
            ? ["Region", "Code", <Head key="z" mark="tz" words="Time zone" why="The zone a region's days, months and years are counted in: the zone of most of its demand." />,
              <Head key="b" mark="bas" words="Balancing authorities" why="The balancing authorities EIA places in the region, active or retired since July 2018. Hover a count for their codes." />,
              <Head key="g" mark="grids" words="Grids among them" why="Which of the seven grids of the other views are among the region's balancing authorities." />,
              <Head key="f" mark="first" words="Demand held from" why="The first hour of demand held for the region, UTC." />,
              <Head key="l" mark="last" words="To" why="The last hour of demand held for the region, UTC." />]
            : ["Region", "Code", <Head key="g" mark="grids" words="Grids among them" why="Which of the seven grids of the other views are among the region's balancing authorities, by EIA's placing of each authority in one region." />]}
          rows={regions.map((r) => {
            const p: Place = { level: "region", code: r.code };
            const name = <span key="n" data-cd-region={r.code} {...(isNewRegion(r.code) ? { "data-cd-region-new": "1" } : {})}><Link href={pick(p)} title={`${r.name}, EIA's region ${r.code}.${isNewRegion(r.code) ? " No page of the site drew this region before 19 November 2026: none of the seven grids is in it." : ""}`}>{r.name}</Link>{isNewRegion(r.code) ? <span className="ml-2 text-xs text-muted">new to the site</span> : null}</span>;
            const grids = gridWords(r.grids).join(", ") || "none";
            if (!index) return { key: r.code, highlight: slots.some((s) => samePlace(s.place, p)), cells: [name, r.code, grids] };
            const none = `The index does not hold it for ${r.name}.`;
            return { key: r.code, highlight: slots.some((s) => samePlace(s.place, p)), cells: [name, r.code, r.tz ?? <NOT key="z" why={none} />,
              r.bas ? <span key="b" title={r.bas.join(", ")} className="cursor-help">{r.bas.length}</span> : <NOT key="b" why={none} />, grids,
              r.first_hour ? utcHourWords(r.first_hour) : <NOT key="f" why={none} />, r.last_hour ? utcHourWords(r.last_hour) : <NOT key="l" why={none} />] };
          })} />
        {index?.bas?.length ? (
          <Fold title={`The balancing authorities (${index.bas.length})`}>
            <ToolTable minWidth={900} words caption="Every balancing authority of the lower 48 that EIA's Form EIA-930 lists"
              head={["Code", "Name", "Region",
                <Head key="z" mark="batz" words="Time zone" why="From EIA's time zone of the authority (Eastern, Central, Mountain, Arizona, Pacific)." />,
                <Head key="g" mark="bagrid" words="One of the seven grids" why="The grid of the other views the authority is, when it is one." />,
                <Head key="d" mark="bademand" words="Files demand" why="EIA's 'Generation Only BA' files no demand: no demand file is written for it." />,
                <Head key="a" mark="baactive" words="Active" why="EIA's 'Active BA', and its retirement date when it has one." />,
                <Head key="f" mark="bafirst" words="Held from" why="The first hour held, UTC (demand, or net generation for a generation-only authority)." />,
                <Head key="l" mark="balast" words="To" why="The last hour held, UTC (demand, or net generation for a generation-only authority)." />]}
              rows={index.bas.map((x) => {
                const p: Place = { level: "ba", code: x.code };
                const has = !x.generation_only && (!x.files || x.files.includes("demand"));
                const none = `The index does not hold it for ${x.code}.`;
                return { key: x.code, highlight: slots.some((s) => samePlace(s.place, p)), cells: [
                  <span key="c" data-cd-ba={x.code} className="font-mono">{x.code}</span>,
                  has ? <Link key="n" href={pick(p)}>{x.name}</Link> : <span key="n" title={`${x.name} files no demand with EIA (a generation-only balancing authority), so there is no demand to draw for it.`} className="cursor-help">{x.name}</span>,
                  x.region ? REGION_NAME[x.region] ?? x.region : <NOT key="r" why={none} />, x.tz ?? <NOT key="z" why={none} />, x.grid ? GRID_NAME[x.grid] ?? x.grid : "",
                  x.generation_only ? "no, generation only" : "yes", x.retired ? `retired ${x.retired}` : x.active === false ? "no" : "yes",
                  x.first_hour ? utcHourWords(x.first_hour) : <NOT key="f" why={none} />, x.last_hour ? utcHourWords(x.last_hour) : <NOT key="l" why={none} />] };
              })} />
          </Fold>
        ) : null}
      </ToolSection>

      <p className="mt-8 border-t border-rule pt-3 text-xs leading-relaxed text-muted" data-cd-source="1">
        Source: EIA Form EIA-930, hourly demand by balancing authority and region (public domain){wSlots.length ? `; the weather view also from the weather record the files name${wSlots[0].file!.weather!.weather_table ? ` (table ${wSlots[0].file!.weather!.weather_table})` : ""}` : ""}
        {tables.length ? <>; ERW table{tables.length > 1 ? "s" : ""} {tables.map((t, i) => <span key={t}>{i ? ", " : ""}<SiteLink href={`/data#${t}`} className="font-mono" gate="plain">{t}</SiteLink></span>)}</> : null}
        {withFile.map((s) => (s.file!.built ? <span key={s.mark}>; the file of {s.name} built {s.file!.built.slice(0, 10)}</span> : null))}
        {index?.built ? <>; the index built {index.built.slice(0, 10)}</> : null}. This page is in review and reads the site&apos;s own copies of the files.
        {notes.map((m) => <span key={m}>{" "}<SiteLink href={`/data/methods/${m.replace(/^docs\/methods\//, "").replace(/\.md$/, "")}`}>The files&apos; method</SiteLink>.</span>)}
      </p>
    </div>
  );
}

/** What the page mounts: the index and the files read from site/data/regions/, the view drawn. */
export function CountryView({ q }: { q: Q }) {
  return <Country q={q} index={regionsIndex()} fileOf={demandPlaceFile} />;
}
