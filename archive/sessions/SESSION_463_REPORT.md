# Session 463 report: the generator page's decisions block, method note and replication

21 October 2026, about 09:36 to 09:55 UTC, unattended, on portable-laptop (the code role; the chain was written for samueloldlaptop and taken here by the queue), in the worktree `C:\Users\samen\Documents\erw-462` on `wip/462-463-cost`, after session 462. The chain `queue/done/019-night-21-october-code.md`, session 463. Model spend USD 0; no warehouse data written; no web request. Not landed: the parent lands the chain's branches together.

## Read these first

- **`/cost-of-power/seller` has the "Decisions on this page" block at its foot** (session 462's shared component, `data-decisions="463"`), between the sensitivity chart and the source line: 23 lines, each with the session that made the choice and the ruling where one exists (`site/lib/decisions.ts`, `GENERATOR_DECISIONS`). Session 298's sentence in the source line stays. No number moved.
- **The step-by-step note has the same list as section 13**, word for word, and **a sign-off block**, which the generator pack (session 381) named as missing: what signing accepts, and blank lines for the name, the date and the items ruled (`docs/methods/generator_earns_algorithm.md`). Section 7 now says what the scenarios hold since sessions 212, 298 and 353 (it said "no degradation" and named the contract panel gone since 212); section 8 says the NPV is USD -76.66 million since ruling 7a (it said -74.16) and how a reader runs the replication.
- **"Checked against" is 34 figures, from 21**: session 448's thirteen rows (Lazard's June 2025 report and the ATB 2025, read by the third machine on 21 October), inserted before the ten CAISO rows, which session 257 keeps last. Every source is linked with its page.
- **The replication against today's page.** The mirror, run from `site/public/seller/` with `python -I` (the three downloads, the standard library, nothing else): exit 0, 34 lines. Against the page as built at about 09:47 UTC, figure for figure: revenue over the last twelve months USD 59.85 per kW (page 59.85, `ms|...|twelve|revenue`); the 2023 to 2025 average 102.24 (102.24); every full year 130.80 (130.80); energy 2,580 MWh per MW (2,580); the price received 23.27 (23.27, `cap|ercot|HB_HUBAVG|rt|solar|l12|price`), the flat average 32.17 (32.17) and the capture rate 72 (72); debt payments 7,078,769 (7.08 million); coverage 0.67 (0.67); the contract price for 1.25 times 39.14 (39.14), NPV at 12 percent USD -76.66 million (-76.66) and the breakeven PPA price 58.36 (58.36), the last three as `check-seller-scenarios.mjs` read them. Every figure equal. The CSV is the model's snapshot of 4 October, which the page still reads.

## What to review

- After the landing: `https://erw-flame.vercel.app/cost-of-power/seller`, the foot, and `/data/methods/generator_earns_algorithm#cross-checks`, sections 7, 8, 13 and "Sign-off".
- The shots: `docs/brand/review-463/` (before on production, after on the local build, the block opened once; README).

## Checks

Every gate redirected to a file under `runs/chain_019/s463/` in the worktree, never piped; the exit code read before the next step. Heavy steps under the machine's build lock.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 463"` | 0 | passed; the duty mark is the main checkout's (a worktree holds no token), said by the precheck |
| `tests.test_session463` with 22 tests that read the page, its note or its pack (107, 120_page, 122, 123, 145, 162, 183, 183_replication, 186, 190, 195, 196, 235, 253, 257, 260, 264, 273, 298, 352, 353, 401) and 462, first run | 1 | 3 failures, 1 error: `test_session253` and `test_session257` pin the count 21 and the CAISO rows' place; `test_session273` failed to import scipy in that run |
| 253, 257 and 463 after they follow | 0 | OK |
| `test_session273` alone | 0 | OK: the import error did not recur |
| `scripts/db_probe.py` before the build | 1 | 3.18 s, closed by 0.18 s. **The build ran anyway**: it was chained in the same command line as the probe, my error. It passed with no statement timeout |
| `npm run build` | 0 | |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 1,406 of 1,406 |
| `check-cross-checks.mjs` | 0 | the seller page counts 34 and its note's table has 34 rows; the other two pages as before |
| `check-seller-scenarios.mjs` | 0 | all passed: every default as it was, NPV USD -76.66 million |
| The mirror, `python -I erw_2026_generator_replication.py` in `site/public/seller/` | 0 | the figures above |
| `scripts/db_probe.py` at the end | 1 | 3.66 s |
| Impeccable | not run | not installed on this machine |

## Decisions made without you

1. **Thirteen rows inserted before CAISO's ten**, not appended, so that session 257's rule (the ten last) holds; `test_session257` reads the ten from row 25 now, `test_session196`, `253`, `298` and the pack's demo line count 34.
2. **The sign-off block written as the datacenter note's**: what signing accepts, three blank lines; it accepts section 13 too.
3. **"Run it" is the reader's own folder of the three downloads**, as session 381 framed a replication a reader can run; no new file, since the mirror already needs nothing else.
4. **The battery's degradation line names session 196**, which set Lazard's 2.6 percent (the git history), and MISO's line the pause of session 89.
5. **The build that ran on a closed probe was kept**: it passed, its checks read Supabase directly, and nothing was loaded or deployed.

## For Samuel's ruling

- The note's sign-off: sign it, or name what to change.
- The replication's CSV is the snapshot of 4 October; a newer snapshot needs the data machine's export (`warehouse/derived/generator_hourly_export.py`), and the test `tests/test_session183_replication.py` says when.

## To finish

- Lands with the chain's branches (the parent's landing): freeze status, snapshot before and after, `check-values` (full), check-routes.
- Impeccable `detect` on `site/app/cost-of-power/seller/page.tsx` on a machine that has it.

## Files

- New: `tests/test_session463.py`, `docs/brand/review-463/` (5 PNG and a README), this report.
- Changed: `site/lib/decisions.ts` (the generator's list), `site/app/cost-of-power/seller/page.tsx`, `docs/methods/generator_earns_algorithm.md`, `docs/reviews/packs/generator.md` (the demo's count), `tests/test_session196.py`, `test_session253.py`, `test_session257.py`, `test_session298.py`.
- Not in git: `runs/chain_019/s463/`.
