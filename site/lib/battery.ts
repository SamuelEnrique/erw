// Session 38: the home battery game's rules and its perfect-foresight optimum. Shared by the game (the browser), the
// score route (the server recomputes every score from the actions and the real prices) and the test
// (site/scripts/test-battery.mjs, run by tests/test_session38.py). No imports: Node runs this file as it is.
//
// The battery is an assumption, labelled so on the page: 13.5 kWh usable, 5 kW, 90 percent round trip (the square root
// of it on the way in and again on the way out), half full at the start. Each 15-minute interval the player charges
// (buys at the interval's price), discharges (sells) or idles. The VPP call is a game rule, not a real program's
// terms: in the day's highest-price hour, energy delivered earns a bonus of that hour's mean price (never below zero).
//
// Session 50 (game v2): the battery's settings are the player's, within stated ranges (SETTINGS); a difficulty sets
// what the game shows and enforces (DIFFICULTIES): on Hard, a backup reserve the battery may not discharge below and a
// degradation cost per kWh discharged from the battery. Every function takes the rules (rulesOf) and defaults to the
// session 38 battery on Normal. docs/methods/battery_game.md.
//
// Session 63 (game v3), three game rules, each labelled so on the page: (1) money: every play starts with $5
// (START_MONEY) and ends in the interval its money falls below $0; (2) on Hard, a grid emergency (EMERGENCY): the day's
// dearest clock hour climbs toward the price cap, then a two-hour outage in which the grid is down and the house runs on
// its battery alone (the backup reserve included); if the battery cannot carry the house through an interval, the lights
// go out and the round ends there, its score kept; (3) the presets carry "-v3", so v3 plays are ranked only against v3
// plays. The optimum stays exact under these rules: two paths at the same charge, the one with more money is never worse.
//
// Session 66 (game v4), each a game rule, labelled so on the page: (1) lights out costs money (LIGHTS_OUT): the round
// still ends, and every remaining interval of the outage charges the house's unserved energy at a whole multiple of the
// price cap, so the perfect battery never gives up the house where it can keep it; (2) the spiked price is never shown
// as a real one (shownPrices: the number carries SPIKE_LABEL and the real price beside it); (3) the end screen's hour
// (worstHour), from simulate()'s own per-interval earnings; (4) Hard's add-ons (ADDONS), off by default, the first a
// rooftop solar array whose output follows the grid's real solar fleet (a level's `solar`); (5) presets end "-v4" and
// carry the add-ons.
//
// Session 70 (still v4, which was not yet released): (1) the lights-out charge is priced at Texas's value of lost load
// (LIGHTS_OUT.usdPerMwh), not at a multiple of the cap found by search; (2) going dark at any point of the outage
// charges the unserved energy of the whole outage, not only of what is left of it; (3) the roof is curtailed, earning
// nothing, when the price is below zero and the battery is not charging (roofSale).

export type Settings = { kwh: number; kw: number; rte: number; reserve: number; deg: number };
export type Difficulty = "easy" | "normal" | "hard";

/** Each setting: its default, range and step, and where the default comes from. Lazard, "Levelized Cost of Energy+",
 * June 2025, LCOS v10.0, Key Assumptions, Residential Standalone (0.006 MW / 0.025 MWh): initial capital cost (DC)
 * USD 721 to 1,338 per kWh, lifetime storage output 158 MWh, efficiency 91 to 88 percent. */
export const SETTINGS: Record<keyof Settings, { label: string; unit: string; def: number; min: number; max: number; step: number; source: string }> = {
  kwh: { label: "Usable energy", unit: "kWh", def: 13.5, min: 5, max: 30, step: 0.5, source: "assumption: one home battery's usable energy, the session 38 game's" },
  kw: { label: "Continuous power", unit: "kW", def: 5, min: 1, max: 11.5, step: 0.5, source: "assumption, the session 38 game's; ERCOT's ADER governing document gives +/-5 kW as its example of a battery's rated dispatchable range" },
  rte: { label: "Round-trip efficiency", unit: "percent", def: 0.9, min: 0.75, max: 0.95, step: 0.01, source: "assumption, inside Lazard's 88 to 91 percent for residential standalone storage (LCOS v10.0, 2025)" },
  reserve: { label: "Backup reserve", unit: "percent", def: 0.2, min: 0, max: 0.5, step: 0.05, source: "assumption: the share kept back for an outage, 20 percent by default; enforced on Hard" },
  deg: { label: "Degradation cost", unit: "USD per kWh discharged", def: 0.11, min: 0, max: 0.3, step: 0.01, source: "Lazard LCOS v10.0 (2025), residential standalone: the low end of its capital cost, USD 721 per kWh x 25 kWh, over its lifetime storage output, 158 MWh, is USD 0.114 per kWh, rounded to 0.11; charged on Hard" },
};
export const DEFAULT_SETTINGS: Settings = { kwh: SETTINGS.kwh.def, kw: SETTINGS.kw.def, rte: SETTINGS.rte.def, reserve: SETTINGS.reserve.def, deg: SETTINGS.deg.def };

