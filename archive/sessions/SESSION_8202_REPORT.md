# Session 8202 report (chain 502, lab-desktop second window)

19 November 2026, 11:13 to 11:25 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting (`site/data/industry.json` not on main, `ai_energy_published` not in coverage).

## Family 2, the six regions the site has never shown: 27 drafts

- `docs/findings/regions/`, loaded to `public.scanner_drafts` in state draft; second pass 27 of 27 reproduce; 27 of 27 do-files hold.
- Ten candidates over the Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest: the peak hour, the mean hour, winter's peak against summer's, the winter share of the top 100 hours, the load factor, net generation against demand (EIA-930, demand summed from the authorities), and coal, gas, solar and nuclear shares of the core states' generation since 2001 (`eia_state_generation_monthly`; the hourly tables hold no fuel, and the sentence names the states).
- The three strongest:
  - The Carolinas' highest hour: 47,130 MW in January 2025, against 41,648 MW in August 2019; 37 of the 100 highest hours of 2025 fell in winter, against 4 in 2019.
  - Tennessee's winter peak hour was 109.2 percent of its summer peak in 2025, against 94.0 percent in 2019.
  - Coal's share of Georgia and Alabama's generation: 14.4 percent in 2025 against 60.2 percent in 2001; gas's 42.2 percent against 5.5.
- The peaks were checked by hand (`runs/c502/peaks.py`): each year's five highest hours sit together, no lone spike.
- Folded: Tennessee's net generation against demand (the trade family's net imports), the Southeast's and Tennessee's winter share of top hours (their winter peak draft).

## Code

- `warehouse/analysis/findings/deep/regions.py` on `wip/8202-findings` (`53dd21ebe`), stacked on `wip/8201-findings`. Its landing row is added when the stack is next requested.

## Decisions made without you

- Florida's demand sum is first full in 2021 (Gainesville's 2019 hours and New Smyrna Beach's end in 2020 leave 2019 and 2020 short), so its sentences compare with 2021.
- The fuel shares use the region's core states, named in the sentence, because the ERW's EIA-930 fuel mix starts in August 2026.

## Needs the key

- Nothing.
