# Session 7562 report: the company database read as a fund analyst (samueloldlaptop, 17 November 2026 UTC)

- **Asked:** the third of the six reads: `/companies`. Checked first: no `companies-read` file on any branch; part A's 31 rows read (rows 9, 20, 22 cited).
- **The read:** `docs/reviews/companies-read-2026-11-16.md`. Five cases (Constellation, Vistra, NextEra and FPL, Talen's Susquehanna, the hyperscalers), 10 rows: 2 site fixed, 2 data machine (requests 306, 307), 3 rulings, 1 license, 2 browser (305, 306).
- **Found:** the listed parent of a fleet reads 0 MW and names none of its subsidiaries; the subsidiaries' "Parent" is not linked though the parent's page exists (Constellation, NextEra). Only 18 of 12,724 companies state a parent.
- **Fixed on the page:** the Footprint column's hover now says a plant both operated and owned counts twice (Susquehanna 2,532 MW operated, 4,811 footprint); an empty search says 1,309 companies named only in held tables are not listed. The two texts live in `site/lib/companydb.ts` (`FOOTPRINT_WORDS`, `noneHeldWords`), since a page file may export nothing but its own names. Tests: `site/scripts/test-companies-read.mjs` 5 of 5 (the page drawn whole with the font stand-in); `test-companies.mjs` passes; pytest `test_session1878, 5160` 18 passed.
- **What to review:** `https://erw-flame.vercel.app/companies?q=talen` (hover Footprint); `https://erw-flame.vercel.app/companies?q=amazon` (the empty answer).
- **Needs the key:** nothing.
- **Decisions made without you:** none beyond the read's defaults.
- **For Samuel's ruling:** rows 5 (no parent sum; default: none), 6 (ownership only as stated; default: the NRC's field and reviewed aliases) and 8 (Seen dates; default: as they are).