export const DIFFICULTIES: Record<Difficulty, { label: string; forecastHours: number; reserve: boolean; degradation: boolean; emergency: boolean; addons: boolean; what: string }> = {
  easy: { label: "Easy", forecastHours: 3, reserve: false, degradation: false, emergency: false, addons: false, what: "the next three hours show as a band: each clock hour's lowest to highest real price" },
  normal: { label: "Normal", forecastHours: 0, reserve: false, degradation: false, emergency: false, addons: false, what: "no forecast, no reserve, no degradation cost" },
  hard: { label: "Hard", forecastHours: 0, reserve: true, degradation: true, emergency: true, addons: true, what: "no forecast; the backup reserve is enforced, each kWh discharged costs the degradation cost, and a grid emergency strikes: the price spikes toward the cap, then a two-hour outage runs the house on the battery" },
};

/** Session 63: the money a play starts with, USD (a game rule). Below $0 the game ends. */
export const START_MONEY = 5;
/** Session 63: Hard's grid emergency (game rules). The spike: the day's dearest clock hour (vppHour on the real prices)
 * climbs toward the cap, each of its four intervals a share of the way from its real price to the cap; the cap is
 * ERCOT's system-wide offer cap since 2023 (USD 5,000/MWh), used for every grid. The outage: the eight intervals (two
 * hours) after the spike hour, the grid down: no buying or selling, and the house draws 1.5 kW from the battery (an
 * assumption: a home's evening load with air conditioning; the reserve is for exactly this). */
export const EMERGENCY = { cap: 5000, ramp: [0.25, 0.5, 0.75, 0.9], outageIntervals: 8, houseKw: 1.5 };
export const RULES_VERSION = "v4";
/** Session 66: lights out costs money (a game rule). Session 70: the round still ends, and if the lights go out at any
 * point of the outage the house is charged for the unserved energy of the whole outage (EMERGENCY.houseKw for every
 * interval of it, less what a rooftop array makes in each) at Texas's value of lost load.
 * usdPerMwh: the value of lost load the Public Utility Commission of Texas approved for the ERCOT region at its open
 * meeting of 2024-08-29 (Project No. 55837; no written order, the Commission's press release of that day states it).
 * study: the one-hour, ERCOT-wide value of ERCOT's study by The Brattle Group, "Value of Lost Load Study for the ERCOT
 * Region" (filed in Project No. 55837 on 2024-08-22), which the Commission rounded. residential: the same study's
 * one-hour value for residential customers alone. All 2024 dollars per MWh of unserved energy. The game uses the
 * system-wide figure, on California's days too. docs/methods/battery_game.md, "Version 4". */
export const LIGHTS_OUT = {
  usdPerMwh: 35_000, study: 35_685, residential: 3_964,
  release: "https://ftp.puc.texas.gov/public/puct-info/agency/resources/pubs/news/2024/PUCT_Adopts_Reliability_Standard_for_the_ERCOT_Market.pdf",
  report: "https://www.brattle.com/wp-content/uploads/2024/09/Value-of-Lost-Load-Study-for-the-ERCOT-Region.pdf",
};
/** Session 66: what a spiked price carries wherever it is shown. */
export const SPIKE_LABEL = "game rule, not a real price";

/** Session 66: Hard's add-ons, optional switches, off by default. A preset names the ones that are on, so a board ranks
 * only plays with the same rules and add-ons. To add one: a key here, its rule in rulesOf, simulate and optimum, and
 * what it needs from the level where the page and the server check it (the solar shape). */
export type AddonKey = "solar";
export const ADDONS: Record<AddonKey, { label: string; what: string }> = {
  solar: { label: "Rooftop solar", what: "a 5 kW rooftop array (a game rule). Each fifteen minutes it makes 5 kW times the real output, per MW installed, of the grid's whole solar fleet that hour: the fleet's shape, not one roof's. Its power is sold at that moment's price, or goes into the battery for free while you charge; when the price is below zero and the battery is not charging, the roof is switched off and earns nothing, as a real system would be, instead of paying to export; in the outage it runs the house first, and what is left over charges the battery" },
};
/** The rooftop array's size, kW (a game rule). */
export const SOLAR = { kw: 5 };
export const ADDON_KEYS = Object.keys(ADDONS) as AddonKey[];
/** The add-ons a play may switch on: known keys, each once, and none where the difficulty has no add-ons. */
export function validAddons(x: unknown, d: Difficulty): x is AddonKey[] {
  if (!Array.isArray(x) || new Set(x).size !== x.length || !x.every((k) => typeof k === "string" && k in ADDONS)) return false;
  return x.length === 0 || DIFFICULTIES[d].addons;
}
/** A level's solar shape: one number per interval (the fleet's output per MW installed), every one present. */
export function validSolar(x: unknown, n: number): x is number[] {
  return Array.isArray(x) && x.length === n && x.every((v) => typeof v === "number" && Number.isFinite(v));
}

/** The rules a play is scored by: the battery's settings, with the reserve and the degradation cost only where the
 * difficulty enforces them; session 66: the lights-out penalty and the add-ons (only where the difficulty has them). */
