import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SourceLine, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import * as BS from "@/lib/batterystack";
import { MARKETS, latestPrices, newest, storageUnits } from "@/lib/data";
import { day, node, price, shown, utc } from "@/lib/format";
import { DOCS, digestChartDays, digestTitle, render, topItems } from "@/lib/markdown";
import { GROUPS } from "@/lib/pages";
import { HOURLY, required, rest } from "@/lib/supabase";
import findings from "@/data/findings/catalogue.json";
import markets from "@/data/markets.json";

// Session 300 (the owner's ruling of 18 October 2026, from mockup A: docs/brand/home-mockups/): the home page, top to
// bottom: the one line; a "right now" strip, the latest wholesale price per grid in USD per MWh with its hour (from
// latest_prices, the 15-minute table) and Henry Hub, WTI and Brent with their dates, each figure a link to /board and
// nothing else from the board; today's chart with its sentence (the Digest's chart of the day, docs/digest/charts/);
// the five top-level groups of the menu (Economics, Grid, Infrastructure, Analysis, Games), each with one line and one
// live number, not the sub-tools; the latest Digest, its first five stories. The page stays in review. Every figure is
// a Num with its table; a figure the live set lacks shows "no data", never a placeholder. The page takes the brand
// (components/Brand.tsx) as the tool pages do. What stood here (session 53's three audiences, the price cards with
// sparklines, "Gas and oil", "Open now", "In review" and the status strip) is in the session's report and in git.
// the latest prices refresh every 15 minutes; the rest of the page reads hourly data
export const revalidate = 900;
// Session 90: this page is never cached with a failed read in it. Every read below goes through lib/supabase.ts's
// `required`, not `attempt`: a read that fails throws, the render is thrown away, and the last good page stays until a
// later render reads everything. "no data" below is for what the tables do not hold (a grid with no row).

const n0 = (v: number) => Math.round(v).toLocaleString("en-US");
const n2 = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** One figure of the strip: the number (a Num, or "no data") and the line under it, the whole a link to the board. */
function Figure({ label, value, unit, when, sub }: { label: string; value: ReactNode; unit?: string; when: string; sub?: string }) {
  return (
    <Link href="/board" className="block bg-panel px-3 py-2 no-underline" gate="plain" data-home-figure={label}>
      <span className="block text-xs text-muted">{label}{sub ? <span className="font-mono"> {sub}</span> : null}</span>
      <span className="mt-0.5 block font-serif text-xl tabular-nums text-ink">{value}{unit ? <span className="ml-1 font-sans text-xs text-muted">{unit}</span> : null}</span>
      <span className="block text-xs text-muted">{when}</span>
    </Link>
  );
}

/** The "right now" strip: the newest real-time interval of each grid's main hub or zone, and the three fuels' newest spot closes. */
async function RightNow() {
  const latest = await required(latestPrices);
  const f = markets.fuels;
  const fuels = await Promise.all(f.entities.map(async (e) => ({ e, r: await required(() => newest(f.table, e.entity, f.variable)) })));
  return (
    <section className="mb-10" aria-label="Right now" data-home-now="1">
      <h2 className="mb-2 border-b border-rule pb-1 font-serif text-xl text-accent">Right now</h2>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
        {MARKETS.map((m) => {
          const p = latest.ok ? latest.data.find((r) => r.entity === m.main) : undefined;
          return (
            <Figure key={m.iso} label={m.iso} sub={node(m.main)}
              value={p ? <Num check={`latest_prices|${p.entity}|${p.variable}|${p.ts_utc}`} raw={p.value}>{price(p.value)}</Num> : <NoData reason={latest.ok ? `latest_prices has no row for ${m.main}` : latest.reason} />}
              unit={p ? p.unit : undefined} when={p ? `real time, the interval from ${utc(p.ts_utc)}` : "real time"} />
          );
        })}
        {fuels.map(({ e, r }) => (
          <Figure key={e.entity} label={e.label}
            value={r.ok && r.data ? <Num check={`series|${f.table}|${e.entity}|${f.variable}|newest`} raw={r.data.value}>{price(r.data.value)}</Num> : <NoData reason={r.ok ? `${f.table} has no row for ${e.entity}` : r.reason} />}
            unit={r.ok && r.data ? r.data.unit : undefined} when={r.ok && r.data ? `daily spot, ${day(r.data.ts_utc)}` : "daily spot"} />
        ))}
      </div>
      <p className="mt-1 text-xs text-muted">Each figure opens the <Link href="/board">price board</Link>, which holds every price with its moves. Prices as each ISO and EIA publish them.</p>
    </section>
  );
}

