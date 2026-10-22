# Session 725 report: the utility's path, walked

22 October 2026, from 13:57 UTC, on portable-laptop, unattended, in the worktree `C:\Users\samen\Documents\erw-725` on `wip/725-allgrids` (cut from `wip/724-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 725. Model spend USD 0. No warehouse data written; no request to a publisher. The only requests: production's own pages, in the internal view. Nothing fixed, as the section asks; session 726 fixes.

## Read these first

- **`docs/reviews/siting-utility-path.md`**: eleven questions a utility planner asks of the tab (where large loads are going and what they would ask of the grid), twelve steps walked click by click at 1280 and 390 with a 1,000 MW load, what each showed with its tips, and what broke with its cause.
- **The walk is a script**, `docs/brand/review-725/walk-725.mjs`: 24 of 24 steps made, exit 0 at both widths; no page error; no page wider than 390. Its records (`walk-1280.json`, `walk-390.json`) hold every checked figure and every tip in view.
- **Walked on production** (`e39de81a`, sessions 700 to 718): 719 to 724 (unlanded, on `wip/724-allgrids`) change nothing of the utility, headroom, connect and capacity columns this path reads.
- **What broke, inside this chain's files (three items, for 726)**: the Utility column sorts bundled, energy-only and delivery-only revenue per MWh as one figure, said in the tip only; the rule's document is written into the tip as text, not reachable; the A and B panel's utility row compares a county's utility with a state's stand-in without saying so.
- **For the ruling, unchanged**: Houston's and San Antonio's utilities are the county's largest seller to industry in the state (a cooperative each), not the county's main utility (718's item). The heavy-industry profile's interruptions (702's item).
- **Gaps and later sessions**: a zone's own growth (728), reserve margins (731), a load's own wait, ISO-NE's rule and median, the interruptible rider, the tracker's facilities while held (729 for the placements).

## What to review

1. `docs/reviews/siting-utility-path.md`, the table and "What broke".
2. The shots, `docs/brand/review-725/`: `02-utility-dearest_1280.png` (the Utility column first), `03-utility-ercot_1280.png` (Houston's cooperative), `05-headroom-zones_1280.png` (every zone its grid's growth), `06-connect_1280.png` (the rules and approvals under the months), `07-rule-tip_1280.png` (the tip on focus), `09-ab-zones_1280.png` and `_390.png`, `10-tracker_1280.png` (the hold).
3. To walk it yourself: after `/internal/open` on `https://erw-flame.vercel.app`, each step's address in the table.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 725" |
| `npm ci` in the worktree | 0 | |
| `walk-725.mjs` against production | 0 | 24 of 24 steps |
| em dashes in the new files | 0 | none |

No build in this session (production walked; nothing of the site changed).

## The landing

None: 726 lands 719 to 726 together.

## Decisions made without you

1. **Walked on production**, as 723 did: the columns the planner reads are the same on the branch.
2. **A 1,000 MW load** (the lab's size), since a planner is asked about loads of that order; the per-MWh figures do not move with it.
3. **The rule's tip was read by keyboard focus** (Tab to the trigger), as session 714 made the tips reachable, rather than by a mouse hover the script cannot make.

## For Samuel's ruling

- Nothing new. The planner's unanswered questions (planned generation by county, load growth by zone, the queue's loads by zone, the open rules named, a utility's own tariff) are listed in the path file, not built.

## Files

- New: `docs/reviews/siting-utility-path.md`, `docs/brand/review-725/` (the script, 24 shots, two records), this report.
- On this machine, not in git: `runs/chain_062/walk725.out`.
