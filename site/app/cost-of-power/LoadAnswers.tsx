"use client";
// Session 228: the three answers "What a datacenter pays" gives beside "What will it pay?", for the load the reader
// describes: will the power be there (the hours of the last twelve months at or above the scarcity level, and what a
// flexible load avoided in them), how clean (the load's carbon from the grid's intensity of consumed electricity), how
// soon (the operator's own figures of large load, ERCOT's). Each follows the page's pattern: one sentence with the
// number, at most three numbers, one table, and the answer for scenario B where B runs the other way. The figures are
// computed on the server (lib/datacenter/reads.ts on lib/datacenter/answers.ts, from the live set and the page's own
// files) and handed over; this file chooses which way's figure each scenario reads (scenario A's way sets the
// headline) and writes each number with its check key (dc|<address>|<stat>), which scripts/check-values.mjs recomputes.
//
// Session 236 (the owner's ruling of 12 October 2026 on the scarcity level): USD 1,000 per MWh stays the level for every
// grid and is stated beside the count; each grid's own signal is a second count where the warehouse holds a table of
// it. CAISO's notices are held (caiso_grid_emergencies): counted in the page's twelve months and in the last twelve
// months the table itself covers. ERCOT's own signal, its reserve adders, is not held yet: one plain line says it is
// coming. Any other grid's: "not held". And where scenario B stands at a site of its own, each answer adds that
// site's figure, computed the same way for that site's address (its own check key).
import { useScenarios } from "@/components/decisions/ScenarioBlock";
import { Num } from "@/components/Num";
import { HeadlineNumber, HeadlineRow, ToolTable } from "@/components/tool/ToolPage";
import { monthName, two, usdShort, whole } from "@/lib/datacenter";
import { statOf, type Answers, type Way } from "@/lib/datacenter/answers";
import { shown } from "@/lib/format";
import { FLEX, type Assumptions } from "@/lib/datacenter/finance";
import { statedStat, stageWords, type Stated, type Statement } from "@/lib/datacenter/statements";
import type { ReactNode } from "react";

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

export type AnswerFacts = { pre: string; place: string; size: string; span: string | null; gridName: string; own: Way; words: Record<Way, string>; stdName: string };
/** Session 236: the same answers at scenario B's own site, when it has one (null: B is at the site of "Your load"). */
export type SiteB = { a: Answers | null; f: AnswerFacts; reason: string | null } | null;
/** The level, as the page states it wherever the count stands. */
export const LEVEL_WORDS = "USD 1,000 per MWh is the level for every grid: the cap on an incremental energy offer in the FERC markets (Order 831). ERCOT is outside FERC and its own cap is higher (USD 5,000); the same level is used there, so that the count means the same thing on every grid.";
/** A grid's own scarcity signal that the warehouse holds no table of: it is "not held". (ERCOT's, its reserve adder,
 * is held since session 244 and is counted below; CAISO's notices are counted too.) */
const OWN_SIGNAL: Record<string, { name: string }> = {
  NYISO: { name: "its reserve shortage pricing" }, "ISO-NE": { name: "its reserve shortage pricing" }, SPP: { name: "its reserve shortage pricing" },
};
/** A day as the page writes it, from YYYY-MM-DD. */
const dayWords = (d: string) => `${Number(d.slice(8, 10))} ${monthName(d.slice(0, 7))}`;
/** A notice's type in words, as the table names its types (caiso_grid_emergencies, event_type). */
const TYPE_WORDS: Record<string, string> = { rmo: "restricted maintenance operations", flex_alert: "flex alerts", transmission_emergency: "transmission emergencies" };
const typeWords = (byType: Record<string, number>) => Object.entries(byType).sort((x, y) => y[1] - x[1]).map(([t, n]) => `${TYPE_WORDS[t] ?? t.replace(/_/g, " ").replace(/\beea\b/, "EEA")} ${n}`).join(", ");

