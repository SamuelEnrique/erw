"use client";
// Session 194: the decisions block of /cost-of-power, as session 179 built it for the battery and session 186 for the
// generator. An assumptions panel (eight assumptions, each with its default, the default's source and a Reset), two
// scenarios A and B set side by side on the same eight rows, a row that sets B against A, and a sensitivity chart for
// the scenario in view. Everything is computed in the browser (lib/datacenter/finance.ts) from figures the server
// already computed for this page: the last twelve months of the load run flat and run flexible, and the bad month of
// each. A change sends no request: the address is rewritten in place (history.replaceState) so that a comparison can be
// shared as a link. No sentence here judges: each states a number. The formulas are in
// docs/methods/datacenter_pays_algorithm.md, section 4.14.
//
// Session 195: the panel, the two columns, the rows in words and the chart are the component the three decision pages
// share (components/decisions/ScenarioBlock.tsx); this file hands it the load's fields, rows and figures. The two
// scenarios are held above the page's sections (LoadDecisions), and scenario A sets the headline: the three headline
// numbers are A's rows, and the power per GPU-hour of the summary sentence and of "What will it cost" follows A's power
// per GPU and overhead ratio (LoadHeadline.tsx). "Your load" no longer holds those two fields; their names in an older
// link are read as the scenarios' (lib/datacenter/finance.ts, parseScenarios). No usage count is sent from here: the
// owner's ruling of 11 October 2026.
//
// Session 213 (the owner's chain prompt of 12 October 2026, the battery page's layout): the page asks three questions.
// The block answers the second, "Which option is better?", with ten assumptions now: the contract's share of the energy
// and its price per MWh are scenario assumptions, 0 by default, so the default is fully merchant and every figure at a
// share of 0 is what it was. The standalone contract panel and "With your contract" are gone. The sensitivity chart
// answers the third question, "What matters most", in a section of its own (LoadSensitivity), so the block is handed
// no chart.
//
// Session 236 (the owner's chain prompt of 12 October 2026: "its A and B compare two sites or two contracts"): scenario
// B may stand at a site of its own (another zone or hub, or another grid: `bsite` in the address, read by the server,
// which hands B's two ways of running at that site in `facts.b`), and its contract terms are two of its assumptions,
// as A's are. B's column, the row "B against A" and B's chart then read B's site; the table's first heading and the
// row "What differs" name both sites. With no site of its own B is at A's, and nothing here differs from session 213.
import { useCallback, useMemo, type ReactNode } from "react";
import { ScenarioBlock, ScenarioState, Sensitivity, useScenarios, type Cell, type Chart, type Field, type Row, type Side, type Values, type View } from "@/components/decisions/ScenarioBlock";
import { monthName, two, usdShort, whole } from "@/lib/datacenter";
import {
  FLAT, FLEX, KEYS, SPECS, against, bound, defaultsOf, differenceWords, differing, held, isOldParam, isScenarioParam, parseScenarios, resultOf, scenarioQuery, sensitivity, wayOf,
  type Assumptions, type Key, type Scenarios as Both, type Ways,
} from "@/lib/datacenter/finance";

const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const four = (v: number) => `USD ${v.toFixed(4)}`;

/** The bad month of one way of running: the month, its price per MWh, and the window it was ranked in. */
export type Bad = { m: string; per: number; of: number; first: string; to: string };
/** What the page hands the block: figures it already computed, for the grid, region, market and size chosen. A way of
 * running that is not held is null in `ways` and its reason is beside it. */
export type Facts = {
  /** `size` is the load's size in words ("100 MW"), `place` where it is and how it buys ("LZ_NORTH in ERCOT, real time") */
  mw: number; size: string; place: string; span: string | null;
  /** how "Your load" runs (0 flat, 1 flexible), the page's cited power per GPU and overhead ratio, and the source of each */
  load: { run: number; gpu: number; pue: number }; gpuSource: string; pueSource: string;
  ways: Ways;
  /** each way in words, and why a way is not held */
  words: [string, string]; why: [string, string];
  /** each way's bad month of its last 36, held even where its last twelve months are not */
  bads: [Bad | null, Bad | null];
  /** session 236: scenario B's own site, when the address names one: where it is, its own last twelve months, its two
   * ways of running there and why a way is not held. Null or absent: B is at the site above. */
  b?: { grid: string; region: string; place: string; span: string | null; ways: Ways; bads: [Bad | null, Bad | null]; why: [string, string] } | null;
};
/** The site a scenario stands at: B's own when it has one, else the page's. */
const siteOf = (f: Facts, p: View) => (p === "b" && f.b ? f.b : f);

/** The parameters of the address the scenarios replace: their own, and the two old names read as the scenarios'. */
const drop = (name: string) => isScenarioParam(name) || isOldParam(name);