export type Rules = {
  kwh: number; kw: number; eta: number; reserveKwh: number; deg: number; start: number; minutes: number; money0: number; emergency: boolean; houseKw: number;
  voll: number; solarKw: number;  // voll: what unserved house energy costs, USD/MWh (LIGHTS_OUT.usdPerMwh)
};
export function rulesOf(s: Settings = DEFAULT_SETTINGS, d: Difficulty = "normal", addons: AddonKey[] = []): Rules {
  const D = DIFFICULTIES[d];
  return { kwh: s.kwh, kw: s.kw, eta: Math.sqrt(s.rte), reserveKwh: D.reserve ? s.kwh * s.reserve : 0, deg: D.degradation ? s.deg : 0, start: s.kwh * 0.5, minutes: 15,
    money0: START_MONEY, emergency: D.emergency, houseKw: EMERGENCY.houseKw,
    voll: LIGHTS_OUT.usdPerMwh, solarKw: D.addons && addons.includes("solar") ? SOLAR.kw : 0 };
}

/** Session 63: the prices a play sees and is scored at, and Hard's emergency windows (intervals, inclusive), or null. */
export function emergencyOf(prices: number[], r: Rules): { prices: number[]; spike: { first: number; last: number } | null; outage: { first: number; last: number } | null } {
  if (!r.emergency || prices.length < 4) return { prices, spike: null, outage: null };
  const v = vppHour(prices);
  const p = prices.slice();
  for (let k = 0; k < 4 && v.first + k < p.length; k++) {
    const i = v.first + k;
    if (p[i] < EMERGENCY.cap) p[i] = p[i] + (EMERGENCY.cap - p[i]) * EMERGENCY.ramp[k];
  }
  const o0 = v.last + 1, o1 = Math.min(prices.length - 1, v.last + EMERGENCY.outageIntervals);
  return { prices: p, spike: { first: v.first, last: v.last }, outage: o0 <= o1 ? { first: o0, last: o1 } : null };
}
/** Session 63: the charge the house takes from the battery in one outage interval, kWh (the meter's need over the
 * battery's one-way efficiency), and the whole outage's. */
export const outageDraw = (r: Rules) => (r.houseKw * r.minutes) / 60 / r.eta;

/** Session 66: what the rooftop array makes in each interval, kWh at the meter: solarKw times the fleet's output per MW
 * installed, which the game keeps between 0 and 1 (a roof draws nothing at night, where EIA reports a fleet's station
 * use as negative output, and makes no more than its rating). All zero without the add-on. With it, a shape of the
 * day's length is required: a missing one is never filled. */
export function solarKwh(prices: number[], r: Rules, solar?: number[] | null): number[] {
  if (r.solarKw <= 0) return prices.map(() => 0);
  if (!validSolar(solar, prices.length)) throw new Error("rooftop solar: no solar shape for this day");
  return solar.map((v) => (r.solarKw * Math.min(1, Math.max(0, v)) * r.minutes) / 60);
}
/** Session 66: one outage interval. The roof carries the house first; what is left over charges the battery (up to its
 * power and its room; the rest is lost, since the grid is down); what the roof does not cover comes from the battery.
 * The new state of charge, or null when the battery cannot carry the house: lights out. */
function outageStep(soc: number, sun: number, r: Rules): number | null {
  const need = (r.houseKw * r.minutes) / 60;
  if (sun >= need) {
    const stored = Math.min((sun - need) * r.eta, ((r.kw * r.minutes) / 60) * r.eta, r.kwh - soc);
    return stored <= 0 ? soc : stored === r.kwh - soc ? r.kwh : soc + stored;
  }
  const taken = (need - sun) / r.eta;
  return soc + 1e-12 < taken ? null : soc - taken;
}
/** Session 66: the house's unserved energy from interval `first` to interval `last` (kWh at the meter: the house's need
 * less what the roof makes), and what it costs at the value of lost load, USD. Session 70: lights out is charged for the
 * whole outage, so both callers pass the outage's first and last interval, whenever the lights went out. */
function unserved(first: number, last: number, sun: number[], r: Rules): { kwh: number; usd: number } {
  const need = (r.houseKw * r.minutes) / 60;
  let kwh = 0;
  for (let j = first; j <= last; j++) kwh += Math.max(0, need - sun[j]);
  return { kwh, usd: (kwh * r.voll) / 1000 };
}
/** Session 70: what the roof's power earns in one interval outside the outage (USD), and how much of it is curtailed
 * (kWh). At a price of zero or more all of it earns the price (sold, or taken by the charging battery in place of a
 * purchase: the same money). Below zero a real system does not pay to export: the roof's power is used only as far as
 * the charging battery takes it (`stored`, the kWh this interval's charge put into the battery; that power then replaces
 * grid power the battery would have been paid to take), and the rest is curtailed and earns nothing. So with the
 * battery idle, selling or full, a negative price curtails the whole roof. */
function roofSale(sun: number, price: number, stored: number, r: Rules): { usd: number; curtailed: number } {
  if (price >= 0 || sun <= 0) return { usd: (sun * price) / 1000, curtailed: 0 };
  const used = Math.min(sun, Math.max(0, stored) / r.eta);
  return { usd: (used * price) / 1000, curtailed: sun - used };
}

