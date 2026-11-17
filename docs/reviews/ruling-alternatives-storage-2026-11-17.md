# Ruling alternatives: /storage (17 November 2026)

Session 7727 (samueloldlaptop, claimed in `docs/state/ruling_alternative_claims.md`). For each line of `docs/reviews/ruling-impact-storage-2026-11-17.md` whose change is 1 percent or more, or that adds or removes a figure, the other choice is built on its own branch from origin/main, with a test that pins the figure under it. The branch number is the line's number in the impact file. No branch asks to land; no default on main changed. This machine cannot build the site: the branch is held by its tests (the page's own function on the local table) and has one row in `docs/state/browser_reads_wanted.md` for its screenshot at 1280.

- **The table is public:** `storage_daily_cycle` (EIA-930's battery net generation and CAISO's own batteries, derived), as this machine holds it, to 7 October 2026; its newest whole month here is September 2026. On the site the month is the newest the live set holds whole.
- **No model call** was made (spend USD 0).

| # | Line | Branch | Figure, main's rule | Figure, the other choice | Files touched | Test | Browser row |
|---|---|---|---|---|---|---|---|
| 1 | Give the daily cycle a month's total discharge by grid (ERCOT's October 2026, for one) beside the newest day and the 30-day spark | `wip/alt-storage-1` (`e5c266321`) | The panel: the newest complete local day and the 30-day spark (ERCOT 28,606 MWh on 6 October; 767,302 over the 30 days to it, on this machine's copy) | A column "Discharged, newest whole month": each grid's newest calendar month whose every local day is held, summed, with its days and its daily mean on hover; a month with a day missing is not summed. On this machine's copy, September 2026: CAISO 1,335,586 MWh (44,520 a day), ERCOT 787,056 (26,235), SPP 31,766 (1,059); August 2026: 1,462,303, 796,960 and 33,939. On the site, October 2026. A figure added a grid; none that stands moves. Computed with the page's own function, as the impact file has them | `site/lib/storagemonth.ts` (`monthTotal`), `site/app/storage/page.tsx` (the column and its hover), `site/scripts/alt-storage-figures.mjs`, `tests/test_alt_storage_1.py` | `tests/test_alt_storage_1.py`, 2 of 2 with the table (1 without); the 12 test files that name the page, 227 tests: one failure, `test_session148`, which fails the same on clean origin/main; the read test 25 of 25; no new type error | 363 |

## Browser reads of chain 401 (lab-desktop, 17 November 2026)

Faults seen on a build of a branch, from `docs/state/browser_reads_wanted.md`; none is fixed here.

- Browser row 363 (session 7800): `wip/alt-storage-1` (browser row 363): the column "Discharged, newest whole month" reads "no whole month" for all six rows on a build reading the live set of 17 November, where the record expects October 2026's totals; the live set's `storage_daily_cycle` appears to hold no calendar month whole for any grid.