/** Today's chart: the Digest's chart of the day, the newest record and picture the chart-maker left (as /research draws it). */
function TodayChart() {
  const days = digestChartDays();
  const today = days.length ? (DOCS.digest_charts ?? {})[days[0]] : null;
  return (
    <ToolSection title="Today's chart" id="today">
      {today ? (
        <figure className="lead-chart" data-today-chart={today.date}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`/digest-charts/${today.image}`} alt={`${today.title}. ${today.fact}`} width={1600} height={900} />
          <figcaption>
            <p className="lead-date">{day(today.date)}</p>
            <h3>{today.title}</h3>
            <p className="lead-fact" data-today-fact="1">{today.fact}</p>
            <p className="lead-source text-xs text-muted" data-today-source="1">
              Source: {today.source ? <>{today.source}, </> : null}ERW table <code className="font-mono">{today.table}</code>. Drawn by code from the scanner&apos;s strongest flag of the day;{" "}
              <Link href="/research">today&apos;s and every day&apos;s chart</Link>.
            </p>
          </figcaption>
        </figure>
      ) : (
        <p className="text-sm text-muted" data-today-chart="none">No daily chart is held yet (docs/digest/charts/ is empty).</p>
      )}
    </ToolSection>
  );
}

/** The five groups' live numbers, each read here and checked by scripts/check-values.mjs under its key. */
async function groupNumbers() {
  const bx = BS.inputsOf({});
  const [demand, fleet, stack] = await Promise.all([
    required(() => newest("eia930_all_demand", "eia930:ERCO", "demand_mw")),
    required(storageUnits),
    required(() => rest<BS.Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${BS.TABLE}`, entity: `eq.${BS.gridOf(bx.grid).entity}`,
      variable: `like.${bx.strat}_${bx.dur}h_*`, order: "variable,ts_utc" }, HOURLY)),
  ]);
  const out: Record<string, { value: ReactNode; unit?: string; note: string; table: string }> = {};
  // Economics: the default battery (100 MW, 4 hours, ERCOT), the last twelve months per kW, as /cost-of-power/battery leads
  if (stack.ok) {
    const v = BS.stat(stack.data, [], bx, "l12_kw:total");
    const l12 = BS.lastTwelve(BS.monthsOf(stack.data, bx.strat, bx.dur));
    if (v !== null && l12) out.Economics = { value: <><span className="font-sans text-sm text-muted">USD </span><Num check={`bs|${BS.inputsKey(bx)}|l12_kw:total`} raw={v}>{n2(v)}</Num></>, unit: "per kW",
      note: `What a 100 MW, 4-hour battery in ERCOT earned, ${BS.monthName(l12[0].m)} to ${BS.monthName(l12[11].m)}.`, table: BS.TABLE };
  }
  // Grid: ERCOT's demand in the newest hour held
  if (demand.ok && demand.data) {
    const r = demand.data;
    out.Grid = { value: <Num check="series|eia930_all_demand|eia930:ERCO|demand_mw|newest" raw={r.value}>{n0(r.value)}</Num>, unit: "MW",
      note: `ERCOT's demand at ${r.ts_utc.slice(11, 16)} UTC on ${r.ts_utc.slice(0, 10)}, the newest hour held.`, table: "eia930_all_demand" };
  }
  // Infrastructure and Games: the batteries operating in the US, and in ERCOT (the fleet the game sets beside its own)
  if (fleet.ok) {
    const mw = (rows: typeof fleet.data) => Math.round(rows.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
    const op = fleet.data.filter((u) => u.status === "operating");
    out.Infrastructure = { value: <Num check="storage|mw|operating" raw={mw(op)}>{shown(mw(op))}</Num>, unit: "MW",
      note: "Batteries operating in the US, nameplate power, from EIA's monthly generator inventory.", table: "storage_capacity" };
    const tx = op.filter((u) => u.iso === "ERCOT");
    out.Games = { value: <Num check="storage|iso_mw|ERCOT|operating" raw={mw(tx)}>{shown(mw(tx))}</Num>, unit: "MW",
      note: "Batteries operating in ERCOT, the real fleet the battery game sets beside your own.", table: "storage_capacity" };
  }
  // Analysis: the findings in the library (site/data/findings/catalogue.json, checked by the value checker from the file)
  out.Analysis = { value: <Num check="findings|count" raw={findings.length}>{n0(findings.length)}</Num>, unit: "findings",
    note: "In the research library today, each run with the inputs you choose.", table: "findings catalogue" };
  return out;
}

/** The five top-level groups of the menu (lib/pages.ts), each with one line and one live number; the sub-tools are the menu's. */
const GROUP_LINES: Record<string, string> = {
  Economics: "What energy costs and earns: every price on one board, the cost of power, what a battery or a generator earns, and the tax on a barrel.",
  Grid: "The grid as it runs: one grid at a time, the network of balancing authorities and the power they trade, demand growth and curtailment.",
  Infrastructure: "What is built, where and by whom: the project map, the datacenter tracker, the battery fleet and the deals.",
  Analysis: "Research on demand, a warehouse you can ask, the events, policy and the Thesis Builder, every answer from the tables.",
  Games: "The battery game and the EV game, the tour, a bill built line by line, and five problem sets for a class.",
};
const HOME_GROUPS = ["Economics", "Grid", "Infrastructure", "Analysis", "Games"];

function Groups({ N }: { N: Awaited<ReturnType<typeof groupNumbers>> }) {
  const groups = HOME_GROUPS.map((label) => GROUPS.find((g) => g.label === label)!);
  return (
    <ToolSection title="The five groups" id="groups">
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5" data-home-groups={groups.length}>
        {groups.map((g) => {
          const n = N[g.label];
          return (
            <div key={g.label} className="flex flex-col border-t-2 border-accent pt-2" data-home-group={g.label}>
              <Link href={g.pages[0].href} className="font-serif text-lg">{g.label}</Link>
              <p className="mt-1 flex-1 text-sm leading-snug text-muted">{GROUP_LINES[g.label]}</p>
              <div className="mt-3 font-serif text-2xl tabular-nums text-ink">
                {n ? <>{n.value}{n.unit ? <span className="ml-1 font-sans text-xs text-muted">{n.unit}</span> : null}</> : <NoData reason="the table was read and holds no row for this figure" />}
              </div>
              {n ? <p className="mt-1 text-xs leading-snug text-muted">{n.note}</p> : null}
            </div>
          );
        })}
      </div>
    </ToolSection>
  );
}

/** The latest Digest: its title, its opening line and its first five stories (docs/digest/latest.md). */
function Digest() {
  const items = topItems(DOCS.latest, 5);
  const title = digestTitle(DOCS.latest).replace(/^(?:ERW's )?Energy Digest,\s*/, "");
  const opening = DOCS.latest.split("\n").map((s) => s.trim()).find((s) => s && !s.startsWith("#")) ?? "";
  return (
    <ToolSection title="ERW's Energy Digest" id="digest" note={<>The weekday brief of energy news, scored and ranked. <Link href="/digest">The full Digest of {title} and the archive</Link>; <Link href="/roundup">ERW&apos;s Roundup</Link> on Sundays.</>}>
      <p className="mb-3 text-sm text-muted" data-home-digest={title}>{opening}</p>
      {items && items.length ? (
        <ol className="prose-erw list-decimal pl-5" data-home-stories={items.length}>
          {items.map((md, i) => (
            <li key={i} dangerouslySetInnerHTML={{ __html: render(md, "docs/digest/latest.md") }} />
          ))}
        </ol>
      ) : (
        <NoData what="the digest" reason="docs/digest/latest.md has no 'Top of the industry' section" />
      )}
    </ToolSection>
  );
}

export default async function Home() {
  const N = await groupNumbers();
  const today = digestChartDays()[0];
  const chartTable = today ? (DOCS.digest_charts ?? {})[today]?.table : undefined;
  return (
    <Brand>
      <ToolPage>
        <div data-home="300">
          <ToolHeader crumb="Energy Research Warehouse" title="The live, citable record of the US energy system." />
          <RightNow />
          <TodayChart />
          <Groups N={N} />
          <Digest />
          <SourceLine tables={[...new Set(["latest_prices", markets.fuels.table, ...(chartTable ? [chartTable] : []), ...HOME_GROUPS.map((g) => N[g]?.table).filter((t): t is string => !!t && !t.includes(" "))])]}
            note={<>Every number on this page is read from the ERW&apos;s tables and checked against them; the findings are counted from the library&apos;s own catalogue. <Link href="/data">Data and methods</Link>.</>} />
        </div>
      </ToolPage>
    </Brand>
  );
}
