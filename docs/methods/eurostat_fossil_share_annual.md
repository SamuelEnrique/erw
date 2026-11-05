# The share of fossil fuels in Europe's gross available energy, 1990 to 2024 (Eurostat's nrg_ind_ffgae)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2826).

Tables: `eurostat_fossil_share_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Share of fossil fuels in gross available energy" (nrg_ind_ffgae, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ffgae/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ffgae?format=SDMX-CSV&compressed=false`.

Source id `eurostat:nrg_ind_ffgae`. Connector: `warehouse/connectors/eurostat_fossil_share.py` (session 2826), whose raw store is `warehouse/raw/eurostat_fossil_share/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1646).

## Vintage and revision

Written by run `20261026T065619Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T06:54:40Z. Eurostat's last update, as the file gives it (no time zone), is 16/07/26 23:00:00.

## Shape and variables

Series, 1,279 rows, 39 areas, 1990 to 2024:
- `entity` `eurostat_fossil_share:<geo>`; `variable` `fossil_share_gross_available_energy`; `unit` pct.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR), blank for EU27_2020.

**Figures:**
- The EU27: 82.37 per cent in 1990, 68.12 in 2024.
- Lowest in 2024: Iceland 16.38, Sweden 32.06. Highest: Malta 94.91, Cyprus 88.62.

## Reading the source

- **Estonia's shares are above 100 in its first three years** (1990 103.79, 1991 102.19, 1992 100.96). They are kept as Eurostat publishes them, counted in the header and listed in the run log.
- The United Kingdom and Kosovo are left out. There are no blanks. Nothing is filled.
- The run stops, asking nothing, while Eurostat is paused. It also stops on:
  - a header not Eurostat's;
  - a frequency or unit not expected;
  - a value not a number;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_ffgae. In the release package; held from the live set.

## Cross-check

Context, not a test: this share plus `eurostat_renewable_shares_annual`'s `renewable_share_overall` has a median of 97.62 over 743 country years. The renewable share is a share of gross final consumption, a different denominator, so the two are not complements.
