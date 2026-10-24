# Session 1425 report: the method notes and the rulings list

24 October 2026, from about 11:50 UTC, on samueloldlaptop (the old laptop), the seventh session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1425-grid`, cut from `wip/1424-grid` (chains 077, 078, 091, 100, 107 and 111 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1425`. Code-only, as the brief sets the chain (`runs/c077/brief.md`): no build, no server, no browser. Documents and tests only: no site code changed. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher, production not read (HTTP 402).

## Read these first

- **Every rule chain 111 set is in a method note, with its decisions.** Reports 1419 to 1424 read against `docs/methods/grid_network.md`'s section "The older blocks' files, anchors, method links and render cases (chain 111, 24 October 2026)", the one note chain 111 changed. Each session 1420 to 1424 had written its paragraph and Decisions; what its report held beyond them went into a block "Decisions (chain 111, session <N>, the rest of its report, written by session 1425)":
  - 1420: the figures drawn once and filed (the 18 `check=` of session 473 kept); the check scripts' default list also asks for 1415's and 1416's files and ISO-NE's page; ERCOT's queue file not in `GRID_FILE_PAGES` until production draws it.
  - 1422: no pin retired; a block later named on the page moves its case to the panel's name; no clock in a case's words; the fixture whole, not a sample; a count raised only to what is drawn.
  - 1423: the comparison tied to one build (`snapshot_built` of the snapshot and of session 1165's fixture); the opening hour equals `shownHour`.
  - 1424: how a fixed width is read at 390 px (rem as 16 px, breakpoints not counted); session 1158's keyboard items stand open.
  - 1421 needed nothing: its section holds every rule and decision of its report. 1419 changed no note.
- **The section opens with one index line**, "Chain 111 in this note (sessions 1419 to 1426): ...", naming 1419 to 1425 and where each sits; it replaced the short line session 1420 wrote (no test pinned it). No heading changed: `METHOD_RIGHT_NOW`'s fragment stands. The notes session 1421's links open (`storage`, `price_board`, `energy_projects`, `datacenter_facilities`, `california_reliability`) have no chain 111 section and need none.
- **The rulings list** (`docs/reviews/grid-rulings-2026-10-23.md`): one paragraph says none of the 65 items has been ruled (main's commits and `docs/state/` read at 12:00 UTC, main at `1cf485c1`; the notes since 1417's read are data chains 110, 112, 113 and chain 107's, none rules on this list), none struck. 6 new lines: words 3 (1420's download line under six older blocks, 1421's three method lines, 1421's bare "Method" links), design 3 (1422's older blocks as named panels, 1420's row height, 1421's Batteries link target), data 0. 1424's keyboard item is session 1158's two lines, said in the paragraph, not repeated. Total 71.
- **"To finish"**: its first line now opens with production's HTTP 402 (Samuel's), then the landing, now `wip/1425-grid` (every session 1152 to 1425, main merged at `c446038c`, chain 111 merged none). Six chain 111 lines after chain 107's: the expected differences; the check scripts 1420 to 1424 extended (`check-table-downloads`, `check-download --grid`, `check-routes` 26 of 26, `check-links`, `check-390` with AccessLint, `check-network-v3`); check-values on four grids; screenshots (`review-1424/`); the gate's render tests and 1423's snapshot rule; the case moves after a ruling on 1422's item.

## What to review

1. Read `docs/reviews/grid-rulings-2026-10-23.md` on `wip/1425-grid` (until it lands): the session 1425 paragraph under the opening; the three lines after 1184's "Method: <the section's words>" line in "The page's words"; the three lines after 1416's row height in "The design"; "To finish" line 1 and the six lines after chain 107's screenshots line.
2. Read the index line at the top of `docs/methods/grid_network.md`'s chain 111 section, then each block marked "written by session 1425".
3. After the landing, on production: `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**, then `https://erw-flame.vercel.app/data/methods/grid_network` and search "written by session 1425".
4. Screenshots: not taken, no build (documents only).

## Checks

- Precheck for session 1425: run by the orchestrator, exit 0.
- `python -m unittest`, one module at a time, 45 modules (every module that names `grid_network.md`, the rulings list or the methods folder): each exit 0, 661 tests. `test_session1176` (29 tests, 6 new), `1188` (21 tests, 6 new), `1162` (5, its regex extended) among them. The 17 that skipped a node case without `node_modules` were run again with the junction, each exit 0, no 14xx or 118x skip left (the skips that remain need warehouse tables the worktree lacks). The exits were echoed in the loop and joined by `tr` after each was read.
- With the `node_modules` junction: `npm run content` exit 0; `node scripts/check-methods.mjs` exit 0, 553 of 553 figures named, 57 pages; `test-markdown-safe.mjs` (alias loader) exit 0, 7 tests; `test-grid-older-methods.mjs` exit 0, 3 of 3; `test-grid-methods.mjs` exit 0, 5 of 5.
- The junction removed with `cmd /c rmdir`; the main copy's `node_modules` intact (333 entries).
- No `tsc`: no TypeScript changed. No em dash in any changed file (`TheNotesChain111.test_no_em_dash`); every changed file still CRLF throughout.

## The landing

- None: chain 111 is code-only, stacked on `wip/1417-grid` (chains 077 to 107, not on main), and production answers HTTP 402. This branch lands with them. Pushed: `wip/1425-grid`.

## To finish

- Land with the combined landing (`wip/1425-grid` or its successor), once production's 402 is mended. Expected differences from this session: the method page `/data/methods/grid_network` gains the index line and four Decisions blocks; no figure or key moves.
- At that landing, `check-methods.mjs --values <the run> --write`, then `check-methods.mjs` again (today's run read the keys recorded before the six chains).

## Decisions made without you

- **No `tests/test_session1417.py` exists**: chain 107's counts are in `test_session1176` and `1188`, so chain 111's went beside them (`TheRulingsChain111`, `TheNotesChain111`), no new module.
- **The tests extended, nothing loosened**: `TheRulingsChain100`'s count of 56 now leaves out `14[12]\d` lines, `TheRulingsChain107`'s total of 65 leaves out `142\d` lines (each with a comment), `test_session1162`'s regex takes 1420 to 1422. The new classes count chain 111's 6 by session and group, the total 71, the "none of the 65" line, the order in each group, the 402-then-landing line and the chain's "to finish" lines; one test holds that only `grid_network.md` has a chain 111 section.
- **Production's 402 opens the first "to finish" line**, not a line of its own: four tests of earlier chains read the landing from the first line, and a line before it would have meant changing them.
- **Weight within groups**: the words lines right after 1184's method line, since they carry 1182's and 1184's words to the older blocks (chain 107's four stay last, as its test holds); the design lines after 1416's row height and before 1404's lines on the tests, 1422's named panels first.
- **A line named again is not a new line**: 1424's keyboard item is 1158's two lines; the test holds the map line to one.
- **No test mechanics copied into a note**, as 1188 and 1417 decided, except where a report gave a rule for later work (1422's case move and no clock in the words, 1423's `snapshot_built`, 1424's width reader).

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `docs/reviews/grid-rulings-2026-10-23.md`, `docs/methods/grid_network.md`, `tests/test_session1162.py`, `tests/test_session1176.py`, `tests/test_session1188.py`.
- On this machine only: `runs/s1425/` in the worktree (every test's output, check-methods' output).
