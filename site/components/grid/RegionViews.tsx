// Energy Research Warehouse (ERW) site, session 8602 (chain 504, 19 November 2026): the whole country in the Grid
// tool. EIA's thirteen regions of the lower 48 beside the seven grids of the picker, each with the tool's four tabs,
// drawn on the server from the whole country's page files (data/regions/, the data machine's; the contract is
// docs/state/page_files_regions.md; lib/regionsdata.ts reads them, lib/gridregions.ts is the arithmetic).
//
// - RegionPicker   the thirteen under the grid picker. Until the index is on the server the row says so and no region
//                  can be chosen; the tool is then exactly as it was.
// - RegionMixView  the Mix tab for a region, in the form the tab has for a grid: the latest hour held, the last days
//                  hour by hour, the average day of any month or year, the shares by source, one calendar month year
//                  after year. A part of the grid's tab the region's file does not hold (a price, a forecast, the
//                  records) is drawn blank with its reason on hover, not hidden.
// - RegionTradeView  under the Gravity tab: the power the region exchanged with each neighbour, by month, from both
//                  sides' reports (the Exchange view's blocks for a grid).
// - RegionAuthorities, RegionCleanView  the Network and Clean tabs' own lines for a region.
// Real data only: every figure is one the region's file holds; a figure it does not hold is the short placeholder.
import type { ReactNode } from "react";
import { Lines } from "@/components/mix/Charts";
import { Missing } from "@/components/mix/Now";
import { Chips } from "@/components/mix/views";
import { SiteLink as Link } from "@/components/SiteLink";
import { CategoryChart } from "@/components/svgchart";
import { ToolPicker } from "@/components/tool/Choose";
import { SourceLine } from "@/components/tool/ToolPage";
import { ALIKE, MIX_SOURCES, NEW_REGIONS, lastHours, latestHour, monthsOf, neighborName, newestTradeMonth, regionHref, tradeMonth, whySentence,
  type Alike, type IndexRegion, type RegionCode, type RegionIndex, type RegionMix, type RegionTrade, type RegionView } from "@/lib/gridregions";
import * as mix from "@/lib/mix2";
import { HOURS, n0, n1 } from "@/lib/mixpage";

const file = (kind: string, code: string) => `site/data/regions/${kind}/${code.toLowerCase()}.json`;
const NH = ({ why, words = "not held for this region" }: { why: string; words?: string }) => <Missing why={why} words={words} />;
const utc = (t: string) => `${t.slice(0, 13).replace("T", " ")}:00 UTC`;
const local = (t: string, tz: string) => new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(t));
const signed = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${n0(Math.abs(v))}`;

function Block({ title, children, id }: { title: ReactNode; children: ReactNode; id?: string }) {
  return <section id={id} className="mb-8"><h2 className="mb-2 border-b border-accent pb-0.5 font-serif text-lg text-accent">{title}</h2>{children}</section>;
}
function Table({ head, rows, caption, name }: { head: ReactNode[]; rows: { key: string; cells: ReactNode[]; on?: boolean }[]; caption: string; name: string }) {
  return (
    <div className="overflow-x-auto" data-region-table={name}>
      <table className="w-full border-collapse text-sm tabular-nums">
        <caption className="sr-only">{caption}</caption>
        <thead><tr className="border-b border-rule text-xs text-muted">{head.map((h, i) => <th key={i} className={`py-1 pr-3 font-normal ${i ? "text-right" : "text-left"}`}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((r) => <tr key={r.key} className={`border-b border-rule/60 ${r.on ? "bg-paper" : ""}`}>{r.cells.map((c, i) => (i ? <td key={i} className="py-1 pr-3 text-right">{c}</td> : <th key={i} scope="row" className="py-1 pr-3 text-left font-normal">{c}</th>))}</tr>)}</tbody>
      </table>
    </div>
  );
}
/** A column head with its rule on hover (the page standard: an explanation is a hover, never grey text). */
const Head = ({ children, tip }: { children: ReactNode; tip: string }) => <span title={tip} className="cursor-help border-b border-dotted border-muted">{children}</span>;

// ------------------------------------------------------------------ the picker
/** What a region's hover says: its code, the balancing authorities EIA places in it, which of the seven grids are among
 * them, and, where a grid covers nearly its ground, the data machine's own sentence on why the two differ. */
export function regionTitle(r: IndexRegion, alike: Alike | null): string {
  const grids = r.grids.length ? ` Of the seven grids, among them: ${r.grids.join(", ")}.` : " None of the seven grids is among them.";
  const why = alike ? ` Beside ${ALIKE[r.code as RegionCode]?.grid ?? alike.grid}: ${whySentence(alike)}` : "";
  return `${r.name} (${r.code}), a region of EIA's hourly grid monitor: ${r.bas.length} balancing authorit${r.bas.length === 1 ? "y" : "ies"} (${r.bas.join(", ")}).${grids}${why}`;
}

