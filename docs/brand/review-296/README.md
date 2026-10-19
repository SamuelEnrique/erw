# Session 296: the battery page, pass 1 (Samuel's ten rulings of 15 October 2026)

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026. "Before" is production
before the session (the page as session 295 left it); "after" is the local build of branch `wip/296-battery-pass1`
in its default state (the box's two open sections open, the three closed ones closed). Taken with
`runs/chain_oct19/capture296.mjs` (session 208's capture, keeping each section's own state), which also kept each
page's checked numbers and visible text under `runs/chain_oct19/s296/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `before_battery_*.png`, `after_battery_*.png` | `/cost-of-power/battery` | ERCOT, 4 hours, perfect foresight, 100 MW: the default page |
| `before_battery8_*.png`, `after_battery8_*.png` | `/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead` | the 8-hour battery: the ATB's defaults move its cost figures (item 8) |
| `before_caiso_*.png`, `after_caiso_*.png` | `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead` | CAISO: its own stress events in the window's "leave out" boxes |

What to look at, after:

1. The left box "Assumptions": five sections, "Assumptions" and "Headline figures" open, each closed one with its
   line ("Financing: Scenario A: 20% debt at 8%, 12% hurdle, no contract"; "Sensitivity: Sourced range, NPV").
2. The year chart's title mark (a hover tip) and its Chart | Table toggle; the unit at the top left, the series named
   at the top right with the hatched note.
3. "Income by stream": "From 2018 to 2026", "Leave out: Uri, Elliott, the 2023 heat" (ERCOT) or CAISO's notice days;
   the columns: the last twelve months, each calendar year, "Your window, a year".
4. "Is it worth building?": the results table alone, with the line that the twelve assumptions are set under Financing.
5. "What matters most": six rows at their published low and high case; the line naming the four with no range.
6. At 390 px nothing scrolls sideways (page width 390 in a 390 window, every address).

The headline, the summary sentence, the year chart's figures, the results table and the income table's figures at
the default window are the same as before on the 4-hour pages (660 of 660 check-values keys match Supabase; every key
the pages shared before and after carries the same value). On the 8-hour page the debt payment, coverage and the
scenario rows move with the ATB's defaults; its revenue does not.
