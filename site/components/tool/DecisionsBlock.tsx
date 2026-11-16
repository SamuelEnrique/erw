// Energy Research Warehouse (ERW) site, session 462 (chain 019 of 21 October 2026): the "Decisions" block at the foot of
// a page, in the form the grid page (session 299) and /impact (session 347) carry: one fold, closed to start, one line a
// modelling choice the page makes, each ending with the session that made it and the ruling where one exists. The lines
// are data (lib/decisions.ts), so the page and its method note can be checked against one list. Words only: no figure
// of the block is a checked number, and nothing on the page is computed from it.
import type { Decision } from "@/lib/decisions";
import { Tip } from "@/components/tool/ToolPage";

// Session 5001 (chain 233): `open` draws the fold open to start, for the battery page, which has nothing collapsed (the
// owner's ruling of 12 October 2026); the other pages pass nothing and are as they were.
export function DecisionsBlock({ id, title, items, open = false }: { id: string; title: string; items: Decision[]; open?: boolean }) {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions={id} open={open || undefined}>
      <summary className="cursor-pointer py-1 text-accent">{title}</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={items.length}>
        {items.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text} <span className="text-xs text-muted">({d.session}{d.ruling ? `; ${d.ruling}` : ""})</span>
            {/* session 7402 (chain 303): a choice's default and its source, on hover, tap or focus, where the list gives them */}
            {d.def || d.source ? (
              <Tip id={`decision-${id}-${d.key}`} label="this choice's default and source">
                {d.def ? <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span> : null}
                {d.source ? <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span> : null}
              </Tip>
            ) : null}
          </li>
        ))}
      </ul>
    </details>
  );
}
