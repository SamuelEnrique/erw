# Session 2236 (chain 156, deals and datacenters) report: the datacenter facilities

6 November 2026, about 11:35 to 13:20 UTC, portable-laptop (code role), unattended. Worktree `erw-2236` on `wip/2236-deals`, cut from `wip/2235-deals`. Model spend **USD 0.0933** (one recording of the facilities fixture, 3 calls, measured). No ledger row (a code machine; `ERW_LEDGER=0`). Nothing deployed; no warehouse data written.

- **`warehouse/datacenters/facility_fields.py`** (new): `mw_basis` (it, total, tenant, phase, unstated), `power_kind`, the grid with its basis (named in the stories, or the state's main grid), the county's EIA-861 utility where exactly one serves it, `energized_year`, `country`; the place rules (`has_place`, `place_conflict`) and `description`.
- **`warehouse/datacenters/extract.py`**: the prompt asks for the MW basis, the energized year and the country, one facility per site, the wider status words and the confidence bands; a `same_as` across two places is refused; a facility with no stated place is not kept; an operator that is a description is dropped; every row gets the derived fields on every run (an old row's read from its own values).
- **`warehouse/derived/datacenter_tracker_rollups.py`** (new): facilities and stated MW by grid, state and operator, the series shape, the facilities without MW counted beside each sum and no sum where none states MW; validator pass on the stored table's 501 rows. A step of the daily run after `datacenter_facilities`.
- **The fixture** (`tests/fixtures/datacenters/`, 35 stories, 28 answers, the recording) and **`warehouse/datacenters/eval/dc_fixture.py`**; **`tests/test_session2236_deals.py`** (14 tests). Before and after in the audit file: no-place facilities 2 to 0; two places in one row 6 to 0; state 3 to 1; status 3 to 1; one facility now missed.
- **Method notes**: `docs/methods/datacenter_projects.md` (the columns and rules of this session), `docs/methods/datacenter_tracker_rollups.md` (new); `docs/methods/deal_counterparties.md` corrected (below).
- **Tests**: 2236 with 166, 2232 and 2235: 45 passed; every test file that reads the facility tables, the deals or the license file (the license tests among them): 883 passed, 17 skipped.

## Decisions made without you

1. **Session 2234's license row was not in its commit** (`scripts/licenses.py status` had rewritten the csv after the row was added, and dropping it; the json entry stayed). Found here by `test_session207` and `test_session410`. Neither new table (`deal_counterparties`, `datacenter_tracker_rollups`) gets a row now: session 410's test holds every row of `license_status.csv` to a table `coverage.csv` holds, and only the data machine's build puts them there. The csv and the site's copy are main's again; both method notes say the row is written at the first build; no live set, page or download reads either table until then. The step for the desktop is in the chain's note.
2. **A facility needs a stated place**, even when the model names an operator: the trade is one real facility lost on the fixture (DataOne's "NJ data center", whose state the model did not return) against two non-facilities kept. The prompt asks for the state; session 2249 reads the count again.
3. **The MW of any basis is summed** in the rollups, with the basis on each facility and the page to say so: the stored rows state no basis yet, so a sum of one basis alone would be empty until a re-extraction.
4. **The grid read from a state** is the site's own reading (`STATE_GRID`), marked `grid_basis` state, never presented as the story's.
5. **The gazetteers are not read in the fixture** (the place lookup is session 16's, graded elsewhere); the fixture fakes them to stay offline.

## For Samuel's ruling

1. Whether the two derived tables (`deal_counterparties`, `datacenter_tracker_rollups`) take the hold of their parent tables in `license_status.csv` at their first build, as this chain assumes.
