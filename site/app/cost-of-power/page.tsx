import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { ASSUMED, hrefOf, loadWords, monthName, two, usdShort, whole, type Inputs } from "@/lib/datacenter";
import { KINDS, KIND_LABELS, deliveryStat, slugOf, type UtilityDelivery } from "@/lib/datacenter/delivery";
import { held as heldWays } from "@/lib/datacenter/finance";
import { DELIVERY, INDEX, type MatrixRow } from "@/lib/datacenterdata";
import { shown } from "@/lib/format";
import { GridsView } from "./GridsView";
import { YearCost } from "./LoadCharts";
import { LoadForm } from "./LoadForm";
import { HowClean, HowSoon, PowerThere } from "./LoadAnswers";
import { GpuHourOfA, LoadHeadline } from "./LoadHeadline";
import { LoadDecisions, LoadScenarios, LoadSensitivity } from "./LoadScenarios";
import { LoadSiteB } from "./LoadSiteB";
import { FORESEEN, FORESEEN_WHY, NY_SHOWN, NYLOAD, day, inputsFrom, loadModel } from "./model";
import { CostTabs } from "./Tabs";

// Session 138: "What a datacenter pays", the mirror of /cost-of-power/battery for a buyer. A load the reader describes
// (grid, region, size, how it runs, how it buys) and four questions: what it will cost, whether the power is there, how
// clean it is, how soon it can be had. The cost is computed here, on the server, by lib/datacenter.ts from the site's
// own files of hourly hub and zone prices (data/datacenter, warehouse/derived/datacenter_page.py); the contract is
// computed in the browser and never sent. The other three questions show headline numbers of the mix, demand and queue
// tools, read from those tools' own files, and link to them: nothing of theirs is rebuilt here. What the tab showed
// before session 138 is the view "Grid by grid" (GridsView.tsx). The page face carries no method: a figure that is
// missing is a short placeholder with its reason on hover, and the rest is in the Method note
// (docs/methods/datacenter_cost.md).
//
// Session 213 (the owner's chain prompt of 12 October 2026): the battery page's layout, one page on three questions,
// nothing folded. (1) "What will it pay?": the summary sentence, the three headline numbers, the cost chart by year
// and the cost table "What will it cost" (its rows as they were, the delivery rows among them), one sentence of what
// the model cannot see, the links to the grid's own tools, and the two CSV downloads. (2) "Which option is better?":
// scenarios A and B, with the contract's share of the energy and its price as two of their assumptions (0 by default,
// so the default is fully merchant) and the results table with B set against A. (3) "What matters most": the
// sensitivity chart with one line on how to read it. Gone from the page, into the CSV downloads: the three grid
// questions "Will the power be there", "How clean" and "How soon" with the waits by stage and the rules in motion, the
// folds (every year, every month, the transmission matrix, every region) and New York's load in line. Gone outright:
// the standalone contract panel and "With your contract" (LoadContract.tsx stays on disk, undrawn). What the page
// computes is model.ts, shared with the downloads; the three cells the grid questions drew are grid-cells.tsx, undrawn.
// The defaults stay (hurdle rate 9.6). At a contract share of 0 every number is what it was.
//
// Session 228: the page's four questions are four sections again, each computed for the load: what will it pay, will
// the power be there, how clean, how soon (LoadAnswers.tsx), before the two of the decisions.
//
// Session 236 (the owner's chain prompt of 12 October 2026): the page takes the brand (components/Brand.tsx; every rule
// in app/tokens.css; no color, font or spacing of its own: the legend and the view switch name tokens, the chart reads
// them at its box). It serves a buyer of power: the four questions stay, in their order, and scenarios A and B compare
// two sites or two contracts (B may stand at a site of its own, `bsite` in the address; the contract's share and price
// are two of each scenario's assumptions). The scarcity level stays USD 1,000 per MWh for every grid, stated beside
// the count, with each grid's own signal as a second count where a table is held. Texas's delivery charges are one
// row a component in USD per MWh, with their total (lib/datacenter/delivery.ts); the tariff's own lines are in
// tables.csv. No default and no number at the default changed.
export const metadata: Metadata = { title: "What a datacenter pays" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/datacenter_cost";
// Session 190: every number of the page, step by step, is docs/methods/datacenter_pays_algorithm.md, and the source line
// offers the default case hour by hour as CSV with its Stata do-file and Python mirror (site/public/datacenter, written
// by warehouse/derived/datacenter_hourly_export.py from this page's own files). No number of the page changed.
const ALGORITHM = "/data/methods/datacenter_pays_algorithm";
// Session 194: the decisions. One more section after "With your contract", "Scenarios A and B" (LoadScenarios.tsx on
// lib/datacenter/finance.ts): eight assumptions with their defaults and Resets, two scenarios on the same rows, B set
// against A, and a sensitivity chart, all computed in the browser from the two ways of running this function hands over
// (the load run flat, and run flexible, over the same last twelve months). No number above it changed.
const HOURLY_CSV = "/datacenter/erw_2026_datacenter_hourly.csv", DO_FILE = "/datacenter/erw_2026_datacenter_replication.do", MIRROR = "/datacenter/erw_2026_datacenter_replication.py";
const MONTHS_CSV = "/cost-of-power/months.csv", TABLES_CSV = "/cost-of-power/tables.csv";

/** A short placeholder with its reason on hover. */
function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
/** A figure or a label with its explanation on hover. */
function Hover({ why, children }: { why: string; children: ReactNode }) {
  return <span className="cursor-help border-b border-dotted border-muted" title={why}>{children}</span>;
}
const usd = (v: number | null, why: string) => (v === null ? <Missing why={why} /> : <>USD {usdShort(v)}</>);
const perMwh = (v: number | null, why: string) => (v === null ? <Missing why={why} /> : <>{two(v)}</>);
/** Session 213: a heading inside one of the three questions (the cost table's). */
function Sub({ children }: { children: ReactNode }) {
  return <h3 className="mb-3 mt-2 border-t border-rule pt-3 font-serif text-lg">{children}</h3>;
}

function ViewNav({ x }: { x: Inputs }) {
  const item = (view: "load" | "grids", label: string) => (
    <Link href={hrefOf(x, { view })} scroll={false} aria-current={x.view === view ? "page" : undefined} data-view={view} style={{ color: x.view === view ? "var(--color-surface)" : "var(--color-ink)" }}
      className={`border px-2 py-1 no-underline ${x.view === view ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{label}</Link>
  );
  return <nav aria-label="Views" className="mb-6 flex flex-wrap gap-1 text-xs" data-views="1">{item("load", "Your load")}{item("grids", "Grid by grid")}</nav>;
}

export default async function CostOfPower({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const x = inputsFrom(q);
  return (
    <Brand noUsage>
    <ToolPage>
      <ToolHeader
        title="What a datacenter pays"
        crumb={<CostTabs active="buy" />}
        lead={<>What a buyer of power pays at a site, whether the power is there when it is needed, how clean it is and how soon it can be had, each computed for a load you describe; then two sites or two contracts side by side, and what moves the figure most. <Link href={METHOD}>Method note</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}
      />
      <ViewNav x={x} />
      {x.view === "grids" ? <GridsView /> : <LoadView asked={x} buyGiven={typeof sp.buy === "string"} gridAsked={typeof sp.grid === "string" ? sp.grid : undefined} q={q} />}
    </ToolPage>
    </Brand>
  );
}

async function LoadView({ asked, buyGiven, gridAsked, q }: { asked: Inputs; buyGiven: boolean; gridAsked?: string; q: Record<string, string | undefined> }) {
  const M = await loadModel(asked, buyGiven, gridAsked, q);
  const { x, g, failed, side, flex, off, s12, sh12, ysH, rule, bad, badPer, ys, place, market, noYear, savedH, saved, ref12, l12Span, size, facts, scenarioParams, matrix, utilities, deliveryParts } = M;
  const region = M.region;
  // session 236: the three answers at scenario B's own site, when it has one
  const siteB = M.bSite && M.answerFactsB ? { a: M.answersB?.ok ? M.answersB.data : null, f: M.answerFactsB, reason: M.answersB && !M.answersB.ok ? M.answersB.reason : null } : null;
  // the two downloads take the page's own parameters and the scenarios', as this request has them
  const query = new URLSearchParams();
  for (const [n, v] of Object.entries(q)) if (v !== undefined && n !== "view") query.set(n, v);
  const suffix = query.size ? `?${query.toString()}` : "";

  return (
     <LoadDecisions key={`${hrefOf(x)}|${JSON.stringify(scenarioParams)}`} load={facts.load} open={heldWays(facts.ways)} initial={scenarioParams}>
      {/* data-no-usage: no usage count on this tool page (the owner's ruling of 11 October 2026; components/Usage.tsx). Until
          session 213 the contract panel's promise "sent or stored" silenced the counter; the mark says it outright, as the
          battery page's does since session 208 */}
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]" data-no-usage="1">
        <aside>
          <InputPanel title="Your load">
            <LoadForm key={hrefOf(x)} x={x} grids={M.grids} blank={INDEX.blank} />
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {failed ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The price files could not be read, so no number is shown: {failed}</p>
          ) : !side ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">{x.region}: <Missing why={`No ${market} price is held for ${place}.`} /></p>
          ) : (
            <>
              <div data-question="1">
              <ToolSection title="What will it pay?" id="pays">
                <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                  {s12 && s12.per !== null ? (
                    <>{loadWords(x)} at {place}, buying {market}, paid USD <span data-stat="l12_per">{two(s12.per)}</span> per MWh over the last twelve months,
                      USD <span data-stat="l12_cost">{usdShort(s12.cost * x.mw)}</span> in all{flex && saved !== null ? <>, USD <span data-stat="l12_saved">{two(saved)}</span> per MWh less than a flat load{savedH !== null ? <> (<Hover why={FORESEEN_WHY}>USD <span data-stat="l12_saved_foreseen">{two(savedH)}</span> {FORESEEN}</Hover>)</> : null}</> : null}: USD <span data-stat="gpu_hour"><GpuHourOfA per={s12.per} /></span> per GPU-hour for power alone.</>
                  ) : (
                    <>{loadWords(x)} at {place}, buying {market}: last twelve months <Missing why={noYear} />.</>
                  )}
                </p>

                {/* session 195: the three headline numbers are scenario A's rows (LoadScenarios.tsx) */}
                <LoadHeadline facts={facts} missing={<Missing why={noYear} />}
                  foreseen={flex && sh12?.per != null ? <> <Hover why={FORESEEN_WHY}><span data-stat="l12_per_foreseen">USD {two(sh12.per)}</span> {FORESEEN}</Hover>.</> : null} />

                <ChartFrame title={`Cost by year, USD per MWh, ${x.region}, ${market}`}
                  legend={flex ? [{ label: "Flat load", color: "var(--color-muted)" }, { label: "This load", color: "var(--color-accent)" }, { label: "If perfectly foreseen", color: "var(--color-ink)" }, { label: "Incomplete year", color: "var(--color-accent)", hatch: true }] : [{ label: "Flat load", color: "var(--color-accent)" }, { label: "Incomplete year", color: "var(--color-accent)", hatch: true }]}>
                  <YearCost rows={ys.map((r) => ({ y: r.y, flat: r.flat, per: r.per, complete: r.complete, months: r.months, down: r.down, foreseen: flex ? ysH.find((h) => h.y === r.y)?.per ?? null : null }))} flex={flex} off={off}
                    label={`Cost of power by year at ${place}, ${market}, USD per MWh${flex ? ": a flat load and this load" : ""}`} />
                </ChartFrame>

                <Sub>What will it cost</Sub>
                <ToolTable caption="What will it cost" minWidth={620} head={["", "USD per MWh", `USD, ${size}`, ""]}
                  rows={[
                    { key: "flat", cells: ["Market energy, a flat load, last twelve months", perMwh(s12?.flat ?? null, noYear), usd(s12 ? s12.flatCost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{l12Span ?? ""}</span>] },
                    ...(flex ? [
                      { key: "load", highlight: true, cells: [<Hover key="h" why={rule}>Market energy, this load, last twelve months</Hover>, perMwh(s12?.per ?? null, noYear), usd(s12 ? s12.cost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{s12 ? `${whole(s12.energy * x.mw)} MWh` : ""}</span>] },
                      { key: "saved", cells: [<Hover key="h" why={rule}>What the flexibility saves</Hover>, perMwh(saved, noYear), usd(s12 ? (s12.flatCost - s12.cost) * x.mw : null, noYear),
                        <span key="n" className="text-xs text-muted">{s12 ? (x.run === "shift" ? "the same energy, moved within each day" : `off in ${whole(s12.down)} hours; ${whole((s12.held - s12.energy) * x.mw)} MWh not bought`) : ""}</span>] },
                      { key: "foreseen", cells: [<Hover key="h" why={FORESEEN_WHY}>This load, {FORESEEN}</Hover>, <span key="p" data-foreseen="per">{perMwh(sh12?.per ?? null, noYear)}</span>, usd(sh12 ? sh12.cost * x.mw : null, noYear),
                        <span key="n" className="text-xs text-muted">{savedH !== null ? `would have saved ${two(savedH)} per MWh${saved !== null && savedH > 0 ? `; the rule kept ${whole((100 * saved) / savedH)} percent of it` : ""}` : ""}</span>] },
                    ] : []),
                    ...(region?.ref ? [{ key: "ref", cells: [<>The hub beside it, {region.ref}, a flat load</>, <span key="p" data-ref-hub="1">{perMwh(ref12?.flat ?? null, `Twelve complete months of ${market} prices are not held for ${region.ref} over the same months.`)}</span>, usd(ref12 ? ref12.flatCost * x.mw : null, noYear),
                      <span key="n" className="text-xs text-muted">{ref12?.flat != null && s12?.flat != null ? `the load zone is ${two(Math.abs(s12.flat - ref12.flat))} per MWh ${s12.flat >= ref12.flat ? "above" : "below"} its hub` : ""}</span>] }] : []),
                    { key: "bad", cells: ["A bad month", perMwh(badPer, noYear), usd(bad ? bad.cost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{bad ? monthName(bad.m) : ""}</span>] },
                    { key: "gpu", cells: ["Power per GPU-hour", s12?.per != null ? <GpuHourOfA key="g" per={s12.per} /> : <Missing key="m" why={noYear} />, "", <span key="n" className="text-xs text-muted">USD per GPU-hour, not per MWh</span>] },
                    ...(x.grid === "ercot"
                      ? (utilities.length || DELIVERY.withheld.length
                        ? [...DELIVERY.withheld.map((w) => ({ key: `d-${w.utility}`, cells: [<>Delivery and transmission, {w.utility}</>], wide: <Missing words={w.words} why={w.why} /> })),
                          { key: "matrix", cells: ["Wholesale transmission, all of ERCOT"], wide: matrix.length ? <MatrixCell rows={matrix} /> : <Missing why="The Commission's transmission charge matrices are not in this page's files yet." /> }]
                        : [{ key: "delivery", cells: ["Delivery and transmission charges"], wide: <Missing why="The four large Texas wires utilities' tariff charges are not in this page's files yet." /> }])
                      : [{ key: "delivery", cells: ["Delivery charges"], wide: <Missing why={`The delivery and transmission tariffs of ${g.name}'s utilities are not in the warehouse. Texas's four large wires utilities are.`} /> }]),
                  ]} />
                {/* session 236: Texas's delivery charges, one row a component in USD per MWh, and the total; the tariff's own
                    lines (the schedule names, the rates as filed) are in the download */}
                {x.grid === "ercot" && deliveryParts.length ? <DeliveryTable parts={deliveryParts} mw={x.mw} size={size} href={`${TABLES_CSV}${suffix}`} /> : null}
                {/* session 213: one sentence of what the model cannot see; the rest is in the methods note */}
                <p className="mt-2 max-w-3xl text-xs text-muted" data-income-note="1">
                  Market energy at {x.region}&apos;s {market} price, for {size}: no delivery, transmission, capacity or ancillary charge is added to it (Texas&apos;s delivery charges stand in their own table below, never added), the load buys every hour at the hour&apos;s price with no hedge, and a flexible load follows a rule decided before each hour, not the year&apos;s prices.
                  {" "}<Link href={`${ALGORITHM}#cannot-see`}>What else the model cannot see</Link>.
                </p>
                <p className="mt-2 max-w-3xl text-xs text-muted" data-grid-links="1">
                  The grid&apos;s own figures, on their pages: <Link href={`/demand?area=${x.grid}`}>demand growth</Link>, <Link href={`/mix?view=stress&grid=${x.grid}`}>how hard the grid works</Link>, <Link href={`/mix?view=clean&grid=${x.grid}`}>how clean, and when</Link>, <Link href={`/queues?grid=${x.grid}&tech=all`}>interconnection queues</Link>, <Link href="/datacenters">the datacenter tracker</Link>.
                </p>
                <p className="mt-2 max-w-3xl text-xs text-muted" data-months-csv="1">
                  <a href={`${MONTHS_CSV}${suffix}`} download>Every month, CSV</a>: a flat load&apos;s price, this load&apos;s, the foreseen price, the hours off and the cost for {size}, each month and each year held, and the hours at or above the scarcity level and the grid&apos;s carbon intensity in each.
                  {" "}<a href={`${TABLES_CSV}${suffix}`} download>The other tables, CSV</a>: the three answers below (the scarce hours by month and clock hour, the carbon by way and by year, the large load reports), the grid&apos;s own figures as the page drew them until session 213 (the queue, the large load, how long a large load waits by stage, the rules in motion), every region of {g.name} over its own last twelve months, {x.grid === "ercot" ? "Texas's delivery tariffs line by line as filed, " : ""}the Commission&apos;s transmission charge matrix{x.grid === "nyiso" && NY_SHOWN ? `, and New York's load in line, request by request (${whole(NYLOAD.total.requests)})` : ""}.
                </p>
              </ToolSection>
              </div>

              {/* session 228: the three answers beside "What will it pay?", computed for this load from the live set and the
                  page's own files (lib/datacenter/answers.ts); each number carries its check key */}
              <div data-question="power">
              <ToolSection title="Will the power be there?" id="there">
                {M.answers?.ok ? <PowerThere a={M.answers.data} f={M.answerFacts} b={siteB} /> : <p className="max-w-3xl text-sm" role="status" data-answer="power" data-answer-none="1">{M.answers ? `The live set could not be read, so no figure is shown: ${M.answers.reason}` : `Twelve complete months are not held for ${x.region}, so the hours short in them cannot be counted.`}</p>}
              </ToolSection>
              </div>
              <div data-question="clean">
              <ToolSection title="How clean?" id="clean">
                {M.answers?.ok ? <HowClean a={M.answers.data} f={M.answerFacts} b={siteB} /> : <p className="max-w-3xl text-sm" role="status" data-answer="clean" data-answer-none="1">{M.answers ? `The live set could not be read, so no figure is shown: ${M.answers.reason}` : `Twelve complete months are not held for ${x.region}, so the load's carbon over them cannot be counted.`}</p>}
              </ToolSection>
              </div>
              <div data-question="soon">
              <ToolSection title="How soon?" id="soon">
                {M.answers?.ok ? <HowSoon a={M.answers.data} f={M.answerFacts} rules={M.rules} b={siteB} /> : <p className="max-w-3xl text-sm" role="status" data-answer="soon" data-answer-none="1">{M.answers ? `The live set could not be read, so no figure is shown: ${M.answers.reason}` : M.rules.words}</p>}
              </ToolSection>
              </div>

              <div data-question="2">
              <ToolSection title="Which option is better?" id="scenarios">
                {/* session 236: what A and B are for, in the block's own title and one line; B's site is set here */}
                <Sub>Scenarios A and B: two sites, or two contracts</Sub>
                <p className="mb-3 max-w-3xl text-sm" data-how-to-compare="1">
                  Scenario A is the load under &quot;Your load&quot;, and it sets the headline. To compare two sites, give scenario B a site of its own here: another zone or hub, or another grid. To compare two contracts, give A and B a different contract share and price below. The table then sets B against A.
                </p>
                <LoadSiteB sites={M.sitesB} current={M.bSite ? `${M.bSite.grid}:${M.bSite.region}` : ""} asked={typeof q.bsite === "string" ? q.bsite : ""} aPlace={place} keep={Object.entries(q).filter(([n, v]) => v !== undefined && n !== "bsite") as [string, string][]} />
                <LoadScenarios facts={facts} />
              </ToolSection>
              </div>

              <div data-question="3">
              <ToolSection title="What matters most" id="matters">
                <LoadSensitivity facts={facts} />
              </ToolSection>
              </div>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[...INDEX.tables, "carbon_intensity_monthly", "carbon_intensity_hourly", ...(x.grid === "caiso" || M.bSite?.grid === "caiso" ? ["caiso_grid_emergencies"] : []), ...(x.grid === "ercot" ? ["ercot_large_load_status"] : []), "large_load_rules", "clean_energy_summary", "grid_stress_yearly", "eia930_demand_growth", "interconnection_queue_summary", ...(x.grid === "ercot" ? ["ercot_large_load_status"] : []), ...(g?.demand_source && !M.withheld ? [g.demand_source.split(" ")[0]] : []), ...(DELIVERY.table && x.grid === "ercot" ? [DELIVERY.table, ...(DELIVERY.matrix_table ? [DELIVERY.matrix_table] : [])] : []), ...(x.grid === "nyiso" ? ["nyiso_load_queue"] : []), ...(M.cFile?.clean ? ["clean_energy_hourly"] : [])]}
        note={<>The price files were built {day(INDEX.built)}. Defaults: <span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.gpu.source}>power per GPU</span>, <span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.pue.source}>overhead ratio</span>. The default case hour by hour: <a href={HOURLY_CSV} download data-download="csv">CSV</a>, <a href={DO_FILE} download data-download="do">Stata do-file</a>, <a href={MIRROR} download data-download="py">Python mirror</a>. <Link href={METHOD}>Method note</Link>. <span data-checked-against="6">Checked against: 6 published figures (EIA). <Link href="/data/methods/datacenter_pays_algorithm#cross-checks">Each comparison, with its gap and the reason</Link>.</span></>} />
     </LoadDecisions>
  );
}

