# Sessions 1059 and 1060 report: the method notes, and the open items in one place

23 October 2026, about 08:10 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, sessions 1059 and 1060. Model spend USD 0. No request; no build of their own.

## Session 1059

- **`docs/methods/siting.md` version 7**, "What version 7 changed": a node's county and zone and its county's projects (1048, decision 31); the other grids' reserve margins named, not drawn (1047, decision 30); the county map designed (1049); the tables not landed (1046).
- **`docs/methods/packages.md` version 2**, "What version 2 changed": three new sentences in the three packages (1056); the conformance file's version 2 (1055); the new tables read (1053); the owner's run and the two rulings not yet (1054, 1058).
- **`docs/reviews/siting-gaps.md`**, "State on 23 October 2026, day (chain 072)": two rows changed (a node's county, filled for 569 nodes; projects by county, filled for a placed node's county); reserve margins for the other grids now wait on a ruling. The table's rows are as written, so `gaps.json` is unchanged (checked: the builder's `gaps_file` gives the same rows).

## Session 1060

- **`docs/reviews/siting-open-2026-10-23.md`**, "State after chain 072": lines 11 and 12 closed in part (1048), 20 closed for ERCOT with the rest on a ruling (1047), 21 designed (1049), 33 proposed (1061). 4 closed, 3 closed in part, 26 open.
- **`docs/reviews/siting-rulings-2026-10-23.md`**: two items added, **23** (EIA-411's 2016 projections: draw, or not, or read NERC instead; recommendation: not, and the new source) and **24** (the county map; recommendation: yes); its state section: none of 1 to 24 ruled.
- **`docs/reviews/packages-open.md`**: item 10 closed by 1055; items 1 to 9 unanswered; item 11 (`ferc_eqr_contracts_history`'s partition test) not read by this chain; item 12 joined by chain 049's tables.

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

1. **The two new rulings items are written with a recommendation each**, as the file's other items are.
2. **packages-open item 11 left open**: reading the data machine's current file needs the table rebuilt from the archive (a large table), outside this session's hour.

## For Samuel's ruling

- Rulings items 23 and 24 (above).
