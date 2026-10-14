# Session 264 report: What a generator earns, deep

Chain of 14 October 2026, unattended, on the old laptop. Worktree `C:\Users\lossa\Documents\erw-188`, branch `wip/264-generator-pack` (from `afacb21e`). Model spend USD 0. No warehouse write, no request to a publisher.

## Read these first

- The review pack: `docs/reviews/packs/generator.md` (replaces the how-it-works note, which is `git rm`ed; the README row of `docs/howitworks/README.md` points at the pack).
- The owner's nine tasks for this tool, done on the page with no section added, moved or removed:
  1. The capture rate beside every capture price, from the same rows, with a check key: the summary sentence ("... below the flat average of USD 32.17: a capture rate of 72 percent.") and the headline ("..., a capture rate of 72 percent; real time, ...") carry `cap|<grid>|<hub>|<market>|<fuel>|l12|price, flat, rate`; a battery's and a peaker's headline, the income table and the revenue headline carry new `ms|iso=<grid>&...|<span>|<stat>` keys; the results row says "a capture rate of 72.3 percent of USD 32.17".
  2. "PPA term, years", the eleventh assumption (`y`, 1 to 40, whole, cut to the life; default the asset's life: 35, 30, 20, 30). The contract and the breakeven PPA price run for it; the debt keeps its own term. At the defaults no number moved.
  3. `check-seller.mjs` and `check-seller-face.mjs` moved to `site/scripts/_retired/` with a README (the `app/_retired` convention); the page's numbers are covered by `check-values` (234 keys on the four seller views, 179 before).
  4. The two CSV downloads follow the license verdicts: offered for ERCOT, CAISO and SPP (prices "may be public"); for a grid "license needed" on the day (ISO-NE and NYISO from 21 October) the links give way to the catalogue's words and the two addresses answer 403 with them; the every-hub table blanks such a grid's rows with the words in `note`. No license or verdict changed.
  5. Every check key names its grid; `check-values` refuses an `mr|` or `ms|` key without `iso=` (or naming a hub's model) and a `cap|` key whose grid the file does not hold.
  6. The edge cases tested tonight on a local build, internal view (pack part 5); a new guard line under "Your plant" says when a typed value was held at its bound (size, MWh, heat rate, variable O&M, battery size, and every scenario assumption).
  7. 21 published figures in the pack's cross-checks (Lazard, the ATB, EIA, CAISO's market monitor, Berkeley Lab); ERCOT's market monitor is not held (part 9).
  8. The replication files: at the page's defaults already; session 264 added the capture rate, the energy, the contract price for 1.25, NPV and the breakeven PPA price to the do-file and its mirror, which ran tonight and equal the page (72; 2,580; 39.14; -74.16 million; 58.36).
  9. `tests/test_session264.py`; the checks below.

## What to review

- `https://erw-flame.vercel.app/internal/open`, then:
- `https://erw-flame.vercel.app/cost-of-power/seller`: the sentence and the headline's capture rate (72); the eleventh field "PPA term" in scenario A and B.
- `https://erw-flame.vercel.app/cost-of-power/seller?bn=100&bp=58.36&by=20&v=b`: a 20-year PPA at the 35-year breakeven price.
- `https://erw-flame.vercel.app/cost-of-power/seller?mw=9999`: the line "Size, MW: 9,999 is above the bound of 5,000, so the page uses 5,000."
- `https://erw-flame.vercel.app/cost-of-power/seller?iso=caiso`: 13.86 against 28.53, a capture rate of 49 percent.
- `https://erw-flame.vercel.app/cost-of-power/seller?iso=nyiso&asset=solar`: a plant type with no data.

## Checks, with exit codes

Every gate run unpiped, its output in `C:/Users/lossa/Documents/erw/runs/session264/` (not in git). The final cycle on the code of `3f694726` plus the pack commits, under the build mutex 09:13 to 09:21 UTC.

| Check | Exit | Result |
|---|---|---|
| `npx tsc --noEmit` | 0 | twice (08:46, 09:13) |
| `npm run build` | 0 | twice; no "statement timeout" line |
| `check-values`, `CHECK_VALUES_PAGES=/cost-of-power/seller`, run 1 and run 2 | 0, 0 | 234 of 234 both times (179 before: 55 new `ms|` keys and the headline and sentence `cap|` keys) |
| `check-routes.mjs` | 0 | 1 live page and 203 in review asked as a visitor; 0 failed |
| `check-seller-scenarios.mjs` | 0 | 106 ok (a first run at 08:50 failed 7: the shared address and the PPA term inferred from the debt's, decision 2; fixed) |
| `check-seller-deeper.mjs` | 1 | stale since session 212 (session 235's report, item 3): its battery-beside rows read NaN (that section is in the CSV) and it crashes at its line 120. Not retired (not in the brief): pack part 9, question 4 |
| `node scripts/test-seller-finance.mjs` | 0 | all passed (with a session 264 block of 9 checks) |
| `runs/session264/edge.mjs` on the local build | 0 | the pack's part 5 |
| `runs/session264/profile_edges.mjs` | 0 | the capacity factors of part 5 |
| `python erw_2026_generator_replication.py` | 0 | equals the page: 59.85, 23.27, 32.17, 72, 7,078,769, 0.67, 2,580, 39.14, -74.16, 58.36 |
| The 33 test modules that read a changed file (`grep -l`), one run | 1, then 0 | 557 tests; one failure (`test_session260`: the pack lacked "adding the allowance waits for a ruling"), fixed; then 260, 262, 264 exit 0 and 249 exit 0 |
| No em dash in any file changed since `afacb21e` | none found | |
| The battery page unchanged | not owed | no shared component, `tokens.css` or `batterystack.ts` touched |
| Screenshots | not owed | the brief asks none |

## Decisions made without you

1. The PPA term's default is the asset's life (Lazard's economic life, the debt's own default term): no published PPA term is held in the repository, and the life is what every contract of this page ran for until today, so no default number moves. The reversible option. Its sensitivity step is 5 years, as the term's and the life's.
2. The PPA term is never inferred from the debt's term. A first version read an address with `at` and no `ay` as "PPA term = debt term" (to keep older links identical); the browser check showed a shared address then opened other numbers than the browser showed. Dropped: an older link that set a scenario's debt term and holds a contract now runs that contract for the life. Such links can only date from 12 or 13 October (contracts became scenario assumptions in session 212).
3. The capture rate in the sentence and the headline is the capture file's own whole percent (the key `cap|...|rate`), the figure the capture table writes; the results row keeps its one decimal (72.3) and now says "a capture rate of".
4. The profile box ("Your plant's own year") is not clamped: it takes no nameplate, so a value of 150 MW is not above any bound it knows; it refuses a value below zero and a year of the wrong length, as before. The bounded fields of "Your plant" and of the scenarios get the new line.
5. Retiring the two scripts by moving them to `site/scripts/_retired/` with a README, mirroring `site/app/_retired/`; four test pins (145, 162, 183, 195) moved to the new path with a note "session 264".
6. The downloads' license gate uses `licenseHeldGrid()` (the grid's prices), the rule the curtailment page and the price board use; the model's table `merchant_revenue_monthly` is held by grid (ISO-NE, MISO, NYISO).
7. The income table and the headline's spans carry keys only at the main hub (the snapshot `check-values` reads); at another hub they stay unkeyed as before.
8. `ms|` keys are recomputed in `check-values.mjs` by an independent reading of `lib/seller2.ts`'s rules (Node cannot import that file: it names `@/` paths), not by moving code.

## For Samuel's ruling

The pack's part 9, numbered with options: the CAISO peaker's carbon cost; the SunZia sentence; Berkeley Lab's terms; the retired scripts; the PPA term's default; a published ERCOT figure; solar degradation; the capture figures (`cap|`) of a "license needed" grid, which `components/Num.tsx` does not hold (a licensing change, not made unattended); CAISO's stress days and history.

## Pins moved (each with a note "session 264")

- `tests/test_session186.py`, `test_session196.py`, `test_session235.py`: eleven keys; the defaults line with `ppa: costs.life`.
- `tests/test_session183_replication.py`: the do-file's display lines 27 to 32, the mirror's 29 to 34.
- `tests/test_session145.py`, `test_session162.py`, `test_session183.py`, `test_session195.py`: the retired scripts' path.
- `tests/test_session257.py`: reads the pack where it read the old note.
- `site/scripts/test-seller-finance.mjs` and `check-seller-scenarios.mjs`: eleven assumptions, eleven bars with a contract, eight Lazard citations, "holds the others".

## The landing

filled by the orchestrator
