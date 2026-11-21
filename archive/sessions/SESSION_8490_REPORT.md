# Session 8490 report: /supply's whole-country views on the real files (chain 503, part E)

Energy Research Warehouse (ERW). The old laptop (samueloldlaptop, code role), unattended, 19 November 2026. Worktree `C:\Users\lossa\Documents\erw-8460`, branch `wip/8460-supply-regions-done`. Two runs: the first was cut off at 13:30 UTC, the second resumed at 13:42 and finished.

## What was done

- The page files reached origin/main (`af1962719`). The 108 untracked copies were each identical to main's (`git hash-object` against `git rev-parse origin/main:<path>`), so none was kept aside. They were removed and origin/main merged (`196673600`).
- The first run's uncommitted edit was finished and committed (`dba4caf28`): a figure that rounds to zero reads "0.0", never "-0.0" or "+0.0".
- The five cases of `docs/reviews/supply-regions-read-2026-11-19.md` were each taken start to finish on the page, drawn with the site's own code at each case's address (`site/scripts/supply-read-page.mjs`, no build, no server). Every question is answered on the page. The new rows 16 to 27 are in the document. Six faults were fixed at their cause, each with a test (`site/scripts/test-supply-regions-8490.mjs`, 34 of 34):
  - a pair's months held (16);
  - the storage hover (17);
  - "-0.0" (18);
  - the mean of a pair now has a hover: it runs over the hours both reported and can stand outside the two reports, as in 53 of 160 region pairs (19);
  - the percent's hover says when the two sides filed different hours (20);
  - a mix month the file leaves out now stands as a row reading "not held yet", with the builder's 90 percent rule on hover (21).
- Tests, each with its own loader, run after every change:
  - `test-supply-regions-8490` 34 of 34;
  - `test-supply-regions-8460` 20 of 20;
  - `test-supply-regions` 108 of 108;
  - the page pin `test-supply-pin` 208 of 208. No figure the page shows for the seven grids moved.
  - Two other test files fail with and without this session's changes. `test-supply-read.mjs` fails on base too: NYISO's cleared table is held under `license_status.json`, not this work. `check-network-v3.mjs` is a browser check: it needs Chrome and only names its own `pct1`.
- The replication on the real files after the merge and every change: **43,552 of 43,552** figures over 27 files. With `--same-flow`, 375 of 375 pairs agree with the trade files within 0.05 GWh. Both counts are in the method note and the document.
- The Stata do-file `replication/supply/replicate_regions.do`: the five headline figures with their expected values at its top. Not run, because Stata is not installed here. It needs Stata 16 with Python, since the files are JSON. The expected values were checked by an independent Python computation against what the page prints. One of them, the Northwest's figure from Canada, is exactly -7,769,650 MWh, a half: the page rounds it to -7,769.7, and Stata may print -7769.6.
- The cross-check is in the document, with a table of hosts (robots file and terms read first) and a table of ours against theirs:
  - Texas's 2025 shares by source stand within 0.4 points of ERCOT's own fact sheet.
  - Texas's net generation for September 2024 is within 0.5 percent of ERCOT's monthly overview.
  - ERCOT's text for September 2025 does not agree with itself, so no figure was taken from it.
  - EIA's Short-Term Energy Outlook puts ERCOT's solar 14 percent below ours. Wind agrees within 1.4 percent.
  - Trade with Canada and Mexico differs from EIA's Form EIA-111 by definition. For Mexico the sign is opposite; the likely reason is named but not confirmed.
  - No figure was adjusted.
- The decisions were checked on the real files. The section's hovers carry each choice with its default and source: the 10 percent gap, the regions drawn first and the year drawn first.
- The state table and the method note (`docs/methods/supply_and_trade.md`, "On the real files (session 8490)") are updated.

## What to review

- https://erw-flame.vercel.app/supply?region=ten&b=car&year=2025#whole-country : in "Who trades with whom", hover the Mean of Tennessee and the Carolinas (91.0, below both reports of 94.2 and 91.1). The hover should say the mean runs over the hours both reported.
- https://erw-flame.vercel.app/supply?region=sw&b=nw&year=2024#whole-country : in the Northwest's table, hover the percent for California (0.1). It should end with each side's hours, 8,784 and 8,000. In the Northwest's mix, November 2024 should stand as a row reading "not held yet". The Southwest's mix for 2024 should read "not held yet", with the 90 percent rule on hover.
- https://erw-flame.vercel.app/supply?region=tex&b=none&year=2025#whole-country : December 2025 should stand as a row reading "not held yet". The "2025, 11 months" row should name it on hover.
- https://erw-flame.vercel.app/supply?region=mida&b=midw&year=2025#whole-country : January and February 2025 should stand as rows reading "not held yet" in both mixes.
- These addresses show the change only once the branch lands. Every page is in review.

## Needs the key

- Nothing. Model spend was USD 0 (`ERW_SPEND_CAP_USD=0`), and no model was called.

## Decisions made without you

- The hours sentence on a percent's hover appears after the source sentence, not inside the facts. This keeps session 8430's tested words unchanged. It shows for any difference of hours, even one hour.
- A mix month counts as missing only between the file's `first` and `upto`. A year before the file's first month draws no such rows.
- In the cross-check, the set of ERCOT's fact-sheet shares that adds to 100 was used. The PDF's text also carries an overlaid 45.1 and 24.3 and a stale footnote.
- The Hourly Electric Grid Monitor was not read. It is an application with no figure on a page, and it draws the same Form EIA-930 the replication checks.
- CAISO was not asked: the California region is wider than CAISO's ground, and our 2024 holds 11 months.

## For Samuel's ruling

- Row 24: "Months held 12 of 12" can stand beside a report that covers 81 percent of the hours. Default taken: months on the face, hours on hover.
- Row 26: a year's share when a month is left out (Texas solar in 2025, 11 months). Default taken: the share over the months held, with the count on the face. The other choice: no share for such a year.
- Rows 9 to 11 of session 8460 (sorting, "not held yet" at the border, marking a large gap before rounding) and session 8430's three decisions still wait.
