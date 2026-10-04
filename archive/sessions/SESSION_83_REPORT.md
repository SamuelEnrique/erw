# Session 83 report: contracts

**Built.** The approved pull ran to the end under its ceiling: 187,527 contract rows from all 4,077 filings of the second quarter of 2026, against a ceiling of 400,000. The internal table `ferc_eqr_contracts` holds 186,873 of them, and the review page `/contracts` lists new contracts by the quarter they were signed, with seller, buyer, product, term, price as filed and delivery point, and session 81's three limits stated at the top. One deploy, with a snapshot before and after: no number on a live page changed.

**Read these four first:**

1. **Most of the record is not power sales.** Energy, capacity and tolling are 35 percent of the rows. The rest are transmission, interconnection and ancillary service agreements, which the same form carries. So "new contracts signed in the second quarter of 2026" is 1,391 rows in all, and **227 rows of energy, capacity and tolling: 174 agreements between 78 sellers and 95 buyers, 112 of them with a price as a number.** The page opens on those.
2. **The second limit is worse in the whole quarter than in the sample.** Session 81's sample said 45 percent of rows give their price as words. With the large filers in, it is 56 percent (104,952 of 186,873). The page says "about half" and prints the count of the rows it holds.
3. **Texas is nearly absent, not absent.** The sample found no row naming ERCOT. The quarter has 244 that name it as the delivery point, 229 of them one utility's transmission and interconnection agreements. The page's words changed from "does not cover Texas" to "hardly covers Texas", with the count.
4. **Eleven rows are left out because their date cannot be held.** Filers typed execution dates in the years 2526, 2706 and 2915. The standard's readers stop at 2262, so the validator blocked the table. Those 11 rows are left out and counted in the header; nothing was corrected. 54 other rows are dated after the quarter (July 2026 to 2223): they are kept as filed, counted on the page, and not listed.

Energy Research Warehouse (ERW), session 83, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 03:05 to 04:20 UTC, unattended. **Model spend: USD 0.00.** One pull, the approved one: 4,039 requests to FERC's report viewer, 3.26 GB over the wire (a filing's contracts cannot be fetched without its transactions, which were dropped unread), 31 minutes. No model call, no force push. The data lock was held 03:17 to 03:48 UTC for the pull, briefly twice more to rebuild the table from the raw files, and 03:50 to 04:00 for coverage, the archive, the upload and the load; released each time.

## To finish

```bash
# Nothing is left half done. What is yours:

# 1. The page cannot be opened on production until the internal token on Vercel is this warehouse's (session 77's step,
#    still open): set INTERNAL_COSTS_TOKEN on Vercel to the value in .env and redeploy. Until then /contracts answers
#    the "in review" page to everyone, and with a wrong token it would say the table is unavailable. I read it on this
#    machine's build, with this machine's token, against the real database: it works (numbers below).

# 2. The license. The table is internal by your instruction. FERC's filings are public, but ferc.gov answers this
#    machine with HTTP 403 and I did not work around it, so FERC's own terms are still unread. If you read them and
#    they allow it: sources.csv, the line of ferc:eqr, license public; then the page needs a public reader.

# 3. A second quarter. The page shows "new" by execution date, and one quarter's filings already hold every contract in
#    force, so one quarter is enough to list signings. A second quarter would show which contracts ended. Not pulled:
#    you approved one. The command, when you do:
python warehouse/lock.py run --task "EQR 2026 Q3" -- python warehouse/connectors/ferc_eqr_contracts.py --quarter 2026_Q3

# 4. Session 82's report is on main now (it rode this session's push). This report is on wip/083-contracts.
```

## In plain words

### The pull

FERC serves a quarter as one zip of 3.6 GB that holds 4,077 small zips, one per filing. The server answers requests for a range of bytes, so the connector reads the list first and then one filing at a time, keeps the contracts file of each, and drops the rest unread. The contact persons in the identification file (names, telephone numbers, email addresses) are never written anywhere.

Session 81 could not say how many contract rows the quarter held: its sample could not reach the large filers. The count ran close to the ceiling for the first thousand filings (104,197 rows, on a pace for about 425,000) and then fell away, because the large filers come first in the file. It ended at 187,527. Had it passed 400,000 the connector would have stopped and written nothing.

| | |
|---|---|
| Filings read | 4,077 of 4,077 |
| Companies | 4,010; 67 earlier filings of a company that refiled are left out |
| Contract rows read | 187,527 |
| Rows in the table | 186,873 |
| Left out | 643 rows of superseded filings; 11 rows whose execution date no table can hold |
| The largest filers, by rows | Tri-State Generation and Transmission 21,660; PJM Interconnection 14,778; Constellation Energy Generation 7,766; Midcontinent ISO 7,534; Western Area Power Administration 6,501 |
| Rows with a rate as a number | 81,718 (43.7 percent) |
| Energy rows priced in USD per MWh | 16,765; median 50.45, the middle half 28.24 to 71.75 |
| Rows with a delivery balancing authority | 46,145: CISO 11,727, ISNE 5,373, PJM 4,647, SOCO 3,404, PACE 3,116 |

The row of superseded filings: 187,527 read, less 11, less 186,873 kept, is 643.

### The table

