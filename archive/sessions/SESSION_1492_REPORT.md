# Session 1492 report: the datacenter's replication, in Stata, and the method note

Energy Research Warehouse (ERW), session 1492, chain 158, samueloldlaptop, 6 November 2026, 09:00 to 09:06 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1487-replication`.

## What it did, with commits

- `6d37e0c86`:
  - `replication/datacenter/replicate.do`: the page's public do-file, generated as the other two were. Its three reads (the hourly file twice, the carbon file once) take the repository's paths; its three defaults come from `assumptions.csv`; it ends with the energy price and the GPU-hour beside the page's.
  - `assumptions.csv`, `page_figures.csv`.
  - The defaults' sources as the do-file names them: NVIDIA DGX H100, 8 GPUs at 10.2 kW; the Uptime Institute's Global Data Center Survey 2024.
  - `docs/methods/datacenter_pays_algorithm.md` section 8.1, "Run it": the known difference named, and pointers to the "Cross-checks" table and the decisions block (section 12).
- Tests: `tests/test_session1492.py`. With 1488's and 1490's: 18 passed.

## Found

- The do-file opens with `clear all` before the defaults are read, and its later `clear` and `preserve` keep scalars, so the defaults from the file hold to the end.
- **The do-file has not been run** (no Stata here).

## Decisions made without you

- None.

## For Samuel's ruling

- Your Stata run of `replication/datacenter/replicate.do`.