/** Will the power be there: the hours at or above the scarcity level. */
export function PowerThere({ a, f, b }: { a: Answers; f: AnswerFacts; b?: SiteB }) {
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
        Over the last twelve months{f.span ? `, ${f.span},` : ""} the price at {f.place} was at or above USD {s.level.toLocaleString("en-US")} per MWh in <N pre={f.pre} stat="scarce:hours" a={a} /> {s.hours === 1 ? "hour" : "hours"}
        {s.hours ? <>: {when}. A flat {f.size} load paid USD <N pre={f.pre} stat="scarce:flat_usd" a={a} usd /> in {s.hours === 1 ? "it" : "them"}.{wayLine(w.a, "Scenario A")}{w.differ ? wayLine(w.b, "Scenario B") : null}</> : <>. Nothing was short at this level.</>}
        {b ? <span data-answer-b-site="power"> Scenario B&apos;s site, {b.f.place}{b.f.span ? `, ${b.f.span}` : ""}: {b.a ? <><N pre={b.f.pre} stat="scarce:hours" a={b.a} /> {b.a.scarcity.hours === 1 ? "hour" : "hours"} at or above the same level, in which a flat {f.size} load paid USD <N pre={b.f.pre} stat="scarce:flat_usd" a={b.a} usd />.</> : <span className="text-muted">not held ({b.reason ?? "twelve complete months are not held there"}).</span>}</span> : null}
      </p>
      <HeadlineRow>
        <HeadlineNumber label={`Hours at or above USD ${s.level.toLocaleString("en-US")}, last twelve months`} value={<N pre={f.pre} stat="scarce:hours" a={a} />} unit={s.hours === 1 ? "hour" : "hours"}
          note={<>of the hours held at {f.place}. The level is the same for every grid.</>} />
        <HeadlineNumber label="What a flat load paid in them" value={<>USD <N pre={f.pre} stat="scarce:flat_usd" a={a} usd /></>}
          note={<>for {f.size}; {s.hours ? <>USD {two(s.flatUsd / s.hours)} per MWh on average in those hours</> : "none"}.</>} />
        <HeadlineNumber label={`Scenario ${w.differ ? "A" : "A and B"}: what its way avoided`}
          value={a.held[w.a] && w.a !== "flat" ? <>USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.a}`} a={a} usd /></> : w.a === "flat" ? <>USD 0</> : <span className="text-muted">not held</span>}
          note={a.held[w.a] && w.a !== "flat" ? <>{f.words[w.a]}: off in <N pre={f.pre} stat={`scarce:off:${w.a}`} a={a} /> of the {s.hours} hours, under the rule decided before each hour.{w.differ ? <span data-answer-b="power"> Scenario B ({f.words[w.b]}): {a.held[w.b] && w.b !== "flat" ? <>off in <N pre={f.pre} stat={`scarce:off:${w.b}`} a={a} />, avoided USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.b}`} a={a} usd /></> : "runs flat, avoided nothing"}.</span> : null}</>
            : w.a === "flat" ? <>a flat load runs in every hour.{w.differ ? <span data-answer-b="power"> Scenario B ({f.words[w.b]}): {a.held[w.b] ? <>off in <N pre={f.pre} stat={`scarce:off:${w.b}`} a={a} /> of them, avoided USD <N pre={f.pre} stat={`scarce:avoided_usd:${w.b}`} a={a} usd /></> : "not held here"}.</span> : null}</> : <>this way of running needs the region&apos;s day-ahead prices, which are not held.</>} />
      </HeadlineRow>
      {/* session 236: the level, stated where the count stands, and the grid's own signal as a second count */}
      <div className="mb-6" data-two-counts="1">
      <ToolTable caption="The two counts: the price level, and the grid's own signal" minWidth={520} words head={["The count, last twelve months", "", "What it is"]}
        rows={[
          { key: "level", cells: [`Hours at or above USD ${s.level.toLocaleString("en-US")} per MWh`, <N key="h" pre={f.pre} stat="scarce:hours" a={a} />, <span key="w" data-level-words="1">{LEVEL_WORDS}</span>] },
          ...(a.notices
            ? a.notices.held
              ? [{ key: "own", cells: [`${f.gridName}'s own signal: its notices dated in these months`, <span key="n" data-own-signal="count"><N pre={f.pre} stat="notices:count" a={a} /></span>,
                  <span key="w">Flex alerts, restricted maintenance operations and transmission or energy emergencies, as {f.gridName} posted them (caiso_grid_emergencies){a.notices.count ? `: ${typeWords(a.notices.byType)}` : ""}. The table runs to {a.notices.last}{a.notices.count === 0 && a.notices.last !== null && a.notices.last.slice(0, 7) < s.months[0] ? ", before these twelve months began, so this is not a count of none" : ""}.</span>] },
                ...(a.notices.own ? [{ key: "own12", cells: [`${f.gridName}'s notices in the last twelve months its table covers, ${monthName(a.notices.own.first)} to ${monthName(a.notices.own.last)}`,
                  <span key="n" data-own-signal="table"><N pre={f.pre} stat="notices:own:count" a={a} /></span>, <span key="w">{a.notices.own.count ? `${typeWords(a.notices.own.byType)}.` : "None."} Not the months of the price count above.</span>] }] : [])]
              : [{ key: "own", cells: [`${f.gridName}'s own signal: its notices`, <span key="n" data-own-signal="none">not held</span>, <span key="w">No notice of {f.gridName}&apos;s is in the table.</span>] }]
            : a.adders
              // session 236, after session 244: ERCOT's own signal, the adder of its operating reserve demand curve
              ? [{ key: "own", cells: [`${f.gridName}'s own signal: hours its reserve adder was at least USD ${a.adders.level} per MWh, in the part of these months it was published`,
                  <span key="n" data-own-signal="count"><N pre={f.pre} stat="adders:hours" a={a} /></span>,
                  <span key="w" data-adder-words="1">The adder of {f.gridName}&apos;s operating reserve demand curve, the price it added to real-time energy when its reserves ran short (ercot_rtm_price_adders, the hour&apos;s mean of the on-line adder). {f.gridName} published it until {dayWords(a.adders.last)} and no longer: this count covers <N pre={f.pre} stat="adders:held" a={a} /> hours, {dayWords(a.adders.first)} to {dayWords(a.adders.last)}, and no hour of these months after, so it is not a count of the twelve months. The reliability deployment adder, which {f.gridName}&apos;s file carries since, is another thing and is not counted.</span>] },
                { key: "own12", cells: [`The same adder over the last year it was published, ${dayWords(a.adders.own.from)} to ${dayWords(a.adders.own.to)}`,
                  <span key="n" data-own-signal="table"><N pre={f.pre} stat="adders:own:hours" a={a} /></span>, <span key="w">Hours at or above the same USD {a.adders.level} per MWh. Not the months of the price count above.</span>] }]
              : f.gridName === "ERCOT"
              ? [{ key: "own", cells: [`${f.gridName}'s own signal: its reserve adder`, <span key="n" data-own-signal="none">not held</span>,
                  <span key="w">{f.gridName} ended the adder of its operating reserve demand curve on 4 December 2025: the table holds no hour of it in these months.</span>] }]
              : [{ key: "own", cells: [`${f.gridName}'s own signal`, <span key="n" data-own-signal="none">not held</span>,
                  <span key="w">{OWN_SIGNAL[f.gridName] ? `${OWN_SIGNAL[f.gridName].name[0].toUpperCase()}${OWN_SIGNAL[f.gridName].name.slice(1)}: no table of those hours is held.` : "No table of it is held."}</span>] }]),
        ]} />
      </div>
      {s.hours ? (
        <ToolTable caption="The hours at or above the scarcity level, by month" minWidth={520} head={["Month", "Hours", `A flat load paid, USD, ${f.size}`, "USD per MWh in them"]}
          rows={s.byMonth.map((m) => ({ key: m.m, cells: [monthName(m.m), <N key="h" pre={f.pre} stat={`scarce:month:${m.m}:hours`} a={a} />, <N key="u" pre={f.pre} stat={`scarce:month:${m.m}:usd`} a={a} usd />, two(m.usd / m.hours)] }))} />
      ) : null}
      <p className="mt-2 max-w-3xl text-xs text-muted" data-answer-note="power">
        The hours are the page&apos;s own price files at {f.place}, counted in {f.stdName}; a flexible load&apos;s hours off are the rule&apos;s (decided from day-ahead prices before each hour), so what it avoided is what it would have avoided, not a forecast. {a.notices === null && !a.adders ? `${f.gridName}'s own emergency notices are not held as a table, so the price is the measure.` : ""}
      </p>
    </>
  );
}

