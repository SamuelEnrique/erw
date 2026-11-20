"use client";
// Energy Research Warehouse (ERW) site, chain 507 (session 8900): finding a draft at /internal/findings. The sheet of forty
// opens first, in the sheet's order; "Every draft" shows the whole list, newest and strongest first, as the page did.
// Filters: family, the audit's verdict, the reader the sheet names, already known or not, the ruling, and a search of the
// sentences. The count of each verdict stays on screen (a bar held at the top while scrolling), and a count is also a
// filter. The drafts are drawn by the server; this only chooses which to show, forty at a time.
import { Children, useMemo, useState, type ReactNode } from "react";
import { KNOWN_ORDER, KNOWN_TIPS, VERDICT_ORDER, VERDICT_TIPS, type BrowseItem } from "@/lib/findingauditwords";

const STEP = 40;
const ANY = "";
// the drafts this filter sees wait for a ruling (the page lists the ruled ones under "Ruled", as before)
const RULINGS: [string, string][] = [["draft", "not reviewed"], ["full_card_asked", "full card asked"]];

export function AuditBrowser({ items, readers, children }: { items: BrowseItem[]; readers: string[]; children: ReactNode }) {
  const blocks = Children.toArray(children);
  // the sheet first; a list with none of the sheet's drafts in it (a test's fixture, a later sheet) opens on every draft
  const [view, setView] = useState<"sheet" | "all">(items.some((it) => it.rank > 0) ? "sheet" : "all");
  const [family, setFamily] = useState(ANY);
  const [verdict, setVerdict] = useState(ANY);
  const [reader, setReader] = useState(ANY);
  const [known, setKnown] = useState(ANY);
  const [ruling, setRuling] = useState(ANY);
  const [q, setQ] = useState("");
  const [shown, setShown] = useState(STEP);

  const inView = useMemo(() => {
    const idx = items.map((it, i) => ({ it, i })).filter(({ it }) => view === "all" || it.rank > 0);
    return view === "sheet" ? idx.sort((a, b) => a.it.rank - b.it.rank) : idx;
  }, [items, view]);
  const words = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const passes = (it: BrowseItem, skip?: "verdict") =>
    (!family || it.family === family) && (skip === "verdict" || !verdict || it.verdict === verdict) && (!reader || it.reader === reader)
    && (!known || it.known === known) && (!ruling || it.ruling === ruling) && words.every((w) => it.text.includes(w));
  const matches = inView.filter(({ it }) => passes(it));
  const count = (v: string) => inView.filter(({ it }) => passes(it, "verdict") && it.verdict === v).length;
  const families = [...new Set(items.map((it) => it.family).filter(Boolean))].sort();
  const reset = (f: (v: string) => void) => (e: { target: { value: string } }) => { f(e.target.value); setShown(STEP); };
  const verdicts = [...VERDICT_ORDER, "none" as const].filter((v) => items.some((it) => it.verdict === v));

  return (
    <div data-audit-browser={items.length} data-audit-view={view}>
      <div className="sticky top-0 z-20 -mx-1 mb-4 border-b border-rule bg-paper px-1 pb-2 pt-2" data-audit-counts="1">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          {(["sheet", "all"] as const).map((v) => (
            <button key={v} type="button" onClick={() => { setView(v); setShown(STEP); }} aria-pressed={view === v} data-audit-view-button={v}
              className={`border px-3 py-1 ${view === v ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink hover:border-ink"}`}>
              {v === "sheet" ? `The sheet of forty (${items.filter((it) => it.rank > 0).length})` : `Every draft (${items.length})`}
            </button>
          ))}
          <span className="text-xs" data-audit-matches={matches.length}>{matches.length} match</span>
        </div>
        <div className="mt-2 flex flex-wrap gap-1 text-xs">
          {verdicts.map((v) => (
            <button key={v} type="button" onClick={() => { setVerdict(verdict === v ? ANY : v); setShown(STEP); }} aria-pressed={verdict === v} title={VERDICT_TIPS[v]}
              data-audit-count={v} data-n={count(v)}
              className={`border px-2 py-0.5 tabular-nums ${verdict === v ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink hover:border-ink"}`}>
              {v === "none" ? "not covered" : v}: {count(v)}
            </button>
          ))}
        </div>
      </div>
      <div className="mb-4 grid grid-cols-1 gap-2 text-sm sm:grid-cols-3 lg:grid-cols-6" data-audit-filters="1">
        <label className="flex min-w-0 flex-col text-xs">Search
          <input type="search" value={q} onChange={(e) => { setQ(e.target.value); setShown(STEP); }} placeholder="words of the sentence"
            className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-2 py-1 text-sm" data-audit-search="1" />
        </label>
        <label className="flex min-w-0 flex-col text-xs">Family
          <select value={family} onChange={reset(setFamily)} className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-1 py-1 text-sm" data-audit-filter="family">
            <option value={ANY}>every family</option>
            {families.map((f) => <option key={f} value={f}>{f.replace(/_/g, " ")} ({inView.filter(({ it }) => it.family === f).length})</option>)}
          </select>
        </label>
        <label className="flex min-w-0 flex-col text-xs">Verdict
          <select value={verdict} onChange={reset(setVerdict)} className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-1 py-1 text-sm" data-audit-filter="verdict">
            <option value={ANY}>every verdict</option>
            {verdicts.map((v) => <option key={v} value={v}>{v === "none" ? "not covered" : v}</option>)}
          </select>
        </label>
        <label className="flex min-w-0 flex-col text-xs" title="Only the forty on the sheet carry a reader: the one the sheet ranks the finding for.">Reader
          <select value={reader} onChange={reset(setReader)} className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-1 py-1 text-sm" data-audit-filter="reader">
            <option value={ANY}>every reader</option>
            {readers.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        <label className="flex min-w-0 flex-col text-xs">Already known
          <select value={known} onChange={reset(setKnown)} className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-1 py-1 text-sm" data-audit-filter="known">
            <option value={ANY}>new or known</option>
            {KNOWN_ORDER.map((k) => <option key={k} value={k} title={KNOWN_TIPS[k]}>{k}</option>)}
          </select>
        </label>
        <label className="flex min-w-0 flex-col text-xs">Ruling
          <select value={ruling} onChange={reset(setRuling)} className="mt-0.5 w-full min-w-0 border border-rule bg-paper px-1 py-1 text-sm" data-audit-filter="ruling">
            <option value={ANY}>any ruling</option>
            {RULINGS.map(([v, w]) => <option key={v} value={v}>{w}</option>)}
          </select>
        </label>
      </div>
      {matches.length === 0 ? <p className="text-sm" data-audit-none="1">No draft matches.</p> : (
        <div className="flex flex-col gap-8" data-audit-list={Math.min(shown, matches.length)}>
          {matches.slice(0, shown).map(({ it, i }) => <div key={it.id}>{blocks[i]}</div>)}
        </div>
      )}
      {matches.length > shown ? (
        <button type="button" onClick={() => setShown(shown + STEP)} data-audit-more="1"
          className="mt-6 border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink">
          Show the next {Math.min(STEP, matches.length - shown)} of {matches.length - shown}
        </button>
      ) : null}
    </div>
  );
}
