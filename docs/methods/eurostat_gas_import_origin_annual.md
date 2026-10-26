# Europe's natural gas import dependency by country of origin, 2015 to 2020 (Eurostat's nrg_ind_idogas)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2821).

Tables: `eurostat_gas_import_origin_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Natural gas import dependency by country of origin" (nrg_ind_idogas, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_idogas/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_idogas?format=SDMX-CSV&compressed=false`.

Source id `eurostat:nrg_ind_idogas`. Connector: `warehouse/connectors/eurostat_gas_import_origin.py` (session 2821), whose raw store is `warehouse/raw/eurostat_gas_import_origin/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1637). Session 2821 took it in place of Transelectrica, whose robots files answer HTTP 500 (reads 1635 and 1636).

## Vintage and revision

Written by run `20261026T063828Z`, which read the file retrieved at 2026-10-26T06:35:59Z. **Eurostat's last update, as the file gives it, is 29/09/22 23:00:00, and the dataset holds no year after 2020.** It is the record of Europe's gas imports by origin before 2022.

## Shape and variables

Series, 1,253 rows, 32 areas, 2015 to 2020:
- `entity` `eurostat_gas_origin:<geo>:<partner>`, the partners being DZ Algeria, NG Nigeria, NO Norway, QA Qatar, RU Russia, UK the United Kingdom and US the United States.
- `variable` `import_dependency_by_origin`; `unit` pct, as Eurostat gives it (natural gas, G3000).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR); `x_partner`, `x_flag` (`i`: see Eurostat's metadata) and `x_conf_status`.
- Sector `gas`.

**Figures, 2020, Russia:** Germany 68.66, Finland 82.23, Italy 43.72. Bosnia and Herzegovina, Czechia, Latvia, Moldova, Serbia and North Macedonia 100. Italy on Algeria 22.84.

## Reading the source

- **Zeros for origins not reported:** Austria and Georgia give 0 for every partner in every year. Those 12 country years are not written; they are counted and listed in the run log. 635 other zeros are kept. 301 blanks (flag m) have no row. Nothing is filled.
- The United Kingdom and Kosovo are left out as reporters. The United Kingdom stays as a partner.
- The run stops, asking nothing, while Eurostat is paused. It also stops on:
  - a header not Eurostat's;
  - a frequency, product, unit or partner not expected;
  - a value not a number, or outside 0 to 100;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_idogas. In the release package; held from the live set.

## Cross-check

The seven partners' sum against each country's natural gas import dependency in `eurostat_import_dependency_annual` (nrg_ind_id, G3000), in the 176 country years both give:

| Measure | Value |
|---|---|
| Median difference | 0.43 points |
| More than 5 points above | 41 |
| More than 5 points below | 70 |
| Poland 2020 | 95.23 here, 78.25 there |
| Finland 2020 | 83.33 here, 100.29 there |

**They are different measures** (seven partners only, and Eurostat's own definition of each), and neither is read as the other.

`eurostat_import_concentration_annual` (session 2827) agrees where one partner is the whole: Czechia's and Latvia's gas import concentration is 1.0 in 2020.
