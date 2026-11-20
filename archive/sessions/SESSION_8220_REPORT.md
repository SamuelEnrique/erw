# Session 8220 report (chain 502, lab-desktop second window)

19 November 2026, 12:55 to 13:02 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 12:54: both still waiting.

## Part D, second round: authorities, 7 drafts (peak season, load factor)

- Two measures added to `authorities.py`: the share of each authority's 100 highest hours that fell in January, February or December, and its load factor (the mean hour over the highest), a lone spike dropped first.
- Folded: TVA and Southern Company (the regions' and chain 164's winter drafts); Duke Energy Progress East, Duke Energy Carolinas and Dominion Energy South Carolina (inside the Carolinas region, whose winter-share draft exists).
- The three strongest:
  - ERCOT's load factor: 66.6 percent in 2025 against 58.8 percent in 2019.
  - NorthWestern Energy (Montana): 78 of its 100 highest hours fell in winter in 2025, against 42 in 2019.
  - Tucson Electric Power's load factor: 47.9 percent in 2025 against 40.8 in 2019.
- Every authorities draft reproduces (26 of 26); 7 of 7 new do-files hold.

## Code

- `authorities.py` on `wip/8202-findings` (`ed384eb87`).

## Needs the key

- Nothing.
