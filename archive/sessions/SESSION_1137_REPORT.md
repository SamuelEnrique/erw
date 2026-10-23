# Session 1137 report: what the board draws, downloadable

23 October 2026, 20:06 to 20:10 UTC, on samueloldlaptop, unattended, on `wip/1137-board` (cut from `wip/1134-board`). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Model spend USD 0.

## What was done

- **`/board/rows`**: the rows the board draws as one CSV (`rowsCsv` in `site/lib/board.ts`, served by `site/app/board/rows/route.ts`), from the page's own file after the day's hold (session 1116's `holdRows`), so no second read and no held figure: a `#` header as the data standard writes one (what it is, when the file was built, where each row comes from, the license, the grids held that day), then one line a row: its id, group, label, unit, frequency, status, latest date and value, its four moves, its two means, its year's low and high, and its source. A row that is "license needed", "licensed source needed", paused or not held carries no figure. Static (made at the build, no database read) and under `/board`, so the release gate covers it as it covers the page.
- **The page links it** above the tables' own downloads: "The rows drawn here, as one CSV".

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-board-1137.mjs`: exit 0, 4 of 4 (the header; every figure the file's; the held rows with none; the route from the held file).
- `tests.test_session1137`, 1116, 132, 240: exit 0, after session 240's test of the page's return line was split in two around the new footer.
- Em dashes: 0.

## Decisions made without you

1. **A route under the page, not an `/api/download`**: the CSV is the page's own figures, not a table of the live set, and it stays behind the page's gate. Reversible.

## For Samuel's ruling

- None new.
