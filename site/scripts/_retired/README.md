# Retired check scripts

Energy Research Warehouse (ERW) site. A script here is kept as a record and is not run: no gate, no workflow and no
test calls it. It was moved here, not deleted (CLAUDE.md rule 3), as `site/app/_retired/` keeps a retired page.

| Script | Written | Retired | Why | What covers the page now |
|---|---|---|---|---|
| `check-seller.mjs` | session 145 | session 264, 14 October 2026 | It reads `/cost-of-power/seller` as it stood before session 212: the months, debt coverage, the stress days and the folds the owner's ruling of 12 October 2026 moved into the CSV downloads. It exited 1 on 12 of 33 since then (sessions 235, 241c and 257 reported it) | `scripts/check-values.mjs`: every figure the page reads from its files carries a check key (`cap|<grid>|...`, `mr|iso=<grid>&...`, `ms|iso=<grid>&...`, session 264) and is recomputed; `scripts/check-seller-scenarios.mjs` in a browser for the scenarios (106 of 106 on 14 October 2026). `scripts/check-seller-deeper.mjs` is stale too (it exits 1 on the battery-beside section session 212 moved to the CSV) and is left in place for the owner's ruling |
| `check-seller-face.mjs` | session 183 | session 264, 14 October 2026 | It looks for the sections "Month by month" and "Debt coverage" at 1280 and 390 px, which session 212 removed | The same |
| `check-seller-deeper.mjs` | session 162 | session 298, 19 October 2026 (the owner's ruling 4d of 18 October) | It reads the three blocks of session 162 as they stood before session 212: its battery-beside rows are NaN since that section moved into the CSV, and it crashed at its line 120 before the profile box (session 235's report, item 3) | `scripts/check-values.mjs` (the page's keys), `scripts/check-seller-scenarios.mjs` and `scripts/check-decisions-face.mjs` (the three questions and the profile box) |

The relative imports inside the three files (`../lib/...`) point one folder too high from here; to run one again for a
record, copy it back to `site/scripts/` first. Do not restore it as a gate: it describes a page that is gone.
