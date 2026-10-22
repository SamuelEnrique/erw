import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { InlineSpark } from "@/components/InlineSpark";
import { InputPanel } from "@/components/tool/ToolPage";
import type { ReactNode } from "react";
import { nodeShortMonths, shortMonthsWords, CAPACITY_RULE, COLUMNS, CURTAIL_WORDS, GRID_NAMES, NODE_HUB, PROFILES, NODE_SORTS, SORT_WORDS, allInCell, capacityCell, capacityOverPeak, columnValue, nodeTable, rowOf, screen, yearKey, yearOf, carbonCell, connectCell, cpCharge, demandGrowth, utilityCell, energyCell, hubRows, nodeRows, profileCell, profileKey, sitingHref, sitingInputs, type EnergyCell, type NodeSort, type Row, type SitingInputs, type Twelve } from "@/lib/siting";
import { CP, NODES, SITING_DC, SITING_FILES } from "@/lib/sitingdata";
import { AllGridsForm } from "./AllGridsForm";
import { AllGridsNodes } from "./AllGridsNodes";

// Session 700 (chain 050, docs/methods/siting.md): the All grids tab of "What a datacenter pays". The questions "Your
// load" answers for one region (what a load pays, when it connects, how clean the power is) for every grid, hub and
// zone the page's price files hold, and behind a toggle every ERCOT node of node_basis_daily, in one table, with the
// same model: the rows are "Your load"'s own index (lib/sitingdata.ts), and each column is computed by the library
// function that computes it for "Your load" (lib/siting.ts). The left box holds every input, the right side only
// results. The tab ranks nothing by a score and expresses no view: it sorts by the column the reader chooses and says
// what the sort is. Every figure is a check key, allgrids|<column>|<row>, recomputed by scripts/check-values.mjs from the
// same files. Session 700 draws the rows, the toggle, the column heads with their tips, and one number: the row count.

const tipCls = "cursor-help border-b border-dotted border-muted";
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const monthWords = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

/** Session 714: a tip a keyboard reaches. Until this session the tab's tips were `title`, which shows on a mouse's hover
 * only. Now the words sit in a role="tooltip" span inside the thing, which the site's rule shows on hover and on focus
 * (app/tokens.css, ".tip", as components/tool/ToolPage.tsx's Tip), and a screen reader reads with it. `extra` is drawn
 * in the tip under the words (a figure's twelve months). */
// The trigger is a button described by the tip (as the shared Tip's is), so a keyboard reaches it and a screen reader
// reads the tip as its description; AccessLint's scan found the focusable spans without a role at first (session 714).
// The ids number the page's tips in the order drawn: a page is drawn in one pass on the server.
let tipSeq = 0;
function Tp({ tip, children, extra, dotted = true, className = "", data }: { tip: string; children: ReactNode; extra?: ReactNode; dotted?: boolean; className?: string; data?: Record<string, string> }) {
  const id = `ag-tip-${(tipSeq = (tipSeq + 1) % 1_000_000)}`;
  return (
    <span className={`tip relative inline-block ${className}`.trim()} {...Object.fromEntries(Object.entries(data ?? {}).map(([k, v]) => [`data-${k}`, v]))}>
      <button type="button" aria-describedby={id} className={`text-inherit ${dotted ? tipCls : ""}`} data-tip-trigger="1">{children}</button>
      <span role="tooltip" id={id} className="absolute right-0 top-full z-20 hidden w-72 max-w-[80vw] whitespace-normal border border-rule bg-paper px-2 py-1.5 text-left font-sans text-xs font-normal leading-snug text-ink">
        {tip}{extra ? <span className="mt-1 block">{extra}</span> : null}
      </span>
    </span>
  );
}
/** A cell the warehouse cannot fill: short words in ink, the reason on hover and on focus (no visible grey text). */
function Words({ words, why }: { words: string; why: string }) {
  return <Tp tip={why} data={{ "cell-words": "1" }}>{words}</Tp>;
}
/** One figure with its tip: the reason, the window and its source; `children` (a figure's twelve months) in the tip. */
function Fig({ check, v, tip, children }: { check: string; v: number; tip: string; children?: ReactNode }) {
  return <Tp tip={tip} extra={children}><Num check={check} raw={v}>{two(v)}</Num></Tp>;
}
/** Session 701: the twelve months of a figure, drawn on hover and on focus (the shared inline chart, components/InlineSpark). */
function Spark({ t, label }: { t: Twelve; label: string }) {
  return (
    <span className="inline-block bg-white p-1" data-spark="1">
      <InlineSpark values={t.months.map((r) => ({ t: `${r.m}-01`, v: r.per }))} label={label} width={140} height={32} />
    </span>
  );
}
function twelveTip(t: Twelve, market: string): string {
  const last = t.months.at(-1)!;
  return `${market}, a flat load, ${monthWords(t.from)} to ${monthWords(t.to)}, ${t.hours.toLocaleString("en-US")} hours held: USD ${two(t.per)} per MWh. The last whole month, ${monthWords(last.m)}: USD ${two(last.per)}.${t.year ? ` The last whole year, ${t.year.y}: USD ${two(t.year.per)}.` : ""} From the page's hourly files, as "Your load" computes it (lib/datacenter.ts).`;
}
/** Session 701: the energy cell: the day-ahead figure, real time beside it where held; a node's hub plus its basis. */
function EnergyTd({ r, e }: { r: Row; e: EnergyCell }) {
  if (e.node) {
    const n = e.node;
    return (
      <Fig check={`allgrids|energy|${r.id}|da`} v={n.per}
        tip={`${NODE_HUB}'s day-ahead price over ${monthWords(n.hub.from)} to ${monthWords(n.hub.to)}, USD ${two(n.hub.per)} per MWh, plus this node's mean daily day-ahead basis to it, USD ${two(n.basis)}, over ${n.days} of the ${n.due} days (node_basis_daily, daily, not hourly). Real time is not held at the nodes for twelve months.`}>
        <Spark t={n.hub} label={`${NODE_HUB} day-ahead by month`} />
      </Fig>
    );
  }
  if (!e.da && !e.rt) return <Words words={e.words ?? "not held"} why={e.why ?? ""} />;
  return (
    <span className="whitespace-nowrap">
      {e.da ? <Fig check={`allgrids|energy|${r.id}|da`} v={e.da.per} tip={twelveTip(e.da, "Day-ahead")}><Spark t={e.da} label={`${r.region} day-ahead by month`} /></Fig> : <Words words="no day-ahead" why={`Twelve whole months of day-ahead prices are not held for ${r.region}.`} />}
      {e.rt ? <span className="ml-2 text-xs" data-rt="1">rt <Fig check={`allgrids|energy|${r.id}|rt`} v={e.rt.per} tip={twelveTip(e.rt, "Real time")} /></span> : null}
    </span>
  );
}

