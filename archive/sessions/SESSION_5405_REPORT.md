# Session 5405 report: chain 255, two more published counterparts in the generator's cross-check table

Energy Research Warehouse (ERW). Chain 255, portable laptop window P1, 13 November 2026, about 20:55 to 20:59 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read`.

- From ERCOT's market monitor's 2025 report (read this evening; its text extracted, quoted, not copied):
  - **The default case's price received** (23.27 USD per MWh, solar at the hub average, October 2025 to September 2026), "No published counterpart held" until now, beside the report's "average captured price for solar at $21 per MWh" in 2025 (pages 19 and 20): +2.27, the hub against each plant's node (the report: congestion lowers nodal prices "in regions with high renewable capacity") and twelve months against calendar 2025.
  - **A new section, ERCOT's gas peaker in 2025** (the page's "Price years", 50.42 USD per kW): beside "Net revenues for a CT were $52.59 per kW-year" (page 103), -2.17, within 5 percent, theirs with reserves and node prices; and beside "The peaker net margin in ERCOT reached almost $79 per kW in 2025" (page 97; defined on page 98), about -28.58, a unit counted in every interval it would profit, with no run rule.
- The table's count of figures with no counterpart: eight of 13 (was nine).
- **Tests:** `tests/test_session5073.py` holds the three new gaps and reads the new table's header; with `tests/test_session3707.py`: 29 tests, OK.

## Decisions made without you

- A whole year (2025) of the peaker, from the page's "Price years", is set beside the report's year; the year is whole, so the table's build of 20 October does not move it.

## For Samuel's ruling

- Nothing new.
