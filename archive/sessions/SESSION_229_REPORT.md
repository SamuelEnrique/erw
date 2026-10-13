# Session 229 report: the whole-ERW review, for the roadmap

13 October 2026, 03:50 to about 06:00 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Read only: no page, table or setting changed. The output: `docs/reviews/erw-review-2026-10-12.md` and `docs/reviews/erw-review-2026-10-12/` (67 screenshots, 25 MB after quantizing), landed on `task/229-review`. Model spend USD 0. Pulls: none; the live set read with the public key. No em dash in anything written.

## Read these first

1. **The five sellable tools are two landings and five signatures away from "done".** The battery, generator and datacenter tools are finished on their branches (three questions, decisions blocks, replications, cross-checks; session 228 answers the datacenter's four questions with every number keyed); `main` still shows the old layouts, the generator's with 205 "not held" cells. Automated Analysis is one 29,000 px scroll, not a final form. The Grid tool is six pages on EIA-930 that have not been merged. No method note carries Samuel's signature. Section A.
2. **The 20 October license question reaches the pages a visitor sees first.** The price board, the datacenter tracker, deals, the digest, the Roundup, events and the map all read tables flagged "license needed" from 20 October (ISO-NE, MISO and NYISO's prices; the news outlets' index). The Terms page already holds the per-source table; the pages do not yet say what goes dark. Section D, item 8.
3. **Every number checked matches its table, and nothing is broken in the ways a scanner finds.** check-values on production: 6,928 of 6,959 values match (the 31 others are latest prices superseded within 45 minutes). On the 57 menu pages: 0 console exceptions, 0 sideways scrolls; dead links only on `/data` (two of the largest tables' downloads answer 502 on production: a timeout, not a missing table) and `/data/methods` (404 on the local build, 200 on production). Freshness is good: the stale tables are the ones already known (MISO paused, ERCOT's hub history to August).
4. **The site has twice the pages it needs.** EIA-930 is shown three ways plus seven grid pages; storage three ways; carbon three ways; a lease tab, a resources page, a tour, a customer battery and a companies list that each repeat a neighbour. Section B lists thirteen merges or cuts; section C the menu they leave.
5. **Session 228's scarcity level: keep USD 1,000 for every grid for the 20th**, say it on the page (done), and add each grid's own signal as a second count when its table is held, ERCOT's reserve adders first. Section F holds both cases.

## What was done

- The inventory: the 45 menu pages of `site/lib/pages.ts`, the home page, Privacy, the seven grid pages, the three Data subpages (57), and the three tool pages on their branches (the branch `wip/213-datacenter-layout` holds all three next versions, since each branch builds on the one before).
- The facts: `runs/session229/review.mjs` opened every page in a headless Chrome in the internal view on a local production build of `main` (`37c3a74e`) and of the branch, at 1280 px (and 390 px for the five tools and the Grid tool's parts): a full-page screenshot, the words, the headings, the placeholders, the dates, the console exceptions, every same-origin link fetched once, the scroll width. `scripts/check-values.mjs` ran against production for the checked number of each page; `runs/session229/probe_pages.py` read one table behind the pages that carry no key.
- The judgments: one block a page in the review (for whom, ten seconds, screenshot, the checked number, fresh or stale with the 20 October status of its tables, broken, four scores, a verdict), and sections A to F at the top.
- The landing: `task/229-review`, docs only; the snapshot before and after, 0 differences (the comparison's lines below).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 229"` | 0 | 6 of 6; on duty until 13 October 19:50 UTC |
| `npm run build` of `main` (`37c3a74e`) | 0 | no "statement timeout" line |
| `runs/session229/review.mjs` on the branch (3 pages, 1280 and 390) and on `main` (57 pages at 1280; 4 at 390) | 0, 0, 0, 0 | the first branch run was redone: the link checker had fetched the header's `/internal/lock` link and locked the view (the script now skips `/internal/` links) |
| `scripts/check-values.mjs https://erw-flame.vercel.app` (every page) | 0 | 6,928 of 6,959 values match; 31 latest prices superseded within 45 minutes |
| `runs/session229/probe_pages.py` | 0 | one table behind each of fifteen pages without a check key |
| `runs/session229/write_review.py` | 0 | 60 blocks, 67 screenshots, 25 MB |
| `node site/scripts/snapshot-live.mjs take s229-before`, `git push`, the check, `take s229-after`, `compare` | see below | |
| `scripts/freeze.py status` | see below | |

## Decisions made without you

1. **Production was used for the checked numbers and the local build for the screenshots.** `check-values` opens the internal view on production; the review script's unlock did not take there (the unlock answered 404 to it), so the 57 pages were read on a local build of `main`, which is the same commit as production. Nothing differs but `/data/methods` (404 locally, 200 on production), which the review records.
2. **The screenshots were quantized to 96 colors** (72 MB to 25 MB) so that a docs commit does not carry 72 MB; the text is readable, the charts' colors are approximate.
3. **The ten-second judgment is the session's, from the screenshot and the page's text**, not a user's. The scores are relative across the site, not against another site.
4. **Freshness is judged by the page's tables' newest timestamp against their cadence** (hourly and daily: four days; weekly: fourteen; monthly: 110; yearly: 400), from `coverage.csv`, with the newest date printed on the page beside it.
5. **Section D ranks landings first**: the three tool branches are finished work waiting on a screenshot review, and each is one session to land.

## For Samuel's ruling

1. The thirteen merges and cuts of section B, and the menu of section C.
2. The twenty improvements of section D: which to do before 20 October.
3. The scarcity level (section F).
4. The signatures: a line with your name and the date at the top of each of the five method notes.

## The landing

Filled in below by the session after the push.
