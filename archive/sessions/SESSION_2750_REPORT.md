# Session 2750 report: the Tennessee Valley Authority not taken (a Cloudflare challenge in place of its robots file); queue file 140 written first

25 October 2026, about 21:45 to 22:00 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed first (`runs/c139/pre2750.out`). Model spend USD 0. Pulls: 4 requests of 15, all by the probe.

## Read these first

- **Queue file 140 first:**
  - `queue/next/140-day-10-december-data-austria-spain-italy-greece.md` (sessions 2764 to 2777) was written from file 139 by `runs/c139/write_140.py`, made by exact replacements from chain 138's writer (`runs/c139/make_write_140.py`). It keeps the rules word for word.
  - 140 was the next free number, and 2764 to 2777 were free on main and on every branch.
  - **Its sources are four national statistics offices:** Statistics Austria, Spain's INE, Italy's ISTAT and Greece's ELSTAT. None is in the record or the queue. Their grids' operators are held (Spain, Austria) or closed (Italy's Terna, Greece's IPTO a file a day), and each office is likely to publish under an open licence, which each session confirms. Each names a held table to cross-check against (all five named tables are in coverage).
  - Pushed to main alone as `577a1199`; snapshots `c139-q140-before` and `c139-q140-after` show **0 differences** (Vercel's deployment of the commit completed at 21:55:48 UTC).
- **Chain 139's worktree:** `erw-c139` on `wip/2750-2763-data`, from main at `27052bab`.
- **TVA not taken:**
  - **www.tva.com** answers its robots file with HTTP 403: a Cloudflare managed challenge ("Enable JavaScript and cookies to continue") served in its place. **tva.com** and **www.tva.gov** redirect to it and get the same challenge (reads 1481 to 1483).
  - **lakeinfo.tva.gov** answers 404 for a robots file (read 1484), so it states no rule, but TVA's terms of use are on www.tva.com, behind the challenge. Its lake levels would be read without terms, and they are not power figures. It was not asked further.
  - A challenge is not answered by the reader (chain 137's rule for PEI's Radware page). TVA's hourly load and generation are held already through EIA-930's TVA balancing authority.
- **No table.**
- **Test 205's bound** is raised by 40 for this chain's reads, from 1481.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.tva.com's robots file (its own request) | 403, a Cloudflare challenge |
| 2 | tva.com's robots file (its own request) | redirected to www.tva.com, 403 |
| 3 | www.tva.gov's robots file (its own request) | redirected to www.tva.com, 403 |
| 4 | lakeinfo.tva.gov's robots file (its own request) | 404 |

Reads recorded: 1481 to 1484.

## Decisions made without you

- **lakeinfo.tva.gov not used:** its owner's terms cannot be read, and lake levels are not a power series.

## For Samuel's ruling

- None new. (TVA could be asked to let the ERW's reader past its challenge; that is a letter, and no session sends one.)

## Files

- New: this report. Changed: test 205's bound, the license record (reads 1481 to 1484) and `docs/licenses.md`.
- On the data machine only: `runs/c139/s2750/`, `runs/c139/make_write_140.py`, `runs/c139/write_140.py`, `runs/c139/raise205.py`, `runs/license_reads/s2750/`.
