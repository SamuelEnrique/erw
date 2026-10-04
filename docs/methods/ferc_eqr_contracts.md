# FERC Electric Quarterly Report contracts: method

Built in session 83 for the review page `/contracts` ("Where power contracts are being struck"), after the scope of session 81 (`archive/sessions/SESSION_81_REPORT.md`). One table:

| Table | Tier | License | What |
|---|---|---|---|
| `ferc_eqr_contracts` | source | internal | The contracts in force that sellers of wholesale power filed with FERC for one quarter: one row per product of an agreement, as filed |

Code: `warehouse/connectors/ferc_eqr_contracts.py`. The page reads the table through two database functions that answer only with the internal token (`warehouse/supabase/migrations/020_eqr_contracts.sql`).

## What the record is

Public utilities, and other sellers with more than a small presence in the market, file an Electric Quarterly Report (EQR) with the Federal Energy Regulatory Commission every quarter. A filing has two parts that matter here: the contractual terms of the seller's agreements (contracts), and what was delivered and billed in the quarter (transactions). **This table holds the contracts only.** The transactions are far more rows (session 81 estimated about 115 million a quarter, from a sample) and were not parsed.

A contract row names the seller, the buyer, whether they are affiliates, the product, the class and term, the dates of execution, commencement and termination, a quantity, a rate or a description of one, and the points of receipt and delivery.

## The pull

- **Source:** FERC's EQR report viewer, `https://eqrreportviewer.ferc.gov/` (Downloads, Quarterly Filings, All Companies). One zip per quarter, `CSV_<year>_Q<q>.zip`. For the second quarter of 2026 it is 3,601,874,263 bytes and holds 4,077 small zips, one per filing.
- **A filing at a time.** The server answers range requests. The connector reads the list of the quarter's filings first, then asks for one filing's bytes at a time, and from each filing reads the contracts file and three columns of the identification file (the filer's company identifier, name and quarter). Fetching a filing means fetching its transactions too, because they are in the same zip: 3.26 GB went over the wire for a table of 113 MB. The transactions are dropped unread.
- **What is kept on disk:** each filing's contracts file as FERC served it, under `warehouse/raw/ferc_eqr_contracts/2026_Q2/`, with an index. Nothing else of a filing. **The filers' contact persons (names, telephone numbers, email addresses, in the identification file) are never written to a row or a raw file.**
- **Ceiling:** 400,000 contract rows (the approval of session 83). The quarter held 187,527. Had it passed the ceiling the run would have stopped and written nothing.
- **Cost:** USD 0. 4,039 requests, about 31 minutes.

## What is in the table

| | |
|---|---|
| Rows | 186,873 |
| Filings read | 4,077, of 4,010 companies; 67 earlier filings of a company that refiled were left out (the newest is the company's) |
| Rows left out | 11, for an execution date no table can hold (see below); none for a date that could not be read |
| Sellers named | 3,161; buyers named 17,955 (names as filed, never merged) |
| Products | ENERGY 48,195; OTHER 36,995; INTERCONNECTION AGREEMENT 18,616; CAPACITY 18,079; POINT-TO-POINT AGREEMENT 9,678; then reserves and other transmission services |
| Rows with a rate as a number | 81,718 (43.7 percent); 104,952 give words only; 203 give neither |
| Rows with a delivery balancing authority | 46,145; 140,728 leave it empty |
| Affiliate contracts | 11,346 |
| Terminated | 8,031 carry an actual termination date; 178,842 are in force |
| Executed in the second quarter of 2026 | 1,391 rows, of which 227 are energy, capacity or tolling |

The standard columns (`docs/datastandard.md`, the events shape):

| Column | What |
|---|---|
| `event_id` | `ferc_eqr:<quarter>:<company identifier>:<FERC contract id>:<n>`. FERC's contract id repeats across the products of one contract, so `n` is the row's place among them |
| `event_date` | The contract's execution date |
| `event_type` | `contract` |
| `parties` | Seller, then buyer, as filed |
| `mw` | The quantity, only when its units are MW (12,169 rows) |
| `price`, `currency` | The rate, only when its units are `$/MWH` (36,905 rows), in USD |
| `status` | `terminated` when an actual termination date is filed, else `in_force` |
| `x_*` | Every other column of FERC's contract file under its own name, and `x_company_id`, `x_filing`, `x_quarter` |

Nothing is filled, corrected or merged. A rate in other units stays in `x_rate` with `x_rate_units`; a price given in words stays in `x_rate_description`.

## Three limits (session 81), and what the full quarter adds

1. **No column says what technology a contract is for.** Solar, wind or storage can be read only from a seller's name.
2. **More than half the rows give their price as words.** In the sample of session 81 it was 45 percent (2,961 of 6,508); in the whole quarter it is 56 percent (104,952 of 186,873). The large filers the sample could not reach price by tariff more often.
3. **Every agreement in force is filed again each quarter.** A contract is new because its execution date is recent, not because it is in this file. 25,126 rows were executed before 2000.

And three things the sample did not show:

- **Texas is nearly absent, not absent.** 244 rows name ERCOT (`ERCO`) as the delivery balancing authority, 229 of them one utility's transmission and interconnection agreements. Sales inside ERCOT are outside FERC's jurisdiction; the sample found none.
- **Most rows are not power sales.** Energy, capacity and tolling energy are 35 percent of the rows; the rest are transmission, interconnection, ancillary and "other" service agreements, which the same form carries. The page opens on energy, capacity and tolling.
- **Some execution dates are wrong at the source.** 54 rows are dated after the quarter they were filed for: 46 between July 2026 and January 2027 (signed after the quarter closed, or mistyped), 7 in 2101 and 1 in 2223. They are kept as filed; the page counts them and does not list them. 11 more are dated 2526, 2706 and 2915: no table can hold those as dates (the standard's readers stop at 2262), so those rows are left out and counted in the header.

## The live set and the page

The live set holds the rows executed in the last 1,000 days (`live_set.yaml`, `event_days: 1000`): 19,009 rows on 2026-10-04. Row-level security hides them from the public key, as it hides every internal table; the page reads them through `internal_eqr_contracts` and `internal_eqr_summary`, which answer only with the internal token. Since session 90 the summary (the counts by month, product and balancing authority) is computed once by the loader, from the rows it loads, and stored (`load.py` `eqr_summary`, migration 021); the page's function reads that one row. Before that it counted the table on every request, which took 4.8 seconds against the public key's limit of 3, and production cancelled it. The page is in review and stays behind the internal view while the table is internal.

## License

Internal. The filings are public: FERC publishes them to make the data available to the public (its notice of 17 February 2026, 91 FR 7279). But FERC's own statement of terms on `ferc.gov` could not be read by this machine (the site answers automated requests with HTTP 403, which was not worked around), and the instruction of session 83 is an internal table. A person who reads FERC's terms can open it.
