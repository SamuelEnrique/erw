import type { Metadata } from "next";
import type { ReactNode } from "react";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ExploreFrame, FilterForm } from "@/components/explore/Explore";
import { HeldFreshness } from "@/components/explore/HeldFreshness";
import { GroupedBars } from "@/components/tool/GroupedBars";
import { ChartFrame, HeadlineNumber, HeadlineRow, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { headers } from "@/lib/data";
import { choose, isoKey, type Params } from "@/lib/explore";
import {
  BASE, DEFAULT_GRID, DEFAULT_WINDOW, GRIDS, TABLE, WINDOWS, entityOf, lastWhole, latestOf, monthName, newest, valueOf, variablesOf,
  viewHref, windowOf, yearTs, yearsOf, ytdThrough, type Row,
} from "@/lib/explore/demandgrowth";
import { shown } from "@/lib/format";
import { HOURLY, attempt, rest } from "@/lib/supabase";

// Session 404: the demand growth explorer (platform tool 5, the second signature explorer), in review. Growth since
// 2019 by grid and by window of the year, from eia930_demand_growth as it stands in the live set: for any of the seven
// grid operators and the Lower 48, the whole year's average hour or its highest hour, the year so far, one calendar
// month or one local hour of the day. The ERW's documents name no "thesis chart" for demand growth; the first chart is
// the table's own headline figure, growth since 2019, for every grid, in the window chosen. The filters are a GET form,
// so every figure is drawn on the server from one row of the table and carries that row's check key
// (scripts/check-values.mjs reads it again). Nothing is computed here. The same table is drawn on /demand (as metered),
// with its month-and-hour map and its ranking; that page is left as it is.
export const metadata: Metadata = { title: "Demand growth explorer" };
export const dynamic = "force-dynamic";

const PATH = "/explore/demand-growth";
const SELECT = "entity,variable,ts_utc,value";
const t0 = (y: number) => Date.UTC(y, 0, 1) / 1000;

export default async function DemandGrowthExplorer({ searchParams }: { searchParams: Promise<Params> }) {
  const sp = await searchParams;
  const [gridS, badGrid] = choose(sp, "grid", GRIDS.map((g) => g.slug), DEFAULT_GRID);
  const [winS, badWin] = choose(sp, "window", WINDOWS.map((w) => w.slug), DEFAULT_WINDOW);
  const grid = GRIDS.find((g) => g.slug === gridS)!;
  const win = windowOf(winS)!;
  const [read, header] = await Promise.all([
    attempt(() => rest<Row>("series", { select: SELECT, table_name: `eq.${TABLE}`, variable: `in.(${variablesOf(win).join(",")})`, order: "entity,variable,ts_utc" }, HOURLY)),
    attempt(() => headers(TABLE)),
  ]);
  const through = header.ok ? ytdThrough(header.data) : null;
  const so = (y: number) => (through && y === through.year ? ` so far (January to ${monthName(through.month)})` : "");
  const fresh = (
    <HeldFreshness
      tables={[TABLE]}
      detail={<>{through ? <>The newest year, {through.year}, is partial: the table holds its year so far, 1 January to the end of {monthName(through.month)} {through.year} (the table&apos;s header), and compares it with the same months of {BASE}. </> : null}Weather is not removed: a year&apos;s demand is what was metered that year.</>}
    />
  );
  const asked = [badGrid && "grid", badWin && "window"].filter(Boolean);
  const filters = (
    <FilterForm
      action={PATH}
      fields={[
        { name: "grid", label: "Grid", value: grid.slug, options: GRIDS.map((g) => ({ value: g.slug, label: g.name })) },
        { name: "window", label: "Window", value: win.slug, options: WINDOWS.map((w) => ({ value: w.slug, label: w.label })) },
      ]}
      reset={{ href: PATH, defaults: "ERCOT, the whole year's average hour (the table's headline: average demand growth since 2019)" }}
      note={asked.length ? <span data-asked-unknown="1">The address asked for a {asked.join(" and a ")} the table does not hold; the page shows the default in its place.</span> : undefined}
    />
  );
  const frame = (body: ReactNode) => (
    <ExploreFrame
      id="demand-growth"
      title="Demand growth"
      definition={<>Demand growth is how much more power a grid used than in {BASE}: the change in its average hour (or its highest hour) of metered demand, in percent, over the whole year, the year so far, one month or one hour of the day, from EIA&apos;s hourly demand of the seven grid operators and the Lower 48. Weather is not removed.</>}
      fresh={fresh}
      filters={filters}
      method={{ href: "/data/methods/demand_growth", label: "Demand growth since 2019" }}
      tables={[TABLE]}
      sourceNote={<>EIA Form EIA-930 (Hourly Electric Grid Monitor), hourly demand: a balancing authority&apos;s adjusted demand, and the Lower 48&apos;s demand; an hour is used when it is held, above zero and within 25 percent of the four hours around it. Public domain.</>}
    >
      {body}
    </ExploreFrame>
  );
  if (!read.ok || read.data.length === 0) {
    return frame(<NoData what={TABLE} reason={read.ok ? "the table returned no rows" : read.reason} />);
  }

  const rows = read.data;
  const e = entityOf(grid.ba);
  const latest = latestOf(rows, e, win);
  const whole = lastWhole(rows, e);
  const recent = newest(rows, e);
  const key = (entity: string, variable: string, y: number) => `series|${TABLE}|${entity}|${variable}|${isoKey(yearTs(y))}`;
  const val = (entity: string, variable: string, y: number | undefined) => (y === undefined ? undefined : valueOf(rows, entity, variable, y));
  // a figure: MW written whole (check-values reads this table's MW keys as whole), a percent with its sign outside the number
  const N = ({ entity = e, v, y, pct }: { entity?: string; v: string; y: number | undefined; pct?: boolean }) => {
    const x = val(entity, v, y);
    if (x === undefined || y === undefined) return <span className="text-muted">not held</span>;
    const text = pct || v.startsWith("growth_pct") ? shown(x) : Math.round(x).toLocaleString("en-US");
    return <>{pct && x > 0 ? "+" : ""}<Num check={key(entity, v, y)} raw={x}>{text}</Num></>;
  };
  const when = (y: number | undefined) => (y === undefined ? "" : `${y}${win.latest === "newest" ? so(y) : ""}`);
  const ytdWords = (y: number | undefined) => (y === undefined ? "" : `${y}${so(y) || (through ? ` (January to ${monthName(through.month)})` : "")}`);
  const signedText = (v: number) => `${v > 0 ? "+" : ""}${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  // the thesis chart: growth since the base year by grid, in the window chosen, each grid at its own latest year
  const byGrid = GRIDS.map((g) => {
    const ge = entityOf(g.ba), y = latestOf(rows, ge, win);
    return { g, y, v: val(ge, win.growth, y) };
  });
  const ordered = [...byGrid].sort((a, b) => (a.v === undefined ? 1 : b.v === undefined ? -1 : b.v - a.v));
  const third: { label: string; value: ReactNode; unit: string } = win.growthMw
    ? { label: `Change since ${BASE}, ${win.short}, ${grid.name}, ${when(latest)}`, value: <N v={win.growthMw} y={latest} />, unit: "MW" }
    : win.slug === "ytd"
      ? { label: `Average demand growth since ${BASE}, whole year, ${grid.name}, ${whole ?? ""}`, value: <N v="avg_demand_growth_since_2019_pct" y={whole} pct />, unit: "percent" }
      : { label: `The year so far: growth since ${BASE}, ${grid.name}, ${ytdWords(recent)}`, value: <N v="ytd_avg_demand_growth_since_2019_pct" y={recent} pct />, unit: "percent" };
  const along = (variable: string): Line["points"] => yearsOf(rows, e, variable)
    .map((y) => ({ t: t0(y), v: val(e, variable, y) }))
    .filter((p): p is { t: number; v: number } => p.v !== undefined);
  const growthLines: Line[] = [
    { label: "Average hour, whole year", points: along("avg_demand_growth_since_2019_pct"), color: "accent" },
    { label: "Highest hour, whole year", points: along("peak_demand_growth_since_2019_pct"), color: "ink" },
    { label: `The year so far${through ? ` (January to ${monthName(through.month)})` : ""}`, points: along("ytd_avg_demand_growth_since_2019_pct"), color: "muted" },
  ].filter((l) => l.points.length > 0);
  const years = yearsOf(rows, e, win.mw);
  const noPeak = grid.ba === "US48";

  const body = (
    <>
      <HeadlineRow>
        <HeadlineNumber label={`Growth since ${BASE}, ${win.short}, ${grid.name}, ${when(latest)}`} value={<N v={win.growth} y={latest} pct />} unit="percent"
          note={<>{BASE}{win.latest === "newest" && through ? `, January to ${monthName(through.month)}` : ""}: <N v={win.mw} y={BASE} /> MW; {latest ?? ""}: <N v={win.mw} y={latest} /> MW</>} />
        <HeadlineNumber label={`${win.short[0].toUpperCase()}${win.short.slice(1)}, ${grid.name}, ${when(latest)}`} value={<N v={win.mw} y={latest} />} unit="MW"
          note={<>{BASE}: <N v={win.mw} y={BASE} /> MW</>} />
        <HeadlineNumber label={third.label} value={third.value} unit={third.unit} />
      </HeadlineRow>

      <ChartFrame title={`The headline chart: growth since ${BASE} by grid, ${win.short}`}
        note={<>One bar a grid, at its {win.latest === "newest" ? "newest year, the year so far against the same months of " + BASE : "last whole year"}, largest first; {grid.name} is marked &quot;shown below&quot;. Each bar is one row of the table; its figure is in the table under the chart.{byGrid.some((x) => x.v === undefined) ? <> A grid without a bar has no row for this window{win.slug === "peak" ? " (the Lower 48 has no peak: the method note says why)" : ""}.</> : null}</>}>
        <div className="border border-rule bg-panel p-3" data-thesis-chart="1">
          <GroupedBars id="growth-by-grid" unit="percent" label={`Growth since ${BASE} of ${win.short}, by grid, percent`}
            series={[{ name: `Growth since ${BASE}, ${win.label.toLowerCase()}`, tone: "accent" }]}
            fmt={signedText}
            groups={ordered.map(({ g, y, v }) => ({
              label: g.name, sub: g.slug === grid.slug ? "shown below" : v === undefined ? "not held" : undefined, values: [v ?? null],
              title: v === undefined ? `${g.name}: not held` : `${g.name}: ${signedText(v)} percent from ${BASE} to ${y}`,
            }))} />
        </div>
      </ChartFrame>

      <ToolSection title={`Every grid: ${win.short}`} note={`Each grid at its ${win.latest === "newest" ? "newest year (the year so far)" : "last whole year"}; a grid's name opens it in this window.`}>
        <ToolTable caption={`Growth since ${BASE} of ${win.short}, by grid`} minWidth={win.growthMw ? 520 : 440}
          head={["Grid", `${BASE}, MW`, `${win.latest === "newest" ? "Newest year" : "Last whole year"}, MW`, `Growth since ${BASE}, percent`, ...(win.growthMw ? ["Change, MW"] : [])]}
          rows={byGrid.map(({ g, y }) => {
            const ge = entityOf(g.ba);
            return {
              key: g.slug, highlight: g.slug === grid.slug,
              cells: [
                <Link key="g" href={viewHref(g.slug, win.slug)}>{g.name}</Link>,
                <N key="b" entity={ge} v={win.mw} y={BASE} />,
                <span key="l"><N entity={ge} v={win.mw} y={y} />{y !== undefined ? <span className="ml-1 text-xs text-muted">{y}</span> : null}</span>,
                <N key="p" entity={ge} v={win.growth} y={y} pct />,
                ...(win.growthMw ? [<span key="m">{(val(ge, win.growthMw, y) ?? 0) > 0 ? "+" : ""}<N entity={ge} v={win.growthMw} y={y} /></span>] : []),
              ],
            };
          })} />
      </ToolSection>

      <ChartFrame title={`${grid.name}: growth since ${BASE}, year by year, by window`}
        note={<>Each point is a year&apos;s row of the table, against {BASE}.{noPeak ? " No peak is given for the Lower 48 (the method note says why)." : ""}{through ? ` The year so far compares 1 January to the end of ${monthName(through.month)} of each year with the same months of ${BASE}; ${through.year} has only that window.` : ""}</>}>
        {growthLines.length === 0 ? <NoData what={TABLE} reason={`no growth rows for ${grid.name}`} /> : (
          <LineChart x="year" unit="percent" height={260} ariaLabel={`${grid.name}: growth since ${BASE} of average demand, peak demand and the year so far, by year`} lines={growthLines} />
        )}
      </ChartFrame>

      <ChartFrame title={`${grid.name}: ${win.short} by year, MW`}
        note={<>One point a year the table holds for this window{win.growthMw ? "; the change since " + BASE + " is written on the last whole year's row only" : ""}.</>}>
        {years.length === 0 ? <NoData what={TABLE} reason={`no ${win.mw} rows for ${grid.name}`} /> : (
          <LineChart x="year" unit="MW" height={240} ariaLabel={`${grid.name}: ${win.short} by year, MW`} lines={[{ label: win.label, points: along(win.mw), color: "accent" }]} />
        )}
      </ChartFrame>

      <ToolSection title={`${grid.name}, year by year: ${win.short}`}
        note={win.slug === "avg" ? "Hours used: the hours of the year whose demand passed the method's test; a year is written when at least 95 percent of its hours are used." : win.slug === "ytd" ? "Hours used: the hours of the window whose demand passed the method's test." : undefined}>
        <ToolTable caption={`${grid.name}: ${win.short}, every year the table holds`} minWidth={360}
          head={["Year", "MW", ...(win.perYear ? [`Growth since ${BASE}, percent`] : []), ...(win.slug === "avg" ? ["On the year before, percent", "Hours used", "Hours in the year"] : []), ...(win.slug === "ytd" ? ["Hours used", "Hours in the window"] : [])]}
          rows={years.map((y) => ({
            key: String(y), highlight: y === latest,
            cells: [
              `${y}${win.latest === "newest" ? so(y) : ""}`,
              <N key="mw" v={win.mw} y={y} />,
              ...(win.perYear ? [y === BASE ? <span key="g" className="text-muted">base year</span> : <N key="g" v={win.growth} y={y} pct />] : []),
              ...(win.slug === "avg" ? [y === BASE ? <span key="o" className="text-muted">base year</span> : <N key="o" v="avg_demand_growth_yoy_pct" y={y} pct />, <N key="u" v="hours_used" y={y} />, <N key="h" v="hours_in_year" y={y} />] : []),
              ...(win.slug === "ytd" ? [<N key="u" v="ytd_hours_used" y={y} />, <N key="h" v="ytd_hours_in_window" y={y} />] : []),
            ],
          }))} />
      </ToolSection>

      <p className="max-w-3xl text-sm" data-related-view="1">
        The same table is drawn on <Link href="/demand">Demand growth</Link>, with the map of where the growth sits by month and hour of the day
        and a ranking of the grids; this explorer reads any grid in any window of the year, every figure checked against the live set.
      </p>
    </>
  );
  return frame(body);
}
