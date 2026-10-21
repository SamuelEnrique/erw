import { Fold } from "@/components/tool/ToolPage";
import { SiteLink as Link } from "@/components/SiteLink";

// Session 465: the deal tracker's decisions, in the form roadmap item 2 asks of a finished tool: every choice the
// pages make about the deals, one line each, with the session that made it and the ruling where one exists. Words only,
// no figure: it is drawn under every tab and under the hold, since it describes the method, not a row. DECISIONS is
// exported so tests/test_session465.py can read the list as the page draws it.
export const DECISIONS: { choice: string; session: string; ruling?: string }[] = [
  { choice: "A deal is read only from the news stories the ERW scores: a deal no story in its feeds reported is not here.", session: "15" },
  { choice: "No number is inferred: a number is kept only where the words it was read from are in the story and parse to the same value.", session: "15" },
  { choice: "A state, a country and a status are kept only where a story's words name them.", session: "16", ruling: "session 16's ruling" },
  { choice: "A deal's date is the announced date where a story states it, else the day its first story was published (UTC).", session: "15" },
  { choice: "At the start of a month with no deal yet, the month's counts are the previous month's, labeled.", session: "49" },
  { choice: "Rows the register warehouse/deals/duplicates.csv names as one deal are shown once, with the story links of both.", session: "113" },
  { choice: "Four deal types are named in the panel (power purchase, offtake, project finance, acquisition) and the others gathered under Other; tolling holds none.", session: "113" },
  { choice: "A deal's grid is read from the state a story names, for the states one grid operator mostly serves; the table holds no point of delivery.", session: "113" },
  { choice: "Storage only is a match on words in the technology and the asset.", session: "113" },
  { choice: "A price is a price in US dollars per MWh; a figure in another unit is shown as extracted, never converted.", session: "113" },
  { choice: "The AI power tag is the model's; \"True\" and \"true\" in the table are one flag.", session: "114 and 149" },
  { choice: "A figure a story does not state is \"not stated\", never zero and never an estimate; a sum is over the deals that state the figure, said with their count.", session: "113" },
  { choice: "The kinds of master plan tool 6 (nuclear restart, small modular reactor, gas generation, behind the meter) are the extraction's type or the same words in the asset or technology; gas generation is not called a buildout, since the table does not say whether a plant is new.", session: "465" },
  { choice: "The status is the one the stories state; a deal whose stories state none is not given one.", session: "465" },
  { choice: "The comparables view computes nothing from fewer than three deals that state a figure: such a cell says so.", session: "466" },
  { choice: "Each tab offers its public tables as the live set's CSV with a Python and a Stata reader; the evidence sentences are outlet text and stay internal.", session: "328 and 329" },
  { choice: "From 21 October 2026 energy_deals is held for a license: the page shows the catalogue's words where a deal would be, and how many rows the hold covers.", session: "215 and 465", ruling: "the owner's ruling of 12 October 2026" },
];

export function DealsDecisions() {
  return (
    <div className="mb-8 border-t border-rule" data-deals-decisions={DECISIONS.length}>
      <Fold title={`Decisions (${DECISIONS.length})`}>
        <ol className="max-w-3xl list-decimal space-y-1.5 pl-5">
          {DECISIONS.map((d) => (
            <li key={d.choice}>
              {d.choice} <span className="text-xs text-muted">Session {d.session}{d.ruling ? `; ${d.ruling}` : ""}.</span>
            </li>
          ))}
        </ol>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Each is described in <Link href="/data/methods/energy_deals" className="underline">the method note</Link>.
        </p>
      </Fold>
    </div>
  );
}
