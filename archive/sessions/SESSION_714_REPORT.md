# Session 714 report: 390 pixels, accessibility, links, tips

22 October 2026, from 10:30 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-714` on `wip/714-allgrids` (cut from `wip/713-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 714. Model spend USD 0. No warehouse data written. The only requests: the local build and the live site's own pages.

## Read these first

- **Every tip of the tab is reachable by keyboard.** Until this session the tips were `title`, which a browser shows only on a mouse's hover.
  - Each tip is now a button (the figure or the words) described by a `role="tooltip"` span. The site's rule shows the tip on hover and on focus (`app/tokens.css`, ".tip", the shared `Tip`'s pattern). A screen reader reads it as the button's description.
  - The node list's headings carry theirs the same way, and the defaults' sources in the box are the shared `Tip` (the small "i").
  - Shot: a figure's tip opened by focus, at 1280 and 390, `docs/brand/review-714/after_tip_focused_*.png`.
- **At 390 by 844**: the box "Your load" folds once the page has loaded. Its summary says the load ("Datacenter, 100 MW, load factor 0.90"). It opens on the server and without script. The table scrolls inside its own frame, and the first column stays in place.
- **AccessLint's unattended scan** (the command its `audit_live` runs, @accesslint/cli 0.13.0, WCAG 2.2 A and AA) on the tab's nine addresses at 1280 and 390, through session 583's scripts in the internal view:
  - **first: 7,460 findings on 18 scans**: 737 a page of "keyboard-accessible/focus-order", the tips' focusable spans without a role;
  - then 24 (the node list's words, a duplicate region name, an unmarked link);
  - **after: 0 on 18 scans.**
  - "Your load" (`/cost-of-power`) was 0 before and after.
  - The fixes are in the tab's own files and in `app/tokens.css`: a tip's trigger keeps the cell's face. The node list is a table to assistive technology (`role="table"`, `row`, `columnheader` with `aria-sort`, `cell`), and the A and B table's region has its own name.
- **check-links** on the tab's four addresses, the method note and `/internal/siting-gaps`: 288 links, 48 addresses, **0 findings** (2 aliases, by design).
- **No figure moved**: check-values 2,487 of 2,487 on every `/cost-of-power` address (715's build, which holds this session).

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view), click in the table, and press Tab: each figure takes the focus, and its tip opens under it.
2. On a phone (or a window 390 wide): the box is folded under "Your load"; tap its summary to open it.
3. `runs/chain_050/scan714_after.json` on this machine: the scan, rule by rule.
4. Screenshots: `docs/brand/review-714/` (after at 1280 and 390, the focused tip). The before is 712's build, `docs/brand/review-712/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session714`, `237` (every CSS rule closed) | 0 | OK |
| AccessLint, 9 addresses at 1280 and 390, three rounds | 0 | 7,460, then 24, then 0 findings; 0 tool errors |
| `check-links.mjs` on 6 pages | 0 | 0 findings |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` (715's build) | 0 | 2,487 of 2,487 |

## The landing

With sessions 713 to 715 in one push (see 715's report).

## Decisions made without you

1. **A tip's trigger is a button**: an interactive role is what the scan asks for, and the shared `Tip` uses one. The ids number the page's tips in the order the server draws them.
2. **The box folds after load on a narrow screen**, not on the server: the server does not know the width, and the box stays usable without script.
3. **Session 583's scanner was reused as it is** (`docs/brand/review-583/`), with the tab's addresses. The Chrome it started was stopped at the end.

## For Samuel's ruling

- The hub table's page is about 1.7 MB of HTML (the tips are long and the server's payload repeats them): fast on this machine, heavy on a phone. Shorter tips, or one source line a column, would halve it. See 716's report.

## Files

- Changed: `site/app/cost-of-power/AllGridsView.tsx` (`Tp`; every tip), `AllGridsNodes.tsx` (headings, words, table roles), `AllGridsForm.tsx` (the fold; the shared `Tip` for the defaults' sources), `site/app/tokens.css` (the trigger's face).
- New: `tests/test_session714.py`, `docs/brand/review-714/`, this report.
