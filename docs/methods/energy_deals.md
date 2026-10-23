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
  Since session 531 the code checks too (below, "One deal across days").

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

## The comparables view (session 466)

`/deals?view=comparables` (in review, under the tracker's tab) sets the deals' disclosed figures side by side, one
dimension at a time: the deal type (the extraction's fourteen types, the default), the technology as the story states
it, the grid (read from the state, as the tracker reads it) or the year (`?by=type`, `technology`, `grid`, `year`). The
register's folded pairs are counted once, as on the tracker. For each group, a row of one table:

- `deals|comp_deals|<dimension>|<value>`: the deals of the group;
- `deals|comp_with_price|<dimension>|<value>`: those that state a price in US dollars per MWh;
- `deals|comp_median_price|<dimension>|<value>`: the median of those prices, only where three or more deals state one;
- `deals|comp_with_mw|<dimension>|<value>`: those that state a size in MW;
- `deals|comp_median_mw|<dimension>|<value>`: the median of those sizes, only where three or more deals state one.

The value is the group's own (a type's id, a technology's words, a grid, a year), "-" for the group that does not state
it. **Nothing is computed from fewer than three disclosed deals**: a group with fewer says "fewer than three". A median
is of the figures the stories state; a deal that states none is left out, never counted as zero. One chart beside the
table shows the median price of each group that has one; where no group of the dimension has three deals that state a
price (every group of the 492 rows of 20 October: none states a price), it shows the median size, and says so. The
functions are `comparables()`, `medianOf()` and `shown()` of `site/lib/deals2.ts`; `site/scripts/check-values.mjs`
recomputes every key with the same functions on the live set's rows. Under the hold the view shows the hold's words
and the rows it covers, and nothing of a row.

## Held by row: how a row is shown (sessions 499 and 500)

The site can now hold `energy_deals` row by row instead of whole, by each row's own license (session 441's method,
[`docs/reviews/sources-by-row-2026-10-21.md`](../reviews/sources-by-row-2026-10-21.md)). Nothing changes until the data
machine does two things: the table's CSV carries a column `row_license` (one of `public`, `license needed`, `unsettled`,
computed from every publisher the row rests on), which the loader keeps in the row's `extra`; and
`warehouse/metadata/license_status.csv` marks the table `hold = row`, which `scripts/licenses.py status` copies into
`site/data/license_status.json`. Today no table carries the mark, so the deal pages show the hold as above.

Once both are there, the site's one reader (`site/lib/supabase.ts`) asks for the public rows only
(`extra->>row_license=eq.public`) and checks each row again when it comes back; a row with no `row_license` is held. The
three deal views (the deals, the tracker and the comparables) show the public rows as they show every deal, each with its
stories linked, and a line above them says how many rows are held and why: a count of the rows whose license is missing
or not public (check key `held|events|energy_deals|rows`), never a row of them. Every figure the views compute (the
month's count and MW, the tracker's counts, the comparables' medians) is then of the public rows only. The download of
the table, Ask and the catalogue on `/data` still treat it as held whole: serving its public rows there waits for a later
session and Samuel's ruling.

## One deal across days (session 531)

The Roundup audit of 21 October (`docs/reviews/roundup-audit-2026-10-21.md`, fix 8) found deals printed twice in two
issues: the Department of Energy's loan to Vistra (a row of 2 October, "US" lending USD 4 billion, and one of 5
October, "Department of Energy" lending USD 4.2 billion) and Amazon's PPA with Constellation (a row of 30 September,
and one of 6 October, "nuclear expansions", from the story of Google's deal that says Constellation signed with "both
Google and Amazon in the last week"). The second rows came from the daily run: it sends only the stories it has not
checked, so a deal reported over several days is sent again with its later stories, and the model's `same_as` was the
only guard. It left both empty.

From session 531, `warehouse/deals/extract.py` applies three rules of `warehouse/deals/deal_parties.py` to every deal the
model does not mark as one already held. No model is called for them.

- **One deal, one row.** The deal is merged into a deal already held, as a `same_as` would be, when the two have the
  same type and the same two parties (buyer and seller, in either order), are dated within 30 days of each other, name
  assets that share a word (when both name one), and state sums within a quarter of each other (when both state one).
  A name is the same party when one is the other with words added ("Constellation", "Constellation Energy"); the US
  government is one party whatever the story calls it ("US", "DOE", "Department of Energy", "Pentagon").
- **Two governments are not a deal.** A deal whose buyer and seller are both governments or countries is not kept: in
  the stories held such rows were policy, talks or a memorandum ("Trump says Russia to supply diesel to US and global
  markets"; 8 of the 497 rows of 21 October, each with a confidence of 0.6 or less).
- **A party the story does not name is not kept.** A buyer or seller whose name is not in the story's words (an
  equity raise's "investors" where no investor is named) is left empty, as a number without its words is.

Each is said in the run log. The rules change what a later extraction writes, not the rows already held: the table is
as the extraction left it, so the tracker's counts did not move. Run over the 497 rows of 21 October, read only, the
first rule finds four repeats: the audit's two, session 113's folded Prysmian and Atkore pair, and its doubtful Lynas
pair (the Pentagon and "US" are one party for the rule). Folding the held rows is the register's (`duplicates.csv`), a
person's choice.

## The public rows, keyed (session 822)

Chain 080 sorts the deals by the publishers of their evidence rows (`warehouse/deals/public_rows.py`, session 821;
`docs/reviews/deals-public-rows-2026-10-23.md`): a deal at least one of whose evidence rows comes from a publisher
whose terms the ERW reads as public ("may be public" in `license_verdicts.csv`) is shown; a deal every evidence row of
which asks for permission is held; a deal resting on a publisher whose page was not read is unsettled. The reader
writes `site/data/deals_public.json` from the archive's copy of the two tables (the live set is not asked for a held
table's rows): the counts, and each shown row as the live set would serve it, with its source, source_url and
story_urls set from the public evidence alone, so no held outlet's name or address is in the file. The table on the
deals tab draws the shown rows with every column; the line above it counts the held and the unsettled.

- `dealpub|counts|shown`, `dealpub|counts|held`, `dealpub|counts|unsettled`: the three counts of the line above the
  table. `check-values` reads the live set's row count of `energy_deals` against the file: shown is the live count
  less the file's held and unsettled, so a file older than the table fails the check.
- `dealpub|<deal>|mw` and `dealpub|<deal>|dollars`: a shown row's `mw` and its dollars, read again from the live set's
  row by its id, only for an id the file lists as shown.

- `dealpub|tracker|all|<stat>` and `dealpub|tracker|selection|<stat>` (session 823), with the stat one of deals, mw,
  with_mw, with_price, with_dollars: the tracker's counts over the shown rows only (every shown deal, and the page's
  selection, which with no selection is the same), the register's folded pairs shown once; each says so in its hover
  tip with the held count beside it. `check-values` recomputes them with `lib/deals2.ts`'s own functions over the
  live set's rows whose ids the file lists as shown.
- `dealpub|comp_<stat>|<dimension>|<value>` (session 823): the comparables' cells over the shown rows, as
  `deals|comp_<stat>|...` names the held table's; nothing is computed from fewer than three deals that state a figure.
- The tracker's deals-by-month chart draws the shown deals and, hatched above them, the held or unsettled deals dated
  in the month (`held_by_month` of the file: a count a month, nothing of a row), with the tip saying so.

Session 828 writes "What is shown and what is held" in full.
