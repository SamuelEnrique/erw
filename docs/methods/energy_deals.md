# Energy deals and the companies they name

The deal tracker (`/deals`: the deals, the tracker and the companies tabs). Written by session 329 (20 October 2026)
from the builders' own descriptions, `warehouse/deals/extract.py` (session 15) and
`warehouse/companies/seed_from_deals.py` (session 27); until then the page's lead paragraphs were its only note.

## Where a deal comes from

- **The stories.** The news stories the ERW scores (`news_stories`, `warehouse/news/`) that are scored, of the sectors
  deal, ppa, capital, nuclear, generation, datacenter_power, lng, oil or gas, with a significance of 5 or more. The
  page shows the deals reported since 1 October 2025.
- **The extraction.** Stories about the same event (the scorer's cluster) are sent together to a model, which says
  whether they report a specific transaction and, if so, extracts each deal: its type, buyer, seller, other parties,
  asset, technology, state, country, megawatts, megawatt hours, dollars, price, term, status, announced date, whether
  it is for AI power, a confidence, and the evidence sentence.
- **No number is inferred.** For every number the model returns the exact words of the title or summary it read it
  from; the number is kept only if those words are in the story and parse to the same value, and is blank otherwise.
  A state, a country and a status are kept only where the story's words name them (session 16's ruling).
- **One deal, every story.** Each call carries the deals already extracted, and a deal the model marks as one of them
  adds its story to that deal instead of making a new one; `warehouse/deals/duplicates.py` lists the pairs left.

## The tables

| Table | License | What it holds |
|---|---|---|
| `energy_deals` | public | one row a deal (the events shape, `docs/datastandard.md`): the fields above and the story links, no outlet text |
| `energy_deals_evidence` | internal | one row a deal and story, with the evidence sentence (outlet text): not on the site |
| `energy_companies` | public | one row a company: those the Thesis Builder found (`docs/methods/thesis.md`) and every buyer, seller and other party of a deal |

## The tabs

- **Deals:** every deal in a table with its filters and their Reset; the counts of the month (deals, megawatts, the
  share for AI power) are computed from `energy_deals` and read again by `check-values`.
- **Tracker:** the same deals by type, technology, grid, counterparty and year.
- **Companies:** a party of a deal becomes a company row named as its deals most often spell it, with the sector of
  its deals' stories, a tag for each deal type and technology, the place a deal states (where the deal is, not
  necessarily where the company is based), the stories as sources, and the Thesis Builder's confidence rule (20 a
  source, up to three, plus 20 or 10 for recency). Its stage, raised amount and founders stay blank, marked "from
  deals; not yet researched", until the Thesis Builder researches it. A party that is not a company (a description, a
  government, a law, a university) stays in the deal and is not a company row. Each confidence is read again by
  `check-values` (session 329).

## Downloads

Under each tab, its public tables as the live set's CSV with a Python and a Stata reader of that CSV (session 328's
shared line); the evidence table is internal and is not offered.

## The figures on the page and their keys

Each number `/deals` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `deals|month_count|<month>`: the deals of the month in the first cell, counted from the rows of `energy_deals` whose announced date falls in it (at the start of a month with no deal yet, the previous month, labeled).
- `deals|month_mw|<month>`: the MW announced in that month, the sum of the deals' `mw`, with the number of deals that state MW beside it.
- `deals|month_ai_pct|<month>`: the share of that month's deals tagged AI or datacenter power, rounded to a whole percent; with no deal in the month the cell says so and shows no number.
- `event|energy_deals|<deal>|mw` and `event|energy_deals|<deal>|dollars`: a deal's `mw` and its dollars in the table's row, blank where the story states none.
