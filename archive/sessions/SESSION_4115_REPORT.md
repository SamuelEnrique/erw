# Session 4115 report: hard-coded counts, and the record's own description of its method

Energy Research Warehouse (ERW). Chain 229, session 16 of 50, lab-desktop third window, 13 November 2026 11:50 to 11:53 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4115-licenses` (stacked on `wip/4110-licenses`, landing row 2).

## Checked

- **No hard-coded count of held tables or of verdicts** in `site/app`, `site/lib`, `site/components`, `docs/*.md` or `package/*.md`, outside the files the record writes. The held count of 48 to 49 lives in `docs/guide.md`, `package/README.md` and `package/llms.txt`, kept in step since session 4102.
- **The words "not settled" or "unsettled" on the site** are the record's own vocabulary (`site/lib/license.ts`, `site/lib/packages.ts`).

## Fixed

- **`docs/licenses.md`'s header** (written by `scripts/licenses.py write`):
  - it gains a line on a verdict read again (robots first, a new label, the sentence found by code, a refusing host not asked);
  - "One request a publisher, no second try. Times are UTC, 12 October 2026." becomes "One request a label", the reads after the first 40 dated in the record.

## Tests

- **The 34 license test files with tests 4101 and 4109:** 508 passed, 12 skipped.

## Decisions made without you

- **No separate method note** for the license procedure: `docs/licenses.md`'s header is its description, and it now says how a verdict is read again.

## For Samuel's ruling

- None new.
