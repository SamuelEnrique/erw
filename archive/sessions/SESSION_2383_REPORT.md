# Session 2383 report: Canada's annual energy balance by province and fuel (Statistics Canada, table 25-10-0029-01), the third own choice

24 October 2026, from 09:09 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. It runs before session 2382 so that the records include its table. Precheck passed (`runs/c112/pre2383.out`). Model spend USD 0. Pulls: 2 of 20 (below).

## Read these first

- **One public table:** `statcan_energy_balance_annual`, from Statistics Canada's table 25-10-0029-01, "Supply and demand of primary and secondary energy in terajoules, annual" (the Report on Energy Supply and Demand). It is written, validated, archived, in coverage (sectors power, gas, oil and coal), and held from the live set and the release. 128,420 rows, 354 series, 1995 to 2024:
  - for Canada, each province and territory, the Atlantic provinces together and the three territories together;
  - 28 fuels with values (StatCan's 29, anthracite having none; session 2380 corrected "29"), from coal by rank, crude oil, natural gas and NGLs to refined products, steam, primary and secondary electricity and renewable fuels;
  - 46 supply and demand lines: production, trade, inter-regional transfers, stock changes, transformation to electricity, coke, refined products and steam, producer consumption, non-energy use, and final use by industry, transport, agriculture, residential, commercial and public administration.
  - In MWh (StatCan's terajoules times 1,000,000/3,600; terajoules are not in the ERW's unit list).
  - The two groups of provinces or territories have a blank geo; StatCan's ended series are marked `x_terminated`.
  - 49,530 confidential cells and 32,103 not available have no row.
  - Fuels and lines overlap (totals hold their parts), which the header says.
- **Why this one:** it is the yearly balance behind this chain's monthly electricity trade and petroleum products tables, and the ERW holds no Canadian energy balance.
- **License:** Statistics Canada's Open Licence, on record (public). The robots file asks a crawl delay of 2 seconds (kept) and names no AI agent (read 620).

## The cross-check (`runs/c112/s2383/cross.py`, `cross.out`; tables read past their header lines)

- **Primary energy production:**
  - The Atlantic provinces equal Newfoundland and Labrador, Prince Edward Island, Nova Scotia and New Brunswick in all 25 years within 0.1 per cent.
  - The provinces and territories equal Canada in all 17 years where none is suppressed.
- **Canada's hydro and nuclear production against `statcan_electricity_generation_monthly`'s hydraulic and nuclear turbines:** the balance is 33 to 55 TWh a year higher (2017: 519.80 against 486.50 TWh; 2024: 478.54 against 423.56). The balance's "primary electricity" may count generation the monthly survey classes elsewhere. Session 2380's note found that from 2016 to 2024 the gap equals the generation table's wind, solar and tidal generation within 4 TWh a year (2024: 54.98 against 51.08 TWh): the balance's primary electricity appears to hold them, though StatCan's metadata does not say so. The header now says so.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www150.statcan.gc.ca | 2 of 20 | robots, the table's zip (2.8 MB); 6 s apart (the probe log; this line first said 3) |

## Errors

- **The write's metadata step ended with exit 1** (`runs/c112/s2383/write.out`): its patch met the branch's newer rows in coverage, the manifest, `docs/coverage.md` and sources. They were joined by `runs/union_resolve.py` (`runs/c059/resolve.sh`), and each table is once in each file; nothing is missing. This line first said "None" (session 2380).

## Decisions made without you

- **StatCan's energy balance chosen** as the third own choice.
- **Terajoules written as MWh;** the groups of provinces and territories kept, with a blank geo.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/statcan_energy_balance.py`
  - `tests/test_session2383.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (620), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c112/s2383/`, `runs/license_reads/s2383/`.
