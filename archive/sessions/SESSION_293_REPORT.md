# Session 293 report: the problem sets for a class

15 October 2026, unattended, on samueloldlaptop (the code machine), the sixth session of the afternoon chain. Branch `wip/games-v2`, pushed, **not landed**. Model spend USD 0. No pull from a publisher; the edition read the ERW live set (Supabase) once, read only. No warehouse data written.

## Read these first

- **Each set now comes two ways** (ruling 8a): the live set, rebuilt from the newest data as before, and a **dated edition** whose numbers do not move. The first edition is of **15 October 2026** (read 00:17 UTC), all five sets.
- **An edition has a students' copy without answers** (`/learn/problems/<set>/2026-10-15`) **and a teacher's copy with every answer and worked solution**, ready to print (`.../teacher`).
- **Every question has a download of the rows it needs**: 25 CSV files, 1 to 96 rows each, from the same check keys `check-values.mjs` recomputes. The test checks that A1's download gives back its answer (the two peaks are the maxima of the 24 rows of each grid).
- **A figure computed from a committed file** (the bill rules, the merchant snapshot, the network snapshot) is a row marked "computed", its source the file: honest, but not a table row a student can recompute in a spreadsheet. Noted for your ruling.

## What to review

Screenshots: https://github.com/SamuelEnrique/erw/tree/wip/games-v2/docs/reviews/games-2026-10-14/293

1. Before: `before/01-index-1280.png`, `before/02-live-set-1280.png`.
2. After: `after/01-index-1280.png` (each set live, its edition and its teacher's copy), `after/02-live-set-1280.png` (the line "For a class" in the teachers' box), `after/03-edition-students-1280.png`, `after/04-edition-teacher-390.png`.
3. A download: https://github.com/SamuelEnrique/erw/blob/wip/games-v2/site/public/problems/2026-10-15/know-your-grid-a1.csv

Locally: `C:\Users\lossa\Documents\erw-279\site`, `npx next start -p 3289`, unlock at http://localhost:3289/internal/unlock?token=<INTERNAL_COSTS_TOKEN>, then http://localhost:3289/learn/problems/prices-and-your-bill/2026-10-15/teacher .

## What was done

- `site/scripts/build-problem-edition.mjs`: builds all five sets with `lib/problems.ts` (the live pages' own code, through the alias loader), writes `site/data/problem_editions/<date>.json` and `index.json`, and for each question `site/public/problems/<date>/<set>-<id>.csv` with a header naming the edition, the source and the time read. Every request carries `x-erw-check: 1`.
- `site/lib/problemEditions.ts`: reads the editions. `app/learn/problems/[slug]/[edition]/page.tsx` (students), `.../teacher/page.tsx` (teacher, with `PrintButton.tsx`), `Frozen.tsx` (an edition's figures drawn as built, carrying their key as `data-frozen`, not checked against today's tables: their source rows are in the downloads).
- The index and each live set link the newest edition and its teacher's copy.
- `docs/methods/problem_sets.md`: a section on editions, the copies and the rows.
- Tests: `tests/test_session293.py` (10).

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `build-problem-edition.mjs 2026-10-15` | 0 | 5 sets, 25 questions, 25 files (117 KB) |
| `tsc`, `eslint` | 0, 0 | |
| Tests of sessions 293, 288, 44, 55 | 0 | 34 |
| `npm run build` (worktree) | 0 | 10 edition pages static |
| `check-values.mjs`, Games pages | 0 | 105 of 105 (the live sets) |
| A download as a visitor | 200, `text/csv` | the release gate does not cover files (`proxy.ts` matcher) |
| Screenshots after | 0 | 8, no sideways overflow |

## Decisions made without you

- **The edition's date is the UTC day it was read, 15 October**, though the chain is of 14 October.
- **The students' copy shows no answer at all** (not a closed "Show answer"), so a class cannot open one; the live set keeps its "Show answer".
- **Downloads are files in `site/public/`**, outside the release gate: they hold rows of public tables only. When the pages are in review a visitor can still fetch a CSV by its address.
- **Writing the edition from the code machine:** it is a frozen copy of page content (like the battery game's levels), read only from the live set; no warehouse table was written.
- **The live sets carry no download**: their rows move; the edition's are the ones a class uses.

## For Samuel's ruling

- The "computed" rows (bill, merchant snapshot, network snapshot): keep as figures, or add the underlying inputs (the tariff lines, the snapshot's days) to those downloads.
- How often a new edition: on request (as built), or each term.

## Files

- New: `site/scripts/build-problem-edition.mjs`, `site/lib/problemEditions.ts`, `site/app/learn/problems/Frozen.tsx`, `PrintButton.tsx`, `[slug]/[edition]/page.tsx`, `[slug]/[edition]/teacher/page.tsx`, `site/data/problem_editions/` (2 files), `site/public/problems/2026-10-15/` (25 files), `tests/test_session293.py`, `docs/reviews/games-2026-10-14/293/`, this report.
- Changed: `site/app/learn/problems/page.tsx`, `site/app/learn/problems/[slug]/page.tsx`, `docs/methods/problem_sets.md`.
