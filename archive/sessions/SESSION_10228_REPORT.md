# Session 10228 report: the company database audited as a hostile expert would

Chain 710, part D, the old laptop, 26 November 2026. Worktree `erw-c710-b`, branch `wip/audit-companies-doc`. The audit: `docs/reviews/companies-model-audit-2026-11-26.md`, its evidence in `docs/reviews/companies-model-audit-2026-11-26/`.

## What was done

- `/companies`, `/companies/<id>`, their downloads, `lib/companydb.ts`, the page files of 16 November, the builders and the method note read; the deals page's companies tab and `energy_companies` read.
- Every figure of the default view and of three company pages (Florida Power & Light, Google, Constellation Energy Generation) restated from the page files' links alone: 204,275 keys, 9 gaps, all double rounding of 0.1 to 1 MW. The arithmetic is right.
- Seven findings, each with a test on its own branch: seven words branches (1 to 7) and their merge `wip/audit-companies-words` (`6a395e269`), each drawn with the site's own code and read (pass), no figure moved (5,168 keyed figures and cells equal); two test-only branches for ruling (8, 9).
- No table written, no lock, no model call, no request to a service, no default changed.

## Decisions made without you

- Finding 1's "Has: Policy actions" choice is marked "(license needed)" but left enabled (disabling it would change behaviour, not words); the column keeps its order link and gains a hover.
- Words that would go stale on a rebuild (counts) were kept out of the pages and put in the method note with their date; the kinds hover computes the unoffered kinds from `KIND_ORDER`.
- Adding "power marketer" to the Kind choices adds a count on the page, so it is a ruling (branch 9), not a words fix.
- "Headquarters state" relabelled "Owner's address state": a words fix, the figure unchanged.
- The double count was first measured as 62,735.3 MW (each company rounded); the unrounded sum, 62,736 MW, is used everywhere.

## For Samuel's ruling (default "left as it is")

- Finding 2, `wip/audit-companies-8` (`af73f45bb`): order `/companies` by the footprint without the share of a generator the company already counts whole: 62,736 MW at 106 companies out; 5 of the first 10 change places, PacifiCorp leaves for DTE Electric; 41 of the first 50 move.
- Finding 5, `wip/audit-companies-9` (`81f339980`): offer "power marketer" among the Kind choices: the choice "power marketer (439)" added.

## Needs the key

- Nothing.

## Rows returned to the chain's main session

- Landing: `wip/audit-companies-words` (`6a395e269`), words only.
- Data request: rebuild `site/data/companies/` from the tables of 25 November and report what moves (the audit's data request 1).

## Problems

- `tests/test_session156.py`'s node test of `/ask` fails on the merged branch and identically on origin/main: not this session's.
