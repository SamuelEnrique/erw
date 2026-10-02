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

export const DIFFICULTIES: Record<Difficulty, { label: string; forecastHours: number; reserve: boolean; degradation: boolean; emergency: boolean; what: string }> = {
  easy: { label: "Easy", forecastHours: 3, reserve: false, degradation: false, emergency: false, what: "the next three hours show as a band: each clock hour's lowest to highest real price" },
  normal: { label: "Normal", forecastHours: 0, reserve: false, degradation: false, emergency: false, what: "no forecast, no reserve, no degradation cost" },
  hard: { label: "Hard", forecastHours: 0, reserve: true, degradation: true, emergency: true, what: "no forecast; the backup reserve is enforced, each kWh discharged costs the degradation cost, and a grid emergency strikes: the price spikes toward the cap, then a two-hour outage runs the house on the battery" },
};

/** Session 63: the money a play starts with, USD (a game rule). Below $0 the game ends. */
export const START_MONEY = 5;
/** Session 63: Hard's grid emergency (game rules). The spike: the day's dearest clock hour (vppHour on the real prices)
 * climbs toward the cap, each of its four intervals a share of the way from its real price to the cap; the cap is
 * ERCOT's system-wide offer cap since 2023 (USD 5,000/MWh), used for every grid. The outage: the eight intervals (two
 * hours) after the spike hour, the grid down: no buying or selling, and the house draws 1.5 kW from the battery (an
 * assumption: a home's evening load with air conditioning; the reserve is for exactly this). */
export const EMERGENCY = { cap: 5000, ramp: [0.25, 0.5, 0.75, 0.9], outageIntervals: 8, houseKw: 1.5 };
export const RULES_VERSION = "v3";

/** The rules a play is scored by: the battery's settings, with the reserve and the degradation cost only where the
 * difficulty enforces them. */
export type Rules = { kwh: number; kw: number; eta: number; reserveKwh: number; deg: number; start: number; minutes: number; money0: number; emergency: boolean; houseKw: number };
export function rulesOf(s: Settings = DEFAULT_SETTINGS, d: Difficulty = "normal"): Rules {
  const D = DIFFICULTIES[d];
  return { kwh: s.kwh, kw: s.kw, eta: Math.sqrt(s.rte), reserveKwh: D.reserve ? s.kwh * s.reserve : 0, deg: D.degradation ? s.deg : 0, start: s.kwh * 0.5, minutes: 15,
    money0: START_MONEY, emergency: D.emergency, houseKw: EMERGENCY.houseKw };
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
 * cost only on Hard), so only plays under the same rules are ranked together. */
export function presetOf(s: Settings, d: Difficulty): string {
  const base = `${d}:${s.kwh}-${s.kw}-${Math.round(s.rte * 100)}`;
  return `${d === "hard" ? `${base}-r${Math.round(s.reserve * 100)}-d${s.deg}` : base}-${RULES_VERSION}`;  // session 63: the rules' version
}
export const DEFAULT_PRESET = presetOf(DEFAULT_SETTINGS, "normal");
export function presetLabel(p: string): string {
  const m = /^(easy|normal|hard):([\d.]+)-([\d.]+)-(\d+)(?:-r(\d+)-d([\d.]+))?(-v3)?$/.exec(p);
  if (!m) return p;
  const d = DIFFICULTIES[m[1] as Difficulty].label;
  const old = m[7] ? "" : " (v2 rules)";  // session 63: a board from before the v3 rules says so
  if (presetOf(DEFAULT_SETTINGS, m[1] as Difficulty) === p || presetOf(DEFAULT_SETTINGS, m[1] as Difficulty) === `${p}-v3`) return `${d}, the default battery${old}`;
  return `${d}, ${m[2]} kWh, ${m[3]} kW, ${m[4]} percent round trip${m[5] !== undefined ? `, reserve ${m[5]} percent, wear $${m[6]} per kWh` : ""}${old}`;
}

/** Session 55: a preset back to its settings and difficulty, or null when it is not a preset presetOf writes: an
 * unknown difficulty, a setting outside its range or off its step, the reserve and degradation on a level other than
 * Hard (or missing on Hard), or any other spelling of the same rules. The read route of the leaderboard refuses the rest. */
export function parsePreset(raw: unknown): { settings: Settings; difficulty: Difficulty; v3: boolean } | null {
  if (typeof raw !== "string" || raw.length > 64) return null;
  // session 63: a v3 preset ends "-v3"; a board from before (v2) is still readable, never written
  const v3 = raw.endsWith("-v3");
  const p = v3 ? raw.slice(0, -3) : raw;
  const m = /^(easy|normal|hard):(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)-(\d+)(?:-r(\d+)-d(\d+(?:\.\d+)?))?$/.exec(p);
  if (!m) return null;
  const difficulty = m[1] as Difficulty;
  if ((difficulty === "hard") !== (m[5] !== undefined)) return null;
  const settings: Settings = {
    kwh: Number(m[2]), kw: Number(m[3]), rte: Number(m[4]) / 100,
    reserve: m[5] !== undefined ? Number(m[5]) / 100 : DEFAULT_SETTINGS.reserve, deg: m[6] !== undefined ? Number(m[6]) : DEFAULT_SETTINGS.deg,
  };
  if (!validSettings(settings) || presetOf(settings, difficulty) !== `${p}-v3`) return null;
  return { settings, difficulty, v3 };
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
};

