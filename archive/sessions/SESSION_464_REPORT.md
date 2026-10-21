# Session 464 report: the battery calibrated against Modo Energy's ERCOT 2025 figures

21 October 2026, about 09:39 to 10:10 UTC, unattended, on portable-laptop (code role), in the worktree `C:\Users\samen\Documents\erw-464` on `wip/464-battery-modo` (from `origin/main` at `440a2c8f`, with `origin/wip/015-land` merged in). The chain of 21 to 22 October, night (`queue/done/019-night-21-october-code.md`, written for samueloldlaptop and taken by this machine's queue step). Model spend USD 0; no warehouse data written. Requests: 3 of 4, all to modoenergy.com, robots file and terms first.

## Read these first

- **Modo's 2025 figure was already on the page's note** (session 208, read 12 October: the 4-hour battery at USD 87 and 78 per kW against the fleet's 29.4). This session did not redo it. It sets the same figure beside the configuration closest to the fleet: 2 hours, the day-ahead schedule, the year 2025 at `HB_HUBAVG`.
  - That configuration earns **USD 56.01 per kW** (`series|price_years_by_window|ercot:HB_HUBAVG|battery_dayahead_2h_year_2025|2025-01-01T00:00:00Z`, read from the live set; the same to the cent from `battery_stack_monthly`). Against the fleet's 29.4 that is a gap of **+26.61**.
  - **The gap is the reserves.** The model's energy revenue alone is 29.94, within 0.54 of the fleet's whole revenue; its reserve revenue is 26.07.
- **Modo's June share was read here for the first time**: "ERCOT BESS earned 76% of revenue from energy arbitrage in June 2025, up from 25% a year earlier" (*How does a battery energy storage system make money?*, 19 May 2026).
  - The model's 2-hour share is 46.8 percent in June 2025 and 27.4 in June 2024. June 2024 agrees within 2.4 points; June 2025 is 29.2 points under.
  - The model's 8-hour battery, at 76.1 percent, matches the fleet's 76.
- **No figure on the page moves.** The method note gains two rows in "Cross-checks" and a section "Modo Energy's ERCOT 2025 figures, reconciled" (`#modo-2025`). The page's source line says "Checked against: 17 published figures" (15 before).
- **Not built.** The database gate was closed at every probe; the build, `check-values`, `check-cross-checks` and the after shots are under "To finish".

## What to review

- The note: `docs/methods/battery_earns_algorithm.md`, the last two rows of "Cross-checks" and the section after the table's notes. On GitHub: `https://github.com/SamuelEnrique/erw/blob/wip/464-battery-modo/docs/methods/battery_earns_algorithm.md#cross-checks`.
- After the landing: `https://erw-flame.vercel.app/data/methods/battery_earns_algorithm#modo-2025` and the source line of `https://erw-flame.vercel.app/cost-of-power/battery`.
- The shots: `docs/brand/review-464/` (before only; its README).

## Requests

| n | UTC | Address | Status | Purpose |
|---|---|---|---|---|
| 1 | 09:41 | `https://modoenergy.com/robots.txt` | 200 | the robots file, first: `Allow: /` for every client, ClaudeBot and anthropic-ai named |
| 2 | 09:42 | `https://modoenergy.com/website-terms-of-service` | 200 | the terms, before any research page: no sentence on automated reading; "You may not recirculate, redistribute or publish the analysis and presentation included in the Service without Modo's prior written consent" |
| 3 | 09:42 | `https://modoenergy.com/research/en/how-does-battery-energy-storage-make-money` | 200 | the June 2025 share (published 19 May 2026, from the page's own metadata) |

The fourth request was not spent: the nowcast's post was read by session 208 on 12 October and is quoted as it read it. The log is `runs/chain_019/s464/requests.csv` (git ignores `runs/`); the raw pages are beside it and are not in git.

## Checks

Every gate redirected to a file under `runs/chain_019/s464/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 464"` | 0 | passed. The duty mark is held by the main checkout's chain ("not marked again"), so this worktree did not mark it a second time |
| `tests.test_session464` (with `ERW_OUTPUT_DIR` at the main checkout's tables) | 0 | 8 tests OK. They check the 17 rows the page counts, the two rows' quotations, addresses and dates, and the earlier 15 rows in order. They recompute 56.01, 29.94, 26.07, 64.41 and the six June shares from `battery_stack_monthly`, and check for dashes |
| `tests.test_session464` against a copy with a dash planted and the count at 16 | 1 | 2 failures, as it should |
| The 19 tests that read the note or the page, and 464 (`test_session86`, `89_miso_pause`, `92`, `115_page`, `116_page`, `120_page`, `122`, `123`, `178`, `179`, `195`, `196`, `246`, `257`, `263`, `296`, `297`, `314`, `409`) | 0 | 339 tests OK, 35 skipped, under the build lock. A first run failed 3 of `test_session92`'s node tests: the worktree had no `site/content/docs.json` (the build writes it, git ignores it). Once `node scripts/build-content.mjs` wrote it, they pass, as they do in the main checkout |
| `scripts/db_probe.py` | 1 | at 10:01 UTC: 3.23 s against 3 s. No build |
| Before shots (`site/scripts/shot.mjs`, production, the internal view) | 0 | four PNGs at 1280 and 390 |
| Build, `check-values`, `check-cross-checks`, `check-methods`, after shots | not run | the database (above) |

## Decisions made without you

1. **Modo's 2025 nowcast was not read again.** Session 208 read it on 12 October and quoted it with its address. The chain's ceiling of 4 is better kept than spent re-reading a quoted sentence.
2. **Two rows, not one.** The chain names one figure from each of two Modo posts: the year's revenue at the fleet's duration and the June share. Each is its own comparison with its own gap, so the count went from 15 to 17.
3. **The rows are at the table's foot, after the Potomac Economics row.** Placing them beside session 208's Modo rows would have made the next row's "the same" refer to the 2-hour battery.
4. **The closest configuration is 2 hours on the day-ahead schedule.** Modo's fleet was mostly 1 and 2 hours (session 208's row), it settles without foresight, and the page offers no 1-hour battery. The hub stays `HB_HUBAVG`: the page holds no fleet-weighted node.
5. **The page's line names the new rows by count:** "and seven comparisons with published ERCOT battery figures", where it said "five published ERCOT battery revenues". `test_session196`'s pin follows (15 to 17).
6. **`origin/wip/015-land` was merged into this branch first**: it changes the note (session 409's subsection 4.12) and the page (one class). So this branch carries sessions 401 to 414 until they land.
7. **Read from the live set once**, two small filtered reads of `series` (the price-years rows and two June months), to cite the page's own key. The database was slow, but both reads answered.
8. **Modo's terms forbid redistributing its analysis**, so two quoted sentences with their sources are the whole of what the note holds of Modo's, as session 208 did. Nothing of theirs is saved in the repository.

## For Samuel's ruling

- **Modo Energy's rows, now four.** Its terms say "you may not recirculate, redistribute or publish the analysis and presentation included in the Service without Modo's prior written consent". The rows quote one sentence of each post, with its source, as a citation. Keep them as citations, ask Modo, or drop them (session 208's ruling 4, still open).
- **Whether the reconciliation earns a line on the page itself** ("the model is about twice the fleet at the fleet's duration; the difference is the reserves"), beside the source line. That is words on a page, not a figure; this session left the page as it was.

## To finish

In the worktree `C:\Users\samen\Documents\erw-464`, once `scripts/db_probe.py` exits 0. These are separate commands: the build never runs after a closed probe.

```bash
PY=/c/Users/samen/Documents/erw/.venv/Scripts/python.exe; L=/c/Users/samen/Documents/erw/runs/chain_019/buildlock.py
$PY scripts/db_probe.py; echo "exit=$?"            # 0 to go on
$PY $L acquire land; $PY scripts/duty.py beat
cmd //c rmdir site\\node_modules                  # the link only; Turbopack refuses a junction outside the root
cd site && npm ci > ../runs/chain_019/s464/npmci.out 2>&1; echo "exit=$?"
npm run build > ../runs/chain_019/s464/build.out 2>&1; echo "exit=$?"
npx next start -p 3464 &
MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/cost-of-power/battery node scripts/check-values.mjs http://localhost:3464 > ../runs/chain_019/s464/values.out 2>&1; echo "exit=$?"
node scripts/check-cross-checks.mjs http://localhost:3464 > ../runs/chain_019/s464/crosschecks.out 2>&1; echo "exit=$?"
node scripts/check-methods.mjs http://localhost:3464 > ../runs/chain_019/s464/methods.out 2>&1; echo "exit=$?"
for w in 1280 390; do MSYS_NO_PATHCONV=1 node scripts/shot.mjs "http://localhost:3464/data/methods/battery_earns_algorithm#modo-2025" ../docs/brand/review-464/after/note_modo_$w.png $w 1400; MSYS_NO_PATHCONV=1 node scripts/shot.mjs "http://localhost:3464/cost-of-power/battery" ../docs/brand/review-464/after/battery_$w.png $w 1400 "[data-checked-against]"; done
$PY $L release land
```

Then the chain's combined landing (session 461's second part): freeze status, merge origin/main, trial-merge the remote `task/` branches, snapshot before and after with every difference listed, push `task/`. If session 448's battery rows land too, the count is 17 plus theirs (10): 27.

## Files

- `docs/methods/battery_earns_algorithm.md` (two rows, one section).
- `site/app/cost-of-power/battery/page.tsx` (the source line's count and words).
- `tests/test_session196.py` (the count, 15 to 17), `tests/test_session464.py` (new).
- `docs/brand/review-464/` (README, four before shots).
- This report.
- Not in git: `runs/chain_019/s464/` (the requests log, the raw pages, the reads, the test outputs).
