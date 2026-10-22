import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { InlineSpark } from "@/components/InlineSpark";
import { InputPanel } from "@/components/tool/ToolPage";
import type { ReactNode } from "react";
import { CAPACITY_RULE, COLUMNS, CURTAIL_WORDS, GRID_NAMES, NODE_HUB, PROFILES, allInCell, capacityCell, capacityOverPeak, connectCell, cpCharge, demandGrowth, energyCell, hubRows, nodeRows, profileCell, profileKey, sitingHref, sitingInputs, type EnergyCell, type Row, type SitingInputs, type Twelve } from "@/lib/siting";
import { CP, NODES, SITING_DC, SITING_FILES } from "@/lib/sitingdata";
import { AllGridsForm } from "./AllGridsForm";

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

/** A cell the warehouse cannot fill: short words in ink, the reason on hover and on focus (no visible grey text). */
function Words({ words, why }: { words: string; why: string }) {
  return <span className={tipCls} title={why} tabIndex={0} data-cell-words="1">{words}</span>;
}
/** One figure with its hover: the reason, the window and its source. */
function Fig({ check, v, tip, children }: { check: string; v: number; tip: string; children?: ReactNode }) {
  return (
    <span className={`group relative inline-block ${tipCls}`} title={tip} tabIndex={0}>
      <Num check={check} raw={v}>{two(v)}</Num>
      {children}
    </span>
  );
}
/** Session 701: the twelve months of a figure, drawn on hover and on focus (the shared inline chart, components/InlineSpark). */
function Spark({ t, label }: { t: Twelve; label: string }) {
  return (
    <span className="pointer-events-none absolute right-0 top-full z-10 hidden border border-rule bg-white p-1 group-hover:block group-focus:block" data-spark="1">
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
      {p.curtail !== "none" && p.curtail !== "interruptible" ? <span className="ml-2 text-xs" data-lost="1">off <span title={`Hours of the ${t.held.toLocaleString("en-US")} held the load was off`}><Num check={`allgrids|lost|${r.id}|${k}`} raw={t.lost}>{t.lost.toLocaleString("en-US")}</Num></span> h</span> : null}
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
  return <span className={tipCls} title={why} tabIndex={0} data-license-held={table}>license needed</span>;
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
            tip={`Generation in ${GRID_NAMES[r.grid]}: the median months from queue entry to commercial operation of the ${g.n} requests that came online from ${g.from} to ${g.to} (lbnl_interconnection_queue, Berkeley Lab's Queued Up, ${g.vintage}); a quarter took under ${g.p25?.toFixed(0)} months, a quarter over ${g.p75?.toFixed(0)}. A generator's wait, not a load's: loads are not in this file.`} /> mo</span>
        : <Words words="not held" why={"why" in g ? g.why : ""} />}
      <span className="block text-xs" data-connect-load="1">
        load: {c.rule ? <span className={tipCls} title={ruleTip} tabIndex={0}>rule {c.rule.date.slice(0, 7)}</span> : <Words words="no rule held" why={ruleTip} />}
        {c.status ? <>, <span title={`ERCOT's large loads approved to energize, MW, its report of ${c.status.day} (${c.status.document}; ercot_large_load_status): approved to connect, not a wait.`}><Num check={`allgrids|llapproved|${r.id}`} raw={c.status.approved}>{c.status.approved.toLocaleString("en-US")}</Num> MW approved</span></> : null}
        {"held" in c.wait ? <>, wait <Held table="large_load_waits" why={c.wait.held} /></> : null}
      </span>
    </span>
  );
}

const signed2 = (v: number) => `${v > 0 ? "+" : ""}${two(v)}`;
/** Session 706: headroom: the grid's demand growth (percent), generation under construction due in the next twelve
 * months (MW), and installed capacity against the last year's peak where the grid is whole states. */
function HeadroomTd({ r }: { r: Row }) {
  const g = demandGrowth(SITING_FILES.demand, r.grid), h = SITING_FILES.headroom, pl = h?.planned[r.grid], c = capacityOverPeak(SITING_FILES.demand, h, r.grid);
  return (
    <span className="inline-block text-right">
      {"pct" in g
        ? <span className="whitespace-nowrap"><span className={`group relative inline-block ${tipCls}`} tabIndex={0}
            title={`${GRID_NAMES[r.grid]}'s mean demand (EIA-930, ${g.ba}), ${monthWords(g.from)} to ${monthWords(g.to)}, ${Math.round(g.mw).toLocaleString("en-US")} MW, against the twelve months before, ${Math.round(g.before).toLocaleString("en-US")} MW: each month's mean weighted by its hours (eia930_demand_growth, "Your load"'s file data/demand_growth.json). The grid's own balancing authority, not the row's zone: sub-region demand is not in the tab's files. Weather is not removed.`}>
            <Num check={`allgrids|demand|${r.id}`} raw={g.pct}>{signed2(g.pct)}</Num></span> %</span>
        : <Words words="not held" why={g.why} />}
      <span className="block text-xs" data-headroom-planned="1">
        {pl && h ? <span title={`Generators under construction (EIA-860M status U, V or TS) in ${GRID_NAMES[r.grid]} due to operate from ${h.from} to ${h.to}, the twelve months after the table's vintage (${h.vintage}): ${pl.construction_n} generators. Approvals received, not under construction: ${Math.round(pl.approved_mw).toLocaleString("en-US")} MW; planned, approvals pending or not started: ${Math.round(pl.other_mw).toLocaleString("en-US")} MW. EIA-860M records no interconnection agreement; construction is the nearest it states (eia860m_planned_generators).`}><Num check={`allgrids|planned|${r.id}`} raw={pl.construction_mw}>{Math.round(pl.construction_mw).toLocaleString("en-US")}</Num> MW coming</span> : <Words words="no plan held" why={`No planned generator of ${GRID_NAMES[r.grid]} is in eia860m_planned_generators.`} />}
        {"pct" in c ? <>, <span title={`Installed net summer capacity of ${c.states.join(", ")} in ${c.year} (eia_state_capacity_annual), ${Math.round(c.mw).toLocaleString("en-US")} MW, over ${GRID_NAMES[r.grid]}'s peak demand of ${c.peakYear} (EIA-930), ${Math.round(c.peak).toLocaleString("en-US")} MW. Not a reserve margin: imports, outages and derates are not in it, and reserve margins by zone are not held.`}>capacity <Num check={`allgrids|capratio|${r.id}`} raw={c.pct}>{Math.round(c.pct).toLocaleString("en-US")}</Num>% of peak</span></> : null}
      </span>
    </span>
  );
}

