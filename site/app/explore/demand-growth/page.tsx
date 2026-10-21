import type { Metadata } from "next";
import type { ReactNode } from "react";
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
  // a figure: MW written whole (check-values reads this table's MW keys as whole); a growth (percent or MW) with its sign outside the number
  const n = (entity: string, v: string, y: number | undefined, pct?: boolean): ReactNode => {
    const x = val(entity, v, y);
    if (x === undefined || y === undefined) return <span className="text-muted">not held</span>;
    const text = pct || v.startsWith("growth_pct") ? shown(x) : Math.round(x).toLocaleString("en-US");
    return <>{(pct || v.startsWith("growth_")) && x > 0 ? "+" : ""}<Num check={key(entity, v, y)} raw={x}>{text}</Num></>;
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
    ? { label: `Change since ${BASE}, ${win.short}, ${grid.name}, ${when(latest)}`, value: n(e, win.growthMw, latest), unit: "MW" }
    : win.slug === "ytd"
      ? { label: `Average demand growth since ${BASE}, whole year, ${grid.name}, ${whole ?? ""}`, value: n(e, "avg_demand_growth_since_2019_pct", whole, true), unit: "percent" }
      : { label: `The year so far: growth since ${BASE}, ${grid.name}, ${ytdWords(recent)}`, value: n(e, "ytd_avg_demand_growth_since_2019_pct", recent, true), unit: "percent" };
  // the grid's growth by window along the years: one group a year, one bar a window (the site's bar chart, whose year
  // labels are the years themselves); a window without a row that year has no bar
  const GROWTH = [
    { v: "avg_demand_growth_since_2019_pct", name: "Average hour, whole year", tone: "accent" as const },
    { v: "peak_demand_growth_since_2019_pct", name: "Highest hour, whole year", tone: "ink" as const },
    { v: "ytd_avg_demand_growth_since_2019_pct", name: `The year so far${through ? ` (January to ${monthName(through.month)})` : ""}`, tone: "muted" as const },
  ].filter((s) => yearsOf(rows, e, s.v).length > 0);
  const growthYears = Array.from(new Set(GROWTH.flatMap((s) => yearsOf(rows, e, s.v)))).sort((a, b) => a - b);
  const years = yearsOf(rows, e, win.mw);
  const noPeak = grid.ba === "US48";

  const body = (
    <>
      {noPeak && win.slug === "peak" ? (
        <p className="mb-6 max-w-3xl text-sm" data-no-window="1">
          The table gives no peak for the Lower 48: its demand is EIA&apos;s sum over every balancing authority, faulty hours included, so its highest hour
          could be a fault (the <Link href="/data/methods/demand_growth">method note</Link> says why). The other grids&apos; peaks are below.
        </p>
      ) : null}
      <HeadlineRow>
        <HeadlineNumber label={`Growth since ${BASE}, ${win.short}, ${grid.name}, ${when(latest)}`} value={n(e, win.growth, latest, true)} unit="percent"
          note={<>{BASE}{win.latest === "newest" && through ? `, January to ${monthName(through.month)}` : ""}: {n(e, win.mw, BASE)} MW; {latest ?? ""}: {n(e, win.mw, latest)} MW</>} />
        <HeadlineNumber label={`${win.short[0].toUpperCase()}${win.short.slice(1)}, ${grid.name}, ${when(latest)}`} value={n(e, win.mw, latest)} unit="MW"
          note={<>{BASE}: {n(e, win.mw, BASE)} MW</>} />
        <HeadlineNumber label={third.label} value={third.value} unit={third.unit} />
      </HeadlineRow>

      <ChartFrame title={`The headline chart: growth since ${BASE} by grid, ${win.short}`}
        note={<>One bar a grid, at its {win.latest === "newest" ? "newest year, the year so far against the same months of " + BASE : "last whole year"}, largest first; {grid.name} is marked &quot;shown below&quot;. Each bar is one row of the table; its figure is in the table under the chart.{byGrid.some((x) => x.v === undefined) ? <> A grid without a bar has no row for this window{win.slug === "peak" ? " (the Lower 48 has no peak: the method note says why)" : ""}.</> : null}</>}>
          <GroupedBars id="growth-by-grid" unit="percent" label={`Growth since ${BASE} of ${win.short}, by grid, percent`}
            series={[{ name: `Growth since ${BASE}: ${win.label}`, tone: "accent" }]}
            fmt={signedText}
            groups={ordered.map(({ g, y, v }) => ({
              label: g.name, sub: g.slug === grid.slug ? "shown below" : v === undefined ? "not held" : undefined, values: [v ?? null],
              title: v === undefined ? `${g.name}: not held` : `${g.name}: ${signedText(v)} percent from ${BASE} to ${y}`,
            }))} />
      </ChartFrame>

      <ToolSection title={`Every grid: ${win.short}`} note={`Each grid at its ${win.latest === "newest" ? "newest year (the year so far)" : "last whole year"}; a grid's name opens it in this window.`}>
        <ToolTable caption={`Growth since ${BASE} of ${win.short}, by grid`} minWidth={win.growthMw ? 520 : 440}
          head={["Grid", `${BASE}, MW`, `${latest ?? (win.latest === "newest" ? "Newest year" : "Last whole year")}, MW`, `Growth since ${BASE}, percent`, ...(win.growthMw ? ["Change, MW"] : [])]}
          rows={byGrid.map(({ g, y }) => {
            const ge = entityOf(g.ba);
            return {
              key: g.slug, highlight: g.slug === grid.slug,
              cells: [
                <Link key="g" href={viewHref(g.slug, win.slug)}>{g.name}</Link>,
                <span key="b">{n(ge, win.mw, BASE)}</span>,
                <span key="l">{n(ge, win.mw, y)}{y !== undefined && y !== latest ? <span className="ml-1 text-xs text-muted">{y}</span> : null}</span>,
                <span key="p">{n(ge, win.growth, y, true)}</span>,
                ...(win.growthMw ? [<span key="m">{n(ge, win.growthMw, y)}</span>] : []),
              ],
            };
          })} />
      </ToolSection>

      <ChartFrame title={`${grid.name}: growth since ${BASE}, year by year, by window`}
        note={<>Each bar is a year&apos;s row of the table, against {BASE}; the three figures of a year are in its hover.{noPeak ? " No peak is given for the Lower 48 (the method note says why)." : ""}{through ? ` The year so far compares 1 January to the end of ${monthName(through.month)} of each year with the same months of ${BASE}; ${through.year} has only that window.` : ""}</>}>
        {GROWTH.length === 0 ? <NoData what={TABLE} reason={`no growth rows for ${grid.name}`} /> : (
          <GroupedBars id="growth-by-window" unit="percent" label={`${grid.name}: growth since ${BASE} of average demand, peak demand and the year so far, by year, percent`}
            series={GROWTH.map((s) => ({ name: s.name, tone: s.tone }))} fmt={() => ""}
            groups={growthYears.map((y) => {
              const vs = GROWTH.map((s) => val(e, s.v, y));
              return {
                label: String(y), values: vs.map((v) => v ?? null),
                title: `${grid.name}, ${y}: ${GROWTH.map((s, k) => `${s.name.toLowerCase()} ${vs[k] === undefined ? "not held" : signedText(vs[k]!) + " percent"}`).join("; ")}`,
              };
            })} />
        )}
      </ChartFrame>

      <ChartFrame title={`${grid.name}: ${win.short} by year, MW`}
        note={<>One bar a year the table holds for this window{win.growthMw ? "; the change since " + BASE + " is written on the last whole year's row only" : ""}.</>}>
        {years.length === 0 ? (noPeak && win.slug === "peak" ? <p className="text-sm text-muted" data-no-window="1">No peak is given for the Lower 48 (above): the table holds no row of it.</p> : <NoData what={TABLE} reason={`no ${win.mw} rows for ${grid.name}`} />) : (
          <GroupedBars id="demand-by-year" unit="MW" label={`${grid.name}: ${win.short} by year, MW`} series={[{ name: win.label, tone: "accent" }]}
            groups={years.map((y) => ({ label: String(y), values: [val(e, win.mw, y) ?? null], title: `${grid.name}, ${y}: ${Math.round(val(e, win.mw, y) ?? 0).toLocaleString("en-US")} MW` }))} />
        )}
      </ChartFrame>

      {years.length === 0 ? null : (
        <ToolSection title={`${grid.name}, year by year: ${win.short}`}
          note={win.slug === "avg" ? "Hours used: the hours of the year whose demand passed the method's test; a year is written when at least 95 percent of its hours are used." : win.slug === "ytd" ? "Hours used: the hours of the window whose demand passed the method's test." : undefined}>
          <ToolTable caption={`${grid.name}: ${win.short}, every year the table holds`} minWidth={360}
            head={["Year", "MW", ...(win.perYear ? [`Growth since ${BASE}, percent`] : []), ...(win.slug === "avg" ? ["On the year before, percent", "Hours used", "Hours in the year"] : []), ...(win.slug === "ytd" ? ["Hours used", "Hours in the window"] : [])]}
            rows={years.map((y) => ({
              key: String(y), highlight: y === latest,
              cells: [
                `${y}${win.latest === "newest" ? so(y) : ""}`,
                <span key="mw">{n(e, win.mw, y)}</span>,
                ...(win.perYear ? [y === BASE ? <span key="g" className="text-muted">base year</span> : <span key="g">{n(e, win.growth, y, true)}</span>] : []),
                ...(win.slug === "avg" ? [y === BASE ? <span key="o" className="text-muted">base year</span> : <span key="o">{n(e, "avg_demand_growth_yoy_pct", y, true)}</span>, <span key="u">{n(e, "hours_used", y)}</span>, <span key="h">{n(e, "hours_in_year", y)}</span>] : []),
                ...(win.slug === "ytd" ? [<span key="u">{n(e, "ytd_hours_used", y)}</span>, <span key="h">{n(e, "ytd_hours_in_window", y)}</span>] : []),
              ],
            }))} />
        </ToolSection>
      )}

      <p className="max-w-3xl text-sm" data-related-view="1">
        The same table is drawn on <Link href="/demand">Demand growth</Link>, with the map of where the growth sits by month and hour of the day
        and a ranking of the grids; this explorer reads any grid in any window of the year, every figure checked against the live set.
      </p>
    </>
  );
  return frame(body);
}
