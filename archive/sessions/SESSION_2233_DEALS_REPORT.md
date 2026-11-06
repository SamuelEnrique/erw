# Session 2233 (chain 156, deals and datacenters) report: deduplication

6 November 2026, about 07:52 to 08:03 UTC, portable-laptop (code role), unattended. Worktree `erw-2233` on `wip/2233-deals`, cut from `wip/2232-deals`. Model spend **USD 0** (the fixture's model is a fake: the rules are code). Nothing deployed; no warehouse data written.

- **`warehouse/deals/dedupe.py`** (new): one record a deal. Session 531's rule plus four: one party named on one side with a size agreeing; a name and its initials; a later stage within a year; the size within tolerance (USD a quarter, MW a tenth). `merge` adds the story, keeps the earliest first-reported date, moves `stage` and `status` forward and writes every change to the new column **`status_history`**, fills gaps and never replaces a figure held.
- **`warehouse/deals/extract.py`**: every deal the model does not mark `same_as` is matched by `dedupe.find_record` (a superset of session 531's `find_same`); every merge, the model's or the code's, goes through `dedupe.merge`; a new record starts its history with its first stage.
- **`tests/test_session2233_deals.py`** (11 tests): twelve stored stories about four deals over three runs make four records; the history, the closing a month later, the one-party loan, the initials; the negative cases (another sum, one party without a size, the same stage a year later). `tests/test_session531.py`'s "as it was" test now also switches off the new matcher, so it still shows what the extraction did before session 531.
- **The register**: the audit's two open pairs folded (`warehouse/deals/duplicates.csv`; the Vistra loan, Amazon and Constellation), `site/data/deal_duplicates.json` rebuilt (5 folded, 3 doubtful; 524 deals of 529 rows). The new rules over the stored 529 rows find exactly those two pairs.
- **Tests**: 2233, 2232, 531, 113, 465, 466, 239: 100 passed, 2 skipped.

## Decisions made without you

1. **The two audit pairs folded in the register** by this session (session 113 wrote the register's first rows the same way); the reasons quote the stories. Both were named by the Roundup audit of 21 October as one deal each.
2. **A year for a later stage**: an acquisition or a loan closes months after it is signed; the same stage a year apart stays two deals.
3. **One party is enough only with a size both state that agrees**: one lender with many borrowers (the DOE) would otherwise fold unrelated loans.
4. **`status` moves forward too**, not only the new `stage`: the Roundup prints `status`, and a deal that closed should read closed. An earlier stage never replaces a later one.

## For Samuel's ruling

- None new.
