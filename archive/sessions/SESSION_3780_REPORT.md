# Session 3780 report: FERC-714 forecast growth and the EIA-860M pipeline, second pass (parked 193)

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:48 to 13:56 UTC. Opus 5.5. Model spend USD 0. Requests: none. Both tables already stand on the newest inputs, so nothing was rebuilt and no data lock was needed.

## Read these first

- **`ferc714_forecast_growth`: skipped, as the chain's file allows.** Chain 211's sessions 3758 and 3759 built it on 12 November from the newest filing year FERC-714 holds (report year 2025): 198,354 rows, 168 planning areas, archive `20261112T112909Z-local`.
- **The cross-check's unmapped planning areas cannot be mapped from what the warehouse holds.**
  - The cross-check needs each area's actual peak hour. The warehouse holds hourly peaks by balancing authority only for the seven ISOs and US48 (`eia930_demand_growth`).
  - `eia930_daily_demand` holds all 71 respondents, but as MWh a day, which gives no peak hour.
  - So the map stays at the seven ISO respondents. The method note already names the unmapped classes (members inside an ISO; balancing authorities with no demand-growth row; PJM's six hub respondents).
  - Mapping the non-ISO utilities (TVA, Duke, Southern, FPL and the other western balancing authorities) needs EIA-930 hourly demand by balancing authority for those respondents: a new pull of a source already held, carried to the next file.
- **`generator_pipeline_by_grid` is on the newest EIA-860M month:** vintage 2026-09 (retrieved 24 October; EIA's October update is due late in November). The table was built on 6 November from it, so there was nothing to rebuild.
- **The datacenter-tagged rule matches nothing.** Its pattern (a plant or owner name with "data center", "datacenter", "lab" or "laboratory") tags 0 planned generators in 2026-09 and in 2026-08, so `datacenter_mw` is 0 in every cell.
  - A wider read of the 2,361 planned generators found no plant or owner named for a hyperscaler or a compute campus either (compute, hyperscale, Meta, Google, Amazon, Microsoft, xAI, Stargate, Crusoe, Oracle, OpenAI, Digital Realty, Equinix, QTS, Vantage, CoreWeave, campus).
  - EIA-860M names a plant by its project or utility, not by the load it serves.
- **The "came online" cross-check against EIA-923** was not read again: neither input has moved since the table was built.

## Decisions made without you

- **No rebuild on unchanged inputs:** each would rewrite the same rows with a new retrieval time.
- **The datacenter rule is left as it is,** although it matches nothing. A wider name list would tag generators by guesswork; the variable stays, and it reads 0 honestly.

## For Samuel's ruling

- **`datacenter_mw` in the pipeline table** is 0 everywhere because EIA-860M does not name the load a plant serves. Recommendation: drop the variable at the next rebuild, or tie it to the datacenter tracker's facilities by plant ID when the tracker carries one. Default: kept, reading 0.
