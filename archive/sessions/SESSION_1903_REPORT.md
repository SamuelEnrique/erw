# Session 1903: the landing of chain 217's stack, with sessions 1907 and 1908 (chain 219, 13 November 2026)

Energy Research Warehouse (ERW). Chain 219, session 1903, samueloldlaptop, unattended, Opus 5.5. About 01:52 to 03:37 UTC. Chain 217's unfinished step 2: the landing of its whole stack.

## What it did, with commits

- **The stack:** `wip/1903-stack` cut from `wip/1898-lab` (it holds `wip/1883-board`, `1882-periodicals`, `1884-records`, `1894-periodicals`, `1896-periodicals`), `wip/1890-board` and `wip/1892-windows` merged in, then `origin/main`: no conflict (`72fe8fa6d`). The paths' faults of session 1885 given their states in `trader-path.md`, `lab-path.md` and `onenergy-walkthrough.md` (`0c2853246`).
- **Session 1898's stale build lock** (`s1898`, since 01:42 UTC) released (`scripts/buildlock.py release s1898`), session 1898 having ended.
- **Gate 1** on `0c2853246` (`runs/s1903/land_check.out`): freeze to serve pass, the suite 8602 tests OK (368 skipped), build 180 s; **check_values failed**: 8021 of 8033 values matched. Nine failures were this stack's: the datacenter tracker's grids view, which session 1898 drew for the first time, "page shows "164,685" | page read 164685.4 | Supabase 164685.4" (eight capacity cells and ERCOT's reserve margin "11.4"). The page's figures were the live set's; `check-values.mjs` expected two decimals for a figure that is not whole, while the page writes MW whole and the margin to one decimal.
- **The fix:** `check-values.mjs` reads `dcgrid|` MW and counts whole and the share of peak and the margin to one decimal; `tests/test_session1903.py` runs the two rules in node on the gate's own cells (`77dc4347e`).
- **Sessions 1907 and 1908 folded in** (`wip/1908-periodicals`, `0b9c9754f`), then `origin/main` merged again (main had meanwhile landed the data machine's chain 216, with check-values' Digest keys): `2504ff817`.
- **Gate 2** on `2504ff817` (`runs/s1903/land_check2.out`): the suite 8633 tests OK (368 skipped), build 133 s; check_values 8033 of 8034, 2 failures, neither this stack's: `/digest`'s floor (0 checked numbers, as in sessions 1880's and 1888's gates) and `/digest/2026-11-12`'s "digest_story|news_stories|news:808f73a07b2ad109|price | page shows "USD 2.1 billion" | Supabase undefined", the real mismatch session 3823 found and carried to the data machine's next file. The grids view's nine cells now pass.
- **The three skipped checks by hand** on the kept worktree served on 3903 under the build lock (as sessions 1880 and 1888 did): `check-routes` exit 0 (1 live page and 225 in review, 0 failed), `check-cross-checks` exit 0 (92 passed), `check-csp` exit 0 (97 pages, 0 violations).
- **Session 1898's three fixes read on that build** at 390 and 1280 with the internal cookie (`runs/s1903/read.json`, shots `runs/s1903/shots/`): the grids view draws every grid's peak and capacity ("83,597", "164,685" for ERCOT) and ERCOT's margin "11.4% (summer 2027)", the facilities' cells still "license needed"; the Lower 48's card reads "Net export by grid" with no MW; ERCOT's In the news is the one held sentence, no "No story in the last 14 days matched".
- **The landing:** `scripts/freeze.py status` exit 0; the before snapshot `s1903-before` (25 pages, 0 failed); `origin/main` an ancestor of `2504ff817`; pushed to `task/1903-stack` at 03:15 UTC. Its result follows.

## Decisions made without you

- The checker was taught the page's rounding rather than the page changed: the page's whole MW and one-decimal margin are the tracker's own forms elsewhere on the page.
- Sessions 1907 and 1908 were folded into this landing to spare a third 45-minute gate.
- The two `/digest` failures were taken as session 1880's and 1888's were: main's, not this stack's; the skipped checks were run by hand.
- The 481 px scroll width the read measured at 390 is headless Chrome's minimum window (its shot renders 496 px wide), not the page's.

## For Samuel's ruling

- None new.

## The landing's result

- `code-branch` run 43357695421 passed and merged `task/1903-stack` as **`b1bc8829f`** at about 03:30 UTC.
- Production probed with the internal cookie until the grids view drew ERCOT's capacity ("164,685", 03:33 UTC); then the after snapshot `s1903-after` and `compare s1903-before s1903-after`: **0 differences in all 25 pages** (expected: every page is in review, so a visitor sees the in-review page at each address).
- Deleted on origin, each an ancestor of `origin/main` first: `wip/1882-periodicals`, `1883-board`, `1884-records`, `1890-board`, `1892-windows`, `1894-periodicals`, `1896-periodicals`, `1898-lab`, `1903-stack`, `1907-periodicals`, `1908-periodicals` (`task/1903-stack` was deleted by the workflow). Their worktrees and the three gates' kept worktrees removed (17 before, 4 after: the main copy, `erw-1425`, `erw-1600`, `erw-1899`).
