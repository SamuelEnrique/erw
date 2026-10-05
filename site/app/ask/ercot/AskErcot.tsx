"use client";
// Energy Research Warehouse (ERW) site, session 92: Ask ERCOT, the reference version (/ask/ercot, in review).
// The form, the answer, its sources, the series it rests on (a chart and a table of the rows the tools returned, each
// with its table and source report) and the follow-up questions, which ask themselves when clicked. The series are
// drawn from the rows in the answer's record (lib/chat/ercot.ts seriesOf): the tool's rows, not the model's text.
// Session 121: a conversation. The answers stay on the page, oldest first, and each new question is sent with the
// turns before it, so "and the year before?" is read as what it continues. While a question is being answered the page
// shows which table is being read, as the server reports it; the answer itself arrives whole, after its check. A
// refusal shows the tables that come nearest to what was asked, and what each holds. A question whose premise the
// tables contradict says so above the answer. Under each chart: how many of the fetched rows it shows.
import { useState } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { LineChart } from "@/components/LineChart";
import { chartPoints, isDrawn, keySeconds } from "@/lib/chat/series";

export { keySeconds };

type Citation = { table: string; source_report: string; data_version: string; tier?: string };
type Row = { key: string; value: number | null; n?: number; at?: string };
type Series = {
  result_id: string; table: string; title: string; group_by: string; kind: "line" | "bar"; unit: string | null; rows: Row[];
  rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null; chosen_by: string;
  check?: { rows_fetched: number; rows: number; same: boolean; points: number; not_drawn: number };
};
type Result = {
  answer: string; citations: Citation[]; status: string; model: string; tool_calls: number; retried: boolean; cost_usd: number | null;
  series?: Series[]; followups?: string[];
  seconds?: number; calls?: { tool: string; input: Record<string, unknown> }[]; nearest?: { table: string; holds: string }[]; premise?: string;
};
type Turn = { question: string; res: Result };
const MAX_HISTORY = 3; // earlier turns sent with a question (lib/chat/spec_ercot.json max_history)
export type Context = { view: string; title?: string; settings?: Record<string, string> };

const STATUS: Record<string, string> = {
  answered: "Answered from the ERCOT tables",
  not_in_warehouse: "Not in the warehouse",
  refused_unverified: "No answer: its numbers could not all be traced to a query",
  model_refusal: "No answer",
};
const SHOWN = 24; // rows of a series shown before the fold

const shown = (v: number | null) => (v === null ? "not held" : Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { maximumFractionDigits: 4 }));

