# The policy monitor's impact reads, against the tables they cite

Energy Research Warehouse (ERW), session 469, 21 October 2026. Every impact read of `/policy` (`policy_reads`, as the
live set served it at 09:45:25 UTC) read for the ERW tables and the figures it cites, with the page's own function
(`site/lib/policyreads.ts`, `citeOf`, run by `site/scripts/audit-policy-reads.mjs`). One row a read is in
[`policy-impact-reads-2026-10-21.csv`](policy-impact-reads-2026-10-21.csv). No request to any publisher, no model.

## The count

**385 reads; 0 cite an ERW table; 255 state figures, every one from the action's own text; 130 state no figure.**

| Agency | Reads | Figures from the action's text | No figure | An ERW table |
|---|---|---|---|---|
| FERC | 153 | 111 | 42 | 0 |
| NRC | 121 | 77 | 44 | 0 |
| DOE | 43 | 25 | 18 | 0 |
| Interior | 19 | 12 | 7 | 0 |
| EPA | 18 | 7 | 11 | 0 |
| BLM | 17 | 11 | 6 | 0 |
| PUCT | 11 | 9 | 2 | 0 |
| CPUC | 2 | 2 | 0 | 0 |
| IRS | 1 | 1 | 0 | 0 |
| **All** | **385** | **255** | **130** | **0** |

The 255 reads with figures state 509 figures between them (a figure counted once a read). The 130 with none are of
significance 5 (65), 6 (42), 7 (15), 8 (4) and 9 (4).

Beside the reads, the actions as the live set held them at 09:57 UTC: 1,926, every one scored; 377 at 5 or more, every
one with a read; 8 reads belong to actions a later recheck scored below 5 (the read is kept and shown).

## The reading

- **No read cites a table, by construction.** `warehouse/policy/reads.py` gives the model the action's own text and
  keeps a field only when every quotation stands in that text word for word and every number in the field stands in
  the text read (`docs/methods/policy_monitor.md`, section 3). A read has no way to cite an ERW table, and none names
  one: `citeOf` looks for any of the 212 table names of `coverage.csv` in the read's words and finds none.
- **So a read's figure is the regulator's or the applicant's, not the ERW's.** The page now says so under each read
  ("Figures: " then the read's own figures, then "Each figure stands in the action's own text ...; no ERW table is
  cited. Source: the action."), and marks a read with no number "No figure: this read states no number."
- **What "a figure" is here.** A number with its unit where one follows. Dates, years, times of day, dockets, order and
  section numbers, parts of the Code of Federal Regulations, numbered things (a lease sale, a compressor station, an
  Energy Emergency Alert level, a unit or reactor) and model names (Xe-100) are not figures. A number written in words
  is not read. The rule is a pattern, and a numbered thing it does not know is counted as a figure: of the 509, a bare
  number with no unit is the case to look at in the CSV.

## What the page does with it (no figure moves)

- Under each read, in the row the reader opens, one line: the figures and their source, or "no figure"
  (`data-read-cites` is `text`, `none` or `table`). Nothing else on the page changes; no figure is computed, so no new
  `check-values` key: the figures are the read's own words, printed in the read above the line.
- The stored text of `policy_reads` is the warehouse's and is not rewritten. A read that cited a table could only do
  so if `reads.py` gave the model a table: that is a change for the data machine (below), not a page's.

## For the data machine (not done tonight)

- If reads should cite ERW tables, `reads.py` would give the model the figures of a named table beside the action's
  text and keep a table figure only when it equals the table's value under a key; every read made again is a model
  call (money), so it waits for a ruling.
- The 8 reads of actions now scored below 5 are kept by the page; whether a recheck that drops an action below 5
  should withdraw its read is a ruling.
