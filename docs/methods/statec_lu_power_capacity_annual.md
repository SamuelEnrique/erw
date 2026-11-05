# Luxembourg's power stations and the mix supplied to its end users (STATEC's LUSTAT)

Energy Research Warehouse (ERW), method note written in session 2787 (chain 141) for two tables first written on 26 October 2026 (sessions 2784 and 2785). The companion of `docs/methods/statec_lu_electricity_generation_annual.md`, which describes chain 140's generation and trade tables.

Tables: `statec_lu_power_capacity_annual`, `statec_lu_supplier_mix_annual`

## Publisher and address

STATEC, Luxembourg's national statistics institute, through LUSTAT, its .Stat Suite SDMX service (`https://lustat.statec.lu/`). No key. Each table reads one dataflow, every key, as CSV with labels:
- `statec_lu_power_capacity_annual`: DF_A4201 "Net maximum power (in MWe) and units of the power stations", `https://lustat.statec.lu/rest/data/LU1,DF_A4201,1.0/all?format=csvfilewithlabels`; source id `statec:lustat_df_a4201`; connector `warehouse/connectors/statec_power_capacity.py` (session 2784).
- `statec_lu_supplier_mix_annual`: DF_A4209 "National mix of electricity provided to the end-users (in %)", `https://lustat.statec.lu/rest/data/LU1,DF_A4209,1.0/all?format=csvfilewithlabels`; source id `statec:lustat_df_a4209`; connector `warehouse/connectors/statec_supplier_mix.py` (session 2785).

Both store their raw files in `warehouse/raw/statec/`. lustat.statec.lu has no robots file: its address answers the data explorer's page (reads 1582 and 1586).

## Vintage and revision

- The capacity table was written by run `20261026T015617Z`, reading the file retrieved at 2026-10-26T01:53:49Z.
- The mix table was written by run `20261026T020104Z`, reading the file retrieved at 2026-10-26T01:59:35Z.
- STATEC adds a year each year and may revise earlier ones.

## Shape and variables

Both are series; `ts_utc` the year's first day; `freq` P1Y; `geo` LU; `node` STATEC's code and label. A missing observation has no row.

**`statec_lu_power_capacity_annual`** (951 rows, 14 entities, 1960 to 2024): `entity` `statec_cap:lu:<code>`, with `variable` `net_maximum_power` (MW, STATEC's MWe) or `power_stations` (count). The codes are:
- l01 the total;
- sl01 primary and sl02 secondary generation stations;
- ssl01 to ssl05 hydropower, wind, solar, classic thermal and CHP stations;
- sssl01 to sssl06 pumping, large and micro hydro, biomethanation, woodwaste and woodpellets stations.

The total was 1,230.3 MW in 15 stations in 1990, and 2,266.9 MW in 22,861 stations in 2024, of which 22,610 solar.

**`statec_lu_supplier_mix_annual`** (196 rows, 13 entities, 2009 to 2024): `entity` `statec_mix:lu:<code>`, `variable` `supply_mix_share`, `unit` pct. The codes are:
- l01 fossil, l02 nuclear, l03 renewable and l04 other and unidentified sources;
- sl01 to sl04 hard coal, brown coal, natural gas and other fossil;
- sl05 to sl09 biomass and biogas, wind, hydroelectricity, solar and other renewables.

**It is the suppliers' disclosed mix, not the generation in Luxembourg:** most of the electricity Luxembourg's end users take is imported, and the disclosure counts the certificates attached to it. The renewable share was 21.3 per cent in 2009, 55.2 in 2016 and 66.5 in 2024.

## Reading the source

- Each run stops at once, asking nothing, while `statec` or lustat.statec.lu is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **Capacity:** l01 is sl01 plus sl02, sl01 is ssl01 to ssl03, and sl02 is ssl04 and ssl05, compared every year within 0.5 MW and exactly for the counts. STATEC's figures differ in 11 cases, counted and kept as published: the power in 2009 (the total by 9.1 MW, primary by 4.0) and the number of secondary stations in 1996 to 2000, 2020, 2021 and 2024 (and the total's count in 2024). The third level is not compared, as pumping, large and micro stations do not sum to hydropower as published.
- **Mix:** the four groups make 100, and fossil and renewable their sources, compared every year within 0.15 points (the shares are rounded to 0.1). Three cases differ, kept as published: renewables in 2019 (by 2.8 points), and the groups and renewables in 2022 (by 0.3).
- A header not the service's, a variable or code not expected, a key given twice, or a value not a number (or a share outside 0 to 100) stops either run. Nothing is filled.

## License

Public. STATEC's legal notice, linked from LUSTAT's footer (read 1564): "without restriction, under the terms of the Universal Transfer in the Public Domain Creative Commons CC0 1.0". The verdict, may be public, was given in session 2771. Both tables are in the release package and held from the live set.

## Cross-check

**Capacity** against `eurostat_electricity_capacity_annual` (Luxembourg, `net_capacity_total`), MW:

| Year | Wind (here) | Eurostat RA300 | Solar (here) | Eurostat RA420 | Hydro (here) | Eurostat RA100 |
|---|---|---|---|---|---|---|
| 2015 | 63.794 | 63.794 | 116.272 | 116.272 | 1,330.266 | 1,330.266 |
| 2024 | 213.736 | 213.081 | 549.797 | 547.867 | 1,330.009 | 1,329.994 |

**The mix** has no like table in the ERW. As context, `eurostat_renewable_shares_annual`'s electricity share for Luxembourg (20.5 per cent in 2024, the directive's generation against consumption) is far below the suppliers' disclosed renewable share (66.5): the two measure different things.
