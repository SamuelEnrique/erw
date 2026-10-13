"use client";
// Session 228: the three answers "What a datacenter pays" gives beside "What will it pay?", for the load the reader
// describes: will the power be there (the hours of the last twelve months at or above the scarcity level, and what a
// flexible load avoided in them), how clean (the load's carbon from the grid's intensity of consumed electricity), how
// soon (the operator's own figures of large load, ERCOT's). Each follows the page's pattern: one sentence with the
// number, at most three numbers, one table, and the answer for scenario B where B runs the other way. The figures are
// computed on the server (lib/datacenter/reads.ts on lib/datacenter/answers.ts, from the live set and the page's own
// files) and handed over; this file chooses which way's figure each scenario reads (scenario A's way sets the
// headline) and writes each number with its check key (dc|<address>|<stat>), which scripts/check-values.mjs recomputes.
import type { ReactNode } from "react";
import { useScenarios } from "@/components/decisions/ScenarioBlock";
import { Num } from "@/components/Num";
import { HeadlineNumber, HeadlineRow, ToolTable } from "@/components/tool/ToolPage";
import { monthName, two, usdShort, whole } from "@/lib/datacenter";
import { statOf, type Answers, type Way } from "@/lib/datacenter/answers";
import { shown } from "@/lib/format";
import { FLEX, type Assumptions } from "@/lib/datacenter/finance";

const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const hh = (h: number) => `${String(h).padStart(2, "0")}:00`;
/** A number of the answers with its check key: the figure is statOf's, by the stat's name, so that the page's raw value
 * and check-values' recomputation are one definition; the text is lib/format's shown (a whole number, else two
 * decimals), or USD short inside data-format="usd", as check-values reads them. */
function N({ pre, stat, a, usd }: { pre: string; stat: string; a: Answers; usd?: boolean }) {
  const v = statOf(a, stat);
  if (v === null || v === undefined) return <span className="text-muted">not held</span>;
  const num = <Num check={`dc|${pre}|${stat}`} raw={v}>{usd ? usdShort(v) : shown(v)}</Num>;
  return usd ? <span data-format="usd">{num}</span> : num;
}
/** The way each scenario runs among the three the answers hold, and the words for it. */
function useWays(own: Way, words: Record<Way, string>) {
  const { s } = useScenarios<Assumptions>();
  const of = (run: number): Way => (run === FLEX ? (own === "shift" ? "shift" : "flex") : "flat");
  const a = of(s.a.run), b = of(s.b.run);
  return { a, b, differ: a !== b, words };
}
const Hover = ({ why, children }: { why: string; children: ReactNode }) => <span className="cursor-help border-b border-dotted border-muted" title={why}>{children}</span>;

export type AnswerFacts = { pre: string; place: string; size: string; span: string | null; gridName: string; own: Way; words: Record<Way, string>; stdName: string };