export const BATTERY = { kwh: DEFAULT_SETTINGS.kwh, kw: DEFAULT_SETTINGS.kw, roundTrip: DEFAULT_SETTINGS.rte, startShare: 0.5, minutes: 15 };
export const FLEET = 10_000;
export type Action = -1 | 0 | 1; // 1 charge, 0 idle, -1 discharge

const ETA = Math.sqrt(BATTERY.roundTrip);
const V1 = rulesOf();

/** The settings within their ranges and on their steps, and nothing else. */
export function validSettings(x: unknown): x is Settings {
  if (!x || typeof x !== "object") return false;
  const o = x as Record<string, unknown>;
  if (!Object.keys(o).every((k) => k in SETTINGS)) return false;
  return (Object.keys(SETTINGS) as (keyof Settings)[]).every((k) => {
    const v = o[k], r = SETTINGS[k];
    if (typeof v !== "number" || !Number.isFinite(v) || v < r.min - 1e-9 || v > r.max + 1e-9) return false;
    const n = (v - r.min) / r.step;
    return Math.abs(n - Math.round(n)) < 1e-6;
  });
}
export const validDifficulty = (x: unknown): x is Difficulty => x === "easy" || x === "normal" || x === "hard";

/** The leaderboard's preset: the difficulty and the settings that change the score (the reserve and the degradation
 * cost only on Hard), so only plays under the same rules are ranked together. Session 66: then the add-ons that are on,
 * in the order of ADDONS, then the rules' version: hard:13.5-5-90-r20-d0.11-solar-v4. */
export function presetOf(s: Settings, d: Difficulty, addons: AddonKey[] = []): string {
  const base = `${d}:${s.kwh}-${s.kw}-${Math.round(s.rte * 100)}`;
  const on = DIFFICULTIES[d].addons ? ADDON_KEYS.filter((k) => addons.includes(k)).map((k) => `-${k}`).join("") : "";
  return `${d === "hard" ? `${base}-r${Math.round(s.reserve * 100)}-d${s.deg}` : base}${on}-${RULES_VERSION}`;
}
export const DEFAULT_PRESET = presetOf(DEFAULT_SETTINGS, "normal");
export type RulesVersion = "v2" | "v3" | "v4";
const PRESET = /^(easy|normal|hard):(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)-(\d+)(?:-r(\d+)-d(\d+(?:\.\d+)?))?((?:-[a-z]+)*)(?:-(v3|v4))?$/;

/** Session 55: a preset back to its settings and difficulty, or null when it is not a preset presetOf writes: an
 * unknown difficulty, a setting outside its range or off its step, the reserve and degradation on a level other than
 * Hard (or missing on Hard), or any other spelling of the same rules. The read route of the leaderboard refuses the rest.
 * Session 66: a v4 preset ends "-v4" and may name add-ons before it; boards from before stay readable, never written:
 * a v3 preset ends "-v3", a v2 one has no version, and neither has add-ons. */
export function parsePreset(raw: unknown): { settings: Settings; difficulty: Difficulty; addons: AddonKey[]; version: RulesVersion } | null {
  if (typeof raw !== "string" || raw.length > 64) return null;
  const m = PRESET.exec(raw);
  if (!m) return null;
  const difficulty = m[1] as Difficulty;
  const version = (m[8] ?? "v2") as RulesVersion;
  if ((difficulty === "hard") !== (m[5] !== undefined)) return null;
  const addons = m[7] ? m[7].slice(1).split("-") : [];
  if (!validAddons(addons, difficulty) || (addons.length > 0 && version !== RULES_VERSION)) return null;
  const settings: Settings = {
    kwh: Number(m[2]), kw: Number(m[3]), rte: Number(m[4]) / 100,
    reserve: m[5] !== undefined ? Number(m[5]) / 100 : DEFAULT_SETTINGS.reserve, deg: m[6] !== undefined ? Number(m[6]) : DEFAULT_SETTINGS.deg,
  };
  // the one spelling presetOf writes: the same numbers, the add-ons in ADDONS' order
  const body = m[8] ? raw.slice(0, -3) : raw;
  if (!validSettings(settings) || presetOf(settings, difficulty, addons) !== `${body}-${RULES_VERSION}`) return null;
  return { settings, difficulty, addons, version };
}
/** A preset in words; a board from before the current rules says which rules it was played under. */
export function presetLabel(p: string): string {
  const m = PRESET.exec(p);
  if (!m) return p;
  const d = m[1] as Difficulty;
  const old = m[8] === RULES_VERSION ? "" : ` (${m[8] ?? "v2"} rules)`;
  const on = (m[7] ? m[7].slice(1).split("-") : []).map((k) => (k in ADDONS ? `, with ${ADDONS[k as AddonKey].label.toLowerCase()}` : `, with ${k}`)).join("");
  const body = (m[8] ? p.slice(0, -3) : p).slice(0, m[7] ? -m[7].length : undefined);
  if (presetOf(DEFAULT_SETTINGS, d) === `${body}-${RULES_VERSION}`) return `${DIFFICULTIES[d].label}, the default battery${on}${old}`;
  return `${DIFFICULTIES[d].label}, ${m[2]} kWh, ${m[3]} kW, ${m[4]} percent round trip${m[5] !== undefined ? `, reserve ${m[5]} percent, wear $${m[6]} per kWh` : ""}${on}${old}`;
}