export function RegionPicker({ index, on, view, alike }: { index: RegionIndex | null; on: string | null; view: RegionView; alike: Record<string, Alike | null> }) {
  if (!index) {
    return (
      <p className="mb-4 flex flex-wrap items-center gap-1 text-sm" data-region-picker="absent">
        <span className="mr-2 text-xs text-muted">EIA region</span>
        <NH words="not built yet" why="EIA's thirteen regions of the lower 48 (California, Carolinas, Central, Florida, Mid-Atlantic, Midwest, New England, Northwest, New York, Southeast, Southwest, Tennessee, Texas) are read from site/data/regions/index.json, which the data machine writes from Form EIA-930. The file is not on the site yet, so no region can be chosen. The seven grids and the Lower 48 above are as they were." />
      </p>
    );
  }
  return (
    <div data-region-picker={index.regions.length} data-region-on={on ?? ""}>
      <ToolPicker label="EIA region" items={index.regions.map((r) => ({ key: r.code.toLowerCase(), label: r.name, href: regionHref(r.code, view), on: r.code === on, title: regionTitle(r, alike[r.code] ?? null) }))} />
    </div>
  );
}

// ------------------------------------------------------------------ the Mix tab for a region
/** The parts of a grid's Mix tab that a region's file does not hold: each is drawn, blank, with its reason. */
const NOT_HELD: [string, string][] = [
  ["Hub price beside the mix", "A region's file holds generation by source, demand, net generation and net imports. It holds no price: a hub price belongs to a market, and an EIA region is a sum of balancing authorities."],
  ["Wind and solar forecasts against actual", "EIA-930's regions carry no wind or solar forecast; the seven grids' forecasts come from each operator's own data."],
  ["Records: the highest and lowest hours", "The region's file carries no table of records. The hours of its last 35 days are above; the seven grids' records come from generation_mix_records."],
  ["How hard the system works", "The stress measures of the seven grids (grid_stress_yearly) are not computed for a region."],
  ["Availability by source", "Capacity and availability by source are held for the seven grids only."],
  ["Carbon intensity, temperature beside the mix", "No carbon intensity and no temperature profile is in the region's mix file; the Clean tab says what is held."],
  ["By state, and since 2001", "The opening view's table by state and EIA's record since 2001 are kept by state, not by region."],
];

