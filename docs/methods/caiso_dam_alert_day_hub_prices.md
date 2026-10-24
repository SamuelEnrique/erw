# CAISO day-ahead hub prices on Flex Alert and emergency days, and the scorecard's comparison days

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table first written in session 60 (approved pull b, the Flex Alert scorecard).

Tables: `caiso_dam_alert_day_hub_prices`

## Publisher and address

California ISO (CAISO), OASIS Locational Marginal Prices, day-ahead market (report PRC_LMP, market DAM), `https://oasis.caiso.com/mrioasis/logon.do`, asked a Pacific day at a time through `iso_prices.py`'s CAISO pull (gridstatus), for the hubs TH_NP15_GEN-APND and TH_SP15_GEN-APND; each row cites its OASIS request (`https://oasis.caiso.com/oasisapi/SingleZip?...queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=...`). Source id `caiso:PRC_LMP`. Raw responses under `warehouse/raw/caiso_alert_prices/<run>/`.

Connector: `warehouse/connectors/caiso_alert_prices.py` (session 60). It asks `warehouse/derived/flex_alert_scorecard.py --days` for the days the scorecard needs (every day since 2018-07 with a CAISO notice in `caiso_grid_emergencies`, and the hottest tenth of non-alert days the model holds out), pulls each day not held, writes it as soon as both hubs have every hour, and resumes where it stopped. Days older than OASIS's 39 months are recorded and not requested. Ceiling 60,000 rows. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it; it is not in the Supabase live set (docstring). Reader: `warehouse/derived/flex_alert_scorecard.py`.

## Vintage and revision

The header's last run is `20261019T113142Z` ("This run wrote 48 rows"); every row's `retrieved_at` falls between 2026-10-02T04:57:02Z and 05:04:36Z (one per day); `vintage` is empty. A day once written is not asked again.

## Shape and variables

Series, 3,024 rows: 63 Pacific days of 48 rows (24 hours at each hub). `entity` `caiso:<hub>`, `node` the hub, `variable` lmp_dam, `unit` USD/MWh, `freq` PT1H, `geo` US-CA, `market` caiso_dam (the partition column).

- Days by year: 18 in 2023 (from 14 July), 36 in 2024, 9 in 2025 (to 24 August); by month, July 28, August 17, September 6, March 4, November 3, January 2, February, April and June 1 each.
- 44 of the 63 days are days with a notice in `caiso_grid_emergencies`; 19 are not (the comparison days).
- NP15: 4.46633 to 1,090.9045, mean 59.71; SP15: -45.0 to 1,247.6335, mean 64.22, negative in 35 hours. SP15 is above NP15 in 61.3 percent of the hours, by 4.51 on average.

## Placing values in time, and what is filled

`ts_utc` is the hour's start in UTC; a day is the Pacific day the scorecard names. The days are scattered: the table is not a window. A day CAISO does not complete is recorded and not written; nothing is filled.

## License

Header: "License: public. CAISO's Privacy and Terms of Use (https://www.caiso.com/privacy-terms-of-use): credit the California ISO." `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/caiso_dam_alert_day_hub_prices.csv`, read past its 9 header lines (scripts in `runs/c098/s2214/`).

- 3,024 rows, `ts_utc` from 2023-07-14T07:00:00Z to 2025-08-25T06:00:00Z, as the header states ("Holds 63 days, 3,024 rows"); no (entity, variable, ts_utc) twice; 48 rows on every day.
- Against the hub price history (`iso_hub_prices_history`, CAISO's day-ahead hub rows): all 3,024 hub-hours are present there and equal to 0.0005 USD/MWh.

## Where the description and the data disagree

1. **Days "left incomplete".** Header line 3 introduces its list as "Days CAISO left incomplete, not written" and then gives "160 days before 2023-07-19, outside OASIS's 39-month history ... not served, not requested": those days were never asked for, not left incomplete by CAISO.
2. **A moving cutoff.** The header's cutoff, 2023-07-19, is the run's date less 39 months; the table holds three days before it (2023-07-14, 16 and 17), pulled by earlier runs when they were inside OASIS's window. The header does not say the cutoff moves.

Acted on in session 2214: the connector's header now introduces the list as "Wanted days not written (outside OASIS's history, never requested; or left incomplete by CAISO)" and says the cutoff is the run's date less 39 months, so it moves, and that days before it pulled by earlier runs are kept. The table is not written again: the connector is run by hand against OASIS, and session 2214 made no request; the next run's header carries both.

## What it does not hold

- The 160 wanted days before OASIS's reach, prices at any node but the two hubs, and real-time prices.
