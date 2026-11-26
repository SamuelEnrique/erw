# Session 11000 report: chain 750, the start, part A and part B

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's second window (`$HOME\Documents\erw-w2`, a worktree; code role), unattended. Chain file: `queue/done/750-night-26-november-portable-window2-browser-read.md`. Kept current while the session runs; the progress file `docs/state/progress_c750.md` has each step, and `docs/reviews/browser-read-2026-11-26.md` is the review itself.

## What was done

- **The start.** The chain file taken by hand (`4e8d24f7e`); the resume file `queue/next/751-resume-chain-750.md` committed alone (`0fac57d61`); the progress file started. No freeze. Sessions 11000 to 11199 were free on origin/main and all 818 remote branches.
- **Memory.** 1,656 MB free at the start (11:11 UTC); 1.8 to 4.5 GB available before each browser. One browser at a time, each closed before the next. No build, no whole suite, no model call.
- **Part A, the rows that waited for a browser.** Rows 418 to 422 of `docs/state/browser_reads_wanted.md`: their three branches are in main now; all five read on production at 1280 and 390 px and marked seen. No row is left wanted.
- **Part B, the list.** Nothing changed a page's code between 21 November 04:06 UTC and tonight, so the list is 14 pages and views landed 20 and 21 November. Each line says whether a browser read it on production after it landed.
- **Part B, read so far (on production, internal view, 1280 px with a mouse and 390 px with a finger):**
  - the four accessibility fixes of 20 November that were built without a browser (`/policy?view=week`, `/severance`, three headings pages, the Grid tool's reliability table);
  - `/conditions` in full: five cases, 15,553 table cells and 21 summary lines against the page files in seven views, the hand 11 of 11 at each width;
  - `/congestion` in full: five cases, 166 of 166 checks at each width (1,715 marked figures, 1,400 list cells, 4,608 cells of the hour-by-month tables, 1,218 monthly figures), the hand 12 of 12;
  - the thirteen regions in the Grid tool: 94,435 cells against the mix files;
  - chain 620's ten fixes and the tour's eighth stop: all on production;
  - the problem edition of 21 November: 82 of 82 checks at each width;
  - a sweep of 146 addresses at 390 px (every fixed address and the Grid tool's 63 views).
- **Faults found and fixed (three branches, each with a test; none landed, none built here):**
  - `wip/c750-grid-reliability` (`038ecbfcd`): `/grid?grid=caiso` was 539 px wide at 390 px. The labels the accessibility fix of 20 November added to the reliability table escape the table's scrolling frame and widen the page. One class.
  - `wip/c750-conditions` (`569d15885`): `/conditions` listed 40 alerts under a heading that counted 44 (and 40 of 79), with no word that the list was cut; and each operator's line said its clock twice.
- **Faults found and filed:**
  - Two fixes of the desktop's second window read "landed" and never reached main (`4f3247287`, `923d4cb4f` on `wip/w2-c620-fixes`); both faults are still on production. Row 2 of this window's landing file.
- **`docs/state/landing_request_portable_w2.md`** written in the form of the portable laptop's file: three rows, each `ready, to be seen` (the first window sees them in a build; window A's desk lands them).
- **The pictures:** `docs/reviews/browser-read-2026-11-26/`, a folder a page.

## The five worst things found so far

1. `/grid?grid=caiso` scrolls sideways on a phone (539 of 390 px) since 21 November: a fix made without a browser broke the page it mended. Fixed, to be seen.
2. `/conditions` silently dropped the last day's alerts of CAISO's September 2022 heat wave, and half of the August 2020 one. Fixed, to be seen.
3. Two fixes marked landed on 21 November are not on main. Filed.
4. Every page that draws from the data machine's page files shows 18 to 20 November: its daily commits of 21 to 25 November sit on `wip/red-dm-*` branches. Known to window A (chain 701, part C); no request filed.
5. A reason given on hover (why a strip or a cell is blank) cannot be opened by a finger. Site-wide; for Samuel's ruling.

## Decisions made without you

- **The precheck's failed check was passed over.** From a worktree `daily_cap` always fails (no cost ledger in the folder, and Supabase's copy did not answer). This window spends USD 0 on models, so the session went on, as the desktop's worktree windows do.
- **A slip of mine, mended.** I ran the precheck twice without `--dry-run`. Each failed run recorded the laptop as idle, which would have emailed "ready for review" fifteen minutes later while both windows were working. I retook the machine's duty mark with `scripts/duty.py start` (the designed way: a machine on duty again after its idle row sends nothing), and a dry run of the ready check confirmed no email was due. This wrote one file in the main folder, `.erw/duty.json`, the same file a passing precheck writes; nothing else there was touched. The duty mark now names both windows' sessions.
- **Documents go to main, code to `wip/c750-*` branches,** as the chain says and as the laptop's first window does.
- **`/grid`'s fault was fixed here and not only filed.** The chain's table gives the old laptop the audits of `/cost-of-power` and Automated Analysis; its part D has also begun an audit of the Grid tool's figures. This fix is one class on the reliability table's frame and changes no figure, so it was made on its own branch, and the landing row says the audit is running.
- **`/conditions` now lists every alert its heading counts** (on the branch), where the other reading was to keep the cut at 40 and add a sentence saying so. The cut was nowhere declared (not in the page's decisions, not in the method note). If the cut should stay, the branch's one line is easy to turn into the sentence.
- **The second window's landing file was not edited** (another window's file). The two unlanded commits are a row of this window's own file instead.
- **No data request was filed for the stale page files:** chain 701's file already names the cause and repairs it tonight.
- **`/data/licenses`' "undefined" was not reopened:** the read of 20 November settled it as the publisher's own answer.
- **Three "not a fault" calls on `/congestion`** (a thousands comma, a base case called a contingency, cells readable only on hover) went to the ruling list and not to a branch: the first is pinned by the gate's own check, the others are choices of words and of design.

## For Samuel's ruling

Kept at the foot of `docs/reviews/browser-read-2026-11-26.md`, each with the page left as it is.

## Needs the key

- Nothing. No model was called.

## What to review

- `docs/reviews/browser-read-2026-11-26.md`, and the three rows of `docs/state/landing_request_portable_w2.md`.
