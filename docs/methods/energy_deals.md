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

## Master plan tool 6, field by field (session 465)

Master plan tool 6 (`docs/master_plan.md`): "Structured, running database of every deal struck to power AI: nuclear
restarts, SMR offtakes, gas buildouts, PPAs, behind-the-meter, with counterparties, MW, price where disclosed, and
status." Each field against `energy_deals` as extracted on 2026-10-20T06:17:34Z (492 rows); the counts are in
`docs/reviews/deals-tool6-2026-10-21.md`, with the script that made them.

- **Held as a field**: the type (fourteen types, with `ppa`, `offtake`, `project_finance`, `m_and_a`,
  `nuclear_restart`, `smr` and `behind_the_meter` among them), the buyer, seller and other parties, `mw`, the price
  (`price` in USD per MWh, `price_value` with `price_unit` otherwise), the status, the AI power tag.
- **Read from fields already held** (session 465, `kindsOf` in `site/lib/deals2.ts`, nothing written to a table): the
  four kinds tool 6 names that the tracker's groups gather under Other. Nuclear restart, small modular reactor and
  behind the meter are the extraction's own type, or the same words in the asset or the technology ("restart",
  "small modular", "SMR", "microreactor", "behind the meter", "co-located", "on-site"). Gas generation has no type: a
  deal is of it where the technology names gas and the asset a plant, a turbine or generation, an acquisition or a fuel
  supply excepted. Whether a plant is new build the table does not say, so the kind is called gas generation, not a
  buildout. The tracker offers the kinds and the status as two more choices; the AI power subset was already one click.
- **Needs a pull not approved**: a deal's point of delivery and node, its tenor where the story omits it, and prices the
  stories do not state (a filing or a press release beyond the news the ERW reads).

## The hold (session 465)

From 21 October 2026 `energy_deals` is "license needed" (`warehouse/metadata/license_status.csv`; the owner's ruling of
12 October 2026, drawn on the pages by session 215): every deal of the table was extracted from news stories, and the
outlets' own pages ask for permission. The pages draw the catalogue's words where a deal would be, and say how many
rows the hold covers: `catalogue|energy_deals|n_rows`, the row count of `energy_deals` in the catalogue, the figure
`/data` shows. No row of the held table is read for it.

Which rows rest on a source whose terms the ERW reads as public was counted by the third machine's session 441 on the
files of 20 October (`docs/reviews/sources-by-row-2026-10-21.md`, on `wip/441-450-third` until it lands): 9 of the 492
rows, all from World Nuclear News, none with a stated MW. Showing those rows alone needs a license column a row (that
review's method) and a ruling; until then the hold is whole.

## Decisions

The pages list every choice they make about the deals, one line each with its session and ruling, in a block under
every tab (`site/app/deals/Decisions.tsx`, session 465).
