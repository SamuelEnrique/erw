# Session 10222 report (chain 710, part D: the supply page audited)

26 November 2026, the old laptop, worktree `erw-c710-c`, branch `wip/audit-supply-doc`. Model spend USD 0. No table written, no lock taken, no live service asked, no web read, no default on main changed.

## What was done

- `docs/reviews/supply-model-audit-2026-11-26.md` and its evidence folder: `/supply` audited as a utility planner or a fund analyst would.
- The default view restated by scripts that import no site or warehouse code: 618 of 623 printed cells equal to the digit (the five others: percents of three series under 0.4 Bcf/d, which the file's four-decimal copy cannot settle); headline cards and the eight surprises equal; the burn rows re-done from EIA-930's workbooks hour by hour (637 of 637 weeks, every year, five-year and surprise figure equal). The whole-country section's replication on the files now on main: 45,313 of 45,313.
- Five findings; six branches and one merged branch, all pushed (the table in the audit).

## Findings

- 1, Moderate: California's gas burn (and the seven grids' total) compared across EIA-930 to CAISO's own (16 December 2025); EIA ran 30.5 and 47.3 percent above CAISO's own in 2024 and 2025. On the year -22.8 printed, +0.8 like for like; the total +3.49 printed, +6.46.
- 2, Minor: NYISO's and ISO-NE's held cleared rows read "licensed source needed".
- 3, Moderate: "normal for the season" is a five-year average, not the season for a trend (production) or a change of level (New York's and SPP's oil burn).
- 4, Minor: the Outlook's regional months labelled "history only"; they move up to 3.94 percent a month.
- 5, Minor: storage regions share a name with the electricity regions below.

## Decisions made without you

- The pin of session 8430 (`site/scripts/pins/supply-page-8430.json`) is rewritten on each words branch from that branch's code, since any words change outside the whole-country section moves it; each rewrite was checked to move no address's count of checked figures, and the default view was drawn before and after.
- The production rows' source words were changed in the builder, so they reach the page at the next build of `site/data/supply.json`; the committed file was not edited by hand.
- The held-row fix keys on the builder's note saying "held", so PJM's row (not held at all) keeps "licensed source needed".
- California's EIA side was restated before the join only; the gap months of 2019 and 2020 were not restated (in no default figure).

## For Samuel's ruling

- California's gas burn on CAISO's own supply throughout (`wip/audit-supply-2`): moves California on the year from -22.8 to +0.8 percent, its five-year average from 1.89 to 1.73 Bcf/d, the seven grids' total on the year from +3.49 to +6.46 percent. Default: left as it is.

## Needs the key

- Nothing. The Ask panel was not run.

## Problems

- `tests/test_session8430_supply_regions.py::ThePageDrawn::test_the_whole_country_section` fails on a clean origin/main on this machine; not this session's.
- One push of `wip/audit-supply-words` was refused by the remote without a reason and went through on the second try.