export function RegionMixView({ region, mixFile, period, cal }: { region: IndexRegion; mixFile: RegionMix | null; period: string | null; cal: string | null }) {
  const code = region.code;
  if (!mixFile) {
    return (
      <div data-region-view="mix" data-region-mix="absent">
        <Block title={`${region.name}: generation by source`}>
          <p className="text-sm"><NH words="not built yet" why={`This tab reads ${file("mix", code)} (generation by source for the region: by month, by year and for its newest 35 days by hour), which the data machine writes from Form EIA-930. The file is not on the site yet, so no figure is drawn here.`} /></p>
        </Block>
      </div>
    );
  }
  const months = monthsOf(mixFile), years = Object.keys(mixFile.years).sort().reverse();
  const asked = period && (mixFile.months[period] || mixFile.years[period]) ? period : mixFile.months[mixFile.upto] ? mixFile.upto : months[0];
  const p = mix.periodOf(mixFile as unknown as mix.GridFile, asked);
  const calAsked = cal && /^(0[1-9]|1[0-2])$/.test(cal) ? cal : asked && asked.length === 7 ? asked.slice(5) : (months[0] ?? "").slice(5);
  const now = latestHour(mixFile);
  const hours = lastHours(mixFile, 35);
  const label = (key: string) => mix.sourceOf(key)?.label ?? key;
  const color = (key: string) => mix.sourceOf(key)?.color ?? "var(--color-muted)";
  const href = (more: Record<string, string | undefined>) => `${regionHref(code, "mix", { period: asked && asked !== mixFile.upto ? asked : undefined, cal: cal ?? undefined, ...more })}`;
  const across = calAsked ? mix.acrossYears(mixFile as unknown as mix.GridFile, calAsked) : [];
  const tables = mixFile.tables?.length ? mixFile.tables : ["eia930_region_fuel_hourly"];
  return (
    <div data-region-view="mix" data-region-mix={code} data-region-period={asked ?? ""}>
      {/* the latest hour held: what the Now blocks are for a grid */}
      <Block title="The latest hour held" id="now">
        {now ? (
          <div data-region-now={now.ts}>
            <p className="mb-2 text-sm">{utc(now.ts)} ({local(now.ts, mixFile.tz)} in {region.name}, <span title={`The region's days and local hours are counted in ${mixFile.tz}, the time zone of most of its demand.`} className="cursor-help border-b border-dotted border-muted">{mixFile.tz}</span>).</p>
            <dl className="mb-3 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
              {([["Demand", now.demand, "The sum of the demand of the region's balancing authorities that file demand, written for an hour only when every one of them holds it."],
                ["Net generation", now.net_generation, "The sum of the eight sources in the hour."],
                ["Net imports", now.net_imports, "EIA's total interchange with its sign turned: positive when the region imports, negative when it exports."]] as const).map(([name, v, tip]) => (
                <div key={name} className="border border-rule bg-paper p-2">
                  <dt className="text-xs"><Head tip={tip}>{name}</Head></dt>
                  <dd className="font-mono text-lg tabular-nums" data-region-figure={name}>{v === null ? <NH words="not held" why={`${name} is not held for ${region.name} in this hour.`} /> : <>{name === "Net imports" ? signed(v) : n0(v)} <span className="text-xs">MW</span></>}</dd>
                </div>
              ))}
            </dl>
            <Table name="now" caption={`Generation by source in ${region.name}, ${utc(now.ts)}`} head={["Source", "MW", <Head key="s" tip="The source's megawatts over the hour's net generation, the sum of the eight sources.">Share of net generation</Head>]}
              rows={now.sources.map((s) => ({ key: s.key, cells: [<span key="n"><span className="mr-1.5 inline-block h-2.5 w-2.5" style={{ background: color(s.key) }} />{label(s.key)}</span>,
                s.mw === null ? <NH key="m" words="not held" why={`${label(s.key)} is not held for ${region.name} in this hour.`} /> : n0(s.mw), s.share_pct === null ? "" : `${n1(s.share_pct)}%`] }))} />
          </div>
        ) : <p className="text-sm"><NH why={`The region's file (${file("mix", code)}) carries no hourly part, or no hour of it holds a net generation.`} /></p>}
      </Block>
      {/* the last days hour by hour */}
      <Block title={hours ? `Generation by source, hour by hour: the last ${Math.round(hours.x.length / 24)} days` : "Generation by source, hour by hour"} id="hours">
        {hours ? (
          <div data-chart="stack" data-region-hours={hours.x.length}>
            <CategoryChart id={`erw-region-hours-${code}`} x={hours.x} unit="MW" label={`${region.name}, generation by source by hour, UTC`} height={320} every={24 * 14}
              series={[...mix.SOURCES.filter((s) => (MIX_SOURCES as readonly string[]).includes(s.key) && hours.get(s.key).some((v) => v !== null)).map((s) => ({ name: s.label, color: s.color, values: hours.get(s.key), kind: "area" as const, stack: "mix" })),
                ...(hours.get("demand").some((v) => v !== null) ? [{ name: "Demand", color: "var(--color-ink)", values: hours.get("demand"), kind: "line" as const, width: 1.6 }] : [])]} />
          </div>
        ) : <p className="text-sm"><NH why={`The region's file (${file("mix", code)}) carries no hourly part.`} /></p>}
      </Block>
      {/* the average day of a month or a year */}
      <Block title={`Generation by source, by hour: the average day of ${asked ? mix.periodName(asked) : ""}`} id="day">
        <div className="mb-2 space-y-1">
          <Chips label="Month" items={months.slice(0, 13).map((m) => ({ key: m, label: mix.periodName(m), href: href({ period: m === mixFile.upto ? undefined : m }), on: m === asked }))} />
          <Chips label="Year" items={years.map((y) => ({ key: y, label: y, href: href({ period: y }), on: y === asked }))} />
        </div>
        {p ? (
          <div data-chart="stack">
            <CategoryChart id={`erw-region-day-${code}-${asked}`} x={HOURS} unit="MW" label={`${region.name}, ${asked ? mix.periodName(asked) : ""}, local hour`} height={300}
              series={[...mix.sourcesIn(p).map((s) => ({ name: s.label, color: s.color, values: p.avg[s.key] ?? [], kind: "area" as const, stack: "mix" })),
                ...(p.avg.demand ? [{ name: "Demand", color: "var(--color-ink)", values: p.avg.demand, kind: "line" as const, width: 2 }] : [])]} />
          </div>
        ) : <p className="text-sm"><NH words="not held" why={`${region.name} holds no ${asked ? mix.periodName(asked) : "such period"}: a month is written when at least 90 percent of its days are complete.`} /></p>}
      </Block>
      <Block title={`Shares of generation by source, ${asked ? mix.periodName(asked) : ""}`} id="shares">
        {p ? (
          <Table name="shares" caption={`Shares of generation by source, ${region.name}`} head={["Source", <Head key="s" tip="The source's energy over the period's net generation.">Share</Head>, "MWh"]}
            rows={[...mix.shares(p).filter((s) => p[`${s.key}_mwh`] !== undefined).map((s) => ({ key: s.key, cells: [<span key="n"><span className="mr-1.5 inline-block h-2.5 w-2.5" style={{ background: s.color }} />{s.label}</span>, `${n1(s.share)}%`, n0(s.mwh)] })),
              { key: "all", on: true, cells: ["Net generation", "", typeof p.net_generation_mwh === "number" ? n0(p.net_generation_mwh) : <NH key="g" words="not held" why="The period carries no total." />] }]} />
        ) : <p className="text-sm"><NH words="not held" why={`${region.name} holds no ${asked ? mix.periodName(asked) : "such period"}.`} /></p>}
        {p ? <p className="mt-1 text-sm">{n0(p.days_held)} days held{typeof p.days_in_month === "number" ? <> of {p.days_in_month}</> : null}.</p> : null}
      </Block>
      {/* one calendar month across the years */}
      <Block title={`Year after year: net load by hour in ${calAsked ? mix.calName(calAsked) : ""}`} id="years">
        <div className="mb-2"><Chips label="Calendar month" items={Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, "0")).map((m) => ({ key: m, label: mix.calName(m).slice(0, 3), href: href({ cal: m }), on: m === calAsked }))} /></div>
        {across.length ? (
          <>
            <Lines x={HOURS} unit="MW" name={`erw-region-years-${code}-${calAsked}`} label={`${region.name}, net load by hour in ${mix.calName(calAsked)}, each year`}
              series={across.map((y, i) => ({ name: y.year, color: i === across.length - 1 ? "var(--color-accent)" : "var(--color-muted)", values: y.net, width: i === across.length - 1 ? 2.2 : 1 }))} />
            <Table name="years" caption={`${region.name}: ${mix.calName(calAsked)} across the years`}
              head={["Year", <Head key="l" tip="The lowest hour of net load (demand less wind and solar) from 09:00 to 16:00.">Midday low, MW</Head>, "Hour", <Head key="e" tip="The highest hour of net load from 16:00.">Evening high, MW</Head>, "Hour", <Head key="r" tip="The evening high less the midday low.">Ramp, MW</Head>, "Days held"]}
              rows={across.map((y) => ({ key: y.year, cells: [y.year, y.low ? n0(y.low.value) : <NH key="l" words="not held" why="Demand, wind or solar is not held for every hour of this month." />, y.low ? mix.hourName(y.low.hour) : "", y.evening ? n0(y.evening.value) : "", y.evening ? mix.hourName(y.evening.hour) : "", y.ramp === null ? "" : n0(y.ramp), n0(y.days)] }))} />
          </>
        ) : <p className="text-sm"><NH words="not held" why={`${region.name} holds no ${calAsked ? mix.calName(calAsked) : "month"} in any year.`} /></p>}
      </Block>
      {/* the parts of a grid's tab a region's file does not hold: drawn blank, each with its reason */}
      <Block title="The rest of the Mix tab" id="rest">
        <Table name="rest" caption={`Parts of the Mix tab not held for ${region.name}`} head={["Part of the tab, as a grid has it", region.name]}
          rows={NOT_HELD.map(([part, why]) => ({ key: part, cells: [part, <NH key="w" why={`${why} (${file("mix", code)})`} />] }))} />
      </Block>
      <SourceLine tables={tables} note={<>Form EIA-930, public domain (EIA). Built {mixFile.built.slice(0, 16).replace("T", " ")} UTC; {mixFile.first} to {mixFile.upto}. Method: <code className="font-mono">{mixFile.method ?? "docs/methods/regions_pages.md"}</code>.</>} />
    </div>
  );
}

