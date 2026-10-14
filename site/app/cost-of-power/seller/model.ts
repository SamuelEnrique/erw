// Session 212: what /cost-of-power/seller computes before it draws, shared by the page and by its two CSV downloads
// (months.csv/route.ts, tables.csv/route.ts), so that a download is the same read and the same arithmetic as the page.
// Until this session every line here stood at the top of page.tsx (sessions 145 to 195); nothing is computed
// differently. The battery page's read.ts is the pattern. Server only: it reads the committed snapshots from disk and
// the battery page's table from Supabase.
import fs from "node:fs";
import path from "node:path";
import captureJson from "@/data/seller/capture.json";
import hybridJson from "@/data/seller/hybrid.json";
import hubsJson from "@/data/seller/hubs/index.json";
import * as B from "@/lib/batterystack";
import { caisoJoinDay } from "@/lib/caisoJoin";
import {
  FUELS, MARKETS, ORDER, combined, hubAt, hubName, hubOf, hubYears, lastTwelve as captureTwelve, monthName as shortMonth, twelve, whyNoYear, whyNot, yearCell, years as captureYears,
  type CaptureFile, type Fuel, type Hub, type Market,
} from "@/lib/capture";
import {
  DEBT, DEFAULT_SIZE, DEFAULTS, durationOf, HEAT_RATE, inputsKey, inputsOf, keyOf, months, stress, summary, VOM,
  type Inputs, type Snapshot,
} from "@/lib/merchant";
import { BATTERY_DEG, BATTERY_DEG_SOURCE, KEYS as SCENARIO_KEYS, SPECS, debtUsd, defaultsOf, isOldParam, isScenarioParam, parseScenarios } from "@/lib/seller/finance";
import { ASSETS, GRIDS, PAUSED, sentence, spanOf, spans, years } from "@/lib/seller2";
import * as H from "@/lib/sellerhybrid";
import * as HB from "@/lib/sellerhubs";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import type { PremiumRow } from "./SellerCharts";
import type { Facts, MonthRevenue } from "./SellerScenarios";
import type { HyCell, HyRow, HyTable } from "./SellerHubYears";
import { longMonth } from "./nums";

export const HUBS = hubsJson as unknown as HB.HubIndex;
// session 183: one hub's model, read when it is asked for and kept while the server lives (a hub's file is about half a megabyte)
const HUB_FILES = new Map<string, unknown>();
export function hubFile<T>(rel: string): T | null {
  if (!HUB_FILES.has(rel)) {
    if (HUB_FILES.size > 16) HUB_FILES.clear();
    try { HUB_FILES.set(rel, JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "seller", "hubs", rel), "utf8"))); } catch { HUB_FILES.set(rel, null); }
  }
  return HUB_FILES.get(rel) as T | null;
}
export const CAPTURE = captureJson as unknown as CaptureFile;
export const NEAR = CAPTURE.near;
export const BATTERY_GRIDS = ["ercot", "caiso"];  // the grids the battery page's model is open for
export const PJM_WHY = "PJM's prices come from a licensed source; none is held in a public table, so no figure is shown.";
export const HYBRID = hybridJson as unknown as H.HybridFile;
export const ZONES: Record<string, string> = { "-5": "Eastern Standard Time (UTC-5)", "-6": "Central Standard Time (UTC-6)", "-8": "Pacific Standard Time (UTC-8)" };
export const STANDARD: Record<string, number> = { ercot: -6, caiso: -8, nyiso: -5, isone: -5, spp: -6 };

// (a) the co-optimized pair of the reader's sizes: one day's program at a time (about a tenth of a second for the
// twelve months), kept while the server lives
const PAIRS = new Map<string, H.Totals>();
export function pairOf(grid: string, fuel: Fuel, mw: number, bmw: number, dur: number): H.Totals | null {
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
export function hubYearsTable(): HyTable {
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
export function snapshot(): Snapshot {
  if (!SNAP) SNAP = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "merchant_snapshot.json"), "utf8")) as Snapshot;
  return SNAP;
}

