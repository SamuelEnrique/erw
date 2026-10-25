# The Western Area Power Administration's energy sold and power rate by project, FY 2008 to FY 2025

Energy Research Warehouse (ERW), method note written in session 2759 (chain 139) for a table first written on 25 October 2026 (session 2751).

Tables: `wapa_energy_sales_annual`

## Publisher and address

The Western Area Power Administration (WAPA), one of the Department of Energy's power marketing administrations. The table reads WAPA's workbook "Rates and Sales Data FY 2008-2025", `https://www.wapa.gov/wp-content/uploads/2026/03/3-Rates-and-Sales-Data-FY-2008-2025.xlsx`, its sheet "Energy Sales and Rates Data", found through WAPA's WordPress media listing (read 1487). No key. Source id `wapa:rates_and_sales_data`. Connector: `warehouse/connectors/wapa_rates_sales.py` (session 2751), whose raw store is `warehouse/raw/wapa/`. www.wapa.gov's robots file closes only `/wp-admin/` and names no Claude agent (read 1485); the bare name wapa.gov fails its TLS handshake (read 1486) and is not asked.

## Vintage and revision

Written by run `20261025T220440Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T21:59:36Z, last modified 20 March 2026. WAPA posts a new workbook each spring with the fiscal year just ended; the address changes with it.

## Shape and variables

Series, 307 rows, 12 entities, each federal fiscal year from FY 2008 to FY 2025. `entity` `wapa_proj:<project>`, the row's label as a slug with its footnote mark dropped, and `wapa_proj:wapa_total`, WAPA's total row. `variable`:
- `energy_sold`, MWh, for eleven projects and the total ("Energy Sold (MWh)");
- `power_rate`, USD/MWh, for six projects: WAPA's "Power Rate (cents/kWh)" times 10, an exact change of unit (1 cent/kWh = 10 USD/MWh).

`ts_utc` is the fiscal year's first day, 1 October of the year before: FY 2025 runs from 1 October 2024 to 30 September 2025 and is stamped `2024-10-01T00:00:00Z`. `freq` P1Y; `geo` US; `node` the row's label as written.

**Figures:** WAPA's total energy sold was 36,446,147 MWh in FY 2008, 42,428,128 in FY 2011 (the peak), 30,770,428 in FY 2016 and 27,821,288 in FY 2025. The Pick-Sloan Missouri Basin Program's Eastern Division sold the most each year (10,084,903 MWh in FY 2025).

The sheet's third table, the transmission rate in dollars a kW a month, is not taken: the data standard has no unit for it.

## Reading the source

- The run stops at once, asking nothing, while `wapa` or www.wapa.gov is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **WAPA's footnotes,** stated in the header:
  - the Central Arizona Project's Navajo plant ceased generating on 19 November 2019 (its later years are N/A);
  - the Central Valley Project's energy includes custom product power purchases;
  - the Boulder Canyon and Parker-Davis rates exclude the Lower Colorado River Basin Development Fund surcharge, and Boulder Canyon's 2018 to 2024 rates were restated;
  - the Central Valley rate excludes the Restoration Fund charge;
  - the Loveland and Pick-Sloan rates include a drought adder from FY 2008 to FY 2024.
- Each table is found by its title in column A; its year row must be each year from 2025 down to 2008. A project given twice, a cell neither a number nor "N/A", or a negative stops the run.
- "N/A" has no row (the Central Arizona Project after FY 2019, Olmsted before FY 2019). Washoe's FY 2008 zero stays a zero.
- **Check,** within 0.5 MWh: the projects' energy sold adds to WAPA's total. It holds exactly in all 18 years.
- Nothing is filled.

## License

Public. WAPA's Web Policies (read 1490) state no copyright or reuse term, and DOE's notice governs: "Government information at DOE websites is in the public domain" (read 54). WAPA's verdict, may be public, was given in session 2755. Credit WAPA. In the release package; held from the live set.

## Cross-check

Against `usbr_hydropower_monthly` (Reclamation's net generation, each fiscal year's twelve months summed), MWh:

| Fiscal year | Boulder Canyon Project, sold (here) | Hoover, net generation | Difference |
|---|---|---|---|
| FY 2014 | 3,743,225 | 3,894,787 | -3.9% |
| FY 2018 | 3,489,820 | 3,600,360 | -3.1% |
| FY 2019 | 3,522,045 | 3,480,065 | +1.2% |
| FY 2025 | 2,939,453 | 2,907,310 | +1.1% |

The Parker-Davis Project's sales stay near 1.42 TWh every year from FY 2011 (1,421,463 to 1,424,160 MWh; FY 2008 1,343,545), while Parker's and Davis's net generation together ran from 1,307,744 (FY 2024) to 1,623,308 MWh (FY 2014): sales are contract amounts, met with purchases or surplus, not the plants' output.
