# The contracts tracker: megawatts, prices in words, tags and changes by quarter

Built in session 125 for the review page `/contracts`, on top of `ferc_eqr_contracts` (session 83,
[`ferc_eqr_contracts.md`](ferc_eqr_contracts.md)) and the buyer names by rule (session 99,
[`eqr_buyers.md`](eqr_buyers.md)). Code: `warehouse/derived/eqr_terms.py`, and the connector's history mode in
`warehouse/connectors/ferc_eqr_contracts.py`.

**All four tables are internal,** as their input is. They are in `warehouse/output` and in no file of this repository.
No party's name and no party's figure is written here, in a test, or in a session report: only counts. The examples
below are made up.

| Table | Shape | What a row is |
|---|---|---|
| `ferc_eqr_contracts_history` | events | a contract row as filed for a quarter before the newest, in the shape of `ferc_eqr_contracts`; `x_quarter` says which |
| `ferc_eqr_contract_terms` | events | one row for each row of the newest quarter, with the same `event_id`: the buyer under one name, megawatts and price where stated, tags, the quarters the contract is held in |
| `ferc_eqr_party_mw` | entities | a buyer or a seller of energy, capacity or tolling whose contracts in force state megawatts, ranked by megawatts |
| `ferc_eqr_quarter_changes` | series, quarterly | contracts in force per quarter and product, and those new, gone and kept against the quarter before |

No model is used. Every reading is a rule a person can read, and every row says which rule read it or why none did.

## The pull

Session 125's approved pull: the three quarters before 2026 Q2 (2026 Q1, 2025 Q4, 2025 Q3), a filing at a time,
under a ceiling of 800,000 contract rows for the pull, at no cost.

- `--fetch-only` reads a quarter's filings from FERC's file one at a time, with a pause between two, and keeps each
  filing's contract file under `warehouse/raw/` (not in git). It writes no table and needs no data lock.
- `--history` then writes the quarter from those raw files to `ferc_eqr_contracts_history`. `ferc_eqr_contracts`
  stays one quarter, the newest: every agreement in force is filed again each quarter, so one table of four quarters
  would hold most contracts four times, and the page, the buyers' tables and the live set read one.
- `--also` names the pull's other quarters, whose rows on disk count toward the ceiling. The run refuses to pass it.
- **What was pulled:** 2026 Q1, 4,016 filings and 191,996 contract rows; 2025 Q4, 3,912 of 3,914 filings and 191,132
  rows; 2025 Q3, 3,768 filings and 190,877 rows. 574,005 rows of the 800,000 allowed.
- **What it cost FERC's server:** 2026 Q1, 4,018 requests and 3.74 GB; 2025 Q3, 3,770 and 3.95 GB; 2025 Q4 in two runs,
  the first stopped by an unreadable filing after more than 2,502 requests and 2.6 GB, the second 1,218 and 0.84 GB.
  A filing's zip holds its transactions too; only its contracts file is kept, about 200 MB for the three quarters.
- A filing whose zip cannot be opened is asked for once more; if it is the same again it is left out, named in the
  run log and counted in the table's header. Any other failure stops the run.
- The registry's row for FERC keeps its words and its document; an earlier quarter adds its table only.

## Megawatts, where a quantity is stated

A row states megawatts when its quantity is filed with the units MW, or kW (divided by 1,000). A quantity in
megawatt-hours, per month, per day, or with no units is not a number of megawatts and is not converted. A quantity of
zero is not a quantity.

**The ceiling.** Some rows file a year's megawatt-hours, or kilowatts, under MW: the largest "MW" in the 2026 Q2 file
is above 600,000. A contract cannot be for more than the largest power station operating in the United States, which
the warehouse holds: 6,809 MW (`eia860m_operating_generators`, vintage 2026-08, summed by plant). A row stating more
keeps its figure in `mw`, as filed, carries `x_mw_ranked` no, and is left out of the ranking and counted: 45 rows of
17 contracts in 2026 Q2. A figure under the ceiling can be mislabelled too, and nothing in the filing can tell.

