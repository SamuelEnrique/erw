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
// per GPU and overhead ratio (LoadHeadline, GpuHourOfA). "Your load" no longer holds those two fields; their names in
// an older link are read as the scenarios' (lib/datacenter/finance.ts, parseScenarios). No usage count is sent from
// here: the owner's ruling of 11 October 2026.
import { useCallback, useMemo, type ReactNode } from "react";
import { ScenarioBlock, ScenarioState, useScenarios, type Cell, type Field, type Row, type Side, type Values, type View } from "@/components/decisions/ScenarioBlock";
import { HeadlineNumber, HeadlineRow } from "@/components/tool/ToolPage";
import { gpuHour as gpuHourOf, monthName, two, usdShort, whole } from "@/lib/datacenter";
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
};

/** The parameters of the address the scenarios replace: their own, and the two old names read as the scenarios'. */
const drop = (name: string) => isScenarioParam(name) || isOldParam(name);

/** The two scenarios of the page, held above its sections: the block edits them, the headline reads scenario A. */
export function LoadDecisions({ load, open, initial, children }: { load: { run: number; gpu: number; pue: number }; open: [boolean, boolean]; initial: Record<string, string | undefined>; children: ReactNode }) {
  const d = useMemo(() => defaultsOf(load), [load]);
  const query = useCallback((s: { a: Values; b: Values; view: View }) => scenarioQuery(s as unknown as Both, d), [d]);
  return <ScenarioState start={parseScenarios(initial, d, open)} query={query} drop={drop}>{children}</ScenarioState>;
}

/** Power per GPU-hour at a price per MWh, at scenario A's power per GPU and overhead ratio: the figure of the summary
 * sentence and of "What will it cost", which price the load as "Your load" describes it. */
export function GpuHourOfA({ per }: { per: number }) {
  const { s } = useScenarios<Assumptions>();
  return <>{gpuHourOf(per, s.a.gpu, s.a.pue).toFixed(4)}</>;
}

/** The three headline numbers: scenario A's rows "Market energy", "A bad month" and "Power per GPU-hour". `foreseen`
 * is the server's own note beside the first, for the way "Your load" describes; `missing` says why a figure is not held. */
