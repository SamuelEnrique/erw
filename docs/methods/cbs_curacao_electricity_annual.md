# Curacao's electricity production a year (CBS Curacao, Aqualectra's figures)

Energy Research Warehouse (ERW), method note written in session 2597 (chain 128) for a table first written on 25 October 2026 (session 2591).

Tables: `cbs_curacao_electricity_annual`

## Publisher and address

The Central Bureau of Statistics Curacao (CBS), its statistics page "Manufacturing", a table of water and electricity production a year whose source is the Curacao Water and Power Company (Aqualectra): `https://www.cbs.cw/manufacturing-0`. One GET, no key. Source id `cbs_cw:manufacturing_electricity_production`. Connector: `warehouse/connectors/cbs_curacao_electricity.py` (session 2591). www.cbs.cw's robots file closes `/` to a list of named SEO agents only, none an AI agent's (read 1159).

## Vintage and revision

Written by run `20261025T033828Z` (the write under the lock, offline), which read the page saved at 2026-10-25T03:36:57Z. `vintage` is empty: the page sends no last-modified time. CBS replaces the page's years as it updates them.

## Shape and variables

Series, 3 rows, 1 entity. `entity` `cbs_cw:aqualectra` (Aqualectra's system, the island's public supply); `variable` `production`; `unit` MWh (CBS's million kWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` CW; `node` CBS's label. Production 866.9 GWh in 2022, 916.3 in 2023, 982.8 in 2024.

## Reading the source

- The run stops at once, asking nothing, while `cbs_cw` or www.cbs.cw is paused.
- One request a run; `--offline` reads the saved page.
- The page's text is read for the header "Water Production (1000 m 3 ) Electricity Production (mln kWh)" (found once), then each "<year> <water> <electricity>" up to the source line, which must name Aqualectra; nothing else may stand between them, and the years must run without a gap. The water column is not taken.

Nothing is filled. CBS's page points to its main site for earlier years, not read.

## License

Public. CBS's Disclaimer (read 1162): its statistical data "may be used, downloaded for personal use or communicated to the public, simply on condition that the source (Central Bureau of Statistics Curacao or CBS Curacao) be mentioned accurately and clearly". Verdict: may be public. Cited as CBS's, with Aqualectra as the source. In the release package; held from the live set.

## Cross-check

EIA keeps Curacao inside "NLDA", the former Netherlands Antilles (`eia_world_electricity_annual`, read past its header lines): 910.0, 1,029.7 and 1,006.4 GWh for 2022 to 2024, against Curacao's 866.9, 916.3 and 982.8.
