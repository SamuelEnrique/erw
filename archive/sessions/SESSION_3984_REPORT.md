# Session 3984 report: the chat's data requests (docs/state/data_requests_ask.md)

Energy Research Warehouse (ERW). Chain 279, data machine (lab-desktop), 15 November 2026 from 02:00 UTC. Opus 5.5. Model spend USD 0. No request to a publisher.

Taken early under the no-waiting rule (sessions 3984 to 3987's step) while sessions 3979 to 3983 wait for the runs of 15 November. A new request file reached main at 18:50 UTC on 14 November (the old laptop's chain 280, session 6113): six rows.

- **Row 1 (`forecast_tool_parameters`, 768 rows) and row 2 (`iso_reserve_margin_reports`, 5 rows):** both join the live set whole, under `review_hold` (`warehouse/supabase/live_set.yaml`, as `impact_tax_rules` did in session 346): the catalogue lists them, no page reads them. Both public (verdict public; the first in release v1). The 401 test files that read `live_set.yaml`: 2,151 passed. The load itself follows the landing, from the main checkout under the data lock.
  - **Gate f** (`wip/c279-land-f`): every step passed (suite 9,510 OK at 02:25 UTC); **landed at `a2c908cd4`** (run 43669093846); snapshots `before-d7c3604c` and `after-d7c3604c`: 0 differences.
  - **The load** (03:01 UTC, `lock.py run` with `load.py --only '^(forecast_tool_parameters|iso_reserve_margin_reports)$'`; the dry run first: 773 rows): database gate open (0.36 s); both tables "match" (768 and 5 written, 0 deleted); the catalogue reads `in_live_set` review for both; `pg_database_size` 1,535.1 to 1,535.3 MB. Snapshots `before-load3984` and `after-load3984`: 0 differences.
  - **The loader exited 1** on one line, not these tables: "MISMATCH sources: CSV 739, Supabase 740", the old IEA source row with its en dash, which session 3940 folded out of `sources.csv` and which only `load.py --prune` (a person's command) deletes. Every daily load will print the same until then.
  - **pj10's re-key** (the chat's evaluation) left to the chat's chain: its key names the row that answers, and which place's cost answers "a new combined-cycle gas plant" is the evaluation's choice. A run of `platform_questions.py --help` wrote its two evaluation files in the main checkout (the script reads no flags); both put back as committed at once, the lock free.
  - **Marked** at `91a04da40` (rows 1 and 2 done, 5 answered, 6 waits; snapshots `before-markask` and `after-markask`: 0 differences).
- **Row 3** (the three research tables) and **row 4** (`deal_counterparties` beside its held parent): wait for the owner, as their rows say. Nothing done.
- **Row 5 (the two license files):** they answer different questions. `site/data/license_status.json` lists only the tables held on the site ("license needed"); a table absent from it is public to the chat's hold. `site/data/table_verdicts.json` (written by `package/tools/build_tables.py` from the license record) gives every table's verdict, "unsettled" for the eight. The stricter rules: an unsettled verdict means the table is not redistributed, so none of the eight is loaded into the live set, and today none is. Making the two agree means writing the eight into the hold file, which is ruling 4's open question on the research tables (chain 267's note). Under "For Samuel's ruling".
- **Row 6 (`deal_counterparties`, 527 in coverage, 532 in the archive):** coverage's 527 is the run of 12 November (the last daily commit on main); the run of 13 November wrote 532, and its commit was refused. The next daily commit to land (15 November) brings coverage to the table's count. Waiting.

## Decisions made without you

- **The two small public tables loaded under review_hold** rather than waiting for a page: the request is the chat's, and review_hold keeps them off `/data`'s public list.

## For Samuel's ruling

- **Which license file rules for the eight tables public in the hold file and unsettled in the verdicts** (Ask request 5). Default: the verdict rules (the stricter): none of the eight enters the live set until its terms are settled; the hold file unchanged until ruling 4's research tables are decided.
- **`load.py --prune`** to delete the one stale source row in Supabase (the IEA's name with an en dash). Default: not run (a person's command; it also deletes rows of tables no live-set rule matches); every load prints the mismatch and exits 1 until it is.
