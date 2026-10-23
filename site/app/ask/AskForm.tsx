"use client";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { useState } from "react";
import { SeriesBlock, type Series } from "@/components/ask/AskPanel";
import { AnswerSources } from "@/components/ask/AnswerSources";

type Citation = { table: string; source_report: string; data_version: string; tier?: string };
type Result = {
  answer: string;
  citations: Citation[];
  status: string;
  model: string;
  tool_calls: number;
  retried: boolean;
  cost_usd: number | null;
  // session 1145: what the route returns since sessions 1115, 1111, 1132 and 1142, drawn here as Ask ERCOT's panel draws it
  seconds?: number;
  reads?: { table: string; entity?: string; variable?: string; start?: string; end?: string; aggregation?: string; group_by?: string; tz?: string }[];
  nearest?: { table: string; holds: string }[];
  series?: Series[];
  why?: string;
};
type Turn = { question: string; res: Result };
const MAX_HISTORY = 3;   // session 1129: the turns the general chat holds

const STATUS: Record<string, string> = {
  answered: "Answered from the warehouse",
  not_in_warehouse: "Not in the warehouse",
  refused_unverified: "The warehouse does not hold that figure",  // session 1110: the refusal's own words
  model_refusal: "No answer",
};

// session 35: grid, a grid page's scoped chat (/ask?grid=<slug>); initial, the question its Ask box carried
// session 1145: examples, questions a reader can click to place in the box (never sent until the reader presses Ask)
export function AskForm({ grid = null, initial = "", placeholder, examples = [] }: { grid?: string | null; initial?: string; placeholder?: string; examples?: string[] }) {
  const [q, setQ] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
  const [err, setErr] = useState<string | null>(null);
  // session 1145: the conversation so far (session 1129), sent with the next question; "New conversation" clears it
  const [turns, setTurns] = useState<Turn[]>([]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setRes(null);
    const history = turns.filter((t) => t.res.status === "answered" || t.res.status === "not_in_warehouse").slice(-MAX_HISTORY)
      .map((t) => ({ question: t.question, answer: t.res.answer, reads: t.res.reads ?? [], citations: t.res.citations.map((c) => ({ table: c.table })) }));
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: q, ...(grid ? { grid } : {}), ...(history.length ? { history } : {}) }) });
      const body = await r.json();
      if (!r.ok) setErr(body.error ?? `HTTP ${r.status}`);
      else { setRes(body as Result); setTurns((t) => [...t, { question: q, res: body as Result }]); }
    } catch (x) {
      setErr((x as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="q" className="sr-only">
          Question
        </label>
        <input
          id="q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          maxLength={500}
          placeholder={placeholder ?? "For example: what was the median ERCOT HB_WEST real-time price last week?"}
          className="flex-1 border border-rule bg-panel px-3 py-2 text-sm"
        />
        <button type="submit" disabled={busy || !q.trim()} className="border border-accent bg-accent px-4 py-2 text-sm text-paper disabled:opacity-50">
          {busy ? "Querying the warehouse" : turns.length ? "Ask next" : "Ask"}
        </button>
        {turns.length && !busy ? (
          <button type="button" onClick={() => { setTurns([]); setRes(null); setErr(null); setQ(""); }} className="border border-rule bg-panel px-3 py-2 text-sm" data-new-conversation="1">New conversation</button>
        ) : null}
      </form>
      {examples.length && !turns.length ? (
        <div className="mt-2 flex flex-col items-start gap-1" data-ask-examples={examples.length}>
          {examples.map((x) => <button key={x} type="button" onClick={() => setQ(x)} className="border border-rule bg-panel px-3 py-1 text-left text-sm hover:border-accent hover:text-accent">{x}</button>)}
        </div>
      ) : null}
      {turns.length > 1 ? <p className="mt-1 text-xs text-muted" data-turns={turns.length}>The next question is read as a continuation of the last {Math.min(turns.length, MAX_HISTORY)} (session 1129).</p> : null}
      {busy ? <p className="mt-3 text-xs text-muted">Each answer takes several queries; this can take up to a minute.</p> : null}
      {err ? (
        <div className="mt-4 border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
          <span className="font-semibold text-ink">no answer</span>: {err}
        </div>
      ) : null}
      {res ? (
        <section className="mt-6" aria-live="polite">
          <div className="mb-1 text-xs text-muted">{STATUS[res.status] ?? res.status}</div>
          <p className="mb-4 whitespace-pre-wrap leading-relaxed">{res.answer}</p>
          {(res.nearest ?? []).length ? (
            <div className="mb-3 border border-rule bg-panel px-3 py-2 text-sm" data-nearest={res.nearest!.length}>
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">{res.status === "not_in_warehouse" ? "The nearest thing the warehouse does hold" : "The tables read for this question"}</div>
              <ul>{res.nearest!.map((x) => <li key={x.table} className="py-0.5"><Link href={`/data#${x.table}`} className="font-mono" gate="plain">{x.table}</Link>: {x.holds}</li>)}</ul>
            </div>
          ) : null}
          {(res.series ?? []).map((s) => <SeriesBlock key={s.result_id} s={s} form="chart" />)}
          {/* session 1194: the sources and the reads in the brand's source line, as under every chat's answer (components/ask/AnswerSources.tsx) */}
          <AnswerSources citations={res.citations} reads={res.reads} />
          <p className="mt-3 text-xs text-muted">
            {typeof res.seconds === "number" ? <span data-answered-in={res.seconds.toFixed(1)}>Answered in {res.seconds.toFixed(1)} seconds; </span> : null}
            {res.tool_calls} warehouse queries by {res.model}
            {res.retried ? "; the first draft was sent back because a number could not be traced" : ""}
            {res.cost_usd !== null ? `; model cost USD ${res.cost_usd.toFixed(4)}` : ""}.
          </p>
        </section>
      ) : null}
    </div>
  );
}
