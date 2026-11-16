// Energy Research Warehouse (ERW) site, session 7501 (chain 304): the decisions of /contracts, in the form the five
// tools and the trackers carry (components/tool/DecisionsBlock.tsx): one fold at the foot of the page, one line a choice
// that moves a figure of the page, each with the session that made it, and its default and its source on hover. The
// list lives here, in the tool's own folder (the shared list, lib/decisions.ts, is being edited on other branches), and
// is drawn here with the same marks, so a test reads it as it reads the others. Words only: no figure of the page reads
// it, and it is drawn whether or not the server holds the internal token, since it describes the method and no row.
// docs/methods/contracts.md, section 9, carries the same list; site/scripts/test-contracts-render.mjs holds the two
// to one list.
import { Tip } from "@/components/tool/ToolPage";

export type ContractDecision = { key: string; text: string; session: string; ruling?: string; def: string; source: string };

export const CONTRACTS_DECISIONS: ContractDecision[] = [
  { key: "contracts-only", session: "sessions 81 and 83",
    text: "The page reads the contract files of FERC's Electric Quarterly Reports and nothing of the transactions: what was agreed, not what was delivered or billed.",
    def: "Contracts only. The transactions were estimated at about 115 million rows a quarter and were not parsed.",
    source: "Federal Energy Regulatory Commission, Electric Quarterly Reports, quarterly filings of all companies (eqrreportviewer.ferc.gov); the scope of session 81." },
  { key: "newest-filing", session: "session 83",
    text: "A company with more than one filing in the quarter is read from its newest filing; its earlier filings are left out whole.",
    def: "The newest filing. For 2026 Q2: 4,077 filings of 4,010 companies, 67 earlier filings left out.",
    source: "The connector's count in the table's header (docs/methods/ferc_eqr_contracts.md, \"What is in the table\")." },
  { key: "window", session: "session 83",
    text: "The list by quarter signed holds the rows executed in the 1,000 days before the table was last loaded; the other three views read every row of the newest quarter's file.",
    def: "1,000 days. The oldest quarter listed is therefore held in part, and says so on hover.",
    source: "warehouse/supabase/live_set.yaml (event_days: 1000): the live set's size limit. No published rule sets the number." },
  { key: "signed", session: "session 83",
    text: "A contract is new by its execution date, not by standing in the filing: every agreement in force is filed again each quarter. A quarter is the quarter of the execution date.",
    def: "The execution date as filed. A row dated after the quarter it was filed for is counted beside the list and not listed.",
    source: "FERC's contract file, the column contract_execution_date; the three limits of session 81." },
  { key: "product-default", session: "session 83",
    text: "The list opens on energy, capacity and tolling energy: the other products of the form are transmission, interconnection, ancillary and other service agreements.",
    def: "Energy, capacity and tolling (35 percent of the rows of 2026 Q2). \"Every product\" is one click away.",
    source: "FERC's product names, compared in capitals (docs/methods/ferc_eqr_contracts.md, \"Most rows are not power sales\")." },
  { key: "agreement-and-contract", session: "sessions 83 and 99",
    text: "In the list, an agreement is a seller's name with its service agreement identifier. In the other three views, a contract is the filer's company identifier with its own contract identifier. One agreement files a row for each product.",
    def: "Two counts with two names; neither merges a renumbered contract with its old number.",
    source: "FERC's contract file: contract_service_agreement_id and contract_unique_id, with the filer's company identifier." },
  { key: "price-as-filed", session: "session 83",
    text: "A price is the rate and its units when the filer gave a number, else the filer's own words. No price is filled in, converted or estimated.",
    def: "As filed. About half the rows give words.",
    source: "FERC's contract file: rate, rate_units, rate_description." },
  { key: "in-force", session: "session 99",
    text: "A contract is in force when its row files no actual termination date. The largest buyers and sellers, the megawatts and the changes by quarter count contracts in force only.",
    def: "No actual termination date filed. For 2026 Q2: 178,842 rows in force, 8,031 terminated.",
    source: "FERC's contract file, the column actual_termination_date." },
  { key: "buyer-names", session: "session 99",
    text: "A buyer's spellings are counted together only when six rules leave them identical (capitals and spaces, punctuation, a leading \"The\", a short list of abbreviations, the legal form written one way, a name with and without its one legal form). A pair that merely looks alike is listed for a person and not merged.",
    def: "The six rules, in that order; no doubtful pair accepted yet. A buyer's count is a floor.",
    source: "docs/methods/eqr_buyers.md; every merge is a row of the internal table ferc_eqr_buyer_names. FERC publishes no identifier for a buyer." },
  { key: "sellers", session: "session 99",
    text: "A seller is a filer: one FERC company identifier, shown under the spelling it files on the most rows. Sellers are never merged by name, and a parent is not counted with its subsidiaries.",
    def: "FERC's company identifier.",
    source: "The identification file of each filing (company identifier and name)." },
  { key: "rank", session: "session 99",
    text: "The largest buyers and sellers are ranked by contracts in force, then by rows, then by name, and the first 25 of each list are shown. Megawatts do not rank that view.",
    def: "By contracts; 25 shown.",
    source: "docs/methods/eqr_buyers.md, \"ferc_eqr_party_totals\"." },
  { key: "mw-stated", session: "session 125",
    text: "A row states megawatts only when its quantity is filed in MW, or in kW (divided by 1,000). Megawatt-hours, a quantity per month or day, a quantity with no units and a quantity of zero are not megawatts and are not converted.",
    def: "MW and kW only.",
    source: "FERC's contract file: quantity and units (docs/methods/eqr_terms.md, \"Megawatts, where a quantity is stated\")." },
  { key: "mw-ceiling", session: "session 125",
    text: "A row that states more megawatts than the largest power station operating in the United States is left out of the megawatts ranking and counted: it is another unit filed under MW.",
    def: "6,809 MW.",
    source: "U.S. Energy Information Administration, Preliminary Monthly Electric Generator Inventory (Form EIA-860M), operating generators, vintage 2026-08, nameplate summed by plant." },
  { key: "mw-per-contract", session: "session 125",
    text: "A contract's megawatts are the largest any of its rows states, then added up by party: its rows repeat the quantity by period and by product.",
    def: "The largest row. The \"MW filed\" column of the largest buyers and sellers is the other count: every row's MW added up, as filed, with no ceiling.",
    source: "docs/methods/eqr_terms.md, \"The ranking\"." },
  { key: "price-from-words", session: "session 125",
    text: "A price is read from a rate filed as words only when the words hold exactly one dollar amount, followed at once by its unit, with no condition and no other number beside it. Every other row is left unread, with the first test it fails as its reason.",
    def: "The rule errs toward leaving a row unread: 23 rows of 104,952 are read for 2026 Q2.",
    source: "docs/methods/eqr_terms.md, \"A price from the words\": the list of units and of conditional words." },
  { key: "tags", session: "session 125",
    text: "Tolling and storage are tagged only from FERC's product fields (product name, product type, class, term, increment). A seller named for a battery, or a tariff's storage schedule, is counted beside the tag and not tagged.",
    def: "Tolling: the product name Tolling Energy. Storage: no row, since FERC's product list has no storage product.",
    source: "FERC's contract file, the five product columns." },
  { key: "new-and-gone", session: "session 125",
    text: "A contract is new when it is in force in a quarter's filings and not in the quarter before, gone when the reverse. A filer that renumbers its contracts makes one gone and one new, so both counts are ceilings on real change.",
    def: "Two quarters in a row, four quarters held (2025 Q3 to 2026 Q2).",
    source: "ferc_eqr_contracts_history (docs/methods/eqr_terms.md, \"Contracts new and gone\")." },
  { key: "shown", session: "session 83",
    text: "The list draws the first 400 rows of a quarter, newest first, and reads at most 5,000 rows of one quarter; it says so when a quarter holds more.",
    def: "400 drawn, 5,000 read. No quarter held passes 5,000 rows.",
    source: "The page's own limits (site/app/contracts/page.tsx, read.ts); the database function allows no more than 5,000." },
  { key: "internal", session: "session 83", ruling: "the owner's instruction of session 83",
    text: "The table and its seven sister tables are internal: the page is read only in the internal view, offers no download, and a server without the internal token draws no figure and no row.",
    def: "Internal, until a person has read the Commission's own statement of terms.",
    source: "docs/methods/ferc_eqr_contracts.md, \"License\": ferc.gov answered this project's requests with HTTP 403 on 5 October 2026, which was not worked around." },
];

export function ContractsDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7501">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={CONTRACTS_DECISIONS.length}>
        {CONTRACTS_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text} <span className="text-xs text-muted">({d.session}{d.ruling ? `; ${d.ruling}` : ""})</span>
            <Tip id={`decision-7501-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