export function LoadHeadline({ facts: f, foreseen, missing }: { facts: Facts; foreseen: ReactNode; missing: ReactNode }) {
  const { s } = useScenarios<Assumptions>();
  const a = s.a, run = a.run === FLEX ? FLEX : FLAT;
  const w = wayOf(a, f.ways), r = w ? resultOf(a, w) : null, bad = f.bads[run];
  const own = run === (f.load.run === FLEX ? FLEX : FLAT);
  return (
    <HeadlineRow>
      <HeadlineNumber label="Last twelve months, market energy"
        value={w ? <>USD {two(w.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={w ? <>USD {usdShort(w.cost * f.mw)} for {whole(w.energy * f.mw)} MWh, {f.span}.{own ? foreseen : <span data-scenario-a-run="1"> Scenario A runs {run === FLEX ? `flexible (${f.words[FLEX]})` : "flat"}. The sections below are the load as &quot;Your load&quot; describes it.</span>}</> : null} />
      <HeadlineNumber label="A bad month: the worst tenth of the last 36"
        value={bad ? <>USD {two(bad.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={bad ? <>{monthName(bad.m)}. One month in ten of the {bad.of} held from {monthName(bad.first)} to {monthName(bad.to)} cost this or more.</> : null} />
      <HeadlineNumber label="Power per GPU-hour"
        value={r ? <>USD {r.gpuHour.toFixed(4)}</> : missing}
        note={<>At {a.gpu} kW per GPU and an overhead ratio of {a.pue}: {f.size} powers {whole((f.mw * 1000) / (a.gpu * a.pue))} GPUs.{a.adder > 0 ? <span data-scenario-a-adder="1"> With USD {plain(a.adder)} per MWh of other charges, as scenario A has them.</span> : null}</>} />
    </HeadlineRow>
  );
}

export function LoadScenarios({ facts: f }: { facts: Facts }) {
  const { s } = useScenarios<Assumptions>();
  const d = useMemo(() => defaultsOf(f.load), [f.load]);
  const open = useMemo(() => held(f.ways), [f.ways]);
  const a = s[s.view];
  const diff = differing(s.a, s.b);
  const col = (p: View) => { const w = wayOf(s[p], f.ways); return { p, y: s[p], w, r: w ? resultOf(s[p], w) : null }; };
  const cols = { a: col("a"), b: col("b") };
  type Col = ReturnType<typeof col>;
  const bars = sensitivity(a, f.ways);
  const sourceOf = (k: Key) => (k === "gpu" || k === "pue" ? (k === "gpu" ? f.gpuSource : f.pueSource).replace(/\.$/, "") : SPECS[k].source);
  const rising = (g: number) => `${g > 0 ? "rising" : "falling"} ${plain(Math.abs(g))} percent a year`;
  const wayLabel = (v: number) => (v === FLEX ? `Flexible: ${f.words[FLEX]}` : "Flat: the same in every hour");

  const fields: Field[] = KEYS.map((k) => {
    const sp = SPECS[k];
    const base = { key: k, label: sp.label, unit: sp.unit, min: sp.min, max: sp.max, whole: sp.whole };
    if (k !== "run") return { ...base, note: <>Default {plain(d[k])}. {sourceOf(k)}.</> };
    return { ...base, aria: sp.label, options: [FLAT, FLEX].map((v) => ({ value: v, label: `${wayLabel(v)}${open[v] ? "" : " (not held here)"}`, disabled: !open[v] })),
      note: <>Default {d.run === FLEX ? "flexible" : "flat"}. {sourceOf(k)}.{open[FLAT] && open[FLEX] ? "" : ` ${f.why[open[FLAT] ? FLEX : FLAT]}`}</> };
  });
  const none = (c: Col): Cell => ({ v: "not held", raw: null, why: f.why[c.y.run === FLEX ? FLEX : FLAT] });
  const row = (key: string, label: string, note: string, cell: (c: Col) => Cell): Row => ({ key, label, note, cell: (p) => cell(cols[p]) });
  const rows: Row[] = [
    row("price", "Market energy, last twelve months", "USD per MWh consumed",
      (c) => (c.w ? { v: `USD ${two(c.w.per)}`, raw: c.w.per, note: `${f.span ? `${f.span}; ` : ""}${f.words[c.y.run]}` } : none(c))),
    row("bill", "A year's energy", `for ${f.size}, the last twelve months`,
      (c) => (c.r && c.w ? { v: usd(c.r.bill * f.mw), raw: c.r.bill, note: `${whole(c.w.energy * f.mw)} MWh${c.y.adder > 0 ? `, with USD ${plain(c.y.adder)} per MWh of other charges` : ""}` } : none(c))),
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
      (c) => (c.r ? { v: usd(c.r.pv * f.mw), raw: c.r.pv, note: `${plain(c.y.life)} years at ${plain(c.y.hurdle)} percent${c.y.upfront > 0 ? `; USD ${plain(c.y.upfront)} per kW upfront` : ""}${c.y.growth !== 0 ? `; prices ${rising(c.y.growth)}` : ""}` } : none(c))),
    row("level", "Fixed price with the same present value", "a contract for the whole of the energy, USD per MWh: its breakeven against the market",
      (c) => (c.r && c.w ? { v: `USD ${two(c.r.level)}`, raw: c.r.level, note: c.y.growth === 0 ? "the last twelve months' price, repeated every year" : `the market's USD ${two(c.w.per)}, ${rising(c.y.growth)} for ${plain(c.y.life)} years` } : none(c))),
    row("allin", "All-in power per GPU-hour, over the years counted", "the upfront cost and the energy, over the GPU-hours run, both at the hurdle rate",
      (c) => (c.r ? { v: four(c.r.allIn), raw: c.r.allIn, note: `${whole(c.r.gpuHours * f.mw)} GPU-hours a year` } : none(c))),
  ];

  // B set against A, in sentences that state numbers
  const ca = cols.a, cb = cols.b;
  const versus = (() => {
    if (!ca.w || !cb.w || !ca.r || !cb.r) return "Not held for both scenarios.";
    if (!diff.length) return "No difference.";
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
  const versusRate = (() => { if (!ca.w || !cb.w || !diff.length) return ""; const g = against(ca.y, ca.w, cb.y, cb.w); return g.rate === null ? "" : String(g.rate); })();
  const versusEven = (() => { if (!ca.w || !cb.w || !diff.length) return ""; return String(against(ca.y, ca.w, cb.y, cb.w).evenUpfront); })();

  const side = (t: Side | null) => (t ? `${four(t.v)} at ${plain(t.value)}` : "no step inside its bounds");
  return (
    <ScenarioBlock
      fields={fields} defaults={d} bound={(k, v) => bound(k as Key, v, d)} head={`For ${f.size} at ${f.place}`} rows={rows}
      differing={diff} short={(k, v) => SPECS[k as Key].short(v)} differs={differenceWords(s.a, s.b)}
      against={{ words: versus, rate: versusRate, even: versusEven }}
      sentence={ca.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-pv-sentence="a">
          Scenario A, {f.size} at {f.place}: at a hurdle rate of {plain(s.a.hurdle)} percent, {plain(s.a.life)} years of power cost {usd(ca.r.pv * f.mw)} today, {four(ca.r.allIn)} per GPU-hour.
        </p>
      ) : null}
      chart={bars.length ? { bars: bars.map((b) => ({ ...b, down: b.down ? { value: b.down.value, v: b.down.v } : null, up: b.up ? { value: b.up.value, v: b.up.v } : null })),
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
        side: (b, t) => (t ? `${four(t.v)} at ${b.key === "run" ? f.words[t.value] : plain(t.value)}` : b.key === "run" ? "" : "no step inside its bounds") } : null}
    />
  );
}
