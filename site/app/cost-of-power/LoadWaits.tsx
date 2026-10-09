import type { ReactNode } from "react";
import { ToolTable } from "@/components/tool/ToolPage";
import { LOWER, NONE_MEASURED, NONE_STATED, NOT_HELD, NOT_HELD_WHY, NOT_HERE, NOT_YET, PAUSED_WHY, PAUSED_WORDS, basisWords, blockOf, dayWords, measuredTip, measuredWords, notHereWhy, notYetWhy, num, sentenceOf, sourceWords, statedTip, waitingTip, waitingWords, type Stage, type Stated } from "@/lib/howsoon";
import { howSoonFile } from "@/lib/howsoondata";

// Session 163: "How long a large load waits", in the section "How soon" of "What a datacenter pays" (/cost-of-power, in
// review), above "Rules in motion". For New York: the durations measured from dated copies of NYISO's queue, stage by
// stage, each with the count of requests behind it, the requests still waiting marked a lower bound, and NYISO's own
// stated expectation beside the stage it speaks of. For Texas: "not measured here" (ERCOT's reports name no request),
// and what Texas's own entities measured and stated, each labeled whose figure it is and what it covers. Every other
// grid reads "not measured yet"; MISO reads "paused while terms are reviewed". One summary sentence is written by code
// from the numbers (lib/howsoon.ts sentenceOf). Everything is read from one site file of aggregates,
// data/datacenter/how_soon.json (lib/howsoondata.ts; warehouse/derived/how_soon.py): the page reads no table of
// requests, and no request's name, queue position or megawatts is in the file. A stated figure is shown as the figure,
// who stated it and a link to the stater's own document; no sentence of a document is shown. The face carries no
// method: a thing not held is a short placeholder with its reason on hover, every figure has its source on hover, and
// the rest is in the Method note (docs/methods/datacenter_cost.md).

