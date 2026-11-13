# What a datacenter pays (`/cost-of-power`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5003. Read on the local production build of session 5001 (the page unchanged from main) in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. The file is named `datacenter-cost-` so that it is not taken for the datacenter tracker's (`datacenter-faults-2026-11-11.md`). States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | `site/lib/datacenter.ts`, `weights()`; the decisions line "foreseen"; the note's section 10, item 15 | The owner ruled on 12 October 2026 that "if perfectly foreseen" takes the rule's hour budget in a partial year (`docs/roadmap.md`, "Rulings"); the code still pro-rated it (a load of 100 hours got 76 in 2026 against the rule's 100), and the page's decisions block still said "waits for a ruling" | `k = min(hours held, shedBudget(x, hours of the year))`, the recommendation the ruling took; the decisions line and the note's line 7 state the ruling; item 15 closed; the note's worked example recomputed on its frozen inputs (foreseen 29.29, 4.44 less, "the rule kept 51 percent"; day-ahead 30.19), each old figure kept beside it; the test mirror in `test_session190_replication.py` follows. New: `site/scripts/test-foreseen-5003.mjs` and `tests/test_session5003.py`. No default figure moves: the default load is flat | fixed (session 5003) |
| 2 | Method note, section 10, item 4 | "ERCOT's load zones stop on 3 October 2026 ... `run_data_machine.sh` is registered nowhere": the page's last twelve months now run to October 2026 (`replication/datacenter/replicate.py`: 2025-11 to 2026-10), and `price_compare` is a daily step of the data machine since session 204 | The row reads closed by session 204, session 190's text kept after it | fixed (session 5003) |
| 3 | The page's foot | The decisions block starts closed | Not a fault: the datacenter page is not under the battery's "nothing collapsed" ruling | not a fault |

## The read (session 5001's build)

| View | 1280: width, keys, errors | 390: width, keys, errors | Decisions block |
|---|---|---|---|
| `/cost-of-power` | 1265, 249, 0 | 390, 249, 0 | `462`, closed, 21 lines |

No broken text. Nothing scrolls sideways at 390. The default headline (USD 34.07 per MWh, November 2025 to October 2026) equals the replication's.

## The done line after session 5003

| Item | State |
|---|---|
| Method note | complete for signature (sections 1 to 12, the sign-off block); unsigned: the owner signs; section 10's open items are his, item 15 now closed by his ruling |
| Replication | `replication/datacenter/replicate.py` from the public CSV, 14 of 14; the do-file never run (no Stata on this laptop) |
| Cross-check table | `docs/methods/crosschecks/datacenter.md`, current |
| Decisions block | `DATACENTER_DECISIONS` on the page and the note's section 12, word for word |

## The wider read (session 5008)

Session 5004's build (which holds row 1's fix), internal view, 1280 and 390: each of the seven grids (ERCOT, CAISO, PJM, NYISO, ISO-NE, MISO, SPP) in the load view and the grids view, and the all-grids view, 30 views; and the load turned off in 100 hours a year. No console error, no broken text, nothing scrolls sideways at 390, a checked figure on every view. `check-values` restricted to `/cost-of-power` and `/research`: 2,873 of 2,873 values match Supabase.
