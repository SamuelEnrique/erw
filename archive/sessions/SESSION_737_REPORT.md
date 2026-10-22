# Session 737 report: the page's weight

22 October 2026, from 16:38 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-737` on `wip/737-allgrids` (cut from `wip/736-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 737. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Where the hub table's bytes go** (a build of `wip/735-allgrids`, the internal view, `runs/chain_062/weigh.mjs`): 1,860,363 bytes of HTML.
  - **1,055,175 bytes are the server's payload** for the client, drawn after the HTML: the same tree again, as App Router sends it.
  - **496,573 bytes are the 787 tips' markup**, and 285,176 of those repeat a text already drawn elsewhere on the page. The four-peak charge's tip, for one, is the same on each of ERCOT's rows.
- **What shrank without a word changed: the tip's box.** It was a list of fourteen utility classes on each of the 787 tips, drawn twice (in the HTML and in the payload). It is now one rule in `app/tokens.css`, keyed by a short attribute (`data-tp`).
  - **The hub table: 1,860,363 to 1,584,786 bytes, 275 KB less (15 percent).** The flexible profile: 1,702,164 to 1,425,282. The node list barely moves (its tips are its own).
  - **The look is the same.** The shots before and after show the same box and the same rows. The first try also moved the wrapper's classes into the rule, which changed the rows' height where a cell made its tip a block, so the wrapper keeps its classes. The tip's line height is set to the old one.
- **No figure moved**: check-values reads 2,696 of 2,696.
  - The existing tab shows 3 differences from production, all in "Your load"'s carbon window at SP15 (9,944 hours against 9,920).
  - That window reads the hourly intensity live, and this build is newer than production's page (built at 14:53). This chain's change is not involved.
- **The shorter-tip variant was not built.** Session 716's ruling item asks whether to shorten the tips by changing their words, and choosing those words is the ruling itself.
  - What it could take off is measured: 193,486 bytes of repeated tip text in the HTML, and about as much again in the payload.
  - It is listed in the rulings file (session 741) with that measure, instead of a branch `wip/737-tips-variant`.

## What to review

1. `docs/brand/review-737/before_tip_1280.png` against `after_tip_1280.png`: the same tip.
2. `docs/brand/review-737/weight.txt`: the three addresses before and after.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `npm ci`, `npm run build` three times (lock `s737`, beat) | 0 | |
| `weigh.mjs`, before (735's build) and after | 0 | above |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,696 of 2,696 |
| `check-existing-tab.mjs`, production against the build | 1 | 3 differences, the live carbon window (above) |

## The landing

With the next landing.

## Decisions made without you

1. **Only markup moved**: the tip's box is styled once in `tokens.css` (the chain's rule that style lives there). Every word and every figure is as it was.
2. **No variant branch**: the words of a shorter tip are the ruling's to choose; the measure is in the rulings file.

## For Samuel's ruling

- Session 716's item stands, now with a measure: shorter tips would take off about 190 KB of the hub table's HTML and about as much of its payload.

## Files

- Changed: `site/app/cost-of-power/AllGridsView.tsx` (the tip's box), `site/app/tokens.css` (its rule).
- New: `docs/brand/review-737/`, this report.
