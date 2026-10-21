# Session 412 report: accessibility on every visitor page

21 October 2026, about 06:10 to 08:30 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-412` on `wip/412-s` (cut from `wip/381-382-land` at `df638a38`). Chain `queue/done/015-day-20-october-code-pm.md`, "Session 412: accessibility on every page". Model spend USD 0; no pull from any publisher; no warehouse data written; the site was read only on this machine (`http://localhost:3412`).

## Read these first

- **The review the chain named did not exist.** `docs/reviews/accessibility-2026-10-20.md` was on no branch (local, `origin`, every `wip/` and `task/`), and no earlier queue file asked for it. The session wrote it from its own audit, before and after the fixes: twelve findings, each with the page, the tool and rule, the count before, the fix and the count after.
- **AccessLint finds nothing on any of the 49 audits after** (47 pages: the snapshot's 25 addresses as 11 distinct pages and two query variants, and every page of the menus), against 250 findings on 13 of them before, 218 of those the board's rows. The keyboard walk (Tab from the top, up to 80 stops a page, 2,651 stops in all) shows the brand's ring at every stop, where 85 footer stops and 2 date fields had none or the browser's thin one; the accessibility tree has no control without a name, where the impact page had two (and two named by their placeholder).
- **The fixes are in the shared pieces first**: `app/tokens.css` (footer focus, date fields), `components/Nav.tsx` (`aria-current` in the menus), `components/ScrollRegions.tsx` mounted once in `app/layout.tsx` with `lib/cells.ts` (scrolling tables reachable by the keyboard; empty header cells drawn as plain cells in `ToolTable` and `DataTable`), `components/board/BoardView.tsx` (a button in each row's name). Then five pages' own: demand, curtailment, events, network, impact.
- **One real fault a visitor would see**: on `/demand` the ranking's three column headers were white on the brand's white header, invisible (shots `07-demand-ranking_before_1280.png` and `_after_`).

## What to review

- The review: `https://github.com/SamuelEnrique/erw/blob/wip/412-s/docs/reviews/accessibility-2026-10-20.md`
- The shots, 13 places at 1280 and 390 px, before and after: `https://github.com/SamuelEnrique/erw/tree/wip/412-s/docs/brand/review-412`
- The code: commit `6540e30d` (the fixes and `tests/test_session412.py`); the review and shots: `63513a01`.
- After the landing, in the internal view: `/demand` (the ranking's headers), `/board` (Tab to a row's name, Enter opens the workbench), `/contracts` and `/demand` at 390 px (Tab reaches the wide table, the arrow keys scroll it), `/impact` (each field reads its label), `/curtailment` (the tiles' words, the "Where free energy is" link), any page's footer by keyboard.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s412/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `duty.py beat` before each of the four builds | 0, 0, 0, 0 | |
| `npm ci` in the worktree's `site/` (under the mutex) | 0 | |
| `npm run build`, before the fixes | 0 | no statement timeout |
| `npm run build`, after the fixes | 0 | no statement timeout |
| `npm run build`, with the script's first pass made at once | 0 | |
| `npm run build`, with the shared tables marked on the server (the build the last checks read) | 0 | no statement timeout |
| AccessLint `audit_live`, 49 audits, before | | 13 audits with findings, 250 in all (see the review) |
| AccessLint `audit_live`, 49 audits, after | | none on any; the pages with scrolling tables read once with `wait_for` the script's mark and again without it on the last build (only `/data`'s install line is then found, before the page's script runs: listed) |
| `a11y-412.mjs` (accessibility tree and keyboard walk), 47 pages, before / after / last build | 0, 0, 0 | 2 unnamed fields and 87 stops without the brand's ring before; none after |
| `shots-412.mjs`, before and after, 13 places, 2 widths | 0, 0 | 52 PNGs; each pair looked at before it is described |
| `tests.test_session412` | 0 | 20 tests OK |
| The 43 modules that read the changed files (109, 110, 114_part2, 124, 132, 144_page, 168_board, 168_network, 177, 179, 180, 186, 193, 194, 203, 235 to 241c, 266 to 268, 281, 296, 298, 299, 314, 317 to 319, 328, 331, 351, 352, 370, 54, 67, 93) | 0 | after the fixes; `test_session241a` follows the tiles' new switch |
| The whole suite, `unittest discover -s tests` | see "Suite" below | |

## Decisions made without you

1. **The review was written by this session** (it did not exist), from AccessLint and the browser's tree on a local build of this branch, as the chain's notes ask; the findings are this session's readings, before and after.
2. **AccessLint was pointed at a Chrome the session started on port 9412** and unlocked by the form (the token posted, never in an address), because every page is in review and AccessLint's own browser would audit the curtain. The Chrome, its profile and the server were stopped and removed at the end; nothing was left on 9222.
3. **Scrolling tables, two layers.** The script (`ScrollRegions.tsx`) marks any scrolling box under `<main>` that holds nothing focusable and takes the marks back when it fits, at any width; the shared tables also carry the marks from the server, so the keyboard reaches them before and without the script. A table that fits loses its stop once the script runs, so a wide screen gains no extra stops (the walk after: 3 regions at 1280 px, the three that scroll).
4. **A region's name is the table's caption** (already given to a screen reader), else its figure's or section's title, else "Table" or "Code": words a sighted reader does not see, the one kind of words the brief allows ("a missing label").
5. **The board's row is no longer a stop of the keyboard; its name is a button.** The row still opens on a click anywhere; the button's click reaches the row, so it opens once. A blank row (paused, licensed) opens nothing and has no button. `aria-pressed` marks the row in the workbench.
6. **Empty header cells are plain cells**, kept in the sticky first column; no word was added to say "rank", which a ruling could add.
7. **The curtailment tiles' switch moved from 0.5 to 0.655** (the point where white and ink give the same contrast on the ruled accent ramp); the ramp itself, ruled on 20 October, is unchanged. No switch reaches 4.5 to 1 in the band: a ruling.
8. **Links underlined on two pages only** (the curtailment note's link and the events' titles), the two AccessLint found; the brand's rule for links in running text was not widened to every `div`, which would underline links across the site.
9. **`test_session241a` was changed** where it asserted the old switch (`s > 0.5`), with a comment; nothing else of it.
10. **No landing to `main`**: the brief's "Land" is this branch, `wip/412-s`, pushed.

## For Samuel's ruling

- The curtailment tiles between about 53 and 69 percent shading carry their words at about 3.6 to 1 at best (white passes 4.5 only from 70 percent, ink only to 53): (a) a white band for the words inside the tile; (b) the words under the tile; (c) leave 3.6 to 1.
- The Ask panel on `/network`, `/grid` and `/ask` is reached by the keyboard after the whole page while drawn at its top right: (a) first in the page's order; (b) a second skip link to it; (c) leave it.
- The menus' names are 20 px tall where the brand asks 24 px for a target (WCAG's 24 px is met by their spacing): (a) raise them, the header grows 4 px; (b) leave.
- The hover tip's mark ("i") is 16 px square, under the brand's 24 px: (a) a 24 px target around the same mark; (b) leave.
- `/data`'s install line is reached by the keyboard only once the page's script has run: (a) mark it on the server with a name; (b) leave.

## Suite

`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests` at `63513a01`: exit 1, 4,802 tests in 492 s, 252 skipped, one failure: `test_session156.TheNodeTests.test_the_sessions_own_tests_pass_with_no_request_and_no_switch_set` (the ask fixtures' `site/scripts/test-ask-ready.mjs`, its test 10: "Cannot read properties of undefined (reading 'day')"), the failure the chain's rules expect tonight; this session touched none of the ask code. Output: `runs/chain_oct21/s412/suite.out`.

## Files

- New: `site/components/ScrollRegions.tsx`, `site/lib/cells.ts`, `tests/test_session412.py`, `docs/reviews/accessibility-2026-10-20.md`, `docs/brand/review-412/` (52 shots, `a11y-412.mjs`, `shots-412.mjs`, `unlock9412-412.mjs`, the page list and the two walk summaries).
- Changed: `site/app/tokens.css`, `site/app/layout.tsx`, `site/components/Nav.tsx`, `site/components/tool/ToolPage.tsx`, `site/components/svgchart.tsx`, `site/components/board/BoardView.tsx`, `site/app/demand/page.tsx`, `site/app/curtailment/Sections.tsx`, `site/app/curtailment/page.tsx`, `site/app/events/page.tsx`, `site/app/network/Network.tsx`, `site/app/impact/page.tsx`, `tests/test_session241a.py`.
- This report.
