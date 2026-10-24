# Session 2361 report: seven held tables named in their family notes

24 October 2026, from 08:35 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0. Pulls: none.

## Read these first

- **The finder** (`runs/c110/s2361/find_unnoted.py`, session 2298's pointed at this worktree, main and chains 108's and 109's branches) lists 49 tables with no `Tables:` line or note named for them. The source tables among them:
  - six FERC EQR tables;
  - this chain's two, which session 2366 describes, and chain 105's Eurostat capacity table.
- **The FERC EQR tables were already described**, in two family notes under other names, as chain 108's agent also found (session 2326):
  - `eqr_buyers.md` describes `ferc_eqr_buyer_names`, `ferc_eqr_buyer_doubtful` and `ferc_eqr_party_totals`;
  - `eqr_terms.md` describes `ferc_eqr_contracts_history`, `ferc_eqr_contract_terms`, `ferc_eqr_party_mw` and `ferc_eqr_quarter_changes`.

  The finder misses them because it reads only `Tables:` lines and file names.
- **The changes to the two notes:**
  - a `Tables:` line in each, naming its tables;
  - a checks section in each, with counts only (the tables are internal: no party's name or figure is written);
  - the Method cells of the seven tables link them.
- **The counts** (`runs/c110/s2361/check_eqr.py`):
  - **`ferc_eqr_buyer_names`:** 17,955 rows.
  - **`ferc_eqr_buyer_doubtful`:** 1,281 pairs (near spelling 687, an extra clause 349, a different legal form 245).
  - **`ferc_eqr_party_totals`:** 12,290 rows.
  - **`ferc_eqr_contracts_history`:** 571,115 rows, three quarters, no event id twice.
  - **`ferc_eqr_contract_terms`:** 186,873 rows, one for each row of `ferc_eqr_contracts`.
  - **`ferc_eqr_party_mw`:** 812 rows.
  - **`ferc_eqr_quarter_changes`:** 68 rows, 2025 Q3 to 2026 Q2.
  - Every shape is as the notes' tables of tables give it.
- **One point corrected.** `eqr_terms.md` gave the pull's rows read, 574,005, as if they were the table. The table holds 571,115 (190,816, 190,249 and 190,050 by quarter): each quarter's earlier filings of a company, and the rows whose execution date the standard cannot hold, are left out, as each run's header counts them. The note now says both.

## Errors

- None.

## Decisions made without you

- **`Tables:` lines added to the family notes,** rather than seven new notes repeating them.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `docs/methods/eqr_buyers.md`, `docs/methods/eqr_terms.md`, `docs/coverage.md` (seven Method cells).
- On the data machine only: `runs/c110/s2361/`.