/** How clean: the load's carbon from the grid's intensity of consumed electricity. */
export function HowClean({ a, f, b }: { a: Answers; f: AnswerFacts; b?: SiteB }) {
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
        {b ? <span data-answer-b-site="clean"> Scenario B&apos;s site, {b.f.place}: {b.a && b.a.carbon.l12[w.b].kgPerMwh !== null ? <><N pre={b.f.pre} stat={`co2:l12:kg:${w.b}`} a={b.a} /> kg of CO2 per MWh at {b.f.gridName}&apos;s monthly average, <N pre={b.f.pre} stat={`co2:l12:tonnes:${w.b}`} a={b.a} /> tonnes a year for {f.size}.</> : <span className="text-muted">not held.</span>}</span> : null}
      </p>
      <HeadlineRow>
        <HeadlineNumber label="This load's carbon, last twelve months" value={<><N pre={f.pre} stat={`co2:l12:kg:${w.a}`} a={a} /><span className="ml-1 font-sans text-sm text-muted">kg CO2 per MWh</span></>}
          note={<>{f.gridName}&apos;s intensity of consumed electricity, month by month, weighted by this load&apos;s energy in each month{l.months < l.of ? ` (${l.of - l.months} of the twelve months ${l.of - l.months === 1 ? "has" : "have"} no intensity in the table and ${l.of - l.months === 1 ? "is" : "are"} left out)` : ""}; scenario A runs {wayLabel(w.a)}.</>} />
        <HeadlineNumber label="Tonnes of CO2 a year" value={<N pre={f.pre} stat={`co2:l12:tonnes:${w.a}`} a={a} />}
          note={<>for {f.size}: the rate of the {l.months} of {l.of} months with an intensity, on the year&apos;s {whole(l.energy * a.mw)} MWh.{w.differ ? <span data-answer-b="clean"> Scenario B ({wayLabel(w.b)}): {c.l12[w.b].tonnesPerMw === null ? "not held" : <><N pre={f.pre} stat={`co2:l12:tonnes:${w.b}`} a={a} /> tonnes</>}.</span> : null}</>} />
        <HeadlineNumber label="Its own hours against the grid's average" value={win.ways[w.a] !== null && win.grid !== null ? <><N pre={f.pre} stat={`co2:window:${w.a}`} a={a} /><span className="ml-1 font-sans text-sm text-muted">against {whole(win.grid)}</span></> : <span className="text-muted">not held</span>}
          note={<>kg per MWh over the {whole(win.hours)} hours the hourly table holds ({win.from?.slice(0, 10)} to {win.to?.slice(0, 10)}): flat {win.ways.flat === null ? "not held" : whole(win.ways.flat)}, flexible {win.ways.flex === null ? "not held" : whole(win.ways.flex)}, shifting {win.ways.shift === null ? "not held" : whole(win.ways.shift)}.</>} />
      </HeadlineRow>
      <ToolTable caption={`${f.gridName}'s carbon intensity of consumed electricity by year`} minWidth={520} head={["Year", "kg CO2 per MWh, the mean of its months", "Months held"]}
        rows={c.years.map((r) => ({ key: String(r.y), muted: r.months < 12, cells: [String(r.y), <N key="k" pre={f.pre} stat={`co2:year:${r.y}`} a={a} />, `${r.months} of 12`] }))} />
      <p className="mt-2 max-w-3xl text-xs text-muted" data-answer-note="clean">
        The intensity is the ERW&apos;s from EIA-930&apos;s hourly CO2 estimates (carbon_intensity_monthly and carbon_intensity_hourly, the balancing authority&apos;s consumed electricity: generation plus imports less exports); the hours counted hour by hour are the ones the live set holds of the hourly table, named above. A year&apos;s figure is the mean of its months held; {year(new Date().getUTCFullYear())?.months ?? 0} months of {new Date().getUTCFullYear()} are held.
      </p>
    </>
  );
}

