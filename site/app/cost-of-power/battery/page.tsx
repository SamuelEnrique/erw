import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Source_Serif_4 } from "next/font/google";
import { AskErcotLink } from "@/components/AskErcotLink";
import type { ReactNode } from "react";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  CAPACITY_WORDS, COSTS, DEBT, DURATION_WORDS, LEFT_OUT, PRODUCTS, REVIEW_TABLE, STRATEGIES, TABLE, awardsBeside, debtPerMw, gridOf, inputsKey, inputsOf, last36,
  lastThreeYears, lastTwelve, monthName, monthsOf, outlier, stat, usdShort, years, type AwardsSnapshot, type Inputs, type Month, type Year,
} from "@/lib/batterystack";
import awardsData from "@/data/battery_awards_beside.json";
import stepsData from "@/data/battery_scenario_steps.json";
import { debtUsd, defaultsOf, isOldParam, isScenarioParam, parseScenarios, stepState, stepsOffered, type StepFile } from "@/lib/battery/finance";
import { attempt } from "@/lib/supabase";
import { CostTabs } from "../Tabs";
import { BatteryForm } from "./BatteryForm";
import { U, V } from "./nums";
import { internalView, reviewRows, rowsOf } from "./read";
import { BatteryDecisions, BatteryHeadline, BatterySensitivity, Scenarios } from "./Scenarios";
import "./brand.css";

// Session 203, branch wip/203-brand-battery (not on main): the page restyled on the brand, version 0 (docs/brand.md,
// direction A), for Samuel's review. The three families are loaded here, for this page alone, and every rule is in
// brand.css, scoped to the class brand-a on the page's wrapper. The year chart names its series on the chart (the
// legend's own three words) where it had a legend box.
const brandSerif = Source_Serif_4({ variable: "--font-brand-serif", subsets: ["latin"], weight: ["600"] });
const brandSans = IBM_Plex_Sans({ variable: "--font-brand-sans", subsets: ["latin"], weight: ["400", "500", "600"] });
const brandMono = IBM_Plex_Mono({ variable: "--font-brand-mono", subsets: ["latin"], weight: ["400", "500"] });

