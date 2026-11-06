# Session 3012 report: the landing service (the board, rows 1 and 2), then tariffs and policy

6 November 2026, about 12:20 to 12:47 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The old laptop's board landed: `task/1600-1610-board` merged as `0aa1dbd02`** (run 42218427806: checks passed 12:42, merged 12:43, Vercel success). It covers request rows 1 and 2, chain 165's sessions 1600 to 1609. Snapshots `s3008-land-before` and `s3008-land-after`: 25 pages, **0 differences** (expected: every page is in review).
- **How it got there:**
  - **The gate's first run** (session 3008, `3c3d1578f`) failed at the suite: 3 of 7,864 tests, older board tests (sessions 166, 207 and 247) that chain 165's own changes broke. ISO-NE's reserves are now "licensed", two more held-grid checks were added (the hub spreads and the spark spreads), and there is one more whole-table reader (the ERCOT adders). The three tests now follow the branch's intended changes, each with a comment saying why (`1dd13ecf`).
  - **The second run:**
    - the suite passed (7,864 tests)
    - npm ci, the build and serve passed
    - check-values matched 7,812 of 7,812 values
  - **check-values' two failures are main's known floors,** `/deals` (1 checked number) and `/learn/problems/know-your-grid` (0). Session 2969's report names the same two, and the branch does not touch those pages.
  - **As chain 157 did in session 2969,** I ran the gate's remaining checks by hand on a build of the same commit (build lock held, port 3600, the server stopped by its PID): check-routes (225 pages in review asked as a visitor, 0 failed), check-cross-checks (92 passed) and check-csp (97 pages, 0 violations).
- **Rows 1 and 2 of `docs/state/landing_request_oldlaptop.md` are marked "landed at 0aa1dbd02"** (`2890b7917`, snapshots `s3008-mark-before` and `s3008-mark-after`: 0 differences).
  - Rows 3 to 6 are held in row 7 (`wip/1633-board`), which waits for session 3016.
- **Not done: deleting the landed branches.** The 11 branches `wip/1600-board` to `wip/1610-board` are all ancestors of main, checked one by one, but the permission check refused deleting remote branches. They are left for you; see "For Samuel's ruling".
- **12 retail drafts on the review list** (module `deep.tariffs_policy`, state draft), from `warehouse/analysis/findings/deep/retail.py`:
  - **Commercial electricity sales:** 1,503.3 TWh in the US in 2025, against 1,083.1 in 2001. Texas: 174.7, against 87.9.
  - **The average residential price:** USD 172.6 per MWh in the US in 2025, against 85.8 in 2001 (nominal). Hawaii: 404.7, against 163.4.
  - **Homes against industry:** the residential price was USD 87.7 per MWh above the industrial in the US in 2025, against 35.4 in 2001. Michigan: 115.2, against 31.4.
  - **Minutes without power** (customer-weighted SAIDI, major event days included): Nebraska 542.8 in 2025, against 67.9 in 2015. Missouri 466.0, against 164.9. The US's rise (209.2 to 305.4) fails the half-change test.
  - **Smart meters:** 60.5 percent of US meters in 2019, against 38.6 in 2013. Illinois: 92.8, against 6.4. The ERW's table splits them out by state only to 2019.
  - **Net-metered capacity:** 55,809 MW in the US in 2024, against 5,462 in 2013. California: 18,822, against 2,125.
- **Five reproduction scripts printed their expected figures exactly.**

## What it did

- **`deep/retail.py`:** six candidates on public EIA tables. `tests/test_session3012.py` (1 test, passed).

## Decisions made without you

- **The hand checks stand for the gate's last three steps.** That is the precedent of session 2969, when the gate stopped at check-values on the same two floors of main.
- **The large-load tariffs, the connection rules and the policy actions are not drafted by year.** They are levels and recent months, and the chain's questions on them need a comparison across utilities, not a change over years.
- **The leftover folder `C:\Users\Shared\Documents\erw-land1610`:** git no longer counts it as a worktree, but Windows could not delete it (a path too long in `node_modules`). Session 3022's clean-up removes it.

## For Samuel's ruling

- **May this window delete the remote branches a landing makes ancestors of main?** The request files ask for it, and the permission check refuses it. Waiting now: `wip/1600-board` to `wip/1610-board` (11 branches), all ancestors of main.
