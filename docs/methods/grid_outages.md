# Generation out of service, as SPP and CAISO publish it

Chain 601, part D (session 9000, 20 November 2026). Connector: `warehouse/connectors/grid_outages.py`. Table: `generation_outages_hourly` (the chain named it `generation_outages`; the data standard asks a name of three parts). The ground: `docs/reviews/grid-conditions-sources-2026-11-20.md`.

## What a reader gets

- **SPP:** the megawatts of generation on outage in each hour, by balancing area (SPP, SWPW and SPP's own Total) and by fuel (coal, oil, hydro, gas, nuclear, solar, waste, wind, waste heat, other), from 2025 (deepening a year at a time toward 2016).
- **CAISO:** the megawatts curtailed in each hour of its balancing area, planned and forced, from its daily report of the prior trade date (from 2026, deepening toward 17 June 2021).
- **Nuclear in every grid:** the NRC's daily power level of each reactor, `nrc_reactor_status` (held since 2020), stands beside these on the conditions page; it is a federal record and needs no license.

## Sources

| Operator | Report | Address |
|---|---|---|
| SPP | Capacity of Generation on Outage (`spp:CAP-GEN-OUTAGE`), one csv a day | `https://portal.spp.org/file-browser-api/download/capacity-of-generation-on-outage?path=/YYYY/MM/Capacity-Gen-Outage-YYYYMMDD.csv`; archived years `/<year>/<year>.zip` |
| CAISO | Curtailed and Non-Operational Generator Prior Trade Date Report (`caiso:CURTAILED-NONOP-GEN`), one workbook a trade date | `https://www.caiso.com/documents/curtailed-non-operational-generator-prior-trade-date-report-<date>.xlsx` (the date written `YYYYMMDD`, except 2024-05-31 `2024-05-31` and 2024-06-01 to 2025-01-12 `mon-dd-yyyy`; 2024-06-01 has "and" in the name). Not under `/resources/`, which CAISO's robots file disallows |

## Decisions

1. **SPP's hours.** SPP's file of a day is published that morning and holds the hours from 03:00 Central of that day through the next six days. An hour is taken from the newest file published on its own day or the day before, never from a forecast made earlier than that: hours 3 to 23 from the same morning's file, hours 0 to 2 from the day before's.
2. **CAISO's hours.** Each row of the report is one curtailment interval of one outage: start, end (empty while it goes on), megawatts, planned or forced. An hour's figure is the sum over rows of the megawatts times the share of the hour the row covers, clipped to the trade date; an empty end runs to the end of the trade date. A row printed twice (same outage, start, end and megawatts) counts once. Where one resource's rows add to more than its Pmax in an hour, they are scaled down to its Pmax in proportion (none did in the trial of 14 to 18 November 2026).
3. **What CAISO counts.** The report holds every curtailment of a resource: planned maintenance, forced outages, and derates the operator files as forced (ambient conditions, transmission induced, fuel). The table sums them as printed and does not separate the kinds of work. In the trial, CAISO's hourly total averaged about 21,400 MW (7,400 planned, 14,000 forced).
4. **No forecast.** SPP's outlook for later days is not kept. CAISO's report is of a day already past.
5. **Never filled.** A (place, variable, day) is written only when every hour of the operating day is there. A missing document is a gap, named in the header.
6. **Not asked:** ERCOT (its outage reports are on paths its robots file disallows; the owner's ruling 2 of 6 November 2026), PJM (paid license), NYISO and ISO-NE (written permission), MISO (paused).
