# Net generation by state and energy source, all sectors, a month (EIA, Form EIA-923)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 27 September 2026 (session 18).

Tables: `eia_state_generation_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), electric power operational data (Form EIA-923, Electric Power Monthly; page cited `https://www.eia.gov/electricity/data/browser/`), through the EIA API v2 route `electricity/electric-power-operational-data` (`https://api.eia.gov/v2/electricity/electric-power-operational-data/data/`), frequency monthly, data `generation`, facets `sectorid` 99 (all sectors) and `fueltypeid` in the 14 energy sources of `GEN_FUELS`, pages of 5,000 sorted by period, location and fueltypeid. Source id `eia:electricity/electric-power-operational-data`. Connector: `warehouse/connectors/eia_series.py` (session 18). The key comes from `EIA_API_KEY` and is shown as `REDACTED` in the address each row keeps in `source_url`.

`warehouse/connectors/eia_power_fuel_stocks.py` names this table only in its docstring: its stocks are "the stocks behind the coal and oil burns that eia_state_generation_monthly records". It reads the same route's `stocks` column for its own table, `eia_power_fuel_stocks_monthly`, and neither reads nor writes this one. `eia_power_plant_fuel_costs` (`eia_board.py`) reads the same route's cost columns.

## Vintage and revision

January 2001 to July 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261022T152428Z-github`, from the connector's run `20261022T143537Z`; "Dates EIA lists without a value, omitted: 769". The rows' `retrieved_at` are 29 September 2026 (193,656 rows) and 22 October 2026 (6,707 rows).

Each run asks for the full history and `ip.write_csv` merges it on (entity, variable, ts_utc): a month EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 200,363 rows, 760 series. `entity` `eia:generation:<location>:<fueltypeid>`; `variable` `net_generation`; `unit` MWh (EIA's thousand MWh times 1,000, exact); `ts_utc` the month's first day; `freq` P1M; `node`, `market` and `vintage` empty (EIA's names of the series are in the header).

- 64 locations: the 50 states and DC (`geo` `US-<state>`), Puerto Rico (`geo` `US-PR`, from January 2016), US (`geo` US), and eleven census region codes, ENC, ESC, MAT, MTN, NEW, PAC, PCC, PCN, SAT, WNC and WSC (`geo` empty). PAC begins in January 2011 and is listed beside its parts PCC and PCN.
- Energy sources, with the locations that have each: ALL all fuels (64), PET petroleum (64), NG natural gas (64), BIO biomass (63), OTH other (63), SUN solar (63), COW all coal products (62), DPV estimated small-scale solar photovoltaic (62, from January 2014), HYC conventional hydroelectric (61), WND wind (57), OOG other gases (54), NUC nuclear (42), HPS hydroelectric pumped storage (29), GEO geothermal (12).
- ALL = COW + PET + NG + OOG + NUC + HYC + HPS + WND + SUN + GEO + BIO + OTH; DPV is not in ALL (the connector's note, and its docstring's check for Texas, July 2026).
- 8,352 rows are negative, as EIA gives them: 6,600 of them pumped storage, whose U.S. net generation is negative in all 307 months, and 1,349 OTH.

The states sum to the U.S., the regions hold their states, and ALL holds its sources: a sum takes one level.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; an empty answer stops it too.
- A unit not in the connector's map, or a (series, month) given twice, stops the table.
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (769 when written). Nothing is filled.
- A page is tried up to four times; pages are 0.5 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines.
- The U.S. ALL row equals its twelve sources within 2.0 MWh in all 307 months (the largest gap June 2003): December 2025, 380,021,511.69 MWh against 380,021,511.68, with DPV's 5,538,327.72 MWh outside it.
- The 50 states and DC sum to the U.S. ALL row within 1,421 MWh in all 307 months (the largest gap June 2002; December 2025, 380,021,511.72 against 380,021,511.69). Puerto Rico is not in the U.S. row (1,363,032.98 MWh in December 2025).
- The U.S. generated 4,425,028,525.98 MWh in 2025, the twelve months summed.

## What it does not hold

- The sectors' parts (utilities, independent producers, commercial and industrial plants): sector 99 only.
- The route's finer energy sources: only the 14 of `GEN_FUELS` are asked.
- Plants: generation by plant is `eia923_plant_fuel_monthly` (method note `eia923_monthly.md`).
- Months before 2001.
