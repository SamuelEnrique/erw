// Energy Research Warehouse (ERW) site, session 8012 (chain 505, part B2): the decisions of "Energy per AI query, as
// published", in the form of the resource map's (app/resources/Decisions.tsx). docs/methods/ai_energy_published.md,
// "Decisions (session 8012)", carries the same list; tests/test_session8012_ai_energy.py holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type AiDecision = { key: string; text: string; session: string; def: string; source: string };

export const AI_DECISIONS: AiDecision[] = [
  { key: "as-printed", session: "session 8012",
    text: "Every figure is the number its publication printed, in its own unit, beside the publication's own words. No unit is converted.",
    def: "The printed number and unit.",
    source: "The table ai_energy_published: each row cut by a session from the publication's saved copy (docs/methods/ai_energy_published.md)." },
  { key: "no-sum", session: "session 8012",
    text: "Nothing is averaged, summed or set against another figure. The publications measure different things (one prompt, a thousand inferences, a training run, a year of a fleet), and the page says which.",
    def: "No figure of the ERW's own.",
    source: "Chain 505, part B2, after chain 502's part C: no figure of the ERW's own, nothing averaged or summed across publishers, no ranking of companies." },
  { key: "order", session: "session 8012",
    text: "The figures open in the order of their publishers, A to Z, then by date; they can be put in order of what is measured or of date. No order by the figure's size is offered.",
    def: "Publisher, A to Z.",
    source: "ordered in site/lib/aienergy.ts." },
  { key: "no-pair", session: "session 8012",
    text: "No two figures are set side by side for comparison, since no two publications measure the same thing in the same way.",
    def: "One table of every figure.",
    source: "The rule of the site's page standard, two cases side by side where a reader would compare, read against this table's rule of no comparison across publishers." },
  { key: "which-publications", session: "session 8012",
    text: "The publications are those a session found and could read: the model makers' and cloud operators' own statements and the peer-reviewed papers the method note names. A publication whose host refuses automated reading is not read, and is named in the method note.",
    def: "Nine publications on 19 November 2026.",
    source: "docs/methods/ai_energy_published.md, \"Limits\"." },
];

export function AiEnergyDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="ai-energy">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({AI_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={AI_DECISIONS.length}>
        {AI_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-ai-energy-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
