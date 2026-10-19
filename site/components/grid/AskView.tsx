// Energy Research Warehouse (ERW) site, session 237: the Ask view of the Grid tool (/grid), the page's question box.
// ERCOT is asked as its own profile, the deep answers of Ask ERCOT (components/ask/AskPanel.tsx, as on its grid page
// until now: the box answers right below itself). The six other grids are asked of the general chat for that grid, and
// the Lower 48 of the general chat for the whole warehouse (app/ask/AskForm.tsx, the form of /ask). A question carried
// in the address (q) is placed in the box; the page never sends it: a question is sent when the reader presses Ask.
import { AskForm } from "@/app/ask/AskForm";
import { AskPanel } from "@/components/ask/AskPanel";
import { SiteLink as Link } from "@/components/SiteLink";
import { SourceLine } from "@/components/tool/ToolPage";
import type { GridChoice, GridView } from "@/lib/gridtool";

/** Session 299: drawn as the panel beside every tab (`compact`: the panel's smaller type); `tab` is the view on screen,
 * which ERCOT's context names (lib/askContext.ts: a path of the site and its settings), so the answer knows what the
 * reader is looking at. The other grids' chats take the grid alone, as the existing routes do. */
export function AskView({ grid, question, tab = "network", compact = false }: { grid: GridChoice; question: string; tab?: GridView; compact?: boolean }) {
  const q = question.slice(0, 500);
  // the context: the grid page's path (a path of the site, as lib/chat/ercot.ts cleanContext admits it: no query) and the tab on screen in its title and settings
  const context = { view: "/grid/ercot", title: `The grid: ERCOT, ${tab}`, settings: { grid: "ERCOT", tab } };
  return (
    <div data-grid-view="ask" data-ask-compact={compact ? "1" : undefined} data-ask-scope={grid.slug === "ercot" ? "profile:ercot" : grid.slug === "us48" ? "general" : `general:${grid.slug}`}>
      {grid.slug === "ercot" ? (
        <>
          <p className="mb-4 max-w-3xl text-base leading-relaxed">
            Ask ERCOT a question. The answer comes from the ERW&apos;s tables for Texas and appears below the box, with a chart or a table where the question calls for one.
          </p>
          <div className="mb-6"><AskPanel grid="ercot" initial={q} inputId="ask-grid" showContext={false} context={context} /></div>
        </>
      ) : grid.slug === "us48" ? (
        <>
          <p className="mb-4 max-w-3xl text-base leading-relaxed">
            Ask the warehouse a question about US energy prices, demand, generation, projects or news. Every number in an answer comes from a query of a table, and the answer names the table.
            Public tables only; at most 10 questions per hour.
          </p>
          <AskForm initial={q} />
        </>
      ) : (
        <>
          <p className="mb-4 max-w-3xl text-base leading-relaxed">
            Ask {grid.label} a question. This chat speaks for {grid.name} only: it reads the tables and rows that carry {grid.label}, and the text written about it.
            Every number in an answer comes from a query of a table. Public tables only; at most 10 questions per hour.
          </p>
          <AskForm grid={grid.slug} initial={q} placeholder={`For example: what was ${grid.label}'s highest demand this week?`} />
        </>
      )}
      <SourceLine tables={["the live set, through four read-only tools"]} note={<><Link href="/ask">Ask about the whole warehouse</Link>.</>} />
    </div>
  );
}

/** The question box at the foot of the other views: it opens the Ask view with the question placed in its box. */
export function AskBox({ grid }: { grid: GridChoice }) {
  const who = grid.slug === "us48" ? "the warehouse" : grid.label;
  return (
    <form action="/grid" method="get" className="mt-8 flex max-w-3xl flex-col gap-2 border border-rule p-3 sm:flex-row sm:items-center" data-ask-box={grid.slug}>
      <label htmlFor="ask-box" className="text-sm font-semibold">Ask {who}</label>
      <input type="hidden" name="grid" value={grid.slug} />
      <input type="hidden" name="view" value="ask" />
      <input id="ask-box" name="q" maxLength={500} placeholder={grid.slug === "us48" ? "For example: which grid used the most power yesterday?" : `For example: what was ${grid.label}'s highest demand this week?`} className="flex-1 border border-rule bg-panel px-3 py-1.5 text-sm" />
      <button type="submit" className="border border-accent px-3 py-1.5 text-sm text-accent">Ask</button>
    </form>
  );
}
