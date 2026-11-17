# Ruling alternatives: /play/battery (17 November 2026)

Session 7718 (samueloldlaptop, claimed in `docs/state/ruling_alternative_claims.md`). For each line of `docs/reviews/ruling-impact-play-battery-2026-11-17.md` whose change is 1 percent or more, or that adds or removes a figure, the other choice is built on its own branch from origin/main, with a test that pins the figure under it. The branch number is the line's number in the impact file. No branch asks to land; no default on main changed.

- **The figures are the game's own:** its rules (`site/lib/battery.ts`: `optimum`, `rulesOf`, `simulate`) run on its committed famous days (`site/data/battery_levels.json`); every test runs on any machine. The impact file used the rules of `wip/7535-play-battery`; on main's rules the perfect scores are the same (Uri USD 240.23, the August 2023 heat 60.97).
- **No model call** was made (spend USD 0).

## Decisions made without Samuel

- Line 1 offers 2, 4 or 8 hours. The branch takes 4 (5 kW, 20 kWh): 8 hours (40 kWh) is beyond the game's own largest battery (30 kWh), and 2 hours (10 kWh) is smaller than the battery the game has now.

| # | Line | Branch | Figure, main's rule | Figure, the other choice | Files touched | Test | Browser row |
|---|---|---|---|---|---|---|---|
| 1 | Change the game's battery (13.5 kWh and 5 kW, 2.7 hours) to one of the battery page's 2, 4 or 8 hour durations | `wip/alt-play-battery-1` (`0fe35954c`) | 13.5 kWh, 5 kW: the perfect battery on Normal, Uri USD 240.23, the August 2023 heat 60.97, the negative-price day 0.79, CAISO's duck day 12.98; the fleet 135 MWh | 20 kWh, 5 kW (four hours): Uri 301.40 (+25.5 percent), the heat day 67.98 (+11.5), the negative-price day 1.01 (+26.7), the duck day 13.48 (+3.9); half full at the start is 10 kWh; the fleet 200 MWh. Every player's score moves with it, and past scores under the old preset no longer compare. Computed with the game's own rules on its committed days, as the impact file has them | `site/lib/battery.ts` (`SETTINGS.kwh.def` and its source), `site/app/play/battery/page.tsx` (three sentences follow the default), `site/scripts/alt-play-battery-figures.mjs`, `tests/test_alt_play_battery_1.py`; nine tests skipped with their reason because they pin the 13.5 kWh default's figures: `test_session111` (2), `test_session289` (2), `test_session290` (2), `test_session38` (1), `test_session66` (2) | `tests/test_alt_play_battery_1.py`, 3 of 3; the 15 test files that name the game, 147 tests, pass with those nine skipped (all nine pass on clean origin/main); no new type error | 344 |