function Missing({ why, words = NOT_HELD }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
const dotted = "cursor-help border-b border-dotted border-muted";
const tag = "ml-1 inline-block cursor-help whitespace-nowrap border border-rule px-1 text-[10px] uppercase tracking-wide text-muted";
const requests = (n: number) => `${num(n)} ${n === 1 ? "request" : "requests"}`;

function StatedLink({ s, k }: { s: Stated; k: string }) {
  return (
    <span className="mr-3 inline-block" data-waits-stated={k} data-waits-basis={s.basis}>
      <a href={s.url} title={statedTip(s)} className="cursor-help">{s.figure}</a>
      {s.mark ? <span className={tag} title={s.note || undefined} data-waits-mark={s.mark}>{s.mark}</span> : null}
    </span>
  );
}

function stageRow(st: Stage, i: number, tips: { measured: string; waiting: string }, entity: string): { key: string; cells: ReactNode[] } {
  const m = st.measured, w = st.waiting;
  return {
    key: `stage-${i}`,
    cells: [
      <span key="l" data-waits-stage={st.interval} data-waits-requests={st.requests}>{st.label}</span>,
      <span key="m" data-waits-measured={st.interval} data-waits-n={m.n} data-waits-form={m.form}>
        {m.n ? <span className={dotted} title={tips.measured}>{requests(m.n)}: {measuredWords(st)}</span> : <Missing words={NONE_MEASURED} why={tips.measured} />}
      </span>,
      <span key="w" data-waits-waiting={st.interval} data-waits-n={w.n} data-waits-lower={w.n ? "1" : "0"}>
        {w.n ? <><span className={dotted} title={tips.waiting}>{requests(w.n)}: {waitingWords(st)}</span><span className={tag} title={tips.waiting} data-waits-mark="lower">{LOWER}</span></>
          : <span className="cursor-help text-muted" title={tips.waiting}>none</span>}
      </span>,
      <span key="s" className="block" data-waits-beside={st.interval}>
        {st.stated.length ? st.stated.map((s, j) => <StatedLink key={j} s={s} k={`${i}-${j}`} />)
          : <Missing words={NONE_STATED} why={`No figure of ${entity}'s own for this stage is among the statements held.`} />}
      </span>,
    ],
  };
}

function StatedTable({ rows, caption }: { rows: Stated[]; caption: string }) {
  return (
    <div data-waits-stated-table={rows.length}>
      <ToolTable caption={caption} words minWidth={720} head={["Whose figure", "Figure", "What it covers", "Document"]}
        rows={rows.map((s, i) => ({ key: `stated-${i}`, cells: [
          <span key="b" data-waits-whose={s.stated_by}>{basisWords(s)}</span>,
          <StatedLink key="f" s={s} k={`t-${i}`} />,
          <span key="c">{s.covers}</span>,
          <span key="d" className="block text-xs text-muted" title={s.document}>{s.document.length > 70 ? `${s.document.slice(0, 68).trimEnd()}...` : s.document}{dayWords(s.date) ? `, ${dayWords(s.date)}` : ""}{s.page ? `, page ${s.page}` : ""}</span>,
        ] }))} />
    </div>
  );
}

/** The short word the section's own table carries for the grid the page opened, beside the label "How long a new large
 * load waits": the block below holds the figures. */
export function WaitsWord({ grid, name }: { grid: string; name: string }) {
  const { file } = howSoonFile();
  const b = blockOf(file, grid);
  if (b.state === "measured") return <a href="#waits" data-waits-word="measured">measured, below</a>;
  if (b.state === "not measured here") return <span data-waits-word="here"><Missing words={NOT_HERE} why={notHereWhy(b.entry!)} /></span>;
  if (b.state === "paused") return <span data-waits-word="paused"><Missing words={PAUSED_WORDS} why={PAUSED_WHY} /></span>;
  if (b.state === "not held") return <span data-waits-word="held"><Missing why={NOT_HELD_WHY} /></span>;
  return <span data-waits-word="yet"><Missing words={NOT_YET} why={notYetWhy(name)} /></span>;
}

export function LoadWaits({ grid, name }: { grid: string; name: string }) {
  const { file, error } = howSoonFile();
  const b = blockOf(file, grid), g = b.entry;
  const place = g?.place ?? name;
  const built = file ? dayWords(file.built_at_utc) : null;
  return (
    <div className="mt-6" id="waits" data-waits="1" data-waits-for={grid} data-waits-state={b.state}>
      <h3 className="mb-2 font-serif text-lg text-accent">How long a large load waits, {place}</h3>
      <p className="mb-3 max-w-3xl text-sm" data-waits-sentence="1">{sentenceOf(file, grid, name)}</p>
      {b.state === "paused" ? (
        <p className="text-sm" data-waits-paused="1"><Missing words={PAUSED_WORDS} why={PAUSED_WHY} /></p>
      ) : b.state === "not held" ? (
        <p className="text-sm" data-waits-empty="held"><Missing why={error && error !== "not there" ? `The file of measured waits could not be read: ${error}.` : NOT_HELD_WHY} /></p>
      ) : b.state === "measured" && g && g.copies ? (
        <>
          <ToolTable caption={`How long a large load waits, ${place}, measured by stage`} words minWidth={760}
            head={["Stage", "Measured here", "Still waiting", `Stated by ${g.entity ?? place}`]}
            rows={g.stages.map((st, i) => stageRow(st, i, { measured: measuredTip(st, g.copies!, file!), waiting: waitingTip(st, g.copies!, file!) }, g.entity ?? place))} />
          {g.stated.length ? (
            <>
              <h4 className="mb-2 mt-5 text-sm font-semibold">Also stated by {place}&apos;s own entities</h4>
              <StatedTable rows={g.stated} caption={`Other stated figures, ${place}`} />
            </>
          ) : null}
          <p className="mt-2 text-xs text-muted" data-waits-foot="1">
            <span className={dotted} title={sourceWords(g.copies)} data-waits-copies={g.copies.n ?? ""}>{g.copies.n === null ? "dated copies" : `${num(g.copies.n)} dated copies`}, {dayWords(g.copies.first)} to {dayWords(g.copies.last)}</span>
            {built ? <>; <span className={dotted} title={`The file of measured waits was built on ${built}. It holds counts, bounds and medians by stage, and no request.`}>held {built}</span></> : null}
          </p>
        </>
      ) : (
        <>
          <p className="text-sm" data-waits-empty={b.state === "not measured here" ? "here" : "yet"}>
            {b.state === "not measured here" && g ? <Missing words={NOT_HERE} why={notHereWhy(g)} /> : <Missing words={NOT_YET} why={notYetWhy(name)} />}
          </p>
          {g && g.stated.length ? (
            <>
              <h4 className="mb-2 mt-5 text-sm font-semibold">What {place}&apos;s own entities measured and stated</h4>
              <StatedTable rows={g.stated} caption={`What ${place}'s own entities measured and stated`} />
            </>
          ) : null}
        </>
      )}
    </div>
  );
}
