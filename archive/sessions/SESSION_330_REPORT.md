# Session 330 report: /map and /storage, finished (lighter)

20 October 2026, from about 06:25 UTC, unattended, on samueloldlaptop (the code machine), the third finish session of the chain of 19 to 20 October, night (`CHAIN_OCT19_PROMPT.md`). Branch `wip/330-map-storage` in the worktree `erw-296`, from session 329's branch; lands on main as `task/330-map-storage` after session 329. Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **Both pages were already near the standard.** The map's numbers are its file's, checked by `check-map`; the storage tabs carry every number with its check key (`check-values`); the map's "Choose" panel and the build-out's and owners' panels have their Resets with their defaults written. What they lacked: the downloads, and notes that say what the pages draw since sessions 239, 303 and 318.
- **The map's own copy is eleven days old.** `site/data/map.json` was built on 9 October (EIA-860M of August, the queues as held on 30 September, the tracker of 9 October), while `datacenter_facilities` and the two EIA-860M tables ran on 20 October and `energy_projects` on 5 October. The file is rebuilt by the monthly job or by hand: the data machine's.

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first).

1. https://erw-flame.vercel.app/map and https://erw-flame.vercel.app/map?tab=resources : the downloads at the foot.
2. https://erw-flame.vercel.app/storage , `?tab=buildout`, `?tab=owners`: the downloads under each tab.
3. `docs/methods/energy_projects.md` ("The page as it stands") and `docs/methods/storage.md` (its last section); `docs/brand/review-330/`.

## What was done

- **Downloads** (session 328's shared line): `/map`, under both tabs, the four tables its file is built from (`energy_projects` and `datacenter_facilities` as CSV, Python and Stata; the two EIA-860M tables on Redivis, as the live set does not hold them). `/storage`: the fleet tab's four tables, the build-out's table; the owners' table is held for review in the live set, so its tab points to Data and methods.
- **Method notes**: a section on each page as it stands (tabs, the charts in SVG, the maps on the canvas pending a ruling, the numbers' checks, the downloads, the tables' dates on 20 October).
- Tests: `tests/test_session330.py`.

## Stale tables, for the data machine

Read from the public catalogue on 20 October 2026: `energy_projects` last ran on 5 October (the queues); `site/data/map.json` was built on 9 October (above); `storage_buildout_monthly` and `storage_owners_monthly` hold EIA-860M's August 2026 inventory (the owners table is held for review in the live set). The storage fleet's tables ran on 20 October.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 330"` | 0 | |
| `tests.test_session330` and every test that reads a file this session changed (10 modules) | 0 | OK |
| `eslint` on the two pages | 0 | |
| `finish_build.sh 330` (erw-296 at `7efd3011`): build | 0 | the first two runs failed on the home page's required read, a database statement timeout (06:42 and 06:44 UTC; not this session's change); the script now takes a build again after such a timeout, as `land_checks.sh` does, and the next build passed (one try with two timeouts that did not fail the build, then one with none) |
| `check-values` on `/map` and `/storage` | 0 | 524 of 524 |
| `check-routes` | 0 | every page |
| `check-map`, `check-resources`, `check-buildout` | 0 | 91 of 91; 97 of 97; 10,241 (3,530 numbers equal to the fixture's rows) |
| `check-table-downloads` on the five addresses, the Python reader run on `storage_daily_cycle` | 0 | 22 of 22 on the second run; the first failed on `energy_projects` (the route's row-count fault, which reaches an entities table too: the check now names it as it names a series table) and on the owners tab (its one table is held for review, so the line offers none and says every public table is on Data and methods: the check now says so and passes the page by) |
| Impeccable `detect --json` on the two changed pages | 0 | no finding |
| The probe at 390 on the five addresses | 0 | 390 within 390 on each |
| Shots, 1280 and 390, before (production) and after (the build) | 0 | twenty, `docs/brand/review-330/` |

## Landing of session 329 (recorded here: session 329's report is in that landing's own commit)

## Landing

## Decisions made without you

- **The resource layers are not offered as downloads** on the map's second tab: they are their publishers' files, each named with its terms in the tab's note; the line offers the ERW tables laid over them.
- **A table the live set holds for review is left out**, as on `/datacenters` (session 329): the owners tab offers none.
- Questions skipped (Impeccable's playbooks ask them).

## For Samuel's ruling

- Session 318's question stands: whether the two maps should leave the chart library (an SVG map from the GeoJSON held).

## Files

- New: `tests/test_session330.py`, `docs/brand/review-330/`, this report.
- Changed: `site/app/map/page.tsx`, `site/app/storage/page.tsx`, `docs/methods/energy_projects.md`, `docs/methods/storage.md`.
