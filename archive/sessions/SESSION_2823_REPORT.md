# Session 2823 report: Croatia's transmission network a year from 2017 (HOPS, Elektroenergetski podaci)

26 October 2026, from about 06:48 to 06:53 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2823.out`). Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 by the connector's online trial); one web search.

## Read these first

- **`hops_croatia_annual` is new:** HOPS's "Elektroenergetski podaci", the transmission network's yearly figures, 2017 to 2025:
  - production by source (hydro, thermal, wind, solar) and its total;
  - imports (half of Krško's output included), exports and the net;
  - the energy carried;
  - the system's peak and minimum load (MW, with the day and hour as printed);
  - consumption without losses, losses, and deliveries to customers on the network.

  126 rows, 9 years. The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2829's draft.
- **Its licence is internal:** HOPS links no terms of reuse (read 1643), and its home page calls its live figures informative only. Session 2825's round looks further.
- **Figures:**
  - 2024: production 11,924 GWh, imports 13,010, exports 7,951; the peak load 3,363 MW (17 July, 20 h).
  - 2025: wind 2,883 GWh, up from 1,088 in 2017.
- **The page's own balances** (20 of 36 hold within 1 GWh):
  - the sources make the total, and imports less exports make the net, every year;
  - **from 2018 the energy carried exceeds both production plus imports and consumption, losses plus exports, by the same amount:** 102 GWh in 2018 rising to 372 in 2025. That is an inflow the page does not name, kept as published, counted, and listed in the run log.
- **Cross-check:** against `eurostat_electricity_production_annual` (all of Croatia):
  - HOPS's hydro is 86 to 96 per cent of Eurostat's (2024: 5,847 GWh against 6,727);
  - its wind is 92 to 98 per cent (2024: 2,419 against 2,577);
  - its solar is 46 GWh against 820 in 2024, since most solar is on the distribution network, which this table does not cover.
- **Reading the page:** a dot is its thousands separator ("4.809" GWh is 4,809 GWh). The loads' "MWh/h" is written as MW.

## The requests

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.hops.hr's and hops.hr's robots files | HTTP 404, no robots file |
| 3 | the Elektroenergetski podaci page (probe) | 200, one table |
| 4 | the same, into the connector's raw folder | 200 |

Reads recorded: 1641 to 1643.

## Decisions made without you

- **The unnamed inflow kept,** counted, not given a row of its own.
- **Licence internal** until HOPS's terms are read.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/hops_croatia.py`
  - `tests/test_session2823.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1641 to 1643) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2823/`, `runs/license_reads/s2823/`;
  - `warehouse/raw/hops_croatia/`.
