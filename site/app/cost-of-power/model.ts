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
import { FLAT, FLEX, SITE_B, isOldParam, isScenarioParam, type Way, type Ways } from "@/lib/datacenter/finance";
import { ownWay, readAnswers, waysOf, type Ruled as AnswerRuled } from "@/lib/datacenter/answers";
import { deliveryOf, utilitiesOf } from "@/lib/datacenter/delivery";
import { blockOf as rulesBlockOf, docketWords, rulesGrid } from "@/lib/rules";
import { rulesFile } from "@/lib/rulesdata";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { WINDOW_RE, chosen, windowWords, type PriceYear } from "@/lib/priceyears";
import { priceYears } from "@/lib/priceyearsread";
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
/** Session 352: one way of running over a window of price years: the table's price per MWh (price_years_by_window, the
 * page's own run), and the page's own complete months inside the window for the cost, the energy and the hours, a year
 * (the averages over the years they cover). The bad month stays the last 36 months'. Null when the window holds no
 * complete month here. */
function wayWindow(ms: Month[], w: PriceYear): Way | null {
  const inside = ms.filter((r) => r.complete && r.m >= w.from && r.m <= w.to);
  if (!inside.length) return null;
  const k = w.kind === "year" ? 1 : w.kind === "avg_3y" ? 3 : w.kind === "avg_7y" ? 7 : Math.max(1, inside.length / 12);
  const t = span(inside), win = last36(ms), b = badMonth(win?.months ?? []);
  return { per: w.value, cost: t.cost / k, energy: t.energy / k, held: t.held / k, flatCost: t.flatCost / k, down: t.down / k,
    bad: b ? { m: b.m, per: b.cost / b.energy, cost: b.cost } : null, of: win?.months.length ?? 0 };
}

/** The bad month of one way of running, with the window it was ranked in: the headline's second number (session 195:
 * the headline is scenario A's, so both ways are handed over). Held wherever a month is, as the headline always was. */
function badOf(ms: Month[] | null): Bad | null {
  const w = ms ? last36(ms) : null, b = badMonth(w?.months ?? []);
  return w && b ? { m: b.m, per: b.cost / b.energy, of: w.months.length, first: w.months[0].m, to: w.to } : null;
}

/** Session 236: scenario B's own site from the address, `bsite=<grid>:<region>`. Null when the address names none, names
 * a grid or a region the page's files do not hold, or names the site of "Your load" (B is then at A's site, as before). */
export function siteBOf(raw: string | undefined, x: Pick<Inputs, "grid" | "region">): { grid: string; region: string } | null {
  if (!raw) return null;
  const i = raw.indexOf(":");
  const grid = i < 0 ? raw : raw.slice(0, i), region = i < 0 ? "" : raw.slice(i + 1);
  const g = INDEX.grids[grid];
  if (!g || !g.regions.some((r) => r.id === region) || (grid === x.grid && region === x.region)) return null;
  return { grid, region };
}

/** Everything "Your load" computes for one address, in the order page.tsx computed it until session 213. Session 228:
 * and the three answers beside "What will it pay?" (lib/datacenter/reads.ts), read from the live set. */
