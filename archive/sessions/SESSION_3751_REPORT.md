# Session 3751 report: main green (with 3752)

Energy Research Warehouse (ERW). Chain 211, sessions 2 and 3 of 24 (3751 and 3752 done as one), data machine (lab-desktop), 12 November 2026 from 09:55 UTC. Opus 5.5. Model spend USD 0.

- **Each failing test root-caused** (`docs/state/main_red_2026-11-11.md`), fixed on `wip/3751-green`, one commit each:
  - `test_session183` (`d7f81e578`): the seller hubs check compared the model's capture price with the capture file's only where their twelve months matched. The data machine rebuilds the capture file daily (twelve to 2026-10); the hub models end 2026-09, so 10 hubs were compared against a floor of 12. The capture file is now read over the model's own twelve months: 26 compared, worst 4.7 percent (bound 6).
  - `test_session502` (`b31b1d062`): since the data machine's board build of 7 November, `board.json` names six held tables in the notes of rows that draw no figure. `scripts/page_tables.py` counted those as reads. It now leaves those notes out. The two tables the board does read (`iso_rtm_hub_prices`, `eia_heat_rates_annual`, both public) were added to the page's `TABLES`; `test_session328`'s count went from 29 to 31.
  - `test_session1139` (`4a27343d1`): the rounding bound for a move's percent. A change of two 4-decimal values can be off by 1e-4, and each percent is rounded to 2 decimals. The builder was right; the bound is now the true one, with the 4 November case and a case that should fail.
- **The guard on the path that broke main** (`121f0dc3e`): `warehouse/run_data_machine.sh`'s `dm_commit` runs `scripts/push_guard.py` after its pull and before its push. A red commit goes to `wip/red-dm-<day>` and the checkout returns to `origin/main` (chain 208's three lines, never added until now). `tests/test_session3751.py` covers it and the hold-note rule.
- **Row 16 merged in** (`e25064e8c`): `wip/3701-sellable`'s three changes (`suite_gate.py`'s traceback handling, `test_session244`'s load by path, `test_session3712`); its tests: 30, OK. It lands with this branch (session 3755's step, done here).
- **The suite green twice on a clean worktree:**
  - `scripts/suite_gate.py --ref` at `add502058`: 8,346 tests passed;
  - the gate's own suite at `4212a70ac`: 8,346, OK (skipped 360).
- **The landing:** see session 3753's report for the gate's end, the push and the snapshots.
- **The hourly and 15-minute workflows** start and pass every time. They write Supabase only and never commit to main, so there is nothing to repair and no GitHub setting for the owner.

## Decisions made without you

- Two tests were wrong rather than the code, and each now checks the rule its figure follows, with the reason in its commit:
  - 1139: the rounding bound;
  - 183: compare over the same months.
- For 502, the reading tool was wrong to count a held row's note as a read. Two real reads were missing from the page's list, and they were added. This changes what the board's license line and downloads list (two public tables more); the page is in review, so no visitor sees it, and no figure moves.
- Row 16 was merged into this branch, so one gate lands both.

## For Samuel's ruling

- None new.
