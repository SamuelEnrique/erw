# Session 7600 report: chain 305's ground, and part A: the browser reads

Energy Research Warehouse (ERW). Chain 305 (`queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`), portable-laptop (code role), 16 November 2026, 10:30 to about 12:20 UTC. Model spend: USD 0 (`ERW_SPEND_CAP_USD=0`; no script that calls a model was run; the site was built and served here with no model key in its environment).

## At the top, because they are not what the chain file expected

- **One build ran under the chain's 2 GB rule.** The measure before the first build read 2,268 MB free; installing the site's packages in the worktree came between, and the build started at 1,760 MB without a fresh measure. It finished. Every build after it went through a script that measures first and refuses under 2,048 MB (eight builds, 2,463 to 3,646 MB free).
- **Two of Samuel's windows were closed to free that memory**, as the chain's rule says ("close what holds it"): the Snipping Tool, and the Edge window (a Google Doc, "3 City Analysis Plan", and one more page). Both were closed by their own window, not killed; Edge keeps its tabs in its history. Chrome (the remote view of the old laptop) was left open.
- **The fault the reads found is on production today, on every tool that draws the shared "i" mark**, not only on the pages read: at 390 px, 62 of the 91 marks measured on 19 pages run their box past the screen, and the page scrolls sideways while it is open. Fixed on the branch below for every page.

## The ground

- Precheck passed (10:30 UTC); `git fetch`; no freeze; 2.2 GB of memory free of 15.6 at the start, 307 GB of disk. Sessions 7600 to 7699 and queue numbers 350 to 359 free on origin/main, every branch and every queue file.
- No resume file of this machine in `queue/next/`. `queue/next/350-resume-chain-305.md` written, committed alone and pushed (`60435cc99`).
- `docs/state/done_line_claims.md` was on no branch: written from the chains' table (24 rows), committed alone and pushed (`e5ba04eb4`). `docs/state/data_requests_done_line.md` written with row 1 as the chain words it (`df15207e5`).
- Rule 8: `runs/snapshots/c305-before`, 25 pages, 0 failed, 10:30 UTC. Every push to main of this session holds state and queue files only, no site file.

## Part A, first bullet: the large-load pages of chain 302

