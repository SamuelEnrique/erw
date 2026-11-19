import type { Metadata } from "next";
import Link from "next/link";
import { Hint } from "@/components/demand/Hint";
import { Hover } from "@/components/demand/Hover";
import { CountryView } from "@/components/demand/Country";
import { ChangeBars, DOWN, Heat, UP, YearsChart } from "@/components/demand/Growth";
import { FIT_YEARS, WeatherView } from "@/components/demand/Weather";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/demand_growth.json";
import { caisoJoinDay } from "@/lib/caisoJoin";
import {
  RANKS, TABLE, byHour, byMonth, cells, choices, extremes, hourName, href, localHour, monthName, ranking, signed, slugOf, whole, wholeYears, yearToDate,
  type DemandFile,
} from "@/lib/demandgrowth";
import { CA_BASE_FAULT, HOUR_WHY, METHODS, caBaseWhy, viewHref, viewOf, type Fault } from "@/lib/demandpage";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { Tabs } from "@/components/tool/Tabs";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { DecisionsBlock } from "@/components/tool/DecisionsBlock";
import { DEMAND_DECISIONS } from "@/lib/decisions";
import { ConsumptionView } from "../consumption/view";
import { DEMAND_GROWTH_DECISIONS } from "../explore/demand-growth/Decisions";
import faultsJson from "@/data/data_faults.json";
import { demandGrowth } from "@/lib/siting";

// Session 7543 (chain 304, part C: the read of /demand as a utility planner reads it,
// docs/reviews/demand-read-2026-11-16.md). Three hovers the reader needed, each read from the file that holds the words
// on another page, so the two pages cannot say different things: the explorer's line on demand against retail sales
// (app/explore/demand-growth/Decisions.tsx, "against-sales"), the register's entry on California's early 2019
// (data/data_faults.json), and how an hour is named (the explorer's "local-time" line, in this page's words).
const AGAINST_SALES = (() => { const d = DEMAND_GROWTH_DECISIONS.find((x) => x.key === "against-sales")!; return `${d.text} ${d.def} Source: ${d.source}`; })();
const faults = faultsJson as unknown as { rows: Fault[]; status_words: Record<string, string> };
/** Session 7543 (the read, row 12): the All grids tab of the datacenter cost page computes its own demand growth from
 *  this file (lib/siting.ts, demandGrowth: the last twelve months over the twelve before), another period from this
 *  column's; the hover gives both for the grid shown, from the same function, so neither page reads as the other's error. */
function yoyWhy(name: string, slug: string, last: { year: string; row: Record<string, number> }) {
  const here = `${name}, ${last.year} on ${Number(last.year) - 1}: ${signed(last.row.avg_demand_growth_yoy_pct)} percent, a calendar year's average over the year before's.`;
  const g = demandGrowth(file as never, slug);
  if (!("pct" in g)) return here;
  return `${here} The All grids tab of the datacenter cost page (/cost-of-power?view=allgrids) gives ${signed(g.pct)} percent for ${monthName(Number(g.from.slice(5, 7)))} ${g.from.slice(0, 4)} to ${monthName(Number(g.to.slice(5, 7)))} ${g.to.slice(0, 4)} on the twelve months before, from the same table: another period, not another figure for this one.`;
}
const CA_2019 = faults.rows.find((f) => f.id === CA_BASE_FAULT);

// Demand growth, one page at one address (session 152), in review (lib/release.ts). Two views, both in the address
// (lib/demandpage.ts):
//   as metered (session 97)                    for the seven ISO balancing authorities and the Lower 48, annual average
//                                              and peak demand and their growth since 2019; where the growth sits by
//                                              month and hour; a ranking. Every number is a row of eia930_demand_growth
//                                              (warehouse/derived/demand_growth.py), from data/demand_growth.json.
//   with the weather taken out (126 and 129)   components/demand/Weather.tsx; it stood at /demand/weather on its branch,
//                                              and that address redirects here (next.config.ts).
// The two page files as they were are kept, unrouted, under app/_retired (demand-original, demand-weather). Every
// chart answers the mouse (components/demand/Hover.tsx). No method or limitations prose stands on the face: a short
// placeholder carries it as a hover (components/demand/Hint.tsx) and the method is in the two Method notes
// (docs/methods/demand_growth.md, docs/methods/demand_weather.md).
export const metadata: Metadata = { title: "Demand growth", robots: { index: false, follow: false } };