function RowToggle({ x, hubs, nodes }: { x: SitingInputs; hubs: number; nodes: number }) {
  const item = (rows: SitingInputs["rows"], label: string, n: number) => {
    const on = x.rows === rows;
    return (
      <Link href={sitingHref(x, { rows })} scroll={false} aria-current={on ? "page" : undefined} data-allgrids-rows={rows}
        style={{ color: on ? "var(--color-surface)" : "var(--color-ink)" }}
        className={`border px-2 py-1 no-underline ${on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>
        <span style={{ color: on ? "var(--color-surface)" : "var(--color-ink)" }}>{label} ({n.toLocaleString("en-US")})</span>
      </Link>
    );
  };
  return <nav aria-label="Rows" className="mb-3 flex flex-wrap gap-1 text-xs" data-allgrids-toggle="1">{item("hubs", "Hubs and zones", hubs)}{item("nodes", "ERCOT nodes", nodes)}</nav>;
}

const lastCp = () => CP.summers.at(-1);
/** Session 702: a profile's energy cell: the day-ahead price over the hours the load runs, and the hours it was off. */
function ProfileTd({ r, x }: { r: Row; x: SitingInputs }) {
  const c = profileCell(SITING_DC, SITING_FILES, r, x, CP);
  if ("why" in c) {
    const e = energyCell(SITING_DC, SITING_FILES, r);
    return <Words words={e.words ?? (r.blank ? r.blank.words : "not held")} why={c.why} />;
  }
  const p = PROFILES[x.profile], t = c.t, k = profileKey(x);
  const flat = energyCell(SITING_DC, SITING_FILES, r);
  const flatPer = flat.node?.per ?? flat.da?.per;
  const rule = p.curtail === "peaks_strike"
    ? `Off in an hour whose day-ahead price is at or above USD ${two(t.strike ?? 0)} per MWh${r.grid === "ercot" ? `, and in the hours of ERCOT's four summer peak intervals: none of those held falls in these months (ercot_4cp_intervals holds summers to ${lastCp()?.year ?? "none"}; ${CP.note})` : ""}.`
    : p.curtail === "below_strike"
      ? `Runs in an hour whose day-ahead price is ${x.strike === null ? `at or below USD ${two(t.strike ?? 0)} per MWh, this row's own price at the load factor ${x.lf.toFixed(2)} (the cheapest ${Math.round(x.lf * 100)} percent of its hours)` : `below USD ${two(t.strike ?? 0)} per MWh`}.`
      : p.curtail === "interruptible" ? "Runs every hour: no table the warehouse holds names the hours a grid interrupts a heavy load." : "Runs every hour.";
  const tip = `${p.label}, day-ahead, ${monthWords(t.from)} to ${monthWords(t.to)}: USD ${two(c.per)} per MWh over the ${t.run.toLocaleString("en-US")} hours it ran, off in ${t.lost.toLocaleString("en-US")} of the ${t.held.toLocaleString("en-US")} hours held. ${rule}${flatPer !== undefined ? ` A flat load: USD ${two(flatPer)}.` : ""}${c.daily ? ` A node: ${NODE_HUB}'s figure under the same rule plus the node's mean daily basis, USD ${two(c.basis ?? 0)} (node_basis_daily, daily: the rule reads the hub's hours).` : ""}`;
  return (
    <span className="whitespace-nowrap">
      <Fig check={`allgrids|energy|${r.id}|da|${k}`} v={c.per} tip={tip} />
      {p.curtail !== "none" && p.curtail !== "interruptible" ? <span className="ml-2 text-xs" data-lost="1">off <Tp dotted={false} tip={`Hours of the ${t.held.toLocaleString("en-US")} held the load was off`}><Num check={`allgrids|lost|${r.id}|${k}`} raw={t.lost}>{t.lost.toLocaleString("en-US")}</Num></Tp> h</span> : null}
    </span>
  );
}

/** Session 703: the transmission cell. ERCOT: the profile's own four-peak charge, with the firm and the curtailing
 * charge beside it; elsewhere "not held", the large-load tariff that would fill it named on hover. */
function TxTd({ r, x }: { r: Row; x: SitingInputs }) {
  const c = cpCharge(SITING_DC, SITING_FILES, r, x);
  if ("why" in c) return <Words words={c.words} why={c.why} />;
  const k = profileKey(x), p = PROFILES[x.profile];
  const ivs = c.intervals.map((iv) => `${iv.local} (${iv.w === null ? "price not held" : iv.w ? "on" : "off"})`).join("; ");
  const base = `ERCOT's four summer peak intervals of ${c.year} (ercot_4cp_intervals) at the Commission's ${c.rate.year} rate, USD ${c.rate.value.toFixed(6)} per kW of four-peak demand a year (texas_transmission_matrix), over the ${Math.round(c.hours).toLocaleString("en-US")} hours a year the load runs${r.kind === "node" ? ` (${NODE_HUB}'s hours: the node table is daily)` : ""}. The charge is paid the year after the summer.`;
  const firmTip = `Firm: the load's full demand in all four intervals. ${base}`;
  const curtTip = `Curtailing: a load off in the four intervals' hours, computed from its weights in those hours, not assumed. ${base}`;
  return (
    <span className="whitespace-nowrap">
      {c.own === null ? <Words words="not held" why={`The price of an interval's hour is not held, so the load's share in it cannot be computed. ${base}`} />
        : <Fig check={`allgrids|tx|${r.id}|${k}`} v={c.own} tip={`${p.label}: it ran in ${Math.round((c.share ?? 0) * 4)} of the four intervals of ${c.year} (${ivs}). ${base}`} />}
      <span className="ml-2 text-xs" data-tx-firm="1">firm <Fig check={`allgrids|tx|${r.id}|firm|${k}`} v={c.firm} tip={firmTip} /></span>
      {c.curtailing !== null ? <span className="ml-2 text-xs" data-tx-curtailing="1">off <Fig check={`allgrids|tx|${r.id}|curtailing|${k}`} v={c.curtailing} tip={curtTip} /></span> : null}
    </span>
  );
}
/** Session 703: the all-in cell, drawn only where energy, transmission and capacity are each held or zero by design. */
function AllInTd({ r, x }: { r: Row; x: SitingInputs }) {
  const a = allInCell(SITING_DC, SITING_FILES, r, x);
  if ("missing" in a) return a.words === "license needed" ? <Held table="iso_all_capacity_prices" why={`Computed where the capacity tables are held and drawn as "license needed" (session 408's rule): ${a.missing}`} /> : <Words words="not held" why={`Not every part is held: ${a.missing}`} />;
  return <Fig check={`allgrids|allin|${r.id}|${profileKey(x)}`} v={a.v} tip={`Energy USD ${two(a.parts.energy)}, transmission USD ${two(a.parts.transmission)} and capacity USD ${two(a.parts.capacity)} per MWh${r.grid === "ercot" ? " (ERCOT has no capacity market)" : ""}. No delivery, distribution, ancillary or retail charge is in it.`} />;
}

/** A figure computed from an internal table: "license needed" in place, with the table and why on hover (session 408's
 * rule; the same words and mark as components/Num.tsx's held figures, so the value checker passes it by). */
function Held({ table, why }: { table: string; why: string }) {
  return <Tp tip={why} data={{ "license-held": table }}>license needed</Tp>;
}
const periodWords = (s: string, e: string) => `${s.slice(0, 10)} to ${e.slice(0, 10)}`;
/** Session 704: the capacity cell. No market: the words and why. Held: "license needed", with the zone, the auction and
 * the rule of conversion on hover. */
function CapTd({ r, x }: { r: Row; x: SitingInputs }) {
  const c = capacityCell(SITING_FILES, r, x);
  if ("zero" in c) return <Words words="no capacity market" why={`${c.zero} Counted as zero in the all-in figure.`} />;
  if ("why" in c) return <Words words={c.words} why={c.why} />;
  const h = c.held;
  return <Held table={h.table} why={`The latest cleared capacity price for ${h.entity.split(":")[1]}${h.own ? "" : " (the system-wide price: the newest auction priced no zone of this row's own)"}: ${h.market.auction}, delivery ${periodWords(h.market.period_start, h.market.period_end)}, ${h.market.unit} (${h.table}, internal: ${h.market.license}). ${CAPACITY_RULE} Computed where the table is held; drawn as "license needed".`} />;
}

/** Session 705: the time to connect: the grid's median months from queue entry to operation (Berkeley Lab), and the
 * large-load path under it: the newest decided rule, ERCOT's approved large loads, and the measured waits (held). */
function ConnectTd({ r }: { r: Row }) {
  const c = connectCell(SITING_FILES, r);
  const g = c.gen;
  const ruleTip = c.rule ? `The newest decided large-load rule held for ${GRID_NAMES[r.grid]}: ${c.rule.regulator}, docket ${c.rule.docket}, ${c.rule.date} (${c.rule.topic}). ${c.rule.read ?? ""} ${c.rule.url}${r.grid === "ercot" ? " No faster path for a controllable load is stated in the rules held." : ""}` : c.ruleWhy;
  return (
    <span className="inline-block text-right">
      {"median" in g && g.median !== null
        ? <span className="whitespace-nowrap"><Fig check={`allgrids|connect|${r.id}`} v={g.median}
            tip={`Generation in ${GRID_NAMES[r.grid]}: the median months from queue entry to commercial operation of the ${g.n} requests that came online from ${g.from} to ${g.to} (${SITING_FILES.connect?.table ?? "interconnection_durations"}, from Berkeley Lab's Queued Up, ${g.vintage}); a quarter took under ${g.p25?.toFixed(0)} months, a quarter over ${g.p75?.toFixed(0)}. A generator's wait, not a load's: loads are not in this file.`} /> mo</span>
        : <Words words="not held" why={"why" in g ? g.why : ""} />}
      <span className="block text-xs" data-connect-load="1">
        load: {c.rule ? <Tp tip={ruleTip}>rule {c.rule.date.slice(0, 7)}</Tp> : <Words words="no rule held" why={ruleTip} />}
        {c.status ? <>, <Tp dotted={false} tip={`ERCOT's large loads approved to energize, MW, its report of ${c.status.day} (${c.status.document}; ercot_large_load_status): approved to connect, not a wait.`}><Num check={`allgrids|llapproved|${r.id}`} raw={c.status.approved}>{c.status.approved.toLocaleString("en-US")}</Num> MW approved</Tp></> : null}
        {"held" in c.wait ? <>, wait <Held table="large_load_waits" why={c.wait.held} /></> : null}
      </span>
    </span>
  );
}

/** Session 706: headroom: the grid's demand growth (percent), generation under construction due in the next twelve
 * months (MW), and installed capacity against the last year's peak where the grid is whole states. */
function HeadroomTd({ r }: { r: Row }) {
  const g = demandGrowth(SITING_FILES.demand, r.grid), h = SITING_FILES.headroom, pl = h?.planned[r.grid], c = capacityOverPeak(SITING_FILES.demand, h, r.grid);
  return (
    <span className="inline-block text-right">
      {"pct" in g
        ? <span className="whitespace-nowrap"><Tp
            tip={`${GRID_NAMES[r.grid]}'s mean demand (EIA-930, ${g.ba}), ${monthWords(g.from)} to ${monthWords(g.to)}, ${Math.round(g.mw).toLocaleString("en-US")} MW, against the twelve months before, ${Math.round(g.before).toLocaleString("en-US")} MW: each month's mean weighted by its hours (eia930_demand_growth, "Your load"'s file data/demand_growth.json). The grid's own balancing authority, not the row's zone: sub-region demand is not in the tab's files. Weather is not removed.`}>
            {g.pct > 0 ? "+" : ""}<Num check={`allgrids|demand|${r.id}`} raw={g.pct}>{two(g.pct)}</Num></Tp> %</span>
        : <Words words="not held" why={g.why} />}
      <span className="block text-xs" data-headroom-planned="1">
        {pl && h ? <Tp dotted={false} tip={`Generators under construction (EIA-860M status U, V or TS) in ${GRID_NAMES[r.grid]} due to operate from ${h.from} to ${h.to}, the twelve months after the table's vintage (${h.vintage}): ${pl.construction_n} generators. Approvals received, not under construction: ${Math.round(pl.approved_mw).toLocaleString("en-US")} MW; planned, approvals pending or not started: ${Math.round(pl.other_mw).toLocaleString("en-US")} MW. EIA-860M records no interconnection agreement; construction is the nearest it states (eia860m_planned_generators).`}><Num check={`allgrids|planned|${r.id}`} raw={pl.construction_mw}>{Math.round(pl.construction_mw).toLocaleString("en-US")}</Num> MW coming</Tp> : <Words words="no plan held" why={`No planned generator of ${GRID_NAMES[r.grid]} is in eia860m_planned_generators.`} />}
        {"pct" in c ? <>, <Tp dotted={false} tip={c.table === "grid_peak_vs_capacity"
          ? `${GRID_NAMES[r.grid]}'s operating generators' net summer capacity at the end of ${c.year}, ${Math.round(c.mw).toLocaleString("en-US")} MW (solar ${Math.round(c.parts?.solar ?? 0).toLocaleString("en-US")}, wind ${Math.round(c.parts?.wind ?? 0).toLocaleString("en-US")}, storage ${Math.round(c.parts?.storage ?? 0).toLocaleString("en-US")}, at their summer ratings), against its peak hour of ${c.peakYear}, ${Math.round(c.peak).toLocaleString("en-US")} MW: grid_peak_vs_capacity (the data machine's, by each generator's balancing authority, EIA-860M and EIA-930). Not a reserve margin: no imports, outages or derates, and solar and wind at their ratings.`
          : `Installed net summer capacity of ${c.states.join(", ")} in ${c.year} (eia_state_capacity_annual), ${Math.round(c.mw).toLocaleString("en-US")} MW, over ${GRID_NAMES[r.grid]}'s peak demand of ${c.peakYear}, ${Math.round(c.peak).toLocaleString("en-US")} MW. Not a reserve margin.`}>capacity <Num check={`allgrids|capratio|${r.id}`} raw={c.pct}>{Math.round(c.pct).toLocaleString("en-US")}</Num>% above peak</Tp></> : null}
      </span>
    </span>
  );
}

/** Session 707: carbon: the eGRID subregion's CO2 rate (kg, lb under it); for a profile that runs in some hours, the
 * grid's hourly intensity over the hours it runs, where held, as the figure, the annual rate under it. */
function CarbonTd({ r, x }: { r: Row; x: SitingInputs }) {
  const c = carbonCell(SITING_DC, SITING_FILES, r, x);
  if ("why" in c) return <Words words={c.words} why={c.why} />;
  const k = profileKey(x), cf = SITING_FILES.carbon!;
  const annualTip = `The ${c.sub.words}: its ${c.plants.toLocaleString("en-US")} plants' CO2 over their net generation in ${c.year} (egrid_power_plants, ${cf.vintage}), ${two(c.kg)} kg (${two(c.lb)} lb) per MWh generated, annual.`;
  return (
    <span className="inline-block text-right">
      {c.hourly
        ? <><span className="whitespace-nowrap"><Fig check={`allgrids|carbonh|${r.id}|${k}`} v={c.hourly.kg} tip={`The grid's hourly intensity (carbon_intensity_hourly, ${cf.hourly_variable}, kg CO2 per MWh consumed), weighted by the load over the ${c.hourly.hours.toLocaleString("en-US")} of the ${c.hourly.of.toLocaleString("en-US")} hours it runs where both are held: hourly, the grid's balancing authority, not the subregion. ${annualTip}`} /> kg</span>
            <span className="block text-xs" data-carbon-annual="1">annual <Tp dotted={false} tip={annualTip}><Num check={`allgrids|carbon|${r.id}`} raw={c.kg}>{two(c.kg)}</Num></Tp></span></>
        : <><span className="whitespace-nowrap"><Fig check={`allgrids|carbon|${r.id}`} v={c.kg} tip={`${annualTip}${c.hourlyWhy ? ` ${c.hourlyWhy}` : ""}`} /> kg</span>
            <span className="block text-xs" data-carbon-lb="1"><Tp dotted={false} tip={annualTip}><Num check={`allgrids|carbonlb|${r.id}`} raw={c.lb}>{two(c.lb)}</Num></Tp> lb</span></>}
    </span>
  );
}

/** Session 708: the utility: the largest seller to industry in the row's state inside the grid, its industrial revenue
 * per MWh and its industrial sales growth, the newest year held (EIA-861). */
function UtilityTd({ r }: { r: Row }) {
  const c = utilityCell(SITING_FILES, r);
  if ("why" in c) return <Words words={c.words} why={c.why} />;
  if (c.county) return <CountyUtilityTd r={r} c={c} />;
  const u = c.u!;
  const tip = `${u.utility} (EIA utility ${u.number}), the largest of ${u.sellers} sellers to industry in ${c.state} inside ${GRID_NAMES[r.grid]} (balancing authority ${c.ba}) in ${c.year}: ${Math.round(u.sales_mwh).toLocaleString("en-US")} MWh to industry for USD ${Math.round(u.revenue_usd).toLocaleString("en-US")} (eia861_utility_sales, ${u.service === "Energy" ? "energy only: the wires utility bills delivery" : "bundled: energy and delivery"}). This row's name is not a place, so no county's service territory can be read for it: this is the state's largest seller, which the data machine found is not the county's utility in 4 of 7 hub counties (session 681).`;
  return (
    <span className="inline-block text-right">
      <Tp tip={tip} className="block max-w-[11rem] text-xs" dotted={false} data={{ "util-name": "1" }}><span className="block truncate">{u.utility}</span></Tp>
      <span className="whitespace-nowrap"><Fig check={`allgrids|utilrev|${r.id}`} v={c.rev} tip={tip} /></span>
      {c.growth !== null ? <span className="block text-xs" data-util-growth="1"><Tp dotted={false} tip={`Industrial sales ${c.year} over ${c.prior}: ${Math.round(u.sales_mwh).toLocaleString("en-US")} against ${Math.round(u.sales_prior_mwh ?? 0).toLocaleString("en-US")} MWh.`}>{c.growth > 0 ? "+" : ""}<Num check={`allgrids|utilgrowth|${r.id}`} raw={c.growth}>{two(c.growth)}</Num></Tp> %</span> : null}
    </span>
  );
}

/** Session 718: a row whose name is a place: its county's utilities (EIA-861's service territories), the first named, and
 * the largest seller to industry among them inside the row's grid, its revenue per MWh and growth. */
function CountyUtilityTd({ r, c }: { r: Row; c: Extract<ReturnType<typeof utilityCell>, { county: object }> }) {
  const cu = c.county!, u = c.u;
  const others = cu.utilities.filter((x) => x.name !== u?.utility);
  const names = cu.utilities.map((x) => `${x.name}${x.ba.length ? ` (${x.ba.join(", ")})` : " (no sales row)"}`).join("; ");
  const where = `${cu.county} County, ${cu.state}, a county this row's name places it in`;
  const tip = u
    ? `${where}: EIA-861's service territories (utility_service_territories, ${cu.territory_year}) list ${cu.utilities.length}: ${names}. Of those that bill customers inside ${GRID_NAMES[r.grid]} (balancing authority ${cu.ba}), ${u.utility} sold most to industry in the state in ${c.year}: ${Math.round(u.sales_mwh).toLocaleString("en-US")} MWh for USD ${Math.round(u.revenue_usd).toLocaleString("en-US")} (${u.service === "Delivery" ? "delivery only: the charge for the wires, not the energy" : "bundled: energy and delivery"}; eia861_utility_sales). A utility with no sales row (a wires company that reports none) is listed and not priced.`
    : `${where}: EIA-861's service territories list ${names}. None of them bills industry inside ${GRID_NAMES[r.grid]} in eia861_utility_sales, so no revenue per MWh is drawn.`;
  return (
    <span className="inline-block text-right">
      <Tp tip={tip} className="block max-w-[11rem] text-xs" dotted={false} data={{ "util-name": "1" }}><span className="block truncate">{u?.utility ?? cu.utilities[0]?.name ?? cu.county}{others.length ? ` and ${others.length} more` : ""}</span></Tp>
      {u && c.rev !== null ? <span className="whitespace-nowrap"><Fig check={`allgrids|utilrev|${r.id}`} v={c.rev} tip={tip} /></span> : <Words words="no sales row" why={tip} />}
      {u && c.growth !== null ? <span className="block text-xs" data-util-growth="1"><Tp dotted={false} tip={`Industrial sales ${c.year} over ${c.prior}: ${Math.round(u.sales_mwh).toLocaleString("en-US")} against ${Math.round(u.sales_prior_mwh ?? 0).toLocaleString("en-US")} MWh.`}>{c.growth > 0 ? "+" : ""}<Num check={`allgrids|utilgrowth|${r.id}`} raw={c.growth}>{two(c.growth)}</Num></Tp> %</span> : null}
    </span>
  );
}

function RowHead({ r }: { r: Row }) {
  return (
    <th scope="row" className="px-3 py-1.5 text-left font-normal" data-row={r.id}>
      <span className="text-xs text-muted">{GRID_NAMES[r.grid]}</span>{" "}
      {r.blank ? <Tp tip={r.blank.why}>{r.label}</Tp> : r.label}
    </th>
  );
}

/** Session 709: what every ERCOT node shares, drawn once above the node table: the four-peak charge (paid on the hub's
 * hours), no capacity market, the grid's time to connect, headroom and carbon, and what the node tables do not hold. */
/** Session 717: what every node shares, as one sentence: the walk of the lab's path found the cells drawn here as they
 * are in the table (each a block of its own) broke the line into pieces. Each figure keeps its key and its tip. */
function SharedLine({ hub, x }: { hub: Row; x: SitingInputs }) {
  const k = profileKey(x);
  const c = cpCharge(SITING_DC, SITING_FILES, hub, x), con = connectCell(SITING_FILES, hub), g = demandGrowth(SITING_FILES.demand, hub.grid), cb = carbonCell(SITING_DC, SITING_FILES, hub, x);
  return (
    <p>
      Every node below is in ERCOT, and shares these, drawn once: the four-peak charge, paid on {NODE_HUB}&apos;s hours,{" "}
      {"why" in c ? <Words words={c.words} why={c.why} /> : <>USD {c.own === null ? <Words words="not held" why="The price of an interval's hour is not held." /> : <Fig check={`allgrids|tx|${hub.id}|${k}`} v={c.own} tip={`This load's charge: it ran in ${Math.round((c.share ?? 0) * 4)} of the four intervals of ${c.year}, at the Commission's ${c.rate.year} rate.`} />} per MWh for this load (firm <Fig check={`allgrids|tx|${hub.id}|firm|${k}`} v={c.firm} tip="On in all four intervals." />{c.curtailing !== null ? <>, off at the peaks <Fig check={`allgrids|tx|${hub.id}|curtailing|${k}`} v={c.curtailing} tip="Off in the four intervals' hours, computed from its weights." /></> : null})</>};
      {" "}no capacity market (<Words words="why" why="ERCOT is an energy-only market: it has no capacity market and no capacity charge." />);
      {" "}generators took a median of {"median" in con.gen && con.gen.median !== null ? <Fig check={`allgrids|connect|${hub.id}`} v={con.gen.median} tip={`From queue entry to operation, ${con.gen.n} requests online from ${con.gen.from} to ${con.gen.to} (lbnl_interconnection_queue).`} /> : <Words words="not held" why={"why" in con.gen ? con.gen.why : ""} />} months to connect;
      {" "}demand grew {"pct" in g ? <>{g.pct > 0 ? "+" : ""}<Fig check={`allgrids|demand|${hub.id}`} v={g.pct} tip={`ERCOT's mean demand (EIA-930, ERCO), ${monthWords(g.from)} to ${monthWords(g.to)}, over the twelve months before.`} /> percent</> : <Words words="not held" why={g.why} />} on the year;
      {" "}carbon {"kg" in cb ? <><Fig check={`allgrids|carbon|${hub.id}`} v={cb.kg} tip={`eGRID subregion ERCT, ${cb.year}: the plants' CO2 over their net generation.`} /> kg CO2 per MWh</> : <Words words={cb.words} why={cb.why} />}.
    </p>
  );
}

function NodeShared({ x }: { x: SitingInputs }) {
  const hub = hubRows(SITING_FILES.index).find((r) => r.id === `ercot:${NODE_HUB}`)!;
  return (
    <div className="mb-3 max-w-4xl text-sm" data-node-shared="1">
      <SharedLine hub={hub} x={x} />
      <p className="mt-1">
        Not held for any node: its load zone, its settlement hub and its wires utility (TSP). node_basis_daily sets every node against {NODE_HUB} and names no zone or utility; <Words words="not held" why="ERCOT publishes each settlement point's zone and hub in its settlement point mapping, and each node's TSP in its resource registration; neither is a table of the warehouse yet (docs/reviews/siting-gaps.md)." />.
      </p>
    </div>
  );
}

const usdWhole = (v: number) => Math.round(v).toLocaleString("en-US");
/** Session 710: A and B side by side, in "Your load"'s form (two columns, B less A, no verdict): every column's figure
 * where held, the load's year all-in in USD and its MWh, and the months to connect. */
function AbPanel({ x }: { x: SitingInputs }) {
  const ra = x.a ? rowOf(SITING_FILES, x.a) : undefined, rb = x.b ? rowOf(SITING_FILES, x.b) : undefined;
  if (!ra && !rb) return null;
  const k = profileKey(x), yk = yearKey(x);
  const cell = (r: Row | undefined, c: (typeof COLUMNS)[number]) => {
    if (!r) return "";
    const v = columnValue(SITING_DC, SITING_FILES, r, x, c.id);
    return v === null ? <Words words="not held" why="Not held for this row, or held under a license and drawn in its column as such: see the row in the table." /> : <Num check={`allgrids|col|${c.id}|${r.id}|${k}`} raw={v}>{two(v)}</Num>;
  };
  const diff = (c: (typeof COLUMNS)[number]) => {
    if (!ra || !rb) return "";
    const va = columnValue(SITING_DC, SITING_FILES, ra, x, c.id), vb = columnValue(SITING_DC, SITING_FILES, rb, x, c.id);
    return va === null || vb === null ? "" : <>{vb - va > 0 ? "+" : ""}<Num check={`allgrids|diff|${c.id}|${ra.id}|${rb.id}|${k}`} raw={vb - va}>{two(vb - va)}</Num></>;
  };
  const year = (r: Row | undefined) => (r ? yearOf(SITING_DC, SITING_FILES, r, x) : null);
  const ya = year(ra), yb = year(rb);
  const yr = (r: Row | undefined, y: ReturnType<typeof year>) => (!r ? "" : y ? <Num check={`allgrids|year|${r.id}|${yk}`} raw={y.usd}>{usdWhole(y.usd)}</Num> : <Words words="not held" why="The all-in figure is not drawn for this row: not every cost part is held." />);
  const mwh = (r: Row | undefined, y: ReturnType<typeof year>) => (!r || !y ? "" : <Num check={`allgrids|mwh|${r.id}|${yk}`} raw={y.mwh}>{usdWhole(y.mwh)}</Num>);
  const name = (r: Row | undefined) => (r ? `${GRID_NAMES[r.grid]} ${r.region}` : "none chosen");
  const th = "px-3 py-1.5 text-right font-normal";
  return (
    <section className="mb-5" aria-label="A and B" data-allgrids-abpanel="1">
      <h3 className="mb-2 font-serif text-lg">A and B, side by side</h3>
      <div className="overflow-x-auto" role="region" aria-label="A and B, the table" tabIndex={0}>
        <table className="w-full border-collapse text-sm tabular-nums" style={{ minWidth: 520 }}>
          <thead><tr className="bg-accent text-white"><th scope="col" className="px-3 py-1.5 text-left font-normal">USD per MWh unless said</th><th scope="col" className={th}>A: {name(ra)}</th><th scope="col" className={th}>B: {name(rb)}</th><th scope="col" className={th}>B less A</th></tr></thead>
          <tbody>
            {COLUMNS.map((c) => (
              <tr key={c.id} className="border-b border-rule"><th scope="row" className="px-3 py-1.5 text-left font-normal">{c.head} <span className="text-xs text-muted">{c.unit === "USD per MWh" ? "" : c.unit}</span></th>
                <td className="px-3 py-1.5 text-right">{cell(ra, c)}</td><td className="px-3 py-1.5 text-right">{cell(rb, c)}</td><td className="px-3 py-1.5 text-right">{diff(c)}</td></tr>
            ))}
            <tr className="border-b border-rule bg-paper"><th scope="row" className="px-3 py-1.5 text-left font-normal">A year all-in, USD, {x.mw.toLocaleString("en-US")} MW</th><td className="px-3 py-1.5 text-right">{yr(ra, ya)}</td><td className="px-3 py-1.5 text-right">{yr(rb, yb)}</td><td className="px-3 py-1.5 text-right">{ya && yb && ra && rb ? <>{yb.usd - ya.usd > 0 ? "+" : ""}<Num check={`allgrids|yeardiff|${ra.id}|${rb.id}|${yk}`} raw={yb.usd - ya.usd}>{usdWhole(yb.usd - ya.usd)}</Num></> : ""}</td></tr>
            <tr className="border-b border-rule"><th scope="row" className="px-3 py-1.5 text-left font-normal">Energy used a year, MWh</th><td className="px-3 py-1.5 text-right">{mwh(ra, ya)}</td><td className="px-3 py-1.5 text-right">{mwh(rb, yb)}</td><td /></tr>
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs" data-ab-note="1">Each figure is the row&apos;s own in the table below, under the same load. Months to connect are the grid&apos;s generators&apos; (the column &quot;Time to connect&quot;). The year all-in is the all-in figure times the energy the load uses in a year: its draw while running times the hours it runs.</p>
    </section>
  );
}
/** Session 710: the one headline line A drives, every figure a key, drawn only where held. */
function Headline({ x }: { x: SitingInputs }) {
  const r = x.a ? rowOf(SITING_FILES, x.a) : undefined;
  if (!r) return <p className="mb-3 max-w-3xl text-sm" data-allgrids-headline="0">Choose A and B under &quot;A and B, side by side&quot; in the box to set two rows beside each other; A sets this line.</p>;
  const y = yearOf(SITING_DC, SITING_FILES, r, x), c = connectCell(SITING_FILES, r), p = PROFILES[x.profile];
  return (
    <p className="mb-3 max-w-3xl font-serif text-xl leading-snug" data-allgrids-headline="1">
      A {p.label.toLowerCase()} load of {x.mw.toLocaleString("en-US")} MW at {GRID_NAMES[r.grid]} {r.region}
      {y ? <> pays USD <Num check={`allgrids|allin|${r.id}|${profileKey(x)}`} raw={y.allin}>{two(y.allin)}</Num> per MWh all-in, USD <Num check={`allgrids|year|${r.id}|${yearKey(x)}`} raw={y.usd}>{usdWhole(y.usd)}</Num> a year</> : <> has no all-in figure (not every cost part is held)</>}
      {"median" in c.gen && c.gen.median !== null ? <>; generators there took a median of <Num check={`allgrids|connect|${r.id}`} raw={c.gen.median}>{two(c.gen.median)}</Num> months to connect</> : null}.
    </p>
  );
}

/** Session 711: a node's panel: its basis to the hub over the year (the 10th, 50th and 90th percentile of its days, and
 * each month's mean in the shared chart), its four-peak exposure, and what is not held about its place (county, planned
 * generation near it, transmission projects). */
function NodePanel({ id, x }: { id: string; x: SitingInputs }) {
  const n = NODES.nodes.find((k) => `ercot:${k.id}` === id);
  if (!n) return null;
  const months = Object.entries(n.dam_basis ?? {}).sort(([a], [b]) => a.localeCompare(b));
  const close = `?${new URLSearchParams({ view: "allgrids", rows: "nodes" }).toString()}`;
  return (
    <section className="mb-4 border border-rule bg-paper px-4 py-3 text-sm" aria-label={`Node ${n.id}`} data-node-panel={id}>
      <h3 className="font-serif text-lg">{n.id} <span className="text-sm">({n.cls}{n.types ? `, ERCOT's resource types ${n.types}` : ""})</span> <a href={`/cost-of-power${close}`} className="ml-2 text-xs underline">Close</a>
        {/* session 724: a node as A or B of the hub table's panel, from the page (the trader's walk, step 8) */}
        <a href={sitingHref(x, { rows: "hubs", a: id })} className="ml-3 text-xs underline" data-node-set="a">Set as A</a>
        <a href={sitingHref(x, { rows: "hubs", b: id })} className="ml-2 text-xs underline" data-node-set="b">Set as B</a></h3>
      {n.pct ? (
        <p className="mt-1">
          Its daily day-ahead basis to {NODE_HUB}, {NODES.pct_from} to {NODES.pct_to} ({n.pct[3]} days held, node_basis_daily): one day in ten at or below USD{" "}
          <Num check={`allgrids|nodepct|${id}|10`} raw={n.pct[0]}>{two(n.pct[0])}</Num>, half at or below <Num check={`allgrids|nodepct|${id}|50`} raw={n.pct[1]}>{two(n.pct[1])}</Num>, nine in ten at or below <Num check={`allgrids|nodepct|${id}|90`} raw={n.pct[2]}>{two(n.pct[2])}</Num> per MWh.
        </p>
      ) : <p className="mt-1"><Words words="not held" why="No day of day-ahead basis is held for this node in the twelve months." /></p>}
      {months.length >= 2 ? (
        <div className="mt-2" data-node-chart="1">
          <span className="text-xs">Each month&apos;s mean daily basis, USD per MWh, {months[0][0]} to {months.at(-1)![0]}:</span>
          <InlineSpark values={months.map(([m, v]) => ({ t: `${m}-01`, v: v[0] }))} label={`${n.id}: mean daily day-ahead basis to ${NODE_HUB} by month`} width={320} height={48} />
        </div>
      ) : null}
      <ul className="mt-2 list-disc pl-5">
        <li>Four peaks: as every node, the charge on {NODE_HUB}&apos;s hours, above the list. Its own price in the four intervals of summer 2025 is <Words words="not held" why="node_basis_daily begins on 1 October 2025, after the summer; and it holds days, not the 15-minute intervals." />.</li>
        <li>Its county, and so the planned generation near it (eia860m_planned_generators, by county): <Words words="not held" why="No table of the warehouse places an ERCOT settlement point in a county; ERCOT's resource registration does, and is not pulled (docs/reviews/siting-gaps.md)." />.</li>
        <li>Transmission projects in its county: <Words words="not held" why="texas_transmission_matrix holds each wires utility's transmission cost of service and four-peak charge, not projects by county, and it is internal; no table of projects by county is held." />.</li>
      </ul>
    </section>
  );
}

export function AllGridsView({ q }: { q: Record<string, string | undefined> }) {
  const x = sitingInputs(q);
  const hubs = hubRows(SITING_FILES.index), nodes = nodeRows(NODES);
  const p = PROFILES[x.profile];
  const shown = x.rows === "hubs" ? screen(SITING_DC, SITING_FILES, hubs, x) : [];
  // session 717: the column the table is sorted by is drawn first, beside the rows' names (the walk found it off the
  // screen to the right on a laptop); the order of the others is kept
  const cols = x.sort === "name" ? COLUMNS : [...COLUMNS.filter((c) => c.id === x.sort), ...COLUMNS.filter((c) => c.id !== x.sort)];
  return (
    <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]" data-no-usage="1" data-allgrids="1">
      <aside>
        <InputPanel title="Your load">
          <AllGridsForm x={x} rows={[...hubs.map((r) => ({ id: r.id, label: `${GRID_NAMES[r.grid]} ${r.label}` })),
            // session 724: a node set as A or B stays in the lists, so Show keeps it
            ...[...new Set([x.a, x.b])].filter((v): v is string => !!v && nodes.some((r) => r.id === v)).map((v) => ({ id: v, label: `ERCOT ${v.split(":")[1]} (node)` }))]} />
        </InputPanel>
      </aside>
      <div className="min-w-0">
        <p className="mb-3 max-w-3xl text-sm" data-allgrids-count={x.rows}>
          {x.rows === "nodes"
            ? <>Every ERCOT node of node_basis_daily that is neither a hub nor a load zone: <Num check="allgrids|rows|nodes" raw={nodes.length}>{nodes.length.toLocaleString("en-US")}</Num> nodes, from {NODES.first} to {NODES.last}.</>
            : <>Every hub and load zone the page&apos;s price files hold, and the grids they do not price: <Num check="allgrids|rows|hubs" raw={hubs.length}>{hubs.length.toLocaleString("en-US")}</Num> rows.</>}
          {" "}{/^[aeiou]/i.test(p.label) ? "An" : "A"} {p.label.toLowerCase()} load of {x.mw.toLocaleString("en-US")} MW at a load factor of {x.lf.toFixed(2)}, {CURTAIL_WORDS[p.curtail]}{x.strike !== null ? ` (USD ${x.strike.toLocaleString("en-US")} per MWh)` : ""}.
        </p>
        <RowToggle x={x} hubs={hubs.length} nodes={nodes.length} />
        {x.rows === "hubs" ? <><Headline x={x} /><AbPanel x={x} /></> : null}
        {x.rows === "hubs" ? (
          <p className="mb-2 text-sm" role="status" data-allgrids-sort={`${x.sort}|${x.dir}`}>
            Sorted by {SORT_WORDS[x.sort]}{x.sort === "name" ? (x.dir === "asc" ? ", A to Z" : ", Z to A") : x.dir === "desc" ? ", largest first; a row with no figure, or one held under a license, last" : ", smallest first; a row with no figure, or one held under a license, last"}.
            {" "}{shown.length} of {hubs.length} rows shown{x.grids.length ? `, in ${x.grids.map((g) => GRID_NAMES[g]).join(", ")}` : ""}{x.kind !== "all" ? `, ${x.kind === "zone" ? "load zones" : "hubs"} only` : ""}{x.band ? `, energy from USD ${x.band[0]} to ${x.band[1]} per MWh` : ""}{x.held ? ", every cost part held" : ""}. The order is the column&apos;s, not a ranking of sites.
          </p>
        ) : null}
        {x.rows === "nodes" ? (
          <>
            <NodeShared x={x} />
            {q.node ? <NodePanel id={q.node} x={x} /> : null}
            <AllGridsNodes rows={nodeTable(SITING_DC, SITING_FILES, x)} pkey={profileKey(x)} datacenter={x.profile === "datacenter"} open={q.node ?? null}
              short={shortMonthsWords(nodeShortMonths(NODES))} find={q.nq ?? ""}
              csvHead={[`Energy Research Warehouse (ERW): the ERCOT nodes of the All grids tab of /cost-of-power ("What a datacenter pays"), ${sitingHref(x, { rows: "nodes" })}`,
                `${/^[aeiou]/i.test(p.label) ? "An" : "A"} ${p.label.toLowerCase()} load of ${x.mw} MW at a load factor of ${x.lf.toFixed(2)}; energy is ${NODE_HUB}'s day-ahead price over its twelve whole months plus the node's mean daily basis (node_basis_daily, ${NODES.first} to ${NODES.last}); USD per MWh`,
                "Method: docs/methods/siting.md. Downloaded from the page: the rows shown, in the page's own figures."]}
              sort={(NODE_SORTS as readonly string[]).includes(q.nsort ?? "") ? (q.nsort as NodeSort) : "node"} dir={q.ndir === "desc" ? "desc" : "asc"} />
          </>
        ) : (
        <div className="overflow-x-auto" role="region" aria-label="All grids" tabIndex={0} data-allgrids-table="1">
          <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 960 }}>
            <caption className="sr-only">What a {p.label.toLowerCase()} load pays, when it connects and how clean the power is, at every hub and zone</caption>
            <thead>
              <tr className="bg-accent text-white">
                <th scope="col" className="px-3 py-1.5 font-normal">Grid and region</th>
                {cols.map((c) => (
                  <th key={c.id} scope="col" className="px-3 py-1.5 text-right font-normal" data-col={c.id}>
                    <Tp tip={`${c.tip} ${c.unit}.`} className="border-white/70">{c.head}</Tp>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shown.map((r) => (
                <tr key={r.id} className="border-b border-rule" data-allgrids-row={r.id}>
                  <RowHead r={r} />
                  {cols.map((c, ci) => <td key={c.id} className="px-3 py-1.5 text-right" data-cell={c.id} data-opens={ci < 4 ? "right" : undefined}>{c.id === "energy" ? (x.profile === "datacenter" ? <EnergyTd r={r} e={energyCell(SITING_DC, SITING_FILES, r)} /> : <ProfileTd r={r} x={x} />)
                    : c.id === "transmission" ? <TxTd r={r} x={x} /> : c.id === "capacity" ? <CapTd r={r} x={x} /> : c.id === "connect" ? <ConnectTd r={r} /> : c.id === "headroom" ? <HeadroomTd r={r} /> : c.id === "carbon" ? <CarbonTd r={r} x={x} /> : c.id === "utility" ? <UtilityTd r={r} /> : c.id === "allin" ? <AllInTd r={r} x={x} /> : null}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
        <p className="mt-2 max-w-3xl text-xs" data-allgrids-method="1">
          One row a hub, zone or node; one column a question. The columns are filled one session at a time from the warehouse&apos;s own tables, each by the function that computes it for &quot;Your load&quot;.
          {" "}<Link href="/data/methods/siting">Method note</Link>.
        </p>
      </div>
    </div>
  );
}
