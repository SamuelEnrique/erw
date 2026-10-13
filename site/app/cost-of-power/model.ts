// Session 213: what /cost-of-power computes for "Your load" before it draws, shared by the page and by its two CSV
// downloads (months.csv/route.ts, tables.csv/route.ts), so that a download is the same read and the same arithmetic as
// the page. Until this session every line here stood in page.tsx's LoadView (sessions 138 to 195); nothing is computed
// differently. The seller page's model.ts (session 212) is the pattern. Server only: it reads the site's own files.
import demandJson from "@/data/demand_growth.json";
import loadJson from "@/data/large_load_status.json";
import nyLoadJson from "@/data/nyiso_load_queue.json";
import queuesJson from "@/data/queues.json";
import * as clean from "@/lib/clean";
import {
  ASSUMED, BUYS, DEFAULTS, badMonth, cleanShare, expandSeries, hrefOf, inputsOf, last36, lastTwelve, monthsOf, monthsRuled, ruleWords, shortMonth, span,
  whenOf, years, type Inputs, type Month, type Ruled, type Span,
} from "@/lib/datacenter";
import { FLAT, FLEX, isOldParam, isScenarioParam, type Way, type Ways } from "@/lib/datacenter/finance";
import { DELIVERY, INDEX, yearFiles } from "@/lib/datacenterdata";
import type { DemandFile } from "@/lib/demandgrowth";
import { SLUGS } from "@/lib/demandgrowth";
import { waitsGrid } from "@/lib/howsoon";
import { span as loadSpan, type LoadFile } from "@/lib/largeload";
import { CLEAN, STRESS, type Slug } from "@/lib/mixdata";
import { viewOf, type QueueFile } from "@/lib/queues";
import * as stress from "@/lib/stress";
import type { Bad, Facts } from "./LoadScenarios";

export const DEMAND = demandJson as unknown as DemandFile;
export const QUEUES = queuesJson as unknown as QueueFile;
export const LOADS = loadJson as unknown as LoadFile;
// Session 140: NYISO's load interconnection requests, the one grid that publishes load in line by place
// (warehouse/connectors/nyiso_load_queue.py; the sheet "Load Projects" of its interconnection queue workbook).
export type NyRow = { queue_position: string; name: string; zone: string; zone_name: string; county: string; mw: number | null; request_date: string; request_date_printed: string;
  proposed_in_service_printed: string; status: string; end_use_words: string; utility: string; in_line: boolean; group: string; sheet: string; sheet_row: number };
export type NyZone = { zone: string; zone_name: string; requests: number; mw: number; by_status: { status: string; requests: number; mw: number }[] };
export type NyFile = { built: string; source: { name: string; url: string; report_page: string; retrieved: string; workbook_last_modified: string }; rule: { in_line: string };
  zones: NyZone[]; total: { requests: number; mw: number }; rows: NyRow[];
  // session 149: the file as the connector writes it while the rows are held internal (shown false): no request, no
  // zone, no megawatt; the placeholder's words and its reason on hover
  shown?: boolean; words?: string; why?: string };
export const NYLOAD = nyLoadJson as unknown as NyFile;
// Session 149 (the owner's ruling of 7 October 2026: the rows are shown only if NYISO's terms allow it; by their words
// they do not, docs/methods/datacenter_cost.md). The switch is the connector's (SHOWN in nyiso_load_queue.py): the
// page shows the megawatts in line and the fold of requests only when the file holds them.
export const NY_SHOWN = NYLOAD.shown !== false && Array.isArray(NYLOAD.rows) && Array.isArray(NYLOAD.zones);
export const NY_HELD_WORDS = NYLOAD.words ?? "NYISO's terms do not allow it";
export const NY_HELD_WHY = NYLOAD.why ?? "NYISO's legal notice confers no license in the content of its site and reserves its rights in their entirety. The load requests are held and not shown.";
export const NOWHERE = "not published anywhere yet";
export const FORESEEN = "if perfectly foreseen";
export const FORESEEN_WHY = "The same load with its hours chosen knowing every price of the year in advance: the most it could have saved. No operator knows them in advance; the figure beside it is what a rule decided before each hour would have paid.";
export const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

/** The page's inputs from an address (session 195: "Your load" no longer holds a power per GPU and an overhead ratio;
 * scenario A does, so the page's inputs carry the cited defaults). */