/** The two scenarios of the page, held above its sections: the block edits them, the headline reads scenario A. */
export function LoadDecisions({ load, open, initial, children }: { load: { run: number; gpu: number; pue: number }; open: [boolean, boolean]; initial: Record<string, string | undefined>; children: ReactNode }) {
  const d = useMemo(() => defaultsOf(load), [load]);
  const query = useCallback((s: { a: Values; b: Values; view: View }) => scenarioQuery(s as unknown as Both, d), [d]);
  return <ScenarioState start={parseScenarios(initial, d, open)} query={query} drop={drop}>{children}</ScenarioState>;
}

/** What the block and the chart both read: the scenarios, the defaults, the two columns and the chart of the scenario
 * in view (session 213, as the battery's Scenarios.tsx holds them). */
function useBlock(f: Facts) {
  const { s } = useScenarios<Assumptions>();
  const d = useMemo(() => defaultsOf(f.load), [f.load]);
  const a = s[s.view];
  const col = (p: View) => { const w = wayOf(s[p], siteOf(f, p).ways); return { p, y: s[p], w, r: w ? resultOf(s[p], w) : null }; };
  const cols = { a: col("a"), b: col("b") };
  const bars = sensitivity(a, siteOf(f, s.view).ways);
  const side = (t: Side | null) => (t ? `${four(t.v)} at ${plain(t.value)}` : "no step inside its bounds");
  const chart: Chart | null = bars.length ? { bars: bars.map((b) => ({ ...b, down: b.down ? { value: b.down.value, v: b.down.v } : null, up: b.up ? { value: b.up.value, v: b.up.v } : null })),
    moves: "all-in power per GPU-hour", axis: "per GPU-hour", fmt: four, pad: 0.0001, wide: true,
    says: (b) => {
      if (b.key === "run") {
        const t = b.down ?? b.up;
        return t ? `How the load runs, the other way (${f.words[t.value]}): ${four(t.v)} per GPU-hour; ${four(b.base)} as it is (${f.words[a.run]}).` : "How the load runs: the other way is not held here, so it has no step.";
      }
      return `${b.label}, moved by ${b.step}: all-in power per GPU-hour is ${side(b.down)} and ${side(b.up)}; ${four(b.base)} at ${plain(a[b.key as Key])}.`;
    },
    sizeWords: (b) => four(b.size), stepWords: (b) => (b.key === "run" ? b.step : `by ${b.step}`),
    heads: ["Per GPU-hour, lowered", "Per GPU-hour, raised"],
    side: (b, t) => (t ? `${four(t.v)} at ${b.key === "run" ? f.words[t.value] : plain(t.value)}` : b.key === "run" ? "" : "no step inside its bounds") } : null;
  return { s, d, a, cols, chart };
}