function RowHead({ r }: { r: Row }) {
  return (
    <th scope="row" className="px-3 py-1.5 text-left font-normal" data-row={r.id}>
      <span className="text-xs text-muted">{GRID_NAMES[r.grid]}</span>{" "}
      {r.blank ? <span className="cursor-help border-b border-dotted border-muted" title={r.blank.why} tabIndex={0}>{r.label}</span> : r.label}
    </th>
  );
}

export function AllGridsView({ q }: { q: Record<string, string | undefined> }) {
  const x = sitingInputs(q);
  const hubs = hubRows(SITING_FILES.index), nodes = nodeRows(NODES);
  const rows = x.rows === "nodes" ? nodes : hubs;
  const p = PROFILES[x.profile];
  return (
    <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]" data-no-usage="1" data-allgrids="1">
      <aside>
        <InputPanel title="Your load">
          <AllGridsForm x={x} />
        </InputPanel>
      </aside>
      <div className="min-w-0">
        <p className="mb-3 max-w-3xl text-sm" data-allgrids-count={x.rows}>
          {x.rows === "nodes"
            ? <>Every ERCOT node of node_basis_daily that is neither a hub nor a load zone: <Num check="allgrids|rows|nodes" raw={nodes.length}>{nodes.length.toLocaleString("en-US")}</Num> nodes, from {NODES.first} to {NODES.last}.</>
            : <>Every hub and load zone the page&apos;s price files hold, and the grids they do not price: <Num check="allgrids|rows|hubs" raw={hubs.length}>{hubs.length.toLocaleString("en-US")}</Num> rows.</>}
          {" "}{/^[aeiou]/i.test(p.label) ? "An" : "A"} {p.label.toLowerCase()} load of {x.mw.toLocaleString("en-US")} MW at a load factor of {x.lf.toFixed(2)}, {CURTAIL_WORDS[p.curtail]}{x.strike !== null ? ` (USD ${x.strike.toLocaleString("en-US")} per MWh)` : ""}. Sorted by grid, then by name.
        </p>
        <RowToggle x={x} hubs={hubs.length} nodes={nodes.length} />
        <div className="overflow-x-auto" role="region" aria-label="All grids" tabIndex={0} data-allgrids-table="1">
          <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 960 }}>
            <caption className="sr-only">What a {p.label.toLowerCase()} load pays, when it connects and how clean the power is, {x.rows === "nodes" ? "at every ERCOT node" : "at every hub and zone"}</caption>
            <thead>
              <tr className="bg-accent text-white">
                <th scope="col" className="px-3 py-1.5 font-normal">{x.rows === "nodes" ? "Node" : "Grid and region"}</th>
                {COLUMNS.map((c) => (
                  <th key={c.id} scope="col" className="px-3 py-1.5 text-right font-normal" data-col={c.id}>
                    <span className={tipCls} title={`${c.tip} ${c.unit}.`} tabIndex={0}>{c.head}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-rule" data-allgrids-row={r.id}>
                  <RowHead r={r} />
                  {COLUMNS.map((c) => <td key={c.id} className="px-3 py-1.5 text-right" data-cell={c.id}>{c.id === "energy" ? (x.profile === "datacenter" ? <EnergyTd r={r} e={energyCell(SITING_DC, SITING_FILES, r)} /> : <ProfileTd r={r} x={x} />)
                    : c.id === "transmission" ? <TxTd r={r} x={x} /> : c.id === "capacity" ? <CapTd r={r} x={x} /> : c.id === "connect" ? <ConnectTd r={r} /> : c.id === "headroom" ? <HeadroomTd r={r} /> : c.id === "allin" ? <AllInTd r={r} x={x} /> : null}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 max-w-3xl text-xs" data-allgrids-method="1">
          One row a hub, zone or node; one column a question. The columns are filled one session at a time from the warehouse&apos;s own tables, each by the function that computes it for &quot;Your load&quot;.
          {" "}<Link href="/data/methods/siting">Method note</Link>.
        </p>
      </div>
    </div>
  );
}