const file = fileJson as unknown as DemandFile;
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;
/** The first view: growth as metered (what /demand showed before session 152). */
function MeteredView({ q }: { q: Record<string, string | undefined> }) {
  const { ba, rank } = choices(q);
  const area = file.areas[ba];
  const slug = slugOf(ba);
  const ys = wholeYears(area);
  const first = ys[0], last = ys[ys.length - 1];
  const ytd = yearToDate(file, area);
  const ex = extremes(cells(file, area));
  const ranked = ranking(file, rank);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const g = (v: number | undefined, k: string) => (v === undefined ? NOT : <N k={k}>{signed(v)}</N>);
  /** A growth figure of a year's row: the base year has none, and says so. */
  const gy = (year: string, v: number | undefined, k: string) => (v === undefined && Number(year) === file.base ? <span className="text-muted">the base year</span> : g(v, k));
  const through = monthName(Number(file.ytd_through.slice(5)));
  const earlier = file.caiso_break.rows.slice(1).map((r) => r.ratio);
  const inside = file.caiso_break.rows.length > 1 && file.caiso_break.rows[0].ratio >= Math.min(...earlier) && file.caiso_break.rows[0].ratio <= Math.max(...earlier);
  const peakAt = (y: string, k = "peak_demand_mw") => (area.at[y]?.[k] ? localHour(area.at[y][k], area.tz) : null);

  return (
    <div data-view-body="metered">
      <p className="mb-8 text-sm" data-weather="1">
        <Hint words="Weather is not removed." why={`A year's demand is what was metered that year, hot summer and cold snap included. A grid whose ${file.last_year} was mild shows less growth than its customers added, and a single heat wave can set a peak. These are differences between years, not a trend line.`} />
        {" "}<SiteLink href={viewHref("weather")}>The same growth with the weather taken out</SiteLink> is the second view.{" "}
        <span data-against-sales="1"><Hint words="Demand at the grid is not retail sales." why={AGAINST_SALES} />{" "}<SiteLink href={viewHref("consumption")}>Retail sales by state and sector</SiteLink> are the third.</span>
        {ba === "CISO" && CA_2019 ? <>{" "}<span data-ca-base="1"><Hint words="California's base year is low in its early months." why={caBaseWhy(CA_2019, faults.status_words)} />{" "}<SiteLink href={`/data/faults#${CA_2019.id}`}>The register&apos;s entry</SiteLink>.</span></> : null}
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" reset={{ href: "/demand", defaults: "ERCOT, ranked by the growth of average demand since 2019." }} note={<>Whole years {first.year} to {last.year}. <Hint words="The year so far" why={`The year so far is January to ${through} of each year, so ${Number(last.year) + 1} is compared with the same months of ${file.base}.`} /></>}>
            <nav aria-label="Area" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {file.order.map((b) => <div key={b}><Link href={href(slugOf(b), rank.slug)} aria-current={b === ba ? "true" : undefined} className={item(b === ba)}>{file.areas[b].name}</Link></div>)}
            </nav>
            <nav aria-label="Ranking" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Rank the grids by growth in</div>
              {RANKS.map((r) => <div key={r.slug}><Link href={`${href(slug, r.slug)}#ranking`} aria-current={r.slug === rank.slug ? "true" : undefined} className={item(r.slug === rank.slug)}>{r.name}</Link></div>)}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
            From {first.year} to {last.year}, {area.name}&apos;s average demand went from <N k="sum|avg0">{whole(first.row.avg_demand_mw)}</N> MW to <N k="sum|avg1">{whole(last.row.avg_demand_mw)}</N> MW, a change of <N k="sum|avg_growth">{signed(last.row.avg_demand_growth_since_2019_pct)}</N> percent
            {last.row.peak_demand_mw !== undefined ? <>, and its highest hour from <N k="sum|peak0">{whole(first.row.peak_demand_mw)}</N> MW to <N k="sum|peak1">{whole(last.row.peak_demand_mw)}</N> MW (<N k="sum|peak_growth">{signed(last.row.peak_demand_growth_since_2019_pct)}</N> percent)</> : null}.{" "}
            {ytd ? <>January to {through} of {ytd.year} ran <N k="sum|ytd_growth">{signed(ytd.row.ytd_avg_demand_growth_since_2019_pct)}</N> percent against the same months of {file.base}.</> : null}{" "}
            {ex ? <>The growth is largest in {monthName(ex.most.month)} at {hourName(ex.most.hour)} (<N k="sum|cell_most">{signed(ex.most.pct)}</N> percent).</> : null} Weather is not removed.
          </p>
          <HeadlineRow>
            <HeadlineNumber label={`Average demand, ${first.year} to ${last.year}`} value={<N k="head|avg_growth">{signed(last.row.avg_demand_growth_since_2019_pct)}</N>} unit="percent"
              note={<><N k="head|avg0">{whole(first.row.avg_demand_mw)}</N> MW to <N k="head|avg1">{whole(last.row.avg_demand_mw)}</N> MW, the mean of the year&apos;s hours.</>} />
            <HeadlineNumber label="Peak demand" value={g(last.row.peak_demand_growth_since_2019_pct, "head|peak_growth")} unit={last.row.peak_demand_mw !== undefined ? "percent" : undefined}
              note={last.row.peak_demand_mw !== undefined
                ? <><N k="head|peak1">{whole(last.row.peak_demand_mw)}</N> MW on {peakAt(last.year)}, against <N k="head|peak0">{whole(first.row.peak_demand_mw)}</N> MW on {peakAt(first.year)}.</>
                : <Hint words="No peak is given for the Lower 48" why="Its total holds its members' faulty hours, and one of them would be the peak." />} />
            <HeadlineNumber label={ytd ? `${ytd.year} so far, against ${file.base}` : "The year so far"} value={ytd ? <N k="head|ytd_growth">{signed(ytd.row.ytd_avg_demand_growth_since_2019_pct)}</N> : NOT} unit={ytd ? "percent" : undefined}
              note={ytd ? <>January to {through}: <N k="head|ytd1">{whole(ytd.row.ytd_avg_demand_mw)}</N> MW on average, against <N k="head|ytd0">{whole(ytd.base.ytd_avg_demand_mw)}</N> MW in the same months of {file.base}.</> : null} />
          </HeadlineRow>

          <ToolSection title="Year by year"
            note={<>Hours left out for {area.name}: <N k="screen|jumps">{whole(area.screened.jumps)}</N> that stand apart from their neighbours, <N k="screen|zero">{whole(area.screened.not_positive)}</N> at or below zero, <N k="screen|blank">{whole(area.screened.blank)}</N> blank.{" "}
              <Hint words="Which hours are used" why={`From EIA-930's hourly demand. An hour is used when its demand is above zero and within ${Math.round(file.jump * 100)} percent of the median of the four hours around it: EIA's file holds faulty hours, and a faulty high hour would otherwise be a year's peak. A year is written when at least ${Math.round(file.near_year * 100)} percent of its hours are used; its average is the mean of those hours. Nothing is filled.`} />{" "}
              <Hint words="The last row" why={`The last row compares January to ${through} of ${ytd?.year ?? "the newest year"} with January to ${through} of ${file.base}: its growth is against those months, not against the whole of ${file.base}.`} /></>}>
            <ChartFrame title={`${area.name}: demand, MW`} legend={[{ label: "Average over the year", color: "var(--color-accent)" }, ...(last.row.peak_demand_mw !== undefined ? [{ label: "The year's highest hour", color: "var(--color-ink)" }] : [])]}>
              <Hover><YearsChart area={area} /></Hover>
            </ChartFrame>
            <ToolTable minWidth={760} caption={`${area.name}: average and peak demand by year`}
              head={["Year", "Average, MW", `Since ${file.base}, percent`, <span key="yoy" title={yoyWhy(area.name, slug, last)} data-yoy-why="1" className="cursor-help border-b border-dotted border-muted">On the year before, percent</span>, "Peak, MW", <span key="when" title={HOUR_WHY} data-hour-why="when" className="cursor-help border-b border-dotted border-muted">When, local time</span>, `Peak since ${file.base}, percent`, "Hours used"]}
              rows={[...ys.map(({ year, row }) => ({ key: year, cells: [year, <N key="a" k={`y|${year}|avg`}>{whole(row.avg_demand_mw)}</N>, gy(year, row.avg_demand_growth_since_2019_pct, `y|${year}|avg_growth`), gy(year, row.avg_demand_growth_yoy_pct, `y|${year}|yoy`),
                row.peak_demand_mw !== undefined ? <N key="p" k={`y|${year}|peak`}>{whole(row.peak_demand_mw)}</N> : NOT, peakAt(year) ?? NOT, gy(year, row.peak_demand_growth_since_2019_pct, `y|${year}|peak_growth`),
                <span key="h"><N k={`y|${year}|hours`}>{whole(row.hours_used)}</N> of {whole(row.hours_in_year)}</span>] })),
              ...(ytd ? [{ key: "ytd", highlight: true, cells: [`${ytd.year}, to ${through}`, <N key="a" k="ytd|avg">{whole(ytd.row.ytd_avg_demand_mw)}</N>, g(ytd.row.ytd_avg_demand_growth_since_2019_pct, "ytd|avg_growth"), <span key="n" className="text-muted">same months</span>,
                ytd.row.ytd_peak_demand_mw !== undefined ? <N key="p" k="ytd|peak">{whole(ytd.row.ytd_peak_demand_mw)}</N> : NOT, peakAt(ytd.year, "ytd_peak_demand_mw") ?? NOT, g(ytd.row.ytd_peak_demand_growth_since_2019_pct, "ytd|peak_growth"),
                <span key="h"><N k="ytd|hours">{whole(ytd.row.ytd_hours_used)}</N> of {whole(ytd.row.ytd_hours_in_window)}</span>] }] : [])]} />
          </ToolSection>

          <ToolSection title="Where the growth is" id="where"
            note={<Hint words="How to read the cells" why={`Each cell is one hour of the day in one month: the average demand of that hour over the month in ${file.last_year}, against the same in ${file.base}. Red is growth, dark grey a fall; the deeper, the larger. One hot or mild month colors a whole row, which is the weather and not a trend. ${HOUR_WHY}`} />}>
            <ChartFrame title={`${area.name}: change from ${file.base} to ${file.last_year}, percent, by month and hour of the day`} legend={[{ label: "Growth", color: UP }, { label: "Fall", color: DOWN }]}>
              <Hover><Heat area={area} file={file} /></Hover>
            </ChartFrame>
            {ex ? <p className="mb-6 max-w-3xl text-sm" data-extremes="1">Largest: {monthName(ex.most.month)} at {hourName(ex.most.hour)}, <N k="cell|most|pct">{signed(ex.most.pct)}</N> percent (<N k="cell|most|mw">{whole(ex.most.mw)}</N> MW). Smallest: {monthName(ex.least.month)} at {hourName(ex.least.hour)}, <N k="cell|least|pct">{signed(ex.least.pct)}</N> percent (<N k="cell|least|mw">{whole(ex.least.mw)}</N> MW).</p> : null}
            <div className="grid gap-x-6 xl:grid-cols-2">
              <ChartFrame title="By month"><Hover><ChangeBars file={file} items={byMonth(file, area).map((m) => ({ label: monthName(m.month), pct: m.pct }))} what="by month" /></Hover></ChartFrame>
              <ChartFrame title="By hour of the day"><Hover><ChangeBars file={file} items={byHour(file, area).map((h) => ({ label: hourName(h.hour), pct: h.pct }))} what="by hour" /></Hover></ChartFrame>
            </div>
          </ToolSection>

          <ToolSection title={`The ranking: growth in ${rank.name.toLowerCase()}`} id="ranking"
            note={<Hint words="What is ranked" why={`Percent change since ${file.base}: average and peak demand to ${file.last_year}; the year so far is January to ${through} against the same months of ${file.base}. The Lower 48 is the total, not a grid among the seven.`} />}>
            <ToolTable minWidth={620} caption={`The grids ranked by growth in ${rank.name.toLowerCase()} since ${file.base}`}
              head={["", "Grid", ...RANKS.map((r) => <Link key={r.slug} href={`${href(slug, r.slug)}#ranking`} className="underline" data-rank={r.slug}>{r.name}{r.slug === rank.slug ? " ↓" : ""}</Link>)]}
              rows={ranked.map((r, i) => ({ key: r.ba, highlight: r.ba === ba, muted: r.ba === "US48", cells: [r.ba === "US48" ? "" : String(ranked.filter((x) => x.ba !== "US48").findIndex((x) => x.ba === r.ba) + 1), <Link key="l" href={href(slugOf(r.ba), rank.slug)} className="text-ink" data-ranked={`${i}|${r.ba}`}>{r.name}</Link>,
                g(r.avg, `rank|${r.ba}|avg`), g(r.peak, `rank|${r.ba}|peak`), g(r.ytd, `rank|${r.ba}|ytd`)] }))} />
          </ToolSection>

          {ba === "CISO" ? (
            <ToolSection title="California across the break of December 2025" id="break"
              note={<Hint words="What this check is" why={`EIA's generation series for California changed on ${caisoJoinDay()}; this page uses demand, which is a different series. The check: the average demand of the 28 days before that date and of the 28 days from it, in 2025 and on the same dates of every earlier year. A step in the series would show as a ratio outside the earlier years' range. California's hours of November 2023 to early December 2025, which EIA dates one hour late, are set back before anything is computed.`} />}>
              <ToolTable minWidth={520} caption="California's demand in the 28 days before and after the date of the break, by year"
                head={["Year", "28 days before, MW", "28 days from the date, MW", "The second over the first"]}
                rows={file.caiso_break.rows.map((r) => ({ key: String(r.year), highlight: r.year === file.caiso_break.rows[0].year, cells: [String(r.year), <N key="b" k={`break|${r.year}|before`}>{whole(r.before_mw)}</N>, <N key="a" k={`break|${r.year}|after`}>{whole(r.after_mw)}</N>, <N key="r" k={`break|${r.year}|ratio`}>{r.ratio.toFixed(4)}</N>] }))} />
              <p className="mt-3 max-w-3xl text-sm" data-break="1">In {file.caiso_break.rows[0].year} the ratio is {file.caiso_break.rows[0].ratio.toFixed(4)}{file.caiso_break.rows.length > 1 ? <>; in the {file.caiso_break.rows.length - 1 === 6 ? "six" : file.caiso_break.rows.length - 1} earlier years it runs from {Math.min(...file.caiso_break.rows.slice(1).map((r) => r.ratio)).toFixed(4)} to {Math.max(...file.caiso_break.rows.slice(1).map((r) => r.ratio)).toFixed(4)}</> : null}.{" "}{/* session 281: no range from no earlier year */}
                {inside ? <>California&apos;s demand does not step at the break.</> : <>That is outside the earlier years&apos; range.</>}</p>
            </ToolSection>
          ) : null}

          <DecisionsBlock id="7018-demand" title="Decisions on this page (each with its default and its source on hover)" items={DEMAND_DECISIONS} />
          <SourceLine tables={[TABLE]} note={<>Derived from EIA Form EIA-930, hourly demand (public domain); built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the table.</>} />
        </div>
      </div>
    </div>
  );
}

