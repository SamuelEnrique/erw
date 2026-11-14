# Session 3947 report: PG&E's Rule 30 held, the tab's two files rebuilt

Energy Research Warehouse (ERW). Chain 272, data machine (lab-desktop), 14 November 2026, 13:26 to 13:35 UTC. Opus 5.5. Model spend USD 0. No request to a publisher (Redivis's API for the draft).

Taken early under the no-waiting rule: sessions 3946 and 3948 to 3950 wait for the runs of 14 to 16 November.

- **Large-load request 14 cannot be done as asked:** the CPUC's Decision 25-07-039 orders the interim Rule 30 but prints none of its four timed steps (the research pass's own row says so), so they cannot be re-cited there.
- **So row 8's default applied to the connection rules too:** `large_load_connection_rules.py` now holds a document with `license: internal` (kept in the registry, named in the header, its steps not written), as the tariffs connector does. It writes the table whole from the registry (a merge would keep held steps). PG&E's Rule 30 held. Test 2924: a held document gives no row and no problem; any other license is still refused; counts 85 steps. The siting test files: 259 passed.
- **Rebuilt under the data lock:** 85 rows (4 keys deleted), validated, archived, in coverage, on the Redivis draft.
- **The All grids tab's files, rebuilt from the tables** (`siting_page.py`'s own builders, these two files only):
  - `conn_rules.json`: CAISO 11 to 10 steps (Rule 30's 4 out, the Board's decision's 3 in), PJM 20 to 22 (FERC's ER26-3515 order);
  - `tariffs.json`: without the fourteen schedules held in session 3937.
- **The method:** `docs/methods/large_load_connection_rules.md`, "Chain 272".
- **Gate i** (chain 272's branch) started at 13:31 UTC; it lands after 16:15 UTC (no landing during the daily run's window).

## Decisions made without you

- **The tab's two files rebuilt alone,** since their tables changed today; the other siting files untouched.

## For Samuel's ruling

- **PG&E's Rule 30 held** (pge.com's terms). Default: held until a commission's copy prints its steps.
