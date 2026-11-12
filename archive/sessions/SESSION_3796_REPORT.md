# Session 3796 report: the FERC-714 cross-check's map, eleven planning areas outside the ISOs

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 16:45 to 16:55 UTC. Opus 5.5. Model spend USD 0. Requests: EIA's API, 22 of 30.

## Read these first

- **Eleven non-ISO planning areas are mapped** in `docs/methods/ferc714_forecast_growth.md`, a new section beside the seven ISO rows. Each sets the respondent's 2025 forecast (the higher of summer and winter, filed for 2024) beside its balancing authority's highest 2025 hour in EIA-930, under the ISO rows' own neighbour and range tests.

| BA | Forecast (MW) | Actual (MW) | Forecast less actual |
|---|---|---|---|
| TVA | 32,838 | 35,086 | -6.4% |
| DUK | 21,216 | 21,931 | -3.3% |
| CPLE | 14,457 | 14,209 | +1.7% |
| FPL | 26,306 | 28,963 | -9.2% |
| FPC | 10,366 | 12,583 | -17.6% |
| AZPS | 8,491 | 8,499 | -0.1% |
| SRP | 8,528 | 8,784 | -2.9% |
| BPAT | 12,185 | 11,537 | +5.6% |
| PSCO | 7,974 | 9,079 | -12.2% |
| NEVP | 7,226 | 9,239 | -21.8% |
| LDWP | 6,226 | 5,356 | +16.2% |

- **The large gaps are boundaries, said so in the note.** A balancing authority balances every utility inside it; a planning area is the respondent's own. NV Energy's authority holds Sierra Pacific's load as well as Nevada Power's. The rows are an order-of-magnitude check; the ISO rows remain the test of forecasting skill.
- **Two faulty EIA-930 hours were left out by the tests:** APS 10,529 MW (2025-02-13T23, between 7,850 and 4,210) and LADWP 5,823 MW (2025-02-01T00, between 2,916 and 2,752).
- **Southern Company has no 2024 filing in the table:** left out, said so.
- **Not a warehouse table:** the figures are a method note's cross-check. `replication/ferc714/ba_peaks.py` reproduces them, offline from the saved pages with `--raw`. The pages are under `warehouse/raw/eia930_ba_peaks/20261112T164614Z/`.
- **Why EIA-930 and not FERC-714's own hourly actuals:** `ferc714_area_demand_*` is held internal until a person rules, so a public note does not quote it.

## Decisions made without you

- **The same tests as the ISO rows:** the neighbour and range tests of `demand_growth.py`, not a new rule.
- **One year (2025):** the cap of 30 requests holds eleven authorities for one year. The ISO rows hold three years.
- **The mapping is by name, not by a code.** FERC-714's respondent table carries EIA's utility id, not the balancing authority code.

## For Samuel's ruling

- None.
