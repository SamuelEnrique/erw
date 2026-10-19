import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AskErcotLink } from "@/components/AskErcotLink";
import { Brand } from "@/components/Brand";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { GroupedBars } from "@/components/tool/GroupedBars";
import { ChartFrame, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, Tip, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import * as B from "@/lib/batterystack";
import { caisoJoinDay } from "@/lib/caisoJoin";  // session 78: the join's date is written in one place
import { MARKETS, freeEnergyHref, hubAt, hubName, monthName as shortMonth, signed, two } from "@/lib/capture";
import { LICENSE_NEEDED, licenseGridTitle, licenseHeldGrid } from "@/lib/license";
import { ASSET_NAMES } from "@/lib/merchant";
import { isOldParam, isScenarioParam } from "@/lib/seller/finance";
import { usd, whole, type Span } from "@/lib/seller2";
import { CostTabs } from "../Tabs";
import { SellerForm } from "./SellerForm";
import { SellerProfile } from "./SellerProfile";
import { CoverHeadline, SellerDecisions, SellerScenarios, SellerSensitivity } from "./SellerScenarios";
import { BATTERY_GRIDS, CAPTURE, HUBS, HYBRID, STANDARD, ZONES, modelOf, type CapRow } from "./model";
import { Missing } from "./nums";

// Session 145: "What a generator earns", one page at one address. It holds what the seller's tab (session 51) and its
// version 2 (session 107, /cost-of-power/seller/v2, which redirects here) each showed, in the battery page's layout,
// and adds four things: (a) the capture price of a solar and a wind plant at every public hub and zone (lib/capture.ts
// on data/seller/capture.json, warehouse/derived/capture_price.py); (b) a contract for a share of the energy, computed
// in the browser and never sent (SellerContract.tsx); (c) a solar plant with a battery beside it, the battery's figure
// being the battery page's own (lib/batterystack.ts on battery_stack_monthly); (d) a link to where the curtailment
// page shows free energy for the hub chosen. The revenue model is the seller's tab's own (lib/merchant.ts on
// data/merchant_snapshot.json), its numbers carrying their check keys (mr|<inputs>|<stat>) for scripts/check-values.mjs.
// The page face carries no method: a figure that is missing is a short placeholder with its reason on hover, and the
// rest is in the Method note (docs/methods/cost_of_power.md). MISO is blank while its terms are reviewed; PJM needs a
// licensed source.
//
// Session 162, "deeper": (a) the plant and the battery co-optimized behind one interconnection against the day-ahead
// prices (lib/sellerhybrid.ts on data/seller/hybrid.json, warehouse/derived/seller_hybrid.py), side by side with the
// plant alone, the battery alone and the two added, session 145's added figure kept in its own row and labeled an
// upper bound, for solar and now for wind; (b) the capture price by hub and year, one table for every public hub
// (SellerHubYears.tsx on lib/capture.ts, hubYears); (c) "Your plant's profile", a year of hourly output pasted or
// uploaded and computed in the browser, never sent or stored (SellerProfile.tsx). Nothing session 145 showed is gone.
//
// Session 183, correctness: (1) the hub or zone chosen now prices everything the model shows (revenue, the months and
// the bad months, debt coverage, the spans, the stress days), not only the capture price and the contract: the model
// solved again with that hub's own price (lib/sellerhubs.ts on data/seller/hubs, warehouse/derived/merchant_hubs.py),
// in the market the hub's capture price is shown in, said beside each figure. The main hub keeps the page's snapshot,
// so no number of a default page moved. The battery beside it and the pasted profile stay at the main hub, and say so.
// (2) Every number, step by step, is docs/methods/generator_earns_algorithm.md, and the source line offers the default
// case hour by hour with its do-file.
//
// Session 186, decisions, as session 179 built them for the battery: one section after the contract, "Scenarios A and
// B" (SellerScenarios.tsx on lib/seller/finance.ts): eight assumptions with their cited defaults and Resets, two
// scenarios on the same eight rows, and a sensitivity chart, computed in the browser from figures this page already
// shows and kept in the address. Nothing above or below it changed. docs/methods/generator_earns_algorithm.md, section 11.
//
// Session 195: scenario A sets the headline. "Your plant" no longer holds a fixed O&M and annual debt payments of its
// own: the page's inputs take both from scenario A as the address has it (an older link's `fom` and `ds` are read as
// A's), and the headline's coverage, the line of one month of debt payments, the section "Debt coverage" and each
// month's coverage follow A in the browser as it is changed (SellerScenarios.tsx). At the defaults every number is what
// it was. The block itself is the one the three decision pages share (components/decisions/ScenarioBlock.tsx).
//
// Session 212 (the owner's chain prompt of 12 October 2026): the battery page's layout, one page on three questions,
// nothing folded. (1) "What did it earn?": the summary sentence, the three headline numbers, the revenue chart by year
// and the income table (the last twelve months beside the long-run averages), unchanged, with one sentence under the
// table of what the model cannot see, the two CSV downloads, and the reader's own year of output (SellerProfile, the
// browser's own arithmetic, kept here as the one tool the page has that is the reader's). (2) "Is it worth building?":
// scenarios A and B, with the contract's share and price as scenario assumptions (0 by default, so the default is
// fully merchant) and the results table. (3) "What matters most": the NPV sensitivity chart with one line on how to
// read it. Gone from the page, into the CSV downloads: the capture price at every hub, by year at the hub and by hub
// and year, the pair with a battery beside it (its figure stays a row of the results table), month by month, the
// section "Debt coverage", and the folds (every month, the stress days, the fleet's hours as EIA reports them). Gone
// outright: the premium chart by year (its figures are in the download and the headline), the standalone contract
// panel and "With your contract" (SellerContract.tsx stays on disk, undrawn). What the page computes is model.ts,
// shared with the downloads. The defaults: hurdle rate 12 percent (lib/seller/finance.ts, session 208). At a contract
// share of 0 every number that stays is what it was.
//
// Session 235 (the owner's task of 12 October 2026, the brand approved that day): (1) the page is on the brand, as the
// battery page is: it wraps what it draws in <Brand> (components/Brand.tsx) and writes no color, font or spacing of its
// own; the revenue chart by year is the brand's bar chart (components/tool/GroupedBars.tsx, plain SVG, its series named
// on the chart) where it was the chart library's with a legend box. (2) The capture price is back on the page, inside
// "What did it earn?", as one chart and one table (session 212 had moved it to a download: wrong): the chart, by year
// and over the last twelve months at the hub chosen, the price the plant received per MWh against the hub's average,
// the capture rate written above each pair; the table, one row a hub or zone of the grid, the last twelve months'
// capture price, hub average and capture rate, and the capture rate of each year. Both are model.ts's capView, the
// functions the download's capture tables are written from, so the page and the download agree; each of a solar or a
// wind plant's figures carries a check key (cap|<grid>|<hub>|<market>|<fuel>|<span>|<stat>) that
// scripts/check-values.mjs recomputes from the capture file. A battery's and a gas peaker's are this page's model at
// each hub. (3) "Is it worth building?": one click makes scenario B a PPA, and the results show the breakeven PPA
// price (SellerScenarios.tsx, lib/seller/finance.ts). No default and no other number moved. The downloads stay.
//
// Session 257 (the owner's task of 13 October 2026, session 253's list): the source line counts 20 published figures
// where it counted 10. The ten more are CAISO's: its market monitor's combustion turbine and Berkeley Lab's market value
// of wind and its PPA indexes, the rows of docs/methods/generator_earns_algorithm.md, section 12.5, that hold a gap, now
// in that note's "Cross-checks". No number of the page moved. Not done, each waiting as that list says: the peaker's
// carbon cost (a ruling), CAISO's stress days (the snapshot holds none), the sentence beside CAISO's wind (a ruling).
//
// Session 264 (the owner's list of 14 October 2026 for this tool; no section added, moved or removed): (1) wherever the
// page states a capture price, the capture rate stands beside it, from the same rows, with a check key: the summary
// sentence and the headline carry cap|<grid>|<hub>|<market>|<fuel>|l12|price, flat and rate (a solar or a wind plant), and
// the headline and the income table carry ms|<inputs>|<span>|<stat> at the main hub (a battery's and a peaker's too),
// which scripts/check-values.mjs recomputes from the model's snapshot. Every check key names its grid: cap| its second
// field, mr| and ms| the inputs' iso=. (2) A typed value of "Your plant" or of a scenario outside its bounds is held at the
// bound, and one line under the panel says so. (3) The two CSV downloads are offered where every publisher of the grid's
// prices allows redistribution (lib/license.ts, the verdicts of docs/licenses.md, unchanged): a grid whose prices are
// "license needed" on the day (ISO-NE and NYISO from 21 October 2026) gets the catalogue's words in their place.
export const metadata: Metadata = { title: "What a generator earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/cost_of_power";
const ALGORITHM = "/data/methods/generator_earns_algorithm";
const HOURLY_CSV = "/seller/erw_2026_generator_hourly.csv", DO_FILE = "/seller/erw_2026_generator_replication.do", MIRROR = "/seller/erw_2026_generator_replication.py";
const MONTHS_CSV = "/cost-of-power/seller/months.csv", TABLES_CSV = "/cost-of-power/seller/tables.csv";

/** Session 212: a heading inside one of the three questions (the income table's, the reader's own year). */
function Sub({ children }: { children: ReactNode }) {
  return <h3 className="mb-3 mt-2 border-t border-rule pt-3 font-serif text-lg">{children}</h3>;
}

export default async function Seller({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const M = await modelOf(q);
  const { snap, iso, x, scenarioParams, g, a, cg, hub, mainHub, atHub, at, key, k, sizeLabel, fuel, peaker, money, bmw, dur, strat, held, monthRows, s, ys, line, mk, why, mine, batt, battWhy, hf, pair, facts, capView } = M;
  const scenarioKey = `${iso}|${hub.id}|${k}|${x.mw}|${JSON.stringify(scenarioParams)}`;
  const costs = M.costsOf(k);

  const spanHead = [
    "",
    <span key="t">Last twelve months<span className="block text-xs font-normal opacity-80">{s.twelve ? `${shortMonth(s.twelve.from)} to ${shortMonth(s.twelve.to)}` : "not held yet"}</span></span>,
    <span key="3">Long-run average, a year<span className="block text-xs font-normal opacity-80">{s.threeYears ? `${s.threeYears[0]} to ${s.threeYears[2]}, the last three full years` : "the last three full years"}</span></span>,
    <span key="e">Long-run average, a year<span className="block text-xs font-normal opacity-80">{s.everyYears.length ? `every full year held, ${s.everyYears[0]} to ${s.everyYears.at(-1)}` : "every full year held"}</span></span>,
  ];
  // session 264: each figure with its check key at the main hub (ms|<inputs>|<span>|<stat>; spanNum below)
  const spanCell = (span: "twelve" | "three" | "every", v: Span | null, f: (v: Span) => string, id: string, whyNone: string) => {
    if (!v) return <Missing why={whyNone} />;
    const raw = id === "revenue" ? v.revenue_kw : id === "energy" ? v.energy : id === "capture" ? v.capture : id === "flat" ? v.flat : v.rate;
    return raw === null ? f(v) : spanNum(span, id, raw, f(v));
  };
  const spanRow = (label: string, f: (v: Span) => string, id: string, highlight = false) => ({
    key: id, highlight, cells: [label, <span key="t" data-seller2={`twelve|${id}`}>{spanCell("twelve", s.twelve, f, id, M.twelveWhy)}</span>, <span key="3" data-seller2={`three|${id}`}>{spanCell("three", s.three, f, id, M.threeWhy)}</span>,
      <span key="e" data-seller2={`every|${id}`}>{spanCell("every", s.every, f, id, M.everyWhy)}</span>],
  });
  // the two downloads take the page's own parameters and scenario A's, as this request has them
  const query = new URLSearchParams();
  for (const [n, v] of Object.entries(q)) if (v !== undefined && (["iso", "hub", "asset", "mw", "mwh", "hr", "vom", "bmw", "dur", "strat"].includes(n) || isScenarioParam(n) || isOldParam(n))) query.set(n, v);
  const suffix = query.size ? `?${query.toString()}` : "";

  // session 235: the capture chart and table (model.ts, capView)
  const capName = fuel ? "Capture price" : peaker ? "Price while running" : "Price while selling";
  const capAt = fuel ? `${hubAt(hub.id)}, ${MARKETS[mk].toLowerCase()} prices` : at;
  const hubHref = (id: string) => { const u = new URLSearchParams(query); u.set("iso", iso); u.set("hub", id); return `/cost-of-power/seller?${u.toString()}#capture`; };
  /** One figure of the capture table: a solar or a wind plant's carries its check key; a rate is written in whole percent. */
  const capNum = (r: CapRow, span: string, what: "price" | "flat" | "rate", v: number) => {
    const raw = what === "rate" ? Math.round(v) : v, text = what === "rate" ? whole(v) : two(v);
    return capView.fuel
      ? <Num check={`cap|${iso}|${r.id}|${r.market}|${capView.fuel}|${span}|${what}`} raw={raw}>{text}</Num>
      : <span data-model-cap={`${r.id}|${span}|${what}`} data-raw={raw}>{text}</span>;
  };
  const capHead = (top: string, under: string) => <span key={top}>{top}<span className="mt-0.5 block text-xs opacity-80">{under}</span></span>;

  // session 264: the capture price of the hub chosen with its rate beside it, each with its check key (the capture file)
  const capKey = (what: "price" | "flat" | "rate") => `cap|${iso}|${hub.id}|${mk}|${fuel}|l12|${what}`;
  const mineRate = mine && mine.flat > 0 ? Math.round((100 * mine.price) / mine.flat) : null;
  // session 264: the model's spans carry ms|<inputs>|<span>|<stat> at the main hub (the inputs name the grid, iso=)
  const spanNum = (span: "twelve" | "three" | "every", stat: string, v: number, text: string) =>
    atHub ? <>{text}</> : <Num check={`ms|${key}|${span}|${stat}`} raw={stat === "energy" || stat === "rate" ? Math.round(v) : v}>{text}</Num>;
  // session 264: a typed value outside its bounds is held at the bound, and the panel says so in one line
  const clamped = M.clampedWords;
  // session 264: the downloads, where the grid's prices may be redistributed (lib/license.ts; no verdict changed here)
  const pricesHeld = licenseHeldGrid(iso);
  const heldWords = <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={licenseGridTitle(iso)} data-license-held="downloads">{LICENSE_NEEDED}</span>;

  return (
    <Brand noUsage>
    <ToolPage>
      <ToolHeader
        title="What a generator earns"
        crumb={<CostTabs active="sell" />}
        lead={<>What a solar plant, a wind plant, a battery or a gas peaker earned selling at the hub price: by year, the price it received against the flat average, whether that covers its debt, and whether it is worth building, with or without a contract. <Link href={METHOD}>Method note</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}
      />
      {x.iso === "ercot" ? <AskErcotLink context={{ view: "/cost-of-power/seller", title: "What a generator earns", settings: { grid: "ERCOT", hub: hubName(hub.id), asset: ASSET_NAMES[x.asset], size: sizeLabel } }} /> : null}
      <SellerDecisions key={scenarioKey} costs={costs} mw={x.mw} initial={scenarioParams}>
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Your plant">
              <SellerForm key={`${key}|${hub.id}|${bmw}|${dur}|${strat}`} x={{ iso, hub: hub.id, asset: x.asset, mw: x.mw, mwh: x.mwh, hr: x.hr, vom: x.vom, bmw, dur, strat }} grids={M.grids} hybrid={M.hybrid} defaults={M.defaults} />
              {clamped.length ? <p className="mt-2 text-xs leading-snug" role="status" data-clamped={clamped.length}>{clamped.join(" ")}</p> : null}
            </InputPanel>
          </aside>

          <div className="min-w-0" data-priced-hub={M.snap.isos[iso].hub} data-priced-market={atHub ? M.he!.market : "rt"}>
            {!mainHub && !atHub ? (
              <p className="mb-4 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-hub-model="none">
                The model holds no month at {hubAt(hub.id)}: revenue, the months and debt coverage below are priced at {g.at}.
              </p>
            ) : null}
            {held.length === 0 ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-seller2-none="1">
                No month of {a.name.toLowerCase()} is held for {g.name}{atHub ? ` at ${hubAt(hub.id)}` : ""}, so no number is shown{x.asset === "solar" && iso === "nyiso" ? ": EIA-930 itemizes no solar generation for New York" : ""}.
              </p>
            ) : null}

            <div data-question="1">
            <ToolSection title="What did it earn?" id="earned">
              {held.length ? (
                <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                  {line ?? <>{g.name} holds no twelve months of {a.name.toLowerCase()} in a row, so the last twelve months are not shown.</>}
                  {mine ? <> At {hubAt(hub.id)} the price it received, weighted by generation, was USD <Num check={capKey("price")} raw={mine.price}>{two(mine.price)}</Num> per MWh, USD {two(Math.abs(mine.premium))}{mine.pct === null ? "" : ` (${Math.abs(mine.pct).toFixed(1)} percent)`} {mine.premium < 0 ? "below" : "above"} the flat average of USD <Num check={capKey("flat")} raw={mine.flat}>{two(mine.flat)}</Num>{mineRate === null ? "" : <>: a capture rate of <Num check={capKey("rate")} raw={mineRate}>{whole(mineRate)}</Num> percent</>}.</> : null}
                </p>
              ) : null}

              <HeadlineRow>
                <HeadlineNumber label={`${money}, last twelve months`}
                  value={s.twelve ? <span data-stat="l12_kw">{spanNum("twelve", "revenue", s.twelve.revenue_kw, usd(s.twelve.revenue_kw))}</span> : <Missing why={M.twelveWhy} />} unit={s.twelve ? "USD/kW" : undefined}
                  note={s.twelve ? <>{shortMonth(s.twelve.from)} to {shortMonth(s.twelve.to)}, priced at <span data-stat="priced_at">{at}</span></> : null} />
                {fuel ? (
                  <HeadlineNumber label={`Price received at ${hubAt(hub.id)}`}
                    value={mine ? <span data-stat="cap_price"><Num check={capKey("price")} raw={mine.price}>{two(mine.price)}</Num></span> : <Missing why={why(hub, fuel, mk)} />} unit={mine ? "USD/MWh" : undefined}
                    note={mine ? <><span data-stat="cap_premium">{signed(mine.premium)}</span> USD per MWh{mine.pct === null ? "" : <> (<span data-stat="cap_pct">{signed(mine.pct, 1)}</span> percent)</>} against the flat average of <span data-stat="cap_flat"><Num check={capKey("flat")} raw={mine.flat}>{two(mine.flat)}</Num></span>{mineRate === null ? "" : <>, a capture rate of <span data-stat="cap_rate"><Num check={capKey("rate")} raw={mineRate}>{whole(mineRate)}</Num></span> percent</>}; {MARKETS[mk].toLowerCase()}, {shortMonth(mine.from)} to {shortMonth(mine.to)}</> : null} />
                ) : (
                  <HeadlineNumber label={peaker ? "Price while running" : "Price while selling"}
                    value={s.twelve && s.twelve.capture !== null ? spanNum("twelve", "capture", s.twelve.capture, usd(s.twelve.capture)) : <Missing why={M.twelveWhy} />} unit={s.twelve && s.twelve.capture !== null ? "USD/MWh" : undefined}
                    note={s.twelve ? <>against {spanNum("twelve", "flat", s.twelve.flat, usd(s.twelve.flat))} for every hour{s.twelve.rate !== null ? <>: a capture rate of {spanNum("twelve", "rate", s.twelve.rate, whole(s.twelve.rate))} percent</> : null}</> : null} />
                )}
                {/* session 195: coverage at scenario A's fixed O&M and debt payments; session 212: and A's contract (SellerScenarios.tsx) */}
                <CoverHeadline rows={monthRows} mw={x.mw} pre={key} facts={facts} />
              </HeadlineRow>

              {held.length ? (
                <>
                  {/* session 235: the brand's bar chart, the series named on it (components/tool/GroupedBars.tsx) */}
                  {/* session 298: the note is a hover tip beside the title, the battery page's manner (session 296, item 9) */}
                  <ChartFrame title={`${money} by year, USD per kW`}
                    tip={<Tip id="revenue-years" label="the chart by year">Per kW of nameplate, priced at {at}. {atHub ? hubName(hub.id) : g.name} is held from {shortMonth(held[0].m)}.{ys.some((y) => !y.complete) ? " A hatched year holds fewer than twelve months and is not a full year." : ""}</Tip>}>
                    <GroupedBars id="revenue" unit="USD per kW" label={`${a.name} in ${g.name}: ${money.toLowerCase()} by year, USD per kW`} series={[{ name: money, tone: "accent" }]}
                      groups={ys.map((y) => ({ label: y.y, sub: y.complete ? undefined : `${y.months} months`, partial: !y.complete, values: [y.revenue / 1000],
                        title: `${y.y}: ${money.toLowerCase()} ${usd(y.revenue / 1000)} USD per kW${y.complete ? "" : ` (${y.months} of 12 months held, not a full year)`}` }))} />
                  </ChartFrame>

                  <Sub>The last twelve months beside the long-run averages</Sub>
                  <ToolTable caption={`${a.name} in ${g.name}, by span`} minWidth={680} head={spanHead}
                    rows={[
                      spanRow(`${money}, USD per kW`, (v) => usd(v.revenue_kw), "revenue", true),
                      spanRow(peaker ? "Energy sold while running, MWh per MW" : "Energy sold, MWh per MW", (v) => whole(v.energy), "energy"),
                      spanRow(peaker ? "Price while running, USD per MWh" : "Capture price, USD per MWh", (v) => (v.capture !== null ? usd(v.capture) : "not held"), "capture"),
                      spanRow("Price of every hour, USD per MWh", (v) => usd(v.flat), "flat"),
                      spanRow(peaker ? "Price while running over every hour's, percent" : "Capture rate, percent", (v) => (v.rate !== null ? whole(v.rate) : "not held"), "rate"),
                    ]} />
                  {x.asset === "battery" ? <p className="mt-2 text-sm">Energy alone. Energy and ancillary services together, at 2, 4 and 8 hours: <Link href="/cost-of-power/battery">What a battery earns</Link>.</p> : null}
                </>
              ) : null}
              {/* session 212: one sentence of what the model cannot see; the rest is in the methods note */}
              <p className="mt-2 max-w-3xl text-xs text-muted" data-income-note="1">
                Per kW of nameplate, priced at {at}. {fuel ? `The plant is ${g.name}'s whole ${fuel} fleet by the hour, scaled to ${sizeLabel}, not one site, and is paid the hub's price, not its own node's; nothing is curtailed, and no capacity or ancillary payment is counted.` : peaker ? `The peaker runs in every hour the hub's price is above its fuel and variable cost, and is paid the hub's price, not its own node's; no start cost, no minimum run, no capacity or ancillary payment is counted.` : `The battery sells energy alone at the hub's price, not its own node's, with no ancillary service and no capacity payment; energy and ancillary services together are on What a battery earns.`}
                {" "}<Link href={`${ALGORITHM}#cannot-see`}>What else the model cannot see</Link>.
                {fuel ? <> <span data-free-energy="1">Hours when power here was free or cost less than nothing: <Link href={freeEnergyHref(iso, hub.id)}>where free energy is, for {hubAt(hub.id)}</Link>.</span></> : null}
              </p>

              {/* session 235: the capture price, one chart and one table (model.ts, capView; the download's own functions) */}
              {held.length || capView.chart.length ? (
                <div id="capture" data-capture={capView.fuel ?? "model"}>
                  <Sub>What it earned per MWh against the hub average</Sub>
                  {capView.chart.length ? (
                    <ChartFrame title={`${capName} against the hub average, by year, USD per MWh`}
                      tip={<Tip id="capture-years" label="the capture chart">At {capAt}. {fuel ? `${capName}: what ${g.name}'s whole ${fuel} fleet was paid for each MWh, the hub's price weighted by the fleet's generation hour by hour.` : `${capName}: what the ${peaker ? "peaker" : "battery"} was paid for each MWh it sold.`} Hub average: the plain average of the price over the same hours. The percent above each pair is the capture rate, the first over the second.{capView.chart.some((c) => c.partial) ? " A hatched year holds fewer than twelve months." : ""}</Tip>}>
                      <GroupedBars id="capture" unit="USD per MWh" label={`${a.name} at ${capAt}: ${capName.toLowerCase()} against the hub average by year, USD per MWh`}
                        series={[{ name: capName, tone: "accent" }, { name: "Hub average", tone: "ink" }]}
                        groups={capView.chart.map((c) => ({ label: c.label, sub: c.partial ? `${c.months} months` : undefined, partial: c.partial, values: [c.price, c.flat],
                          over: c.rate === null ? undefined : `${whole(c.rate)}%`,
                          title: `${c.label}: ${capName.toLowerCase()} ${two(c.price)} USD per MWh against a hub average of ${two(c.flat)}${c.rate === null ? "" : `, a capture rate of ${whole(c.rate)} percent`}${c.partial ? ` (${c.months} of 12 months counted, a partial year)` : ""}` }))} />
                    </ChartFrame>
                  ) : (
                    <p className="mb-6 text-sm" data-capture-chart="none"><Missing why={fuel ? why(hub, fuel, mk) : M.twelveWhy} words={`No year is held at ${hubAt(hub.id)}`} /></p>
                  )}
                  <p className="mb-2 max-w-3xl text-sm" data-capture-lead="1">Every hub and zone of {g.name}: the last twelve months in the first three columns, then the capture rate of each year, in percent.</p>
                  <ToolTable caption={`${capName}, hub average and capture rate at every hub and zone of ${g.name}: the last twelve months, and the capture rate by year`}
                    minWidth={300 + 50 * capView.years.length}
                    head={["Hub or zone", capHead(capName, "USD per MWh"), capHead("Hub average", "USD per MWh"), capHead("Capture rate", "percent"), ...capView.years]}
                    rows={capView.rows.map((r) => ({ key: r.id, cells: [
                      <span key="n" data-cap-row={r.id} data-cap-chosen={r.chosen ? "1" : undefined}>
                        <span className="sm:whitespace-nowrap">{r.chosen ? <strong>{r.name}</strong> : <Link href={hubHref(r.id)} scroll={false}>{r.name}</Link>}</span>
                        <span className="block text-xs text-muted">{r.chosen ? "the hub chosen, " : ""}{MARKETS[r.market].toLowerCase()}</span>
                      </span>,
                      ...(["price", "flat", "rate"] as const).map((what) => {
                        const t = r.twelve, v = t ? (what === "rate" ? t.rate : t[what]) : null;
                        return t && v !== null
                          ? <span key={what} title={`${r.name}, ${shortMonth(t.from)} to ${shortMonth(t.to)}, ${MARKETS[r.market].toLowerCase()} prices`}>{capNum(r, "l12", what, v)}</span>
                          : <Missing key={what} why={t ? "The hub's average is not above zero, so there is no rate." : r.whyTwelve} words="not held" />;
                      }),
                      ...r.years.map((c, i) => (c && c.rate !== null
                        ? <span key={capView.years[i]} className={c.partial ? "text-muted" : undefined}
                            title={`${r.name}, ${capView.years[i]}: ${capName.toLowerCase()} ${two(c.price)} USD per MWh against a hub average of ${two(c.flat)}${c.partial ? `; ${c.months} of 12 months counted, a partial year` : ""}`}>{capNum(r, capView.years[i], "rate", c.rate)}</span>
                        : <Missing key={capView.years[i]} why={c ? "The hub's average is not above zero, so there is no rate." : r.whyYears[i]} words="none" />)),
                    ] }))} />
                  <p className="mt-2 max-w-3xl text-xs text-muted" data-capture-note="1">
                    One row a hub or zone of {g.name}, each at the prices it is held in. {fuel
                      ? `Capture price: the hub's price weighted by ${g.name}'s ${fuel} generation hour by hour, the whole fleet and not one site. `
                      : `${capName}: this page's model of the ${peaker ? "peaker" : "battery"}, solved at each hub's own price. `}
                    Hub average: the plain average of the price over the same hours. Capture rate: the first as a percent of the second, in whole percent; under 100 the plant
                    was paid less for a MWh than the hub&apos;s average. A year in grey holds fewer than twelve months. A hub&apos;s name opens the page at that hub.
                    {fuel ? <> Both fuels, both markets and each year&apos;s capture price at every hub: {pricesHeld ? heldWords : <a href={`${TABLES_CSV}${suffix}`} download>the other tables, CSV</a>}.</> : null}
                  </p>
                </div>
              ) : null}

              <p className="mt-2 max-w-3xl text-xs text-muted" data-months-csv="1">
                {pricesHeld ? <>Every month, CSV: {heldWords}</> : <a href={`${MONTHS_CSV}${suffix}`} download>Every month, CSV</a>}: revenue, energy, the capture price and rate, and each month&apos;s coverage at scenario A&apos;s costs, for {sizeLabel} at {at}.
                {" "}{pricesHeld ? <>The other tables, CSV: {heldWords}</> : <a href={`${TABLES_CSV}${suffix}`} download>The other tables, CSV</a>}: the capture price at every hub and zone of {g.name} over the last twelve months and by year, every public hub by year, the plant with a battery beside it, the stress days, and the fleet&apos;s hours as EIA reports them.
              </p>

              {fuel ? (
                <>
                  <Sub>Your plant&apos;s own year</Sub>
                  <SellerProfile key={`${iso}|${bmw}|${dur}`} grid={iso} gridName={g.name} hub={hubName(cg.main)} zone={ZONES[String(STANDARD[iso])]} years={HYBRID.years[iso] ?? []}
                    battery={{ mw: bmw, hours: dur }} hybridWhy={BATTERY_GRIDS.includes(iso) ? null : battWhy} />
                </>
              ) : null}
            </ToolSection>
            </div>

            <div data-question="2">
            <ToolSection title="Is it worth building?" id="scenarios">
              <SellerScenarios facts={facts} />
            </ToolSection>
            </div>

            <div data-question="3">
            <ToolSection title="What matters most" id="matters">
              <SellerSensitivity facts={facts} />
            </ToolSection>
            </div>
          </div>
        </div>
      </SellerDecisions>
      <SourceLine tables={["merchant_revenue_monthly", "eia_fuel_spot_prices", "eia860m_operating_generators", ...new Set(cg.hubs.flatMap((h) => [...(h.rt?.tables ?? []), ...(h.da?.tables ?? [])])), ...(batt ? [B.TABLE] : [])]}
        note={<>Derived by the ERW from {g.name}&apos;s public prices and EIA-930&apos;s hourly generation by source ({cg.workbook}){cg.generation.includes("caiso") ? `, California from ${caisoJoinDay()} from CAISO's own supply by fuel` : ""}. The model&apos;s snapshot was built {snap.built.slice(0, 10)}, the capture prices {CAPTURE.built.slice(0, 10)}{atHub ? `, the model at ${hubAt(hub.id)} ${HUBS.built.slice(0, 10)}` : ""}{pair && hf ? `, the pair with a battery ${HYBRID.built.slice(0, 10)}` : ""}. The default case hour by hour: <a href={HOURLY_CSV} download data-download="csv">CSV</a>, <a href={DO_FILE} download data-download="do">Stata do-file</a>, <a href={MIRROR} download data-download="py">Python mirror</a>. Cost defaults: Lazard, Levelized Cost of Energy+, June 2025. The buyer&apos;s side is <Link href="/cost-of-power">What a datacenter pays</Link>. <span data-checked-against="21">Checked against: 21 published figures (Lazard, the Annual Technology Baseline, EIA, CAISO&apos;s market monitor, Berkeley Lab, Potomac Economics). <Link href="/data/methods/generator_earns_algorithm#cross-checks">Each comparison, with its gap and the reason</Link>.</span> <span data-decisions="298">Decisions of 18 October 2026 (session 298): solar&apos;s degradation default is the Annual Technology Baseline&apos;s 0.7 percent a year, which moved the default solar case&apos;s NPV from USD -74.16 million to -76.66 million (-741.60 to -766.62 per kW); the CAISO peaker&apos;s run rule counts California&apos;s allowance (USD 43.19 to 19.66 per kW over the last twelve months, 2,294 to 624 hours run).</span></>} />
    </ToolPage>
    </Brand>
  );
}
