# Europe's monthly electricity: net production by fuel and the flows (Eurostat nrg_cb_pem and nrg_cb_em)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2225).

Tables: `eurostat_electricity_monthly`

## Publisher and address

Eurostat (the Statistical Office of the European Union), two monthly data sets through its SDMX 2.1 dissemination API (no key), as session 2123 took `nrg_inf_epcrw`:

- "Net electricity generation by type of fuel, monthly data" (`nrg_cb_pem`): `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_pem?format=SDMX-CSV&compressed=false&startPeriod=2016-01`;
- "Supply, transformation and consumption of electricity, monthly data" (`nrg_cb_em`): the same address with `nrg_cb_em`;
- the English names from the codelists `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC` and `.../codelist/ESTAT/NRG_BAL`.

The data browser page is `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_pem/default/table`. Source id `eurostat:nrg_cb_pem_nrg_cb_em`. Connector: `warehouse/connectors/eurostat_electricity_monthly.py` (session 2225), which takes its countries, its aggregates and its codelist reader from `eurostat_res_capacity.py`. ec.europa.eu's robots file disallows the old `/eurostat/SDMX/diss-web/rest/` and the search pages, not `/eurostat/api/dissemination/` (sessions 2123 and 2225).

## Vintage and revision

January 2016 to August 2026, written by run `20261024T021336Z` (24 October 2026), which read the files saved earlier that morning (its log: "raw file reused" for all four). `nrg_cb_pem` was retrieved at 2026-10-24T02:05:57Z (98,236 rows), `nrg_cb_em` at 2026-10-24T02:05:25Z (31,789 rows). The header records Eurostat's LAST UPDATE for both: 23/10/26 23:00:00. `vintage` is blank in every row: it is the response's Last-Modified (`vintage_of`), and Eurostat's API sent none. The header's "Retrieved: 20261024T021336Z" is the write's run id.

Every run that is not `--offline` asks for all four documents again and writes the whole table again (`write_snapshot`): Eurostat's revisions of earlier months replace the rows held.

## Shape and variables

