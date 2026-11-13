# Session 4202 report: the model (chain 239, window 4)

13 November 2026, about 10:40 to 10:46 UTC. Branch `wip/4200-forecast`. Model spend USD 0.

- **`site/lib/forecast.ts`**: pure, no imports (check-values imports it as it is). For one scenario and each year: JEDI's jobs, earnings and output scaled by spending (construction) and by MW (operations), in 2025 dollars; property tax by rule kind (capacity, production, valuation, the reader's own rate); sales tax on JEDI's taxable share; income tax per single filer on average earnings; severance through a callback; present values.
- **The gas plant's fuel** (`gas.json`): EIA case 5's heat rate (6,266 Btu/kWh, HHV), JEDI's capacity factor (0.65), 2025's mean Henry Hub price from `eia_steo_forecasts` (USD 3.5267/MMBtu over its 12 history months), and EIA's heat content of gas delivered to electric power in 2024 (1,034 Btu per cubic foot, read from EIA's page).

## Decisions made without you

- Construction effects are spread evenly over the construction years (JEDI gives a total, not a profile).
- Income tax brackets held at 2026's in real terms over the life.
