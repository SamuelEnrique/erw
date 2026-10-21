# Session 541 report: the brand rules session 401 found broken

21 October 2026, about 20:09 to 20:45 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-541` on `wip/541-s` (from `origin/main` at `2ecba09d`). Chain `queue/done/024-night-21-october-code.md`, session 541. Model spend USD 0; no pull from any publisher; no warehouse data written; `site/lib/release.ts`, `tokens.css` and every shared component untouched.

## Read these first

- **Four items of session 401's "For Samuel's ruling" were named; `docs/brand.md` decides two of them, and only those two were made.** Each item, the brand's words, and what was done:

| Item (session 401) | What `docs/brand.md` says | Done |
|---|---|---|
| Three empty-state lines on Research begin in lower case (`research/page.tsx`: "no card yet", "no daily chart is held yet", "no week has been analysed yet") | Section 1, Type: "Labels are in sentence case. No capitals by style, no letter-spacing." | Made: "No card yet: ...", "No daily chart is held yet ...", "No week has been analysed yet ...". The rest of each line is unchanged |
| "Reset" on Your load does not say what it resets (`cost-of-power/LoadForm.tsx`) | Section 7, Assumptions: an assumption "can be put back with one press, named for its field ("Reset capital cost")." | Made: "Reset your load". The link puts back the same five values as before; its 24 px target (session 401) is unchanged; it carries `data-load-reset="1"` for the shots and the test |
| "Method note" names two links on the datacenter page (`cost-of-power/page.tsx`, the lead and the source line) | Nothing. The brand has no rule on a link's name (section 2 says a link in running text is underlined; section 7 names a reset, not a link) | Not made; left on the ruling list. Both links go to the one address, `/data/methods/datacenter_cost` (read on the built page, before and after), so a name that "says where it goes" would be the same name twice |
| The battery's box titled "Assumptions" over a fold also called "Assumptions" (`battery/Settings.tsx`) | Nothing. Section 7 says what an assumption shows (its default, its source, a reset); no rule speaks to a title repeated by the fold under it | Not made; left on the ruling list. Renaming either is a choice of words (CLAUDE.md: a tool's findings on words go under "For Samuel's ruling") |

- **No figure moved**: 1,002 checked figures (`data-check`, `data-raw` and the text shown) of `/research` and `/cost-of-power`, read on the built site before and after at 1280 and 390 px, are the same, page for page (`runs/chain_024/s541/compare.out`). `check-values` on the two pages: 1,526 of 1,526 values match; its one FAIL is the held floor of `/research/card/gas_sets_price` (on session 408's list, expected).
- **The empty-state lines do not show on this build**: Research holds cards, 19 daily charts and 3 weeks, so none of the three lines renders; the shots show where the lines stand (the library and the archive), and the test holds the words in the source.
- **Not touched, as the chain says**: the ordinal, the browser's clock and the financing fold (chain 021's session 419, `wip/419-faults`, which edits `battery/Settings.tsx`; this session does not).

## What to review

- The shots, before and after: `https://github.com/SamuelEnrique/erw/tree/wip/541-s/docs/brand/review-541` (`<name>_<1280|390>_<before|after>.png`: `cost-of-power-load` with the Reset link in the middle of the window, `research-library` and `research-archive`; `shots-541.mjs` took them and read the figures). Each PNG was looked at: the load shots show "Reset" before and "Reset your load" after beside Show, the rest of the form unchanged at both widths.
- In the internal view after a landing: `/cost-of-power` (Your load, the link beside Show).
- The diff: `site/app/research/page.tsx` (three words), `site/app/cost-of-power/LoadForm.tsx` (one link).

## Checks

Every gate redirected to a file under `runs/chain_024/s541/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 541"` | 0 | on duty |
| `scripts/db_probe.py`, before each build | 0, 0 | open |
| `duty.py beat`, before each build | 0, 0 | |
| `npm ci` in the worktree's `site/` (under the mutex) | 0 | |
| `npm run build`, before the change | 0 | no statement timeout |
| `shots-541.mjs ... before` | 0 | 6 page reads, none in review, none "could not be read" |
| `npm run build`, after the change | 0 | no statement timeout |
| `shots-541.mjs ... after` | 0 | 6 page reads, none in review, none "could not be read" |
| The figures compared, before against after | 0 | 1,002 figures, 0 pages differing |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power,/research`, `MSYS_NO_PATHCONV=1` | 1 | 1,526 of 1,526 values match; one FAIL, the floor of `/research/card/gas_sets_price` (4 numbers where the floor is 6: its ISO-NE callout is held by `lib/license.ts` since 21 October, session 408's list); no floor lowered |
| `impeccable detect --json` on the two changed files | 0 | `[]` |
| `tests.test_session541`, `test_session401`, `test_session296`, `test_session190`, `test_session194` | 0 | 71 tests, 1 skipped (the report test, before this file) |
| The 14 test modules that name `LoadForm` or Research's `page.tsx` | 0 | 284 tests, 4 skipped |
| Whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 5,244 tests, 268 skipped, 2 failures, neither caused here (this session's diff is the two page files and the tests): `test_session156` (the known one: its node tests end `TypeError: Cannot read properties of undefined (reading 'day')`), and `test_session153`, whose node script `site/scripts/test-ask-tables.mjs` stops on `Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@/data' imported from site/lib/chat/pagefiles.ts` (main's file, untouched here; the same family as the page-file tests of 21 October). Named, not fixed |

The build mutex (`runs/build.lock`) was held from `npm ci` to the end of the second server and released; the server on port 3541 was stopped after each round of shots.

## Decisions made without you

1. **Two of the four items were left for your ruling**, because `docs/brand.md` does not decide them and the chain's part says an item the brand does not decide stays on the ruling list. The datacenter page's two "Method note" links lead to the same page, so naming each for where it goes gives one name twice; the battery's repeated "Assumptions" is a choice of words.
2. **"Reset your load"**, not "Reset all" or "Reset the load": the panel is "Your load" on the page's own view tabs and in its notes, and section 7's example names the thing put back ("Reset capital cost"). The link resets the panel's fields (power, how it runs, how it buys) and the address's power per GPU and overhead ratio, as before.
3. **Only the first letter of each Research line changed**; the lines' paths (`data/findings/`, `docs/digest/charts/`, `docs/analysis/`) stay as written.
4. **Session 401's test updated, not removed**: `tests/test_session401.py` pinned the link's old text; its line now pins the new text with the same class (the 24 px target), with a comment naming this session.
5. **Region shots, not top-of-page shots**: the changed link sits about one screen down; each shot puts the changed line (or where it would stand) in the middle of the window.

## For Samuel's ruling

- "Method note" names two links on the datacenter page (`/cost-of-power`: the lead and the source line), both to `/data/methods/datacenter_cost`: keep one, or name them apart? docs/brand.md has no rule on a link's name.
- The battery's box is titled "Assumptions" over a fold also called "Assumptions" (`battery/Settings.tsx`): rename the box, the fold, or neither? docs/brand.md does not decide a repeated title.

## Files

- `site/app/research/page.tsx`, `site/app/cost-of-power/LoadForm.tsx` (the two fixes).
- `tests/test_session541.py` (new), `tests/test_session401.py` (one line, the Reset link's new name).
- `docs/brand/review-541/` (12 shots and `shots-541.mjs`), this report.
- Raw outputs, not in git: `runs/chain_024/s541/` (every gate's output, the measurements before and after, the comparison).
