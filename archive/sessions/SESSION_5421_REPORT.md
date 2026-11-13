# Session 5421 report: chain 261, step 6, the battery's CAISO case beside its market monitor

Energy Research Warehouse (ERW). Chain 261, portable laptop window P1, 13 November 2026, about 21:12 to 21:18 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read`.

- **The battery's cross-check table gains a CAISO section** (4 hours, 2025): the page's model on the day-ahead schedule, 85.59 USD per kW, beside CAISO's market monitor's own model, 77.3 (Table 1.8 of its 2025 annual report): +8.29; run the monitor's way (session 246), 84.72: +7.42; perfect foresight, 92.00: +14.70; and the real fleet, energy "nearly $35" and regulation "$9" per kW-year, beside the model's 42.31 and 42.25: +7.31 and +33.25, the gap being regulation. The published figures are quoted as `docs/methods/battery_stack.md` (session 246, after the host's robots file) holds them; nothing new was fetched. The page's own 2025 figures (85.59, 92.00) differ from session 246's (85.34, 91.74) by the day added since (2 November 2025).
- **Tests:** `tests/test_session5073.py` holds the five new gaps; with 3707: OK.

## For Samuel's ruling

- Nothing new.
