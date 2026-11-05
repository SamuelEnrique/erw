# U.S. primary energy, a month (EIA's Monthly Energy Review, Tables 1.1 to 1.3)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for a table first written on 23 October 2026.

Tables: `eia_primary_energy_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Monthly Energy Review, through the EIA API v2's `total-energy` route (`https://api.eia.gov/v2/total-energy/`), selected by series id (`msn`). Connector: `warehouse/connectors/eia_series.py`, its table `eia_primary_energy_monthly` (session 953), beside `eia_sector_energy_consumption_monthly` (Tables 2.3 and 2.4). Both share the source row `eia:total-energy`, whose report names both. The key comes from `EIA_API_KEY`.

## Vintage and revision

January 1973 to June 2026 when written. The daily run asks for the full history and merges it on (entity, variable, ts_utc), as every `eia_series` table, so EIA's revisions are taken; a month older than 150 days at the newest stops the table being written.

## Shape and variables

Series, 24 entities, `entity` `eia:<msn>`, `unit` TBtu (EIA's trillion Btu, as published), `freq` P1M, `geo` US. `variable` from each series id (`MER_PRIMARY` in the connector):

| Variable | Series |
|---|---|
| production | TEPRBUS total, FFPRBUS fossil fuels, CLPRBUS coal, NGPRBUS dry natural gas, PAPRBUS crude oil, NLPRBUS natural gas plant liquids, REPRBUS renewables, BMPRBUS biomass |
| imports, exports, net_imports, stock_change_and_other | TEIMBUS, TEEXBUS, TENIBUS, TEAJBUS |
| consumption | TETCBUS total, FFTCBUS fossil fuels, CLTCBUS coal, NNTCBUS natural gas (excluding supplemental gaseous fuels), PMTCBUS petroleum (excluding biofuels), RETCBUS renewables, BMTCBUS biomass |
| consumption_production | NUETBUS nuclear, HVTCBUS hydro, GETCBUS geothermal, SOTCBUS solar, WYTCBUS wind: EIA's one series for both tables |

Totals hold their parts: a sum takes one level.

## Reading the API

- EIA marks a month it has no figure for "Not Available" (solar's 132 months and wind's 120 before EIA counts them): omitted, as "none" is; any other non-number stops the table.
- Units must be EIA's "Trillion Btu"; the route returning no rows stops the table. The series are asked by their msn facet, so one series EIA leaves out is not caught by the code (session 2004 corrected this line, which said it stopped the table).

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 953 and 960)

- Against SEDS's U.S. totals (`eia_seds_state_energy`, years with twelve months): total consumption, coal, nuclear and renewables within 0.5 percent in 35 of 35 years (2024: 94,582 and 94,543 TBtu); natural gas within 1.1 percent; petroleum up to 5 percent apart, since MER's series excludes biofuels and SEDS's includes them.
- The overview's identity: production plus net imports plus stock change and other equals consumption within 0.01 TBtu in all 53 full years.
- Session 960, against the code: the 24 series ids and their variables are `MER_PRIMARY`'s; the shared report text is `MER_REPORT`.

## What it does not hold

- MER's other tables (sector consumption is `eia_sector_energy_consumption_monthly`; prices, electricity and carbon tables are not taken here).
- Annual or fossil fuel equivalent series.
