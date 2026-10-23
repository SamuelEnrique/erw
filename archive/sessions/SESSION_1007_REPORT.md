# Session 1007 report: the data page says how

23 October 2026, from about 03:16 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1007` on `wip/1007-packages` (cut from `wip/1006-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1007. Model spend USD 0. No warehouse data written. Requests: none.

## Read these first

- **`/data` gains "Use the ERW in your tools"**: three panels (Python, Stata, R), each with:
  - its install line;
  - the six calls;
  - a link to its README on GitHub.
- **Under the panels**:
  - the citation each package writes;
  - the specification's sentence on held tables;
  - the site's own download's header, documented (the provenance lines, the "Downloaded" line, then the columns).
- **Every line is the specification's or a README's, word for word.**
  - The lines live in one file, `site/lib/packages.ts`, and test 1007 holds each to its source.
  - The Stata and R READMEs' examples now show all six calls, so the panels can quote them.
- The page's other figures are unchanged; the gate's check-values covers `/data` (below, the landing).
- **Screenshots**: `docs/brand/review-1007/`, before (production, no such section) and after (a build of `wip/1011-packages`, which holds 1007) at 1280 and 390. The code panels scroll inside their frames at 390; the page itself does not scroll sideways.

## What to review

1. Open `https://erw-flame.vercel.app/internal/open` and enter the token, then `https://erw-flame.vercel.app/data#tools` (after the landing).
2. Read the three panels: is each the call you would type?

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session1007` | 0 | 3 tests OK |
| build of `wip/1011-packages` (lock `s1011`, on `db_probe`'s 0) | 0 | |
| `runs/shots1007.mjs`, production and the build | 0 | 4 shots each; the page 1265 and 390 px wide at 1280 and 390 |

## The landing

With 1000 to 1012.

## Decisions made without you

1. **One file for the lines** (`site/lib/packages.ts`), held to the specification and the READMEs by a test, so the page cannot say a call a second way.
2. **The method note linked on the site** (`/data/methods/packages`), not on GitHub.

## For Samuel's ruling

- Nothing new.

## Files

- New: `site/lib/packages.ts`, `tests/test_session1007.py`, `docs/brand/review-1007/`, this report.
- Changed: `site/app/data/page.tsx`, `packages/stata/README.md`, `packages/r/erw/README.md`.
