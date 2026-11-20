# Session 8204 report (chain 502, lab-desktop second window)

19 November 2026, 11:27 to 11:40 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Family 4, the nine events of /events across the thirteen regions: 30 drafts

- `docs/findings/events/`, loaded in state draft; second pass 30 of 30 reproduce; 30 of 30 do-files hold.
- Each event's window (`docs/methods/events.md`) read in all thirteen regions: the window's highest hour of demand (COVID-19's spring: its mean hour) against the same calendar days of every other year held, demand summed from the authorities. Its own five tests (`deep/events.py`): the extreme of the years held, clear by a typical spread, sample large enough, holds against the median, not one hour.
- 113 claims, 42 pass; at most five an event, the six regions no page shows first.
- The three strongest:
  - Tennessee's highest hour in the days /events gives to Winter Storm Elliott: 33,225 MW, 33.9 percent above the same days' mean of the other seven years (24,815 MW).
  - Florida's highest hour in the late January 2026 cold: 52,211 MW, 33.5 percent above the mean of 2021 to 2025 (39,100 MW).
  - The Carolinas' mean hour over the COVID-19 spring of 2020: 20,644 MW, 9.4 percent below the other seven years' mean (22,773 MW).
- The August 2020 West heat wave passes in no region (its window is not the extreme of the years held in any).
- No flow between regions in this family: event-time flows are the donor ledger the chain file leaves to Samuel.

## Code

- `warehouse/analysis/findings/deep/events.py` on `wip/8202-findings`: its own claim, tests and card (the chart: each day's highest hour in the event year against the other years' mean of the same day).

## Decisions made without you

- The other years are the same calendar days in UTC, not the weekday-aligned baseline of the /events pages; the limits sentence says so.
- The sentence says "the days /events gives to" an event, not "during", so that Florida's high in the September 2022 West heat wave's days is not read as caused by it.

## Needs the key

- Nothing.
