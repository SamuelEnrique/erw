"use client";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { useState } from "react";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

type Citation = { table: string; source_report: string; data_version: string; tier?: string };
type Result = {
  answer: string;
  citations: Citation[];
  status: string;
  model: string;
  tool_calls: number;
  retried: boolean;
  cost_usd: number | null;
};

const STATUS: Record<string, string> = {
  answered: "Answered from the warehouse",
  not_in_warehouse: "Not in the warehouse",
  refused_unverified: "No answer: its numbers could not all be traced to a query",
  model_refusal: "No answer",
};

// session 35: grid, a grid page's scoped chat (/ask?grid=<slug>); initial, the question its Ask box carried
export function AskForm({ grid = null, initial = "", placeholder }: { grid?: string | null; initial?: string; placeholder?: string }) {
  const [q, setQ] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setRes(null);
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: q, ...(grid ? { grid } : {}) }) });
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
          {busy ? "Querying the warehouse" : "Ask"}
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
          <div className="mb-1 text-xs text-muted">{STATUS[res.status] ?? res.status}</div>
          <p className="mb-4 whitespace-pre-wrap leading-relaxed">{res.answer}</p>
          {res.citations.length ? (
            <>
              <h2 className="mb-1 border-b border-rule pb-1 text-lg">Sources</h2>
              <ul className="text-sm">
                {res.citations.map((c) => (
                  <li key={c.table} className="border-b border-rule/60 py-1">
                    {c.table.startsWith("docs/grids/") ? (
                      <>
                        Written layer{" "}
                        <Link href={`/grid/${c.table.slice(11, -3)}`} className="font-mono">
                          {c.table}
                        </Link>
                      </>
                    ) : (
                      <>
                        ERW table{" "}
                        <Link href={`/data#${c.table}`} className="font-mono">
                          {c.table}
                        </Link>
                      </>
                    )}
                    {c.tier === "model_extracted" ? (
                      <span className="ml-1 rounded border border-rule px-1 text-xs" title={TIER_TITLE.model_extracted}>
                        {TIER_LABEL.model_extracted}
                      </span>
                    ) : null}
                    , source report <code className="font-mono text-xs">{c.source_report}</code>
                    <div className="text-xs text-muted">{c.data_version}</div>
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          <p className="mt-3 text-xs text-muted">
            {res.tool_calls} warehouse queries by {res.model}
            {res.retried ? "; the first draft was sent back because a number could not be traced" : ""}
            {res.cost_usd !== null ? `; model cost USD ${res.cost_usd.toFixed(4)}` : ""}.
          </p>
        </section>
      ) : null}
    </div>
  );
}
