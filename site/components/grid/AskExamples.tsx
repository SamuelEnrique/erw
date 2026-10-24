// Energy Research Warehouse (ERW) site, session 1157 (chain 077): the stored example answers under the Ask box of the
// Grid tool (/grid), for the grid on screen (lib/gridask.ts, data/grid_ask_examples.json). Each is an answer a recorded
// evaluation of /api/ask graded right, shown as stored, with each figure's source: the table, the filter of the call
// that returned it, and the day it was asked. Folded, one <details> each, so the live box above stays first. No model
// is called and no question is sent: these are stored texts, not figures read from the database, so they carry no
// data-check key (check-values has nothing to recompute in them). An example whose figures come from a table held for
// the grid today is not shown; in its place stand the live Ask's words for that read (lib/license.ts licenseReason).
import { askTabOfView, askTabsOf, examplesLine, gridAskExamples } from "@/lib/gridask";
import type { GridChoice, GridView } from "@/lib/gridtool";
import { GRID_ANCHOR, METHOD_ASK } from "@/lib/gridAnchors";  // session 1183: each panel's anchor; session 1184: its method
import { SiteLink as Link } from "@/components/SiteLink";
import { PanelMethod } from "@/components/grid/PanelMethod";  // session 1184: the line that links the panel's method

const dayWords = (iso: string) => {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso.slice(0, 10) : new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(d);
};

// Session 1405: with the tab on screen (`tab`, the page's view), that tab's examples first (lib/gridask.ts orderByTab);
// the same examples, each <details> closed as before.
export function AskExamples({ grid, tab, now = new Date() }: { grid: GridChoice; tab?: GridView; now?: Date }) {
  const { label, shown } = gridAskExamples(grid.slug, now, undefined, tab ?? null);
  return (
    <section className="mt-8 border-t border-rule pt-3" data-grid-panel={`grid_ask_${grid.slug}`} id={GRID_ANCHOR.ask} data-ask-examples={shown.length} data-ask-stored="1" data-ask-order={tab ? askTabOfView(tab) : undefined} aria-labelledby={`ask-examples-${grid.slug}`}>
      <h3 id={`ask-examples-${grid.slug}`} className="mb-1 font-serif text-base">Stored answers</h3>
      <p className="mb-2 text-xs leading-relaxed text-muted" data-ask-examples-line="1">
        {examplesLine(shown.length, label)} Each is the text a recorded evaluation of this box stored, with the table and filter behind each figure and the day it was asked; nothing here is sent or asked again, so the figures are as of that day.
      </p>
      {shown.map((e) => (
        // session 1158: break-words, so a filter written without a space (where={...}) wraps in the 390 px column, not past it
        <details key={e.id} className="border-b border-rule py-2 text-sm break-words" data-ask-example={e.id} data-ask-example-held={e.held ? e.held.table : undefined} data-ask-example-tab={askTabsOf(e).join(",") || undefined}>
          <summary className="cursor-pointer text-accent">{e.question}</summary>
          {e.held ? (
            <p className="mt-2 leading-relaxed" data-ask-held={e.held.table}>
              {e.held.words}. The stored answer read <code className="font-mono">{e.held.table}</code>, which is held for {label} today, so it is not shown.
            </p>
          ) : (
            <>
              <p className="mt-2 whitespace-pre-line leading-relaxed" data-ask-example-answer="1">{e.answer}</p>
              {e.sources.length ? (
                <ul className="mt-2 space-y-1 text-xs leading-relaxed text-muted" data-ask-example-sources={e.sources.length}>
                  {e.sources.map((s, i) => (
                    <li key={i} data-ask-example-source={s.tables.join(",")}>
                      <span className="font-mono">{s.figures.join(", ")}</span>: {s.tables.map((t, j) => <span key={t}>{j ? ", " : ""}<code className="font-mono">{t}</code></span>)}, {s.tool}{s.filter ? <> with <span className="font-mono">{s.filter}</span></> : null}, read {dayWords(e.asked_at_utc)}.
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-xs text-muted">No figure: the answer says what the warehouse does not hold.</p>
              )}
            </>
          )}
          <p className="mt-2 text-xs text-muted" data-ask-example-run={e.file}>
            From {e.run}: <code className="font-mono">{e.file}</code>, question {e.question_id}.
          </p>
        </details>
      ))}
      <PanelMethod at="ask"><Link href={METHOD_ASK}>Method: the stored answers, in the Grid tool&apos;s panels</Link></PanelMethod>
    </section>
  );
}
