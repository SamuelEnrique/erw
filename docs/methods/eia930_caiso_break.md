# Method note: the break in EIA-930's California generation series (16 December 2025)

Energy Research Warehouse (ERW), session 73. Status: **under review**. The ERW has changed no table's values and switched no page to another source; this note says what changed, what the evidence supports, and which figures are affected. Code: `warehouse/analysis/eia930_break.py` (daily sums from the saved EIA-930 workbooks); CAISO's own figures: `caiso_fuel_supply` (`warehouse/connectors/caiso_fuel_supply.py`).

## What changed

EIA-930 is the hourly report each balancing authority sends the US Energy Information Administration. For the California ISO (`CISO`), from the hour starting 2025-12-16 08:00 UTC (midnight Pacific, the start of CAISO's operating day):

- **A geothermal series appears** (`GEO`), about 17.5 GWh a day. EIA's CISO data had none before.
- **Natural gas falls by more than the geothermal amount.** Daily means: 251.7 GWh before (2025-06-02 to 2025-12-15), 118.3 GWh after (2025-12-16 to 2026-09-29).
- **Total net generation falls**, and stays the sum of the fuels: 554.1 GWh a day before, 454.3 after.
- **Demand and interchange do not step** with it. So EIA's own balance for California (demand less net generation less net imports) was within about 1 percent of demand before (4.7 GWh a day) and is about 12 percent after (80.7 GWh a day). EIA defines a BA's demand as its metered net generation less its net interchange, so after the break California's reported figures no longer satisfy that identity.

## CAISO's own figures

CAISO publishes its supply by fuel source every five minutes (Today's Outlook). The ERW pulled it hourly from 2025-06-01 (`caiso_fuel_supply`, 151,320 rows) to set beside EIA's. Daily means, GWh (UTC days):

| | EIA, before | CAISO, before | EIA, after | CAISO, after |
|---|---|---|---|---|
| Natural gas | 251.7 | 178.3 | 118.3 | 119.1 |
| Geothermal | (none) | 17.8 | 17.4 | 17.6 |
| Large and small hydro | 56.6 | 56.7 | 59.1 | 59.4 |
| Nuclear | 49.0 | 49.1 | 53.5 | 53.8 |
| Solar | 149.4 | 172.2 | 150.6 | 172.7 |
| Wind | 51.7 | 56.7 | 60.5 | 76.6 |
| Generation, all sources (CAISO: imports excluded) | 554.1 | 534.2 | 454.3 | 501.3 |
| Net imports | 97.2 | 84.2 | 111.0 | 97.6 |

Read across the break: **after 2025-12-16, EIA's gas and geothermal equal CAISO's own to within 1 percent; before it, EIA's "natural gas" was about 73 GWh a day above CAISO's**, of which about 18 is the geothermal that was then not separated. Solar runs about 22 GWh a day below CAISO's own on both sides of the break: a standing difference, not this break.

## What the evidence supports, and no more

- **A reporting change on 2025-12-16, not a change in the grid.** The step is in one hour, in the fuel categories, with demand and interchange unmoved.
- **The same day, EIA's fuel categories changed elsewhere too.** ERCOT's "unknown energy storage" (`UES`) series ends on 2025-12-15. That suggests a change in EIA-930's categories, not one California made alone; EIA states none in the workbook's notes. EIA's known-issues page answered HTTP 403 to a plain request on 2026-10-03 and was not read.
- **From the break, EIA's California generation by fuel matches CAISO's own; its total no longer balances EIA's demand.** About 55 to 80 GWh a day that EIA's demand still counts is in no fuel. Before the break it was in EIA's "natural gas", above CAISO's own figure.
- **Not settled by these data:** what that generation is. It could be resources CAISO's own fuel mix does not show, or a definition of demand that changed less than generation did.

## Other grids

The same checks on the other six ISOs, October 2024 to September 2026: no break of this kind. Monthly balance residual as a share of demand:

- ERCOT, ISO-NE and NYISO: 0.
- MISO: a steady -1.7 to -2.9 percent throughout.
- SPP: within 1 percent.
- **PJM: -1 to -5.4 percent since May 2025**, varying month to month rather than one step. Smaller, and flagged here.

## Figures affected

See `archive/sessions/SESSION_73_REPORT.md`, "The audit", for the list of tables and pages and the size of each effect. In short:

- California's carbon intensity of generation (EIA's CO2 over EIA's generation) was 188 kg/MWh before the break against 139 on CAISO's own generation (EIA's own gas emission factor applied to CAISO's gas), and 110 against 101 after. EIA's figure ran about 49 kg/MWh high before and about 9 high after. A comparison across 2025-12-16 overstates the fall, and EIA's consumed intensity (201 to 115 kg/MWh) moves with it.
- The import share measured as demand less net generation reads about 12 points high from the break.

## Recommendation (not applied)

For California from 2025-12-16, use CAISO's own supply by fuel source (`caiso_fuel_supply`) for generation, generation mix and the generation side of the carbon figures, with EIA-930 kept for interchange. Keep EIA-930 before the break, and state the join on every page that crosses it. Samuel rules.
