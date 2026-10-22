# Session 727 report: the lab's path, again

22 October 2026, from 14:23 UTC, on portable-laptop, unattended, in the worktree `C:\Users\samen\Documents\erw-727` on `wip/727-allgrids` (cut from `wip/726-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 727. Model spend USD 0. No warehouse data written; no request to a publisher. The database was read only by the site's own pages on the local build.

## Read these first

- **Session 717's ten steps walked again, with two more** (719's tracker link, 720's card), on a build of this branch, since production still serves `e39de81a` (sessions 700 to 718; the landing of 719 onward waits for the window). `docs/reviews/siting-path.md` gains a "Now" column, each step's result then and now, and a section for this walk.
- **No step fails.** Every figure of the path is as 717 saw it; what differs is what chain 050 and this chain changed since: 718's capacity above the peak for every grid (NYISO 34 and ISO-NE 37 percent above, where 717 read 130 and 134 percent of the peak) and the 18 rows' county utilities, 724's spread column and panel links, 726's basis words and document links, the gaps file at 30 rows (28). So nothing was fixed and no test was written.
- **One reading worth a look**: sorted by the utility's figure smallest first, PJM's row comes first (11.34 per MWh): 718 placed PJM in Allegheny County, whose seller's row is delivery only (a wires charge), where 717 saw "not held". Since 726 the cell says "delivery only; Allegheny County, PA" and the sort line says the column compares unlike bases. Whether a delivery-only figure should sort beside bundled ones is for the ruling (below).
- **The tracker shows no facility** (held) and so no link; **the card** reads the tab's figures (40.83 least, 46.69 most, 45.80 and 100.00 months).

## What to review

1. `docs/reviews/siting-path.md`, the "Now" column and its last section.
2. The shots, `docs/brand/review-727/` (`q1_allin_cheapest_1280.png` to `q12_card_1280.png`, and the 390 pair of each).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 727" |
| `npm ci` in the worktree | 0 | |
| the build served | | session 726's build of the same commit (`f311b096`), served on port 3727: no new build was needed |
| `walk-727.mjs` | 0 | 28 of 28 steps at 1280 and 390, no page error, no page wider than 390 |
| em dashes in the changed files | 0 | none |
| the server stopped | 0 | |

## The landing

None: 730 lands 719 to 730.

## Decisions made without you

1. **Walked on a build of the branch, not on production**, so that 718 to 726 are in place as the section asks; production lacks 719 onward until 730's landing.
2. **Session 726's build was served**, since this branch is the same commit: no build lock, no rebuild.
3. **The utility sort's PJM reading is reported, not changed**: the figure is right (a delivery-only seller's revenue per MWh), the words say what it is, and whether such a figure should sort with the others is a ruling.

## For Samuel's ruling

- Whether a delivery-only utility figure (PJM's Allegheny County seller, 11.34; New York County's Con Edison, 128.79) should sort in the Utility column beside bundled and energy-only figures, or sort last as "unlike" (the cell says its basis since 726).

## Files

- Changed: `docs/reviews/siting-path.md`.
- New: `docs/brand/review-727/` (the script, 28 shots, two records), this report.