const num = (v: string | undefined, d: number, lo: number, hi: number) => {
  const x = v === undefined || v === "" ? NaN : Number(v);
  return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
};

async function batteryRows(entity: string, strat: B.Strategy, dur: B.Duration): Promise<B.Row[]> {
  // the battery page's own read, to the letter, so both pages show one figure
  return rest<B.Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, entity: `eq.${entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}

/** Session 235: one figure of the capture chart and table: the price received, the hub's average over the same hours,
 * and the first over the second in percent (null where the average is not above zero). */
export type CapCell = { price: number; flat: number; rate: number | null; months: number; partial: boolean };
/** One hub or zone of the grid: the market its figures are in, the last twelve months and each year, or why not. */
export type CapRow = {
  id: string; name: string; chosen: boolean; market: Market; twelve: (CapCell & { from: string; to: string }) | null; whyTwelve: string;
  years: (CapCell | null)[]; whyYears: string[];
};
/** The chart's groups (each year at the hub chosen, then the last twelve months) and the table's rows. `fuel` is null
 * for a battery and a gas peaker, whose figures are this page's model at each hub and carry no key of the capture file. */
export type CapView = { fuel: Fuel | null; years: string[]; rows: CapRow[]; chart: (CapCell & { label: string })[] };

export type FormGridOf = { id: string; name: string; open: boolean; words?: string; why?: string; hubs: { id: string; label: string }[] };

/** Everything the page computes for one address, in the order page.tsx computed it until session 212. */
export async function modelOf(q: Record<string, string | undefined>) {
  const snap = snapshot();
  // the grids that can be chosen: the public five the capture file and the model both hold. An address that names
  // another (MISO, PJM) opens the default grid.
  const open = GRIDS.map((g) => g.id).filter((id) => CAPTURE.grids[id] && snap.isos[id]);
  const iso = q.iso && open.includes(q.iso) ? q.iso : "ercot";
  // session 195: scenario A, as the address has it, sets the page's fixed O&M and annual debt payments
  const asked = inputsOf({ ...q, iso });
  // session 196: a battery's degradation default is Lazard's cited rate; the other assets hold none
  const costsOf = (key: keyof typeof DEFAULTS) => ({ ...DEFAULTS[key], ...(asked.asset === "battery" ? { deg: BATTERY_DEG, degSource: BATTERY_DEG_SOURCE } : {}) });
  const A = parseScenarios(q, defaultsOf(costsOf(keyOf(asked))), asked.mw).a;
  const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([n, v]) => (isScenarioParam(n) || isOldParam(n)) && v !== undefined).sort(([a], [b]) => a.localeCompare(b))) as Record<string, string>;
  const g = GRIDS.find((k) => k.id === iso)!, a = ASSETS.find((k) => k.id === x.asset)!;
  const cg = CAPTURE.grids[iso];
  const hub = hubOf(CAPTURE, iso, q.hub)!;
  // session 183: the model the page prices with. At the main hub, the page's snapshot; at another hub or zone, the same
  // model solved with that hub's price. `at` is written beside every figure, so a figure never stands under a hub it
  // was not priced at; a hub whose model is not held says so and shows the main hub's, named.
  const mainHub = hub.id === cg.main;
  const he = mainHub ? null : HUBS.grids[iso]?.hubs[hub.id] ?? null;
  const hubGrid = he ? hubFile<HB.GridFile>(HUBS.grids[iso].file) : null, hubModel = he ? hubFile<HB.HubFile>(he.file) : null;
  const priced: Snapshot = he && hubGrid && hubModel ? HB.withHub(snap, iso, HB.hubIso(snap.isos[iso], hubGrid, hubModel)) : snap;
  const atHub = priced !== snap;
  const at = atHub ? `${hubAt(hub.id)} (${HB.marketWords(he!.market)} prices)` : g.at;
  const key = atHub ? HB.hubKey(inputsKey(x), hub.id, he!.market) : inputsKey(x);
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
  const ms = months(priced, x);
  const sm = summary(ms);
  const st = stress(priced, x);
  const held = ms.filter((r) => r.held);
  const monthRows: MonthRevenue[] = ms.map((r) => ({ m: r.m, revenue: r.revenue, held: r.held, share: r.share }));
  const annual = held.length ? (held.reduce((s, r) => s + r.revenue, 0) / held.length) * 12 : null;
  const perMw = { ...x, mw: 1, mwh: x.asset === "battery" ? x.mwh / x.mw : 0, ds: 0, fom: 0 };
  const ms1 = months(priced, perMw);
  const ms1Main = atHub ? months(snap, perMw) : ms1;  // the battery beside it is priced at the main hub, as the battery page is
  const s = spans(ms1);
  const ys = years(ms1);
  const line = sentence({ grid: iso, asset: x.asset }, s, atHub ? at : undefined);

  // (a) the capture price: the market shown first is real time where the hub holds it, else day-ahead
  const cap = (h: Hub, f: Fuel, m: Market) => twelve(h[m]?.[f], NEAR);
  const has = (h: Hub, m: Market) => FUELS.some((f) => Object.keys(h[m]?.[f] ?? {}).length > 0);
  const whole12 = (h: Hub, m: Market) => FUELS.some((f) => cap(h, f, m) !== null);
  const marketOf = (h: Hub): Market => (whole12(h, "rt") ? "rt" : whole12(h, "da") ? "da" : has(h, "rt") || !has(h, "da") ? "rt" : "da");
  const mk: Market = marketOf(hub);
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

  // Session 235 (the owner's task of 12 October 2026): the capture price back on the page, one chart and one table.
  // The chart: by year and over the last twelve months at the hub chosen, the price the plant received per MWh against
  // the hub's average. The table: one row a hub or zone of the grid, with the last twelve months' capture price, hub
  // average and capture rate, and each year's capture rate. Solar and wind: the capture file (lib/capture.ts), by the
  // functions tables.csv writes capture_last_twelve, capture_by_year and capture_hub_year from, each hub in the market
  // the page shows it in (real time where it holds twelve months, else day-ahead). A battery and a gas peaker choose
  // their hours, so the file's fleet shapes do not describe them: theirs is this page's model solved at each hub
  // (lib/sellerhubs.ts), the price while selling or running against the price of every hour.
  const rateOf = (price: number, flat: number) => (flat > 0 ? (100 * price) / flat : null);
  const capView = ((): CapView => {
    if (fuel) {
      const all = new Set<string>();
      for (const h of cg.hubs) for (const k of Object.keys(h[marketOf(h)]?.[fuel] ?? {})) if (yearCell(h[marketOf(h)]?.[fuel], k.slice(0, 4), NEAR)) all.add(k.slice(0, 4));
      const ysOf = [...all].sort();
      const rows: CapRow[] = cg.hubs.map((h) => {
        const m = marketOf(h), t = cap(h, fuel, m);
        const cells = ysOf.map((y) => { const c = yearCell(h[m]?.[fuel], y, NEAR); return c ? { price: c.price, flat: c.flat, rate: rateOf(c.price, c.flat), months: c.months, partial: !c.whole } : null; });
        return { id: h.id, name: hubName(h.id), chosen: h.id === hub.id, market: m,
          twelve: t ? { price: t.price, flat: t.flat, rate: rateOf(t.price, t.flat), months: 12, partial: false, from: t.from, to: t.to } : null, whyTwelve: t ? "" : why(h, fuel, m),
          years: cells, whyYears: ysOf.map((y, i) => (cells[i] ? "" : `${hubName(h.id)}, ${y}, ${fuel}, ${MARKETS[m].toLowerCase()}. ${whyNoYear(h[m], fuel, m, y, NEAR)}`)) };
      });
      const chart = yearRows(mk).flatMap((r) => { const f = r[fuel]; return f ? [{ label: r.label, price: f.price, flat: f.flat, rate: rateOf(f.price, f.flat), months: r.months, partial: r.partial }] : []; });
      return { fuel, years: ysOf, rows, chart };
    }
    // a battery, a gas peaker: the model per MW at each hub or zone it is held for
    const modelAt = (h: Hub): { snap: Snapshot; market: Market } | null => {
      if (h.id === cg.main) return { snap, market: "rt" };
      const e = HUBS.grids[iso]?.hubs[h.id];
      const gf = e ? hubFile<HB.GridFile>(HUBS.grids[iso].file) : null, hm = e ? hubFile<HB.HubFile>(e.file) : null;
      return e && gf && hm ? { snap: HB.withHub(snap, iso, HB.hubIso(snap.isos[iso], gf, hm)), market: e.market } : null;
    };
    const cellOf = (rs: typeof ms1): CapCell | null => { const v = spanOf(rs, 1); return v && v.capture !== null ? { price: v.capture, flat: v.flat, rate: v.rate, months: rs.length, partial: rs.length < 12 } : null; };
    const at1 = cg.hubs.map((h) => { const md = modelAt(h); return { h, market: md?.market ?? ("rt" as Market), rs: md ? months(md.snap, perMw) : null }; });
    const ysOf = [...new Set(at1.flatMap((r) => (r.rs ?? []).filter((x) => x.held).map((x) => x.m.slice(0, 4))))].sort();
    const yearOf = (rs: typeof ms1, y: string) => cellOf(rs.filter((x) => x.held && x.m.slice(0, 4) === y));
    const rows: CapRow[] = at1.map(({ h, market, rs }) => {
      const t = rs ? spans(rs).twelve : null;
      const none = rs ? `The model holds no twelve months in a row at ${hubAt(h.id)}.` : `The model is not held at ${hubAt(h.id)}.`;
      const cells = ysOf.map((y) => (rs ? yearOf(rs, y) : null));
      return { id: h.id, name: hubName(h.id), chosen: h.id === hub.id, market,
        twelve: t && t.capture !== null ? { price: t.capture, flat: t.flat, rate: t.rate, months: 12, partial: false, from: t.from, to: t.to } : null, whyTwelve: t && t.capture !== null ? "" : none,
        years: cells, whyYears: ysOf.map((y, i) => (cells[i] ? "" : rs ? `No month of ${y} is held at ${hubAt(h.id)}, or the plant sold nothing in it.` : `The model is not held at ${hubAt(h.id)}.`)) };
    });
    const mine1 = ysOf.flatMap((y) => { const c = yearOf(ms1, y); return c ? [{ ...c, label: y }] : []; });
    if (s.twelve && s.twelve.capture !== null) mine1.push({ label: "Last 12 months", price: s.twelve.capture, flat: s.twelve.flat, rate: s.twelve.rate, months: 12, partial: false });
    return { fuel: null, years: ysOf, rows, chart: mine1 };
  })();

  // (b) the contract's twelve months (session 145; since session 212 the contract is two scenario assumptions, priced
  // on the model's energy of the last twelve months: lib/seller/finance.ts, Contract)
  const window = fuel ? captureTwelve(hub[mk]?.[fuel], NEAR) : null;
  const energy = window && window.every((m) => ms1.find((r) => r.m === m)?.held) ? window.reduce((e, m) => e + ms1.find((r) => r.m === m)!.energy, 0) : null;
  const plant = mine && energy !== null ? { energy, price: mine.price } : null;

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
      const same = l12.map((r) => ms1Main.find((p) => p.m === r.m));
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
  const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const DA_PLANT = pair && hf ? `A ${x.mw.toLocaleString("en-US")} MW ${plantName} plant selling every hour at the day-ahead price of ${g.at}, ${pairSpan}: ${hf.days} local days whose every hour holds a price and the fleet's output (${hf.left_out} left out, never filled). ${Math.round(pair.energy).toLocaleString("en-US")} MWh at a capture price of USD ${pair.capture === null ? "none" : two(pair.capture)} per MWh. Per MW: USD ${Math.round(pair.plant / x.mw).toLocaleString("en-US")}.` : "";
  const DA_BATTERY = pair ? `A ${bmw.toLocaleString("en-US")} MW, ${dur}-hour battery on an interconnection of its own, with no plant, on the same days and day-ahead prices. Each day's schedule is the best one against that day's prices, all known in advance. ${RULES} Per MW of battery: USD ${Math.round(pair.battery / bmw).toLocaleString("en-US")}.` : "";
  const DA_PAIR = pair ? `The plant and the battery behind one interconnection of ${two(pair.limit)} MW (the plant's capacity, or its highest hour when that is higher). Each local day the battery's schedule is the best one against that day's day-ahead prices, all known in advance: an upper bound for a schedule made the day before. The battery charges from the plant's own output or from the grid${fromPlant === null ? "" : ` (${fromPlant} percent of its charging came from the plant)`}, and the pair's export and its purchase stay inside the limit. ${RULES} Per MW of plant: USD ${Math.round(pair.pair / x.mw).toLocaleString("en-US")}.` : "";
  const DA_ADDED = pair ? `The plant alone and the battery alone, added: two interconnections, no limit shared, the same days, prices and battery rules as the pair. The pair is the same two assets under one more limit, so it is never above this figure. The difference, USD ${Math.round(pair.added - pair.pair).toLocaleString("en-US")}, is what sharing the interconnection costs.` : "";
  const above = pair !== null && both !== null && pair.pair > both;
  const KEPT = `${COMBINED} The plant is this page's model at real-time prices and the battery is the figure of What a battery earns, energy and ancillary services together. It is on other prices than the row above and holds ancillary revenue the co-optimized pair does not, so the two rows are not one measure${pair && both !== null ? `: here the co-optimized pair, USD ${B.usdShort(Math.round(pair.pair))}, is ${above ? "above" : "below"} it` : ""}.`;

  const grids: FormGridOf[] = ORDER.map((id) => {
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

  const threeWhy = `${g.name} holds ${s.everyYears.length === 0 ? "no full calendar year" : s.everyYears.length === 1 ? `one full calendar year (${s.everyYears[0]})` : `${s.everyYears.length} full calendar years`}; three in a row are needed.`;
  const everyWhy = `${g.name} holds no full calendar year: a year is full when all twelve of its months are held.`;
  const twelveWhy = `${g.name} holds no twelve months in a row for this asset.`;

  // session 186: what the scenarios read. Every figure is one the page shows elsewhere, for the hub, asset and size chosen.
  const assetWords = fuel ? plantName : x.asset === "battery" ? `a ${durationOf(x.mw, x.mwh)}-hour battery` : "a gas peaker";
  const facts: Facts = {
    mw: x.mw,
    size: fuel ? `${sizeLabel} of ${plantName}` : x.asset === "battery" ? `a ${sizeLabel} battery` : `a ${sizeLabel} gas peaker`,
    costs: { ...costsOf(k), capex: D.capex, fom: D.fom, life: D.life, capexNote: `${D.capexRange} for ${assetWords}`, fomNote: `${D.fomRange} for ${assetWords}`, lifeNote: `${D.life} years for ${assetWords}` },
    twelve: s.twelve ? { revenueKw: s.twelve.revenue_kw, energyKw: s.twelve.energy / 1000, span: `${shortMonth(s.twelve.from)} to ${shortMonth(s.twelve.to)}`, at } : null,
    twelveWhy, money,
    capture: fuel
      ? mine && mine.flat ? { price: mine.price, flat: mine.flat, ratio: (100 * mine.price) / mine.flat, words: `${MARKETS[mk].toLowerCase()}, ${shortMonth(mine.from)} to ${shortMonth(mine.to)}` } : null
      : s.twelve && s.twelve.capture !== null && s.twelve.rate !== null ? { price: s.twelve.capture, flat: s.twelve.flat, ratio: s.twelve.rate, words: `${shortMonth(s.twelve.from)} to ${shortMonth(s.twelve.to)}` } : null,
    captureLabel: fuel ? "Capture price and rate" : peaker ? "Price while running, and rate" : "Price while selling, and rate",
    captureWhy: fuel ? why(hub, fuel, mk) : twelveWhy,
    lowest: sm.worst[0] ? { month: longMonth(sm.worst[0].m), usd: sm.worst[0].revenue, months: sm.n } : null,
    contract: fuel ? "energy" : "toll",
    battery: pair ? { withIt: Math.round(pair.pair), without: Math.round(pair.plant), words: `${pairSpan}, a ${bmw.toLocaleString("en-US")} MW, ${dur}-hour battery, priced at ${g.at}` } : null,
    batteryWhy: !fuel ? "A battery beside the plant is modeled for a solar or a wind plant." : !BATTERY_GRIDS.includes(iso) ? battWhy
      : `No twelve months in a row hold ${g.name}'s day-ahead price and its ${plantName} fleet's output on at least 90 percent of their days.`,
  };

  // session 264: a typed value outside its bounds is held at the bound (lib/merchant.ts inputsOf, lib/seller/finance.ts
  // bound); the page says so in one line under "Your plant", value by value. A value that is not a number takes the default.
  const fmt = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 3 });
  const clampedWords: string[] = [];
  const typed = (name: string, label: string, used: number, lo: number, hi: number, whose = "the page uses") => {
    const raw = q[name];
    if (raw === undefined || raw === "") return;
    const v = Number(raw);
    if (!Number.isFinite(v)) clampedWords.push(`${label}: "${raw.slice(0, 20)}" is not a number, so ${whose} ${fmt(used)}.`);
    else if (v < lo) clampedWords.push(`${label}: ${fmt(v)} is below the bound of ${fmt(lo)}, so ${whose} ${fmt(used)}.`);
    else if (v > hi) clampedWords.push(`${label}: ${fmt(v)} is above the bound of ${fmt(hi)}, so ${whose} ${fmt(used)}.`);
  };
  typed("mw", "Size, MW", x.mw, 1, 5000);
  if (x.asset === "battery") typed("mwh", "Energy, MWh", x.mwh, x.mw, x.mw * 8);
  if (peaker) { typed("hr", "Heat rate, MMBtu per MWh", x.hr, 6, 16); typed("vom", "Variable O&M, USD per MWh", x.vom, 0, 50); }
  if (fuel) typed("bmw", "Battery size, MW", bmw, 1, 5000);
  const both2 = parseScenarios(q, defaultsOf(costsOf(keyOf(asked))), asked.mw);
  for (const p of ["a", "b"] as const) for (const kk of SCENARIO_KEYS) {
    const sp = SPECS[kk];
    typed(p + sp.letter, `Scenario ${p.toUpperCase()}, ${sp.label.toLowerCase().replace("ppa", "PPA").replace("o&m", "O&M")}`, both2[p][kk], sp.min, sp.max, "the scenario uses");
  }

  return {
    clampedWords,
    q, snap, open, iso, asked, costsOf, A, x, scenarioParams, g, a, cg, hub, mainHub, he, atHub, at, key, k, D, sizeLabel, fuel, peaker, money, bmw, dur, strat,
    ms, sm, st, held, monthRows, annual, ms1, ms1Main, s, ys, line, cap, mk, other, why, mine, yearRows, capView, plant, hybrid, bg, batt, battWhy, plantTotal, both, COMBINED,
    hf, pair, pairSpan, fromPlant, plantName, DA_PLANT, DA_BATTERY, DA_PAIR, DA_ADDED, above, KEPT, grids, defaults, threeWhy, everyWhy, twelveWhy, facts,
  };
}
export type Model = Awaited<ReturnType<typeof modelOf>>;
