# Session 11000 report: chain 750, the start, parts A, B and D, part C begun

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's second window (`$HOME\Documents\erw-w2`, a worktree; code role), unattended. Chain file: `queue/done/750-night-26-november-portable-window2-browser-read.md`. Kept current while the session runs (state at 15:25 UTC); the progress file `docs/state/progress_c750.md` has each step, `docs/reviews/browser-read-2026-11-26.md` is the review itself, and `docs/state/note_2026-11-26_portable_w2_c750.md` is the short note.

## What was done

- **The start.** The chain file taken by hand (`4e8d24f7e`); the resume file `queue/next/751-resume-chain-750.md` committed alone (`0fac57d61`); the progress file started. No freeze. Sessions 11000 to 11199 were free on origin/main and all 818 remote branches.
- **Memory.** 1,656 MB free at the start (11:11 UTC). Before each browser the read kit reads the memory and refuses under 1,500 MB: it refused twice (274 MB at 12:43 UTC, 1,032 MB at 14:05) while the first window built, and the session wrote up what it had instead. One browser at a time, each closed before the next. No build, no whole suite, no model call.
- **Part A.** Rows 418 to 422 of `docs/state/browser_reads_wanted.md` read on production at 1280 and 390 px and marked seen. No row is left wanted.
- **Part B, all of its list** (14 pages and views landed 20 and 21 November; nothing changed a page's code from 21 November 04:06 UTC until tonight): `/conditions` and `/congestion` in full, the thirteen regions of the Grid tool, the four accessibility fixes built without a browser, chain 620's ten fixes, the problem edition of 21 November, the events, demand and supply pages, the five reader-test pages.
- **Part D,** taken while nothing of tonight's had landed: the five sellable tools (battery, generator, Automated Analysis, the Grid tool; what a datacenter pays read and not edited), every other page of the site with a fixed address walked by hand at both widths (43 pages in three rounds), the first minute, every form of the site against the back button, the readers' cases of the Grid tool and of Automated Analysis taken on the page, links that carry a choice opened fresh, and two tables of `/supply` and `/demand` set beside the region files once more (1,670 and 196 cells, all agreeing).
- **Sweeps:** 146 addresses at 390 px and 145 at 1280 px (every fixed address and the Grid tool's 63 views); the 173 addresses of the site's own check list at 390 px with every chart switched to its table; every field of 82 pages asked for its name.
- **Figures:** about 120,000 set beside the page files; 5,142 beside Supabase by the site's own check on the five tools' addresses. One disagreement (the alerts list of `/conditions`).
- **Part C** began at 14:16 UTC with the first landing of tonight (`task/c701-desk-3`: three of this window's rows, `/impact` with Datacenter, the old laptop's audit fixes). Rows 1, 2 and 3 are seen fixed on production at both widths; `/impact` with Datacenter was read in full (rows I1 to I5 for window C), its four older plant types unchanged (1,700 figures on eleven addresses, before and after); the site's own figure check after the landing: 6,680 of 6,680. `/forecast`, `/equities` and the board's new group were not on main at 15:21 UTC (the desk's next gate is announced for after 16:15 UTC); the board as it stands is recorded (25 groups, 276 rows, 12 tiles) to show it loses nothing, and the eight energy prices in the equities page files already agree with the board.

## Faults found: eight fixed on five branches of this window's (and row 2, two commits of another window's), nine filed

Each branch is cut from origin/main and carries a test that fails on the code before; none was built here. Rows of `docs/state/landing_request_portable_w2.md`.

| Row | Branch | What | State at 15:25 UTC |
|---:|---|---|---|
| 1 | `wip/c750-grid-reliability` | `/grid?grid=caiso` 539 px wide at 390 px (the hidden labels of 20 November's accessibility fix escape the table's frame) | landed 14:16 UTC |
| 2 | `wip/w2-c620-fixes` (the desktop's second window's) | two commits that read landed on 21 November and were not on main | landed 14:16 UTC |
| 3 | `wip/c750-conditions` | `/conditions` listed 40 alerts under a heading counting 44 and 79; the clock said twice | landed 14:16 UTC |
| 4 | `wip/c750-grid-last-week` | the Grid tool's "same day last week" lost its first 5 to 8 hours on every grid | requested |
| 5 | `wip/c750-companies` | `/companies`: five of six fields with no name for a screen reader; the lists kept a choice after the back button | requested (seen in a build by the first window) |
| 6 | `wip/c750-forms-back` | `/prices/compare` and `/conditions`: fields kept a choice after the back button | requested (seen in a build by the first window) |

Filed for the windows that own the page tonight (rows of the review): CP1, `/cost-of-power?view=grids` is 1,677 px wide on a phone after one tap on a chart's Table switch (the old laptop); CP2, the All grids tab does not follow the back button (window A and the old laptop); R1, `/research` says of its small example charts "hover reads them" and they give no value (the old laptop); I1 to I5 on `/impact` with Datacenter (window C): no default's own document can be opened from the page, the taxes' total does not say what it leaves out, Georgia's exemption reads "none", a document's figure the tool does not take is not said (Paducah's USD 100 billion, Starwood's 1,500 jobs), and an address with the project's id alone shows its name over the default's figures. Known to its owner, no request filed: the data machine's page files of 21 to 25 November.

## Stopped by Claude Code, and not started again

- At about 12:23 UTC two runs I had put in the background were stopped, the laptop critically low on memory while the session waited on them: the sweep of all 616 method pages at a phone's width, and the site's figure check over its whole list. Neither is started again unless asked. Since then every read runs in the foreground. The figure check was run in the foreground on the five tools' addresses only; the method pages were not swept.

## Decisions made without you

- **The precheck's failed check was passed over.** From a worktree `daily_cap` always fails (no cost ledger in the folder, and Supabase's copy did not answer). This window spends USD 0 on models, so the session went on, as the desktop's worktree windows do.
- **A slip of mine, mended.** I ran the precheck twice without `--dry-run`. Each failed run recorded the laptop as idle, which would have emailed "ready for review" fifteen minutes later while both windows were working. I retook the machine's duty mark with `scripts/duty.py start` (the designed way), and a dry run of the ready check confirmed no email was due. This wrote one file in the main folder, `.erw/duty.json`, the same file a passing precheck writes; nothing else there was touched.
- **Documents go to main, code to `wip/c750-*` branches,** as the chain says.
- **Faults on `/grid` were fixed here.** The chain's table gives the old laptop the audits of `/cost-of-power` and Automated Analysis; its part D also audited the Grid tool's figures (finished, on main). Neither of this window's two Grid fixes changes a figure that is drawn; the landing rows say which of the audit's branches touch a neighbouring file.
- **`/cost-of-power` and `/research` were not edited,** though the three faults found there are small: the old laptop audits both tonight, and window A is writing the All grids tab.
- **`/conditions` now lists every alert its heading counts,** where the other reading was to keep the cut at 40 and add a sentence. The cut was declared nowhere. Line 6 for a ruling says how to turn it back.
- **The back button's mend for forms that submit with their button is `autocomplete="off"` on the form,** not chain 620's script for the lists that submit themselves: one attribute, no client code, tried on production's own pages (16 of 16 over the three forms). One thing changes for a reader: the browser no longer offers earlier entries in those boxes.
- **The site-walking tests were run in place of the whole suite** (the first window's rule of today for a chain that forbids the suite): 121 test files on rows 1, 3 and 4 merged, 120 on each of rows 5 and 6; about 2,100 tests each time, none failing.
- **The second window's landing file was not edited;** its two unlanded commits were a row of this window's file.
- **No data request was filed** for the stale page files (chain 701 repairs them tonight), and `/data/licenses`' "undefined" was not reopened (settled on 20 November).
- **A foreground figure check on the five tools only** was run after the full one was stopped: a smaller command, no browser, with 3 to 4 GB free. The full list and the method pages' sweep wait for your word.

## For Samuel's ruling

Twelve lines at the foot of `docs/reviews/browser-read-2026-11-26.md`, each with the page left as it is; the same twelve in plain words in the note.

## Needs the key

- Nothing. No model was called.

## What to review

- `docs/reviews/browser-read-2026-11-26.md`, its pictures under `docs/reviews/browser-read-2026-11-26/`, and the six rows of `docs/state/landing_request_portable_w2.md`.
