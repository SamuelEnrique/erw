# Session 419 report: three faults of session 401's list that need no ruling

21 October 2026, about 13:30 to 14:30 UTC, unattended, on portable-laptop (code role), in the worktree `C:\Users\samen\Documents\erw-419` on `wip/419-faults` (from `origin/wip/461-combined` at `2289156d`, chain 019's prepared, unlanded branch, so that one landing takes both chains). The chain of 21 October, day (`queue/done/021-day-21-october-code.md`, session 419), written for samueloldlaptop and taken on this laptop by `chain_queue.py next` on the owner's instruction. Model spend USD 0; no warehouse data written; no request to any publisher. Built and checked locally (gate open at 2.62 s); not landed: no agent lands tonight (this machine's permission check refused an agent's landing).

## Read these first

- **The research rule's percentile is an ordinal.** `site/app/research/view.tsx` wrote "{n}th", so 1, 2, 3, 21, 22 and 23 would read "1th", "2th", "3th", "21th". It now calls `ordinal` from the new `site/lib/ordinal.ts` (pure, no imports): "1st", "2nd", "3rd", "11th", "12th", "13th", "21st", "22nd", "101st", "111th"; a decimal takes its last digit's suffix as written ("87.9th", "21.1st"). No week held today shows the fault (W39 to W41 hold 92.1, 100 and 87.9), so the page reads the same; the test proves the cases.
- **The carbon note's year comes from the page's own twelve months.** `LoadAnswers.tsx` (a client component) wrote "N months of {year} are held" from the browser's clock, so server and browser could disagree on 1 January. The answers now carry `through`, the last month of the twelve the server chose (`lib/datacenter/answers.ts`), and the note names that month's year (`yearOfThrough`); with no month it says only "A year's figure is the mean of its months held." No figure moved: the year is 2026 either way today.
- **A link to "#financing" opens the Financing fold.** The battery page's two links (under the settings and above "Is it worth building?") landed on a closed fold. `components/tool/OpenFoldOnHash.tsx` (client, draws nothing) opens the fold the address names, on load, on a hash change and when a link to the same hash is followed again; the logic is `lib/foldhash.ts` (pure). The fold still starts closed when the address names nothing.

## What to review

- The shots: `docs/brand/review-419/` (README), before from production, after from the local build, at 1280 and 390: `/research/2026-W41`, `/cost-of-power#clean`, `/cost-of-power/battery#financing` (closed before, open after).
- The code: commit `8abe6377`.

## Checks

Every gate redirected into `runs/chain_021/s419/` (git ignores `runs/`), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 419"` | 0 | every check passed |
| `node --import ./scripts/alias-register.mjs scripts/test-session419.mjs` | 0 | 28 of 28 |
| `tests.test_session419` | 0 | 5 tests OK |
| `tests.test_session419` against a copy with "{c.percentile}th" put back | 1 | fails, as it should |
| The tests that read the touched files (`test_session195`, `236`, `265`, `280`, `296`, `297`, `401`, `419`) | 0 | 98 tests OK |
| `scripts/db_probe.py` | 0 | open, 2.62 s (13:58 UTC); again inside the locked job, 0 |
| `npm run build` (under the build lock) | 0 | compiled; TypeScript finished with no error |
| `CHECK_VALUES_PAGES=/research,/cost-of-power node scripts/check-values.mjs` (restricted) | 1 | 1,526 of 1,526 values equal; the one failure is the floor of `/research/card/gas_sets_price` (4 checked numbers drawn, floor 6). The card shares no code with this session (no import of `research/view.tsx`, `lib/ordinal.ts`, `lib/foldhash.ts` or `lib/datacenter/answers.ts`); its two missing figures are of a held grid, one of the ten floors under the holds that session 408 listed ("4, floor 6; 2 held"), which chain 021's rules count as a pass |
| `scripts/shot.mjs`, 12 shots | 0 each | the after shot of `#financing` waited for `[data-settings-fold=financing][open]` |
| Impeccable | not run | not installed on this laptop |

## Decisions made without you

1. **One ordinal helper, new and pure** (`lib/ordinal.ts`), rather than importing `lib/datacenter.ts`' (integers only) into the research view: a percentile is often a decimal.
2. **A decimal's suffix follows its last written digit** ("21.1st", "99.9th"), as the ordinal is read aloud.
3. **The year is the page's last month of its twelve**, carried as an optional `through` on the answers' carbon (no other reader of `Carbon` changes); with none, the clause is left out rather than guessed.
4. **The fold opener is a shared client component mounted once on the battery page**, not a change to `SettingsFold`: the folds' own default (closed) is unchanged and other pages are untouched until a page mounts it.
5. **Stacked on `wip/461-combined`**, as the parent decided for chain 021.
6. **The page's wording is unchanged** but for the ordinal itself: "({ordinal} percentile)".

## For Samuel's ruling

- Whether other pages with links into closed folds should mount the same opener (none was named in session 401's list).

## To finish

- Land `wip/419-faults` with the night's combined landing (after `wip/461-combined`, which it contains): freeze status, merge origin/main, the suite, the build, full check-values, snapshots before and after, the push to a `task/` branch.

## Files

- `site/lib/ordinal.ts`, `site/lib/foldhash.ts`, `site/components/tool/OpenFoldOnHash.tsx`, `site/scripts/test-session419.mjs`, `tests/test_session419.py` (new).
- `site/app/research/view.tsx`, `site/app/cost-of-power/LoadAnswers.tsx`, `site/lib/datacenter/answers.ts`, `site/app/cost-of-power/battery/Settings.tsx` (changed).
- `docs/brand/review-419/` (12 shots and the README), this report.
- Not in git: `runs/chain_021/s419/` (the gates' outputs and the locked job's script).