/** Will the power be there: the hours at or above the scarcity level. */
export function PowerThere({ a, f }: { a: Answers; f: AnswerFacts }) {
  const w = useWays(f.own, f.words);
  const s = a.scarcity;
  const flat = s.flatUsd * a.mw;
  const wayLine = (k: Way, label: string) => (a.held[k] && k !== "flat"
    ? <> {label} ({f.words[k]}) was off in <N pre={f.pre} stat={`scarce:off:${k}`} a={a} /> of them and avoided USD <N pre={f.pre} stat={`scarce:avoided_usd:${k}`} a={a} usd /> of that.</>
    : k === "flat" ? <> {label} runs flat, in every hour.</> : <> {label}&apos;s way ({f.words[k]}) is not held here.</>);
  const when = s.hours ? `${s.byMonth.map((m) => `${monthName(m.m)} (${m.hours})`).join(", ")}, between ${hh(s.from!)} and ${hh(s.to! + 1)} ${f.stdName}` : "";
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-answer="power">
        Over the last twelve months{f.span ? `, ${f.span},` : ""} the price at {f.place} was at or above USD {s.level.toLocaleString("en-US")} per MWh in <N pre={f.pre} stat="scarce:hours" a={a} /> hours
        {s.hours ? <>: {when}. A flat {f.size} load paid USD <N pre={f.pre} stat="scarce:flat_usd" a={a} usd /> in them.{wayLine(w.a, "Scenario A")}{w.differ ? wayLine(w.b, "Scenario B") : null}</> : <>. Nothing was short at this level.</>}
        {a.notices ? <> {a.notices.held ? <>{f.gridName}&apos;s own notices in these months: <N pre={f.pre} stat="notices:count" a={a} />{a.notices.count ? ` (${Object.entries(a.notices.byType).map(([t, n]) => `${t} ${n}`).join(", ")})` : ""}; the table of notices runs to {a.notices.last}.</> : <>No notice of {f.gridName}&apos;s is held.</>}</> : null}
      </p>
      <HeadlineRow>
        <HeadlineNumber label={`Hours at or above USD ${s.level.toLocaleString("en-US")}, last twelve months`} value={<N pre={f.pre} stat="scarce:hours" a={a} />} unit="hours"
          note={<>of the hours held at {f.place}. <Hover why="USD 1,000 per MWh is the cap on an incremental energy offer in every FERC market (Order 831); in ERCOT a price above it comes from its scarcity pricing, the operating reserve demand curve adders, on top of offers. One level for every grid, so the count means the same thing everywhere.">Why this level</Hover>.</>} />
        <HeadlineNumber label="What a flat load paid in them" value={<>USD <N pre={f.pre} stat="scarce:flat_usd" a={a} usd /></>}
          note={<>for {f.size}; {s.hours ? <>USD {two(s.flatUsd / s.hours)} per MWh on average in those hours</> : "none"}.</>} />
        <HeadlineNumber label={`Scenario ${w.differ ? "A" : "A and B"}: what its way avoided`}
          value={a.held[w.a] && w.a !== "flat" ? <>USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.a}`} a={a} usd /></> : w.a === "flat" ? <>USD 0</> : <span className="text-muted">not held</span>}
          note={a.held[w.a] && w.a !== "flat" ? <>{f.words[w.a]}: off in <N pre={f.pre} stat={`scarce:off:${w.a}`} a={a} /> of the {s.hours} hours, under the rule decided before each hour.{w.differ ? <span data-answer-b="power"> Scenario B ({f.words[w.b]}): {a.held[w.b] && w.b !== "flat" ? <>off in <N pre={f.pre} stat={`scarce:off:${w.b}`} a={a} />, avoided USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.b}`} a={a} usd /></> : "runs flat, avoided nothing"}.</span> : null}</>
            : w.a === "flat" ? <>a flat load runs in every hour.{w.differ ? <span data-answer-b="power"> Scenario B ({f.words[w.b]}): {a.held[w.b] ? <>off in <N pre={f.pre} stat={`scarce:off:${w.b}`} a={a} /> of them, avoided USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.b}`} a={a} usd /></> : "not held here"}.</span> : null}</> : <>this way of running needs the region&apos;s day-ahead prices, which are not held.</>} />
      </HeadlineRow>
      {s.hours ? (
        <ToolTable caption="The hours at or above the scarcity level, by month" minWidth={520} head={["Month", "Hours", `A flat load paid, USD, ${f.size}`, "USD per MWh in them"]}
          rows={s.byMonth.map((m) => ({ key: m.m, cells: [monthName(m.m), <N key="h" pre={f.pre} stat={`scarce:month:${m.m}:hours`} a={a} />, <N key="u" pre={f.pre} stat={`scarce:month:${m.m}:usd`} a={a} usd />, two(m.usd / m.hours)] }))} />
      ) : null}
      <p className="mt-2 max-w-3xl text-xs text-muted" data-answer-note="power">
        The hours are the page&apos;s own price files at {f.place}, counted in {f.stdName}; a flexible load&apos;s hours off are the rule&apos;s (decided from day-ahead prices before each hour), so what it avoided is what it would have avoided, not a forecast. {a.notices === null ? `${f.gridName}'s own emergency notices are not held as a table, so the price is the measure.` : ""}
      </p>
    </>
  );
}

