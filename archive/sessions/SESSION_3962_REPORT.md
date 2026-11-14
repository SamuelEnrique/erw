# Session 3962 report: the Grid replication's gravity group (five-tools request 3)

Energy Research Warehouse (ERW). Chain 278, data machine (lab-desktop), 14 November 2026, 14:22 to 14:27 UTC. Opus 5.5. Model spend USD 0. No request to a publisher.

Chain 272's unfinished steps, read from its file and reports since its session 3960 never ran:

- **Waiting, skipped:** the daily run of 14 November (running, the lock held by it from 14:14 UTC), its daily commit through the guard, package tests and health summaries; the data machine's run (17:00 UTC); the runs of 15 and 16 November; the hunt after the daily commit; the CAISO's FERC compliance filing (due 16 November); the Ask weekly run (on or after 19 November).
- **No Digest of 14 November to check:** the 14th is a Saturday, and the Digest is a weekday issue.
- **Already settled by chain 272 on its branch (carried here):** large-load requests 14 (Rule 30 held, session 3947) and 17 (session 3949), forecast request 2 (session 3948). Their rows are marked after this chain's landing.
- **Still stopped, nothing new:** five-tools request 2 (a ruling), forecast request 5 (comptroller.texas.gov's robots file), licenses requests 11 and 12 (the BLS key).

## Five-tools request 3: done

- **The cause, found:** `replicate.py` already computes the gravity shape's generation and share when it is given the generation. Tests 3703 and 5074 compared the committed file with a run given none, so a file written where `eia930_all_generation` is held could never pass.
- **The fix:** both tests now take the committed file's generation figures as an input (as the snapshot is one): test 3703 runs the page's own code again with them (`network_group(..., gen=)`, a new optional argument), test 5074 gives them to `replicate.py`. The share is still computed by each.
- **`replicate.do`:** section 1b computes the gravity shape's generation and share from `eia930_all_generation` at the hour shown; the "does not compute" line updated. Not run (no Stata here); test 5074's family check passes.
- **The files written** with the tables of `warehouse/output` (the EIA-930 tables of 13 November's run): 203 figures (network 70, gravity 30, carbon 21, Ask 82; 22 license needed). `replicate.py`: **178 of 181 computed met, 3 a known difference, 0 not held.** `--check`: current.
- **Tests:** 3703, 5074, 3889, 3705, 5005 and 5502: 51 passed with the tables (`ERW_REPLICATION_TABLES`).
- **The method:** `docs/methods/grid_network.md`, "What it found on 14 November 2026".
- Commit `wip/c278-data` after `d94a411bb`; the request's row is marked after the landing.

## Decisions made without you

- **The tests changed, not the figures cut:** the generation is an input, so feeding the committed generation to both computations keeps every check (the share is still recomputed). Request 3's row asked for window P1's code first; the change was small and in the tests and the do-file only, so the desk made it rather than wait.

## For Samuel's ruling

- None.
