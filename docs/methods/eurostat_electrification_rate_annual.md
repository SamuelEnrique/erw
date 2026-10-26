# Europe's rate of electrification, 1990 to 2023 (Eurostat's nrg_ind_re)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2806).

Tables: `eurostat_electrification_rate_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Rate of electrification by end-user" (nrg_ind_re, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_re/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re?format=SDMX-CSV&compressed=false`;
- the NRG_BAL codelist, for the balance items' names.

Source id `eurostat:nrg_ind_re`. Connector: `warehouse/connectors/eurostat_electrification.py` (session 2806), whose raw store is `warehouse/raw/eurostat_electrification/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1603). Session 2806 took it in place of INE Portugal, whose host answered HTTP 403 at its robots files (reads 1600 and 1601).

## Vintage and revision

Written by run `20261026T043745Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T04:34:41Z. Eurostat's last update, as the file gives it (no time zone), is 16/07/26 23:00:00. Eurostat revises the energy balances, and so this indicator, each year.

## Shape and variables

Series, 38,269 rows, 39 areas, 43 balance items, 1990 to 2023:
- `entity` `eurostat_electrification:<geo>:<NRG_BAL code>`: the item whose energy use is measured. That is final consumption (FC_E), industry (FC_IND_E) and its branches, transport (FC_TRA_E) and its modes, the other sectors (FC_OTH_E) with households and services, and the energy sector's own use (NRG_E) and its parts.
- `variable` `electrification_rate`; `unit` pct: electricity's share of the item's energy use, as Eurostat gives it.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020.
- `node` "<geo> electrification rate, <the NRG_BAL name>"; `x_geo_code`, `x_nrg_bal`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

**Figures:**
- The EU27's final energy use was 17.898 per cent electricity in 1990, 22.165 in 2010 and 22.917 in 2023.
- In 2023 its industry's use was 32.654 per cent electricity, services' 51.204, households' 25.897 and transport's 2.166 (rail 79.556, road 0.515).
- Portugal: 17.797 in 1990, 25.867 in 2023.
- Highest in 2023: Iceland 53.422, Norway 50.571. Lowest: Latvia 14.327.

## Reading the source

- **Final consumption's rate lies within industry's, transport's and the other sectors' in all 1,238 country years that give the four,** and households' and services' together within theirs in all 1,235, within 0.01 points. A rate is a weighted mean of its parts' rates, so a case outside would mean an error; none was found.
- A blank (flag m) has no row (2,478). 3,277 zeros are kept. The United Kingdom, Kosovo and EU28 are left out.
- The run stops, asking nothing, while Eurostat is paused. It also stops, filling nothing, on:
  - a header not Eurostat's;
  - a unit, frequency or balance item not expected;
  - a value not a number, or outside 0 to 100;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_re. In the release package; held from the live set.

## Cross-check

No held table gives total final energy consumption, so the rates were compared only by the balance's own logic (above): every aggregate's rate lies within its parts' rates. A rate is a share, not a quantity, and no held table gives the same share to compare.
