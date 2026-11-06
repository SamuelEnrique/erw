# Session 3709 report: the Grid tool's cross-check table

Energy Research Warehouse (ERW). Chain 208, session 10 of 20, portable laptop, 6 November 2026, about 22:42 to 22:48 UTC, while session 3706's gate ran. Branch `wip/3701-sellable`, commit `a4d09326f`.

- **Requests: 5 of 10.** `epa.gov/robots.txt` and `eia.gov/robots.txt` (neither disallows the pages read), EPA's eGRID summary page, the eGRID2023 summary tables (`summary_tables_rev2.xlsx`), and EIA's answer "How much carbon dioxide is produced per kilowatthour". Both are works of the United States government; the figures are quoted.
- **`docs/methods/crosschecks/grid.md`**, by tab:
  - **The network:** the hour shown has no counterpart held (the copies of EIA's demand and generation here end on 30 September). The comparisons in held hours: ERCOT, ISO-NE and NYISO close EIA's balance; CAISO, MISO, PJM and SPP do not.
  - **The gravity shape:** EIA-930 against Form EIA-923, from -10.45 percent (ERCOT) to +3.05 (SPP).
  - **Carbon intensity in 2023,** rebuilt here from the hourly and emissions tables: US48 348.57 against eGRID's 348.00 (+0.57) and EIA's all-plant 366.03 (-17.46); ERCOT 342.96 against 332.87 (+10.09); ISO-NE 231.85 against 244.61 (-12.76); CAISO 197.38 against California's 194.35 (+3.03).
  - **The Mix tab:** EIA's own rows; California's EIA-930 generation 1,740 MW below CAISO's own.
  - **The Ask panel:** HB_HUBAVG's 2024 on-peak mean 31.57 against ERCOT's load-weighted 2024 average 32.41 (two measures).
- The table cells that hold check keys escape their pipes, so the tables render in GitHub's markdown.

## Decisions made without you

- The carbon rows set a 2023 year, computed from the same tables the page prints, beside eGRID2023. The page's own figures are of hours and months that eGRID does not state.
- ERCOT's and ISO-NE's carbon gaps are "not explained". EIA-930's CO2 is a fuel-factor estimate and eGRID's is each plant's; the note names the difference without asserting the cause.

## For Samuel's ruling

- None new.
