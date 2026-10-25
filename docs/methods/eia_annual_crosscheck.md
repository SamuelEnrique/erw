# EIA's hourly generation against its annual figure: method

Tables: `eia_annual_crosscheck_ba`

Energy Research Warehouse (ERW), session 323 (the Grid pack's question 5, `docs/reviews/packs/grid.md`). Two tables:

- `eia_annual_generation_ba` (source tier): EIA's annual net generation by balancing authority, summed from Form EIA-923's plant rows (`warehouse/connectors/eia923_annual_ba.py`).
- `eia_annual_crosscheck_ba` (derived): the sum of EIA-930's hourly net generation against it, by balancing authority and year (`warehouse/derived/eia_annual_crosscheck.py`).

License: public (EIA's data are in the public domain). Credit: U.S. Energy Information Administration.

## 1. Which annual figure

The Electric Power Annual has no table by balancing authority. Its index (`https://www.eia.gov/electricity/annual/`, read on 19 October 2026, request 2 of 5) gives net generation by energy source and sector (Tables 3.1.A to 3.6) and by state (3.7 to 3.22); the words "balancing authority" do not appear on it.

Form EIA-923's annual file does carry one. Its page (`https://www.eia.gov/electricity/data/eia923/`, request 1) lists one zip a year. In each, the workbook `EIA923_Schedules_2_3_4_5_M_12_<year>_Final` has a sheet "Page 1 Generation and Fuel Data" with each plant's "Balancing Authority Code" and its year's "Net Generation (Megawatthours)", and a sheet "Page 1 Energy Storage" for the storage plants. Read (requests 3 to 5), each marked Final:

| Year | Address | Last-Modified |
|---|---|---|
| 2023 | `https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2023.zip` | Tue, 19 Aug 2025 13:42:05 GMT (Final Revision) |
| 2024 | `https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip` | Mon, 12 Jan 2026 20:59:57 GMT |
| 2025 | `https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip` | Fri, 11 Sep 2026 13:28:33 GMT |

## 2. The sums

- `net_generation_mwh`: the sum over every row of Page 1 (each plant, prime mover and fuel; nuclear plants by unit) of the plants coded to the balancing authority. `storage_net_generation_mwh`: the same over Page 1 Energy Storage (negative). `plants`: the plants with a row.
- A plant with no code is `eia923:none`. EIA's "State-Fuel Level Increment" rows (its estimate for plants outside the monthly sample) are `eia923:state_fuel_increment`.
- 2023 to 2025, 68 entities.

## 3. The cross-check

For the eight balancing authorities whose EIA-930 workbooks the ERW reads (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48), the year's sum of the hourly "Net generation" of the workbook's sheet Published Hourly Data (the extract `warehouse/raw/eia930_emissions/<run>/<ba>_hours.csv`; hours by their UTC start) is set against EIA-923's sum, storage included. US48 against EIA-923's sum over every code but `none`, `HECO` and `state_fuel_increment`.

| BA | 2023 | 2024 | 2025 |
|---|---:|---:|---:|
| CISO | -9.18 | -8.35 | -8.72 |
| ERCO | -7.53 | -7.62 | -10.45 |
| ISNE | -6.51 | -5.52 | -4.91 |
| MISO | -6.29 | -5.52 | -6.68 |
| NYIS | -4.53 | -3.10 | -3.09 |
| PJM | +0.06 | -0.80 | -0.48 |
| SWPP | +3.04 | +2.62 | +3.05 |
| US48 | -4.27 | -4.38 | -4.76 |

Percent: EIA-930 less EIA-923, of EIA-923. Some hours are missing from EIA-930 (CISO 2, 48 and 48; ERCO 48 in 2025; MISO 24 in 2024 and 23 in 2025; PJM 25, 47 and 25; ISNE 2 in 2025; SWPP 1 in 2024); at the year's mean hour, none of them explains its gap.

`x_reason`, by rule: within 2 percent; else the missing hours, when filling them at the year's mean brings the gap within 2 percent; else the likely reason by the gap's sign. **These reasons are hypotheses, not EIA's statements.** EIA-930 lower (every grid but PJM and SPP, and the Lower 48 by about 4.5 percent): EIA-930 is what the balancing authority meters, while EIA-923 is each plant's own net generation, which includes industrial self-generation consumed on site, and plants scheduled into a neighbour. EIA-930 higher (SPP, about 3 percent): generation SPP meters from plants EIA-923 codes to another authority. The UTC year of EIA-930's hours against EIA-923's calendar year shifts a few hours of generation across the year's edge.

## 4. Limits

- Three years. Earlier zips are on EIA's page; the ceiling was five requests.
- The comparison is of totals; neither table says which plants make the difference. EIA-923's plant rows and EIA-860's plant-to-BA codes would let a later session find them.
