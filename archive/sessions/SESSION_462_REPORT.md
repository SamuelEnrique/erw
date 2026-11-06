# Session 462 report: the datacenter page's decisions block and method note

21 October 2026, about 09:06 to 09:35 UTC, unattended, on portable-laptop (the code role; the chain was written for samueloldlaptop and taken here by the queue), in the worktree `C:\Users\samen\Documents\erw-462` on `wip/462-463-cost` (from `origin/main` at `440a2c8f`, with `origin/wip/015-land` merged first). The chain `queue/done/019-night-21-october-code.md`, session 462. Model spend USD 0; no warehouse data written; no web request. Not landed: the parent lands the chain's branches together.

## Read these first

- **`/cost-of-power` has a "Decisions on this page" block at its foot**, closed to start, above the source line: 21 lines, one a modelling choice, each ending with the session that made it and the ruling where one exists. It is the grid page's form (session 299) and /impact's (session 347), made a shared component (`site/components/tool/DecisionsBlock.tsx`) that reads a list (`site/lib/decisions.ts`, `DATACENTER_DECISIONS`). Words only: no figure reads it and no number moved.
- **The step-by-step note has the same list as its section 12** (`docs/methods/datacenter_pays_algorithm.md`, "12. The decisions on the page (session 462)"), word for word, written from the site's file by script; the sign-off now names it. Two stale statements corrected: section 7 and `datacenter_cost.md` said the cost of capital's default is 8 percent (it is 9.6 since the owner's ruling of 11 October, session 196); `datacenter_cost.md` opens with what the page holds since session 213.
- **"Checked against" is 8 figures, from 6.** Two of session 448's rows (the third machine, `docs/reviews/cross-checks-external.md`, D2 and D3): the ATB's gas financing against the 9.6 percent, and the 20 years counted against Lazard's and the ATB's 30. Session 448's D1 (Lazard's own after-tax WACC of 7.7 percent) waits for Samuel's ruling on the default's label, as session 448 said. The three EIA retail rows now say the ERW holds the same figures (`eia_retail_electricity_prices`, July 2026: 70.7, 251.1, 108.1, read from this machine's table). The tariff tables give no published figure to compare: none is held.
- **Every figure was already keyed**: session 409's `check-methods.mjs` (offline, its keys file) 469 of 469, exit 0; the page gains no checked number.

## What to review

- After the landing: `https://erw-flame.vercel.app/cost-of-power`, the foot ("Decisions on this page"), and `/data/methods/datacenter_pays_algorithm#cross-checks`.
- The shots: `docs/brand/review-462/` (before on production, after on the local build, the block opened once; README).
- The code: `site/components/tool/DecisionsBlock.tsx`, `site/lib/decisions.ts`, `site/app/cost-of-power/page.tsx` (one import pair, one block).

## Checks

Every gate redirected to a file under `runs/chain_019/s462/` in the worktree, never piped; the exit code read before the next step. Heavy steps under the machine's build lock (`runs/chain_019/buildlock.py`).

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 462"` | 0 | every check passed |
| `tests.test_session462` with the 22 tests that read the page or its notes (138, 140, 149, 154, 154_page, 163, 190, 190_replication, 194, 195, 196, 199, 236, 257, 265, 280, 298, 317, 352, 354, 370, 401), first run | 1 | 1 failure: `test_session190` pins the note's section list; it now names section 12 |
| The same after that line | 0 | 402 tests (in two runs: the failing three again, OK) |
| `npx tsc --noEmit` | 2 | 13 errors, all Next's build-generated names (`PageProps`, `LayoutProps`) and build-time content files; none in this session's files |
| `scripts/db_probe.py`, start of the chain | 1 | 4.08 s (the parent's probe at 08:53 UTC) |
| `scripts/db_probe.py`, end of the session | 0 | 2.88 s, then 2.93 s |
| `npm run build` with the linked `node_modules` | 1 | Turbopack refuses a junction that points outside the root; `npm ci` in the worktree (exit 0) |
| `npm run build` | 0 | no statement timeout |
| `check-values.mjs` on the local build, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 1,406 of 1,406 values match Supabase (the four economics pages) |
| `check-cross-checks.mjs` on the local build | 0 | the three pages; `/cost-of-power` counts 8 and its note's table has the 8 rows |
| `check-methods.mjs` (offline) | 0 | 469 of 469 figures named |
| Impeccable | not run | not installed on this machine (`docs/tooling.md`: a third machine has none until session 201's installs are repeated) |

## Decisions made without you

1. **One shared component for the block**, in the grid page's form, the lines kept as data, so the page and its note say one list and a test holds them to it; the battery page (named in the chain as the form) has no such block at its foot, so the grid page's and /impact's form was taken.
2. **The block is on the "Your load" view only**, at the foot above the source line; the "Grid by grid" view is another tool's table and makes none of these choices.
3. **`origin/wip/015-land` merged into the branch before editing**: it changes `site/app/cost-of-power/page.tsx` and the shared components (sessions 401 to 414, not on main). The landing therefore carries it; it trial-merges into main with no conflict.
4. **Older tests follow**: `test_session196`'s count of the datacenter's rows (6 to 8) and `test_session190`'s list of the note's sections.
5. **D1 is not a row yet**, as session 448 wrote; D2 and D3 are.
6. **No new checked number**: the block's figures (9.6 percent, 1.3 kW, USD 1,000) are defaults the page already states with their sources.

## For Samuel's ruling

- Session 448's D1: keep 9.6 percent and say "pre-tax" in its label, or take Lazard's after-tax 7.7 percent (which moves every discounted figure).
- The note's sign-off block is still blank; signing now also accepts section 12.
- Whether "Decisions on this page" opens to start (it is closed, as on the grid page).

## To finish

- Lands with the chain's branches (the parent's landing): freeze status, snapshot before and after, `check-values` (full), check-routes.
- Impeccable `detect` on `site/components/tool/DecisionsBlock.tsx` and `site/app/cost-of-power/page.tsx` on a machine that has it.

## Files

- New: `site/components/tool/DecisionsBlock.tsx`, `site/lib/decisions.ts`, `tests/test_session462.py`, `docs/brand/review-462/` (6 PNG and a README), this report.
- Changed: `site/app/cost-of-power/page.tsx`, `docs/methods/datacenter_pays_algorithm.md`, `docs/methods/datacenter_cost.md`, `tests/test_session196.py`, `tests/test_session190.py`.
- Not in git: `runs/chain_019/s462/` (the outputs), `runs/chain_019/buildlock.py` and `shot-at.mjs` in the main checkout.
