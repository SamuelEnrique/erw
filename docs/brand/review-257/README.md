# Session 257: California on the battery page and the generator page

Screenshots in the internal view, a local build of branch `wip/257-california` in its worktree, 13 October 2026. Each
is the whole page at its width, quantized to 32 colors so that the folder stays under 2 MB. Taken with
`runs/session208/capture.mjs`, which also kept each page's checked numbers and visible text (in `runs/session257/`,
not in git).

| File | Address | What it shows |
|---|---|---|
| `battery_caiso_1280.png`, `battery_caiso_390.png` | `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | CAISO chosen, a 4-hour battery on the day-ahead schedule |
| `generator_caiso_1280.png`, `generator_caiso_390.png` | `/cost-of-power/seller?iso=caiso&asset=solar` | CAISO chosen, a solar plant at SP15 |

What to look at:

1. The battery page, under "Income by stream": the new line. "In 2025, for a 4-hour battery on the day-ahead schedule,
   this model takes USD 42.31 per kW from energy and USD 42.25 from regulation; CAISO's market monitor reports that real
   batteries in its area with a full year of operation earned about USD 35 per kW from energy and USD 9 from
   regulation", with the report cited and linked. The first two figures are computed from the table and carry check
   keys; the last two are the report's.
2. The battery page, the small line under the table that begins "Every month, CSV": it ends with California's stress
   days by their days ("4 to 9 September 2024, 20 and 21 January 2025, 9 and 10 September 2026, 5 to 8 October 2026")
   and the table's download, as ERCOT's ends with "Uri, Elliott, the 2023 heat".
3. The generator page, the foot: "Checked against: 20 published figures (Lazard, the Annual Technology Baseline, EIA,
   CAISO's market monitor, Berkeley Lab)". Nothing else on that page changed.

The four files are 0.87 MB together. At 390 px neither page scrolls sideways (page width 390 in a 390 window).

No "before" screenshot is here: for ERCOT the battery page's 51 checked numbers were compared with session 211's and
none differs, and its height is the same 5016 px (`archive/sessions/SESSION_257_REPORT.md`, "Checks").
