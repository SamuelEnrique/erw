# Session 10212 report: the storage page audited as a hostile expert would

Chain 710, part D, 26 November 2026, the old laptop, worktree `erw-c710-b`. Model spend USD 0. No table written, no lock taken, no live service asked, no default moved.

## What was done

- `docs/reviews/storage-model-audit-2026-11-26.md` and its evidence folder: the ground, the default view restated, one rule changed at a time, each claim against the code, an expert's own number, seven findings.
- **The arithmetic is right.** The fleet tab (default view): 97 of 97 marked figures and 9 words-level figures (180 sparkline values) to the digit, restated from EIA-860M and the hourly series without the site's or the builders' code. The build-out tab: 629 of 629 on three views.
- The page drawn with the site's own code from tables rebuilt by the page's own builders in a trial folder under `runs/` (inputs read only from the main copy; "now" 5 November 2026 12:00 UTC, the newest hour held).
- Seven branches, one a finding, and `wip/audit-storage-words` (the six words branches merged, conflicts resolved), each pushed.

## Findings

| # | Severity | Finding | Branch | Kind |
|---|---|---|---|---|
| 1 | Major | "US Lower 48" leaves out CAISO, NYISO and PJM (32.4 percent of operating MW; CAISO alone 88 percent of the Lower 48's 30-day discharge) | `wip/audit-storage-1` `db93006e1` | words |
| 2 | Moderate | "Latest complete local day" is the day settled 48 hours (two complete days held back); CAISO's row has no wait; the charts draw unsettled hours | `wip/audit-storage-2` `2c6ea7ad6` | words |
| 3 | Moderate | ISO-NE's and SPP's series carry no charging; the decision, hover and charts read them as net | `wip/audit-storage-3` `aabbcbaba` | words |
| 4 | Minor | Build-out's early years "slightly understated": 2015 lacks 31 percent, 2019 10 | `wip/audit-storage-4` `3db505ba8` | words |
| 5 | Minor | Build-out's history leaves out batteries retired before 2025 (full list held) | `wip/audit-storage-5` `10a105cff` | figure, ruling |
| 6 | Minor | "Operating" counts 508 MW standby or out of service; "Retired" is two years only | `wip/audit-storage-6` `de9938cee` | words |
| 7 | Minor | "Storage against solar" says batteries could carry the solar fleet; their power is 3 to 66 percent of solar's | `wip/audit-storage-7` `132daefed` | words |

## Decisions made without you

- The default view was drawn from the main copy's inputs rebuilt by the page's own builders in a trial folder (the main copy's derived tables were older than their inputs: `storage_capacity` August, the cycle to 7 October). The hourly and 5-minute inputs were cut to a year from 1 November 2025, within this machine's read budget; no day the page shows is affected.
- Branches 1, 2, 3 and 6 conflict with each other in `page.tsx` (constants beside `ISOS`, two chart notes); a merged branch `wip/audit-storage-words` was made so the desk can land them in one go. Each branch stays whole on its own.
- Finding 4's words carry two measured shares ("about a tenth", "nearly a third") from EIA's August 2026 list of retired generators; they describe history and move only if EIA revises it.
- "Share of the evening peak", asked about in the brief, is on no tab: said so, no finding.

## For Samuel's ruling

- **Finding 5:** read `eia860m_retired_generators_all` in the build-out so batteries retired before 2025 count in the years they operated? Effect, United States year ends: 2015 250.2 MW becomes 362.9 (+45.0 percent), 2016 +27.2, 2017 +19.7, 2018 +13.9, 2019 +11.1, 2020 +6.7, 2021 +1.9, 2022 +0.4, 2023 +0.2, 2024 and after unchanged. Default: left as it is.

## Needs the key

- Nothing.

## Rows returned to the desk (not written here)

- Landing, words: `wip/audit-storage-words` `2931844e2` (or 1, 2, 3, 4, 6, 7 alone).
- Data request (a): the size of EIA's revisions to its newest BAT hours (first-posted against 72 hours later, raw pages of three daily runs, ERCO, ISNE, MISO, SWPP, US48, 30 days).
- Data request (b): EIA-930's other storage fuel types (solar and wind with storage, other) for ERCO, ISNE, MISO and SWPP over 30 days, beside each one's BAT discharge.

## Problems

- One stray `python.exe -c ""` (an empty inline call, run by mistake inside a longer command while checking finding 1's drawing; it ran nothing) broke the rule against inline code. No other inline code, no heredoc.
- The merge commits of `wip/audit-storage-words` carry git's default messages, not "Session 10212:".
- Failing on a clean origin/main as well, not caused here: `test_session148.py`'s node test (Ask speed), `test_session7202_key_refusal.py` and `test_session7203_allgrids_read.py` (run with the spend cap at 0; not looked into), `site/scripts/test-markdown-safe.mjs` (digest 2026-11-12 holds an `<svg>`).
