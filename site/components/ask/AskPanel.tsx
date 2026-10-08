"use client";
// Energy Research Warehouse (ERW) site, session 137: the question box and its answer panel, one component for any
// page, with the grid as a parameter: <AskPanel grid="ercot" />. The answer appears right below the box, in the form
// the question calls for: words alone for a question about an idea; a sentence or two for one figure; a short answer
// with the chart of the series it fetched for a question about how something moved; the rows as a table for a
// breakdown. A chart is drawn only when the answer's form says so, from the rows in the answer's record (the tool's
// rows, not the model's text; lib/chat/ercot.ts sets each series against the rows fetched before it is sent).
//
// It keeps what sessions 92 and 121 built for /ask/ercot, whose markup the checks read by the same attributes: a
// conversation (the turns before go with the next question), what is being read while the answer is prepared, a
// refusal that names the nearest tables, a premise the tables contradict said first, follow-up questions that ask
// themselves. Nothing about method is on its face: that is in the Method note the page links.
//
// A grid with a profile of its own (today: ercot) is asked as that profile, streamed. Any other grid is asked of the
// general chat for that grid (/api/ask with grid), which answers in words with its sources: the same box, so the
// component can be placed on any grid's page later.
import { useState } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { LineChart } from "@/components/LineChart";
import { HOUR_GROUP, chartPoints, isDrawn, keySeconds } from "@/lib/chat/series";
import { PAGE_FILE_HREF } from "@/lib/chat/pagelinks";

export { keySeconds };

type Citation = { table: string; source_report: string; data_version: string; tier?: string };
type Row = { key: string; value: number | null; n?: number; at?: string };
type Series = {
  result_id: string; table: string; title: string; group_by: string; kind: "line" | "bar"; unit: string | null; rows: Row[];
  rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null; chosen_by: string;
  check?: { rows_fetched: number; rows: number; same: boolean; points: number; not_drawn: number };
};
export type Form = "words" | "sentence" | "chart" | "table";
type Result = {
  answer: string; citations: Citation[]; status: string; model: string; tool_calls: number; retried: boolean; cost_usd: number | null; form?: Form;
  series?: Series[]; followups?: string[];
  seconds?: number; calls?: { tool: string; input: Record<string, unknown> }[]; nearest?: { table: string; holds: string }[]; premise?: string;
};
type Turn = { question: string; res: Result };
const MAX_HISTORY = 3; // earlier turns sent with a question (lib/chat/spec_ercot.json max_history)
export type Context = { view: string; title?: string; settings?: Record<string, string> };

/** The grids with a profile of their own; any other grid is asked of the general chat for that grid. */
const PROFILES = new Set(["ercot"]);
const NOT_ANSWERED: Record<string, string> = {
  not_in_warehouse: "Not in the warehouse",
  refused_unverified: "No answer: its numbers could not all be traced to a query",
  model_refusal: "No answer",
};
const SHOWN = 24; // rows of a table shown before the fold

const shown = (v: number | null) => (v === null ? "not held" : Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { maximumFractionDigits: 4 }));

/** Where a cited source is on this site: the grid's written page, a page built from the tables, or the table's entry. */
export function sourceHref(table: string): { href: string; what: string } {
  if (table.startsWith("docs/grids/")) return { href: `/grid/${table.slice(11, -3)}`, what: "Written page" };
  if (table === "site/data/board.json") return { href: "/board", what: "Price board" };
  if (table === "site/data/supply.json") return { href: "/supply", what: "Supply and trade" };
  if (PAGE_FILE_HREF[table]) return PAGE_FILE_HREF[table];   // session 153: a page's own file, read by the tool page_file
  return { href: `/data#${table}`, what: "ERW table" };
}

