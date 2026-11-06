# Energy deals and the companies they name

The deal tracker (`/deals`: the deals, the tracker and the companies tabs). Written by session 329 (20 October 2026)
from the builders' own descriptions, `warehouse/deals/extract.py` (session 15) and
`warehouse/companies/seed_from_deals.py` (session 27); until then the page's lead paragraphs were its only note.

Tables: `energy_deals`, `energy_deals_evidence`, `energy_companies`

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

## The tracker in the v2 shape (chain 156, sessions 2230 to 2247)

Written by session 2247 (6 November 2026) after the audit of the stored records (`docs/reviews/deals-audit-2026-11-06.md`): each field, its vocabulary and its evidence rule, the deduplication, the cross-checks, the counterparties, the views and their keys, the tracers, and what the extraction cannot see. Every rule below is a default this chain set without a ruling, listed in its session's report under "Decisions made without you"; none changes a ruling.

### Each field

| Field | Vocabulary or unit | Kept only where | Code |
|---|---|---|---|
| `deal_type` | the form: ppa, offtake, m_and_a, project_finance, tax_equity, debt, equity_raise, joint_venture, lease, behind_the_meter, nuclear_restart, smr, fuel_supply, other (session 15, unchanged) | the model names it | `extract.py` |
| `kind` | master plan tool 6's kinds, the power kind first: nuclear_restart_uprate, smr, behind_the_meter, gas_buildout, transmission, storage, compute_capacity; then the form: ppa, offtake, project_finance, m_and_a, capital, fuel_supply, other | read from the deal's own words (asset, technology, evidence) in code, else the model's kind, else the type's; `kind_basis` says which | `fields.kind_of` |
| `stage` | rumored, announced, signed, financed, closed, under_construction, operating, cancelled | its words (`stage_text`, in the evidence table) are in the story | `fields.stage_of` |
| `status` | rumored, announced, signed, closed, cancelled (session 15, the Roundup's) | its words are in the story; a later stage moves it forward | `extract.py`, `dedupe.merge` |
| `status_history` | "date stage (story)", oldest first | every change of stage a story brings | `dedupe.merge` |
| `mw`, `mwh`, `usd` (= `dollars`), `term_years` | MW, MWh, US dollars, years | its span is in the title or summary and parses to the same value (GW, bn applied); no figure is converted from another currency, from months or from words without digits | `extract.verified` |
| `usd_per_mwh` (= `price`) | US dollars per MWh | stated so; a price in another energy unit stays in `price_value` with `price_unit`; a percentage or a share price is never a price | `fields.energy_price` |
| `grid` | ERCOT, CAISO, PJM, MISO, SPP, NYISO, ISO-NE | the story names the operator; never read from a state in the table (the page reads a state's main grid, and says so) | `fields.grid_of` |
| `state`, `country` | a US postal code; a country as named | the story's words name it (session 16's ruling) | `extract.stated_words` |
| `ai_power` with `ai_power_basis` | true or false | a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party (`fields.AI_PARTIES`), or the story's words name a datacenter load; a motive alone ("as AI demand booms") is false | `fields.ai_of` |
| `confidence` | 0 to 1 | the model's, in its bands (0.8 a stated deal between named parties; under 0.6 a doubtful one); its words (`confidence_basis`) in the evidence table | `extract.py` |
| `buyer_name`, `seller_name`, `buyer_parent`, `seller_parent`, `buyer_eia861`, `seller_eia861` | one name a company; its parent; an EIA-861 utility number | the rules of `docs/methods/deal_counterparties.md` | `counterparties.annotate` |
| `flags` | words | the cross-check finds a headline's figure the record lacks or contradicts, MW and MWh or USD and USD per MWh confused, a term in months, a figure above a bound | `crosscheck.flags` |

**Not a deal** (the prompt's list, session 2232): a plan or a pledge to invest, a seeking with no counterparty, a government's permission, two governments, a raise whose company the story does not name. **A deal needs a party the story names**: a buyer, a seller, a joint venture's partner, or the company sold. **The evidence** of every field is the story's own words, kept in the internal `energy_deals_evidence` (the sentence, the stage's words, the confidence's words, the figures' spans); no outlet text is in `energy_deals`.

### One record a deal

`warehouse/deals/dedupe.py`: session 531's rule, and a deal with one party named matched to a held one where a size both state agrees; a name and its initials one party; a later stage within a year; the size within tolerance (USD a quarter, MW a tenth). A merge keeps the earliest first-reported date, moves the stage forward with its history, fills a gap and never replaces a figure held. The register (`warehouse/deals/duplicates.csv`) folds what a person or a session judged one deal.

### The views and their keys

- **The table** (`/deals`): the filters kind, grid, state, counterparty, MW from and to, year, AI power, stage, price disclosed; every column sorts; the downloads are the rows shown (CSV with the ERW's header lines and no outlet text, a Python and a Stata reader). Its figures: `event|energy_deals|<deal>|mw` and `|dollars`.
- **The disclosed prices** (`/deals?view=comparables#prices`): the PPAs and offtakes stating a price per MWh by technology, grid or year; `deals|price_count|<dimension>|<value>` always, `deals|price_median`, `deals|price_low` and `deals|price_high` from three. A reader's own deal is placed against them in one line, nothing stored or sent.
- **The AI-power view** (`/deals?view=ai`): the tagged deals by buyer, kind of supply, grid and quarter: `deals|ai_deals|<dimension>|<value>`, `deals|ai_mw`, `deals|ai_with_mw`, `deals|ai_usd`, `deals|ai_with_usd`; the ten with the most MW and the ten with the most US dollars.
- **The charts** (`/deals?view=charts`): `deals|chart_mw|<quarter>|<kind of supply>` (and `|without`), `deals|chart_price|<deal>|price`, `deals|chart_ai|<quarter>|share`, `|ai_mw`, `|all_mw`, `deals|chart_party|<name>|mw`.

### The tracers

`site/scripts/check-values.mjs` recomputes every key above with the page's own functions on the live set. `scripts/check_deals.py` recomputes every chart figure from `energy_deals.csv` with its own Python and compares it with the page's functions (71 of 71 on 6 November 2026). `warehouse/deals/eval/fixture.py` grades the extraction on stored stories with answers written from their words (`tests/fixtures/deals/`); `warehouse/deals/eval/one_day.py` runs a stored day end to end, offline.

### What the extraction cannot see

The warehouse holds a story's title and a short summary (a median of 77 characters on 6 November 2026), not its text. A figure the headline does not state, a deal's point of delivery and node, its tenor where the story omits it, and its price are almost never there: 6 of 18,358 scored stories state a price per MWh. A deal only a press release or a filing describes is not seen until a pull of those is approved (the rulings of 23 October, items 5 and 6). The extraction reads what the outlets report, so the counts by month follow the ERW's news coverage, not the market (the Roundup audit's fix 3).

### A deal with one party named (session 2256)

A sale, an award or a raise whose story names one party and not the other ("Crescent Sells Non-Op D-J Assets": no buyer named; "Sellafield selects partners": no partner named) gets no row by default: the prompt asks for a named deal between named parties. `ERW_DEALS_ONE_PARTY=on` adds one sentence to the prompt that returns such a deal, with the named party in its field and the other empty; the default is off and leaves the prompt as it was, character for character, until the owner rules (chain 156's ruling 2). On the six stated deals of the audit's sample with no row, the switch on returns three (the two above, and Shell's sale of Jiffy Lube to Monomoy Capital, a sale of an asset that is not an energy asset); a plan ("plans $1.8 billion investment"), a commentary headline that names a deal and a valuation still get none (`tests/test_session2256_deals.py`).

### A deal's country from the words (session 2257)

A country is kept where the story's words name it, by its name or its adjective ("Indonesian assets" names Indonesia). Where the model leaves the country empty, the code reads it from the cluster's titles and summaries when one country is named just before what is traded or built ("US shale", "US power deal", "Venezuela gas infrastructure"): the United States by any of its words, read case by case so the pronoun "us" never counts; another country by its name, not its adjective, since an adjective often describes a party ("the Italian oil and gas group"); and where the United States and one other country are both named, the other, since the US words then describe the party ("US energy services firm Baker Hughes"). A country named only as a party's home ("Japan's Jera") is not taken. The words are written to the run's log. On the audit's sample, deals with a place missed went from 12 to 3 (`tests/test_session2257_deals.py`).

### A kind the rule would call "other" (session 2258)

A deal the kind rule would call "other" is read once more from its own words (asset and evidence), in this order: a lease of a data center is `compute_capacity` (a lease is a lease, whatever bonds fund the building); a credit backstop, credit support, loan, bond or guarantee is `project_finance` where the deal names its asset, else `capital`; a data center as the asset of a deal between two named parties is `compute_capacity`, unless the asset is something sold to a data center ("optical fiber for data centers", "local energy infrastructure for ... data center"); a stake bought, sold or exited is `m_and_a`. "Nuclear upgrades" are an uprate's words, and a nuclear deal whose stories name a restart or an uprate ("May Restart Abandoned US Nuclear Project") is `nuclear_restart_uprate`. On the audit's sample, kinds wrong went from 8 to 0, no other row changing (`tests/test_session2258_deals.py`).

### A stage from the deal's own words (session 2259)

Where the model gives no stage, the stage is read from the deal's evidence sentence, the first of these that its words say: cancelled ("scrap", "end plans", "drop ... plan"), rumored ("in talks", "weighs", "source says"), closed ("completes", "closes", "sold", "acquired", "raised"), financed ("financial close", "closes a loan"), signed ("signs", "agrees", "secures", "partners with", "joins", "picks", "deal with"), announced ("announces", "plans to", "will", "to buy", "to develop"); its span is the words. An empty status then takes the stage where the stage is one of the five words the Roundup prints. A stage or status the model gave, with its span in the story, is kept as it is. On the audit's sample, status missed went from 7 to 0 (`tests/test_session2259_deals.py`). Left open: a present-tense headline verb the model reads as closed ("Woodside Divests ... to Perenco"), which no word rule tells from "takes 5% stakes" or "Seals Acquisition", both read as closed by the second read.

### A party a later story names (session 2260)

When a deal is folded into a record already in the table (one record a deal), a party the later story names that the record lacks joins its `other_parties`, and the record's `parties` (buyer;seller;other_parties) is rebuilt; an empty buyer or seller is filled as before. "Microsoft, Chevron and Engine No. 1 sign exclusive deal for power supply", folded into "Chevron, Microsoft Eye Massive Texas Power Project", had kept Microsoft and Chevron only (`tests/test_session2260_deals.py`). A company acquired with no seller named stays the deal's `asset`, not its seller: `seller` is the party selling, as the Roundup prints it.

### A datacenter word that is a motive or a market (session 2270)

A deal is AI power where a named AI lab, hyperscaler or datacenter operator is a party, or where the load the deal serves is a datacenter. A datacenter word that names a motive or a market ("tied to data centre buildout", "for data center and utility markets", "amid the AI boom") is taken out of the words before the load is read, so it no longer tags the deal; a named AI party still does. On the audit's sample, AI-power tags wrong went from 2 to 0, no other row changing (`tests/test_session2270_deals.py`).

### A contract's sum that is another thing's (session 2271)

For a power purchase, an offtake, a lease or a fuel supply, a USD figure is not the deal's when the story's next words are what funds something ("Funded by $3.8 Billion of Junk Bonds") or an asset's cost that no deal word follows ("Over $7 Billion Texas Power Plant"); it is not kept, and the log says why. "$7.5 billion AI data center lease" and "$19 billion data center lease deal" are the contract's own and stay; for a debt deal or an acquisition, the sum is read as before. The cross-check reads the headline the same way, so such a row is not flagged for a figure it refused. On the audit's sample, figures of another thing went from 2 to 0, no other row's sum or flag changing (`tests/test_session2271_deals.py`).

### The provider of credit (session 2275)

In debt and project finance the investors or lenders are the buyer and the company raising the money the seller. Where a deal names no buyer and its evidence says the stored seller provides credit ("Google to serve as credit backstop for TeraWulf data center in Kentucky"; "provides ... financing", "extends a loan", "offers a guarantee"), that party becomes the buyer, and the company the credit is for ("for TeraWulf data center") the seller, taken out of the other parties. The log says so. On the audit's sample, parties wrong went from 1 to 0, no other row changing (`tests/test_session2275_deals.py`).

### A project one party leads (session 2277)

A record whose only named party leads a project, with no counterparty ("Abu Dhabi's G42 Leads $1 Billion Data Center Project in Vietnam"), is not a transaction and is not kept: leading a project is neither a sale nor an award (chain 156's ruling 2 is about those). The log says so (`tests/test_session2277_deals.py`).

### A figure stated in US dollars beside another currency (session 2285)

The model is told not to convert currencies, and leaves a deal's USD empty when its story gives the sum in euros or pounds, even where the story itself adds the US-dollar figure ("EUR 835 million (US$938 million) portfolio financing"). Where the model gives no USD and the deal's evidence states exactly one figure explicitly in US dollars (US$ or USD; never a bare $), that figure is the deal's USD, with the words as its span, unless it is a contract's funding or an asset's cost (session 2271). The log says so (`tests/test_session2285_deals.py`).