/** The VPP hour: the clock hour (four intervals from the day's start) with the highest mean price; the earliest on a tie. */
export function vppHour(prices: number[]): { first: number; last: number; price: number } {
  let best = { first: 0, last: Math.min(3, prices.length - 1), price: -Infinity };
  for (let i = 0; i + 3 < prices.length; i += 4) {
    const m = (prices[i] + prices[i + 1] + prices[i + 2] + prices[i + 3]) / 4;
    if (m > best.price) best = { first: i, last: i + 3, price: m };
  }
  return best;
}

/** One interval: the new state of charge, the market cash (USD), the degradation cost (USD) and the energy delivered
 * (kWh at the meter). Discharge stops at the reserve; the degradation cost is per kWh taken out of the battery. */
export function step(soc: number, a: Action, price: number, r: Rules = V1): { soc: number; cash: number; wear: number; delivered: number } {
  const grid = (r.kw * r.minutes) / 60;
  if (a === 1) {
    const stored = Math.min(grid * r.eta, r.kwh - soc);
    if (stored <= 0) return { soc, cash: 0, wear: 0, delivered: 0 };
    const bought = stored / r.eta;
    return { soc: stored === r.kwh - soc ? r.kwh : soc + stored, cash: (-bought * price) / 1000, wear: 0, delivered: 0 };
  }
  if (a === -1) {
    const room = soc - r.reserveKwh;
    if (room <= 0) return { soc, cash: 0, wear: 0, delivered: 0 };
    const taken = Math.min(grid / r.eta, room);
    const delivered = taken * r.eta;
    return { soc: taken === room ? r.reserveKwh : soc - taken, cash: (delivered * price) / 1000, wear: taken * r.deg, delivered };
  }
  return { soc, cash: 0, wear: 0, delivered: 0 };
}

export type Result = {
  cash: number; wear: number; bonus: number; score: number; soc: number[]; vppKwh: number;
  money: number; end: number | null; why: "" | "bankrupt" | "lights_out"; outageStartKwh: number | null; outageNeedKwh: number; prices: number[];
  /** session 66: the lights-out penalty (USD) and the unserved energy it prices (kWh); the roof's sales (USD) and its
   * output up to the end (kWh); each interval's change of the score (they sum to it; zero after an early end). */
  penalty: number; unservedKwh: number; solar: number; solarKwh: number; gain: number[];
  curtailedKwh: number;  // session 70: the roof's output switched off at negative prices, kWh
};

/** A whole day's play: the score is cash, less the degradation cost, plus the VPP bonus, in USD. Session 63: the money
 * (START_MONEY plus the score so far) ends the game in the interval it falls below $0 ("bankrupt"); on Hard the
 * emergency's prices are the ones traded at, and in an outage interval the action is ignored and the house draws on the
 * battery; when the battery cannot carry it, the lights go out and the game ends there ("lights_out"). `end` is that
 * interval, or null for a whole day; the actions after it do not count. Session 66: lights out also costs the penalty
 * (the money may end below $0); with the rooftop add-on (`solar`, the level's shape), the roof's power is sold at each
 * interval's price (while the battery charges it goes into the battery first, which comes to the same money: the grid
 * supplies only the rest), and in the outage it carries the house before the battery does. Session 70: lights out is
 * charged for the whole outage's unserved energy, whenever in the outage it happens; the roof is curtailed at a
 * negative price unless the battery is charging (roofSale). `upto` stops the day after
 * that many intervals (the page, mid-game: the state so far, with nothing of the hours not yet played; before it the
 * page scored the rest of the day as idle, so on Hard the charge shown already had the coming outage taken out of it, and
 * an outage that idling would lose ended the round before it began). */