export function inputsFrom(q: Record<string, string | undefined>): Inputs {
  return { ...inputsOf(q, INDEX), gpu: DEFAULTS.gpu, pue: DEFAULTS.pue };
}

/** A flat load over the same months: each month's cost is the sum of its prices and its energy the hours held. */
const flatMonths = (ms: Month[]): Month[] => ms.map((r) => ({ ...r, cost: r.flat, energy: r.held, down: 0, tightDown: 0 }));
/** One way of running for the scenarios: its last twelve months and the bad month of its 36, per MW. Null when no
 * twelve complete months in a row are held. */
function wayOf(ms: Month[]): Way | null {
  const l = lastTwelve(ms);
  if (!l) return null;
  const s = span(l), w = last36(ms), b = badMonth(w?.months ?? []);
  if (s.per === null) return null;
  return { per: s.per, cost: s.cost, energy: s.energy, held: s.held, flatCost: s.flatCost, down: s.down, bad: b ? { m: b.m, per: b.cost / b.energy, cost: b.cost } : null, of: w?.months.length ?? 0 };
}
/** The bad month of one way of running, with the window it was ranked in: the headline's second number (session 195:
 * the headline is scenario A's, so both ways are handed over). Held wherever a month is, as the headline always was. */
function badOf(ms: Month[] | null): Bad | null {
  const w = ms ? last36(ms) : null, b = badMonth(w?.months ?? []);
  return w && b ? { m: b.m, per: b.cost / b.energy, of: w.months.length, first: w.months[0].m, to: w.to } : null;
}