/** Session 236: Texas's delivery charges, one row a component (transmission, distribution, other riders) and the total,
 * a column a wires utility, in USD per MWh for a flat load of the reader's size served at transmission voltage. Each
 * figure is lib/datacenter/delivery.ts's sum of that utility's tariff lines of that kind and carries its check key
 * (dcd|<mw>|<utility>:<component>), which scripts/check-values.mjs recomputes from the site's file. Its own table: never
 * added to the market cost. The tariff's own lines are in the download (tables.csv, the table "delivery"). */
function DeliveryTable({ parts, mw, size, href }: { parts: UtilityDelivery[]; mw: number; size: string; href: string }): ReactNode {
  const fig = (u: string, what: string) => {
    const v = deliveryStat(DELIVERY.rows, mw, `${slugOf(u)}:${what}`);
    return v === undefined ? <Missing why="No line of this kind is in the utility's tariff as the page's file holds it." /> : <Num check={`dcd|${mw}|${slugOf(u)}:${what}`} raw={v}>{shown(v)}</Num>;
  };
  const left = parts.reduce((a, d) => a + d.conditional, 0), unread = parts.reduce((a, d) => a + d.unread, 0), lines = parts.reduce((a, d) => a + d.lines, 0);
  return (
    <div data-delivery="1">
      <Sub>Delivery charges in Texas, USD per MWh</Sub>
      <ToolTable caption="Delivery charges in Texas by component, USD per MWh for a flat load" minWidth={560} head={["Component", ...parts.map((d) => d.utility)]}
        rows={[
          ...KINDS.map((k) => ({ key: k, cells: [KIND_LABELS[k], ...parts.map((d) => <span key={d.utility} data-delivery-kind={k}>{fig(d.utility, k)}</span>)] })),
          { key: "total", highlight: true, cells: ["Total delivery", ...parts.map((d) => <span key={d.utility} data-delivery-total={slugOf(d.utility)}>{fig(d.utility, "total")}</span>)] },
        ]} />
      <p className="mt-2 max-w-3xl text-xs text-muted" data-delivery-note="1">
        For a flat {size} load served at transmission voltage, in the area of each of Texas&apos;s four large wires utilities. A component is the sum of that utility&apos;s tariff lines of that kind ({lines} lines in all): a rate per kW a month is counted on the load&apos;s size (a kVA as a kW), a rate per account a month is spread over the year&apos;s energy, a rate per kWh stands as it is.
        {left ? ` ${left} lines that apply only to some loads (a municipal fee or credit, a charge of one former service area) are left out of the sums.` : ""}{unread ? ` ${unread} lines whose unit names no basis are left out too.` : ""} Each figure is rounded to the cent, so a total can differ from the sum of its rows by a cent. These charges are never added to the market cost above; to count one in a scenario, type its total as that scenario&apos;s delivery and other charges.
        {" "}<a href={href} download>The tariff lines as filed, CSV</a>: each schedule&apos;s name, its rate and unit as printed, its page, its date and its document (the table &quot;delivery&quot;).
      </p>
    </div>
  );
}

