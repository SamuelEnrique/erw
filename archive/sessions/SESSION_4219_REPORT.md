# Session 4219 report: the build read, the faults, landing request row 1 (chain 239, window 4)

13 November 2026, about 11:45 to 12:14 UTC. Branch `wip/4200-forecast`. Model spend USD 0.

- **The build lock** came free at 11:51 (after window B's gates); held to 12:03 for `npm ci`, three builds and the reads, then released.
- **The worktree's `node_modules`**: a junction to the main checkout's was refused by Turbopack (outside the project root); removed with `rmdir` (the link only) and replaced by `npm ci`, as `land_check.py` does in its clean copy.
- **check-values** on the four `/impact` addresses: 64 of 64 figures match. To get there the page's figure forms moved into the model (`displayOf`) and check-values judges a forecast figure's text by it (a rule of the page's own, as the datacenter grid's whole and one-decimal rules are).
- **The browser read** (headless Chrome by the DevTools protocol, the internal view's cookies from curl's jar, the token never printed), at 1280 and 390 px, three cases: no sideways scroll at either width after the fixes, no console error, every default's line and tip, the reader's actions (state, size, scenario B, its technology, a planned project, Reset, Copy A to B), each chart's hover, the table by year, the three files.
- **Faults 6 to 13** (`docs/reviews/forecast-faults-2026-11-13.md`): 6, 7, 9, 10, 11 and 12 fixed, each with a test (`tests/test_session4219_forecast_faults.py`); 8 was the read's own selector; 13 (year labels crowding with long lives) is the shared chart's spacing, left open.
- **Hand checks**: Minnesota wind's production tax at 120 MW (120 x 8,760 x 0.4197 x USD 1.20 = USD 529,426), Texas gas's severance at a 50 percent in-state share (USD 5.79 million a year), Texas wind's sales tax and construction jobs: each as the page shows.
- **The 177 test files** that name what the stack touches: 2,180 passed, 56 skipped, 6 failed, each fixed or explained (tests 1903 and 412 brought to the new page; test 1011 a stale build artifact).
- **Merging `origin/main`**: twice; `package/llms.txt` regenerated (a generated file's conflict), and a conflict in `INTERNAL_METHODS` (window B's periodicals' notes and this chain's forecast note) resolved by keeping both.
- **Landing request row 1** on main (`0b1bdbd3e`): `wip/4200-forecast` at `1a1008073`, task `4200-forecast`, port 4200.
- **A slip of mine, repaired**: a temporary worktree for the landing file was created inside the main checkout (a path relative to it) and removed a minute later by the next step; nothing was committed there and the main checkout's status was clean when checked.
