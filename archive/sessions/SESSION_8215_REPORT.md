# Session 8215 report (chain 502, lab-desktop second window)

19 November 2026, 12:39 to 12:44 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 12:38: both still waiting.

## Part D, second round: large_load, 1 draft; emissions_climate, 12 drafts

- large_load, waits by request size (`large_load.py --only-size`, `large_load_waits`, internal: "license needed"): requests of 300 MW and over against under 20 MW, the summary's rule, drafted only where the two ranges do not overlap and the 20 to 100 MW class lies on the same side. One of seven passes: at Bonneville, the median time from request to withdrawal was at least 17.1 and at most 27.4 months for 15 requests of 300 MW and over, against at least 42.8 and at most 56.2 months for 9 under 20 MW.
- emissions_climate, CO2 from energy by country (`deep/worldco2.py`, `eia_world_energy_co2_annual`, from 1980): all energy, coal and natural gas; the world, then the United States, then the largest moves among countries of at least 200 million t in 2023.
  - The world's CO2 from energy: 37,928 million t in 2024 against 18,722 million in 1980.
  - The United States' CO2 from coal: 751 million t in 2024 against 1,454 million in 1980.
  - China's CO2 from natural gas: 832 million t in 2024 against 31 million in 1980.
- Caught on the dry run: before 1980 the series hold the United States alone, and the world aggregate equals it (the world's 1949 figure was the US's 2,206.7 million t). Every country now starts in 1980.
- Every draft of both families reproduces (16 and 28 of them); every new do-file holds.

## Code

- `large_load.py` (the size comparison) and `worldco2.py` on `wip/8202-findings` (`c3a7fa5da`).

## Needs the key

- Nothing.