/** Everything "Your load" computes for one address, in the order page.tsx computed it until session 213. */
export function loadModel(asked: Inputs, buyGiven: boolean, gridAsked: string | undefined, q: Record<string, string | undefined>) {
  let x = asked;
  const g = INDEX.grids[x.grid];
  let files: ReturnType<typeof yearFiles> = [], failed: string | null = null;
  try { files = yearFiles(x.grid); } catch (e) { failed = (e as Error).message; }
  const region = g?.regions.find((r) => r.id === x.region);
  let side = region?.[x.buy];
  const flex = x.run !== "flat", off = x.run === "hours" || x.run === "share";
  // session 140: a flexible load is judged on a rule it could follow (decided from day-ahead prices and the prior 30
  // days, lib/datacenter.ts ruleWeights): that is the page's figure. The same load with its hours chosen knowing the
  // year's prices stands beside it, labelled "if perfectly foreseen".
  const none: Ruled = { months: [], weights: new Map(), prices: new Map(), decided: 0, undecided: 0, da: false };
  let fore: Ruled = failed || !side ? none : monthsRuled(files, x.region, x.buy, x, "forecast");
  let ms: Month[] = fore.months;
  let l12 = lastTwelve(ms);
  // the address named no market and real time holds no twelve complete months here: day-ahead is shown when it does
  if (!buyGiven && x.buy === "rt" && !l12 && !failed && region?.da) {
    const da = monthsRuled(files, x.region, "da", x, "forecast");
    if (lastTwelve(da.months)) { x = { ...x, buy: "da" }; side = region.da; fore = da; ms = da.months; l12 = lastTwelve(ms); }
  }
  const noRule = flex && !!side && !failed && !fore.da;  // no day-ahead price is held here, so the rule cannot decide
  const hind: Ruled = !flex || failed || !side ? fore : monthsRuled(files, x.region, x.buy, x, "hindsight");
  const h12 = lastTwelve(hind.months), sh12: Span | null = h12 ? span(h12) : null;
  const ysH = years(hind.months), msH = new Map(hind.months.map((r) => [r.m, r]));
  const rule = ruleWords(x);
  const s12: Span | null = l12 ? span(l12) : null;
  const bad = badMonth(last36(ms)?.months ?? []);
  const badPer = bad ? bad.cost / bad.energy : null;
  const ys = years(ms);
  const place = `${x.region} in ${g?.name ?? x.grid}`;
  const market = BUYS[x.buy].toLowerCase();
  const heldFrom = side ? day(side.first) : "";
  const noYear = noRule
    ? `No day-ahead price is held for ${x.region}, and a flexible load decides from day-ahead prices. Its ${market} price is held from ${heldFrom || "no date"}.`
    : `Twelve complete months of ${market} prices are not held for ${x.region}: it is held from ${heldFrom || "no date"}. A month counts when at least 95 percent of its hours are held.`;
  const savedH = sh12 && sh12.flat !== null && sh12.per !== null ? sh12.flat - sh12.per : null;
  // the trading hub beside a load zone: a flat load there over the zone's own twelve months
  const refId = region?.ref && g?.regions.find((r) => r.id === region.ref)?.[x.buy] ? region.ref : null;
  const refFrom = l12 ? l12[0].m : "", refTo = l12 ? l12[11].m : "";
  const refMonths = refId && l12 ? monthsOf(files, refId, x.buy, { run: "flat", n: 0, pct: 0, shift: 0 }).filter((r) => r.m >= refFrom && r.m <= refTo && r.complete) : [];
  const ref12 = refMonths.length === 12 ? span(refMonths) : null;
  const l12Span = l12 ? `${shortMonth(l12[0].m)} to ${shortMonth(l12[11].m)}` : null;
  const saved = s12 && s12.flat !== null && s12.per !== null ? s12.flat - s12.per : null;
  const size = `${x.mw.toLocaleString("en-US")} MW`;

  // session 194: the two ways of running the scenarios compare, over the same twelve months. The way under "Your load"
  // is the page's own (`ms`); the other is a flat load over the same months, or, when "Your load" is flat, a load off in
  // the form's default number of hours a year under the same rule (it needs the region's day-ahead prices).
  const altFlex = { run: "hours" as const, n: DEFAULTS.n, pct: 0, shift: 0 };
  const flexWords = (y: Pick<Inputs, "run" | "n" | "pct" | "shift">) => (y.run === "hours" ? `off in the ${y.n.toLocaleString("en-US")} most expensive hours of each year` : y.run === "share" ? `off in the most expensive ${y.pct} percent of hours`
    : `${y.shift} percent of each day's energy moved to the day's cheapest hours`);
  let sets: [Month[] | null, Month[] | null] = [null, null];
  if (!failed && side) {
    if (flex) sets = [ms.length ? flatMonths(ms) : monthsOf(files, x.region, x.buy, { run: "flat", n: 0, pct: 0, shift: 0 }), ms];
    else sets = [ms, region?.da ? monthsRuled(files, x.region, x.buy, altFlex, "forecast").months : null];
  }
  const ways: Ways = [sets[0] ? wayOf(sets[0]) : null, sets[1] ? wayOf(sets[1]) : null];
  const noDa = `No day-ahead price is held for ${x.region}, and a flexible load decides from day-ahead prices.`;
  // session 195: the power per GPU and the overhead ratio are scenario A's; their defaults are the two the page cites
  const facts: Facts = { mw: x.mw, size, place: `${place}, ${market}`, span: l12Span, load: { run: flex ? FLEX : FLAT, gpu: DEFAULTS.gpu, pue: DEFAULTS.pue }, gpuSource: ASSUMED.gpu.source, pueSource: ASSUMED.pue.source, ways,
    words: ["the same in every hour", flexWords(flex ? x : altFlex)], why: [noYear, flex ? noYear : region?.da ? noYear : noDa], bads: [badOf(sets[0]), badOf(sets[1])] };
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([n, v]) => (isScenarioParam(n) || isOldParam(n)) && v !== undefined).sort(([a], [b]) => a.localeCompare(b))) as Record<string, string>;

  // the form's lists: every grid held, each region with what is held of it
  const grids = Object.fromEntries(Object.entries(INDEX.grids).map(([id, v]) => [id, { name: v.name,
    regions: v.regions.map((r) => { const s = r.rt ?? r.da!; return { id: r.id, held: `from ${shortMonth(s.first.slice(0, 7))}`, kind: r.kind ?? null, name: r.name ?? null }; }) }]));

  // every region of the grid over its own last twelve months, flat (until session 213 a fold; since, the download)
  const regionRows = (g?.regions ?? []).map((r) => {
    const s = r[x.buy];
    const name = r.name ?? (r.kind === "hub" ? "trading hub" : null);
    if (!s || failed) return { id: r.id, name, per: null as number | null, from: s?.first ?? null, hours: s?.hours ?? 0, sp: null as string | null };
    const m = monthsOf(files, r.id, x.buy, { run: "flat", n: 0, pct: 0, shift: 0 });
    const t = lastTwelve(m);
    return { id: r.id, name, per: t ? span(t).flat : null, from: s.first, hours: s.hours, sp: t ? `${shortMonth(t[0].m)} to ${shortMonth(t[11].m)}` : null };
  });

  // will the power be there: the grid's own figures from the mix, demand and (session 138) operator demand files
  const slug = x.grid as Slug;
  const sf = STRESS[slug], sy = sf ? stress.defaultYear(sf) : null;
  const peak = sf && sy ? stress.get(sf, sy, "peak_demand_mw") : null, peakAt = sf && sy ? stress.at(sf, sy, "peak_demand_mw") : null;
  const fuels = sf && sy ? stress.fuelRows(sf, sy).filter((f) => f.capacity !== null) : [];
  const ba = SLUGS[x.grid], area = ba ? DEMAND.areas[ba] : undefined;
  const growth = area?.years[String(DEMAND.last_year)];
  const tightYears = Object.entries(g?.demand ?? {}).filter(([, d]) => d.tight_hours !== undefined).sort(([a], [b]) => a.localeCompare(b));
  const tightRows = tightYears.map(([y, d]) => {
    const f = files.find((k) => k.year === Number(y));
    const when = f?.tight ? whenOf(Number(y), f.tight) : null;
    let down: number | null = null;
    const p = fore.prices.get(Number(y)), w = fore.weights.get(Number(y));
    if (f?.tight && flex && side && x.run !== "shift" && p && w) down = f.tight.filter((i) => p[i] !== null && w[i] === 0).length;
    return { y, d, when, down };
  });
  const lastTight = [...tightRows].reverse().find((r) => r.d.whole) ?? tightRows.at(-1);
  const zones = g?.zones ?? {};
  // a demand table held internally (its publisher's terms restrict republishing) is named, and nothing of it is shown
  const withheld = !!g?.demand_source?.startsWith("withheld:");

  // how clean: the grid's figures from the tables behind /mix?view=clean
  const cf = CLEAN[slug], cy = cf ? clean.defaultYear(cf) : null, cv = cf && cy ? clean.yearView(cf, cy) : null;
  // session 140: this load's own hours. The grid's carbon-free share in each hour, weighted by the load in that hour
  // (under the rule above), over the hours of the year where the price and the share are both held.
  const cFile = cy ? files.find((k) => k.year === Number(cy)) : undefined;
  const cP = cy ? fore.prices.get(Number(cy)) : undefined, cW = cy ? fore.weights.get(Number(cy)) : undefined;
  const own = cFile?.clean && cP && cW ? cleanShare(expandSeries(cFile.clean, cFile.hours), cP, cW) : null;

  // how soon: the interconnection queue, and ERCOT's large-load status
  const qv = viewOf(QUEUES, x.grid, "all")?.whole ?? null;
  const ll = x.grid === "ercot" ? loadSpan(LOADS) : null;

  // the names of the seven grids an address can name, for the two blocks that follow the address (sessions 154 and 163)
  const gridNames: Record<string, string> = { ...Object.fromEntries(Object.entries(INDEX.blank).map(([id, v]) => [id, v.name])), ...Object.fromEntries(Object.entries(INDEX.grids).map(([id, v]) => [id, v.name])) };
  const delivery = x.grid === "ercot" ? DELIVERY.rows : [];
  const matrix = x.grid === "ercot" ? DELIVERY.matrix ?? [] : [];
  const utilities = [...new Set(delivery.map((r) => r.utility))];
  const waitsFor = waitsGrid(gridAsked, x.grid);

  return {
    x, g, files, failed, region, side, flex, off, fore, ms, l12, noRule, hind, h12, sh12, ysH, msH, rule, s12, bad, badPer, ys, place, market, heldFrom, noYear, savedH, refId, ref12,
    l12Span, saved, size, ways, facts, scenarioParams, grids, regionRows, slug, sf, sy, peak, peakAt, fuels, growth, tightRows, lastTight, zones, withheld, cf, cy, cv, cFile, own, qv, ll,
    gridNames, delivery, matrix, utilities, waitsFor, href: hrefOf(x),
  };
}
export type LoadModel = ReturnType<typeof loadModel>;
