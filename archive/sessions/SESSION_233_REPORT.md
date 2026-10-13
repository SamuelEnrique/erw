# Session 233 report: the weekly hunt for deeper findings

13 October 2026, 04:55 to 05:25 UTC (the night of 12 October, Pacific), unattended, on lab-desktop (the data machine), the last session of the chain of 12 October, night. Branch `task/233-weekly-hunt`. Model spend USD 0: no model call, and none in what was built. Writes: migration 031 applied to Supabase under the data lock, and 8 drafts added to the review list; no warehouse table.

## Read these first

- **The hunt runs by itself every Saturday at 12:00 local time on this machine and ran once tonight: 8 drafts wait at `/internal/findings`, beside the scanner's 8.** Nothing is published: each draft is a draft until you approve it there.
- **The top three, all ERCOT:**
  1. The day's dearest hour falls in the evening: 71.0 percent of days in 2025, up from 24.9 percent in 2019. The direction holds in 6 of the 6 full years after 2019.
  2. Hours with a price below zero, ERCOT South: 2.68 percent of hours in 2025, up from 0.61 percent in 2019. 6 of 6 years.
  3. The day's dearest hour falls at midday: 3.8 percent of days in 2025, down from 32.9 percent in 2019. 5 of 6 years.
- **Every draft today is ERCOT's.** The library asked 36 claims of five grids and six ERCOT hubs. CAISO has one full year in these findings' tables (it begins September 2024), so no CAISO claim can be tested yet. ISO-NE, NYISO and SPP are never drafted: their publishers need a license or are held by your ruling.
- **The library is seven patterns from four of the findings, not all ten.** A pattern here is a measure by region and by year. Queue outcomes, the event flips, the two curtailment regressions and the impact study are other kinds of claim; their tests are not written, and `hunt.py` says why for each. I did not stretch the three tests over claims they do not fit.
- **Each draft carries what you asked for:** its chart, numbers, CSV, a Stata do-file, a Python mirror, the two LinkedIn pictures (1200 by 627 and 1080 by 1080) and a caption computed from the numbers. The page shows the three tests, the files, the pictures and the caption, and posts nothing. **The do-files were not run: there is no Stata on this machine.** The Python mirror was run on a draft's own CSV in the tests.
- **An approved draft can now be chosen for the Roundup from the review page** ("Use in Roundup" appears once a draft is approved). This closes the gap session 231 found.
- **Sessions 231 and 232 landed:** pushed at 04:52:26 UTC (`aa9aa92a`), check run 38348564176 passed, merged into `main` as `fa58e572` at 04:58:06, deployed 04:59:42. Before snapshot `s231-before` (04:52:13, 25 pages, 0 failed); after snapshot `s233-before` (05:12:46, 25 pages, 0 failed); `compare`: 0 differences in all, as expected. (A first after snapshot, `s231-after`, was taken at 04:58:22, before the deploy had finished; it also showed 0 differences and proves nothing, so the later one is the one that counts.)

## The library

| Pattern | The measure, by year | Finding it runs | Regions |
|---|---|---|---|
| `spikes_against_median` | the year's dearest interval as a multiple of the year's median real-time price | `batteries_lunch` | each of ERCOT's six hubs |
| `spikes_against_median_grids` | the same | `batteries_lunch_grids` | each grid |
| `hours_above_1000` | hours at USD 1,000 per MWh or more | `batteries_lunch_grids` | each grid |
| `gas_sets_price` | share of hours priced below a 7.0 heat rate times Henry Hub | `gas_sets_price` | each grid |
| `negative_prices` | share of hours with a price below zero | `negative_prices_west` | each hub |
| `peak_hour_evening` | share of days whose dearest hour fell in the evening | `peak_hour_grids` | each grid |
| `peak_hour_midday` | share of days whose dearest hour fell at midday | `peak_hour_grids` | each grid |

- **The claim:** the last full year against the first full year, one region.
- **Test 1, more than one year:** at least two full years after the first lie on the claim's side of the first year's value.
- **Test 2, another window:** the direction is the same starting a year later and ending a year earlier (four full years needed).
- **Test 3, the sample:** the two end years each hold at least the pattern's floor of observations.
- **New or changed:** not drafted before for that region, or a newer last full year, or the change moved past the pattern's threshold. Strongest first; at most two regions of a pattern and twelve drafts a hunt; the same numbers under two patterns are drafted once.
- **Not patterns yet** (`NOT_YET` in `hunt.py`): `queue_divorce` (a level by technology over one cohort), `who_rescues_whom` (one event is one episode), `batteries_curtailment` and `batteries_curtailment_hourly` (regression coefficients), `peak_hour_moved` (covered by `peak_hour_grids`), `impact_study` (needs an event a person chooses).

## Tonight's hunt: 36 claims

| Outcome | Count | Which |
|---|---|---|
| Drafted | 8 | the three above; negative prices, ERCOT North (0.57 to 2.56 percent of hours); the worst spike against the median at HB_WEST (128.7 to 13.2 times), HB_SOUTH (123.6 to 13.7) and ERCOT's hub average (126.6 to 12.1); hours at USD 1,000 or more, ERCOT (26.2 to 2.2 hours) |
| Passed, not drafted | 5 | beyond the two strongest regions of their pattern (ERCOT Houston's negative prices; three more ERCOT hubs' spikes), or the same numbers as a draft (the hub average, read by two patterns) |
| Failed a test | 2 | ERCOT West's negative prices and ERCOT's gas share: both turn when the window moves a year |
| No claim | 5 | CAISO in five patterns: fewer than two full years |
| Never drafted | 16 | ISO-NE, NYISO and SPP in every pattern |