`ferc_eqr_contracts`, the events shape, internal. One row per product of an agreement, as the seller filed it. The execution date is the event's date; seller and buyer are the parties; a quantity is a number only when its units are MW, a price only when its units are USD per MWh; every other column of FERC's file is kept under its own name. Nothing is filled, corrected or merged: the same buyer spelled three ways is three buyers.

It passed the validator, is in coverage (internal), in the archive, and in the draft of the internal Redivis dataset (186,873 rows, counted there). The license check passes: 15 internal tables, none in the public dataset.

### The page: `/contracts`, in review

"Where power contracts are being struck." At the top, a box with the three limits. Then a panel (the quarter signed, the product, the delivery balancing authority), one sentence, three numbers, and the table: signed, seller, buyer, product, term, quantity, price as filed, delivered. A price given in words is shown in grey as the filer wrote it. The page counts the rows it shows and does no other arithmetic.

What it shows on this machine, read from the live database with this machine's token:

| View | Rows | Agreements | Sellers | Buyers | With a price as a number |
|---|---|---|---|---|---|
| Signed 2026 Q2, energy, capacity and tolling | 227 | 174 | 78 | 95 | 112 |
| Signed 2026 Q2, capacity | 100 | 96 | 44 | 56 | 56 |
| Signed 2026 Q1, every product, delivered in PJM | 87 | 55 | 14 | 30 | 53 |

The live set holds the rows signed in the last 1,000 days: 19,009. They are internal, so the public key reads none of them: I asked with it and got zero rows of the table, zero catalogue rows and zero header lines for it, and "not authorized" from both functions without the token. With the token the two functions answer. The public key counts 97 catalogue rows after the load, and the home page's catalogue numbers are not among the differences below.

### The deploy, and every difference

One push, `task/083-contracts`; the checks passed (run 37176098686: tests, site build, the route check) and the workflow merged it into `main` as `71e38f5`. Snapshots of the 20 live pages before (03:58 UTC) and after (04:13 UTC): 4,098 checked numbers each time.

**60 differences in all, none of them a number this session changed:**

| Where | Differences | What |
|---|---|---|
| All 20 pages | 20 | The menu gains one greyed item: "Power contracts in review" |
| `/` | 34 | The six latest real-time prices and their lines of text moved on by an hour: the site's 15-minute refresh between the two snapshots (12 number keys, 22 lines of text) |
| `/network` | 6 | Its hourly refresh: "refreshed 2026-10-04 03:05 UTC" became "04:05", and the newest hour of demand moved on by one |

The home page's four catalogue numbers (public tables, rows, last refresh, tables passing) are not among the differences.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session83.py` | 16 tests pass: the shaping on made-up filings (nothing filled, a company read from its newest filing, an undated or unholdable date left out and counted, no column naming a person, the ceiling cannot be raised), the table, the live set and the migration (no table opened, only two functions that check the token), the page's model run by node, the three limits on the page |
| The whole suite, here | 515 tests: the new ones pass. One old failure remains, known since session 82: `test_session49` (`eia930_all_interchange` holds 151,632 rows against a ceiling of 150,000 on data machines; it skips on the runner). The tests of sessions 85 and 88, written while the pull ran, were not part of this commit |
| The suite on the runner | passed (run 37176098686) |
| Validator | pass, exit 0, after the 11 rows were left out (exit 1 before) |
| Coverage | exit 0: 112 tables, one new line |
| Archive | exit 0: 186,873 rows of the new table |
| Redivis upload by name, and the license check | exit 0 both; the count in the draft equals the file's |
| Migration 020, alone | applied |
| Load, `--only` the table | exit 0: 19,009 rows written, counted equal |
| Site: types, build, route check on this machine | exit 0 each; `/contracts` answers 200 in the internal view and the in-review page to a visitor |

## Errors and decisions

- **The validator blocked the first write** (11 dates that are not dates to any reader). I changed the connector to leave such rows out and count them, set the first file aside under `runs/session83/` and rebuilt the table from the raw contract files, with two requests and no new pull of filings.
- **pandas cuts a row at a "#"** when told that "#" starts a comment, and a utility district is named "... District #1". My first look at the table read 54 rows with half their columns empty. The table was right; my reading was wrong. The warehouse's own readers skip the header by count and are not affected. The session's test reads the same way now.
- **A test of session 70 pinned "the newest migration is 019"** to say the game's rules are still version 4. Migration 020 broke it. It now looks at the game's own migrations.
- **`build_coverage.py` failed once**, loudly, as it is meant to: a new table needs a sector on purpose. `ferc_eqr_contracts` is `power`.
- **Decision: the live set holds 1,000 days of execution dates, not the whole table.** The page is about new contracts; 186,873 rows would be a quarter of the database for a page that lists a few hundred. The loader has a new option for it (`event_days`).
- **Decision: rows dated after the quarter are counted on the page and not listed.** Listing them would have made "2223 Q1" the newest quarter in the panel.
- **While the pull ran** I prepared sessions 85, 86, 87 and 88 (connectors and trial runs into a scratch directory, tests, the calculator page). None of that is in this session's commit.

## For Samuel

1. **The Vercel token** (To finish, 1). Every page in review waits behind it.
2. **Is a quarter enough, and is the page's default right?** It opens on energy, capacity and tolling. If you want the interconnection and transmission agreements as the lead, it is one word in `site/lib/contracts.ts`.
3. **Names.** 17,955 buyers as filed. A credit investor will want "who is buying" by company, which needs names merged. That is a matching problem with a person in it, and I did not start it.