/** How soon: the operator's own figures of large load, where a public table holds them. */
/** Session 265b: the large-load statements on a public document for the load's grid (large_load_public; the owner's
 * ruling of 14 October 2026: facts with a link, no quoted text). Counts, the newest wait as the table writes it and the
 * newest megawatt figure, each with its document's link; never a sum across rows. Keys dcll|<grid>|<stat>, recomputed by
 * scripts/check-values.mjs from its own read of the table (lib/datacenter/statements.ts). */
type StatedProp = { s: Stated; grid: string } | { failed: string } | null;
function StatedLine({ stated, gridName }: { stated: StatedProp; gridName: string }) {
  if (!stated) return null;
  if ("failed" in stated) return <p className="mb-4 max-w-3xl text-sm" role="status" data-answer-stated="failed">The public documents on large loads could not be read, so none is stated: {stated.failed}</p>;
  const { s, grid } = stated;
  const K = ({ stat, children }: { stat: string; children?: ReactNode }) => {
    const v = statedStat(s, stat);
    // a wait written in words ("several years") holds no number, so it stands as written, with no key
    if (v === undefined) return children ? <>{children}</> : <span className="text-muted">not held</span>;
    return <Num check={`dcll|${grid}|${stat}`} raw={v}>{children ?? whole(v)}</Num>;
  };
  const dayOf = (d: string) => `${Number(d.slice(8, 10))} ${monthName(d.slice(0, 7))}`;
  const doc = (r: Statement) => <><a href={r.source_url} rel="noopener noreferrer">{r.document_title || "the document"}</a>{r.page ? `, page ${r.page}` : ""}</>;
  if (!s.statements) return <p className="mb-4 max-w-3xl text-sm" data-answer-stated="0">No public document the warehouse holds states a figure on large loads in {gridName}.</p>;
  return (
    <p className="mb-4 max-w-3xl text-sm" data-answer-stated="1">
      Public documents state <K stat="statements" /> figures on large loads in {gridName} (<K stat="mws" /> of megawatts, <K stat="waits" /> of a wait), from <K stat="entities" /> entities in <K stat="documents" /> documents, the newest of {dayOf(s.newest ?? "")}.
      {s.wait ? <> The newest wait: <K stat="wait:newest">{s.wait.duration_as_stated}</K>{s.wait.wait_basis ? `, ${s.wait.wait_basis}` : ""}, stated by {s.wait.parties} on {dayOf(s.wait.event_date)} in {doc(s.wait)}.</> : null}
      {s.mw ? <> The newest megawatt figure: <K stat="mw:newest">{whole(Number(s.mw.mw))}</K> MW{stageWords(s.mw.stage_class) ? `, at the stage ${stageWords(s.mw.stage_class)}` : ""}, stated by {s.mw.parties} on {dayOf(s.mw.event_date)} in {doc(s.mw)}.</> : null}
      {" "}The figures are not added: the entities count differently, and a document often states a total and its parts. Every row, with its link, is in large_load_public.
    </p>
  );
}