function SeriesBlock({ s }: { s: Series }) {
  const drawn = chartPoints(s.rows);
  const points = drawn.points;
  const chart = isDrawn(s.kind, drawn);
  const unit = s.unit ?? "";
  return (
    <section className="mt-5 border border-rule bg-panel p-3" data-series={s.result_id}>
      <h3 className="mb-1 text-sm font-semibold">{s.title}</h3>
      {chart ? (
        <>
          <LineChart lines={[{ label: s.title, points, color: "accent" }]} unit={unit} height={240} x={s.group_by === "year" ? "year" : s.group_by === "month" ? "month" : "minute"}
            ariaLabel={`${s.title}, ${s.rows.length} rows of ${s.table}`} />
          <p className="mt-1 text-xs text-muted" data-chart-check={`${points.length}/${s.rows.length}`}>
            {drawn.undrawn.length === 0 ? `The chart shows all ${s.rows.length} rows fetched, each at its own value; nothing is drawn between them but the line.`
              : `The chart shows ${points.length} of the ${s.rows.length} rows fetched. Not on it, and in the table below: ${drawn.undrawn.slice(0, 6).map((u) => `${u.key} (${u.why === "no value" ? "no value held" : "not a point in time"})`).join(", ")}${drawn.undrawn.length > 6 ? ", and others" : ""}.`}
          </p>
        </>
      ) : (
        <p className="text-xs text-muted">One value per {s.group_by}, shown as the table below.</p>
      )}
      <details className="mt-2 text-sm" open={s.rows.length <= SHOWN}>
        <summary className="cursor-pointer text-muted">The {s.rows.length} rows this rests on, as fetched</summary>
        <div className="overflow-x-auto">
          <table className="mt-1 w-full tabular-nums">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">{s.group_by}</th>
                <th className="py-1 pr-3 text-right font-normal">value{unit ? `, ${unit}` : ""}</th>
                <th className="py-1 pr-3 text-right font-normal">rows</th>
                <th className="py-1 font-normal">source</th>
              </tr>
            </thead>
            <tbody>
              {s.rows.map((r) => (
                <tr key={r.key} className="border-b border-rule/60">
                  <td className="py-0.5 pr-3">{r.key}</td>
                  <td className="py-0.5 pr-3 text-right">{shown(r.value)}</td>
                  <td className="py-0.5 pr-3 text-right text-muted">{r.n ?? ""}</td>
                  <td className="py-0.5 font-mono text-xs">{s.table}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <p className="mt-2 text-xs text-muted">
        Source: ERW table <span className="font-mono">{s.table}</span>{s.tier ? ` (${s.tier})` : ""}{s.license === "internal" ? ", internal" : ""}; source report {s.source_report ?? "not stated"}.
        {s.rows_matched !== null ? ` Computed from ${s.rows_matched.toLocaleString("en-US")} rows.` : ""}{s.note ? ` ${s.note}.` : ""}
        {s.chosen_by.startsWith("default") ? " The answer named no series; this is the last one it fetched." : ""}
      </p>
    </section>
  );
}

export function AskErcot({ initial = "", context = null }: { initial?: string; context?: Context | null }) {
  const [q, setQ] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [asked, setAsked] = useState("");
  const [reading, setReading] = useState<string[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setAsked(question);
    setReading([]);
    // the turns before this one: each question, its answer and the queries run for it
    const history = turns.filter((t) => t.res.status === "answered" || t.res.status === "not_in_warehouse").slice(-MAX_HISTORY)
      .map((t) => ({ question: t.question, answer: t.res.answer, calls: t.res.calls ?? [], citations: t.res.citations.map((c) => ({ table: c.table })) }));
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, profile: "ercot", stream: true, ...(context ? { context } : {}), ...(history.length ? { history } : {}) }) });
      if (!r.ok || !r.body) {
        const body = await r.json().catch(() => ({}));
        setErr((body as { error?: string }).error ?? `HTTP ${r.status}`);
        return;
      }
      // lines of JSON: what is being read, then the answer, whole and checked
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "", got = false;
      const take = (line: string) => {
        if (!line.trim()) return;
        const e = JSON.parse(line) as { type: string; table?: string | null; tool?: string; error?: string } & Partial<Result>;
        if (e.type === "reading") setReading((x) => [...x, e.table ?? (e.tool === "grid_notes" ? "the written page about ERCOT" : "the list of tables")]);
        else if (e.type === "error") { got = true; setErr(e.error ?? "no answer"); }
        else if (e.type === "result") { got = true; setTurns((t) => [...t, { question, res: e as unknown as Result }]); setQ(""); }
      };
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i: number;
        while ((i = buf.indexOf("\n")) >= 0) { take(buf.slice(0, i)); buf = buf.slice(i + 1); }
      }
      take(buf);
      if (!got) setErr("the answer did not arrive whole; ask again");
    } catch (x) {
      setErr((x as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-3xl">
      {context ? (
        <p className="mb-3 border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-context={context.view}>
          Opened from <span className="font-mono">{context.view}</span>{context.title ? ` (${context.title})` : ""}
          {context.settings ? <>, set to: {Object.entries(context.settings).map(([k, v]) => `${k} ${v}`).join("; ")}</> : null}. A question that names no period or setting of its own uses these.
        </p>
      ) : null}
      {turns.map((t, i) => <Answer key={i} turn={t} n={i + 1} last={i === turns.length - 1} busy={busy} onAsk={(f) => { setQ(f); void ask(f); }} />)}
      <form onSubmit={(e) => { e.preventDefault(); void ask(q); }} className={`flex flex-col gap-2 sm:flex-row ${turns.length ? "mt-6 border-t border-rule pt-4" : ""}`}>
        <label htmlFor="q" className="sr-only">Question</label>
        <input id="q" value={q} onChange={(e) => setQ(e.target.value)} maxLength={500}
          placeholder={turns.length ? "Ask the next question: it is read as a continuation (and the year before? and at HB_WEST?)" : "For example: how has the price of regulation up changed by year since 2018?"}
          className="flex-1 border border-rule bg-panel px-3 py-2 text-sm" />
        <button type="submit" disabled={busy || !q.trim()} className="border border-accent bg-accent px-4 py-2 text-sm text-paper disabled:opacity-50">
          {busy ? "Querying the ERCOT tables" : turns.length ? "Ask next" : "Ask"}
        </button>
        {turns.length && !busy ? (
          <button type="button" onClick={() => { setTurns([]); setErr(null); setQ(""); }} className="border border-rule bg-panel px-3 py-2 text-sm" data-new-conversation="1">New conversation</button>
        ) : null}
      </form>
      {busy ? (
        <p className="mt-3 text-xs text-muted" role="status" aria-live="polite" data-progress={reading.length}>
          {asked}: {reading.length ? <>reading <span className="font-mono">{reading[reading.length - 1]}</span>{reading.length > 1 ? ` (${reading.length} queries so far)` : ""}. The answer appears whole once every number in it has been checked.</>
            : "working out which tables to read."}
        </p>
      ) : null}
      {turns.length ? <p className="mt-2 text-xs text-muted">The last {Math.min(turns.length, MAX_HISTORY) === 1 ? "answer is" : `${Math.min(turns.length, MAX_HISTORY)} answers are`} sent with the next question, so it can refer to {turns.length === 1 ? "it" : "them"}.</p> : null}
      {err ? (
        <div className="mt-4 border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
          <span className="font-semibold text-ink">no answer</span>: {err}
        </div>
      ) : null}
    </div>
  );
}

function Answer({ turn, n, last, busy, onAsk }: { turn: Turn; n: number; last: boolean; busy: boolean; onAsk: (q: string) => void }) {
  const res = turn.res;
  return (
    <section className={n > 1 ? "mt-8 border-t border-rule pt-5" : "mt-2"} aria-live={last ? "polite" : undefined} data-turn={n} data-status={res.status}>
      <div className="mb-1 text-xs text-muted">{STATUS[res.status] ?? res.status}: {turn.question}</div>
      {res.premise ? (
        <p className="mb-3 border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-premise="1"><span className="font-semibold">The question assumes something the tables do not show.</span> {res.premise}</p>
      ) : null}
      <p className="mb-4 whitespace-pre-wrap leading-relaxed" data-answer="1">{res.answer}</p>
      {(res.nearest ?? []).length ? (
        <div className="mb-4 border border-rule bg-panel px-3 py-2 text-sm" data-nearest={res.nearest!.length}>
          <div className="mb-1 text-xs uppercase tracking-wide text-muted">{res.status === "not_in_warehouse" ? "The nearest thing the warehouse does hold" : "The tables read for this question"}</div>
          <ul>
            {res.nearest!.map((x) => (
              <li key={x.table} className="py-0.5"><Link href={`/data#${x.table}`} className="font-mono" gate="plain">{x.table}</Link>: {x.holds}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {(res.series ?? []).map((s) => <SeriesBlock key={s.result_id} s={s} />)}
      {res.citations.length ? (
        <>
          <h2 className="mb-1 mt-5 border-b border-rule pb-1 text-lg">Sources</h2>
          <ul className="text-sm">
            {res.citations.map((c) => (
              <li key={c.table} className="border-b border-rule/60 py-1">
                {c.table.startsWith("docs/grids/") ? <>Written layer <Link href={`/grid/${c.table.slice(11, -3)}`} className="font-mono">{c.table}</Link></>
                  : <>ERW table <Link href={`/data#${c.table}`} className="font-mono" gate="plain">{c.table}</Link></>}
                {c.tier ? <span className="ml-1 text-xs text-muted">({c.tier})</span> : null}, source report <code className="font-mono text-xs">{c.source_report}</code>
                <div className="text-xs text-muted">{c.data_version}</div>
              </li>
            ))}
          </ul>
        </>
      ) : null}
      {last && (res.followups ?? []).length ? (
        <div className="mt-5" data-followups={res.followups!.length}>
          <div className="mb-1 text-xs uppercase tracking-wide text-muted">Ask next</div>
          <div className="flex flex-col items-start gap-1">
            {res.followups!.map((f) => (
              <button key={f} type="button" disabled={busy} onClick={() => onAsk(f)} className="border border-rule bg-panel px-3 py-1.5 text-left text-sm hover:border-accent hover:text-accent disabled:opacity-50">
                {f}
              </button>
            ))}
          </div>
        </div>
      ) : null}
      <p className="mt-4 text-xs text-muted">
        {res.tool_calls} warehouse queries by {res.model}
        {res.retried ? "; the first draft was sent back by the check" : ""}
        {typeof res.seconds === "number" ? `; ${res.seconds.toFixed(1)} seconds` : ""}
        {res.cost_usd !== null ? `; model cost USD ${res.cost_usd.toFixed(4)}` : ""}.
      </p>
    </section>
  );
}
