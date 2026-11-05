// Energy Research Warehouse (ERW) site, session 462 (chain 019 of 21 October 2026): the "Decisions" block at the foot of
// a page, in the form the grid page (session 299) and /impact (session 347) carry: one fold, closed to start, one line a
// modelling choice the page makes, each ending with the session that made it and the ruling where one exists. The lines
// are data (lib/decisions.ts), so the page and its method note can be checked against one list. Words only: no figure
// of the block is a checked number, and nothing on the page is computed from it.
import type { Decision } from "@/lib/decisions";

export function DecisionsBlock({ id, title, items }: { id: string; title: string; items: Decision[] }) {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions={id}>
      <summary className="cursor-pointer py-1 text-accent">{title}</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={items.length}>
        {items.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text} <span className="text-xs text-muted">({d.session}{d.ruling ? `; ${d.ruling}` : ""})</span>
          </li>
        ))}
      </ul>
    </details>
  );
}
