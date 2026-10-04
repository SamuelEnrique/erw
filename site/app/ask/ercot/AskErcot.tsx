"use client";
// Energy Research Warehouse (ERW) site, session 92: Ask ERCOT, the reference version (/ask/ercot, in review).
// The form, the answer, its sources, the series it rests on (a chart and a table of the rows the tools returned, each
// with its table and source report) and the follow-up questions, which ask themselves when clicked. The series are
// drawn from the rows in the answer's record (lib/chat/ercot.ts seriesOf): the tool's rows, not the model's text.
import { useState } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { LineChart } from "@/components/LineChart";

type Citation = { table: string; source_report: string; data_version: string; tier?: string };
type Row = { key: string; value: number | null; n?: number; at?: string };
type Series = {
  result_id: string; table: string; title: string; group_by: string; kind: "line" | "bar"; unit: string | null; rows: Row[];
  rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null; chosen_by: string;
};
type Result = {
  answer: string; citations: Citation[]; status: string; model: string; tool_calls: number; retried: boolean; cost_usd: number | null;
  series?: Series[]; followups?: string[];
};
export type Context = { view: string; title?: string; settings?: Record<string, string> };

const STATUS: Record<string, string> = {
  answered: "Answered from the ERCOT tables",
  not_in_warehouse: "Not in the warehouse",
  refused_unverified: "No answer: its numbers could not all be traced to a query",
  model_refusal: "No answer",
};
const SHOWN = 24; // rows of a series shown before the fold

/** A group key as the tools write it ("2021", "2021-03", "2021-03-05", "2021-03-05 14:00") to seconds. */
export function keySeconds(key: string): number | null {
  const m = key.match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?(?: (\d{2}):00)?$/);
  if (!m) return null;
  return Date.UTC(Number(m[1]), m[2] ? Number(m[2]) - 1 : 0, m[3] ? Number(m[3]) : 1, m[4] ? Number(m[4]) : 0) / 1000;
}
const shown = (v: number | null) => (v === null ? "not held" : Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { maximumFractionDigits: 4 }));

function SeriesBlock({ s }: { s: Series }) {
  const points = s.rows.map((r) => ({ t: keySeconds(r.key), v: r.value })).filter((p): p is { t: number; v: number } => p.t !== null && p.v !== null);
  const unit = s.unit ?? "";
  return (
    <section className="mt-5 border border-rule bg-panel p-3" data-series={s.result_id}>
      <h3 className="mb-1 text-sm font-semibold">{s.title}</h3>
      {s.kind === "line" && points.length >= 2 ? (
        <LineChart lines={[{ label: s.title, points, color: "accent" }]} unit={unit} height={240} x={s.group_by === "year" ? "year" : s.group_by === "month" ? "month" : "minute"}
          ariaLabel={`${s.title}, ${s.rows.length} rows of ${s.table}`} />
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
  const [res, setRes] = useState<Result | null>(null);
  const [asked, setAsked] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setRes(null);
    setAsked(question);
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, profile: "ercot", ...(context ? { context } : {}) }) });
      const body = await r.json();
      if (!r.ok) setErr(body.error ?? `HTTP ${r.status}`);
      else setRes(body as Result);
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
      <form onSubmit={(e) => { e.preventDefault(); void ask(q); }} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="q" className="sr-only">Question</label>
        <input id="q" value={q} onChange={(e) => setQ(e.target.value)} maxLength={500}
          placeholder="For example: how has the price of regulation up changed by year since 2018?" className="flex-1 border border-rule bg-panel px-3 py-2 text-sm" />
        <button type="submit" disabled={busy || !q.trim()} className="border border-accent bg-accent px-4 py-2 text-sm text-paper disabled:opacity-50">
          {busy ? "Querying the ERCOT tables" : "Ask"}
        </button>
      </form>
      {busy ? <p className="mt-3 text-xs text-muted">Each answer takes several queries; this can take up to a minute.</p> : null}
      {err ? (
        <div className="mt-4 border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
          <span className="font-semibold text-ink">no answer</span>: {err}
        </div>
      ) : null}
      {res ? (
        <section className="mt-6" aria-live="polite">
          <div className="mb-1 text-xs text-muted">{STATUS[res.status] ?? res.status}{asked ? `: ${asked}` : ""}</div>
          <p className="mb-4 whitespace-pre-wrap leading-relaxed" data-answer="1">{res.answer}</p>
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
          {(res.followups ?? []).length ? (
            <div className="mt-5" data-followups={res.followups!.length}>
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Ask next</div>
              <div className="flex flex-col items-start gap-1">
                {res.followups!.map((f) => (
                  <button key={f} type="button" disabled={busy} onClick={() => { setQ(f); void ask(f); }} className="border border-rule bg-panel px-3 py-1.5 text-left text-sm hover:border-accent hover:text-accent disabled:opacity-50">
                    {f}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          <p className="mt-4 text-xs text-muted">
            {res.tool_calls} warehouse queries by {res.model}
            {res.retried ? "; the first draft was sent back by the check" : ""}
            {res.cost_usd !== null ? `; model cost USD ${res.cost_usd.toFixed(4)}` : ""}.
          </p>
        </section>
      ) : null}
    </div>
  );
}
