# Session 8201 report (chain 502, lab-desktop second window)

19 November 2026, 10:40 to 11:15 UTC. Opus 5.5. Model spend: USD 0 (no model called). Parts B and C checked at the start: both still waiting.

## Family 1, who trades with whom: 34 drafts

- `docs/findings/trade/` (6349e6206), each with its chart, yearly CSV, `reproduce.py` and `reproduce.do`; loaded to `public.scanner_drafts` in state draft, then corrected in place to name chain 502 and its plan (34 of 34 patched while still drafts).
- Second pass: `deep/check.py --family trade` 34 of 34 reproduce from their own scripts in a clean folder; `check_do.py` 34 of 34 do-files hold.
- Nine candidates, 196 claims, 76 pass all five tests; kept by consequence and size: 8 region-pair flows, 5 regions' net trade over demand, 8 ties between authorities, 4 hours-against-direction measures, 2 regions' hours trading the other way, 3 region-pair report gaps, 4 tie report gaps.
- The three strongest:
  - Canada to New York: mean hourly flow 211 MW in 2025 against 1,992 MW in 2019 (5.2 typical yearly moves).
  - Canada to New England: 432 MW in 2025 against 1,945 MW in 2019; the share of hours it ran the other way, 29.5 percent against 0.0.
  - New England's net imports: 7.1 percent of its demand in 2025 against 19.2 percent in 2019.
- Left out by the two-sides rule (the sides moved apart): the Mid-Atlantic's pairs with the Midwest, New York and Tennessee, the Midwest and the Southeast, and 13 ties (MISO and PJM: PJM's side moved by 288 MW, MISO's by minus 6,681 MW). The Midwest, the Northwest and the Southwest's net trade were left out because their total interchange and their border flows disagree.

## Code (for the desk: landing row 1, `wip/8201-findings` at `84d106e33`)

- `warehouse/analysis/findings/deep/hourly930.py`: readers of the 17 November EIA-930 tables, the fault rules, region demand summed from the authorities.
- `warehouse/analysis/findings/deep/trade.py`: the nine candidates and their reproductions.
- `builder.py`: the chain number and plan settable (default 164 unchanged). `check_do.py`: a Stata loop is one block; a folder may be named.
- `tests/test_session8201.py`; the 36 test files that load the findings code: 297 passed, 5 skipped.

## Decisions made without you

- A region's net trade for a region of more than three authorities is drafted only when its border flows by the pair table moved the same way; the Southwest's total interchange showed 54 percent of demand in 2019 because Arizona Public Service and the Salt River Project reported their tie 3,004 MW apart.
- One story is drafted once (the folds listed in `trade.py`, `SKIP`).

## For Samuel's ruling

- None new.

## Needs the key

- Nothing.