export async function loadModel(asked: Inputs, buyGiven: boolean, gridAsked: string | undefined, q: Record<string, string | undefined>) {
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
  let ways: Ways = [sets[0] ? wayOf(sets[0]) : null, sets[1] ? wayOf(sets[1]) : null];
  // session 352: the price years the scenarios are priced on (price_years_by_window, the page's own run at its defaults:
  // off in 100 hours a year, off in 5 percent of hours, 20 percent of each day's energy shifted). The flat way reads
  // flat_<market>; the second way the flexible run shown (or, for a flat load, the hours-off run beside it), only at the
  // run's default. The windows with a stress event taken out are not offered here.
  const atDefault = (r: string) => (r === "hours" ? x.n === DEFAULTS.n : r === "share" ? x.pct === DEFAULTS.pct : r === "shift" ? x.shift === DEFAULTS.shift : true);
  const pyConfigs: [string, string | null] = [`flat_${x.buy}`, flex ? (atDefault(x.run) ? `${x.run}_${x.buy}` : null) : `hours_${x.buy}`];
  const pyEntity = `${x.grid}:${x.region}`;
  const pyReads = !failed && side ? await Promise.all(pyConfigs.map((c) => (c ? priceYears("datacenter", pyEntity, c) : Promise.resolve(null)))) : [null, null];
  const pyLists = pyReads.map((r) => (r?.ok ? r.ws.filter((w) => w.kind !== "all_less") : [])) as [PriceYear[], PriceYear[]];
  const pyWs = pyLists[0];
  const pyId = q.py && WINDOW_RE.test(q.py) ? q.py : null;
  const win = chosen(pyWs, pyId);
  if (win) {
    const second = chosen(pyLists[1], win.id);
    ways = [sets[0] ? wayWindow(sets[0], win) : null, sets[1] && second ? wayWindow(sets[1], second) : null];
  }
  const noDa = `No day-ahead price is held for ${x.region}, and a flexible load decides from day-ahead prices.`;
  // session 195: the power per GPU and the overhead ratio are scenario A's; their defaults are the two the page cites
  const facts: Facts = { mw: x.mw, size, place: `${place}, ${market}`, span: win ? windowWords(win).label.replace(" (default)", "") : l12Span, load: { run: flex ? FLEX : FLAT, gpu: DEFAULTS.gpu, pue: DEFAULTS.pue }, gpuSource: ASSUMED.gpu.source, pueSource: ASSUMED.pue.source, ways,
    words: ["the same in every hour", flexWords(flex ? x : altFlex)], why: [noYear, flex ? noYear : region?.da ? noYear : noDa], bads: [badOf(sets[0]), badOf(sets[1])] };
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([n, v]) => (isScenarioParam(n) || isOldParam(n)) && v !== undefined).sort(([a], [b]) => a.localeCompare(b))) as Record<string, string>;

  // session 236 (the owner's chain prompt of 12 October 2026: A and B compare two sites or two contracts): scenario B
  // may stand at a site of its own, another region of the grid or another grid. Its two ways of running are computed
  // here exactly as A's are above (the same market, the same way "Your load" runs, the same rule), from that site's
  // own price files and over that site's own last twelve months. With no site named B is at A's site and `facts.b` is
  // null: every figure is then what it was.
  const bSite = !failed && side ? siteBOf(q[SITE_B], x) : null;
  const gB = bSite ? INDEX.grids[bSite.grid] : undefined, regionB = bSite ? gB?.regions.find((r) => r.id === bSite.region) : undefined;
  let filesB: ReturnType<typeof yearFiles> = [], failedB: string | null = null;
  if (bSite) { try { filesB = bSite.grid === x.grid ? files : yearFiles(bSite.grid); } catch (e) { failedB = (e as Error).message; } }
  const sideB = regionB?.[x.buy];
  const foreB: Ruled = bSite && sideB && !failedB ? monthsRuled(filesB, bSite.region, x.buy, x, "forecast") : none;
  const l12B = lastTwelve(foreB.months);
  const placeB = bSite ? `${bSite.region} in ${gB?.name ?? bSite.grid}` : "";
  if (bSite) {
    let setsB: [Month[] | null, Month[] | null] = [null, null];
    if (sideB && !failedB) {
      if (flex) setsB = [foreB.months.length ? flatMonths(foreB.months) : monthsOf(filesB, bSite.region, x.buy, { run: "flat", n: 0, pct: 0, shift: 0 }), foreB.months];
      else setsB = [foreB.months, regionB?.da ? monthsRuled(filesB, bSite.region, x.buy, altFlex, "forecast").months : null];
    }
    const noYearB = failedB ? `The price files of ${gB?.name ?? bSite.grid} could not be read: ${failedB}`
      : !sideB ? `No ${market} price is held for ${placeB}.`
      : flex && !foreB.da ? `No day-ahead price is held for ${bSite.region}, and a flexible load decides from day-ahead prices. Its ${market} price is held from ${day(sideB.first)}.`
      : `Twelve complete months of ${market} prices are not held for ${bSite.region}: it is held from ${day(sideB.first)}. A month counts when at least 95 percent of its hours are held.`;
    // session 352: under a window of price years, B at its own site reads that site's own rows of the table, the same window
    const pyB = win && sideB && !failedB ? await Promise.all(pyConfigs.map((c) => (c ? priceYears("datacenter", `${bSite.grid}:${bSite.region}`, c) : Promise.resolve(null)))) : null;
    const winB = pyB ? pyB.map((r) => (r?.ok ? chosen(r.ws, win!.id) : null)) : null;
    facts.b = { grid: bSite.grid, region: bSite.region, place: `${placeB}, ${market}`, span: win ? windowWords(win).label.replace(" (default)", "") : l12B ? `${shortMonth(l12B[0].m)} to ${shortMonth(l12B[11].m)}` : null,
      ways: winB ? [setsB[0] && winB[0] ? wayWindow(setsB[0], winB[0]) : null, setsB[1] && winB[1] ? wayWindow(setsB[1], winB[1]) : null]
        : [setsB[0] ? wayOf(setsB[0]) : null, setsB[1] ? wayOf(setsB[1]) : null], bads: [badOf(setsB[0]), badOf(setsB[1])],
      why: [noYearB, flex ? noYearB : regionB?.da ? noYearB : `No day-ahead price is held for ${bSite.region}, and a flexible load decides from day-ahead prices.`] };
  }
  // the sites scenario B can be given: every region of every grid held, by grid (the form's list)
  const sitesB = Object.entries(INDEX.grids).map(([id, v]) => ({ grid: id, name: v.name, regions: v.regions.filter((r) => r[x.buy]).map((r) => ({ id: r.id, kind: r.kind ?? null })) }));

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

  // session 228: the three answers. Their check key names the address the figures are for (the inputs in force, so a
  // day-ahead fallback is in it) and the size; check-values recomputes each from its own read of the same tables
  const answersKey = `grid=${x.grid}&region=${encodeURIComponent(x.region)}&buy=${x.buy}&run=${x.run}&n=${x.n}&pct=${x.pct}&shift=${x.shift}&mw=${x.mw}`;
  const l12Labels = l12 ? l12.map((r) => r.m) : [];
  const waySpecs = waysOf(x, { n: DEFAULTS.n, shift: DEFAULTS.shift });
  const ruled = {} as Record<"flat" | "flex" | "shift", AnswerRuled>;
  if (!failed && side) for (const k of ["flat", "flex", "shift"] as const) ruled[k] = monthsRuled(files, x.region, x.buy, waySpecs[k], "forecast");
  const answers = !failed && side && l12 ? await attempt(() => readAnswers({ grid: x.grid, mw: x.mw, l12: l12Labels, behind: g?.std_hours_behind_utc ?? 0, ruled,
    rows: (t, p) => rest<Record<string, unknown>>(t, p, HOURLY) })) : null;
  const answerFacts = { pre: answersKey, place: `${x.region} in ${g?.name ?? x.grid}`, size, span: l12Span, gridName: g?.name ?? x.grid, own: ownWay(x),
    words: { flat: "the same in every hour", flex: flexWords(waySpecs.flex), shift: flexWords(waySpecs.shift) } as Record<"flat" | "flex" | "shift", string>, stdName: g?.std_name ?? "standard time" };
  // session 236: the same three answers at scenario B's own site, when it has one: the same reads and arithmetic for
  // that site's address (its check key names that site), over that site's own last twelve months
  const answersKeyB = bSite ? `grid=${bSite.grid}&region=${encodeURIComponent(bSite.region)}&buy=${x.buy}&run=${x.run}&n=${x.n}&pct=${x.pct}&shift=${x.shift}&mw=${x.mw}` : "";
  const ruledB = {} as Record<"flat" | "flex" | "shift", AnswerRuled>;
  if (bSite && sideB && !failedB) for (const k of ["flat", "flex", "shift"] as const) ruledB[k] = monthsRuled(filesB, bSite.region, x.buy, waySpecs[k], "forecast");
  const answersB = bSite && sideB && !failedB && l12B ? await attempt(() => readAnswers({ grid: bSite.grid, mw: x.mw, l12: l12B.map((r) => r.m), behind: gB?.std_hours_behind_utc ?? 0, ruled: ruledB,
    rows: (t, p) => rest<Record<string, unknown>>(t, p, HOURLY) })) : null;
  const answerFactsB = bSite ? { ...answerFacts, pre: answersKeyB, place: placeB, span: l12B ? `${shortMonth(l12B[0].m)} to ${shortMonth(l12B[11].m)}` : null, gridName: gB?.name ?? bSite.grid, stdName: gB?.std_name ?? "standard time" } : null;
  // session 236: Texas's delivery charges by component, USD per MWh for a flat load of the reader's size
  // (lib/datacenter/delivery.ts); the tariff's own lines are in the download
  const deliveryParts = x.grid === "ercot" ? utilitiesOf(DELIVERY.rows).map((u) => deliveryOf(DELIVERY.rows, u, x.mw)) : [];
  // the rules in motion for the grid, from the site's own file (lib/rules.ts), counted; the rows are in the download
  const rgrid = rulesGrid(gridAsked, x.grid);
  const rb = rulesBlockOf(rulesFile().file, rgrid);
  const rulesNewest = rb.state === "shown" && rb.rows.length ? rb.rows[0] : null;
  const rules = { count: rb.state === "shown" ? rb.rows.length : 0, newest: rulesNewest ? rulesNewest.date : null,
    words: rb.state === "paused" ? `${rb.words ?? "paused while terms are reviewed"}.`
      : rb.state === "shown" ? `${rb.rows.length} proceedings and orders on large loads are in motion for ${gridNames[rgrid] ?? rgrid.toUpperCase()} in the public dockets held${rulesNewest ? `, the newest ${docketWords(rulesNewest)} (${rulesNewest.date})` : ""}; each is in the download, with its document.`
      : `No proceeding or order on large loads is held for ${gridNames[rgrid] ?? rgrid.toUpperCase()} in the public dockets read.` };

  return {
    bSite, sitesB, answersB, answersKeyB, answerFactsB, deliveryParts,
    answers, answersKey, answerFacts, rules,
    x, g, files, failed, region, side, flex, off, fore, ms, l12, noRule, hind, h12, sh12, ysH, msH, rule, s12, bad, badPer, ys, place, market, heldFrom, noYear, savedH, refId, ref12,
    l12Span, saved, size, ways, facts, scenarioParams, grids, regionRows, slug, sf, sy, peak, peakAt, fuels, growth, tightRows, lastTight, zones, withheld, cf, cy, cv, cFile, own, qv, ll,
    gridNames, delivery, matrix, utilities, waitsFor, href: hrefOf(x),
    pyWs, pyRead: pyReads[0]?.ok ?? false, pyOffered: !failed && !!side, win,
  };
}
export type LoadModel = Awaited<ReturnType<typeof loadModel>>;
