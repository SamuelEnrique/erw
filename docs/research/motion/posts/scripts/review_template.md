# LinkedIn video posts, 24 November 2026 (session 9900)

Chain of 24 November 2026, night, on lab-desktop. Branch `wip/linkedin-posts-2026-11-24`, not landed. Nothing was posted or published anywhere. Model spend USD 0. Every video uses the approved template of 17 November unchanged (Part A: pixel-identical regression, in the note).

![Every post's final frame](img/all_final_frames.png)

Final frames, left to right, top to bottom: Thanksgiving peak hour; gasoline A; gasoline B; US oil share A; US oil share B; Texas late-January peak; uranium A; uranium B; Dominion mean hour; Canada to New York; California batteries; ERCOT solar.

## Ready

- B2, Thanksgiving: the hour the grid peaks (seven grids, square and tall).
- B3, gasoline on Thanksgiving week, versions A and B (square and tall).
- C1, US share of world oil and liquids production, versions A (full scale 100%) and B (scale to the largest row).
- C2, Texas's highest hour of demand in late January, 2020-2026.
- C3, uranium of US origin, versions A (100%) and B (largest row).
- C4, the mean hour of demand in Dominion's Virginia zone.
- C5, the mean hourly flow from Canada to New York.
- C6, California's battery fleet against its peak-day demand.
- C7, solar's output in ERCOT's tightest hours.
- Every version passed the fit checks and the number check (84 rows, 0 mismatches).

## Decisions made without you

- MISO is drawn in Central time (where most of its load is); EIA's file stamps MISO in Eastern Standard Time, which is why the chat's cross-check read one hour later (11 to 13 and 19 or 20). The shift (7 hours) is the same in either clock.
- California is kept in B2: its 2024 and 2025 midday peaks are battery charging counted as demand (explained below); both medians are 6 pm either way.
- Clock times in B2 are the end of the peak hour (hour ending 19 is "7 pm"), as the chat's example "7 pm to noon" reads. B2's bars use the largest shift (9 h) as full.
- The 200 px track floor is applied to the 1080 x 1080 layout, as written; the tall layout scales every column by the template's 1.08 to 1.15, and B2's tall track is about 145 px (checked by eye, nothing overlaps).
- Number columns with a display text get the template's own 18 px of slack past the widest number. JavaScript's rounding is never used for a drawn figure: every display is written from the source digits rounded half up (toFixed would print 3.805 as $3.80 and 3.395 as $3.39).
- Percent posts use 100% as a full bar (the template's scale); MW and dollar posts use the largest row. For the two low shares (oil 22%, uranium 18%) both scales are rendered.
- Uranium: seven evenly spaced years from 2003 cannot all be held (EIA prints no US-origin figure for 2019, 2020 and 2022), so the years are 2003 plus steps of 22/6 rounded: 2003, 2007, 2010, 2014, 2018, 2021, 2025.
- Oil: 1995 to 2025 every five years (the table starts in 1993, within three years).
- Texas title shortened to "Texas's highest hour of demand in late January" (the first wording took three lines); the window, 23 January to 2 February, is in the source line.
- B3 uses 16 November 2026: at 10:32 UTC on 24 November EIA's API had not published 23 November.
- Sections 9 and 12 were not added: B1 is blocked, so not all ten posts were done.

## For Samuel's ruling

- **B1 (Nvidia) is blocked.** SEC EDGAR answered 403 ("Request Rate Threshold Exceeded") to the ERW's contact string at its robots file, as in sessions 2049 and 3304: SEC asks for a company name and a contact email in the User-Agent. Name the email (or decline) and a later session can pull the shares. For the closes, Stooq's robots file allows only Bing and Google, and Nasdaq reset the connection; no other price source was read. The data file holds the header and the block only: https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/docs/research/motion/posts/data/nvidia_energy_caps.csv
- B3 version B, "Everything is on sale this Friday. Gasoline isn't.": true against past Thanksgiving weeks (2026 is the highest since 1990), but gasoline fell 35 cents in the two weeks to 16 November ($4.153 to $3.805). Keep B, or use A?
- Oil and uranium: full scale (A) or largest row (B)? A is the template's scale and the honest one for a share; B shows the year-to-year change better.
- B2's tall layout: the bar track is about 145 px. Keep, or shorten the clock texts (for example "7pm-noon") for the tall master?
- California in B2: keep with "0 h", or drop it and render six grids with "Seven grids together" first?

{{post:thanksgiving_peak_hour}}

{{post:thanksgiving_gasoline}}

{{post:us_share_world_oil}}

{{post:texas_cold_peak}}

{{post:uranium_us_origin}}

{{post:dominion_mean_hour}}

{{post:canada_new_york_flow}}

{{post:caiso_battery_peak}}

{{post:ercot_solar_tight_hours}}