function SeriesBlock({ s, form }: { s: Series; form: Form }) {
  const drawn = chartPoints(s.rows, s.group_by);
  const hours = s.group_by === HOUR_GROUP;   // session 161: the average day by hour is one line over the 24 local hours
  const points = drawn.points;
  const chart = form !== "table" && isDrawn(s.kind, drawn);
  const unit = s.unit ?? "";
  const src = sourceHref(s.table);
  return (
    <section className="mt-4 border border-rule bg-panel p-3" data-series={s.result_id} data-form={chart ? "chart" : "table"}>
      <h3 className="mb-1 text-sm font-semibold">{s.title}</h3>
      {chart ? (
        <>
          <LineChart lines={[{ label: s.title, points, color: "accent" }]} unit={unit} height={240} x={hours ? HOUR_GROUP : s.group_by === "year" ? "year" : s.group_by === "month" ? "month" : "minute"}
            ariaLabel={`${s.title}, ${s.rows.length} rows of ${s.table}`} />
          <p className="mt-1 text-xs text-muted" data-chart-check={`${points.length}/${s.rows.length}`}
            title={drawn.undrawn.length ? `Not on the chart, and in the table: ${drawn.undrawn.slice(0, 6).map((u) => `${u.key} (${u.why === "no value" ? "no value held" : "not a point in time"})`).join(", ")}` : "Every row fetched is a point of the chart."}>
            {points.length === s.rows.length ? `${s.rows.length} rows` : `${points.length} of ${s.rows.length} rows`}{hours ? ", one for each local hour of the day" : ""}
          </p>
        </>
      ) : null}
      <details className="mt-2 text-sm" open={!chart || (s.rows.length <= SHOWN && !hours)}>
        <summary className="cursor-pointer text-muted">Table: {s.rows.length} rows</summary>
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
                  <td className="py-0.5 pr-3 text-right">{r.value === null ? <span className="text-muted" title="The table holds no value for this row.">not held</span> : shown(r.value)}</td>
                  <td className="py-0.5 pr-3 text-right text-muted">{r.n ?? ""}</td>
                  <td className="py-0.5 font-mono text-xs">{s.table}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <p className="mt-2 text-xs text-muted">
        Source: {src.what === "ERW table" ? "ERW table" : src.what} <Link href={src.href} className="font-mono" gate="plain">{s.table}</Link>{s.tier ? ` (${s.tier})` : ""}{s.license === "internal" ? ", internal" : ""}; source report {s.source_report ?? "not stated"}.
        {s.rows_matched !== null ? ` Computed from ${s.rows_matched.toLocaleString("en-US")} rows.` : ""}
      </p>
    </section>
  );
}

