# Session 2550 report: two more held tables described (datacenter_projects, a note of its own; datacenter_queue_positions, linked to the facilities note)

24 October 2026, about 23:06 to 23:14 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2550.out`). Model spend USD 0. Pulls: none.

## Read these first

- **17 held tables have no note on main** besides this chain's own (session 2536's list; this chain's `derk_bih_electricity_annual` gets its note in session 2555). **The unlanded chains hold notes for eight of them:** chain 119 links `cost_of_power_monthly`; chain 120 links the policy monitor's `policy_actions`, `policy_reads`, `policy_reads_evidence` and `large_load_rule_reads`; chains 118 to 120 each describe `ercot_all_hub_prices_history`, `iso_hub_prices_history` and `iso_rtm_hub_prices`. Those are left alone here, so that their landings meet no second link.
- **Two described:**
  - **`datacenter_projects`**, a note of its own (`docs/methods/datacenter_projects.md`), written from its builder `warehouse/datacenters/extract.py` and checked against the table: 156 rows; `entity_id` `datacenter:<16 hex>` on every row; `capacity_mw` equal to `mw` on every row (43 stated); status planned 56, under construction 13, withdrawn 7, operating 5, empty 75; placed by county 7, by place 16, not placed 133; `ai_power` true throughout; the checks, the deduplication rule of session 166 and the license as the builder states them.
  - **`datacenter_queue_positions`**, whose header names `docs/methods/datacenter_facilities.md` as its method and whose section "Queue rows" there describes it: a `Tables:` line added to that note.
  - Their Method cells set in `docs/coverage.md` (`runs/c125/s2550/cells.py`).
- **Left (seven):** `ai_power_regions`, `ba_supply_monthly`, `news_index`, `news_stories`, and the three large-load tables (`large_load_rules`, `large_load_rules_internal`, `large_load_statements`), each needing a note of its own.
- **Tests:** the 1,385 tests that read the notes, the cells or `docs/methods` pass but for test 705, the worktree artifact (`runs/c125/s2550/tests.out`).

## Decisions made without you

- **Tables the unlanded chains describe are not linked again here.**
- **Two, not six:** the four others need notes written from large builders (the news pipeline, the AI power regions), better a session each.

## For Samuel's ruling

- None.

## Files

- New: `docs/methods/datacenter_projects.md`, this report.
- Changed: `docs/methods/datacenter_facilities.md` (its `Tables:` line), `docs/coverage.md` (two Method cells).
- On the data machine only: `runs/c125/s2550/`.