export function HowSoon({ a, f, rules, b, stated = null }: { a: Answers; f: AnswerFacts; rules: { count: number; newest: string | null; words: string }; b?: SiteB; stated?: StatedProp }) {
  const l = a.largeLoad;
  // session 236: scenario B's own grid, when it is another grid: its operator's figure, or the line that none is held
  const dayOf = (d: string) => `${Number(d.slice(8, 10))} ${monthName(d.slice(0, 7))}`;
  const lb = b && b.f.gridName !== f.gridName ? b.a?.largeLoad?.latest ?? null : null;
  const siteB = b && b.f.gridName !== f.gridName ? (
    <p className="mb-4 max-w-3xl text-sm" data-answer-b-site="soon">
      Scenario B&apos;s site is in {b.f.gridName}: {lb && b.a ? <>by its own report of {dayOf(lb.day)}, <N pre={b.f.pre} stat={`ll:report:${lb.day}:approved`} a={b.a} /> MW of large load was approved to energize.</>
        : <>{b.f.gridName} publishes no figure of large load waiting or energized that the warehouse holds as a public table, so none is stated, and no wait is estimated.</>}
    </p>
  ) : null;
  if (!l || !l.latest) {
    return (
      <>
        <p className="mb-4 max-w-3xl font-serif text-xl leading-snug" data-answer="soon" data-answer-none="1">
          {f.gridName} publishes no regular report of large load waiting or energized that the warehouse holds, so no operator&apos;s figure is stated here, and no wait is estimated.
        </p>
        <StatedLine stated={stated} gridName={f.gridName} />
        <p className="max-w-3xl text-sm" data-answer-rules="1">{rules.words}</p>
        {siteB}
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
      <StatedLine stated={stated} gridName={f.gridName} />
      {siteB}
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
