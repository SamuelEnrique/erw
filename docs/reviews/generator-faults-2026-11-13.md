# What a generator earns (`/cost-of-power/seller`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5002. Read on the local production build of session 5001 (`wip/5000-battery`, the generator page unchanged from main) in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | Method note, section 10, item 3 | "No builder of this page is scheduled ... Open": session 204 made the model, the hub files, the hybrid and the download daily steps of the data machine (`warehouse/scheduled.py`), so the item the sign-off leaves open is already closed | The row reads "Closed by session 204", names the four steps and the capture file's builder, and keeps session 183's text after it | fixed (session 5002) |
| 2 | The page's figures, and the battery page's | The last twelve months end September 2026 on both pages on 13 November; the generator's snapshot (`site/data/merchant_snapshot.json`) was built 4 October 2026, and the battery page draws 2026 as nine months. October 2026 is not yet a held month for either model | Not the code machine's: the daily builders exist (row 1); why October is not held (a month under 90 percent of its days or hours, or a builder refusing) is the data machine's to read in its run log | data machine |
| 3 | The page's foot | The decisions block starts closed | Not a fault: the generator page is not under the battery's "nothing collapsed" ruling, and the block is session 463's form | not a fault |

## The read (session 5001's build)

| View | 1280: width, keys, errors | 390: width, keys, errors | Decisions block |
|---|---|---|---|
| `/cost-of-power/seller` | 1265, 180, 0 | 390, 180, 0 | `463`, closed, 23 lines |

No broken text ("NaN", "undefined", "null%", "license needed%"). Nothing scrolls sideways at 390.

## The done line after session 5002

| Item | State |
|---|---|
| Method note | complete for signature (sections 1 to 13, the sign-off block); unsigned: the owner signs; section 10 holds the items it leaves open, item 3 now closed |
| Replication | `replication/generator/replicate.py` from the public CSV, 13 of 13; the do-file never run (no Stata on this laptop) |
| Cross-check table | `docs/methods/crosschecks/generator.md`, current |
| Decisions block | `GENERATOR_DECISIONS` on the page and the note's section 13, word for word (`tests/test_session463.py`) |
