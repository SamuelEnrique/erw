# Review 228: "What a datacenter pays" answers its four questions

Session 228, 13 October 2026, branch `wip/213-datacenter-layout` (not on `main`; Samuel reviews from these screenshots).
The page at `/cost-of-power` ("Your load"), in the internal view, on a local production build of this branch, ERCOT, LZ_NORTH, a flat 100 MW load, real time, at the defaults.

| File | What it is |
|---|---|
| `datacenter_before_1280.png` | the page as session 213 left it (three questions: what it will pay, which option is better, what matters most), 1280 px wide, full page |
| `datacenter_before_390.png` | the same at 390 px |
| `datacenter_after_1280.png` | the page after this session: "What will it pay?" unchanged, then "Will the power be there?", "How clean?" and "How soon?" each computed for the load, then the two decision questions; 1280 px |
| `datacenter_after_390.png` | the same at 390 px |
| `numbers_before_after.txt` | every number of "What will it pay?" and of the results table before and after (identical), and the new numbers with their check keys |
| `months_default.csv.txt`, `tables_default.csv.txt` | the two downloads for the default load, as the page serves them in the internal view (with their HTTP status on the first line) |

What to look at, in order: the three new sections and whether each answers its question for the load in one sentence
with the number; the three headline numbers and the one table under each; where the answer for scenario B would stand
(set B to run flexible under "Which option is better?" and read the third number of "Will the power be there?" and the
tonnes of "How clean?"); the sentence and the line of "How soon?" for a grid other than ERCOT (open the page with
`?grid=caiso`). The page keeps its current style. The report: `archive/sessions/SESSION_228_REPORT.md`.
