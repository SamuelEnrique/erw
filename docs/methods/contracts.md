# The contracts page as a reader meets it: method

Written in session 7501 (chain 304, 16 November 2026) for `/contracts`, "Where power contracts are being struck". It
says, view by view, which table and which rule every figure of the page comes from, in enough detail to compute each
again from the rows (`replication/contracts/replicate.py` does, from this note). The tables' own notes stay the record
of how each table is built: [`ferc_eqr_contracts.md`](ferc_eqr_contracts.md) (the pull and the columns),
[`eqr_buyers.md`](eqr_buyers.md) (the buyer names by rule) and [`eqr_terms.md`](eqr_terms.md) (megawatts, prices in
words, tags, changes by quarter). Where this note and one of those differ on what the page shows, this note is the
later one.

Tables: `ferc_eqr_contracts`, `ferc_eqr_contracts_history` (source); `ferc_eqr_buyer_names`, `ferc_eqr_buyer_doubtful`,
`ferc_eqr_party_totals`, `ferc_eqr_contract_terms`, `ferc_eqr_party_mw`, `ferc_eqr_quarter_changes` (derived). All
eight are internal. No party's name and no party's own figure is written in this note: counts only.

## 1. The tables and the columns read

One row of `ferc_eqr_contracts` is one product of one agreement, as a seller filed it with the Federal Energy
Regulatory Commission in its Electric Quarterly Report for the newest quarter held (2026 Q2: 186,873 rows, retrieved
on 4 October 2026). `ferc_eqr_contracts_history` holds the three quarters before it in the same shape (571,115 rows).
The page's figures read these columns and no other:

