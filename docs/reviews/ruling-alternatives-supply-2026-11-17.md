# Ruling alternatives: /supply (17 November 2026)

Session 7726 (samueloldlaptop, claimed in `docs/state/ruling_alternative_claims.md`). For each line of `docs/reviews/ruling-impact-supply-2026-11-17.md` whose change is 1 percent or more, or that adds or removes a figure, the other choice is built on its own branch from origin/main, with a test that pins the figure under it. The branch number is the line's number in the impact file. No branch asks to land; no default on main changed; no hold was lifted. This machine cannot build the site: each branch is held by its tests (the page's own library on its committed file, `site/data/supply.json`, rebuilt 17 November 2026 08:45 UTC, after the impact file's copy of 04:51) and has one row in `docs/state/browser_reads_wanted.md` for its screenshot at 1280.

- **No model call** was made (spend USD 0).
- **Line 4 is not built:** the ask panel's licence hold moves no figure on this build (the builder's fix of request 154 already writes no value for NYISO's, ISO-NE's or PJM's cleared rows), and the panel answers only with the key.
- **Known failure, not this work's:** `site/scripts/test-supply-read.mjs` row 1 ("NYISO's cleared table is held on the day") fails the same on main's code with today's file, as that file now carries no value for the held rows.
- **The burn rows of MISO, NYISO and ISO-NE** are EIA-930's (derived from its hourly generation), which the page draws on main; drawing them in an A and B lifts no hold.
- **Order by size:** line 1 (removes the list's first line), line 2 (a second column), line 3 (seven cells added).

## Decisions made without Samuel

- Line 1: the floor is 0.05 Bcf a day, stated for that unit only (a share of each series' own five-year average leaves nothing out).

| # | Line | Branch | Figure, main's rule | Figure, the other choice | Files touched | Test | Browser row |
|---|---|---|---|---|---|---|---|
| 1 | Leave out of "Changes outside the five years' range" a series whose latest value is below a stated floor | `wip/alt-supply-1` (`034178a98`) | Every series ranked: 21 lines, led by "LNG exports, every other point of exit together, monthly" (latest 0.004 Bcf a day, 31.76 of its near-zero ranges out) | A floor of 0.05 Bcf a day leaves that line out: 20 lines, led by US distillate stocks (103.33 million bbl); the heading says the floor and why on hover. Computed with the page's own library on the committed file | `site/lib/supply.ts` (`SURPRISE_FLOOR`, `belowFloor`, in `surprises`), `site/app/supply/page.tsx` (the heading), `site/scripts/test-supply.mjs` (the surprises test held to the other choice), `site/scripts/alt-supply-figures.mjs`, `tests/test_alt_supply_1.py` | `tests/test_alt_supply_1.py`, 2 of 2; the six test files that name the page, 76 tests, pass; `test-supply.mjs` passes; the read test fails the same as on main (the head); no new type error | 364 |