// Session 67: "What a battery earns". What a grid battery of the reader's size and duration earned from energy and
// from ancillary services together, split hour by hour so nothing is counted twice, and whether that covers its debt.
// Every number is computed by lib/batterystack.ts from the rows of battery_stack_monthly (warehouse/derived/
// battery_stack.py), read from Supabase, and carries a check key (bs|<inputs>|<stat>) that scripts/check-values.mjs
// recomputes from its own read. No capacity price is read: the capacity table is internal and is named nowhere here.
// Session 71: the page leads with the last twelve months (the summary sentence, the first headline number, the first
// column of the income table); the average of every year held follows, and beside it the same average without the one
// month that is more than a quarter of everything held (ERCOT's February 2021), which stays in every other figure and
// on the chart. Wording, order and layout only: no number changed.
// Session 86: NYISO and SPP are built and in review. A visitor sees them greyed, as before; with the internal cookie
// they open, and their rows come from data/battery_stack_review.json (battery_stack_review_monthly, held out of the
// live set so no live number moves), not from Supabase. ISO-NE and MISO are not built: their reserve prices are
// internal, and the page says "held, not shown: license needed".
// Session 178: one line under the income table sets the model's day-ahead ancillary revenue beside what ERCOT's storage
// resources were really awarded, from data/battery_awards_beside.json (warehouse/derived/battery_awards_compare.py; no
// new read of the live set, check keys bsa|<strategy>_<N>h|<stat>). The lead links the step-by-step note
// (docs/methods/battery_earns_algorithm.md) and the source line offers the default case hour by hour, with its do-file.
// Session 179: "Scenarios A and B" (Scenarios.tsx): assumptions with their cited defaults and Resets, two scenarios on
// the same seven rows, and a sensitivity chart, all computed in the browser from the months above
// (lib/battery/finance.ts). The two assumptions inside the model, efficiency and cycles a day, take the steps of
// data/battery_scenario_steps.json (warehouse/derived/battery_scenario_steps.py) and nothing between. Both scenarios
// live in the address (two-letter parameters, defaults omitted).
// Session 195: scenario A sets the headline. "Your battery" holds no fixed O&M and no annual debt payments of its own:
// the page's inputs take both from scenario A as the address has it (an older link's `fom` and `ds` are read as A's),
// and the summary sentence, the three headline numbers and each month's coverage follow A in the browser as it is
// changed. The last twelve months end with the last complete month in the table (lib/batterystack.ts, lastTwelve).
// Session 208 (the owner's rulings of 12 October 2026): one page, three questions, nothing folded. (1) "What did it
// earn?": the headline, the three numbers, the year chart and the income table, unchanged, with one sentence under the
// table (energy at the hub, not the battery's node; reserves paid and never called) and a CSV of every month.
// (2) "Is it worth building?": scenarios A and B, with the contract's share and price as scenario assumptions (0 by
// default, so the default is fully merchant) and the results table. (3) "What matters most": the NPV sensitivity chart
// with one line on how to read it. Gone from the page: the standalone contract panel and "With your contract"
// (Contract.tsx stays on disk, undrawn), the "Other grids" table (one line under the grid picker), and the folds
// "Every month" (the CSV), "Stress days" (the table battery_stack_stress_daily is public) and "What this model cannot
// see" (docs/methods/battery_earns_algorithm.md, section 4.11). The defaults: hurdle rate 12 percent and debt share 20
// percent, Lazard's storage cases (lib/battery/finance.ts). At a contract share of 0 every number that stays is what
// it was.
export const metadata: Metadata = { title: "What a battery earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/battery_stack";
const ALGORITHM = "/data/methods/battery_earns_algorithm";
const DISPATCH = "/battery/erw_2026_battery_dispatch.csv", DO_FILE = "/battery/erw_2026_battery_replication.do", MIRROR = "/battery/erw_2026_battery_replication.py";
const MONTHS_CSV = "/cost-of-power/battery/months.csv";
const STRESS_DOWNLOAD = "/api/download?table=battery_stack_stress_daily";
const shortMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
const ENERGY = "#8C1515", ANCILLARY = "#2E2D29";  // cardinal and Stanford black (app/tokens.css: accent and ink)

/** Revenue by year, USD per kW, stacked by stream. A year far above the others (2021 in ERCOT) is drawn to the top of
 * the scale with a break mark and its value written, so the other years stay readable; an incomplete year is hatched. */
function YearBars({ ys }: { ys: Year[] }) {
  const W = 760, H = 300, L = 54, R = 10, top = 26, bot = 44;
  const tot = ys.map((y) => (Math.max(0, y.energy) + Math.max(0, y.ancillary)) / 1000);
  const neg = Math.min(0, ...ys.map((y) => (Math.min(0, y.energy) + Math.min(0, y.ancillary)) / 1000));
  const sorted = [...tot].sort((a, b) => b - a);
  const broken = sorted.length > 2 && sorted[0] > 2.5 * sorted[1];
  const hi = (broken ? sorted[1] : sorted[0] ?? 1) * 1.15 || 1;
  const step = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000].find((s) => hi / s <= 5) ?? 2000;
  const ticks: number[] = [];
  for (let t = Math.ceil(neg / step) * step; t <= hi; t += step) ticks.push(t);
  const y = (v: number) => top + ((hi - v) / (hi - neg)) * (H - top - bot);
  const bw = (W - L - R) / ys.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Revenue by year, USD per kW, stacked: energy and ancillary services">
      <defs>
        <pattern id="hatch-e" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ENERGY} /></pattern>
        <pattern id="hatch-a" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ANCILLARY} /></pattern>
      </defs>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "#2E2D29" : "#D9D2C3"} strokeWidth={t === 0 ? 1 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="#6B665E">{t}</text>
        </g>
      ))}
      <text x={L - 46} y={14} fontSize="11" fill="#6B665E">USD per kW</text>
      {/* session 203 (docs/brand.md, section 6): the series are named on the chart, each in its own color; no legend box */}
      <g data-direct-labels="1">
        <text x={W - R - 252} y={14} textAnchor="end" fontSize="12" fill={ENERGY}>Energy</text>
        <text x={W - R - 122} y={14} textAnchor="end" fontSize="12" fill={ANCILLARY}>Ancillary services</text>
        <rect x={W - R - 108} y={5} width="10" height="10" fill="url(#hatch-a)" stroke={ANCILLARY} strokeWidth="0.75" />
        <text x={W - R} y={14} textAnchor="end" fontSize="12" fill="#6B665E">Incomplete year</text>
      </g>
      {ys.map((r, i) => {
        const e = r.energy / 1000, a = r.ancillary / 1000;
        const x0 = L + i * bw + bw * 0.18, w = bw * 0.64;
        const over = broken && tot[i] > hi;
        // positive parts stack upward from zero (energy first), negative parts downward
        const segs: { v0: number; v1: number; fill: string }[] = [];
        let up = 0, down = 0;
        for (const [v, solid, hatch] of [[e, ENERGY, "url(#hatch-e)"], [a, ANCILLARY, "url(#hatch-a)"]] as [number, string, string][]) {
          if (v >= 0) { segs.push({ v0: up, v1: up + v, fill: r.complete ? solid : hatch }); up += v; }
          else { segs.push({ v0: down + v, v1: down, fill: r.complete ? solid : hatch }); down += v; }
        }
        return (
          <g key={r.y}>
            {segs.map((s, k) => {
              const a1 = Math.min(s.v1, hi), a0 = Math.min(s.v0, hi);
              if (a1 === a0) return null;
              return <rect key={k} x={x0} width={w} y={y(a1)} height={Math.max(0.5, y(a0) - y(a1))} fill={s.fill} stroke={r.complete ? "none" : (k === 0 ? ENERGY : ANCILLARY)} strokeWidth={r.complete ? 0 : 0.75} />;
            })}
            {over ? <path d={`M${x0 - 3},${top + 14} l${w / 4 + 1.5},-5 l${w / 4},5 l${w / 4},-5 l${w / 4 + 1.5},5`} fill="none" stroke="#fff" strokeWidth="3" /> : null}
            <text x={x0 + w / 2} y={(over ? top : y(Math.min(up, hi))) - 6} textAnchor="middle" fontSize="11" fill="#2E2D29">{Math.round(e + a).toLocaleString("en-US")}</text>
            <text x={x0 + w / 2} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="#2E2D29">{r.y}</text>
            {!r.complete ? <text x={x0 + w / 2} y={H - bot + 30} textAnchor="middle" fontSize="10" fill="#6B665E">{r.months} months</text> : null}
            <title>{`${r.y}: energy ${Math.round(e).toLocaleString("en-US")}, ancillary ${Math.round(a).toLocaleString("en-US")} USD per kW${r.complete ? "" : ` (${r.months} months held)`}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

/** Session 208: a heading inside one of the three questions (the income table's). */
function Sub({ children }: { children: ReactNode }) {
  return <h3 className="mb-3 mt-2 border-t border-rule pt-3 font-serif text-lg">{children}</h3>;
}

export default async function Battery({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const internal = await internalView();
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const asked = inputsOf(q, internal);
  const g = gridOf(asked.grid);
  // a grid in review is read from the committed snapshot, never from Supabase
  const read = g.review ? { ok: true as const, data: reviewRows(asked.grid, asked) } : await attempt(() => rowsOf(g.entity!, asked));
  const rows = read.ok ? read.data : [];
  const ms: Month[] = monthsOf(rows, asked.strat, asked.dur);
  // session 195: scenario A, as the address has it, sets the page's fixed O&M and annual debt payments
  const steps = stepsData as unknown as StepFile;
  const stepCase = steps.cases[`${asked.grid}|${asked.strat}|${asked.dur}`] ?? null;
  const offered = stepsOffered(steps, stepState(stepCase, ms, (last36(ms)?.months ?? []).map((r) => r.m)));
  const A = parseScenarios(q, defaultsOf(COSTS[asked.dur]), offered, asked.mw).a;
  const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };
  const key = inputsKey(x);
  const held = ms.filter((r) => r.held);
  const st = (s: string) => stat(rows, [], x, s);
  const ys = years(ms);
  const l12 = lastTwelve(ms);
  const top = outlier(ms);
  const y3 = lastThreeYears(ms);
  const fullYears = ys.filter((r) => r.complete);
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const leftOut = ms.reduce((a, r) => a + r.daysOut, 0), leftAnc = ms.reduce((a, r) => a + r.daysOutAncillary, 0);
  const defaultDs = Math.round(debtPerMw(x.dur) * x.mw);
  const products = PRODUCTS[x.grid];
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([k, v]) => (isScenarioParam(k) || isOldParam(k)) && v !== undefined).sort(([a], [b]) => a.localeCompare(b))) as Record<string, string>;
  const beside = awardsBeside(awardsData as unknown as AwardsSnapshot, x.grid, x.strat, x.dur);
  const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const broken = (() => { const t = ys.map((r) => r.energy + r.ancillary).sort((a, b) => b - a); return t.length > 2 && t[0] > 2.5 * t[1] ? ys.find((r) => r.energy + r.ancillary === t[0])! : null; })();
  const before2024 = ys.some((r) => r.y < "2024");
  const topName = top ? `${monthName(top.m)}${top.m === "2021-02" ? " (Winter Storm Uri)" : ""}` : "";
  const strategyLine = x.strat === "foresight"
    ? "Perfect foresight: energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance. An upper bound, not a forecast."
    : "Day-ahead schedule: the battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading. It assumes its offers clear at the day-ahead price.";
  // the CSV of every month takes the page's own four parameters and scenario A's, as this request has them
  const monthsQuery = new URLSearchParams();
  for (const [k, v] of Object.entries(q)) if (v !== undefined && (["grid", "dur", "strat", "mw"].includes(k) || isScenarioParam(k) || isOldParam(k))) monthsQuery.set(k, v);
  const monthsHref = `${MONTHS_CSV}${monthsQuery.size ? `?${monthsQuery.toString()}` : ""}`;

  // data-no-usage: no usage count on this tool page (the owner's ruling of 11 October 2026; components/Usage.tsx). Until
  // session 208 the contract panel's promise "sent or stored" silenced the counter; the mark says it outright
  return (
    <div className={`brand-a ${brandSerif.variable} ${brandSans.variable} ${brandMono.variable}`} data-brand="a" data-no-usage="1">
    {/* the header and the footer are outside this wrapper: they take the text face by its name */}
    <style>{`body:has(.brand-a) > header, body:has(.brand-a) > footer { font-family: ${brandSans.style.fontFamily}, system-ui, sans-serif; }`}</style>
    <ToolPage>
      <ToolHeader
        title="What a battery earns"
        crumb={<CostTabs active="battery" />}
        lead={<>What a grid battery earned from energy and from ancillary services together, by year and by stream, whether that covers its debt, and whether it is worth building. The battery is split hour by hour between the two, so nothing is counted twice. <Link href={METHOD}>Method</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}
      />
      {/* session 92: drawn only in the internal view while /ask/ercot is in review (components/AskErcotLink.tsx) */}
      {x.grid === "ercot" ? <AskErcotLink context={{ view: "/cost-of-power/battery", title: "What a battery earns", settings: { grid: "ERCOT", duration: `${x.dur} hours`, strategy: `${STRATEGIES[x.strat]} (${x.strat})`, size: `${x.mw} MW` } }} /> : null}
      <BatteryDecisions key={`${x.grid}|${x.dur}|${x.strat}|${x.mw}|${JSON.stringify(scenarioParams)}`} ms={ms} mw={x.mw} costs={COSTS[x.dur]} stepCase={stepCase}
        stepMeta={{ built: steps.built, rte_steps: steps.rte_steps, cycle_steps: steps.cycle_steps }} initial={scenarioParams}>
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Your battery" note={<>Debt payments default to {DEBT.share * 100} percent of the capital cost borrowed at {DEBT.rate * 100} percent over {DEBT.life} years: USD {usdShort(defaultDs)} a year for {size}. Costs and the capital structure are Lazard&apos;s Levelized Cost of Energy+ (June 2025), its storage cases, scaled to the duration.</>}>
              <BatteryForm key={key} x={x} internal={internal} />
            </InputPanel>
          </aside>

          <div className="min-w-0">
            {g.review ? (
              <p className="mb-6 border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-in-review-grid={x.grid}>
                <strong>{g.name} is in review and shown in the internal view only.</strong> Its reserve prices came into the warehouse in session 85. {DURATION_WORDS[x.grid]} {LEFT_OUT[x.grid]}.
              </p>
            ) : null}
            {!read.ok ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
            ) : !held.length ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No month is held for this battery in {g.name}.</p>
            ) : (
              <>
                <div data-question="1">
                <ToolSection title="What did it earn?" id="earned">
                  {/* session 195: the summary sentence and the three headline numbers are scenario A's (Scenarios.tsx) */}
                  <BatteryHeadline ms={ms} x={x} gridName={g.name} gridFrom={g.from} />

                  <ChartFrame title="Revenue by year, USD per kW"
                    note={<>
                      <span className="mb-1.5 block text-sm text-ink" data-upper-bound="1">
                        {before2024
                          ? "This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read."
                          : `This is an upper bound: the battery is assumed to sell as much of its power as reserves as it likes at the posted price, and is never called. ${g.name} is held from ${g.from}, so every year here is a recent one.`}
                      </span>
                      {strategyLine} Per kW of rated power. A hatched year holds fewer than twelve months and is not a full year&apos;s revenue.
                      {broken ? <> {broken.y} is off the scale at <V pre={key} s={`year:${broken.y}:total`} v={st(`year:${broken.y}:total`)} /> USD per kW: Winter Storm Uri, when reserve prices stood near the cap for days.</> : null}</>}>
                    <YearBars ys={ys} />
                  </ChartFrame>

                  <Sub>Income by stream</Sub>
                  {(() => {
                    const cols: { head: string; sub: string; cell: (s: string) => ReactNode; kw: ReactNode }[] = [
                      { head: "Last twelve months, USD", sub: l12 ? `${shortMonth(l12[0].m)} to ${shortMonth(l12[11].m)}` : "not held",
                        cell: (s) => <U pre={key} s={`l12:${s}`} v={st(`l12:${s}`)} />, kw: <V pre={key} s="l12_kw:total" v={st("l12_kw:total")} /> },
                      { head: y3 ? `${y3[0]} to ${y3[2]}, a year, USD` : "Last three full years",
                        sub: y3 ? "the average of the last three full years" : `not held: ${g.name} holds ${fullYears.length === 0 ? "no full calendar year" : fullYears.length === 1 ? `one full year (${fullYears[0].y})` : `${fullYears.length} full years`}`,
                        cell: (s) => <U pre={key} s={`y3:${s}`} v={st(`y3:${s}`)} />, kw: <V pre={key} s="y3_kw:total" v={st("y3_kw:total")} /> },
                      { head: "Every year held, a year, USD", sub: `the average, ${shortMonth(held[0].m)} to ${shortMonth(held.at(-1)!.m)}`,
                        cell: (s) => <U pre={key} s={`avg:${s}`} v={st(`avg:${s}`)} />, kw: <V pre={key} s="avg_kw:total" v={st("avg_kw:total")} /> },
                      ...(top ? [{ head: `Without ${shortMonth(top.m)}, a year, USD`, sub: "the same average, without that one month",
                        cell: (s: string) => <U pre={key} s={`avg_without:${s}`} v={st(`avg_without:${s}`)} />, kw: <V pre={key} s="avg_without_kw:total" v={st("avg_without_kw:total")} /> }] : []),
                    ];
                    const line = (s: string) => cols.map((c, i) => <span key={i}>{c.cell(s)}</span>);
                    return (
                      <ToolTable caption="Income by stream" minWidth={top ? 640 : 560} head={["Stream", ...cols.map((c) => <>{c.head}<span className="mt-0.5 block text-xs opacity-80">{c.sub}</span></>)]}
                        rows={[
                          { key: "energy", cells: ["Energy (charge low, sell high)", ...line("energy")] },
                          { key: "anc", cells: ["Ancillary services", ...line("ancillary")] },
                          ...products.map((p) => ({ key: p.key, muted: true, cells: [<span key="n" className="pl-4">{p.label}</span>, ...line(p.key)] })),
                          { key: "cap", cells: ["Capacity"], wide: CAPACITY_WORDS[x.grid] },
                          { key: "total", highlight: true, cells: ["Total, split hour by hour with no double counting", ...line("total")] },
                          { key: "kw", cells: ["Total, USD per kW", ...cols.map((c, i) => <span key={i}>{c.kw}</span>)] },
                        ]} />
                    );
                  })()}
                  {beside ? (
                    <p className="mt-3 max-w-3xl text-sm" data-awards-beside={`${x.strat}_${x.dur}h`}>
                      Day-ahead ancillary services, {monthName(beside.first)} to {monthName(beside.last)}: this model takes USD <Num check={`bsa|${x.strat}_${x.dur}h|model`} raw={beside.model}>{two(beside.model)}</Num> per
                      kW a month; ERCOT&apos;s storage resources were awarded USD <Num check={`bsa|${x.strat}_${x.dur}h|fleet`} raw={beside.fleet}>{two(beside.fleet)}</Num> per kW of their power a month;
                      the model is <Num check={`bsa|${x.strat}_${x.dur}h|ratio`} raw={beside.ratio}>{two(beside.ratio)}</Num> times the awards. <Link href={ALGORITHM}>How this is counted</Link>.
                    </p>
                  ) : null}
                  {/* session 208 (ruling 2): one sentence of what the model cannot see; the rest is in the methods note */}
                  <p className="mt-2 max-w-3xl text-xs text-muted" data-income-note="1">
                    For {size}, in US dollars, one column for each span. Energy is priced at {g.name}&apos;s {g.at ?? `${g.hub} hub`}, not the battery&apos;s own node; reserves are paid for being held and are assumed never called.
                    {top ? <> {topName} alone is <V pre={key} s="top_share" v={st("top_share")} /> percent of everything this battery earned in the {held.length} months held; the last column is the same average without that one month.</> : null}
                    {" "}<Link href={`${ALGORITHM}#cannot-see`}>What else the model cannot see</Link>.
                  </p>
                  <p className="mt-2 max-w-3xl text-xs text-muted" data-months-csv="1">
                    <a href={monthsHref} download>Every month, CSV</a>: energy, ancillary and total for {size}, each month&apos;s coverage at scenario A&apos;s costs, days held and days left out
                    (<V pre={key} s="out" v={st("out")} /> days in all{leftOut ? `, ${leftAnc} of them for a missing ancillary price` : ""}).
                    {x.grid === "ercot" ? <> The stress days (Uri, Elliott, the 2023 heat): <a href={STRESS_DOWNLOAD} download>the table, CSV</a>.</> : null}
                  </p>
                </ToolSection>
                </div>

                <div data-question="2">
                <ToolSection title="Is it worth building?" id="scenarios">
                  <Scenarios x={x} costs={COSTS[x.dur]} gridName={g.name} stepMeta={{ built: steps.built, rte_steps: steps.rte_steps, cycle_steps: steps.cycle_steps }} />
                </ToolSection>
                </div>

                <div data-question="3">
                <ToolSection title="What matters most" id="matters">
                  <BatterySensitivity x={x} costs={COSTS[x.dur]} />
                </ToolSection>
                </div>
              </>
            )}
          </div>
        </div>
      </BatteryDecisions>
      <SourceLine tables={g.review
        ? [REVIEW_TABLE, "iso_hub_prices_history", ...(x.grid === "nyiso" ? ["nyiso_rtm_zone_prices", "nyiso_dam_zone_prices", "nyiso_as_prices"] : ["iso_rtm_hub_prices", "iso_dam_hub_prices", "spp_as_prices"])]
        : [TABLE, ...(x.grid === "ercot" ? ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_dam_hub_prices", "ercot_as_prices"] : ["iso_hub_prices_history", "iso_rtm_hub_prices", "iso_dam_hub_prices", "caiso_as_prices"])]}
        note={<>Derived by the ERW from {g.name}&apos;s public prices; {g.review ? "the first table is what this page reads, from the site's own copy of it" : "the first table is what this page reads"}. Cost defaults: Lazard, Levelized Cost of Energy+, June 2025. Solar, wind and gas peakers are on <Link href="/cost-of-power/seller">the seller tab</Link>. The default case hour by hour: <a href={DISPATCH} download>CSV</a>, with a <a href={DO_FILE} download>Stata do-file</a> and its <a href={MIRROR} download>Python mirror</a> that rebuild the headline numbers from it. <span data-checked-against="14">Checked against: 14 published figures (Lazard, the Annual Technology Baseline, CAISO&apos;s market monitor, ERCOT&apos;s awards, EIA, and five published ERCOT battery revenues). <Link href="/data/methods/battery_earns_algorithm#cross-checks">Each comparison, with its gap and the reason</Link>.</span></>} />
    </ToolPage>
    </div>
  );
}