export function simulate(prices: number[], actions: Action[], r: Rules = V1, solar?: number[] | null, upto?: number): Result {
  const em = emergencyOf(prices, r);
  const P = em.prices;
  const vpp = vppHour(P);
  const bonusPrice = Math.max(0, vpp.price);
  const sun = solarKwh(prices, r, solar);
  const need = (r.houseKw * r.minutes) / 60;
  let soc = r.start, cash = 0, wear = 0, vppKwh = 0, sold = 0, made = 0, penalty = 0, unservedKwh = 0, curtailedKwh = 0;
  let end: number | null = null, why: Result["why"] = "", outageStartKwh: number | null = null;
  const path = [soc];
  const gain: number[] = new Array(P.length).fill(0);
  const stop = Math.min(P.length, upto ?? P.length);
  for (let i = 0; i < stop; i++) {
    made += sun[i];
    if (em.outage && i >= em.outage.first && i <= em.outage.last) {
      if (i === em.outage.first) outageStartKwh = soc;
      const next = outageStep(soc, sun[i], r);
      if (next === null) {
        const u = unserved(em.outage.first, em.outage.last, sun, r);  // session 70: the whole outage
        penalty = u.usd; unservedKwh = u.kwh; gain[i] = -u.usd;
        soc = 0; path.push(soc); end = i; why = "lights_out";
        break;
      }
      soc = next;
      path.push(soc);
      continue;
    }
    const x = step(soc, actions[i] ?? 0, P[i], r);
    const inVpp = i >= vpp.first && i <= vpp.last;
    const sale = roofSale(sun[i], P[i], x.soc - soc, r), roof = sale.usd;
    curtailedKwh += sale.curtailed;
    soc = x.soc;
    cash += x.cash;
    wear += x.wear;
    sold += roof;
    if (inVpp) vppKwh += x.delivered;
    gain[i] = x.cash - x.wear + roof + (inVpp ? (x.delivered * bonusPrice) / 1000 : 0);
    path.push(soc);
    if (r.money0 + cash - wear + sold + (vppKwh * bonusPrice) / 1000 < 0) { end = i; why = "bankrupt"; break; }
  }
  const bonus = (vppKwh * bonusPrice) / 1000;
  const score = cash - wear + bonus + sold - penalty;
  let outageNeedKwh = 0;
  if (em.outage) for (let j = em.outage.first; j <= em.outage.last; j++) outageNeedKwh += Math.max(0, need - sun[j]) / r.eta;
  return { cash, wear, bonus, score, soc: path, vppKwh, money: r.money0 + score, end, why, outageStartKwh, outageNeedKwh, prices: P,
    penalty, unservedKwh, solar: sold, solarKwh: made, gain, curtailedKwh };
}

/** The perfect-foresight optimum over the same three actions: dynamic programming over every state of charge the
 * actions can reach (each state is its exact value; two paths meeting at one keep the better). The VPP bonus, the
 * reserve and the degradation cost are part of it, as in simulate(); session 66: so are the lights-out penalty and the
 * roof (it never moves the battery's charge outside the outage, and in the outage every state moves by the same forced
 * step, so the states stay as few as without it; session 70: at a negative price its money depends on whether the
 * battery charges, which roofSale reads from the step itself). */
export function optimum(prices: number[], r: Rules = V1, solar?: number[] | null): { score: number; actions: Action[] } {
  const em = emergencyOf(prices, r);
  const P = em.prices;
  const vpp = vppHour(P);
  const bonusPrice = Math.max(0, vpp.price);
  const sun = solarKwh(prices, r, solar);
  type Node = { soc: number; value: number; prev: Node | null; a: Action };
  let layer = new Map<number, Node>();
  layer.set(Math.round(r.start * 1e9), { soc: r.start, value: 0, prev: null, a: 0 });
  // session 63: a play that ends early (bankrupt, lights out) is a terminal node; the best of them competes at the end
  let ended: { node: Node; at: number } | null = null;
  const endAt = (node: Node, at: number) => { if (!ended || node.value > ended.node.value) ended = { node, at }; };
  for (let i = 0; i < P.length; i++) {
    const next = new Map<number, Node>();
    const inVpp = i >= vpp.first && i <= vpp.last;
    const out = em.outage !== null && i >= em.outage.first && i <= em.outage.last;
    const dark = out ? unserved(em.outage!.first, em.outage!.last, sun, r).usd : 0;  // session 70: lights out costs the whole outage
    for (const n of layer.values()) {
      if (out) {  // the grid is down: no action; the roof and the battery carry the house, or the lights go out
        const soc = outageStep(n.soc, sun[i], r);
        if (soc === null) { endAt({ soc: 0, value: n.value - dark, prev: n, a: 0 }, i); continue; }
        const k = Math.round(soc * 1e9), had = next.get(k);
        if (!had || n.value > had.value) next.set(k, { soc, value: n.value, prev: n, a: 0 });
        continue;
      }
      for (const a of [1, 0, -1] as Action[]) {
        const x = step(n.soc, a, P[i], r);
        const value = n.value + x.cash - x.wear + roofSale(sun[i], P[i], x.soc - n.soc, r).usd + (inVpp ? (x.delivered * bonusPrice) / 1000 : 0);
        if (r.money0 + value < 0) { endAt({ soc: x.soc, value, prev: n, a }, i); continue; }  // bankrupt: the game ends
        const k = Math.round(x.soc * 1e9);
        const had = next.get(k);
        if (!had || value > had.value) next.set(k, { soc: x.soc, value, prev: n, a });
      }
    }
    layer = next;
  }
  let best: Node | null = null;
  for (const n of layer.values()) if (!best || n.value > best.value) best = n;
  let stop = P.length;
  const e = ended as { node: Node; at: number } | null;
  if (e && (!best || e.node.value > best.value)) { best = e.node; stop = e.at + 1; }
  const actions: Action[] = [];
  for (let n = best; n && n.prev; n = n.prev) actions.unshift(n.a);
  while (actions.length < P.length) actions.push(0);  // after an early end nothing counts
  return { score: best ? best.value : 0, actions: actions.slice(0, Math.max(stop, actions.length)).slice(0, P.length) };
}