Series, 130,025 rows, 40 entities, 128 months. `entity` eurostat_elec:<Eurostat geo code>; `unit` MWh (Eurostat's GWh times 1,000, rounded to 3 decimals); `ts_utc` the month's first day; `freq` P1M; `geo` the ISO 3166-1 alpha-2 code, Eurostat's EL written GR, blank for EU27_2020; `market` blank; `node` the code's English name from the codelist. Extra columns: `x_geo_code` (Eurostat's code), `x_dataset`, `x_flag` (the observation's flag), `x_conf_status` (blank in every row).

Variables: 23 `net_production:<SIEC code>` from `nrg_cb_pem` (TOTAL; the combustible fuels CF and their parts C0000, G3000, O4000XBIO, CF_R, CF_NR_OTH; N9000, which the connector's docstring (line 15) calls nuclear but Eurostat's codelist names "Nuclear fuels and other fuels n.e.c.", the name the rows carry as `node`; the renewables RA000 and their parts RA100 to RA500_5160; X9900; FE, fossil energy, from January 2023), each as published and no sum made here; and 7 `flow:<NRG_BAL code>` from `nrg_cb_em` (electricity E7000): IMP, IMP_FROM_EU, EXP, EXP_TO_EU, AIM (available to the internal market), DL (distribution losses), TI_EHG_EPS (input to pumped storage). TOTAL, CF, N9000, RA100, RA200, RA300, AIM, IMP, EXP and TI_EHG_EPS begin in January 2016; most of the rest, and DL, in January 2017.

The European Union (EU27_2020), 2025, all twelve months held for each line:

| Line | TWh |
|---|---|
| net_production:TOTAL | 2,666.8 |
| net_production:CF (combustible fuels) | 870.9 |
| net_production:G3000 (natural gas) | 449.2 |
| net_production:C0000 (coal and manufactured gases) | 245.1 |
| net_production:N9000 (nuclear fuels and other fuels n.e.c.) | 620.9 |
| net_production:RA100 (hydro) | 346.2 |
| net_production:RA300 (wind) | 473.1 |
| net_production:RA400 (solar) | 346.8 |
| flow:AIM | 2,445.2 |
| flow:IMP | 436.3 |
| flow:EXP | 460.1 |
| flow:DL | 147.0 |

Months held for net_production:TOTAL: 128 (January 2016 to August 2026) for 20 countries; 127 (to July 2026) for 12 countries and EU27_2020; Bosnia and Herzegovina 104 (from January 2017), Albania and Georgia 103 (from January 2018), Iceland 94 (January 2017 to October 2024), Moldova 79 (from January 2020), Ukraine 52 (October 2017 to January 2022). Switzerland has no TOTAL: its 40 rows are one line, CF_NR_OTH, January 2020 to April 2023.

Flags: blank in 124,558 rows; e (estimated) 4,742, most for Germany (1,338), Luxembourg (809) and Italy (603); p (provisional) 354; n (not significant) 323; u (low reliability) 41, Malta and Croatia; d (definition differs) 6; b (break in series) 1. 40,705 values are 0; one is negative (France, O4000XBIO, August 2017, -2,538 MWh).

## Reading the source

- The run stops at once, asking nothing, while `eurostat` or the host ec.europa.eu is paused.
- Four requests a run, in order: the SIEC codelist, the NRG_BAL codelist, `nrg_cb_pem`, `nrg_cb_em`; each fetched fresh unless `--offline`, which reads the saved files in `warehouse/raw/eurostat_cb_em/` and stops if one is missing. Timeout 300 seconds, 1 second's pause after each; HTTP 404 stops the run, any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart.
- A header other than `HEAD_PEM` or `HEAD_EM` (Eurostat's SDMX-CSV columns), a unit other than GWH (or PC in `nrg_cb_pem`), a frequency other than M, a SIEC code other than E7000 in `nrg_cb_em`, a value that is not a number, a period not of the form YYYY-MM, or a key given twice stops the run; no file is written.
- Kept: the geo codes of `KEPT` in `eurostat_res_capacity.py` (the 27 member states, EFTA's CH, IS, LI, NO, the candidates AL, BA, GE, MD, ME, MK, RS, TR, UA, and the aggregates EU27_2020, EA21, EA20, EA19); the other codes are named in the header and left out: UK and XK in this file. Of `nrg_cb_pem`, only the GWH rows; its PC rows (a fuel's percent share) are not taken.
- A blank OBS_VALUE has no row. Nothing is filled. The code counts no row ceiling.

## License

Public with acknowledgement. `license_verdicts.csv` records Eurostat, read 280: "may be public", for public and for commercial use. The sentence: "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged." The same notice bars commercial reuse of data for countries outside the EU, EFTA and the official candidates, which is why the United Kingdom and Kosovo are left out. The header cites Eurostat, `nrg_cb_pem` and `nrg_cb_em`, and says Eurostat bears no responsibility for the reshaping. `sources.csv` flags `eurostat:nrg_cb_pem_nrg_cb_em` public; `license_tables.csv` lists the table under Eurostat.

## Cross-checks (session 2233)

- The written table and session 2225's trial copy hold the same 130,025 keys with every column equal, so the session's results (`runs/c099/s2225/cross.out`) hold for the written rows:
  - the 27 member states' TOTAL, summed, equals EU27_2020's in all 127 months it is held, the ratio 1.0 to six decimals;
  - against `owid_ember_electricity_annual`'s demand, in 359 full country-years 2016 to 2025: AIM a median 0.896 (0.825 to 0.969 from the 10th to the 90th percentile), TOTAL a median 0.915 (0.649 to 1.075); AIM's furthest are Moldova (0.552 in 2021, 0.587 in 2023) and Montenegro (2.974 in 2016, 3.094 in 2017), not explained here.
- TOTAL against the sum of CF, N9000, RA100, RA200, RA300, RA400, RA500_5160 and X9900 (a blank as 0), computed from the rows: within 1,000 MWh in 4,426 of 4,746 country-months.
- AIM is Eurostat's own line, not a sum the table can rebuild: it is within 1 percent of TOTAL plus IMP less EXP less TI_EHG_EPS in 1,488 of 4,733 country-months, a median 0.955 of it.
- The counts above were computed from the rows, read past the header lines.

## What it does not hold

- The United Kingdom and Kosovo (Eurostat's terms).
- Months before January 2016; the annual data sets.
- Switzerland's production and flows, but for one line over 40 months; Ukraine after January 2022; Iceland after October 2024.
- `nrg_cb_pem`'s percent shares, and any sum made here.
- A vintage per row: Eurostat's last update is in the header only.
