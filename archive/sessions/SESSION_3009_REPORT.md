# Session 3009 report: queues, and a fault of the shared table reader

6 November 2026, about 12:03 to 12:20 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **A fault in `findings_common.read_table`, used by every finding, the weekly hunt and this chain:** it read CSVs with `comment="#"`, which cuts every line at its first `#`.
  - In Berkeley Lab's queue (`lbnl_interconnection_queue`), 1,581 rows hold a `#` in a field (project names such as "Solar #2"), and they lost their later columns.
  - It now skips only the leading `#` header lines (`header_lines`).
  - Found because this chain's reproduction scripts, which skip only the header, disagreed with the module: 77,929 MW of gas requested in 2024 against the module's 74,070.
  - The findings tests (sessions 103 to 538, 17 files) and this chain's: 341 passed, 12 skipped.
- **The site's `queue_divorce` card read the same cut rows.** Computed again on the fixed reader into a scratch folder (nothing written to `site/`), 14 of its 19 numbers differ:
  - projects: 21,758, against 22,348
  - requested: 3,509 GW, against 3,591
  - the best technology's withdrawn share: 51.5 percent, against 53.2
  - operating: 453.9 GW, against 460.6

  The committed card (`site/data/findings/queue_divorce.json`) is not changed; see "For Samuel's ruling".
- **10 queue drafts on the review list** (module `deep.queues_deals_datacenters`), loaded on the cut rows, then corrected in place on the fixed reader (same ids, still drafts):
  - **The wait:** the median months from request to operation for projects that came online in 2024 was 62.8 in the US, against 17.6 for 2005's. In PJM it was 70.3, against 15.0.
  - **What was asked for** (US, requests by queue year): batteries 157,429 MW in 2024, against 0 in 2005. Solar 116,527 MW, against 1,250. Gas 77,929 MW, against 28,602.
  - **Batteries' share of requested MW:** 29.7 percent in 2024, against 0 in 2005.
  - **Solar requests that also list a battery:** 37.0 percent of solar MW requested in the US in 2024. In the Southeast, 13.6 percent, against 0 in 2009.
  - **Withdrawn rather than built:** 88.7 percent of the MW leaving the queue in 2024 (US), against 65.8 in 2005. PJM: 93.4, against 72.1.
- **A draft can now be corrected in place:** `builder.run(..., replace=True)` (the modules' `--replace`).
  - It rebuilds a claim under the id of its open draft and updates that row, only while its state is still `draft`, never a row you acted on. This is the hunt's own pattern (`fix_source_lines` patches rows the same way).
  - Session 3007's draft on new batteries' hours now starts at 2015 (0.53 MWh per MW) instead of 2011.
  - The build-out and queue drafts now say "the first year this measure counts" where their first year is chosen, not the first the ERW holds.

## What it did

- **`deep/queues.py`:** five candidates on Queued Up (CC BY 4.0). Two candidates on the ISOs' own snapshots were removed before loading: ERCOT's MW entered, from 162 MW in 2013, and its months to in-service. A snapshot drops withdrawn requests, so its early years are undercounted, and a finding the data cannot support is not drafted.
- **A withdrawn share now needs both exits held in its year:** ERCOT lists no withdrawal dates before 2013, so its 2012 showed 0 percent withdrawn.
- **`deep/builder.py`:** `max_per` (a candidate may keep three regions: solar, batteries and gas requests), `replace`, `open_rows`, `patch_rows`.
- **Tests:** `tests/test_session3009.py` (3 tests: the reader with `#` in a field, the queue scripts against the module on a table whose names hold `#`, the correction under its own id). With sessions 3001 and 3007: 11 passed.

## Decisions made without you

- **The reader is fixed on this chain's branch.** It reaches main when chain 164 lands (session 3023); nothing of it is on main before.
- **Corrections update the rows in place** rather than adding new drafts beside the old ones, so the review list never holds two figures for one claim.

## For Samuel's ruling

- **The `queue_divorce` card on the site understates Queued Up by 590 projects.** When the fixed reader is on main, should the card be computed again (its figures move: 14 of 19), or kept until you review it?