/** A whole day's play: the score is cash, less the degradation cost, plus the VPP bonus, in USD. Session 63: the money
 * (START_MONEY plus the score so far) ends the game in the interval it falls below $0 ("bankrupt"); on Hard the
 * emergency's prices are the ones traded at, and in an outage interval the action is ignored and the house draws on the
 * battery; when the battery cannot carry it, the lights go out and the game ends there ("lights_out"). `end` is that
 * interval, or null for a whole day; the actions after it do not count. */
export function simulate(prices: number[], actions: Action[], r: Rules = V1): Result {
  const em = emergencyOf(prices, r);
  const P = em.prices;
  const vpp = vppHour(P);
  const bonusPrice = Math.max(0, vpp.price);
  const draw = outageDraw(r);
  let soc = r.start, cash = 0, wear = 0, vppKwh = 0, end: number | null = null, why: Result["why"] = "", outageStartKwh: number | null = null;
  const path = [soc];
  for (let i = 0; i < P.length; i++) {
    if (em.outage && i >= em.outage.first && i <= em.outage.last) {
      if (i === em.outage.first) outageStartKwh = soc;
      if (soc + 1e-12 < draw) { soc = 0; path.push(soc); end = i; why = "lights_out"; break; }
      soc -= draw;
      path.push(soc);
      continue;
    }
    const x = step(soc, actions[i] ?? 0, P[i], r);
    soc = x.soc;
    cash += x.cash;
    wear += x.wear;
    if (i >= vpp.first && i <= vpp.last) vppKwh += x.delivered;
    path.push(soc);
    if (r.money0 + cash - wear + (vppKwh * bonusPrice) / 1000 < 0) { end = i; why = "bankrupt"; break; }
  }
  const bonus = (vppKwh * bonusPrice) / 1000;
  const score = cash - wear + bonus;
  return { cash, wear, bonus, score, soc: path, vppKwh, money: r.money0 + score, end, why, outageStartKwh,
    outageNeedKwh: em.outage ? (em.outage.last - em.outage.first + 1) * draw : 0, prices: P };
}

/** The perfect-foresight optimum over the same three actions: dynamic programming over every state of charge the
 * actions can reach (each state is its exact value; two paths meeting at one keep the better). The VPP bonus, the
 * reserve and the degradation cost are part of it, as in simulate(). */
export function optimum(prices: number[], r: Rules = V1): { score: number; actions: Action[] } {
  const em = emergencyOf(prices, r);
  const P = em.prices;
  const vpp = vppHour(P);
  const bonusPrice = Math.max(0, vpp.price);
  const draw = outageDraw(r);
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
    for (const n of layer.values()) {
      if (out) {  // the grid is down: no action; the house draws on the battery, or the lights go out
        if (n.soc + 1e-12 < draw) { endAt({ soc: 0, value: n.value, prev: n, a: 0 }, i); continue; }
        const soc = n.soc - draw, k = Math.round(soc * 1e9), had = next.get(k);
        if (!had || n.value > had.value) next.set(k, { soc, value: n.value, prev: n, a: 0 });
        continue;
      }
      for (const a of [1, 0, -1] as Action[]) {
        const x = step(n.soc, a, P[i], r);
        const value = n.value + x.cash - x.wear + (inVpp ? (x.delivered * bonusPrice) / 1000 : 0);
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

/** Session 50: the replay's reasons. Each run of one action in a plan, with a line read from the day's prices, such
 * as "charged: the cheapest two hours of the morning", "sold: dearer than 95 percent of the day's prices" or "held:
 * reserve". `hours` is each interval's local clock hour; `clock(i)` labels an interval's start. */
export type Segment = { from: number; to: number; a: Action; text: string };
const PERIODS: [number, number, string][] = [[0, 6, "night"], [6, 12, "morning"], [12, 18, "afternoon"], [18, 24, "evening"]];
const WORDS = ["", "hour", "two hours", "three hours", "four hours", "five hours", "six hours"];
const spanOf = (k: number) => (k % 4 === 0 ? WORDS[k / 4] ?? `${k / 4} hours` : `${k * 15} minutes`);
export function explain(prices0: number[], hours: number[], actions: Action[], r: Rules = V1, clock: (i: number) => string = (i) => String(i)): Segment[] {
  const em = emergencyOf(prices0, r);
  const prices = em.prices;
  const vpp = vppHour(prices);
  const soc = simulate(prices0, actions, r).soc;
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
