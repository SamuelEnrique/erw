# Session 10207 report (chain 710, part D: the severance tool audited)

26 November 2026, the old laptop, worktree `erw-c710-c`, branch `wip/audit-severance-doc`. Unattended. Model spend USD 0 (no model call; `ERW_SPEND_CAP_USD=0` for every python run). No request to any live service.

## What was done

- `docs/reviews/severance-model-audit-2026-11-26.md` and its evidence folder: the severance tool (`/severance`, both tabs) read as a state tax analyst and a mineral-rights economist would.
- **The arithmetic is right:** an independent restatement in exact decimals, from the method note and the rules file, equals the page's own code on 907 figures and printed strings (108 cases; the default view: WTI October 2026 mean 102.07, 1,000 bbl of Texas oil, gross USD 102,070.00, tax 4,695.22, fee 6.25). The published replication: 612 of 612.
- **Five findings:** two Medium (3: the Lease tab taxes every month at today's rates, unsaid; 1: Louisiana's posted field price floor printed, not applied), three Low (2: Louisiana condensate takes a deduction its statute does not give, a figure; 4: "county levies are not here" yet New Mexico's district levy is; 5: "Texas condensate owes 4.6 percent with no floor" against its own cited section).
- **Branches** (each from origin/main, pushed): `wip/audit-severance-1` (`f5b469121`), `-3` (`a1d8dce6d`), `-4` (`72d183f8b`), `-5` (`f59cd1171`), words only, for landing, each drawn to HTML and read (pass); `wip/audit-severance-2` (`36f162994`), a test only, not for landing.
- **Tests run:** each branch's own test, and every test file reading the files it changed (`test_session7502_severance`, `282`, `334`, `239`, `45`, `40`); the four words branches merged in a trial: 61 passed.

## Decisions made without you

- The page was drawn with the site's own loaders plus one stand-in: `components/Brand.tsx` (it imports Next's fonts, which only a build resolves) drawn as a plain wrapper. It holds no figure or word of the tool.
- `site/node_modules` in this worktree is a junction to the main copy's (as the two other worktrees of this chain have): read only, git-ignored, nothing written there.
- Words fixes were put in the decisions fold, the leads and the method note, not in `site/data/severance_rules.json`, which the data machine keeps (the finder and `/impact` read it).
- Finding 2 is a figure (it moves a tax once a transport fee is typed), so only its test was made.
- Git's automatic housekeeping tried, on two commands, to prune two stale worktree records of the main copy's `.git` and was refused ("Permission denied"); nothing was removed. Later commands ran with `-c gc.auto=0`.

## For Samuel's ruling

- Finding 2, default "left as it is": Louisiana condensate stops taking the trucking, barging and pipeline deduction (the statute's "gross value"). 1,000 bbl at USD 102.07 with USD 2 a barrel: USD 12,758.75 instead of 12,508.75 (+250.00, +2.0 percent). Nothing moves at the default.

## Data requests (returned to the main session)

1. EIA's crude oil first purchase prices for Texas, Louisiana and New Mexico, monthly (the table on this machine holds Mars and North Dakota only): each state's gap to WTI Cushing's monthly mean, November 2025 to the latest month, and the tax effect at 4.6, 12.5 and 7.14 percent.
2. The past rates: Louisiana's natural gas severance tax rate and horizontal well exemption shares for each fiscal year July 2022 to June 2026 (the Department of Revenue's bulletins), and TRD's New Mexico rate tables for January 2023 to March 2026 and from September 2026: to size finding 3.

## Needs the key

- Nothing.