**The ranking** (`ferc_eqr_party_mw`). For each contract in force, the largest MW any of its rows states (a
contract's rows repeat its quantity by period and by product; adding them up would count it many times). Summed by
party: buyers under the name the rules count them as, sellers by FERC's company identifier.

**How little is stated.** In 2026 Q2, megawatts are stated for 356 of 22,808 energy contracts in force, 382 of 12,598
capacity contracts and 3 of 216 tolling contracts. The ranking is of what is stated and is not a ranking of the
market: each row shows the party's place by contracts beside its place by megawatts, and the two differ widely.

## A price from the words

About half the rows file their rate as words and no number (104,952 of 186,873 in 2026 Q2). A price is read from the
words only when number and unit leave one reading. All of these must hold; the first that fails is the row's reason
(`x_price_unread`):

| Reason | The words hold | Made-up example | Rows, 2026 Q2 |
|---|---|---|---|
| `no_dollar_amount` | no dollar amount | "Market Based Rate"; "Per Schedule 4 of the Tariff" | 101,781 |
| `several_amounts` | more than one dollar amount | "2027: $40.00/MWh, 2028: $41.00/MWh" | 636 |
| `no_unit` | an amount not followed at once by a unit of energy, or of capacity over time | "Deposit: $10,000"; "$1.50 per kW of demand" | 1,739 |
| `conditional` | one amount with its unit, and a word that makes it a bound, one case among others, or the start of a formula | "$50/MWh, escalating at 2 percent a year"; "no more than $2.00 per kW-week"; "$0.004/kWh plus ancillary charges" | 766 |
| `other_numbers` | another number that is not a quantity in MW, kW, MWh or kWh | "3rd Amendment; $1.50/MWh" | 2 |
| `units_disagree` | a unit that is not the unit the filing's own rate-units field names | words in $/MWh, the field in $/KW-MO | 5 |
| read | exactly one amount, its unit, at most a quantity beside it | "$42.50 per MWh"; "40 MW; $8.00/kW-month" | 23 |

- **23 rows are read; 104,929 remain unread.** The record's prices in words are almost all not prices: 97 percent
  of them hold no dollar amount at all. The commonest are "Market Based" in its several spellings and "No Rates in
  this Contract".
- **For energy, capacity and tolling alone:** 66,656 rows, 24,384 with a number, 42,246 with words, of which 21 are
  read.
- **A figure with a unit and no dollar sign** ("2.50 per MWH") stands in 47 of the rows with no dollar amount. The
  rule does not read them: the currency is not stated, and most are one component of a charge (a variable operating
  cost) or a term of a formula. They are counted here so that the size of what the dollar sign leaves out is known.
- The units read are FERC's own: `$/MWH`, `$/KWH`, `$/KW-MO`, `$/MW-MO`, `$/MW-DAY`, `$/KW-DAY`, `$/KW-YR`, `$/MW-YR`,
  `$/KW-WK`, `$/MW-WK`, written in the words as "/MWh", "per kW-month" and the like.
- `x_price_words` and `x_price_words_unit` keep what was read, in its own unit. `price` (USD per MWh) is filled only
  from a figure in dollars per megawatt-hour or per kilowatt-hour, filed as a number (`x_price_source` filed) or read
  from the words (words: 9 rows). **A capacity price per kW and month is never turned into dollars per megawatt-hour.**
- The conditional words: escalate, adjust, index, CPI, formula, factor, tier, excess, greater or less or more than, up
  to, above, below, plus, minus, times, a multiplication or addition sign, a percent, LMP, market, peak, a year, a
  date, through, deposit, start, or, higher or lower or lesser of, not to exceed, maximum, minimum, if, unless, until,
  agreed, revise, credit, cap, ceiling, floor, discount, penalty, estimate. The list errs toward leaving a row unread.
- The rule was read against every one of the 23 rows it accepts and against the commonest rows of each reason. Its
  first version accepted a cap ("in no case more than"), a price that applies "if" something happens and a formula
  with a time-of-day factor; those words were added and the rows are now unread.
- The known fault `ferc_eqr_rate_as_filed` (a rate filed as a number in a unit it cannot be in) is a filed number and
  is untouched here: this rule reads words only.

## Tags, from the product fields only

- **tolling:** the product name is TOLLING ENERGY: 382 rows of 217 contracts in 2026 Q2.
- **storage:** a product field (product name, product type, class, term, increment) names storage or a battery.
  **None does.** FERC's product list has no storage product, so the tag is empty in every row.
- **Where the words stand instead** (`x_storage_words_in`, not a tag): in 1,095 rows, in the seller's name (715), the
  rate description (266), the agreement's identifier (163) and the tariff reference (68). A seller named for a
  battery sells other things too, and a tariff's storage schedule is not a contract for a battery. The column says
  where a person would have to read.

## Buyers under one name

`parties`, `x_buyer_counted_as` and `x_buyer_merged` apply the merges of `ferc_eqr_buyer_names`: the ones a rule
makes certain. The 1,281 doubtful pairs of `ferc_eqr_buyer_doubtful` stay listed and are merged nowhere. 128,962 of
the 186,873 rows of 2026 Q2 carry a buyer name counted together with at least one other spelling.

## Contracts new and gone

A contract is the filer's company identifier and its own contract identifier. For two quarters held one after the
other: new is in force in the later and not in the earlier, gone the reverse, kept in both. A filer that renumbers
its contracts makes one gone and one new, so both counts are ceilings on real change. `x_first_quarter` and
`x_quarters_held` on each row of the terms table say how far back the contract is held.

The four quarters of the pull, from their raw files (5 October 2026):

| Filed for | Product | Contracts in force | New | Gone | Kept |
|---|---|---|---|---|---|
| 2025 Q3 | every product | 67,680 | | | |
| 2025 Q3 | energy | 21,904 | | | |
| 2025 Q3 | capacity | 12,080 | | | |
| 2025 Q3 | tolling | 209 | | | |
| 2025 Q4 | every product | 67,914 | 11,863 | 11,629 | 56,051 |
| 2025 Q4 | energy | 21,997 | 5,141 | 5,048 | 16,856 |
| 2025 Q4 | capacity | 12,023 | 3,796 | 3,853 | 8,227 |
| 2025 Q4 | tolling | 215 | 29 | 23 | 186 |
| 2026 Q1 | every product | 68,981 | 12,201 | 11,134 | 56,780 |
| 2026 Q1 | energy | 22,161 | 5,361 | 5,197 | 16,800 |
| 2026 Q1 | capacity | 12,205 | 4,122 | 3,940 | 8,083 |
| 2026 Q1 | tolling | 211 | 39 | 43 | 172 |
| 2026 Q2 | every product | 70,277 | 13,561 | 12,265 | 56,716 |
| 2026 Q2 | energy | 22,808 | 5,453 | 4,806 | 17,355 |
| 2026 Q2 | capacity | 12,598 | 4,258 | 3,865 | 8,340 |
| 2026 Q2 | tolling | 216 | 53 | 48 | 163 |

- **About one contract in six is new each quarter, and about as many leave** (16 to 19 percent of those in force).
  Short-term sales and renumbered contracts are in both counts.
- **Three in four have stood for a year.** Of the 70,277 contracts in force in 2026 Q2, 52,994 are filed in all four
  quarters, 2,189 in three, 2,261 in two and 12,833 in that quarter only. For energy: 16,739 of 22,808 in all four.
- **Two filings of 2025 Q4 are left out.** The zip FERC serves for each is cut off inside its transactions file and
  has no directory (read twice, the same bytes). Their contracts files come first and are whole by the zip's own
  CRC-32 (102 and 323 rows), but the file that names the filer comes after the break, so the rows cannot be given a
  company identifier and a contract cannot be followed across quarters. They are 425 of 191,557 rows; those filers'
  contracts count as gone in 2025 Q4 and as new in 2026 Q1.

## FERC's terms for this data

Quoted, not interpreted; footnote marks left out.

- "The Commission established the EQR reporting requirements to help ensure the collection of information needed to
  perform its regulatory functions over transmission and wholesale sales of electricity, while making data available
  to the public and allowing public utilities to better fulfill their responsibility under Federal Power Act (FPA)
  section 205(c) to have rates on file in a convenient form and place." Federal Register, 17 February 2026, 91 FR
  7278, at 7279, FR Doc. 2026-03012.
- "The Commission adopted the EQR as the reporting mechanism for public utilities to fulfill their responsibility
  under FPA section 205(c) to have information relating to their rates, terms and conditions of service available for
  public inspection in a convenient form and place." Federal Register, 24 March 2026, 91 FR 14306, at 14310, FR
  Doc. 2026-05709 (Order No. 917).

**What could not be read.** The Commission's own pages on `ferc.gov` (its disclaimers, its privacy policy and the
Electric Quarterly Reports page) answered this machine's requests with HTTP 403 on 5 October 2026, as in session 83.
That was not worked around. The report viewer's own page answered and holds no statement of terms. The two passages
say the filings are public; neither is a statement of the terms on which the data may be republished. **The tables
stay internal** until a person has read the Commission's statement.

## What this does not do

- It does not read a price out of a schedule, a formula or a tariff. Those are 104,929 rows.
- It does not say what technology a contract is for.
- It does not merge a doubtful pair, a parent with a subsidiary, or a misspelling no rule covers.
- It does not convert megawatt-hours to megawatts, or a capacity price to an energy price.
- It does not cover Texas: sales inside ERCOT are not filed with FERC.