/** Session 66: every interval's price as the page may show it. A spiked price (Hard's emergency: the price played is
 * not the real one) carries SPIKE_LABEL on the number itself, with the real price beside it; any other is the real
 * price, plain. Every place that shows a played price takes its text from here. */
export type ShownPrice = { value: number; real: number; spike: boolean; text: string };
const usdMwh = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const spikeText = (value: number, real: number) => `${usdMwh(value)} USD/MWh (${SPIKE_LABEL}; the real price was ${usdMwh(real)} USD/MWh)`;
export function shownPrices(prices: number[], r: Rules = V1): ShownPrice[] {
  const P = emergencyOf(prices, r).prices;
  return prices.map((real, i) => {
    const spike = P[i] !== real;
    return { value: P[i], real, spike, text: spike ? spikeText(P[i], real) : `${usdMwh(real)} USD/MWh` };
  });
}

/** Session 66: the end screen's third line. The clock hour (four intervals from the day's start, as vppHour) where a
 * play earned the least against the perfect battery, from the two simulate() results' own per-interval earnings; what
 * the perfect battery did in it (what it did in most of the hour's intervals: 1 charged, -1 sold, 0 held; in the outage
 * it can only hold) and the mean price of those intervals, as shownPrices words it. Null when no hour was lost. */
export type HourLost = { first: number; last: number; lost: number; mine: number; perfect: number; did: Action; outage: boolean; price: ShownPrice };
export function worstHour(prices: number[], mine: Result, perfect: Result, r: Rules = V1): HourLost | null {
  const em = emergencyOf(prices, r);
  const shown = shownPrices(prices, r);
  let best: HourLost | null = null;
  for (let first = 0; first < prices.length; first += 4) {
    const last = Math.min(prices.length - 1, first + 3);
    let a = 0, b = 0;
    for (let i = first; i <= last; i++) { a += mine.gain[i]; b += perfect.gain[i]; }
    if (b - a <= 1e-9 || (best && b - a <= best.lost)) continue;
    const did: Action[] = [];
    for (let i = first; i <= last; i++) {
      const out = em.outage !== null && i >= em.outage.first && i <= em.outage.last;
      const d = i + 1 < perfect.soc.length ? perfect.soc[i + 1] - perfect.soc[i] : 0;
      did.push(out ? 0 : d > 1e-12 ? 1 : d < -1e-12 ? -1 : 0);
    }
    const count = (x: Action) => did.filter((v) => v === x).length;
    const most = ([-1, 1, 0] as Action[]).reduce((x, y) => (count(y) > count(x) ? y : x));
    const at = did.map((v, k) => (v === most ? first + k : -1)).filter((i) => i >= 0);
    const mean = (f: (s: ShownPrice) => number) => at.reduce((x, i) => x + f(shown[i]), 0) / at.length;
    const value = mean((s) => s.value), real = mean((s) => s.real), spike = at.some((i) => shown[i].spike);
    const outage = em.outage !== null && first <= em.outage.last && last >= em.outage.first;
    best = { first, last, lost: b - a, mine: a, perfect: b, did: most, outage, price: { value, real, spike, text: spike ? spikeText(value, real) : `${usdMwh(real)} USD/MWh` } };
  }
  return best;
}

/** Session 50: the replay's reasons. Each run of one action in a plan, with a line read from the day's prices, such
 * as "charged: the cheapest two hours of the morning", "sold: dearer than 95 percent of the day's prices" or "held:
 * reserve". `hours` is each interval's local clock hour; `clock(i)` labels an interval's start. */
