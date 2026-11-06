# Session 2866 report: the explorers landed

5 November 2026, about 22:57 to 23:30 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none but the snapshots and GitHub reads.

## Read these first

- **`wip/2204-explorers` landed as `c43eefb06`.**
  - The branch (`c21c8d0d`) was merged with main twice: once before the gate, and again after 2206 landed (`99c7c2d3`).
  - Pushed to `task/2204-explorers`. Run 42128445259 passed and merged at 23:28 UTC; deployed by 23:29.
- **Rule 8's snapshots:** `s2866-before` (23:16) and `s2866-after` (23:29): 25 pages, **0 differences** (expected: the explorers are in review).
- **The gate** (`runs/land_check/71d85f12...`):
  - Suite: 7,366 tests OK. npm ci, build and serve passed.
  - check-values failed on 13 lines, all main's own (`runs/c147/cv_diff.py`: 0 new). One of them is the WTI revision, because the branch was cut before 2206 landed.
- **On the kept build (port 3204, the internal view):**
  - `check-explorers.mjs`: exit 0, 14 of 14 pages read, 0 findings.
  - `check-links.mjs` on the four pages: exit 0, 206 links, 55 addresses, 0 findings, 2 aliases.
  - Eight shots at 390 and 1280, kept in `runs/s2866/shots/`. Two were looked at: each draws its page, its stale-data notice and its figures.
- **Not run:**
  - `check-390.mjs`: its before file (`runs/s2203/390_before.json`) is the old laptop's, and the shots above stand in for it.
  - The pointer-over-chart shot.
  - Impeccable's `detect`, which is not on this machine (`docs/tooling.md`).

## Decisions made without you

- **Landed with check-values' known failures,** as session 2863 decided. Chain 087's own rule asked check-values to pass outright, which it cannot on main as it stands.
- **The shots kept on this machine,** as chain 147 asks, not committed to the branch under `docs/brand/`.

## Files

- New: this report.
- On the data machine only: `runs/s2866/` (`explorers.json`, the checks' output, `shots/`).