/** How clean: the load's carbon from the grid's intensity of consumed electricity. */
export function HowClean({ a, f }: { a: Answers; f: AnswerFacts }) {
  const w = useWays(f.own, f.words);
  const c = a.carbon;
  const l = c.l12[w.a], win = c.window;
  const year = (y: number) => c.years.find((r) => r.y === y);
  // the trend's two ends: the first and the last year with at least ten of its months held
  const first = c.years.find((r) => r.months >= 10), last = [...c.years].reverse().find((r) => r.months >= 10);
  const wayLabel = (k: Way) => (k === "flat" ? "flat" : k === "flex" ? `flexible (${f.words.flex})` : `shifting (${f.words.shift})`);
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-answer="clean">
        {l.kgPerMwh !== null && l.tonnesPerMw !== null ? <>At {f.gridName}&apos;s monthly average, the power this load used over the last twelve months carried <N pre={f.pre} stat={`co2:l12:kg:${w.a}`} a={a} /> kg of CO2 per MWh, <N pre={f.pre} stat={`co2:l12:tonnes:${w.a}`} a={a} /> tonnes a year for {f.size}{w.differ && c.l12[w.b].tonnesPerMw !== null ? <span data-answer-b="clean"> (scenario B, {wayLabel(w.b)}: <N pre={f.pre} stat={`co2:l12:tonnes:${w.b}`} a={a} /> tonnes)</span> : null}.</>
          : <>The grid&apos;s monthly intensity is not held for every one of the last twelve months, so there is no twelve-month figure.</>}
        {win.hours && win.ways[w.a] !== null ? <> Over the <N pre={f.pre} stat="co2:window:hours" a={a} /> hours held hour by hour ({win.from?.slice(0, 10)} to {win.to?.slice(0, 10)}), its own hours carried <N pre={f.pre} stat={`co2:window:${w.a}`} a={a} /> kg per MWh against the grid&apos;s <N pre={f.pre} stat="co2:window:grid" a={a} /> on average.</> : null}
        {first && last && first.y !== last.y ? <> By year, {f.gridName}&apos;s consumed electricity went from <N pre={f.pre} stat={`co2:year:${first.y}`} a={a} /> kg per MWh in {first.y} to <N pre={f.pre} stat={`co2:year:${last.y}`} a={a} /> in {last.y} (the years with at least ten months held).</> : null}
      </p>
      <HeadlineRow>
        <HeadlineNumber label="This load's carbon, last twelve months" value={<><N pre={f.pre} stat={`co2:l12:kg:${w.a}`} a={a} /><span className="ml-1 font-sans text-sm text-muted">kg CO2 per MWh</span></>}
          note={<>{f.gridName}&apos;s intensity of consumed electricity, month by month, weighted by this load&apos;s energy in each month{l.months < l.of ? ` (${l.of - l.months} of the twelve months has no intensity in the table and is left out)` : ""}; scenario A runs {wayLabel(w.a)}.</>} />
        <HeadlineNumber label="Tonnes of CO2 a year" value={<N pre={f.pre} stat={`co2:l12:tonnes:${w.a}`} a={a} />}
          note={<>for {f.size}: the rate of the {l.months} of {l.of} months with an intensity, on the year&apos;s {whole(l.energy * a.mw)} MWh.{w.differ ? <span data-answer-b="clean"> Scenario B ({wayLabel(w.b)}): {c.l12[w.b].tonnesPerMw === null ? "not held" : <><N pre={f.pre} stat={`co2:l12:tonnes:${w.b}`} a={a} /> tonnes</>}.</span> : null}</>} />
        <HeadlineNumber label="Its own hours against the grid's average" value={win.ways[w.a] !== null && win.grid !== null ? <><N pre={f.pre} stat={`co2:window:${w.a}`} a={a} /><span className="ml-1 font-sans text-sm text-muted">against {whole(win.grid)}</span></> : <span className="text-muted">not held</span>}
          note={<>kg per MWh over the {whole(win.hours)} hours the hourly table holds ({win.from?.slice(0, 10)} to {win.to?.slice(0, 10)}): flat {win.ways.flat === null ? "not held" : whole(win.ways.flat)}, flexible {win.ways.flex === null ? "not held" : whole(win.ways.flex)}, shifting {win.ways.shift === null ? "not held" : whole(win.ways.shift)}.</>} />
      </HeadlineRow>
      <ToolTable caption={`${f.gridName}'s carbon intensity of consumed electricity by year`} minWidth={520} head={["Year", "kg CO2 per MWh, the mean of its months", "Months held"]}
        rows={c.years.map((r) => ({ key: String(r.y), muted: r.months < 12, cells: [String(r.y), <N key="k" pre={f.pre} stat={`co2:year:${r.y}`} a={a} />, `${r.months} of 12`] }))} />
      <p className="mt-2 max-w-3xl text-xs text-muted" data-answer-note="clean">
        The intensity is the ERW&apos;s from EIA-930&apos;s hourly CO2 estimates (carbon_intensity_monthly and carbon_intensity_hourly, the balancing authority&apos;s consumed electricity: generation plus imports less exports); the hourly table holds the last 35 days. A year&apos;s figure is the mean of its months held; {year(new Date().getUTCFullYear())?.months ?? 0} months of {new Date().getUTCFullYear()} are held.
      </p>
    </>
  );
}

