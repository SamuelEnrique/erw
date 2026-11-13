# Sessions 1890 and 1891: the board's stale tile and the workbench a click opens (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, sessions 1890 and 1891, samueloldlaptop, unattended, Opus 5.5. Run by one agent in `erw-1890` on `wip/1890-board`, cut from `wip/1883-board` (`30b5b3573`). About 00:45 to 01:35 UTC. Faults 4 and 5 of session 1885's trader path walk (`docs/reviews/trader-path.md`).

## What it did, with commits (branch head `bf6d9e819`, pushed)

- **Fault 4 (session 1890), `/board`, step 13:** the tile "ERCOT Hub average day-ahead 40.64 USD/MWh, 6 Nov 2026 (stale), Day +13.65, Week +0.72" printed moves the series' row blanks. Now a stale tile's Day and Week read "stale", titled "Not shown: the series is stale (...)" as the row is; fresh tiles take their moves through `shownMove`, the row's function (`TopTwelve` in `site/components/board/BoardView.tsx`). `site/scripts/check-board.mjs` checks tile moves against `shownMove` (it expected numbers on stale tiles). `cb6cad4cd`.
- **Fault 5 (session 1891), step 14:** a tile's click set `?s=ercot-hb-hubavg-da` and opened the workbench 1,174 px below the first screen with no scroll and no focus. Now every control that opens the workbench (tiles, headline cells, rows, the week's rows, spikes) flags the click; once drawn, the workbench heading scrolls into view (`block: "start"`, no smoothing under reduced motion) and takes focus (`tabIndex={-1}`, `Workbench.tsx`). A page opened with `?s=` does not jump; a workbench already on screen only takes focus. `bf6d9e819`.

## Tests and the built page

- `tests.test_board_1890` (5), `tests.test_board_1891` (9), `tests.test_board_1883`, `tests.test_session1116`: 28 tests OK.
- Built under the build lock, served on 3890 (`runs/s1890/`): 5 of the 12 tiles stale on this file, each "stale / stale" with no digit, the 7 fresh tiles keep their moves; a click on the first tile scrolls to 1,205 px, the heading 39 px from the top with focus; `?s=` on load leaves the page at the top; no page error. `check-board.mjs` 48 of 48. Shots `runs/s1890/shots/`.

## Decisions made without you

- The scroll goes to the workbench where it stands rather than moving the workbench beside the tiles: no layout change.

## For Samuel's ruling

- None new.
