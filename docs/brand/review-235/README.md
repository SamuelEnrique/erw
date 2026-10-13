# Review 235: "What a generator earns" on the brand, the capture price back, scenario B as a PPA

Session 235, 13 October 2026, branch `wip/235-generator`. The page at `/cost-of-power/seller`, in the internal view, on a
local production build, ERCOT, solar, 100 MW, the hub average. Full pages, quantized to 64 colors.

| File | What it is |
|---|---|
| `generator_before_1280.png` | the page before this session (session 212's layout, the site's old style: cardinal bands, Georgia), 1280 px wide. Session 212's own capture of the same code and data |
| `generator_before_390.png` | the same at 390 px |
| `generator_after_1280.png` | the page after: on the brand, the capture chart and table inside "What did it earn?", "Make B a PPA" under the assumptions, the breakeven PPA price in the results; 1280 px |
| `generator_after_390.png` | the same at 390 px (each chart scrolls sideways inside its frame, as the battery page's does; the series' names are at its left, in view) |
| `battery_unmoved_1280.png` | the battery page on the same build: its checked numbers, its text and its height (5,016 px) are session 211's, to the line |
| `numbers_before_after.txt` | every checked number and results cell before and after; the 154 new keys of the capture table; the battery page's proof |

What to look at, in order:

1. The look against the battery page: white page, serif titles in ink, one dark rule under a table's head, mono figures.
2. "What it earned per MWh against the hub average": the chart (capture price in cardinal, hub average in ink, the
   capture rate above each pair, 2026 hatched) and the table (14 hubs and zones of ERCOT; the last twelve months, then
   each year's capture rate).
3. Under the assumptions: "Make B a PPA" and its one sentence.
4. The results table's ninth row, "Breakeven PPA price": USD 58.36 per MWh at the defaults.

The report: `archive/sessions/SESSION_235_REPORT.md`.
