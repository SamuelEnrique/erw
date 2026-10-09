import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import type { ReactNode } from "react";
import { AskErcotLink } from "@/components/AskErcotLink";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import captureJson from "@/data/seller/capture.json";
import hybridJson from "@/data/seller/hybrid.json";
import * as B from "@/lib/batterystack";
import { caisoJoinDay } from "@/lib/caisoJoin";  // session 78: the join's date is written in one place
import {
  FUELS, MARKETS, ORDER, combined, freeEnergyHref, hubAt, hubName, hubOf, hubYears, lastTwelve as captureTwelve, monthName as shortMonth, premiumWord, signed, twelve, two, whyNot, years as captureYears,
  type CaptureFile, type Fuel, type Hub, type Market, type Span as CaptureSpan,
} from "@/lib/capture";
import { shown } from "@/lib/format";
import {
  ASSET_NAMES, DEBT, DEFAULT_SIZE, DEFAULTS, durationOf, EVENTS, HEAT_RATE, inputsKey, inputsOf, keyOf, months, stress, summary, ttm, VOM,
  type Asset, type Snapshot,
} from "@/lib/merchant";
import { ASSETS, GRIDS, PAUSED, sentence, spans, usd, whole, years, type Span } from "@/lib/seller2";
import * as H from "@/lib/sellerhybrid";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { CostTabs } from "../Tabs";
import { CoverageLine, MonthlyRevenue, PremiumYears, RevenueYears, type PremiumRow } from "./SellerCharts";
import { ContractInputs, ContractProvider, ContractResult } from "./SellerContract";
import { SellerForm, type FormGrid } from "./SellerForm";
import { SellerHubYears, type HyCell, type HyRow, type HyTable } from "./SellerHubYears";
import { SellerProfile } from "./SellerProfile";

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
export const metadata: Metadata = { title: "What a generator earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/cost_of_power";
const CAPTURE = captureJson as unknown as CaptureFile;
const NEAR = CAPTURE.near;
const BATTERY_GRIDS = ["ercot", "caiso"];  // the grids the battery page's model is open for
const PJM_WHY = "PJM's prices come from a licensed source; none is held in a public table, so no figure is shown.";
const HYBRID = hybridJson as unknown as H.HybridFile;
const ZONES: Record<string, string> = { "-5": "Eastern Standard Time (UTC-5)", "-6": "Central Standard Time (UTC-6)", "-8": "Pacific Standard Time (UTC-8)" };
const STANDARD: Record<string, number> = { ercot: -6, caiso: -8, nyiso: -5, isone: -5, spp: -6 };

// (a) the co-optimized pair of the reader's sizes: one day's program at a time (about a tenth of a second for the
// twelve months), kept while the server lives
const PAIRS = new Map<string, H.Totals>();
function pairOf(grid: string, fuel: Fuel, mw: number, bmw: number, dur: number): H.Totals | null {
  const g = HYBRID.grids[grid];
  if (!g || !g.fuels[fuel]) return null;
  const k = `${grid}|${fuel}|${mw}|${bmw}|${dur}`;
  let t = PAIRS.get(k);
  if (!t) {
    t = H.totals(H.daysOf(g, fuel, mw), bmw, dur, mw);
    if (PAIRS.size > 300) PAIRS.clear();
    PAIRS.set(k, t);
  }
  return t;
}

// (b) every public hub and zone by year, made small for the browser: a held cell is four numbers, a cell not held
// the index of its reason
let HUB_YEARS: HyTable | null = null;
function hubYearsTable(): HyTable {
  if (HUB_YEARS) return HUB_YEARS;
  const t = hubYears(CAPTURE);
  const whys: string[] = [], at = new Map<string, number>();
  const why = (w: string) => { let i = at.get(w); if (i === undefined) { i = whys.length; whys.push(w); at.set(w, i); } return i; };
  const r4 = (v: number) => Math.round(v * 1e4) / 1e4;
  const both = <T,>(f: (m: Market, fuel: Fuel) => T) => ({ rt: { solar: f("rt", "solar"), wind: f("rt", "wind") }, da: { solar: f("da", "solar"), wind: f("da", "wind") } });
  const rows: HyRow[] = t.rows.map((r) => ({
    grid: r.grid, gridName: r.gridName, id: r.id, name: r.name, main: r.main, src: { rt: r.tables.rt?.join(", "), da: r.tables.da?.join(", ") },
    c: both((m, f) => t.years.map((y): HyCell => { const c = r.cells[m][f][y]; return c ? [r4(c.price), r4(c.flat), c.hours, c.months] : why(r.why[m][f][y]); })),
    t: both((m, f) => { const c = r.twelve[m][f]; return c ? [r4(c.price), r4(c.flat), c.hours, shortMonth(c.from), shortMonth(c.to)] as [number, number, number, string, string] : why(r.whyTwelve[m][f]); }),
  }));
  const generation = Object.fromEntries(Object.entries(CAPTURE.grids).map(([id, g]) => [id, `EIA-930's hourly generation by source (${g.workbook})${g.generation.includes("caiso") ? `, California from ${caisoJoinDay()} from CAISO's own supply by fuel` : ""}`]));
  HUB_YEARS = { years: t.years, rows, whys, blank: t.blank.map((b) => ({ ...b, why: b.id === "miso" ? PAUSED.words : PJM_WHY })), generation };
  return HUB_YEARS;
}
let SNAP: Snapshot | null = null;
function snapshot(): Snapshot {
  if (!SNAP) SNAP = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "merchant_snapshot.json"), "utf8")) as Snapshot;
  return SNAP;
}

/** A short placeholder with its reason on hover. */
function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
/** A label with its definition on hover. */
function Hint({ children, why }: { children: ReactNode; why: string }) {
  return <span className="cursor-help border-b border-dotted border-muted" title={why}>{children}</span>;
}
/** A number with its check key (mr|<inputs>|<stat>); a count, a ratio or USD as the page shows it. */
function V({ pre, stat, v, d }: { pre: string; stat: string; v: number | null; d?: (v: number) => string }) {
  return v === null ? <span className="text-muted">not held</span> : <Num check={`mr|${pre}|${stat}`} raw={v}>{d ? d(v) : shown(v)}</Num>;
}
function U({ pre, stat, v }: { pre: string; stat: string; v: number | null }) {
  return v === null ? <span className="text-muted">not held</span> : <span data-format="usd"><Num check={`mr|${pre}|${stat}`} raw={v}>{B.usdShort(v)}</Num></span>;
}
const count = (v: number) => String(v);
const longMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
const num = (v: string | undefined, d: number, lo: number, hi: number) => {
  const x = v === undefined || v === "" ? NaN : Number(v);
  return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
};

async function batteryRows(entity: string, strat: B.Strategy, dur: B.Duration): Promise<B.Row[]> {
  // the battery page's own read, to the letter, so both pages show one figure
  return rest<B.Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, entity: `eq.${entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}

export default async function Seller({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const snap = snapshot();
  // the grids that can be chosen: the public five the capture file and the model both hold. An address that names
  // another (MISO, PJM) opens the default grid.
  const open = GRIDS.map((g) => g.id).filter((id) => CAPTURE.grids[id] && snap.isos[id]);
  const iso = q.iso && open.includes(q.iso) ? q.iso : "ercot";
  const x = inputsOf({ ...q, iso });
  const key = inputsKey(x);
  const g = GRIDS.find((k) => k.id === iso)!, a = ASSETS.find((k) => k.id === x.asset)!;
  const cg = CAPTURE.grids[iso];
  const hub = hubOf(CAPTURE, iso, q.hub)!;
  const k = keyOf(x);
  const D = DEFAULTS[k];
  const sizeLabel = x.asset === "battery" ? `${x.mw.toLocaleString("en-US")} MW / ${x.mwh.toLocaleString("en-US")} MWh` : `${x.mw.toLocaleString("en-US")} MW`;
  const fuel: Fuel | null = x.asset === "solar" || x.asset === "wind" ? x.asset : null;
  const peaker = x.asset === "peaker";
  const money = peaker ? "Margin over fuel" : "Revenue";
  const bmw = num(q.bmw, x.mw, 1, 5000);
  const dur = (B.DURATIONS.includes(Number(q.dur) as B.Duration) ? Number(q.dur) : 4) as B.Duration;
  const strat: B.Strategy = q.strat === "dayahead" ? "dayahead" : "foresight";

  // the seller's model: the reader's size (the months, the bad months, coverage, the stress days) and per MW of
  // nameplate (the last twelve months beside the long-run averages)
  const ms = months(snap, x);
  const sm = summary(ms);
  const t = ttm(ms, x.ds);
  const st = stress(snap, x);
  const held = ms.filter((r) => r.held);
  const dsMonth = x.ds / 12;
  const under1 = held.filter((r) => r.dscr !== null && r.dscr < 1), under125 = held.filter((r) => r.dscr !== null && r.dscr < 1.25);
  const annual = held.length ? (held.reduce((s, r) => s + r.revenue, 0) / held.length) * 12 : null;
  const ms1 = months(snap, { ...x, mw: 1, mwh: x.asset === "battery" ? x.mwh / x.mw : 0, ds: 0, fom: 0 });
  const s = spans(ms1);
  const ys = years(ms1);
  const line = sentence({ grid: iso, asset: x.asset }, s);

  // (a) the capture price: the market shown first is real time where the hub holds it, else day-ahead
  const cap = (h: Hub, f: Fuel, m: Market) => twelve(h[m]?.[f], NEAR);
  const has = (h: Hub, m: Market) => FUELS.some((f) => Object.keys(h[m]?.[f] ?? {}).length > 0);
  const whole12 = (h: Hub, m: Market) => FUELS.some((f) => cap(h, f, m) !== null);
  const mk: Market = whole12(hub, "rt") ? "rt" : whole12(hub, "da") ? "da" : has(hub, "rt") || !has(hub, "da") ? "rt" : "da";
  const other: Market = mk === "rt" ? "da" : "rt";
  const why = (h: Hub, f: Fuel, m: Market) => `${hubName(h.id)}, ${MARKETS[m].toLowerCase()}, ${f}. ${whyNot(h[m], f, NEAR)}${iso === "nyiso" && f === "solar" ? " EIA-930 itemizes no solar generation for New York." : ""}`;
  const mine = fuel ? cap(hub, fuel, mk) : null;
  const yearRows = (m: Market): PremiumRow[] => {
    const by = Object.fromEntries(FUELS.map((f) => [f, captureYears(hub[m]?.[f], NEAR)])) as Record<Fuel, ReturnType<typeof captureYears>>;
    const labels = [...new Set(FUELS.flatMap((f) => by[f].map((y) => y.y)))].sort();
    const rows: PremiumRow[] = labels.map((y) => {
      const so = by.solar.find((r) => r.y === y), wi = by.wind.find((r) => r.y === y);
      return { label: y, partial: !(so?.whole ?? wi?.whole), months: (so ?? wi)!.months, solar: so?.f ?? null, wind: wi?.f ?? null };
    });
    const l12 = { solar: cap(hub, "solar", m), wind: cap(hub, "wind", m) };
    if (l12.solar || l12.wind) rows.push({ label: "Last 12 months", partial: false, months: 12, solar: l12.solar, wind: l12.wind });
    return rows;
  };
  const premiumRows = yearRows(mk);

  // (b) the contract: the plant's energy over the capture price's twelve months (the model's output per MW of
  // nameplate) at the price the hub chosen paid. Solar and wind only.
  const window = fuel ? captureTwelve(hub[mk]?.[fuel], NEAR) : null;
  const energy = window && window.every((m) => ms1.find((r) => r.m === m)?.held) ? window.reduce((e, m) => e + ms1.find((r) => r.m === m)!.energy, 0) : null;
  const plant = mine && energy !== null ? { energy, price: mine.price } : null;
  const contractWhy = !fuel
    ? "A share of the energy at a fixed price is computed for solar and wind, whose output does not depend on the price. A gas peaker runs only when the price is above its cost and a battery buys as well as sells. A battery's contract, per kW-month, is on What a battery earns."
    : !mine ? why(hub, fuel, mk)
    : "The model's output per MW of nameplate is not held for every one of these twelve months.";

  // (c) a solar or a wind plant with a battery beside it (wind since session 162): the battery's figure in the kept
  // row is the battery page's own, for that duration
  const hybrid = fuel !== null;
  const bg = B.gridOf(iso);
  let batt: { perMw: number; total: number; from: string; to: string; plantPerMw: number | null; href: string } | null = null, battWhy = "";
  if (hybrid && BATTERY_GRIDS.includes(iso)) {
    const bx = B.inputsOf({ grid: iso, dur: String(dur), strat, mw: String(bmw) });
    const read = await attempt(() => batteryRows(bg.entity!, strat, dur));
    const l12 = read.ok ? B.lastTwelve(B.monthsOf(read.data, strat, dur)) : null;
    if (!read.ok) battWhy = `The battery page's table could not be read, so no number is shown: ${read.reason}`;
    else if (!l12) battWhy = "The battery page holds no twelve consecutive months for this battery.";
    else {
      const same = l12.map((r) => ms1.find((p) => p.m === r.m));
      batt = { perMw: B.sumOf(l12, "total"), total: B.stat(read.data, [], bx, "l12:total")!, from: l12[0].m, to: l12[11].m,
        plantPerMw: same.every((p) => p && p.held) ? same.reduce((e, p) => e + p!.revenue, 0) : null, href: B.hrefOf(bx) };
    }
  } else if (hybrid) {
    battWhy = bg?.review ? `The battery page's model of ${g.name} is in review and shown in the internal view only. It is open for ERCOT and CAISO.`
      : `The battery page's model is built for ERCOT and CAISO. ${g.name}'s reserve prices need a license, so no battery figure is shown.`;
  }
  const plantTotal = batt && batt.plantPerMw !== null ? Math.round(batt.plantPerMw * x.mw) : null;
  const both = combined(plantTotal, batt ? batt.total : null);
  const COMBINED = "Two assets at one hub with their revenues added, over the same twelve months. No shared interconnection limit, no charging from the plant's own output, no clipped energy recovered: each is priced as if it stood alone.";
  // session 162 (a): the pair co-optimized against the day-ahead prices, for the reader's sizes
  const hg = HYBRID.grids[iso], hf = fuel && hg ? hg.fuels[fuel] : undefined;
  const pair = fuel && BATTERY_GRIDS.includes(iso) ? pairOf(iso, fuel, x.mw, bmw, dur) : null;
  const pairSpan = hf ? `${shortMonth(hf.months[0])} to ${shortMonth(hf.months[11])}` : "";
  const fromPlant = pair && pair.charged > 0 ? Math.round((100 * pair.fromPlant) / pair.charged) : null;
  const plantName = fuel === "wind" ? "wind" : "solar";
  const RULES = "Round trip 86 percent, each local day from empty, at most one full cycle a day, no discharge in an hour priced below zero. Energy only: no ancillary service and no capacity payment.";
  const DA_PLANT = pair && hf ? `A ${x.mw.toLocaleString("en-US")} MW ${plantName} plant selling every hour at the day-ahead price of ${g.at}, ${pairSpan}: ${hf.days} local days whose every hour holds a price and the fleet's output (${hf.left_out} left out, never filled). ${Math.round(pair.energy).toLocaleString("en-US")} MWh at a capture price of USD ${pair.capture === null ? "none" : two(pair.capture)} per MWh. Per MW: USD ${Math.round(pair.plant / x.mw).toLocaleString("en-US")}.` : "";
  const DA_BATTERY = pair ? `A ${bmw.toLocaleString("en-US")} MW, ${dur}-hour battery on an interconnection of its own, with no plant, on the same days and day-ahead prices. Each day's schedule is the best one against that day's prices, all known in advance. ${RULES} Per MW of battery: USD ${Math.round(pair.battery / bmw).toLocaleString("en-US")}.` : "";
  const DA_PAIR = pair ? `The plant and the battery behind one interconnection of ${two(pair.limit)} MW (the plant's capacity, or its highest hour when that is higher). Each local day the battery's schedule is the best one against that day's day-ahead prices, all known in advance: an upper bound for a schedule made the day before. The battery charges from the plant's own output or from the grid${fromPlant === null ? "" : ` (${fromPlant} percent of its charging came from the plant)`}, and the pair's export and its purchase stay inside the limit. ${RULES} Per MW of plant: USD ${Math.round(pair.pair / x.mw).toLocaleString("en-US")}.` : "";
  const DA_ADDED = pair ? `The plant alone and the battery alone, added: two interconnections, no limit shared, the same days, prices and battery rules as the pair. The pair is the same two assets under one more limit, so it is never above this figure. The difference, USD ${Math.round(pair.added - pair.pair).toLocaleString("en-US")}, is what sharing the interconnection costs.` : "";
  const above = pair !== null && both !== null && pair.pair > both;
  const KEPT = `${COMBINED} The plant is this page's model at real-time prices and the battery is the figure of What a battery earns, energy and ancillary services together. It is on other prices than the row above and holds ancillary revenue the co-optimized pair does not, so the two rows are not one measure${pair && both !== null ? `: here the co-optimized pair, USD ${B.usdShort(Math.round(pair.pair))}, is ${above ? "above" : "below"} it` : ""}.`;

  const grids: FormGrid[] = ORDER.map((id) => {
    if (open.includes(id)) return { id, name: CAPTURE.grids[id].name, open: true, hubs: CAPTURE.grids[id].hubs.map((h) => ({ id: h.id, label: `${hubName(h.id)} (${h.id})` })) };
    const b = CAPTURE.blank[id];
    return { id, name: b?.name ?? id.toUpperCase(), open: false, words: b?.words ?? "not held yet", why: id === "miso" ? PAUSED.words : PJM_WHY, hubs: [] };
  });
  const defaults = `Defaults for ${a.name.toLowerCase()}, Lazard's Levelized Cost of Energy+ (June 2025), the midpoint of each range: capital ${D.capex.toLocaleString("en-US")} USD/kW (${D.capexRange}), `
    + `fixed O&M ${D.fom} USD/kW a year (${D.fomRange}), life ${D.life} years. Debt: ${DEBT.share * 100} percent of the capital at ${DEBT.rate * 100} percent over the life, `
    + `USD ${B.usdShort(Math.round(D.capex * 1000 * x.mw * DEBT.share * (DEBT.rate / (1 - (1 + DEBT.rate) ** -D.life))))} a year for ${sizeLabel}.`
    + (peaker ? ` Heat rate ${HEAT_RATE} MMBtu/MWh and variable O&M ${VOM} USD/MWh (Lazard gas peaking, new build, 10,275 to 11,175 Btu/kWh and 3.50 to 5.00 USD/MWh).` : "")
    + (x.asset === "battery" ? ` Priced as a ${durationOf(x.mw, x.mwh)}-hour battery (the nearer of the two durations Lazard prices), round trip ${snap.defaults.rte * 100} percent, one full cycle a day at most.` : "")
    + ` Default sizes: ${DEFAULT_SIZE.solar.mw} MW solar, wind or peaker; ${DEFAULT_SIZE.battery.mw} MW / ${DEFAULT_SIZE.battery.mwh} MWh battery.`;

  const cell = (v: Span | null, f: (v: Span) => string, whyNone: string) => (v ? f(v) : <Missing why={whyNone} />);
  const threeWhy = `${g.name} holds ${s.everyYears.length === 0 ? "no full calendar year" : s.everyYears.length === 1 ? `one full calendar year (${s.everyYears[0]})` : `${s.everyYears.length} full calendar years`}; three in a row are needed.`;
  const everyWhy = `${g.name} holds no full calendar year: a year is full when all twelve of its months are held.`;
  const twelveWhy = `${g.name} holds no twelve months in a row for this asset.`;
  const spanHead = [
    "",
    <span key="t">Last twelve months<span className="block text-xs font-normal opacity-80">{s.twelve ? `${shortMonth(s.twelve.from)} to ${shortMonth(s.twelve.to)}` : "not held yet"}</span></span>,
    <span key="3">Long-run average, a year<span className="block text-xs font-normal opacity-80">{s.threeYears ? `${s.threeYears[0]} to ${s.threeYears[2]}, the last three full years` : "the last three full years"}</span></span>,
    <span key="e">Long-run average, a year<span className="block text-xs font-normal opacity-80">{s.everyYears.length ? `every full year held, ${s.everyYears[0]} to ${s.everyYears.at(-1)}` : "every full year held"}</span></span>,
  ];
  const spanRow = (label: string, f: (v: Span) => string, id: string, highlight = false) => ({
    key: id, highlight, cells: [label, <span key="t" data-seller2={`twelve|${id}`}>{cell(s.twelve, f, twelveWhy)}</span>, <span key="3" data-seller2={`three|${id}`}>{cell(s.three, f, threeWhy)}</span>,
      <span key="e" data-seller2={`every|${id}`}>{cell(s.every, f, everyWhy)}</span>],
  });
  /** One hub's last twelve months of one fuel: the market shown first, the other market beside it, each said. */
  const capCells = (h: Hub, f: Fuel): ReactNode[] => {
    const one = (m: Market, what: "price" | "premium") => {
      const c = cap(h, f, m);
      if (!c) return <Missing why={why(h, f, m)} />;
      return what === "price"
        ? <span data-cap={`${h.id}|${m}|${f}|price`} title={`${two(c.price)} USD per MWh received against a flat average of ${two(c.flat)}, ${shortMonth(c.from)} to ${shortMonth(c.to)}, ${c.hours.toLocaleString("en-US")} hours. The grid's whole fleet by hour, not one site.`}>{two(c.price)}</span>
        : <span data-cap={`${h.id}|${m}|${f}|premium`} title={`A ${premiumWord(c.premium)}: the generation-weighted price less the flat average of ${two(c.flat)} USD per MWh over the same hours.`}>{signed(c.premium)}{c.pct === null ? "" : ` (${signed(c.pct, 1)} percent)`}</span>;
    };
    const two2 = (what: "price" | "premium") => (
      <>{one(mk, what)}{h[other] ? <span className="block text-xs text-muted">{MARKETS[other].toLowerCase()} {one(other, what)}</span> : null}</>
    );
    return [<span key={`${f}p`}>{two2("price")}</span>, <span key={`${f}d`}>{two2("premium")}</span>];
  };
  const byYear = (m: Market) => yearRows(m).reverse().map((r) => {
    const cells = (c: PremiumRow["solar"], f: Fuel) => (c
      ? [two(c.price), two(c.flat), signed(c.premium), c.pct === null ? "" : signed(c.pct, 1)]
      : [<Missing key="m" why={r.label === "Last 12 months" ? why(hub, f, m) : `No month of ${r.label} holds at least ${Math.round(NEAR * 100)} percent of its hours with both a price and the grid's ${f} generation.`} />, "", "", ""]);
    return { key: r.label, highlight: r.label === "Last 12 months", muted: r.partial,
      cells: [r.partial ? <Hint key="y" why={`${r.months} of 12 months counted: a partial year, its counted months only.`}>{r.label}, partial</Hint> : r.label, ...cells(r.solar, "solar"), ...cells(r.wind, "wind")] };
  });
  const yearHead = ["", "Solar, received", "Flat average", "Difference", "Percent", "Wind, received", "Flat average", "Difference", "Percent"];

  return (
    <ToolPage>
      <ToolHeader
        title="What a generator earns"
        crumb={<CostTabs active="sell" />}
        lead={<>What a solar plant, a wind plant, a battery or a gas peaker earned selling at the hub price: by month and by year, the price it received against the flat average at every public hub, and whether that covers its debt, with and without a contract. <Link href={METHOD}>Method note</Link>.</>}
      />
      {x.iso === "ercot" ? <AskErcotLink context={{ view: "/cost-of-power/seller", title: "What a generator earns", settings: { grid: "ERCOT", asset: ASSET_NAMES[x.asset], size: sizeLabel } }} /> : null}
      <ContractProvider>
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Your plant">
              <SellerForm key={`${key}|${hub.id}|${bmw}|${dur}|${strat}`} x={{ iso, hub: hub.id, asset: x.asset, mw: x.mw, mwh: x.mwh, ds: x.ds, fom: x.fom, hr: x.hr, vom: x.vom, bmw, dur, strat }} grids={grids} hybrid={hybrid} defaults={defaults} />
            </InputPanel>
            <InputPanel title="Your contract (optional)">
              <ContractInputs />
            </InputPanel>
          </aside>

          <div className="min-w-0">
            {held.length === 0 ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-seller2-none="1">
                No month of {a.name.toLowerCase()} is held for {g.name}, so no number is shown{x.asset === "solar" && iso === "nyiso" ? ": EIA-930 itemizes no solar generation for New York" : ""}.
              </p>
            ) : (
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                {line ?? <>{g.name} holds no twelve months of {a.name.toLowerCase()} in a row, so the last twelve months are not shown.</>}
                {mine ? <> At {hubAt(hub.id)} the price it received, weighted by generation, was USD {two(mine.price)} per MWh, USD {two(Math.abs(mine.premium))}{mine.pct === null ? "" : ` (${Math.abs(mine.pct).toFixed(1)} percent)`} {mine.premium < 0 ? "below" : "above"} the flat average of USD {two(mine.flat)}.</> : null}
              </p>
            )}

            <HeadlineRow>
              <HeadlineNumber label={`${money}, last twelve months`}
                value={s.twelve ? <span data-stat="l12_kw">{usd(s.twelve.revenue_kw)}</span> : <Missing why={twelveWhy} />} unit={s.twelve ? "USD/kW" : undefined}
                note={s.twelve ? <>{shortMonth(s.twelve.from)} to {shortMonth(s.twelve.to)}, priced at {g.at}</> : null} />
              {fuel ? (
                <HeadlineNumber label={`Price received at ${hubAt(hub.id)}`}
                  value={mine ? <span data-stat="cap_price">{two(mine.price)}</span> : <Missing why={why(hub, fuel, mk)} />} unit={mine ? "USD/MWh" : undefined}
                  note={mine ? <><span data-stat="cap_premium">{signed(mine.premium)}</span> USD per MWh{mine.pct === null ? "" : <> (<span data-stat="cap_pct">{signed(mine.pct, 1)}</span> percent)</>} against the flat average of <span data-stat="cap_flat">{two(mine.flat)}</span>; {MARKETS[mk].toLowerCase()}, {shortMonth(mine.from)} to {shortMonth(mine.to)}</> : null} />
              ) : (
                <HeadlineNumber label={peaker ? "Price while running" : "Price while selling"}
                  value={s.twelve && s.twelve.capture !== null ? usd(s.twelve.capture) : <Missing why={twelveWhy} />} unit={s.twelve && s.twelve.capture !== null ? "USD/MWh" : undefined}
                  note={s.twelve ? <>against {usd(s.twelve.flat)} for every hour{s.twelve.rate !== null ? <>: {whole(s.twelve.rate)} percent of it</> : null}</> : null} />
              )}
              <HeadlineNumber label="Debt coverage, last twelve months"
                value={t.length ? <span data-stat="cover"><V pre={key} stat="ttm_last" v={t.at(-1)!.dscr} /></span> : <Missing why="No twelve consecutive months are held, so there is no twelve-month coverage." />} unit={t.length ? "times" : undefined}
                note={t.length ? <>The twelve months to {longMonth(t.at(-1)!.m)}: revenue less fixed O&amp;M, over debt payments of USD <U pre={key} stat="ds" v={x.ds} /> a year.</> : null} />
            </HeadlineRow>

            <ChartFrame title={`Premium or discount to the flat average at ${hubAt(hub.id)}, USD per MWh`}
              legend={[{ label: "Solar", color: "#8C1515" }, { label: "Wind", color: "#2E2D29" }, { label: "Partial year", color: "#2E2D29", hatch: true }]}
              note={<>{MARKETS[mk]} prices. <span data-free-energy="1">Hours when power here was free or cost less than nothing: <Link href={freeEnergyHref(iso, hub.id)}>where free energy is, for {hubAt(hub.id)}</Link>.</span></>}>
              {premiumRows.length ? <PremiumYears rows={premiumRows} hub={hubName(hub.id)} market={MARKETS[mk].toLowerCase()} label={`Solar and wind at ${hubAt(hub.id)}: the generation-weighted price less the flat average, by year, USD per MWh`} />
                : <p className="py-6 text-sm"><Missing why={why(hub, "solar", mk)} /></p>}
            </ChartFrame>

            <ToolSection title="Capture price at every hub, last twelve months" id="capture">
              <ToolTable caption={`Capture price at every public hub and zone of ${g.name}, last twelve months`} minWidth={700}
                head={["Hub or zone", "Solar, USD per MWh", "Against the flat average", "Wind, USD per MWh", "Against the flat average"]}
                rows={cg.hubs.map((h) => ({ key: h.id, highlight: h.id === hub.id,
                  cells: [h.id === hub.id ? <span data-cap-hub={h.id}>{hubName(h.id)}</span> : <Link href={`/cost-of-power/seller?iso=${iso}&asset=${x.asset}&hub=${encodeURIComponent(h.id)}`} scroll={false}>{hubName(h.id)}</Link>, ...capCells(h, "solar"), ...capCells(h, "wind")] }))} />
            </ToolSection>

            <ToolSection title={`By year at ${hubAt(hub.id)}`} id="capture-years">
              <ToolTable caption={`Capture price by year at ${hubAt(hub.id)}, ${MARKETS[mk].toLowerCase()}`} minWidth={760} head={yearHead} rows={byYear(mk)} />
              <p className="mt-1 text-xs text-muted">{MARKETS[mk]} prices, USD per MWh.</p>
              {hub[other] ? (
                <Fold title={`${MARKETS[other]} prices, by year`}>
                  <ToolTable caption={`Capture price by year at ${hubAt(hub.id)}, ${MARKETS[other].toLowerCase()}`} minWidth={760} head={yearHead} rows={byYear(other)} />
                </Fold>
              ) : null}
            </ToolSection>

            <ToolSection title="Capture price by hub and year" id="hub-years">
              <SellerHubYears table={hubYearsTable()} fuel0={fuel ?? "solar"} hub={hub.id} />
            </ToolSection>

            {held.length ? (
              <>
                <ChartFrame title={`${money} by year, USD per kW`} legend={[{ label: "A full year", color: "#8C1515" }, { label: "Incomplete year", color: "#8C1515", hatch: true }]}
                  note={<>Per kW of nameplate, priced at {g.at}. {g.name} is held from {shortMonth(held[0].m)}.</>}>
                  <RevenueYears rows={ys.map((y) => ({ y: y.y, complete: y.complete, v: y.revenue / 1000, months: y.months }))} money={money} label={`${a.name} in ${g.name}: ${money.toLowerCase()} by year, USD per kW`} />
                </ChartFrame>

                <ToolSection title="The last twelve months beside the long-run averages" id="spans">
                  <ToolTable caption={`${a.name} in ${g.name}, by span`} minWidth={680} head={spanHead}
                    rows={[
                      spanRow(`${money}, USD per kW`, (v) => usd(v.revenue_kw), "revenue", true),
                      spanRow(peaker ? "Energy sold while running, MWh per MW" : "Energy sold, MWh per MW", (v) => whole(v.energy), "energy"),
                      spanRow(peaker ? "Price while running, USD per MWh" : "Capture price, USD per MWh", (v) => (v.capture !== null ? usd(v.capture) : "not held"), "capture"),
                      spanRow("Price of every hour, USD per MWh", (v) => usd(v.flat), "flat"),
                      spanRow(peaker ? "Price while running over every hour's, percent" : "Capture rate, percent", (v) => (v.rate !== null ? whole(v.rate) : "not held"), "rate"),
                    ]} />
                  {x.asset === "battery" ? <p className="mt-2 text-sm">Energy alone. Energy and ancillary services together, at 2, 4 and 8 hours: <Link href="/cost-of-power/battery">What a battery earns</Link>.</p> : null}
                </ToolSection>
              </>
            ) : null}

            <ToolSection title="With your contract" id="contract">
              <ContractResult plant={plant} mw={x.mw} hub={hubAt(hub.id)} span={mine ? `${shortMonth(mine.from)} to ${shortMonth(mine.to)}` : null} why={contractWhy} />
            </ToolSection>

            <ToolSection title="With a battery beside it" id="hybrid">
              {!hybrid ? (
                <p className="text-sm">A solar or wind plant with a 2, 4 or 8 hour battery: <Link href={`/cost-of-power/seller?iso=${iso}&asset=solar&hub=${encodeURIComponent(hub.id)}#hybrid`} scroll={false}>open it for solar</Link>.</p>
              ) : !BATTERY_GRIDS.includes(iso) ? (
                <p className="text-sm" data-hybrid="none"><Missing why={battWhy} words="not modeled for this grid" /></p>
              ) : (
                <>
                  <ToolTable caption={`A ${plantName} plant, a battery, the co-optimized pair and the two added`} minWidth={620}
                    head={["", "Plant alone", "Battery alone", <Hint key="p" why="One interconnection: the battery charges from the plant or the grid and sells when the pair earns most. Hover on the figure for its rules.">Co-optimized pair</Hint>,
                      <Hint key="a" why="The two assets priced as if each stood alone, their revenues added. Hover on each figure for what it holds.">Added, not co-optimized: upper bound</Hint>]}
                    rows={[
                      { key: "dayahead", highlight: true, cells: [
                        <>Energy at day-ahead prices<div className="text-xs font-normal text-muted">{pair ? <>{pairSpan}, {x.mw.toLocaleString("en-US")} MW and {bmw.toLocaleString("en-US")} MW, {dur}-hour</> : null}</div></>,
                        ...(pair ? [
                          <span key="p" className="cursor-help" data-hybrid2="plant" data-raw={Math.round(pair.plant)} title={DA_PLANT}>{B.usdShort(Math.round(pair.plant))}</span>,
                          <span key="b" className="cursor-help" data-hybrid2="battery" data-raw={Math.round(pair.battery)} title={DA_BATTERY}>{B.usdShort(Math.round(pair.battery))}</span>,
                          <span key="c" className="cursor-help" data-hybrid2="pair" data-raw={Math.round(pair.pair)} title={DA_PAIR}>{B.usdShort(Math.round(pair.pair))}</span>,
                          <span key="a" className="cursor-help" data-hybrid2="added" data-raw={Math.round(pair.added)} title={DA_ADDED}>{B.usdShort(Math.round(pair.added))}</span>,
                        ] : [<Missing key="m" why={`No twelve months in a row hold ${g.name}'s day-ahead price and its ${plantName} fleet's output on at least 90 percent of their days.`} />, "", "", ""]),
                      ] },
                      { key: "kept", cells: [
                        <>Plant at real-time prices, battery with ancillary services<div className="text-xs font-normal text-muted">{batt ? <>{shortMonth(batt.from)} to {shortMonth(batt.to)}; {B.STRATEGIES[strat].toLowerCase()}: the figure of <Link href={batt.href}>What a battery earns</Link></> : null}</div></>,
                        ...(batt ? [
                          plantTotal === null ? <Missing key="m" why={`The ${plantName} plant's months are not all held over the battery's twelve months.`} /> : <span key="v" className="cursor-help" title={`${a.name} plant alone, ${x.mw.toLocaleString("en-US")} MW, this page's model priced at ${g.at} in real time. Per MW: USD ${Math.round(batt.plantPerMw!).toLocaleString("en-US")}.`}><span data-hybrid="plant" data-raw={plantTotal}>{B.usdShort(plantTotal)}</span></span>,
                          <span key="b" className="cursor-help" title={`Battery alone, ${bmw.toLocaleString("en-US")} MW, ${dur}-hour, ${B.STRATEGIES[strat].toLowerCase()}, energy and ancillary services: the figure of What a battery earns. Per MW: USD ${Math.round(batt.perMw).toLocaleString("en-US")}.`}><span data-hybrid="battery" data-raw={batt.total}>{B.usdShort(batt.total)}</span></span>,
                          <Missing key="n" why="No pair is solved with ancillary services: the co-optimized pair is energy at day-ahead prices, in the row above." words="not modeled" />,
                          both === null ? <Missing key="m" why={`The ${plantName} plant's months are not all held over the battery's twelve months.`} /> : (
                            <span key="v" className="cursor-help" title={KEPT}><span data-hybrid="combined" data-raw={both}>{B.usdShort(both)}</span>
                              {above ? <span className="block text-xs font-normal text-muted" data-hybrid-above="1">below the co-optimized pair</span> : null}</span>
                          ),
                        ] : [<Missing key="m" why={battWhy} />, "", "", ""]),
                      ] },
                    ]} />
                  {pair && hf ? (
                    <p className="mt-1 text-xs text-muted" data-hybrid2-note="1">
                      USD for your sizes. <Hint why={`Of the ${Math.round(pair.charged).toLocaleString("en-US")} MWh the battery took in over the twelve months, ${Math.round(pair.fromPlant).toLocaleString("en-US")} MWh were the plant's own output in the same hour; the rest was bought at the hub price. At one hub price the two cost the same: the split is an account of where the energy came from.`}>{fromPlant === null ? "The battery did not charge" : `${fromPlant} percent of the charging from the plant`}</Hint>;{" "}
                      <Hint why={`A local day is solved only when every hour of its day-ahead price and of the fleet's output is held. ${hf.left_out} of the twelve months' days ${hf.left_out === 1 ? "is" : "are"} left out and counted, never filled.`}>{hf.days} days solved</Hint>.
                    </p>
                  ) : null}
                </>
              )}
            </ToolSection>

            <ToolSection title="Your plant's profile" id="profile">
              {fuel ? (
                <SellerProfile key={`${iso}|${bmw}|${dur}`} grid={iso} gridName={g.name} hub={hubName(cg.main)} zone={ZONES[String(STANDARD[iso])]} years={HYBRID.years[iso] ?? []}
                  battery={{ mw: bmw, hours: dur }} hybridWhy={BATTERY_GRIDS.includes(iso) ? null : battWhy} />
              ) : (
                <p className="text-sm">A year of your own plant&apos;s hourly output, priced on this device: <Link href={`/cost-of-power/seller?iso=${iso}&asset=solar&hub=${encodeURIComponent(hub.id)}#profile`} scroll={false}>open it for solar</Link>.</p>
              )}
            </ToolSection>

            <ToolSection title={`Month by month: ${a.name.toLowerCase()}, ${sizeLabel}, at ${g.name} ${snap.isos[iso].hub}`} id="months">
              {sm.n ? (
                <>
                  <p className="mb-2 max-w-3xl text-sm">
                    Over <V pre={key} stat="n" v={sm.n} d={count} /> months held, {longMonth(sm.first!)} to {longMonth(sm.last!)}, the median month earned{" "}
                    <strong><U pre={key} stat="median" v={sm.median!.revenue} /></strong> USD ({longMonth(sm.median!.m)}) and the 10th-percentile month{" "}
                    <strong><U pre={key} stat="p10" v={sm.p10!.revenue} /></strong> USD ({longMonth(sm.p10!.m)}): one month in ten earned that or less. The year&apos;s average,
                    twelve times the mean month, is <U pre={key} stat="annual_mean" v={annual} /> USD.
                  </p>
                  <p className="mb-2 max-w-3xl text-sm">
                    The worst three months:{" "}
                    {sm.worst.map((r, i) => <span key={r.m}>{i ? "; " : ""}{longMonth(r.m)}, <U pre={key} stat={`worst:${i}`} v={r.revenue} /> USD</span>)}.
                  </p>
                  <MonthlyRevenue rows={ms.map((r) => ({ m: r.m, revenue: r.revenue, held: r.held, share: r.share }))} dsMonth={dsMonth} label="Revenue per month, USD; a dashed line marks one month of debt payments" />
                  <p className="mb-2 flex flex-wrap gap-x-4 text-xs text-muted">
                    <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-ink" />A month held</span>
                    <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-accent" />Below a month of debt payments (USD <U pre={key} stat="ds" v={x.ds} /> a year over twelve)</span>
                    <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-rule" /><Hint why="A month with less than 90 percent of its hours (a battery: days) priced is shown and not counted.">Under 90 percent held</Hint></span>
                  </p>
                </>
              ) : <p className="text-sm"><Missing why={`No month is held for ${a.name.toLowerCase()} at ${g.name}'s hub.`} /></p>}
            </ToolSection>

            <ToolSection title="Debt coverage" id="coverage">
              {held.length ? (
                <>
                  <p className="mb-2 max-w-3xl text-sm">
                    <Hint why="Cash flow available for debt payments is the month's revenue less fixed O&M; coverage is that over one month of the annual debt payments.">Coverage</Hint> with fixed O&amp;M of {x.fom} USD/kW a year and debt payments of{" "}
                    <U pre={key} stat="ds" v={x.ds} /> USD a year: of the <V pre={key} stat="n" v={sm.n} d={count} /> months held,{" "}
                    <strong><V pre={key} stat="under1" v={under1.length} d={count} /></strong> covered less than 1.0x and{" "}
                    <strong><V pre={key} stat="under125" v={under125.length} d={count} /></strong> less than 1.25x.
                    {t.length ? (
                      <> Over trailing twelve months, coverage was <V pre={key} stat="ttm_last" v={t.at(-1)!.dscr} />x at {longMonth(t.at(-1)!.m)}, at its lowest{" "}
                        <V pre={key} stat="ttm_min" v={Math.min(...t.map((r) => r.dscr))} />x; <V pre={key} stat="ttm_under1" v={t.filter((r) => r.dscr < 1).length} d={count} /> of {t.length} twelve-month
                        windows fell under 1.0x and <V pre={key} stat="ttm_under125" v={t.filter((r) => r.dscr < 1.25).length} d={count} /> under 1.25x.</>
                    ) : <> Twelve-month coverage: <Missing why="No twelve consecutive months are held here, so there is no trailing-twelve-month figure." />.</>}
                  </p>
                  {t.length >= 2 ? <CoverageLine rows={t.map((r) => ({ m: r.m, dscr: r.dscr }))} label="Trailing-twelve-month debt coverage; lines at 1.0 and 1.25 times" /> : null}
                  {under1.length ? <p className="mt-1 text-xs text-muted">Months under 1.0x: {under1.map((r) => r.m).join(", ")}.</p> : null}
                </>
              ) : <p className="text-sm"><Missing why={`No month is held for ${a.name.toLowerCase()} at ${g.name}'s hub.`} /></p>}
            </ToolSection>

            <div className="mb-8 border-t border-rule">
              <Fold title="Every month: revenue, energy, capture price and rate, coverage">
                <ToolTable caption="Every month" minWidth={720} head={["Month", "Revenue, USD", "Energy, MWh", "Capture, USD/MWh", "Flat, USD/MWh", "Capture rate, pct", "Coverage", "Held"]}
                  rows={[...ms].reverse().map((r) => ({ key: r.m, muted: !r.held, cells: [r.m,
                    <U key="r" pre={key} stat={`month:${r.m}`} v={r.revenue} />, Math.round(r.energy).toLocaleString("en-US"),
                    r.capture === null ? "" : <V key="c" pre={key} stat={`capture:${r.m}`} v={r.capture} />, shown(r.flat),
                    r.rate === null ? "" : <V key="p" pre={key} stat={`rate:${r.m}`} v={r.rate} />, r.dscr === null ? "" : <V key="d" pre={key} stat={`dscr:${r.m}`} v={r.dscr} />,
                    `${Math.round(r.share * 100)} percent`] }))} />
              </Fold>
              <Fold title="Stress days: Uri, Elliott and the 2023 heat">
                {st && st.length ? (
                  <>
                    <ToolTable caption={`Stress days, for ${sizeLabel}`} minWidth={640} head={["Event", "Days", "Per day, USD", "The window, USD", <Hint key="w" why="Seven times the mean of the same event's baseline days: the same days or weekdays of earlier years.">A normal week, USD</Hint>, "The best day, USD"]}
                      rows={st.map((e) => ({ key: e.event, cells: [<>{EVENTS[e.event]}<div className="text-xs text-muted">{e.start} to {e.end}</div></>, String(e.days),
                        <U key="m" pre={key} stat={`stress_mean:${e.event}`} v={e.windowMean} />, <U key="t" pre={key} stat={`stress_total:${e.event}`} v={e.windowTotal} />,
                        <U key="w" pre={key} stat={`stress_week:${e.event}`} v={e.normalWeek} />, <><U pre={key} stat={`stress_best:${e.event}`} v={e.best.v} /> <span className="text-xs text-muted">({e.best.day})</span></>] }))} />
                    <p className="mt-2 text-xs text-muted">For {sizeLabel}, on the local days of each event.</p>
                  </>
                ) : (
                  <p className="text-sm"><Missing why={`The stress days are ERCOT's: ${g.name}'s hub prices are held from ${longMonth(Object.keys(snap.isos[iso].months).sort()[0])} only, after these events.`} words={iso === "ercot" ? "not held yet" : "ERCOT only"} /></p>
                )}
              </Fold>
              <Fold title="The fleet's hours as EIA reports them">
                <ToolTable caption={`Hours of ${g.name}'s solar and wind fleets as EIA reports them`} minWidth={420} head={["", "Solar", "Wind"]}
                  rows={[
                    { key: "over", cells: ["Hours above installed nameplate", String(snap.isos[iso].over_nameplate.solar ?? 0), String(snap.isos[iso].over_nameplate.wind ?? 0)] },
                    { key: "neg", cells: ["Hours EIA reports negative", String(snap.isos[iso].negative.solar ?? 0), String(snap.isos[iso].negative.wind ?? 0)] },
                  ]} />
              </Fold>
            </div>
          </div>
        </div>
      </ContractProvider>
      <SourceLine tables={["merchant_revenue_monthly", "eia_fuel_spot_prices", "eia860m_operating_generators", ...new Set(cg.hubs.flatMap((h) => [...(h.rt?.tables ?? []), ...(h.da?.tables ?? [])])), ...(batt ? [B.TABLE] : [])]}
        note={<>Derived by the ERW from {g.name}&apos;s public prices and EIA-930&apos;s hourly generation by source ({cg.workbook}){cg.generation.includes("caiso") ? `, California from ${caisoJoinDay()} from CAISO's own supply by fuel` : ""}. The model&apos;s snapshot was built {snap.built.slice(0, 10)}, the capture prices {CAPTURE.built.slice(0, 10)}. Cost defaults: Lazard, Levelized Cost of Energy+, June 2025. The buyer&apos;s side is <Link href="/cost-of-power">What a datacenter pays</Link>.</>} />
    </ToolPage>
  );
}
