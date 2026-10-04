# Who is buying: buyer names by rule, and the largest buyers and sellers

Three derived tables from `ferc_eqr_contracts` (FERC's Electric Quarterly Reports, the contracts in force as filed for
one quarter), built by `warehouse/derived/eqr_buyers.py`, and a view on `/contracts`: "The largest buyers and
sellers", for energy, capacity and tolling.

**All three are internal,** as their input is (session 83's ruling: FERC's license statement could not be read by the
data machine, so the table is held for internal use). They are in `warehouse/output` and in no file of this
repository. No name of them and no party's figures are written here, in a test, or in a session report: only counts
of names and of rows. The examples below are made up.

| Table | Shape | What a row is |
|---|---|---|
| `ferc_eqr_buyer_names` | entities | one buyer name as filed, the name it is counted under, the rules that changed it, how many names share that one |
| `ferc_eqr_buyer_doubtful` | events | a pair of names that look like one buyer and were **not** merged, with the reason for the doubt |
| `ferc_eqr_party_totals` | entities | a buyer (by its merged name) or a seller (by FERC's company identifier), for one product: contracts in force, rows, counterparties, MW filed |

No model is used and no request is made. Every merge is a rule a person can read, and every merge is a row of the
first table.

## The rules, in order

Two names are one buyer only when all of the rules leave them identical.

| Rule | What it does | Made-up example |
|---|---|---|
| `case_space` | capitals; runs of spaces closed up | "Example  Power Co" and "EXAMPLE POWER CO" |
| `punctuation` | "&" read as AND; periods, commas, apostrophes, quotation marks and brackets taken out; a hyphen or a slash read as a space | "Example Light & Power, Inc." and "Example Light and Power Inc" |
| `leading_the` | a leading "The" taken off | "The Example Edison Company" |
| `abbreviation` | a whole word from a short list written one way: Corporation as Corp, Incorporated as Inc, Company as Co, Limited as Ltd, Coop as Cooperative, Assn and Assoc as Association, Elec as Electric, Dept as Department, Auth as Authority, Mgmt as Management, Svc and Svcs as Service and Services, Intl as International, Natl as National, Pwr as Power, Mktg as Marketing, Transm as Transmission | "Example Elec Coop" and "Example Electric Cooperative" |
| `legal_suffix` | the legal form at the end written one way: L L C as LLC, L P as LP, L L P as LLP, Limited Liability Company as LLC, Limited Partnership as LP, N A as NA | "Example Wind, L.L.C." and "Example Wind LLC" |
| `suffix_left_off` | a name with no legal form at its end, when the same name is also filed with exactly one legal form, is counted with it | "Example Power" with "Example Power Company" |

**Where a rule holds back.** "Co" is left alone as the last word of a name that begins City, Town, Village, County or
Borough, or that holds "of": there it may be Colorado. And `suffix_left_off` does nothing when the same name is filed
with two different legal forms: that pair is doubtful.

**The name a group is shown under** is the spelling filed on the most rows.

## Doubtful, never merged

| Reason | What it is | Made-up example |
|---|---|---|
| `different_legal_form` | the same name with two different legal forms; they may be two companies | "Example Energy LLC" and "Example Energy Inc" |
| `extra_clause` | a name that is another name plus a d/b/a, f/k/a, "as agent for" or bracketed clause | "Example Power Company d/b/a Example Light" and "Example Power Company" |
| `near_spelling` | two names of 12 letters or more that are at least 94 percent alike letter by letter and do not differ by a number | "Example Califormia Edison" and "Example California Edison" |

A project's I and II, or 1 and 2, are two companies and not a doubt; such pairs are not listed. The pairs are sorted by
the rows the two names are filed on, so a person meets the ones that matter first. A person decides each: to accept
one, add the pair to a list the builder reads (not built: there is no accepted pair yet).

## What the rules do not do

- **A parent and its subsidiaries stay apart.** They are different names. "Who is buying" at the level of a corporate
  family needs a table of parents kept by a person.
- **A misspelling stays apart** until a person rules on its pair. So a buyer's count is a floor.
- **Sellers are not merged by name.** A seller is a filer, and FERC gives each filer one company identifier.

## `ferc_eqr_party_totals`

Rows in force (no actual termination date filed) whose product is ENERGY, CAPACITY or TOLLING ENERGY (FERC's names,
compared in capitals).

| Column | Meaning |
|---|---|
| `x_role`, `x_product` | buyer or seller; energy, capacity or tolling |
| `x_rank` | within its role and product, by contracts, then rows, then name |
| `x_contracts` | distinct contracts: a filer's company identifier with its contract identifier |
| `x_rows` | product rows (one agreement files a row per product) |
| `x_counterparties` | for a buyer, the sellers it buys from; for a seller, the buyers after the rules |
| `x_mw_filed`, `x_rows_with_mw` | the sum of the quantities filed in MW, and the rows that file one. Most rows file none, so this is not a total |

**The market operators** stand at the top of the buyers of energy and capacity: a sale into an organized market is
filed with the operator as its customer. They are counterparties of record, not users of the power. The page says so.

**In force, not new.** Every agreement in force is filed again each quarter. What was signed lately is the page's
other view.

## The view, and how it gets its figures

`/contracts?view=largest&product=energy|capacity|tolling` (in review, internal view only). The page reads the stored
summary of the contract table (`internal_eqr_summary`, which answers only with the internal token). The loader puts
the first 25 of each list there with the counts of the name rules (`warehouse/supabase/load.py`, `eqr_largest`), when
it next loads the contract table. Until that load the view says it is not loaded. No migration is needed: the stored
summary is one JSON value.

## Rebuilding

```bash
python warehouse/lock.py run --task "EQR buyers" --minutes 10 -- <python> warehouse/derived/eqr_buyers.py
python warehouse/derived/eqr_buyers.py --out-dir DIR      # a trial: nothing in warehouse/output
```

The three tables are rebuilt whole from the quarter's file each run.

## Checks

`tests/test_session99.py`, on made-up names only: each rule alone and in order; "Co" held back where it may be
Colorado; a name with and without its one legal form merged, with two forms not merged and listed; the three kinds of
doubtful pair, and a project's I and II not listed; the totals on rows made for the test; the loader's summary of the
largest; that no name of the real tables is in any file of the repository; and, where the tables are on the machine,
their counts. `site/scripts/check-contracts-largest.mjs`: the view on the built site against a stand-in for the
database that serves the summary from a file kept out of git (`warehouse/supabase/eqr_fixture.py`).
