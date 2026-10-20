# Session 378 report: the licensing sweep to the point of Samuel's signature

20 October 2026, from 18:25 UTC, unattended, on lab-desktop (the data machine), the sixth session of the chain of 20 October, day, done while the daily run held the data lock (it needs none: no data was written). Model spend USD 0. Pulls: none (0 of the ceiling of 2 requests a publisher; below).

## Read these first

- **Every table of `coverage.csv` has one verdict word in `docs/licenses.md`** ("Every table", the last column, "ERW verdict"): **129 public, 33 internal, 47 unsettled** of 209. Public: flagged public and every publisher's sentence read allows it as the ERW is today. Internal: flagged internal. Unsettled: a "license needed" ruling waiting for its permission (41), or a publisher not read on a table flagged public (6: `large_load_public`, `large_load_rule_reads`, `large_load_rules`, `policy_action_tags`, `policy_actions`, `policy_reads`; the other 13 not read are flagged internal), or a flag and a verdict that disagree (0 now). Where a verdict needs a document not held, the table's "Not read" cell names the publisher, and the table stays as flagged.
- **No flag in `coverage.csv` was changed.** No table is flagged internal where a quoted term makes it public, once one is read rightly: `ercot_node_prices_hourly` (session 358) read so at first, but it is internal by the owner's rule for the hourly table (its header), so it is recorded as ruled (`RULED_INTERNAL`), not as a disagreement. Moving it to public would be a reading against a ruling: not done.
- **The five tables of the night chain have their publishers** in `warehouse/metadata/license_tables.csv` (`ercot_4cp_intervals`, `node_basis_daily`, `node_basis_summary` and `ercot_node_prices_hourly`: ERCOT; `price_years_by_window`: CAISO, EIA, ERCOT, NOAA NCEI, SPP). The third machine's three tables (`nlr_jedi_multipliers`, `impact_tax_rules`, `iso_queue_statistics`) bring their own rows with `wip/348-map`; `docs/licenses.md` is written again when that branch is on main (session 380's landing).
- **Four letters, drafts in Samuel's name, not sent:** `docs/reviews/licenses/nyiso-permission-letter.md`, `spp-permission-letter.md`, `pjm-permission-letter.md`, `miso-permission-letter.md`. Each quotes the sentence that makes it needed, names every table it covers, and the use asked (read by script at the publisher's rate; publish the values and figures computed from them with credit; the Redivis archive; a struck-out line for a commercial use). SPP's is needed only if the ERW sells anything; MISO's also asks to resume automated access (MISO is paused, and nothing was asked of it).
- **The prices, for the letter of intent:** a table closes `docs/licenses.md` ("The publishers' prices"): no page read states a figure. PJM names membership ("Member or Associate Member status") without a price; NGI names a data feed or a corporate license without a price. A price has to be asked for: each letter asks it.

## What to review

1. `docs/licenses.md`: "Read these first", the last column of "Every table", and the last section.
2. The four letters under `docs/reviews/licenses/`: the brackets to fill (surname, role, address; NYISO's, PJM's and MISO's contacts are not named on their pages).

## Pulls against their ceilings

| Publisher | Ceiling | Used | Why none |
|---|---|---|---|
| NYISO | 2 | 0 | its legal notice is in the record (read 5) and saved under `warehouse/raw/nyiso_load_queue/` |
| SPP | 2 | 0 | its terms are in the record (read 6), with its contact |
| PJM | 2 | 0 | its agreement is in the record (read 15) |
| MISO | 0 (paused) | 0 | not asked: paused since 4 October |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/licenses.py check` before | 1 | 5 tables not in `license_tables.csv` (the night chain's) |
| `scripts/licenses.py write`, then `check` | 0, 0 | 209 tables, 66 publishers with a verdict, 0 problems |
| `tests.test_session205`, `207`, `248`, `324` | 0 | the first run failed `test_session207` (it pins the table's columns): the new column went last |
| `tests.test_session378` (5 tests) | 0 | |

## Decisions made without you

1. **"Unsettled" covers the 41 "license needed" tables** as well as the 19 not read: each waits for a permission or a read before it can be public.
2. **`ercot_node_prices_hourly` is ruled internal**, by its own header's rule, not listed as a disagreement.
3. **No request was made**: the four pages are in the record; a second read would add nothing the letters need.

## For Samuel's ruling

- The four letters: send, change or hold. SPP's only matters if the ERW sells anything.
- Whether a commercial line goes into the NYISO, PJM and MISO letters (it is in brackets, to strike).

## Files

- New: `docs/reviews/licenses/` (four letters), `tests/test_session378.py`, this report.
- Changed: `scripts/licenses.py` (the verdict word, the ruled table, the hourly table's publisher, the prices section), `warehouse/metadata/license_tables.csv`, `docs/licenses.md`.
