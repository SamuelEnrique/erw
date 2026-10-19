import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { AskErcotLink } from "@/components/AskErcotLink";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { SourceLine, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import {
  CAPACITY_WORDS, COSTS, DURATION_WORDS, LEFT_OUT, PRODUCTS, REVIEW_TABLE, STRATEGIES, STRESS_BY, TABLE, awardsBeside, debtPerMw, eventMonths, fleetBeside, fleetCase, gridOf, inputsKey, inputsOf, last36,
  monthName, monthsOf, outlier, stat, stress, typedNotes, years, type AwardsSnapshot, type Inputs, type Month,
} from "@/lib/batterystack";
import awardsData from "@/data/battery_awards_beside.json";
import stepsData from "@/data/battery_scenario_steps.json";
import { ATB, debtUsd, defaultsOf, isOldParam, isScenarioParam, parseScenarios, scenarioNotes, stepState, stepsOffered, type StepFile } from "@/lib/battery/finance";
import { parseView } from "@/lib/battery/view";
import { attempt } from "@/lib/supabase";
import { CostTabs } from "../Tabs";
import { Income } from "./Income";
import { V } from "./nums";
import { internalView, reviewRows, rowsOf, stressRowsOf } from "./read";
import { BatteryCharts, BatteryDecisions, BatteryHeadline, BatterySensitivity, Scenarios } from "./Scenarios";
import { Settings } from "./Settings";

// Session 203: the page restyled on the brand, version 0 (docs/brand.md, direction A). The year chart names its series
// on the chart (the legend's own three words) where it had a legend box.
// Session 235 (the brand approved, 12 October 2026): the three families and the wrapper are components/Brand.tsx and
// every rule is in app/tokens.css; until then this page loaded the families itself and its rules were in brand.css.

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
// Session 257 (the owner's task of 13 October 2026, session 246's list): CAISO at ERCOT's depth on this page. (a) The
// sentence of the stress days names the events of the grid shown, read from battery_stack_stress_daily (read.ts,
// stressRowsOf): ERCOT's three by their names, as before, and CAISO's by their days, since a rule makes them from
// CAISO's own notices. (b) Under the income table CAISO has the line that ERCOT's awards line is for ERCOT: the model's
// 2025 energy and regulation income for a 4-hour battery on the day-ahead schedule (computed from
// battery_stack_monthly, check keys bs|<that case>|year_kw:2025:<streams>) beside what CAISO's market monitor says the
// real fleet earned (a cited constant, lib/batterystack.ts, FLEET_BESIDE). No ERCOT number moved.
// Session 296 (the owner's ten rulings of 15 October 2026, the page's pass 1): the left box is "Assumptions", five
// sections that open and close (Settings.tsx): the battery and the units, the headline figures (up to six of eight),
// the charts (up to three of four, at a linear, log or adjusted scale), the financing (the twelve assumptions of the
// scenario in view, the contract as a sub-group, moved here from the second question) and the sensitivity (a sourced
// range or a percent step, in NPV or IRR). The income table's columns are the calendar years, the last twelve months
// and one window the reader sets with year pickers, leaving out the grid's stress events by a checkbox each
// (Income.tsx): no window is the ERW's. Every grey note that explained is a hover tip; every chart and the income table
// have a Chart | Table toggle; the 8-hour defaults are NREL's Annual Technology Baseline 2025 (lib/batterystack.ts,
// COSTS). The three questions, their order and every figure at the defaults are unchanged, except the 8-hour page's
// cost figures and the sensitivity chart, which item 7 and item 8 move. The reader's view lives in the address with
// the scenarios (lib/battery/view.ts; nothing is requested).
export const metadata: Metadata = { title: "What a battery earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/battery_stack";
const MONITOR = `${METHOD}#caiso-market-monitor`;
const ALGORITHM = "/data/methods/battery_earns_algorithm";
const DISPATCH = "/battery/erw_2026_battery_dispatch.csv", DO_FILE = "/battery/erw_2026_battery_replication.do", MIRROR = "/battery/erw_2026_battery_replication.py";
const MONTHS_CSV = "/cost-of-power/battery/months.csv";
const STRESS_DOWNLOAD = "/api/download?table=battery_stack_stress_daily";

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
  // session 296: the reader's view, as the address has it
  const view = parseView(q);
  // session 263: what the address asked for and the page does not show as asked is said, in one line, never replaced in silence
  const asItWas = [...typedNotes(q, asked), ...scenarioNotes(q, defaultsOf(COSTS[asked.dur]), offered)];
  const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };
  const key = inputsKey(x);
  const held = ms.filter((r) => r.held);
  const st = (s: string) => stat(rows, [], x, s);
  const ys = years(ms);
  const top = outlier(ms);
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const leftOut = ms.reduce((a, r) => a + r.daysOut, 0), leftAnc = ms.reduce((a, r) => a + r.daysOutAncillary, 0);
  const defaultDs = Math.round(debtPerMw(x.dur) * x.mw);
  const products = PRODUCTS[x.grid];
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([k, v]) => (isScenarioParam(k) || isOldParam(k)) && v !== undefined).sort(([a], [b]) => a.localeCompare(b))) as Record<string, string>;
  const beside = awardsBeside(awardsData as unknown as AwardsSnapshot, x.grid, x.strat, x.dur);
  // session 257: the events of the grid shown, from the stress table's rows (a grid in review holds none and is not asked)
  const stressRead = g.review || !read.ok ? null : await attempt(() => stressRowsOf(g.entity!, asked));
  const events = stressRead?.ok ? stress(stressRead.data, x.strat, x.dur) : [];
  // session 296: each event's revenue by month, for the income table's "leave out" boxes
  const em = stressRead?.ok ? eventMonths(stressRead.data, x.strat, x.dur) : {};
  // session 297: the grid's peak stress event, by its window's revenue, for the stress repeats (USD per kW)
  const peakEvent = events.length ? events.reduce((a, e) => (e.total > a.total ? e : a)) : null;
  const peak = peakEvent ? { kw: peakEvent.total / 1000, label: peakEvent.label } : null;
  // session 257: the published real-fleet figures beside the model's own case (CAISO: a 4-hour battery, day-ahead, 2025).
  // The case's months are the page's own rows when it is the battery shown, else one more read of the same table
  const fleet = g.review || !read.ok ? null : fleetBeside(x.grid);
  const fleetX = fleet ? fleetCase(fleet, x.grid, x.mw) : null;
  const fleetRead = !fleet ? null : fleet.strat === asked.strat && fleet.dur === asked.dur ? { ok: true as const, data: rows } : await attempt(() => rowsOf(g.entity!, fleet));
  const fleetRows = fleetRead?.ok ? fleetRead.data : [];
  const fleetKey = fleetX ? inputsKey(fleetX) : "";
  const fleetStat = (s: string) => (fleetX ? stat(fleetRows, [], fleetX, s) : null);
  const fleetEnergy = fleet ? fleetStat(`year_kw:${fleet.year}:energy`) : null, fleetReg = fleet ? fleetStat(`year_kw:${fleet.year}:${fleet.regulationStreams}`) : null;
  const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const broken = (() => { const t = ys.map((r) => r.energy + r.ancillary).sort((a, b) => b - a); return t.length > 2 && t[0] > 2.5 * t[1] ? ys.find((r) => r.energy + r.ancillary === t[0])! : null; })();
  const before2024 = ys.some((r) => r.y < "2024");
  // the year chart's first line (session 296: in its hover tip, handed to the chart from here)
  const upper = before2024
    ? "This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read."
    : `This is an upper bound: the battery is assumed to sell as much of its power as reserves as it likes at the posted price, and is never called. ${g.name} is held from ${g.from}, so every year here is a recent one.`;
  const topName = top ? `${monthName(top.m)}${top.m === "2021-02" ? " (Winter Storm Uri)" : ""}` : "";
  const strategyLine = x.strat === "foresight"
    ? "Perfect foresight: energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance. An upper bound, not a forecast."
    : "Day-ahead schedule: the battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading. It assumes its offers clear at the day-ahead price.";
  // the CSV of every month takes the page's own four parameters and scenario A's, as this request has them
  const monthsQuery = new URLSearchParams();
  for (const [k, v] of Object.entries(q)) if (v !== undefined && (["grid", "dur", "strat", "mw"].includes(k) || isScenarioParam(k) || isOldParam(k))) monthsQuery.set(k, v);
  const monthsHref = `${MONTHS_CSV}${monthsQuery.size ? `?${monthsQuery.toString()}` : ""}`;
  const stepMeta = { built: steps.built, rte_steps: steps.rte_steps, cycle_steps: steps.cycle_steps };
  const costs = COSTS[x.dur];

  // data-no-usage: no usage count on this tool page (the owner's ruling of 11 October 2026; components/Usage.tsx). Until
  // session 208 the contract panel's promise "sent or stored" silenced the counter; the mark says it outright
  return (
    <Brand noUsage>
    <ToolPage>
      <ToolHeader
        title="What a battery earns"
        crumb={<CostTabs active="battery" />}
        lead={<>What a grid battery earned from energy and from ancillary services together, by year and by stream, whether that covers its debt, and whether it is worth building. The battery is split hour by hour between the two, so nothing is counted twice. <Link href={METHOD}>Method</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}
      />
      {/* session 92: drawn only in the internal view while /ask/ercot is in review (components/AskErcotLink.tsx) */}
      {x.grid === "ercot" ? <AskErcotLink context={{ view: "/cost-of-power/battery", title: "What a battery earns", settings: { grid: "ERCOT", duration: `${x.dur} hours`, strategy: `${STRATEGIES[x.strat]} (${x.strat})`, size: `${x.mw} MW` } }} /> : null}
      <BatteryDecisions key={`${x.grid}|${x.dur}|${x.strat}|${x.mw}|${JSON.stringify(scenarioParams)}`} ms={ms} mw={x.mw} costs={costs} stepCase={stepCase}
        stepMeta={stepMeta} initial={scenarioParams} view={view} peak={peak} hours={x.dur}>
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            {/* session 296: the box "Assumptions", five sections (Settings.tsx) */}
            <Settings x={x} internal={internal} gridName={g.name} costs={costs} defaultDs={defaultDs} stepMeta={stepMeta} />
          </aside>

          <div className="min-w-0">
            {asItWas.length ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-typed-notes={asItWas.length}>{asItWas.join(" ")}</p>
            ) : null}
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
                  {/* session 195: the summary sentence and the headline numbers are scenario A's (Scenarios.tsx) */}
                  <BatteryHeadline ms={ms} x={x} gridName={g.name} gridFrom={g.from} />

                  {/* session 296: the charts the reader picked; by default the year chart alone, as before */}
                  <BatteryCharts ms={ms} x={x} ys={ys} upper={upper} strategyLine={strategyLine}
                    brokenNote={broken ? <> {broken.y} is off the scale at <V pre={key} s={`year:${broken.y}:total`} v={st(`year:${broken.y}:total`)} /> USD per kW: Winter Storm Uri, when reserve prices stood near the cap for days.</> : null} />

                  <Income ms={ms} x={x} pre={key} gridName={g.name} products={products} capacityWords={CAPACITY_WORDS[x.grid]} em={em}
                    events={events.map((e) => ({ event: e.event, short: e.short, label: e.label }))} />
                  {beside ? (
                    <p className="mt-3 max-w-3xl text-sm" data-awards-beside={`${x.strat}_${x.dur}h`}>
                      Day-ahead ancillary services, {monthName(beside.first)} to {monthName(beside.last)}: this model takes USD <Num check={`bsa|${x.strat}_${x.dur}h|model`} raw={beside.model}>{two(beside.model)}</Num> per
                      kW a month; ERCOT&apos;s storage resources were awarded USD <Num check={`bsa|${x.strat}_${x.dur}h|fleet`} raw={beside.fleet}>{two(beside.fleet)}</Num> per kW of their power a month;
                      the model is <Num check={`bsa|${x.strat}_${x.dur}h|ratio`} raw={beside.ratio}>{two(beside.ratio)}</Num> times the awards. <Link href={ALGORITHM}>How this is counted</Link>.
                    </p>
                  ) : null}
                  {/* session 257: for CAISO, the market monitor's real fleet plays the part of ERCOT's awards line */}
                  {fleet && fleetEnergy !== null && fleetReg !== null ? (
                    <p className="mt-3 max-w-3xl text-sm" data-fleet-beside={`${x.grid}_${fleet.year}`}>
                      In {fleet.year}, for a {fleet.dur}-hour battery on the day-ahead schedule, this model takes USD <V pre={fleetKey} s={`year_kw:${fleet.year}:energy`} v={fleetEnergy} /> per
                      kW from energy and USD <V pre={fleetKey} s={`year_kw:${fleet.year}:${fleet.regulationStreams}`} v={fleetReg} /> from regulation; {g.name}&apos;s market monitor reports that real batteries in its area
                      with a full year of operation earned about USD <span data-fleet-published="energy">{fleet.energy}</span> per kW from energy and USD <span data-fleet-published="regulation">{fleet.regulation}</span> from regulation
                      ({fleet.publisher}, <a href={fleet.url} rel="noopener">{fleet.report}</a>, {fleet.where}). <span data-fleet-why="1">The two differ in regulation: this model sells it as if the market had no size, and the monitor writes that &ldquo;there is a large amount of battery capacity competing to provide a relatively low amount of required regulation&rdquo;.</span> <Link href={MONITOR}>How this is counted</Link>.
                    </p>
                  ) : null}
                  {/* session 208 (ruling 2): one sentence of what the model cannot see; the rest is in the methods note.
                      Session 296: kept in view, not a hover tip, for its checked number and its link */}
                  <p className="mt-2 max-w-3xl text-xs text-muted" data-income-note="1">
                    Energy is priced at {g.name}&apos;s {g.at ?? `${g.hub} hub`}, not the battery&apos;s own node; reserves are paid for being held and are assumed never called.
                    {top ? <> {topName} alone is <V pre={key} s="top_share" v={st("top_share")} /> percent of everything this battery earned in the {held.length} months held; leave it out of your window to see the average without it.</> : null}
                    {" "}<Link href={`${ALGORITHM}#cannot-see`}>What else the model cannot see</Link>.
                  </p>
                  <p className="mt-2 max-w-3xl text-xs text-muted" data-months-csv="1">
                    <a href={monthsHref} download>Every month, CSV</a>: energy, ancillary and total for {size}, each month&apos;s coverage at scenario A&apos;s costs, days held and days left out
                    (<V pre={key} s="out" v={st("out")} /> days in all{leftOut ? `, ${leftAnc} of them for a missing ancillary price` : ""}).
                    {/* session 257: the events of the grid shown, read from the table: ERCOT's by name, CAISO's by their days */}
                    {events.length ? <span data-stress-days={events.map((e) => e.event).join(" ")}> The stress days{STRESS_BY[x.grid] ? `, ${STRESS_BY[x.grid]}` : ""} ({events.map((e) => e.short).join(", ")}): <a href={STRESS_DOWNLOAD} download>the table, CSV</a>.</span>
                      : stressRead && !stressRead.ok ? <span data-stress-days=""> The stress days: <a href={STRESS_DOWNLOAD} download>the table, CSV</a>.</span> : null}
                  </p>
                </ToolSection>
                </div>

                <div data-question="2">
                <ToolSection title="Is it worth building?" id="scenarios">
                  <Scenarios x={x} />
                </ToolSection>
                </div>

                <div data-question="3">
                <ToolSection title="What matters most" id="matters">
                  <BatterySensitivity x={x} />
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
        note={<>Derived by the ERW from {g.name}&apos;s public prices; {g.review ? "the first table is what this page reads, from the site's own copy of it" : "the first table is what this page reads"}. Cost defaults: Lazard, Levelized Cost of Energy+, June 2025, at 2 and 4 hours; at 8 hours <a href={ATB.url} rel="noopener">NREL&apos;s Annual Technology Baseline 2025</a> (session 296). Solar, wind and gas peakers are on <Link href="/cost-of-power/seller">the seller tab</Link>. The default case hour by hour: <a href={DISPATCH} download>CSV</a>, with a <a href={DO_FILE} download>Stata do-file</a> and its <a href={MIRROR} download>Python mirror</a> that rebuild the headline numbers from it. <span data-checked-against="15">Checked against: 15 published figures (Lazard, the Annual Technology Baseline, CAISO&apos;s market monitor, ERCOT&apos;s awards, EIA, and five published ERCOT battery revenues). <Link href="/data/methods/battery_earns_algorithm#cross-checks">Each comparison, with its gap and the reason</Link>.</span></>} />
    </ToolPage>
    </Brand>
  );
}
