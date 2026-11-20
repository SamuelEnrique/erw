# Note of 17 November 2026, old laptop, chain 402: the rulings in two lists

Session 7900 (samueloldlaptop, code role). The chain: `queue/done/402-day-17-november-oldlaptop-rulings-ranked.md`. Model spend USD 0. No page, default, table or branch landing was changed.

## The two lists

- **The ranked list:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-ranked-2026-11-17.md
- **The defaults list:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-defaults-2026-11-17.md
- Together they hold all 392 lines of the rulings list of 17 November.

## The ranked list's counts

- **129 entries**, from 133 lines of the rulings list (four entries cover a question the list holds twice).
- 31 change a headline figure, 36 change another figure, 62 add or remove a figure.
- **Recommendations:** keep 15, switch 26, no basis to recommend 88.
- Of the first 30 entries: every figure was looked for again in the measurement script's printout or the branch's test, and found; one figure this session had derived itself (a payback difference) was taken out.
- Screenshots linked when this note was written: 41 entries have a picture of the other choice, 17 also have the page as it is today; the rest say "screenshot not taken yet". The desktop is still pushing pictures; the list is redrawn by `runs/c402/render.py` on this machine.

## The figures that do not agree (12 entries, none carries a recommendation)

- Shoulder hours, the midday low: 8 months to zero in the measurement file's summary, 7 in its printout and in the branch's test.
- The EV game, California's electricity default: the measurement is on the price file of 15 October, the branch on the file rebuilt on 17 November (net present value -13.0 percent against -34.9 percent).
- Automated Analysis, the stored chart: August's margin over the old record is 295,123 MWh in one file and 295,122 in the other.
- The datacenter cost page, the Texas transmission rate: the measurement used 2025's rate (USD 7.83 per MWh), the build reads 2026's (8.62), so the change is +9.6 percent in one and -19.8 percent in the other.
- The battery page's signed note: USD 79.07 per kW on a partial October, USD 80.34 on the whole month; the build found the page already follows the data.
- The battery page's fold: 48 cells counted in the measurement, 72 on the build.
- The December 2022 storm's table: 619,177 against 619,176 MWh, one value rounded two ways.
- The hub page's A less B line: +407.81 against +407.82 USD per MWh, one value rounded two ways.
- The datacenter cost page, the four-peak saving: USD 20,564,190 at 2025's rate, USD 22,658,181 at 2026's.
- The datacenter cost page, California's study step: "60 to 90 days" in the measurement, "90 days" on the build; the document itself prints "60 to 90 days".
- Curtailment, Texas's shares: two figures said to leave the view, one found on the page.
- The generator page, the peaker's degradation bar: USD 2.38 million on the page, USD 2.53 million recomputed.

## The defaults list's counts

- **227 questions**: 183 by page, 41 that a license or a publisher holds, 3 that need the API key.
- Not repeated there: 133 lines that are in the ranked list, 3 more that ask a question the ranked list holds, 23 that repeat another line, 6 signature lines.
- **Needs the key:** about USD 3.0 to 3.1 for the lines whose cost the notes state (up to about USD 10.7 if every story of the older deals is checked); about USD 4.80 more to check the chat on the three large-load tables once they are in the live set.
- **Signatures:** 31 lines, one a tool, each with its method note and its do-file. The home battery game's do-file is on a branch that has not landed.

## Part 0, the two tools left open overnight

- The severance tax tool: the gas heat-content rule finished (`wip/alt-severance-3`, USD 10,427.63 to 10,782.16, +3.40 percent) and the collections hover built (`wip/alt-severance-2`); the claim marked done.
- The electricity bill page: the meter-read span finished (`wip/alt-bill-3`, USD 44.85 to 47.48 per MWh on the example span) and the wires' losses built (`wip/alt-bill-4`, every wholesale figure +5 percent); the claim marked done.
- Four rows wait for the desktop's screenshots (browser rows 373 to 376).

## What waits for Samuel

- His rulings, written after `Ruling:` under each entry of the ranked list, and "defaults stand" (or struck lines) on the defaults list.
- Whether the rule "no recommendation where two sources differ" should also bind where the two differ only by rounding (three of the twelve entries above). Default taken: it binds, and the entry says what would otherwise bear on it.

## Where the working files are

- The entries of the ranked list (`runs/c402/entries/`), its drawing script (`runs/c402/render.py`), the check of the first 30 (`runs/c402/check30.py`) and the defaults list's script and sorting (`runs/c402/partb.py`, `partb_data.py`) are on the old laptop, not in git.