- The spike drafts and the USD 1,000 draft are weak by the hunt's own measure: the change is about half a typical year-to-year move of a very jumpy measure (strength 0.4 to 0.5, against 2.6 to 3.4 for the first four). They pass the three tests you named, so they were drafted. A floor on strength is under "For Samuel's ruling".
- Everything computed, with each claim's reason, is in `runs/hunt/2026-10-13/hunt.json` on this machine.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python -m unittest tests.test_session233 tests.test_session232 tests.test_session231` | 0 | 73 tests |
| `python -m unittest discover -s tests` | 1 | 3,650 tests, 3 failures, the same three as in session 232 and none in what this chain touched: `test_session51`, `test_session125`, `test_session165` compare tables on this machine with committed files and are skipped on GitHub's runner |
| `apply.py --only 031`, under `lock.py run` | 0 | applied 05:00 UTC |
| `verify_rls.py --catalog` | 0 | PASS, 0 mismatches; `scanner_draft_file` refused without the token |
| `hunt.py --dry-run`, then `hunt.py --weekly` | 0, 0 | about two minutes each; 8 drafts added |
| `npm run build` (site), `eslint` on the changed files | 0, 0 | `/internal/findings/file` is in the build |
| `register_weekly_hunt.ps1` | 0 | task "ERW weekly hunt", Ready, next run Saturday 17 October 12:00 local |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **The hunt's drafts go in the scanner's review list** (rule `hunt`), so one page holds everything that waits for you. Migration 031 adds the rule, a `files` column the list does not return, and one read-only function for a file.
2. **Only regions of publishers with a public license are drafted:** not ISO-NE, MISO or NYISO ("license needed"), not NYISO or SPP (held). The findings still read those tables to compute; nothing of them is in a draft.
3. **A draft's source line names its own grid's tables,** not every table the finding read.
4. **Caps:** two regions a pattern, twelve drafts a hunt. Without them tonight's list would have been six near-identical ERCOT hubs.
5. **Saturday at 12:00 local time:** after this machine's daily run, a day and a half before the Sunday Roundup.
6. **The task was registered without elevation,** so it runs only while the account `Shared` is logged on (this shell is not an administrator's). It catches up a missed Saturday when the machine is next on.
7. **The hunt writes no health row and sends no email.** A weekly step in the health table could change how green days are counted, which is the launch gate.
8. **I replaced my own first load of the 8 drafts twice** (a wording fix, then a picture fix) before anyone had ruled on them: deleted and loaded again under the same ids. The scanner's 8 drafts were not touched.
9. **One pinned test was widened:** `tests/test_session177.py` lists the read functions `verify_rls.py` may call; `scanner_draft_file` (a read) joined the list, as session 181's two did.
10. **The proof of the page on the live site is in the closing message,** after the deploy.

## For Samuel's ruling

1. **Run this script once from an elevated PowerShell** so the Saturday task runs with nobody logged on: `powershell -ExecutionPolicy Bypass -File scripts\register_weekly_hunt.ps1`.
2. **A floor on strength?** For example, draft only a change of at least one typical year-to-year move. Tonight that would keep the first four drafts and drop the four spike ones.
3. **Which of the other findings should become patterns first,** and what "holds in more than one year" should mean for an event (`who_rescues_whom`) and for a regression coefficient (the curtailment findings).
4. **The do-files need one run in Stata** before you rely on them: the import line reads the variable names from the CSV's fifth line (four comment lines above it).
5. **A line by email when the hunt has drafts?** Today you learn of them by opening the page.
6. The 16 drafts now waiting (8 of the scanner, 8 of the hunt).

## Files

- New: `warehouse/analysis/findings/hunt.py`, `warehouse/supabase/migrations/031_hunt_drafts.sql`, `warehouse/supabase/rollbacks/031_hunt_drafts.sql`, `site/app/internal/findings/file/route.ts`, `scripts/register_weekly_hunt.ps1`, `scripts/unregister_weekly_hunt.ps1`, `tests/test_session233.py`.
- Changed: `warehouse/analysis/findings/card_image.py` (years on the axis, the title clear of the mark), `site/app/internal/findings/page.tsx` (the hunt's tests, files, pictures and caption), `site/components/analysis/DraftReview.tsx` ("Use in Roundup"), `site/components/analysis/FindingCard.tsx` (one word), `site/lib/scanner.ts`, `site/lib/findings.ts`, `tests/test_session177.py` (one more read function allowed), `warehouse/supabase/verify_rls.py`, `warehouse/supabase/README.md`, `docs/methods/automated_analysis_findings.md`.
- On this machine, not in git: `runs/hunt/2026-10-13/` (the hunt's summary, every draft's card and six files), `runs/hunt/state.json` (the memory), `runs/weekly_hunt.log` (from Saturday), `runs/session233/`.

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Before snapshot `s233-before` (05:12:46 UTC, 25 pages, 0 failed), then the push. The check run, the after snapshot and the comparison are in the chain's closing message: this is the chain's last session. Expected: 0 differences on the 25 pages (`/internal/findings` is internal; the three live pages read none of what changed).