| The page's word | Column | Read as |
|---|---|---|
| signed | `event_date` | the execution date, its first ten characters |
| in force | `x_actual_termination_date` | in force when empty (the table's `status` says the same on every row) |
| product | `x_product_name` | trimmed, in capitals: filers write a name in more than one way |
| seller, its filer | `x_seller_company_name`, `x_company_id` | as filed |
| buyer | `x_customer_company_name` | as filed |
| affiliate | `x_contract_affiliate` | yes when Y, in either case |
| agreement | `x_contract_service_agreement_id` | as filed |
| contract | `x_company_id` with `x_contract_unique_id` | joined by a bar |
| quantity | `x_quantity`, `x_units` | as filed |
| price | `x_rate`, `x_rate_units`, `x_rate_description` | as filed |
| delivered | `x_point_of_delivery_balancing_authority`, `x_point_of_delivery_specific_location` | as filed |
| term | `x_commencement_date_of_contract_term`, `x_contract_termination_date` | eight digits as a date |
| filed for | `x_quarter` | `2026_Q2` |
| product fields | `x_product_name`, `x_product_type_name`, `x_class_name`, `x_term_name`, `x_increment_name` | for the tags |
| tariff | `x_ferc_tariff_reference` | for the storage words |

## 2. The constants

| Constant | Value | Where it is set |
|---|---|---|
| The days of execution the list holds | 1,000 before the day of a load | `warehouse/supabase/live_set.yaml`, `event_days` |
| Rows of a quarter read | 5,000 | `site/app/contracts/read.ts`; migration 020 allows no more |
| Rows of a quarter drawn | 400 | `site/app/contracts/page.tsx` |
| Quarters listed | 12 | the page |
| Balancing authorities listed | 14 | the page |
| Parties shown in a ranking | 25 | `warehouse/supabase/load.py`, `EQR_TOP` |
| The most megawatts one contract can state | 6,809 MW | the largest station of `eia860m_operating_generators` (section 6) |
| Near spelling | 94 percent, names of 12 letters or more | `warehouse/derived/eqr_buyers.py` |

## 3. View 1: the contracts by the quarter signed

**The rows.** The live set holds the rows whose execution date is on or after the day 1,000 days before the load. The
last load the notes record was on 5 October 2026: 18,989 rows, executed on or after 9 January 2024. The loader stores
one summary of those rows with them (`load.py`, `eqr_summary`): rows, rows with a rate filed (`x_rate` not empty), the
first and last execution date, the quarters filed for, and rows by month, by product and by balancing authority. The
page reads that summary, and the rows of one quarter of execution at a time.

**The panel.** The quarters of execution, newest first, up to the quarter filed for and at most 12, each with its rows.
Rows dated after the quarter filed for are counted in one line under the list (54: 46 between July 2026 and January
2027, 7 in 2101, 1 in 2223) and are not listed. The oldest quarter listed is held in part: 2024 Q1 lists 1,404 rows,
those from 9 January on, where the whole file holds 1,546 for that quarter; since session 7501 the page says so on
hover. The product groups: energy, capacity and tolling (the default), each of the three, and every product. The
balancing authorities of the quarter and product chosen, most rows first, ties by name, at most 14: an authority is
its code trimmed and in capitals, and "not stated" for a row that files none (since session 7501: before, "PSCO" and
"PSCo" were two entries, and "not stated" opened no row).

**The sentence and the three headline cells**, for the rows of the quarter, product and authority chosen:

- rows: their count;
- agreements: the distinct pairs of seller name and service agreement identifier (not the contract of sections 5 to 7);
- sellers, buyers: the distinct names as filed, an empty name not counted;
- rows with a price as a number: `x_rate` not empty; "the other" rows are the rest, which give words or nothing;
- between affiliates: the rows the seller marked Y.

**The list**: the first 400 rows, by execution date newest first, then seller, then row identifier. Every cell is as
filed. The term in years is shown when both dates are eight digits and the end is not before the start: the days
between them over 365.25, to one decimal. A day past its month's end runs into the next month, as the page's engine
reads it. An execution date after today carries "as filed" (the ruling of 18 October 2026, item 5); since session 7501
the panel's note does the same for the last date held (2223-01-01).

**The limits box**, on every view: of the rows held in the live set (18,989), those that file no number (10,956). Of
these 10,907 file words and 49 file neither; the box said all 10,956 "give their price as words" until session 7501.

**ERCOT**: the rows of the live set whose authority is ERCO (14 of 18,989; 244 in the whole file).

## 4. What a visitor sees, and what the internal view sees

- **A visitor sees none of this.** `/contracts` is `review` in `site/lib/release.ts`: every visitor is shown the
  in-review page at this address. The page is also marked not to be indexed.
- **The internal view** (a reviewer's: `site/lib/release.ts`) is drawn the page. Its server asks two database functions,
  `internal_eqr_summary` and `internal_eqr_contracts`, with the internal token it holds as `INTERNAL_COSTS_TOKEN`. The
  token is never sent to a browser. Row-level security hides the rows from the public key, so no other read reaches them.
- **A server without the token** asks nothing and draws no figure, no row and no party's name: the list says the table
  is internal, the other three views say they are not loaded. The decisions block and the source line are still drawn.
- **No download** is offered, on the page or on `/data`. No row is in git: the replication copies the rows at run time
  into a folder git ignores, and its written figures hold counts only. A party's own figure is compared and not written.

## 5. View 2: the largest buyers and sellers

**The rows**: every row of the newest quarter's file that is in force and whose product is ENERGY, CAPACITY or TOLLING
ENERGY (66,192 rows), whenever it was signed. Not the live set's 18,989.

**A buyer's name, by six rules in order.** Two spellings are one buyer only when all six leave them identical.

1. Capitals; runs of spaces closed up; leading and trailing spaces off.
2. "&" read as " AND "; these taken out: `. , ' " ` ( ) [ ]` (the period, comma, apostrophe, quotation mark, grave
   accent, round and square brackets); a hyphen or a slash read as a space.
3. A leading THE taken off, when another word follows.
4. A whole word written one way: CORPORATION as CORP, INCORPORATED as INC, COMPANY as CO, LIMITED as LTD, COOP as
   COOPERATIVE, ASSN and ASSOC as ASSOCIATION, ELEC as ELECTRIC, DEPT as DEPARTMENT, AUTH as AUTHORITY, MGMT as
   MANAGEMENT, SVC as SERVICE, SVCS as SERVICES, INTL as INTERNATIONAL, NATL as NATIONAL, PWR as POWER, MKTG as
   MARKETING, TRANSM as TRANSMISSION.
5. The legal form at the end written one way, the first of these that the name ends with, when a word stands before
   it: LIMITED LIABILITY COMPANY, LTD LIABILITY CO, L L C as LLC; LIMITED PARTNERSHIP, LTD PARTNERSHIP, L P as LP;
   L L P as LLP; P L C as PLC; N A as NA.
6. A name with no legal form at its end is counted with the same name that has one, when exactly one form is filed for
   it. The forms: LLC, LLP, LP, INC, CORP, CO, LTD, PLC, NA. CO is not a form at the end of a name that begins CITY,
   TOWN, VILLAGE, COUNTY or BOROUGH or that holds OF: there it may be Colorado.

A group is shown under the spelling filed on the most rows of the whole file (a tie: the first in order of
characters). 17,955 names as filed are 13,836 after the rules; 6,460 names stand in a group of more than one.

**Doubtful pairs, listed and never merged** (1,281): the same name under two legal forms (245); a name that is another
group's name plus a clause, d/b/a, f/k/a, a/k/a, "as agent for" or a closing bracketed clause (349); and two group
names of 12 letters or more that begin with the same four letters, differ in length by at most 3, and are at least 94
percent alike (Python's `difflib` ratio), unless they differ only by a numeral (digits, a Roman numeral, or a letter A
to H) or are already a pair of legal forms (687).

**The figures.** A buyer is its group; a seller is a FERC company identifier, shown under the spelling it files on the
most of these rows. Per party and product: contracts (distinct contracts, section 1), rows, counterparties (for a
buyer, the filers it buys from; for a seller, its buyers after the rules), "MW filed" (the sum of the quantities whose
units are exactly `MW`, every row added, zero included, no ceiling) and the rows that file one. The rank is by
contracts, then rows, then name; 25 are shown. The sentence's count of contracts is the buyers' contracts added up,
which is the count of distinct contracts since no contract has two buyers after the rules.

## 6. View 3: ranked by megawatts stated

- **A row states megawatts** when its quantity is a number above zero and its units, trimmed and in capitals, are MW
  (the quantity) or KW (a thousandth of it). 11,579 rows of 186,873 do.
- **The ceiling**: the largest sum of nameplate capacity of one plant in `eia860m_operating_generators`, 6,809.0 MW
  (the same in the vintages of August and September 2026). A row above it is left out and counted: 45 rows in all.
- **Per contract**, the largest megawatts any of its rows in force states, for the product chosen; then the sum by
  party (buyers by group, sellers by filer), each party's sum rounded to three decimals and the total to one.
- **The counts**: the contracts in force of the product; those with a row under the ceiling; those with a row above it.
  A contract can be in both.
- **The rank** is by megawatts, then name. "Place by contracts" is said by the page to be the party's place in view 2.
  The table computes it by contracts, then name, without the rows: for a party tied on contracts it is another place
  (29 of the 105 cells drawn are view 2's place). This is fault 7, the data machine's.

## 7. View 4: what the filings state

**Prices.** A row files a number when `x_rate` reads as a number (81,718); words when it does not and
`x_rate_description` is not empty (104,952); neither (203). A price is read from the words only when all of these
hold, tested in this order on the words with runs of spaces closed up; the first that fails is the row's reason:

1. `no_dollar_amount`: no "$" followed by a number (digits with commas and an optional decimal part, or a decimal part
   alone), spaces allowed between;
2. `several_amounts`: more than one;
3. `no_unit`: the amount is not followed at once by "/" or "per" and a unit: MWh (also mw-h, megawatt hour), kWh, or
   kW or MW (also kilowatt, megawatt) joined by a hyphen, a slash or a space to mo, mos, month, mth, day, yr, year, wk
   or week;
4. `conditional`: the rest of the words hold one of: escalat, adjust, index, CPI, formula, tier, excess, greater, less
   than, up to, above, below, plus, minus, times, multipl, a plus sign, an asterisk, a percent sign, percent, LMP,
   market, peak, a year from 1900 to 2099, a date with slashes, thru, through, deposit, start, or, higher of, lower
   of, lesser, not to exceed, maximum, minimum, a lone x, if, more than, no case, agreed, revis, factor, unless, until,
   credit, cap, ceiling, floor, discount, penalt, estimat;
5. `other_numbers`: another number stands in the rest that is not followed by MW, kW, MWh, kWh, megawatt or kilowatt;
6. `units_disagree`: the row's `x_rate_units` is not empty and is not the unit read.

23 rows pass (10 in $/KW-MO, 9 in $/MWH, 3 in $/MW-DAY, 1 in $/MW-MO); 104,929 do not (101,781; 636; 1,739; 766; 2; 5).
Only a figure per MWh or per kWh is a price in dollars per megawatt-hour (9 rows).

**Tags.** Tolling: the product name is TOLLING ENERGY, every row filed, a terminated contract's too: 382 rows of 217
contracts, of which 216 are in force (the figure of the table below it and of views 2 and 3; the page says so on hover
since session 7501). Storage: a product field holds "storage", "batter" or the word BESS: no row. The same words
elsewhere, counted and not tagged: the seller's name (715), the rate description (266), the agreement's identifier
(163), the tariff reference (68); 1,095 rows in all.

**Contracts new and gone.** For each quarter held, the contracts in force (every product, and each of the three). For
two quarters in a row: new is in force in the later and not in the earlier, gone the reverse, kept in both.

**Buyers under one name**: the rows whose buyer stands in a group of more than one name (128,962), and the doubtful
pairs (1,281).

## 8. The cross-check against published figures

| Figure | Ours | Published | Publisher, document, date | Difference, and why |
|---|---|---|---|---|
| Companies that file the report | 3,704 for 2025 Q3; 4,010 for 2026 Q2 (4,077 filings) | 3,672, "the total number of EQR filers as of Q2 2025" | Federal Energy Regulatory Commission, Order No. 917, 91 FR 14306, footnote 354, 24 March 2026; the same count in the FERC-920 notice, 91 FR 7278, 17 February 2026 | +32 (0.9 percent) one quarter later; +338 (9.2 percent) four quarters later. Ours counts the company identifiers in FERC's own file of each quarter's filings. The quarter FERC counted is not held, so no quarter is compared like for like |
| The largest power station operating in the United States | 6,809.0 MW | 6,809.0 MW | U.S. Energy Information Administration, EIA-860M, Inventory of Operating Generators as of September 2026 (the warehouse's table of it) | None: the figure is computed from the publisher's own inventory, nameplate summed by plant |
| Contracts in force by product; megawatts stated; rows by price as number or words; contracts new and gone; the largest buyers and sellers | sections 5 to 7 | nothing published | | The Commission publishes the filings and no tally of them that this project could read |

- **Hosts read, robots and terms first** (16 November 2026): `www.federalregister.gov` (its robots file disallows only
  search and account paths; the two documents were read through its documented interface and its full-text files).
- **Hosts that refused**: `www.ferc.gov`. Its robots file answered and disallows no content page, but its disclaimers
  page, its privacy policy and its Electric Quarterly Reports page each answered HTTP 403, as on 5 October 2026. That
  was not worked around, and nothing of `ferc.gov` is quoted here. `eqrreportviewer.ferc.gov` has no robots file (HTTP
  404) and was asked nothing else today.
- No figure was adjusted to match.

## 9. The decisions on the page

The block at the foot of the page (`site/app/contracts/Decisions.tsx`) lists these, each with its default and its
source on hover. The list here is the page's, word for word (`site/scripts/test-contracts-render.mjs` holds the two
together).

1. **contracts-only** (sessions 81 and 83). The page reads the contract files of FERC's Electric Quarterly Reports and nothing of the transactions: what was agreed, not what was delivered or billed.
   - Default: Contracts only. The transactions were estimated at about 115 million rows a quarter and were not parsed.
   - Source: Federal Energy Regulatory Commission, Electric Quarterly Reports, quarterly filings of all companies (eqrreportviewer.ferc.gov); the scope of session 81.
2. **newest-filing** (session 83). A company with more than one filing in the quarter is read from its newest filing; its earlier filings are left out whole.
   - Default: The newest filing. For 2026 Q2: 4,077 filings of 4,010 companies, 67 earlier filings left out.
   - Source: The connector's count in the table's header (docs/methods/ferc_eqr_contracts.md, "What is in the table").
3. **window** (session 83). The list by quarter signed holds the rows executed in the 1,000 days before the table was last loaded; the other three views read every row of the newest quarter's file.
   - Default: 1,000 days. The oldest quarter listed is therefore held in part, and says so on hover.
   - Source: warehouse/supabase/live_set.yaml (event_days: 1000): the live set's size limit. No published rule sets the number.
4. **signed** (session 83). A contract is new by its execution date, not by standing in the filing: every agreement in force is filed again each quarter. A quarter is the quarter of the execution date.
   - Default: The execution date as filed. A row dated after the quarter it was filed for is counted beside the list and not listed.
   - Source: FERC's contract file, the column contract_execution_date; the three limits of session 81.
5. **product-default** (session 83). The list opens on energy, capacity and tolling energy: the other products of the form are transmission, interconnection, ancillary and other service agreements.
   - Default: Energy, capacity and tolling (35 percent of the rows of 2026 Q2). "Every product" is one click away.
   - Source: FERC's product names, compared in capitals (docs/methods/ferc_eqr_contracts.md, "Most rows are not power sales").
6. **agreement-and-contract** (sessions 83 and 99). In the list, an agreement is a seller's name with its service agreement identifier. In the other three views, a contract is the filer's company identifier with its own contract identifier. One agreement files a row for each product.
   - Default: Two counts with two names; neither merges a renumbered contract with its old number.
   - Source: FERC's contract file: contract_service_agreement_id and contract_unique_id, with the filer's company identifier.
7. **price-as-filed** (session 83). A price is the rate and its units when the filer gave a number, else the filer's own words. No price is filled in, converted or estimated.
   - Default: As filed. About half the rows give words.
   - Source: FERC's contract file: rate, rate_units, rate_description.
8. **in-force** (session 99). A contract is in force when its row files no actual termination date. The largest buyers and sellers, the megawatts and the changes by quarter count contracts in force only.
   - Default: No actual termination date filed. For 2026 Q2: 178,842 rows in force, 8,031 terminated.
   - Source: FERC's contract file, the column actual_termination_date.
9. **buyer-names** (session 99). A buyer's spellings are counted together only when six rules leave them identical (capitals and spaces, punctuation, a leading "The", a short list of abbreviations, the legal form written one way, a name with and without its one legal form). A pair that merely looks alike is listed for a person and not merged.
   - Default: The six rules, in that order; no doubtful pair accepted yet. A buyer's count is a floor.
   - Source: docs/methods/eqr_buyers.md; every merge is a row of the internal table ferc_eqr_buyer_names. FERC publishes no identifier for a buyer.
10. **sellers** (session 99). A seller is a filer: one FERC company identifier, shown under the spelling it files on the most rows. Sellers are never merged by name, and a parent is not counted with its subsidiaries.
   - Default: FERC's company identifier.
   - Source: The identification file of each filing (company identifier and name).
11. **rank** (session 99). The largest buyers and sellers are ranked by contracts in force, then by rows, then by name, and the first 25 of each list are shown. Megawatts do not rank that view.
   - Default: By contracts; 25 shown.
   - Source: docs/methods/eqr_buyers.md, "ferc_eqr_party_totals".
12. **mw-stated** (session 125). A row states megawatts only when its quantity is filed in MW, or in kW (divided by 1,000). Megawatt-hours, a quantity per month or day, a quantity with no units and a quantity of zero are not megawatts and are not converted.
   - Default: MW and kW only.
   - Source: FERC's contract file: quantity and units (docs/methods/eqr_terms.md, "Megawatts, where a quantity is stated").
13. **mw-ceiling** (session 125). A row that states more megawatts than the largest power station operating in the United States is left out of the megawatts ranking and counted: it is another unit filed under MW.
   - Default: 6,809 MW.
   - Source: U.S. Energy Information Administration, EIA-860M, Inventory of Operating Generators, vintage 2026-08 (the same figure in the inventory as of September 2026), nameplate capacity summed by plant.
14. **mw-per-contract** (session 125). A contract's megawatts are the largest any of its rows states, then added up by party: its rows repeat the quantity by period and by product.
   - Default: The largest row. The "MW filed" column of the largest buyers and sellers is the other count: every row's MW added up, as filed, with no ceiling.
   - Source: docs/methods/eqr_terms.md, "The ranking".
15. **price-from-words** (session 125). A price is read from a rate filed as words only when the words hold exactly one dollar amount, followed at once by its unit, with no condition and no other number beside it. Every other row is left unread, with the first test it fails as its reason.
   - Default: The rule errs toward leaving a row unread: 23 rows of 104,952 are read for 2026 Q2.
   - Source: docs/methods/eqr_terms.md, "A price from the words": the list of units and of conditional words.
16. **tags** (session 125). Tolling and storage are tagged only from FERC's product fields (product name, product type, class, term, increment). A seller named for a battery, or a tariff's storage schedule, is counted beside the tag and not tagged.
   - Default: Tolling: the product name Tolling Energy. Storage: no row, since FERC's product list has no storage product.
   - Source: FERC's contract file, the five product columns.
17. **new-and-gone** (session 125). A contract is new when it is in force in a quarter's filings and not in the quarter before, gone when the reverse. A filer that renumbers its contracts makes one gone and one new, so both counts are ceilings on real change.
   - Default: Two quarters in a row, four quarters held (2025 Q3 to 2026 Q2).
   - Source: ferc_eqr_contracts_history (docs/methods/eqr_terms.md, "Contracts new and gone").
18. **shown** (session 83). The list draws the first 400 rows of a quarter, newest first, and reads at most 5,000 rows of one quarter; it says so when a quarter holds more.
   - Default: 400 drawn, 5,000 read. No quarter held passes 5,000 rows.
   - Source: The page's own limits (site/app/contracts/page.tsx, read.ts); the database function allows no more than 5,000.
19. **internal** (session 83; the owner's instruction of session 83). The table and its seven sister tables are internal: the page is read only in the internal view, offers no download, and a server without the internal token draws no figure and no row.
   - Default: Internal, until a person has read the Commission's own statement of terms.
   - Source: docs/methods/ferc_eqr_contracts.md, "License": ferc.gov answered this project's requests with HTTP 403 on 5 October 2026, which was not worked around.

## 10. What the tool does not hold

- The transactions of the reports: what was delivered and billed.
- Texas: sales inside ERCOT are not filed with the Commission.
- The technology of a contract; a buyer that never appears as a filer's customer; a contract settled in money.
- A corporate family: a parent and its subsidiaries are different names.
- A total of megawatts for the market: most contracts state none.
- A price for the rows that give words: 104,929 rows are left unread, never estimated.
- Any choice a reader can edit: the page counts and lists, and computes nothing a reader sets. Its decisions are the
  nineteen above.

## 11. The replication, and the faults found

`replication/contracts/`: `copy_rows.py` makes what the page is served from the tables on the machine; `replicate.py`
computes every figure again from the two source tables and sets it beside what the page's own code draws
(`site/scripts/contracts-figures.mjs`); `replicate.do` rebuilds seven headline figures in Stata. On 16 November 2026:
2,539 of 2,615 figures inside the tolerance, 76 named (fault 7), none unexplained; 785 of 785 words the same. The
faults are in [`docs/reviews/contracts-faults-2026-11-16.md`](../reviews/contracts-faults-2026-11-16.md).

The price rule, the name rules and the megawatts rule of sections 5 to 7 were completed in this note from the
builders' code before the replication was written: the tables' notes gave their sense and not their exact patterns.
The replication is therefore a second implementation of rules read once, not a second reading of them.

## 12. Since session 7510: what the list also draws

The page was read as the reader it is for on 16 November 2026
([`docs/reviews/contracts-read-2026-11-16.md`](../reviews/contracts-read-2026-11-16.md)). Nothing of sections 1 to 11
changed; the list by quarter signed draws these beside what it drew:

- **The days of a short term.** A term the page draws as under one year (0.9 years or less to its one decimal) also
  gives its days: the days from the commencement date to the termination date, both counted. A strip of one month is
  "0.1 years: 30 days". A term of 1.0 years or more gives no days.
- **A number with no unit.** A rate filed as a number with empty rate units is followed by "(no unit filed)".
- **The priced rows whose number is 0.** The note under "Rows with a price as a number" says how many of the rows
  counted there file the number 0 (a rate that is not empty and reads as a number equal to zero). They stay counted
  among the rows with a price as a number: the filer filed a number.
- **The panel.** A quarter's link and a product's link keep the balancing authority chosen. The authority chosen
  stays in the panel, with its rows, when it is not one of the entries listed (none of its rows in the quarter, or an
  entry past the fourteenth). The rows beside each quarter are every product's, delivered anywhere, and say so on
  hover. The code of one of the seven grids the site names says the grid's name on hover (`site/lib/gridtool.ts`).
- **The address.** A quarter that is named and not listed (a year, a quarter not held) shows the newest quarter
  listed and says so.
- **One row** reads "1 row ... was signed", one agreement "1 agreement".

The replication computes the first three for every page it draws (`terms_in_days_drawn`, `no_unit_marks`,
`priced_zero`); `site/scripts/test-contracts-read.mjs` holds the rest on made-up rows.
On 16 November 2026, with the three: 2,728 of 2,804 figures inside the tolerance, 76 named (fault 7), none
unexplained; 785 of 785 words the same. The 2,615 figures of section 11 are among them, unchanged.
