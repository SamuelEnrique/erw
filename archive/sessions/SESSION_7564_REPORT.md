# Session 7564 report: Research (Automated Analysis) read as a fund analyst (samueloldlaptop, 17 November 2026 UTC)

- **Asked:** the fifth of the six reads: `/research`. Checked first: no `research-read` file on any branch; part A's 7 rows read; the Research pack's ruling 6a found in `docs/methods/automated_analysis.md` (callouts only).
- **The read:** `docs/reviews/research-read-2026-11-16.md`. Five cases (today's chart; this week's chart; the peak hour, five grids; gas sets the price; the cards' files), 8 rows: 2 site fixed, 2 data machine (requests 309, 310), 2 rulings, 2 browser (309, 310).
- **Found, the most serious of the six reads:** three library cards printed NYISO's and ISO-NE's figures in their why paragraphs and drew them in their charts, while their callouts already read "license needed"; their public CSVs and pictures carry the same rows. Both grids are held since 21 October 2026.
- **Fixed on the page:** `site/lib/cardhold.ts` (new) holds a held grid throughout a card where the cards are read (`lib/findings.ts`): panels and series leave the chart for a "license needed" placeholder; a why or footnote sentence with a held grid and a figure is taken out, with one line saying so. The weekly chart's heading names an old week for what it is (`weekChartTitle`). Tests: `site/scripts/test-research-read.mjs` 17 of 17; pytest of the eleven importers, 205 passed, 1 skipped; `check-analysis-flow.mjs` updated (needs a server, not run).
- **Not fixed here:** today's chart's wrong earlier record (the scanner was fixed on 13 November; the file of 12 November predates it), request 309; the public files, request 310.
- **What to review:** `https://erw-flame.vercel.app/research#library` (the three five-grid cards); `https://erw-flame.vercel.app/research#week` (the heading).
- **Needs the key:** nothing.
- **Decisions made without you:** the hold follows ruling 6a to the why, the footnote and the charts, since the page standard holds every held value; a sentence naming a held grid with no figure stays.
- **For Samuel's ruling:** rows 5 (a title naming a held grid; default: words with no figure stay) and 6 (the readers follow the CSV).