/** How soon: the operator's own figures of large load, where a public table holds them. */
export function HowSoon({ a, f, rules }: { a: Answers; f: AnswerFacts; rules: { count: number; newest: string | null; words: string } }) {
  const l = a.largeLoad;
  if (!l || !l.latest) {
    return (
      <>
        <p className="mb-4 max-w-3xl font-serif text-xl leading-snug" data-answer="soon" data-answer-none="1">
          {f.gridName} publishes no figure of large load waiting or energized that the warehouse holds as a public table, so none is stated here, and no wait is estimated.
        </p>
        <p className="max-w-3xl text-sm" data-answer-rules="1">{rules.words}</p>
      </>
    );
  }
  const t = l.latest, ya = l.yearAgo;
  const day = (d: string) => `${Number(d.slice(8, 10))} ${monthName(d.slice(0, 7))}`;
  const newest = l.reports.filter((r) => r.submissions !== null).at(-1);
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-answer="soon">
        By {f.gridName}&apos;s own report of {day(t.day)}, <N pre={f.pre} stat={`ll:report:${t.day}:approved`} a={a} /> MW of large load was approved to energize and <N pre={f.pre} stat={`ll:report:${t.day}:running`} a={a} /> MW was observed running at the non-simultaneous peak
        {ya && l.approvedChange !== null ? <>; the approved figure {l.approvedChange >= 0 ? "grew" : "fell"} by <N pre={f.pre} stat="ll:approved_change" a={a} /> MW since the {Date.parse(t.day) - Date.parse(ya.day) >= 365 * 86400_000 ? "report of" : "earliest report held, of"} {day(ya.day)}</> : null}.
        {newest && newest.submissions !== null ? <> New submissions by {day(newest.day)}: <N pre={f.pre} stat={`ll:report:${newest.day}:submissions`} a={a} /> requests{newest.submissionsMw !== null ? <>, <N pre={f.pre} stat={`ll:report:${newest.day}:submissionsMw`} a={a} /> MW</> : null}.</> : null}
        {" "}No wait is estimated: {f.gridName} publishes none.
      </p>
      <HeadlineRow>
        <HeadlineNumber label={`Approved to energize, ${day(t.day)}`} value={<><N pre={f.pre} stat={`ll:report:${t.day}:approved`} a={a} /><span className="ml-1 font-sans text-sm text-muted">MW</span></>} note={<>{f.gridName}&apos;s large load interconnection status update, as reported.</>} />
        <HeadlineNumber label="Observed running, non-simultaneous peak" value={<><N pre={f.pre} stat={`ll:report:${t.day}:running`} a={a} /><span className="ml-1 font-sans text-sm text-muted">MW</span></>} note={t.simultaneous !== null ? <>simultaneous peak <N pre={f.pre} stat={`ll:report:${t.day}:simultaneous`} a={a} /> MW.</> : null} />
        <HeadlineNumber label="Rules in motion for a large load" value={<>{whole(rules.count)}</>} note={<>{rules.words}</>} />
      </HeadlineRow>
      <ToolTable caption={`${f.gridName}'s large load reports`} minWidth={560} head={["Report", "Approved to energize, MW", "Observed running, MW", "Simultaneous peak, MW", "New submissions"]}
        rows={[...l.reports].reverse().map((r) => ({ key: r.day, cells: [day(r.day), <N key="a" pre={f.pre} stat={`ll:report:${r.day}:approved`} a={a} />, <N key="r" pre={f.pre} stat={`ll:report:${r.day}:running`} a={a} />,
          <N key="s" pre={f.pre} stat={`ll:report:${r.day}:simultaneous`} a={a} />, r.submissions === null ? "" : <><N key="n" pre={f.pre} stat={`ll:report:${r.day}:submissions`} a={a} />{r.submissionsMw !== null ? <>, <N pre={f.pre} stat={`ll:report:${r.day}:submissionsMw`} a={a} /> MW</> : null}</>] }))} />
      <p className="mt-2 max-w-3xl text-xs text-muted" data-answer-note="soon">
        ERCOT&apos;s Large Load Interconnection Status Update (ercot_large_load_status), the figures as each monthly report prints them; the same figure stands in more than one report when ERCOT repeated it. The rules in motion are the public dockets the warehouse holds (large_load_rules), listed in the download.
      </p>
    </>
  );
}