export default async function Demand({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const view = viewOf(q);
  // session 239: the page is on the brand, its views are the shared tabs (components/tool/Tabs.tsx), and consumption
  // (what /consumption showed) is the third of them
  if (view === "consumption") {
    return (
      <Brand>
        <ToolPage>
          <div data-demand={view}>
            <Tabs page="/demand" active={view} />
            {/* session 331: the view's method note (docs/methods/consumption.md) and its two tables to download */}
            <p className="mb-4 text-xs text-muted" data-method="1"><SiteLink href="/data/methods/consumption">Method, sources and gaps</SiteLink></p>
            {/* session 7543: the same line as the as-metered view's, so a reader setting a state's sales beside a grid's demand meets it on both */}
            <p className="mb-4 text-sm" data-against-sales="1"><Hint words="Retail sales are not demand at the grid." why={AGAINST_SALES} />{" "}<SiteLink href={viewHref("metered")}>Demand at the grid, as metered</SiteLink> is the first view.</p>
            <ConsumptionView />
            <TableDownloads tables={["eia_retail_sales_monthly", "eia_sector_energy_consumption_monthly"]} />
            <Related href="/demand" />
          </div>
        </ToolPage>
      </Brand>
    );
  }
  // session 8420 (chain 503, part C): the whole country, the fourth view: any of EIA's thirteen regions and any
  // balancing authority, two side by side (components/demand/Country.tsx). The three views before it are not touched.
  if (view === "country") {
    return (
      <Brand>
        <ToolPage>
          <div data-demand={view}>
            <Tabs page="/demand" active={view} />
            <CountryView q={q} />
          </div>
        </ToolPage>
      </Brand>
    );
  }
  return (
    <Brand>
    <ToolPage>
      <div data-demand={view}>
        <Tabs page="/demand" active={view} />
        <ToolHeader title="Demand growth"
          lead={view === "weather"
            ? <>For the seven grid operators and each year since {FIT_YEARS.to}: how much demand rose against the average of {FIT_YEARS.from} to {FIT_YEARS.to}, how much of that the year&apos;s weather explains, and how much it does not. Weather from NOAA&apos;s stations, demand from EIA&apos;s hourly record.</>
            : <>How much more power each grid uses than it did in {file.base}: the average over the year, the highest hour of the year, and in which months and hours of the day the growth sits. The seven grid operators and the Lower 48, from EIA&apos;s hourly record.
              See also <SiteLink href="/queues">the interconnection queue</SiteLink> and <SiteLink href="/prices/compare">where power is cheap</SiteLink>.</>} />
        <p className="mb-6 text-xs text-muted" data-method="1"><SiteLink href={METHODS[view].href}>Method, sources and gaps</SiteLink></p>
        {view === "weather" ? <WeatherView q={q} /> : <MeteredView q={q} />}
        {/* session 331: the view's tables, as CSV with a Python and a Stata reader (session 328's shared line) */}
        <TableDownloads tables={view === "weather" ? ["eia930_demand_weather", "noaa_grid_weather_hourly", "noaa_grid_weather_stations"] : ["eia930_demand_growth"]} />
      </div>
    </ToolPage>
    </Brand>
  );
}