- **Read:** `wip/7200-large-load` at `d192de75c` (not landed), built here and served on this machine; `/cost-of-power?view=allgrids` and `/policy?view=monitor&state=VA#large-load-laws` (and MD, TX, IN, WY, every state), in the internal view, at 1280 and 390 px. The whole read is `docs/reviews/large-load-on-site/browser-read-2026-11-16.md`: what was opened against the chain's list, 15 numbered rows, the measures before and after, 40 screenshots.
- **What works as written:** eight rows of five kinds open their panel from either cell; the 26 sorts, the 56 filter choices, A and B (a held rule too), the changes by state and by region, a rule opened from a change, the nine downloads, the 22 held rules' blank cells with "license needed" on hover and to a screen reader; no sideways scroll of the page at 390 px in any state.
- **17 of 17 figures** the browser drew were found in their table rows (the tables written from the committed research files, as chain 302's own test writes them).
- **Ten site faults, fixed with tests** (rows 1 to 10): a hover's box cut by its table's frame; past the window's edge (at 390 px, 144 of the table's 147, 176 of the laws' 227); a sideways scroll bar inside a box; the tables' first column printed over by the cells scrolling under it; a row's utilities named twice; "in effect, not published"; a period left at the head of a line; "newest first" opening with seven months above 13 November; 29 rows under "28 of 28 shown" and 98 under "94 of 94 changes"; axe's target size broken by 57 new elements.
- **After:** 0 of 579 hovers cut at 1280 px, 1 of 579 at 390 px (its trigger was outside the window when measured, the read's own doing); axe finds no rule broken on either page, in five states, at both widths, the 35 elements production already breaks included.
- **Two requests of the data machine** (rows 8 and 9 of `docs/state/data_requests_done_line.md`): the research's working words ("window A", "the brief") in 15 more hovers; `state_large_load_laws` drawn as "on Redivis".

## Part A, second bullet: the old laptop's rows

- `docs/state/browser_reads_wanted.md` held 14 rows by 11:30 UTC, on four branches none of which has landed. They merge with no conflict: merged on this machine into a branch that is not pushed, built once, read at 1280 and 390 px. Index: `docs/reviews/browser-reads-2026-11-16/README.md`, 24 screenshots.
- **Seen as written:** rows 2, 4, 5, 6, 8 and 13 whole; the words, counts and controls of every other row.
- **Faults:**
  - Rows 1, 7, 9, 10, 12 and 14: the shared mark's box past the screen at 390 px (and at 1280 px on `/shoulder`'s third headline). Fixed for every page: the placer written for the large-load hovers takes the shared mark too, mounted once in the site's layout; a headline's mark opens its box above itself so the figure under its label stays whole.
  - Row 11: "the batteries ran not held hours at rated power in those shoulders". Fixed on `wip/7600-shoulder-read`, cut from the old laptop's `wip/7503-shoulder` (its faults row 17).
  - Beside row 3, and on production: `/severance?tab=lease` was 406 px wide on a 390 px screen once a file was loaded. Fixed (the table scrolls in its own frame).
- Read again with the fixes merged in: every fold's box stands at 94 to 382 px of a 390 px screen and the page stays 390 px wide.

## Tests

- `site/scripts/test-large-load-read.mjs`: 54 of 54. `tests/test_session7600_large_load_browser_read.py`: 8 pass. Chain 302's three Node scripts: 92 of 92, 58 of 58 (one pin moved: the first change drawn), 25 of 25. `site/scripts/test-lease.mjs`: 93 of 93. Type check of the site: 0 diagnostics.
- Every test file that names a changed module, each in its own process: 80 files, 900 tests pass after one pin was moved with its reason (`tests/test_session2200.py`: the headline's tip slot now says where its box opens). No full suite and no landing gate here.
- `wip/7600-shoulder-read`: `tests/test_session7600_shoulder_read.py`, 5 pass; the six test files that name the page, 74 pass.

## What to review (both pages are in review; after the landing)

1. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rstate=VA#large-load-rules` on a phone, or a window 390 px wide.
   - Tap the first field of the first row ("New or additional separately meterable load ..."): the box is whole, inside the screen, and "Northern Virginia Electric Cooperative (NOVEC)" beside it is not printed over.
   - Scroll to "What changed in the last 90 days" and press "every state": the first row is dated 2026-11-13, and the line reads "94 of 94 changes, and 4 held".
2. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&llrow=ercot%3ALZ_AEN#large-load-rule` at any width: "The rule of a utility this row names (Austin Energy, Bluebonnet Electric Coop, Inc, Oncor Electric Delivery Company LLC, Pedernales Electric Coop, Inc)", each once; in Oncor's card the status, the docket and "The ERW's notes" are a line each.
3. `https://erw-flame.vercel.app/policy?view=monitor#large-load-laws`: "28 of 28 shown, and 1 read and not shown"; hover the last topic of West Virginia's row: its box is inside the window.
4. `https://erw-flame.vercel.app/impact` on a phone: tap any "i": its box stays inside the screen and the page does not slide sideways (on production today 23 of its 36 do).

## Needs the key

- Nothing in this session.

## Decisions made without you

- The old laptop's four branches were merged locally for one build. Nothing of that merge is pushed.
- The fixes to the large-load pages are on `wip/7600-large-load-read`, cut from the old laptop's `wip/7200-large-load` (the chain's rule). It lands after landing row 15 of `docs/state/landing_request_oldlaptop.md`, or in its place: it holds that branch whole.
- The placer is mounted in the site's layout and takes two kinds of hover only: the large-load rules' and the shared "i" mark. The All grids hub table's own tips and the charts' hovers are left as they are.
- A headline's mark opens its box above itself wherever the whole box fits there; elsewhere a box opens under its mark, as before.
- The hub table's two rule lines are 24 px high (they were 18): each hub row is about 12 px taller. It is what axe's target size asks.
- The fault of the shared mark is written once (row 14 of the large-load read file) and named in the rows of `docs/state/browser_reads_wanted.md`, not copied into the four tools' faults files, which are on the old laptop's branches.
- The first worktree's `node_modules` was a link to the main checkout's, which the build will not follow: the link was removed (the link only) and the packages installed in place, in both worktrees.

## For Samuel's ruling

- **A box opened in a table's frame on a phone has the frame's scroll indicator drawn across one of its lines for about a second after the frame is scrolled** (row 13 of the read). Default taken: left as it is.
- **"(session 83)" stands in grey beside each line of the decisions blocks** of `/contracts` and of the five tools (their title says "each with the session that made it"), while the page rule says no grey text and a reader does not know what a session is. The awards page's block puts it inside the box ("Made in:"). Default taken: nothing changed; it is the five tools' signed form.
- **Whether 24 px rule lines in the hub table read well** beside the cells' other captions. Default taken: 24 px.

## To finish

- The desk lands `wip/7600-large-load-read` (row 34 of `docs/state/landing_request_portable.md`) and `wip/7600-shoulder-read` (row 35), the second after the old laptop's `wip/7503-shoulder`.

## Commits

- main: `60435cc99` (the resume pointer), `e5ba04eb4` (the claims), `df15207e5` and `628bede7d` with its merge `e044a3fac` (the data requests), and the state files that follow this report.
- `wip/7600-large-load-read`: `3ea3ce82d`, `f8405336d`, `82ab05cd0`, `c11941020`, `9fcc1bd41`, and the commit that holds this report.
- `wip/7600-shoulder-read`: `094b3de62`.
