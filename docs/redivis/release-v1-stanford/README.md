# Energy Research Warehouse (ERW), version 1

The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets. Every source is reshaped into three standard table shapes so that tables can be joined and compared: `series` (one row per observation: entity, variable, ts_utc, value), `entities` (one row per physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC; power is MW and prices are USD per MWh unless a `unit` column says otherwise. The data standard: https://github.com/SamuelEnrique/erw/blob/main/docs/datastandard.md

**Version 1 holds 190 tables** (14 entities, 3 events, 173 series) and three metadata tables (`erw_coverage`, `erw_sources`, `erw_headers`). Every table's description is its provenance header: the source report, its address, when it was retrieved, the method, and its license line.

## What is not in it

0 tables of the warehouse's public draft are not in version 1: a table whose publisher's terms ask for permission or a license that has not been recorded is held from 2026-10-21 (the ERW's license record, https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md), and retired tables and the old members of consolidated tables are not tables of the warehouse. Tables licensed for internal use are never in this dataset.

## How to cite

Cite the organization that published the data, then the ERW table and this version. For example:

> U.S. Energy Information Administration (EIA). Spot prices. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, Redivis dataset `datapages.erw`, version v1.

Each table's own citation is in `docs/redivis/release-v1/tables.csv` in the repository.

## How it is made

One connector per source pulls, reshapes and validates; the validator is the gate a table passes before upload. Uploads write a draft only; a version is released by a person after reading what the draft changes. Code, methods and the session reports: https://github.com/SamuelEnrique/erw

## Credit

The Energy Research Warehouse is adapted, with permission, from the infrastructure and documents of the Item Response Warehouse (github.com/ben-domingue/irw).