// ------------------------------------------------------------------ the Gravity tab for a region: its trade
const LINE_COLORS = ["var(--color-accent)", "var(--color-fuel-gas)", "var(--color-fuel-nuclear)", "var(--color-fuel-wind)", "var(--color-fuel-solar)", "var(--color-fuel-hydro)", "var(--color-fuel-coal)", "var(--color-muted)"];

export function RegionTradeView({ region, trade, month }: { region: IndexRegion; trade: RegionTrade | null; month: string | null }) {
  const code = region.code;
  if (!trade) {
    return (
      <div data-region-view="trade" data-region-trade="absent">
        <Block title={`${region.name}: power exchanged with its neighbours`}>
          <p className="text-sm"><NH words="not built yet" why={`This tab reads ${file("trade", code)} (the region's net imports from each neighbour by month, from both sides' reports), which the data machine writes from Form EIA-930. The file is not on the site yet, so no figure is drawn here.`} /></p>
        </Block>
      </div>
    );
  }
  const newest = newestTradeMonth(trade);
  const asked = month && trade.months.includes(month) ? month : newest;
  const m = asked ? tradeMonth(trade, asked) : null;
  const last = trade.months.slice(-36);
  const codes = Object.keys(trade.neighbors).sort();
  const cut = (v: (number | null)[]) => v.slice(-36).map((x) => (x === undefined ? null : x));
  const mwh = (v: number | null, what: string) => (v === null ? <NH words="not held" why={what} /> : signed(v));
  return (
    <div data-region-view="trade" data-region-trade={code} data-region-month={asked ?? ""}>
      <Block title={`${region.name}: power exchanged with each neighbour, ${asked ? mix.periodName(asked) : ""}`} id="trade">
        <div className="mb-2"><Chips label="Month" items={trade.months.slice(-13).reverse().map((x) => ({ key: x, label: mix.periodName(x), href: regionHref(code, "gravity", { month: x === newest ? undefined : x }), on: x === asked }))} /></div>
        {m ? (
          <Table name="trade" caption={`Net imports of ${region.name} from each neighbour, ${asked}`}
            head={["Neighbour", <Head key="o" tip={`Net imports from the neighbour over the month as ${region.name}'s own balancing authorities reported them, MWh: positive when the region imported, negative when it exported.`}>Net imports, own report, MWh</Head>,
              <Head key="t" tip="The same flow as the neighbour's balancing authorities reported it, with the same sign.">The neighbour&apos;s report, MWh</Head>,
              <Head key="g" tip="The region's own report less the neighbour's, over the hours both reported. Two sides of one tie need not agree.">Gap, MWh</Head>,
              <Head key="h" tip="The hours of the month each side reported, and the hours both did.">Hours: own, theirs, both</Head>]}
            rows={[...m.rows.map((r) => ({ key: r.code, cells: [<span key="n">{neighborName(r.code)} <span className="font-mono text-xs">{r.code}</span></span>, mwh(r.own, `${region.name} reported nothing about ${neighborName(r.code)} in this month.`), mwh(r.theirs, `${neighborName(r.code)} reported nothing about ${region.name} in this month.`),
              mwh(r.gap, "No hour of the month was reported by both sides."), `${r.hoursOwn === null ? "" : n0(r.hoursOwn)}, ${r.hoursTheir === null ? "" : n0(r.hoursTheir)}, ${r.hoursBoth === null ? "" : n0(r.hoursBoth)}`] })),
              { key: "all", on: true, cells: ["All neighbours", mwh(m.total, "A month's total is written only when every neighbour's own report holds at least half the month's hours."), "", "", ""] }]} />
        ) : <p className="text-sm"><NH words="not held" why="No month of the file holds a report." /></p>}
        <p className="mt-1 text-sm">EIA&apos;s months are Eastern months.</p>
      </Block>
      <Block title={`Net imports from each neighbour by month, ${last[0] ?? ""} to ${last[last.length - 1] ?? ""}`} id="trade-months">
        <Lines x={last} unit="MWh" zero every={6} name={`erw-region-trade-${code}`} label={`${region.name}, net imports from each neighbour by month, own report`}
          series={[...codes.map((c, i) => ({ name: neighborName(c), color: LINE_COLORS[(i + 1) % LINE_COLORS.length], values: cut(trade.neighbors[c].net_imports_mwh), width: 1.2 })),
            { name: "All neighbours", color: "var(--color-ink)", values: cut(trade.net_imports_mwh), width: 2.2 }]} />
      </Block>
      <SourceLine tables={trade.tables?.length ? trade.tables : ["eia930_region_pair_hourly"]} note={<>Form EIA-930, public domain (EIA). Built {trade.built.slice(0, 16).replace("T", " ")} UTC. Method: <code className="font-mono">{trade.method || "docs/methods/regions_pages.md"}</code>.</>} />
    </div>
  );
}