export type Segment = { from: number; to: number; a: Action; text: string };
const PERIODS: [number, number, string][] = [[0, 6, "night"], [6, 12, "morning"], [12, 18, "afternoon"], [18, 24, "evening"]];
const WORDS = ["", "hour", "two hours", "three hours", "four hours", "five hours", "six hours"];
const spanOf = (k: number) => (k % 4 === 0 ? WORDS[k / 4] ?? `${k / 4} hours` : `${k * 15} minutes`);
export function explain(prices0: number[], hours: number[], actions: Action[], r: Rules = V1, clock: (i: number) => string = (i) => String(i), solar?: number[] | null): Segment[] {
  const em = emergencyOf(prices0, r);
  const prices = em.prices;
  const vpp = vppHour(prices);
  const soc = simulate(prices0, actions, r, solar).soc;
  const out: Segment[] = [];
  let i = 0;
  while (i < actions.length) {
    let j = i;
    while (j + 1 < actions.length && actions[j + 1] === actions[i]) j++;
    const a = actions[i], k = j - i + 1, run = prices.slice(i, j + 1);
    const mean = run.reduce((x, y) => x + y, 0) / k;
    const per = PERIODS.find(([lo, hi]) => hours[i] >= lo && hours[i] < hi) ?? PERIODS[0];
    const inPer = prices.filter((_, t) => hours[t] >= per[0] && hours[t] < per[1]);
    let text: string;
    if (a !== 0) {
      const sorted = [...inPer].sort((x, y) => (a === 1 ? x - y : y - x));
      const edge = sorted[Math.min(k, sorted.length) - 1];
      const within = k <= inPer.length && run.every((p) => (a === 1 ? p <= edge : p >= edge));
      const pct = Math.round((prices.filter((p) => (a === 1 ? p > mean : p < mean)).length / prices.length) * 100);
      const verb = a === 1 ? "charged" : "sold";
      text = within
        ? `${verb}: the ${a === 1 ? "cheapest" : "dearest"} ${spanOf(k)} of the ${per[2]}`
        : `${verb}: ${a === 1 ? "cheaper" : "dearer"} than ${pct} percent of the day's prices`;
      if (a === -1 && i <= vpp.last && j >= vpp.first) text += "; the fleet call";
    } else if (em.outage && i >= em.outage.first && i <= em.outage.last) {
      text = "held: grid outage, the house runs on the battery";
    } else {
      const s0 = soc[i];
      const next = actions.findIndex((x, t) => t > j && x !== 0);
      if (r.reserveKwh > 0 && s0 <= r.reserveKwh + 1e-9) text = next >= 0 ? `held: reserve, until it can charge at ${clock(next)}` : "held: reserve";
      else if (s0 >= r.kwh - 1e-9) text = next >= 0 ? `held: full, waiting to sell at ${clock(next)}` : "held: full";
      else if (s0 <= 1e-9) text = next >= 0 ? `held: empty, waiting to charge at ${clock(next)}` : "held: empty";
      else text = next >= 0 ? `held: no price before ${clock(next)} pays for the round trip` : "held: no price left pays for the round trip";
    }
    out.push({ from: i, to: j, a, text });
    i = j + 1;
  }
  return out;
}

/** Whether a posted play is well formed for a day of n intervals. */
export function validActions(x: unknown, n: number): x is Action[] {
  return Array.isArray(x) && x.length === n && x.every((a) => a === -1 || a === 0 || a === 1);
}

// Nicknames: letters and digits, 3 to 16; a small block list, matched inside the name, case-insensitive.
const BLOCK = ["fuck", "shit", "cunt", "nigg", "fag", "rape", "nazi", "hitler", "slut", "whore", "dick", "cock", "pussy", "bitch", "kike", "spic", "retard"];
export function validNickname(s: string): boolean {
  if (!/^[A-Za-z0-9]{3,16}$/.test(s)) return false;
  const low = s.toLowerCase();
  return !BLOCK.some((b) => low.includes(b));
}

// --- session 46: battery game v1.1 -------------------------------------------------------------------------------

/** The share of the perfect-foresight score a score reaches, percent, or null when perfect foresight earns nothing. */
export function perfectShare(score: number, optimal: number): number | null {
  return optimal > 0 ? (score / optimal) * 100 : null;
}

/** A leaderboard score shown as 100 percent of perfect (or more, rounded as shown): flagged on the leaderboard, since
 * the debrief prints the perfect plan and replaying it scores 100 percent. The score stands; the flag says so. */
export function isPerfect(score: number, optimal: number): boolean {
  const s = perfectShare(score, optimal);
  return s !== null && Math.round(s) >= 100;
}

/** The /events pages whose window (warehouse/derived/event_window.py, local dates, inclusive) takes in ERCOT, so a game
 * day inside one links to it. CAISO's 2020 heat is not an ERCOT event. */
export const EVENT_PAGES = [
  { href: "/events/covid-2020", label: "the COVID-19 lockdowns, spring 2020", start: "2020-03-01", end: "2020-05-31" },
  { href: "/events/uri-2021", label: "Winter Storm Uri, February 2021", start: "2021-02-07", end: "2021-02-24" },
  { href: "/events/elliott-2022", label: "Winter Storm Elliott, December 2022", start: "2022-12-19", end: "2022-12-29" },
  { href: "/events/ercot-heat-2023", label: "ERCOT's summer 2023 heat", start: "2023-08-01", end: "2023-09-10" },
];
export function eventPageFor(date: string): { href: string; label: string } | null {
  const e = EVENT_PAGES.find((x) => date >= x.start && date <= x.end);
  return e ? { href: e.href, label: e.label } : null;
}

/** The fictional fleet at full power and full charge: 10,000 homes x 5 kW = 50 MW; x 13.5 kWh = 135 MWh. */
export const FLEET_MW = (FLEET * BATTERY.kw) / 1000;
export const FLEET_MWH = (FLEET * BATTERY.kwh) / 1000;

/** Session 46 (problem set D): one full cycle of the game's battery, empty to full at `buy` and full to empty at `sell`
 * (USD/MWh): it buys 13.5 kWh over the square root of 0.9 and delivers 13.5 kWh times it; the cash is USD. */
export function fullCycle(buy: number, sell: number): { bought: number; delivered: number; usd: number } {
  const bought = BATTERY.kwh / ETA, delivered = BATTERY.kwh * ETA;
  return { bought, delivered, usd: (delivered * sell - bought * buy) / 1000 };
}
