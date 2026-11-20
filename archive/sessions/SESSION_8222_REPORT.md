# Session 8222 report (chain 502, lab-desktop second window)

19 November 2026, 13:06 to 13:10 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 13:05: both still waiting.

## Part D, second round: cross_family, 8 drafts (utilities against their own forecasts)

- Each large utility's retail sales (EIA-861M, every state it serves summed, years with all twelve months) against the net energy its own FERC 714 filing of three and five years before forecast for that year (`cross502.py --utilities`). The respondent's EIA code is the 861M utility number; utilities with a state of retail or community choice, or under 10 TWh in 2025, are not read; a year under half or over twice its forecast is left out.
- The three strongest:
  - Florida Power and Light's sales ran 2.4 percent above its five-year-old forecast in 2025, against 11.9 percent below in 2019.
  - Georgia Power's: 1.0 percent above in 2025, against 12.6 percent below in 2019.
  - Arizona Public Service's: 1.1 percent below in 2025, against 12.9 percent below in 2019.
- Net energy for load also holds losses and any wholesale load the area serves, so the level of the gap means less than its move (the limits sentence says so).
- Every cross_family draft reproduces (25 of 25); 8 of 8 new do-files hold.

## Code

- `cross502.py` on `wip/8202-findings` (`68c824ce0`).

## Needs the key

- Nothing.
