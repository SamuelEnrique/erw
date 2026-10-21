# Session 401 report: the five tool pages through the installed tools

21 October 2026, about 06:15 to 08:00 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-401` on `wip/401-s` (from `wip/381-382-land` at `df638a38`). Chain `queue/done/015-day-20-october-code-pm.md`, session 401; the roadmap's item 4 (Tooling). Model spend USD 0 (no call to the model API); no pull from any publisher (web-design-guidelines read its rules from the copy session 201 kept, not from GitHub); no warehouse data written.

## Read these first

- **The pass is `docs/reviews/tooling-pass-2026-10-20.md`**: Impeccable (critique as two agents, and its detector), UI/UX Pro Max, frontend-design, web-design-guidelines, react-best-practices and AccessLint, run on `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power` (and its Grid by grid view), `/research` and `/grid`, each finding with the tool that found it: what was fixed, what waits for your ruling (21 lines), what is session 412's (shared components, 10 lines), and the performance findings listed and not changed.
- **Every value unchanged**: 1,646 checked figures (823 at each width) read before and after the fixes at 1280 and 390 px, every key, raw value and text the same; `check-values` on `/cost-of-power` and `/grid`, exit 0, 2,589 of 2,589.
- **Fixed in the pages' own files only** (16 files under `site/app/cost-of-power`, `site/app/research`, `site/app/grid`): 24 px targets (the folds' summaries, a Reset link, the income table's two buttons, the research index, a Clear button), the Grid by grid tier tag at 12 px and square, square calculator fields, header cells with their scope in four hand-written tables, two selects named from their visible word, the pasted profile at 16 px on a phone, a live line announced, a hover on the duration links, no browser suggestions on 15 number fields, "(picked)" out of cardinal, air before "Your own inputs". No shared component and no `tokens.css` was touched (session 412's).
- **The one finding to read first**: Grid by grid's compute calculator writes "license needed MWh" for a figure the reader's own inputs produce (Impeccable A); first line of "For Samuel's ruling".
- **`docs/tooling.md`** has a new section, "First use of each tool": all seven first used on 12 October 2026 in session 201 (on the battery page); the first run on the five tool pages is this one. And how to run AccessLint on a page in review without the token in an address.

## What to review

- `https://github.com/SamuelEnrique/erw/blob/wip/401-s/docs/reviews/tooling-pass-2026-10-20.md`
- The shots, before and after: `https://github.com/SamuelEnrique/erw/tree/wip/401-s/docs/brand/review-401` (`<page>_<1280|390>_<before|after>.png`, the top of each page; `shots-401.mjs` took them and measured the pages)
- In the internal view after a landing: `/cost-of-power?view=grids` (the "derived" tags, the tables), `/cost-of-power/battery` (the income table's Table and Chart buttons, the storage-node fold), `/research` (the index links), `/cost-of-power/seller?asset=solar` (the profile box on a phone).

## Checks

Every gate redirected to a file under `runs/chain_oct21/s401/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `npm ci` in the worktree's `site/` (under the mutex) | 0 | |
| `npm run build`, before the fixes, first try | 1 | `next/font` could not reach Google Fonts (four "Failed to fetch"; no statement timeout); `curl` to the same host answered 200 a minute later |
| `npm run build`, before the fixes, second try | 0 | no statement timeout |
| `shots-401.mjs ... before` | 0 | 12 page reads, none in review, none "could not be read" |
| AccessLint `audit_live`, six addresses, before | (tool) | battery 1 serious; seller 1 serious, 1 minor; datacenter 1 serious, 3 minor; Grid by grid, Research, Grid none. All in shared components |
| `impeccable detect --json` on the three page folders | 2 | 2 findings, one rule (overused font: Inter in `app/research/card/render.css`, the social-picture frame): false positives for the pages |
| `impeccable detect --json` on the shared components (Assessment B) | 0 | none |
| UI/UX Pro Max search script, 12 queries | 0 each | |
| `npm run build` with the fixes | 0 | no timeout |
| `npm run build`, final (with the last three fixes) | 0 | no timeout |
| `shots-401.mjs ... after` (final build) | 0 | 1,646 figures compared, 0 pages differing |
| AccessLint `audit_live`, six addresses, after | (tool) | the same as before, finding for finding |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power,/grid` | 0 | 2,589 of 2,589 values match |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power,/research,/analysis,/grid` | 1 | 2,709 of 2,709 values match (`/research` 120 of 120); one FAIL: the floor of `/research/card/gas_sets_price`, 4 numbers where the floor is 6 (its ISO-NE callout is held from 21 October by `lib/license.ts`; the card page is not one of the five and did not change) |
| The first `check-values` call | 1 | Git Bash rewrote `/cost-of-power` into a Windows path, so those pages were not read; repeated with `MSYS_NO_PATHCONV=1` (the two lines above) |
| `tests.test_session401` | 0 | 10 tests |
| The 40 test modules that name a changed file | 0 | 653 tests OK, 20 skipped |
| Whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,792 tests, 252 skipped, 1 failure: `test_session156` (the ask fixtures), the failure the chain says may come tonight without a session's doing; nothing else |
| `duty.py beat` before each build | 0 | |

## Decisions made without you

1. **Fixes only in the pages' own files.** Session 412 fixes the shared components tonight on `wip/412-s`; every shared finding (the "i" button, the table that scrolls, the chart toggles, the menu, the research cards' small text, the grid's chips and swatches, the selects set in mono by `tokens.css`) is listed for 412 in the review, not fixed here.
2. **The performance findings were listed, not made.** The prompt's fixes are spacing, contrast, focus order and labels; several of react-best-practices' would start the live set's reads together on a night the database answered heavier reads with timeouts.
3. **Grid by grid's bars stay cardinal.** The brand gives the first series ink, but session 317's ruling kept the charts' props from the canvas; listed for your ruling.
4. **Impeccable's critique ran without its launcher, its overlay and its snapshot.** `impeccable context` may download a binary; the overlay needs a server and a browser of its own left running; the snapshot writes `.impeccable/`. Assessment A and B ran as two separate agents, as the playbook asks; A answered every question from `docs/brand.md`. Questions skipped: the session is unattended.
5. **chrome-devtools-mcp was not called**: the shots and measurements were taken over the same DevTools protocol by `site/scripts/browser.mjs`, which opens the internal view by the form. `docs/tooling.md` says so in its row.
6. **AccessLint on pages in review**: a headless browser on port 9222 opened the internal view by the form and `audit_live` was given that port; the browser was stopped after each round (`runs/chain_oct21/s401/chrome9222.mjs`).
7. **The pasted profile's field**: 16 px on a phone, and on a wider screen 12 px with the line height it had (the first try dropped the line height from 18 to 16 px and the seller page grew 10 px shorter; the measurement caught it and it was put back).
8. **The review file is named for 20 October** as the chain asks; the run was on 21 October UTC, which its first line says.

## For Samuel's ruling

- Grid by grid's calculator writes "license needed MWh" for the energy the reader's own inputs produce (`GridsView.tsx:215, 217`, key `cop|energy|...`), while the note under it prints 194,400 MWh: should a figure computed from the reader's inputs ever be held?
- On a phone the three calculators open with their whole form, the first answer about 1,800 to 2,150 px down: summary and headline first, the form folded, or as it is?
- Grid by grid's bars and points are all cardinal with nothing highlighted, and its monthly line does not break the 2021 spike: ink with cardinal for a highlight and a broken 2021, as the battery chart?
- Grid by grid's two tables list the ISOs in opposite orders, and one column holds "7.46 million" above "7,462,511".
- About twenty reasons, definitions and sources are only in a hover title (not reachable by keyboard or touch): give them a tip or a line?
- The Grid and Asset radios open a new page on change, so arrow keys load one page a step: keep, or open on Show?
- The "#financing" links land on a fold that starts closed and do not open it.
- The battery's box has the title "Assumptions" over a fold also called "Assumptions".
- "Show" names no result and nothing says the page is loading after it.
- "Reset" on Your load does not name what it resets (brand section 7).
- Empty table header cells over label and note columns (three tables): words, or a header only screen readers hear?
- Empty cells where the brand says "not held": the research rule's percentile and Grid by grid's cheapest-hours price.
- The research rule's percentile can read "1th", "2th", "3th", "22th" (`research/view.tsx:25`).
- Three empty-state lines on Research begin in lower case.
- "Method note" names two links on the datacenter page.
- The cost of power's tabs wrap to three lines each at 390 px.
- "Is it worth building?" and "Which option is better?" read as a judgment; the source footers name session numbers.
- The finding card's picture frame sets Inter where the brand names IBM Plex Sans (`app/research/card/render.css`).
- The datacenter page's notes run about 120 characters a line in places (brand: 68).
- Grid by grid's calculator keeps its inputs out of the address, has no reset, and its fields cannot be emptied to type.
- `LoadAnswers.tsx:183` reads the year from the browser's clock: server and browser can disagree on 1 January.

## Files

- `docs/reviews/tooling-pass-2026-10-20.md` (new), `docs/tooling.md` (a section), `docs/brand/review-401/` (24 shots and `shots-401.mjs`), `tests/test_session401.py` (new), this report.
- `site/app/cost-of-power/`: `GridsView.tsx`, `charts.tsx`, `LoadForm.tsx`, `LoadAnswers.tsx`, `page.tsx`; `battery/`: `BatteryForm.tsx`, `Income.tsx`, `Scenarios.tsx`, `Settings.tsx`, `page.tsx`; `seller/`: `SellerForm.tsx`, `SellerProfile.tsx`, `page.tsx`. `site/app/research/page.tsx`, `view.tsx`; `site/app/grid/page.tsx`.
- Raw outputs, not in git: `runs/chain_oct21/s401/` (the agents' four reviews, AccessLint's, the detector's, the searches, the measurements and full-page captures, every gate's output).
