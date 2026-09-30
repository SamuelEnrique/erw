// Session 38: the home battery game's rules and its perfect-foresight optimum. Shared by the game (the browser), the
// score route (the server recomputes every score from the actions and the real prices) and the test
// (site/scripts/test-battery.mjs, run by tests/test_session38.py). No imports: Node runs this file as it is.
//
// The battery is an assumption, labelled so on the page: 13.5 kWh usable, 5 kW, 90 percent round trip (the square root
// of it on the way in and again on the way out), half full at the start. Each 15-minute interval the player charges
// (buys at the interval's price), discharges (sells) or idles. The VPP call is a game rule, not a real program's
// terms: in the day's highest-price hour, energy delivered earns a bonus of that hour's mean price (never below zero).

export const BATTERY = { kwh: 13.5, kw: 5, roundTrip: 0.9, startShare: 0.5, minutes: 15 };
export const FLEET = 10_000;
export type Action = -1 | 0 | 1; // 1 charge, 0 idle, -1 discharge

const ETA = Math.sqrt(BATTERY.roundTrip);
const GRID_KWH = (BATTERY.kw * BATTERY.minutes) / 60; // 1.25 kWh at the meter per interval

/** The VPP hour: the clock hour (four intervals from the day's start) with the highest mean price; the earliest on a tie. */
export function vppHour(prices: number[]): { first: number; last: number; price: number } {
  let best = { first: 0, last: Math.min(3, prices.length - 1), price: -Infinity };
  for (let i = 0; i + 3 < prices.length; i += 4) {
    const m = (prices[i] + prices[i + 1] + prices[i + 2] + prices[i + 3]) / 4;
    if (m > best.price) best = { first: i, last: i + 3, price: m };
  }
  return best;
}

/** One interval: the new state of charge, the cash (USD) and the energy delivered (kWh at the meter). */
export function step(soc: number, a: Action, price: number): { soc: number; cash: number; delivered: number } {
  if (a === 1) {
    const stored = Math.min(GRID_KWH * ETA, BATTERY.kwh - soc);
    const bought = stored / ETA;
    return { soc: stored === BATTERY.kwh - soc ? BATTERY.kwh : soc + stored, cash: (-bought * price) / 1000, delivered: 0 };
  }
  if (a === -1) {
    const taken = Math.min(GRID_KWH / ETA, soc);
    const delivered = taken * ETA;
    return { soc: taken === soc ? 0 : soc - taken, cash: (delivered * price) / 1000, delivered };
  }
  return { soc, cash: 0, delivered: 0 };
}

export type Result = { cash: number; bonus: number; score: number; soc: number[]; vppKwh: number };

/** A whole day's play: the score is cash plus the VPP bonus, in USD. */
export function simulate(prices: number[], actions: Action[]): Result {
  const vpp = vppHour(prices);
  const bonusPrice = Math.max(0, vpp.price);
  let soc = BATTERY.kwh * BATTERY.startShare, cash = 0, vppKwh = 0;
  const path = [soc];
  for (let i = 0; i < prices.length; i++) {
    const r = step(soc, actions[i] ?? 0, prices[i]);
    soc = r.soc;
    cash += r.cash;
    if (i >= vpp.first && i <= vpp.last) vppKwh += r.delivered;
    path.push(soc);
  }
  const bonus = (vppKwh * bonusPrice) / 1000;
  return { cash, bonus, score: cash + bonus, soc: path, vppKwh };
}

/** The perfect-foresight optimum over the same three actions: dynamic programming over every state of charge the
 * actions can reach (each state is its exact value; two paths meeting at one keep the better). The VPP bonus is part
 * of the objective, as in simulate(). */
export function optimum(prices: number[]): { score: number; actions: Action[] } {
  const vpp = vppHour(prices);
  const bonusPrice = Math.max(0, vpp.price);
  type Node = { soc: number; value: number; prev: Node | null; a: Action };
  let layer = new Map<number, Node>();
  const start = BATTERY.kwh * BATTERY.startShare;
  layer.set(Math.round(start * 1e9), { soc: start, value: 0, prev: null, a: 0 });
  for (let i = 0; i < prices.length; i++) {
    const next = new Map<number, Node>();
    const inVpp = i >= vpp.first && i <= vpp.last;
    for (const n of layer.values()) {
      for (const a of [1, 0, -1] as Action[]) {
        const r = step(n.soc, a, prices[i]);
        const value = n.value + r.cash + (inVpp ? (r.delivered * bonusPrice) / 1000 : 0);
        const k = Math.round(r.soc * 1e9);
        const had = next.get(k);
        if (!had || value > had.value) next.set(k, { soc: r.soc, value, prev: n, a });
      }
    }
    layer = next;
  }
  let best: Node | null = null;
  for (const n of layer.values()) if (!best || n.value > best.value) best = n;
  const actions: Action[] = [];
  for (let n = best; n && n.prev; n = n.prev) actions.unshift(n.a);
  return { score: best ? best.value : 0, actions };
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
