# Session 7015 report: the done-line data requests 12, 16, 17 and 18; ERCOT's hub days filled from the node pull

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## Request 12: the ERCOT peak premium

- The builder refused October 2026: HB_BUSAVG held 2,880 of 2,976 intervals. ERCOT's real-time hub history lacked five whole Central days, 15 October and 5 to 8 November 2026 (576 rows each): days the runner missed while ERCOT listed them, and the live table lacked them too.
- **At the cause**: `hub_history.py append-ercot` (the data machine's daily step) now takes a wholly absent Central day from `ercot_rtm_node_prices`, which this machine pulls each day from the same ERCOT report (NP6-905-CD lists every settlement point, the hubs among them). Before using it the two tables were compared on every interval both hold: 24,750 of 24,750 equal to the cent. A day is taken only when it is wholly absent from both hub tables and the node table holds every interval of it for every hub; each row keeps its own source, source_url and retrieved_at, and the member's header says so. Test 7015_hub_fill.
- Run under the lock: 2,880 rows filled; the peak premium rebuilt (months to November 2026); `ercot_all_hub_prices_history` and both premium tables validated (exit 0), covered, archived (3,280 rows); the premium loaded (113 annual and 287 monthly rows written). Snapshots `before-load7015` and `after-load7015`: 0 differences.

## Requests 16 and 17: the queue statistics

- This machine's queue tables were of 19 October (NYISO 26 September) while the archive held the runner's pulls of 5 November; the four newer copies were restored and put in place under the lock.
- `queue_statistics.py` writes 0 MW for a status with no position (request 17; positions without a figure stay unwritten). Rebuilt: 1,734 rows (1,511 before), validated, covered, archived, loaded (336 written). Snapshots `before-load7015b`, `after-load7015b`: 0 differences.
- **At the cause**: no schedule ran the builder. A weekly data machine step (`dm_queue_statistics`) builds it from the six queues rebuilt from the archive into `runs/queue_inputs` (`--restore`), never from a mix of dates. Test 7015_queue_statistics.
- The profiles of session 7014 were moved into the same weekly table steps (`dm_mix_profile --snapshot`, a new `dm_curtailment_profile`), so each table is built once and stored with the block's stores and weekly load; their page files' tests run as a group in `run_data_machine.sh` on a week they ran. Tests 247 and 310 follow.

## Request 18: the interconnection explorer's replication

- Run from `wip/7509-interconnection` against the rebuilt table: part A 823 of 823 figures; part B every row equal but the 223 rows of request 17's 0 MW (exactly the table's growth), which the laptop's script still reads as not held. The script needs request 17's rule.

## The landing

- Gate f on `wip/c301-tail` (`f04c808e3`) started at 13:43 UTC, before the pause of 14:00 to 16:15; it lands after 16:15.

## For Samuel's ruling

- None new.

## Needs the key

- Unchanged: the deals' re-extraction (about USD 3), the policy BOEM read (about USD 0.02), the attention reclassification (about USD 0.10), the datacenter re-extraction (about USD 0.70).