export function LoadScenarios({ facts: f }: { facts: Facts }) {
  const { s, d, cols } = useBlock(f);
  // the ways the scenario in view can run are its own site's
  const viewWays = siteOf(f, s.view).ways, viewWhy = siteOf(f, s.view).why;
  const open = useMemo(() => held(viewWays), [viewWays]);
  const diff = differing(s.a, s.b);
  const twoSites = !!f.b;
  type Col = (typeof cols)["a"];
  const sourceOf = (k: Key) => (k === "gpu" || k === "pue" ? (k === "gpu" ? f.gpuSource : f.pueSource).replace(/\.$/, "") : SPECS[k].source);
  const rising = (g: number) => `${g > 0 ? "rising" : "falling"} ${plain(Math.abs(g))} percent a year`;
  const wayLabel = (v: number) => (v === FLEX ? `Flexible: ${f.words[FLEX]}` : "Flat: the same in every hour");
  const contractNote = (c: Col) => (c.y.cshare > 0 ? `${plain(c.y.cshare)} percent of the energy contracted at USD ${plain(c.y.cprice)} per MWh; ` : "");

  const fields: Field[] = KEYS.map((k) => {
    const sp = SPECS[k];
    const base = { key: k, label: sp.label, unit: sp.unit, min: sp.min, max: sp.max, whole: sp.whole };
    if (k !== "run") return { ...base, note: <>Default {plain(d[k])}. {sourceOf(k)}.</> };
    return { ...base, aria: sp.label, options: [FLAT, FLEX].map((v) => ({ value: v, label: `${wayLabel(v)}${open[v] ? "" : " (not held here)"}`, disabled: !open[v] })),
      note: <>Default {d.run === FLEX ? "flexible" : "flat"}. {sourceOf(k)}.{open[FLAT] && open[FLEX] ? "" : ` ${viewWhy[open[FLAT] ? FLEX : FLAT]}`}</> };
  });
  const none = (c: Col): Cell => ({ v: "not held", raw: null, why: siteOf(f, c.p).why[c.y.run === FLEX ? FLEX : FLAT] });
  const spanOf = (c: Col) => siteOf(f, c.p).span;
  const row = (key: string, label: string, note: string, cell: (c: Col) => Cell): Row => ({ key, label, note, cell: (p) => cell(cols[p]) });
  const rows: Row[] = [
    row("price", "Market energy, last twelve months", "USD per MWh consumed; a contracted share at its price, the rest at the market's",
      (c) => {
        if (!c.w) return none(c);
        // with a contract the price of the energy consumed; at a share of 0 the market's own figure, to the bit
        const per = c.y.cshare > 0 && c.r ? c.r.price - c.y.adder : c.w.per;
        return { v: `USD ${two(per)}`, raw: per, note: `${spanOf(c) ? `${spanOf(c)}; ` : ""}${f.words[c.y.run]}${c.y.cshare > 0 ? `; ${contractNote(c).replace(/; $/, "")}, the rest at the market's USD ${two(c.w.per)}` : ""}` };
      }),
    row("bill", "A year's energy", `for ${f.size}, the last twelve months`,
      (c) => (c.r && c.w ? { v: usd(c.r.bill * f.mw), raw: c.r.bill, note: `${whole(c.w.energy * f.mw)} MWh${c.y.cshare > 0 ? `, ${contractNote(c).replace(/; $/, "")}` : ""}${c.y.adder > 0 ? `, with USD ${plain(c.y.adder)} per MWh of other charges` : ""}` } : none(c))),
    row("gpu", "Power per GPU-hour", "USD, for power alone",
      (c) => (c.r ? { v: four(c.r.gpuHour), raw: c.r.gpuHour, note: `${whole(c.r.gpus * f.mw)} GPUs at ${plain(c.y.gpu)} kW and an overhead ratio of ${plain(c.y.pue)}` } : none(c))),
    row("bad", "A bad month", "market energy, USD per MWh: one month in ten of the last 36 cost this or more",
      (c) => (c.w ? (c.w.bad ? { v: `USD ${two(c.w.bad.per)}`, raw: c.w.bad.per, note: `${monthName(c.w.bad.m)}, of ${c.w.of} months; ${usd(c.w.bad.cost * f.mw)} that month` } : { v: "not held", raw: null, why: "No complete month is held to rank." }) : none(c))),
    row("off", "Hours off, and the breakeven value of a GPU-hour", "what the power not bought would have cost, per GPU-hour not run",
      (c) => {
        if (!c.r || !c.w) return none(c);
        if (!c.r.off) return { v: "none", raw: null, note: c.y.run === FLEX ? "the energy is moved within each day; no hour is off" : "a flat load runs in every hour" };
        return { v: four(c.r.off.perGpuHour), raw: c.r.off.perGpuHour, note: `off in ${whole(c.r.off.hours)} hours; USD ${two(c.r.off.perMwh)} per MWh not bought; an hour off saves more than it gives up when a GPU-hour earns less than this` };
      }),
    row("pv", "Present value of the cost, at the hurdle rate", `the upfront cost and every year counted, for ${f.size}`,
      (c) => (c.r ? { v: usd(c.r.pv * f.mw), raw: c.r.pv, note: `${plain(c.y.life)} years at ${plain(c.y.hurdle)} percent${c.y.upfront > 0 ? `; USD ${plain(c.y.upfront)} per kW upfront` : ""}${c.y.growth !== 0 ? `; prices ${rising(c.y.growth)}` : ""}${c.y.cshare > 0 ? `; ${contractNote(c).replace(/; $/, "")}` : ""}` } : none(c))),
    row("level", "Fixed price with the same present value", "a contract for the whole of the energy, USD per MWh: its breakeven against the market",
      (c) => (c.r && c.w ? { v: `USD ${two(c.r.level)}`, raw: c.r.level, note: c.y.growth === 0 ? "the last twelve months' market price, repeated every year" : `the market's USD ${two(c.w.per)}, ${rising(c.y.growth)} for ${plain(c.y.life)} years` } : none(c))),
    row("allin", "All-in power per GPU-hour, over the years counted", "the upfront cost and the energy, over the GPU-hours run, both at the hurdle rate",
      (c) => (c.r ? { v: four(c.r.allIn), raw: c.r.allIn, note: `${whole(c.r.gpuHours * f.mw)} GPU-hours a year` } : none(c))),
  ];

  // B set against A, in sentences that state numbers
  const ca = cols.a, cb = cols.b;
  const versus = (() => {
    if (!ca.w || !cb.w || !ca.r || !cb.r) return "Not held for both scenarios.";
    if (!diff.length && !twoSites) return "No difference.";
    const g = against(ca.y, ca.w, cb.y, cb.w);
    const side = (v: number, lower: string, higher: string) => (v < 0 ? lower : higher);
    const out: string[] = [];
    out.push(g.bill === 0 ? `A year's energy is ${usd(ca.r.bill * f.mw)} in both.` : `A year's energy: ${usd(ca.r.bill * f.mw)} in A, ${usd(cb.r.bill * f.mw)} in B, so B is ${usd(Math.abs(g.bill) * f.mw)} ${side(g.bill, "lower", "higher")}.`);
    if (Math.round(g.gpuHours * f.mw) !== 0) out.push(`B runs ${whole(Math.abs(g.gpuHours) * f.mw)} ${side(g.gpuHours, "fewer", "more")} GPU-hours a year (${whole(cb.r.gpuHours * f.mw)} against ${whole(ca.r.gpuHours * f.mw)}).`);
    const own = ca.y.life !== cb.y.life || ca.y.hurdle !== cb.y.hurdle ? ", each over its own years and at its own hurdle rate" : ` over ${plain(ca.y.life)} years at ${plain(ca.y.hurdle)} percent`;
    out.push(g.pv === 0 ? `The present value of the cost is the same${own}.` : `Present value of the cost: B is ${usd(Math.abs(g.pv) * f.mw)} ${side(g.pv, "lower", "higher")}${own}.`);
    out.push(g.evenUpfront >= 0
      ? `The two have the same present value when B's upfront cost is USD ${plain(Math.round(g.evenUpfront * 100) / 100)} per kW (it is ${plain(cb.y.upfront)}).`
      : "No upfront cost of B gives the two the same present value: B's is the higher with none.");
    if (g.more) {
      const m = g.more.toUpperCase(), hurdle = plain(g.more === "b" ? cb.y.hurdle : ca.y.hurdle);
      out.push(!g.sameYears ? `${m} costs USD ${plain(g.extra)} per kW more upfront; no rate of return is stated, because the two count different years.`
        : g.rate === null ? `${m} costs USD ${plain(g.extra)} per kW more upfront; no rate from -99 to 1,000 percent sets that against its yearly cost.`
        : `${m} costs USD ${plain(g.extra)} per kW more upfront, which returns ${g.rate.toFixed(1)} percent a year in lower yearly cost; ${m}'s hurdle rate is ${hurdle} percent.`);
    }
    return out.join(" ");
  })();
  const versusRate = (() => { if (!ca.w || !cb.w || (!diff.length && !twoSites)) return ""; const g = against(ca.y, ca.w, cb.y, cb.w); return g.rate === null ? "" : String(g.rate); })();
  const versusEven = (() => { if (!ca.w || !cb.w || (!diff.length && !twoSites)) return ""; return String(against(ca.y, ca.w, cb.y, cb.w).evenUpfront); })();

  return (
    <ScenarioBlock
      fields={fields} defaults={d} bound={(k, v) => bound(k as Key, v, d)} head={f.b ? `For ${f.size}: A at ${f.place}; B at ${f.b.place}` : `For ${f.size} at ${f.place}`} rows={rows}
      differing={diff} short={(k, v) => SPECS[k as Key].short(v)} differs={f.b ? `The site: B is at ${f.b.place}, A at ${f.place}${f.b.span && f.b.span !== f.span ? ` (B's last twelve months are ${f.b.span})` : ""}. ${differenceWords(s.a, s.b)}` : differenceWords(s.a, s.b)}
      against={{ words: versus, rate: versusRate, even: versusEven }}
      sentence={ca.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-pv-sentence="a">
          Scenario A, {f.size} at {f.place}: at a hurdle rate of {plain(s.a.hurdle)} percent, {plain(s.a.life)} years of power cost {usd(ca.r.pv * f.mw)} today, {four(ca.r.allIn)} per GPU-hour.
        </p>
      ) : null}
      chart={null}
    />
  );
}

/** Session 213: the sensitivity chart of the scenario in view, in the page's third section, with one line on how to
 * read it (the battery page's BatterySensitivity). Drawn only when the scenario's way is held. */
export function LoadSensitivity({ facts: f }: { facts: Facts }) {
  const { s, chart } = useBlock(f);
  if (!chart) return <p className="max-w-3xl text-sm text-muted" data-sensitivity-none="1">Twelve complete months are not held for this way of running, so there is no figure to move.</p>;
  return (
    <>
      <p className="mb-2 max-w-3xl text-sm" data-how-to-read="1">
        Each row moves one assumption of scenario {s.view.toUpperCase()} down and up by the step named, holds the other nine, and draws where the all-in power per
        GPU-hour lands from the scenario&apos;s own figure (the line); the longest bars are the assumptions that matter most.
      </p>
      <Sensitivity c={chart} view={s.view} />
    </>
  );
}
