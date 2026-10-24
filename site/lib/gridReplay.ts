// Energy Research Warehouse (ERW) site, session 1170 (chain 078): a replayed day's figures on the Grid tool, from the
// replay's committed daily file (site/public/network/daily_<year>.json, warehouse/derived/network_daily.py), drawn on the
// server with their check keys. The Grid pack's blind spot 11: in the live week only the seven ISO grids have a demand;
// the replay's files hold EIA's daily demand (eia930_daily_demand, session 109) for 54 balancing authorities, so a
// day's demand of BPAT, or of any of them, is shown where the file holds it and "not held" where it does not.
// Neither daily table is in the live set (warehouse/supabase/live_set.yaml, session 109): the committed file is the
// figure's source, and check-values recomputes every key from that file in the repository:
// - fmt|n0|file|public/network/daily_<year>.json|demand.<BA>.@<day>: the day's demand, the day's MWh over its hours (the
//   day's average MW), whole MW; scripts/check-file.mjs follows the path, "@<day>" being the element at that day's place
//   in the file's own `days`;
// - fmt|n0|netday|export|<BA>|<day> or fmt|n0|netday|import|<BA>|<day>: the day's net exchange over the ties with a flow
//   that day, signed from the balancing authority's side (positive: power left it), whole MW; netday|ties|<BA>|<day>, how
//   many ties held a flow. A new kind: a sum over the file's links is no path, so check-values runs netdayValue below on
//   the same file (the network's own rule, lib/networkGravity.ts netImportAt, with the sign turned to an export).
// Pure functions, type imports only, so a node test loads this file (scripts/test-grid-replay.mjs).
import type { Fig } from "./gridKeys";

/** A year of the replay, as far as this file reads it. */
export type ReplayYear = { year?: number; days: string[]; built?: string; links: { a: string; b: string; mw: (number | null)[] }[]; demand?: Record<string, (number | null)[]> };

/** A figure written whole, as the page writes it (scripts/check-format.mjs n0). */
export type DayFig = Fig & { text: string };

export type ReplayDay = {
  ba: string; day: string; file: string;
  /** the day is one of the file's days */
  inFile: boolean;
  /** the day's demand, or null: the file holds no demand for this balancing authority on that day */
  demand: DayFig | null;
  /** why the demand is not held, in one line, when it is not */
  demandWhy: string | null;
  /** the day's net over the ties with a flow that day; null with no tie */
  net: (DayFig & { kind: "export" | "import" }) | null;
  ties: DayFig;
  /** how many balancing authorities the file holds a demand for */
  withDemand: number;
};

const n0 = (v: number) => Math.round(v).toLocaleString("en-US");
/** -0 is written 0 */
const z = (v: number) => v || 0;
/** a sum of values with one decimal, held to one decimal (the file's own precision) so the page and the check agree */
const tenth = (v: number) => z(Math.round(v * 10) / 10);

/** The committed file a day is read from, as the keys name it: public/network/daily_<year>.json. */
export function replayFileOf(day: string): string {
  return `public/network/daily_${day.slice(0, 4)}.json`;
}

/** The day's net export of a balancing authority over its ties with a flow that day, and how many: the file's links are
 * counted once, positive when `a` exported to `b` (the file's rule). */
export function netOfDay(y: ReplayYear, ba: string, day: string): { sum: number; ties: number } | null {
  const i = y.days.indexOf(day);
  if (i < 0) return null;
  let sum = 0, ties = 0;
  for (const l of y.links) {
    if (l.a !== ba && l.b !== ba) continue;
    const v = l.mw[i];
    if (v === null || v === undefined) continue;
    sum += l.a === ba ? v : -v;
    ties += 1;
  }
  return { sum: tenth(sum), ties };
}

/** A balancing authority's figures on a replayed day, each with its key and a one-line source. */
export function replayDay(y: ReplayYear, ba: string, day: string): ReplayDay {
  const file = replayFileOf(day);
  const i = y.days.indexOf(day);
  const built = y.built ? `, built ${y.built.slice(0, 16).replace("T", " ")} UTC` : "";
  const from = `the replay's committed file site/${file}${built}`;
  const withDemand = Object.keys(y.demand ?? {}).length;
  const series = y.demand?.[ba];
  const d = i >= 0 ? series?.[i] : undefined;
  const demand: DayFig | null = d !== null && d !== undefined
    ? { check: `fmt|n0|file|${file}|demand.${ba}.@${day}`, raw: d, text: n0(d),
      tip: `eia930_daily_demand as ${from}: ${ba}, EIA's Eastern day ${day}, the day's MWh over its hours (the day's average MW), whole MW` }
    : null;
  const demandWhy = demand ? null
    : i < 0 ? `${day} is not a day of ${from}`
    : !series ? `${from} holds a daily demand for ${withDemand} balancing authorities, and none for ${ba}`
    : `${from} holds no demand for ${ba} on ${day}: EIA's daily demand is not reported, or falls outside half to twice the median of the six days around it (session 109)`;
  const n = netOfDay(y, ba, day);
  const src = (what: string) => `eia930_daily_interchange as ${from}: ${what}, EIA's Eastern day ${day}, the day's average MW`;
  const net = n && n.ties
    ? n.sum >= 0
      ? { kind: "export" as const, check: `fmt|n0|netday|export|${ba}|${day}`, raw: n.sum, text: n0(n.sum), tip: src(`${ba}'s ${n.ties} ties with a flow summed, net export, signed from ${ba}'s side`) }
      : { kind: "import" as const, check: `fmt|n0|netday|import|${ba}|${day}`, raw: z(-n.sum), text: n0(z(-n.sum)), tip: src(`${ba}'s ${n.ties} ties with a flow summed, net import`) }
    : null;
  const t = n ? n.ties : 0;
  return { ba, day, file, inFile: i >= 0, demand, demandWhy, net,
    ties: { check: `netday|ties|${ba}|${day}`, raw: t, text: n0(t), tip: src(`ties of ${ba} with a flow`) }, withDemand };
}

/** check-values' recomputation of a netday| key on the day's file: export, import (a positive number, or undefined when
 * the day's net is the other way) or ties. Undefined for another key, a day not in the file or no tie. */
export function netdayValue(check: string, y: ReplayYear): number | undefined {
  const [kind, what, ba, day] = check.split("|");
  if (kind !== "netday" || !ba || !day) return undefined;
  const n = netOfDay(y, ba, day);
  if (!n) return undefined;
  if (what === "ties") return n.ties;
  if (!n.ties) return undefined;
  if (what === "export") return n.sum >= 0 ? n.sum : undefined;
  if (what === "import") return n.sum < 0 ? z(-n.sum) : undefined;
  return undefined;
}