function Answer({ turn, n, last, busy, onAsk }: { turn: Turn; n: number; last: boolean; busy: boolean; onAsk: (q: string) => void }) {
  const res = turn.res;
  const form: Form = res.form ?? ((res.series ?? []).length ? "chart" : "words");
  return (
    <section className={last ? "mt-4" : "mt-6 border-t border-rule pt-4 opacity-90"} aria-live={last ? "polite" : undefined} data-turn={n} data-status={res.status} data-form={form}
      data-seconds={typeof res.seconds === "number" ? res.seconds.toFixed(1) : undefined}>
      <div className="mb-1 text-xs text-muted">{NOT_ANSWERED[res.status] ? `${NOT_ANSWERED[res.status]}: ` : ""}{turn.question}</div>
      {res.premise ? (
        <p className="mb-3 border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-premise="1"><span className="font-semibold">The question assumes something the tables do not show.</span> {res.premise}</p>
      ) : null}
      <p className="mb-3 whitespace-pre-wrap leading-relaxed" data-answer="1">{res.answer}</p>
      {(res.nearest ?? []).length ? (
        <div className="mb-3 border border-rule bg-panel px-3 py-2 text-sm" data-nearest={res.nearest!.length}>
          <div className="mb-1 text-xs uppercase tracking-wide text-muted">{res.status === "not_in_warehouse" ? "The nearest thing the warehouse does hold" : "The tables read for this question"}</div>
          <ul>
            {res.nearest!.map((x) => (
              <li key={x.table} className="py-0.5"><Link href={`/data#${x.table}`} className="font-mono" gate="plain">{x.table}</Link>: {x.holds}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {(res.series ?? []).map((s) => <SeriesBlock key={s.result_id} s={s} form={form} />)}
      {res.citations.length ? (
        <ul className="mt-3 text-xs text-muted" data-sources={res.citations.length}>
          {res.citations.map((c) => {
            const src = sourceHref(c.table);
            return (
              <li key={c.table} className="py-0.5">
                Source: {src.what} <Link href={src.href} className="font-mono" gate="plain">{c.table}</Link>{c.tier ? ` (${c.tier})` : ""}, <span title={c.data_version}>{c.source_report}</span>
              </li>
            );
          })}
        </ul>
      ) : null}
      {last && (res.followups ?? []).length ? (
        <div className="mt-4" data-followups={res.followups!.length}>
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
    </section>
  );
}

export function AskPanel({ grid, initial = "", context = null, showContext = true, inputId = "q", label, placeholder, methodHref = "/data/methods/ask_ercot" }:
  { grid: string; initial?: string; context?: Context | null; /** false on the page the context names: it need not say where it was opened from */ showContext?: boolean;
    inputId?: string; label?: string; placeholder?: string; methodHref?: string | null }) {
  const [q, setQ] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [asked, setAsked] = useState("");
  const [reading, setReading] = useState<string[]>([]);
  // session 143: the answer's words, shown as soon as they have passed the check, while its chart, sources and next questions are still on their way
  const [early, setEarly] = useState<Turn | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const own = PROFILES.has(grid);
  const name = grid.toUpperCase() === "ISONE" ? "ISO-NE" : grid.toUpperCase();

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setAsked(question);
    setReading([]);
    setEarly(null);
    // the turns before this one: each question, its answer and the queries run for it
    const history = turns.filter((t) => t.res.status === "answered" || t.res.status === "not_in_warehouse").slice(-MAX_HISTORY)
      .map((t) => ({ question: t.question, answer: t.res.answer, calls: t.res.calls ?? [], citations: t.res.citations.map((c) => ({ table: c.table })) }));
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(own ? { question, profile: grid, stream: true, ...(context ? { context } : {}), ...(history.length ? { history } : {}) } : { question, grid }) });
      if (!r.ok || !r.body) {
        const body = await r.json().catch(() => ({}));
        setErr((body as { error?: string }).error ?? `HTTP ${r.status}`);
        return;
      }
      if (!own) {  // the general chat answers in one piece
        const res = (await r.json()) as Result & { error?: string };
        if (res.error) setErr(res.error);
        else { setTurns((t) => [...t, { question, res: { ...res, series: [], form: "words" } }]); setQ(""); }
        return;
      }
      // lines of JSON: what is being read, then the answer, whole and checked
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "", got = false;
      const take = (line: string) => {
        if (!line.trim()) return;
        const e = JSON.parse(line) as { type: string; table?: string | null; tool?: string; error?: string; not_in_warehouse?: boolean } & Partial<Result>;
        if (e.type === "reading") setReading((x) => [...x, e.table ?? (e.tool === "grid_notes" ? `the written page about ${name}` : e.tool === "page_figures" ? "the price board and Supply and trade" : "the list of tables")]);
        else if (e.type === "error") { got = true; setEarly(null); setErr(e.error ?? "no answer"); }
        // session 143: the words first, once checked; the whole answer replaces them when it arrives, and words the whole answer did not bear out are taken back
        else if (e.type === "words" && typeof e.answer === "string") setEarly({ question, res: { answer: e.answer, citations: [], status: e.not_in_warehouse ? "not_in_warehouse" : "answered", model: "", tool_calls: 0, retried: false, cost_usd: null,
          form: e.form === "words" || e.form === "sentence" || e.form === "chart" || e.form === "table" ? e.form : "words", series: [], followups: [], premise: e.premise ?? "" } });
        else if (e.type === "withdrawn") setEarly(null);
        // a whole answer with no type is the route's reply when it did not stream (and the recorded answer the page's check feeds it)
        else if (e.type === "result" || (e.type === undefined && typeof e.answer === "string" && typeof e.status === "string")) { got = true; setEarly(null); setTurns((t) => [...t, { question, res: e as unknown as Result }]); setQ(""); }
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
      setEarly(null);
      setBusy(false);
    }
  }

  // the newest answer sits right below the box; the earlier ones follow it, newest first
  const order = turns.map((t, i) => ({ t, n: i + 1 })).reverse();
  return (
    <div className="max-w-3xl" data-ask-panel={grid}>
      {context && showContext ? (
        <p className="mb-3 border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-context={context.view}>
          Opened from <span className="font-mono">{context.view}</span>{context.title ? ` (${context.title})` : ""}
          {context.settings ? <>, set to: {Object.entries(context.settings).map(([k, v]) => `${k} ${v}`).join("; ")}</> : null}. A question that names no period or setting of its own uses these.
        </p>
      ) : null}
      <form onSubmit={(e) => { e.preventDefault(); void ask(q); }} className="flex flex-col gap-2 border border-rule p-3 sm:flex-row sm:items-center">
        <label htmlFor={inputId} className="text-sm font-semibold">{label ?? `Ask ${name}`}</label>
        <input id={inputId} value={q} onChange={(e) => setQ(e.target.value)} maxLength={500}
          placeholder={placeholder ?? (turns.length ? "Ask the next question: it is read as a continuation" : `For example: how does ${name} set prices? What was the Hub Average price yesterday?`)}
          className="flex-1 border border-rule bg-panel px-3 py-1.5 text-sm" />
        <button type="submit" disabled={busy || !q.trim()} className="border border-accent bg-accent px-4 py-1.5 text-sm text-paper disabled:opacity-50">
          {busy ? "Answering" : turns.length ? "Ask next" : "Ask"}
        </button>
        {turns.length && !busy ? (
          <button type="button" onClick={() => { setTurns([]); setErr(null); setQ(""); }} className="border border-rule bg-panel px-3 py-1.5 text-sm" data-new-conversation="1">New conversation</button>
        ) : null}
      </form>
      {methodHref ? <p className="mt-1 text-xs text-muted"><Link href={methodHref}>Method note</Link></p> : null}
      {busy ? (
        <p className="mt-3 text-xs text-muted" role="status" aria-live="polite" data-progress={reading.length}>
          {asked}: {reading.length ? <>reading <span className="font-mono">{reading[reading.length - 1]}</span>{reading.length > 1 ? ` (${reading.length} so far)` : ""}</> : "thinking"}
        </p>
      ) : null}
      {err ? (
        <div className="mt-3 border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
          <span className="font-semibold text-ink">no answer</span>: {err}
        </div>
      ) : null}
      {busy && early ? <div data-early="1"><Answer turn={early} n={turns.length + 1} last busy onAsk={() => {}} /></div> : null}
      {order.map(({ t, n }) => <Answer key={n} turn={t} n={n} last={n === turns.length && !(busy && early)} busy={busy} onAsk={(f) => { setQ(f); void ask(f); }} />)}
    </div>
  );
}