const matrixTip = (r: MatrixRow) => `${r.document}, filed ${r.filed}, page ${r.page ?? "not printed"} of the attachment${r.scan_page ? ` (page ${r.scan_page} of the filed scan)` : ""}. Column "${r.header}". Read from the line: "${r.sentence}".${r.digits_spaced ? " The text of the file prints this figure with its digits spaced." : ""} ${r.docket_status}.`;
/** The Commission's wholesale transmission rate for all of ERCOT (the postage stamp rate), each year as printed, with
 * what it comes to per MWh for a flat load. Its own row: never added to the market cost. */
function MatrixCell({ rows }: { rows: MatrixRow[] }): ReactNode {
  const rates = rows.filter((r) => r.quantity === "postage_stamp_rate" && r.matrix !== "B");
  return (
    <span className="block text-ink" data-matrix="1">
      {rates.map((r) => (
        <span key={`${r.year}${r.matrix}`} className="mr-4 inline-block">
          <a href={r.scan_url || r.url} className="cursor-help no-underline hover:underline" title={`USD ${r.value.toFixed(6)} per kW of four-peak demand a year, as printed. ${matrixTip(r)}`} data-matrix-rate={r.year}>{r.year}</a>:
          {" "}<span className="cursor-help border-b border-dotted border-muted" title={`A flat load's demand in the four summer peak intervals is its size, so ${r.value.toFixed(6)} per kW a year over 8,760 hours is USD ${two((r.value * 1000) / 8760)} per MWh. This is the rate distribution providers pay for the whole grid's transmission; a retail customer pays it through its utility's transmission factor above. Not added to the market cost.`}>USD {two((r.value * 1000) / 8760)} per MWh, a flat load</span>
          <span className="ml-1 text-xs text-muted">{r.status === "approved" ? "approved" : "filed, not approved"}</span>
        </span>
      ))}
    </span>
  );
}