// ------------------------------------------------------------------ the Network and Clean tabs for a region
/** The balancing authorities EIA places in the region, each a link that opens its panel in the network under it. */
export function RegionAuthorities({ region, index, node }: { region: IndexRegion; index: RegionIndex; node: string | null }) {
  const by = new Map(index.bas.map((b) => [b.code, b]));
  return (
    <div className="mb-4 border border-rule bg-paper p-3 text-sm" data-region-authorities={region.bas.length}>
      <p className="mb-1">{region.name} is {region.bas.length} balancing authorit{region.bas.length === 1 ? "y" : "ies"} of the network below. Choose one to open its panel:</p>
      <ul className="flex flex-wrap gap-x-4 gap-y-1">
        {region.bas.map((code) => {
          const b = by.get(code);
          const tip = b ? `${b.name} (${code})${b.generation_only ? ": it files generation and no demand" : ""}${b.retired ? `; retired ${b.retired}` : ""}${b.grid ? "; one of the seven grids" : ""}.` : code;
          return <li key={code}><Link href={regionHref(region.code, "network", { node: code })} title={tip} aria-current={node === code ? "true" : undefined} className={node === code ? "font-semibold" : ""} data-region-ba={code}>{b?.name ?? code}</Link> <span className="font-mono text-xs">{code}</span></li>;
        })}
      </ul>
    </div>
  );
}

export function RegionCleanView({ region }: { region: IndexRegion }) {
  return (
    <div data-region-view="clean">
      <Block title={`${region.name}: carbon intensity of generation`}>
        <Table name="clean" caption={`The Clean tab for ${region.name}`} head={["Part of the tab, as a grid has it", region.name]}
          rows={[["CO2 per MWh, now and by month since 2018", "The warehouse computes the carbon intensity of generation for the seven grids' balancing authorities (carbon_intensity_hourly, carbon_intensity_monthly). No table holds it for an EIA region."],
            ["How clean each hour is", "The clean-energy summary (clean_energy_summary) is by grid, not by region."],
            ["Emissions by source", "EIA-930's emissions by source are held for the seven grids only."]].map(([part, why]) => ({ key: part, cells: [part, <NH key="w" why={why} />] }))} />
        <p className="mt-2 text-sm">The region&apos;s generation by source, which a carbon intensity is computed from, is on the <Link href={regionHref(region.code, "mix")}>Mix tab</Link>.</p>
      </Block>
    </div>
  );
}

/** Whether no page of the site drew the region before the whole country's files (the picker's hover and the header say so). */
export const isNewRegion = (code: string) => (NEW_REGIONS as readonly string[]).includes(code);
