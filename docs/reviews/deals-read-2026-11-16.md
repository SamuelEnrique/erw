# The deal tracker (`/deals`) read as the reader it is for (session 7561, samueloldlaptop, 16 November 2026 Pacific, 17 November UTC)

Energy Research Warehouse (ERW). Asked by Samuel: the reader's read of chain 304's part B for the six tools of the first ten that had none. The tool reached the done line in chain 303 (`docs/reviews/trackers-signature-pack-2026-11-16.md`, section 2; faults `docs/reviews/deals-faults-2026-11-11.md`, 28 rows).

**The reader:** a fund analyst at an infrastructure fund checking a firm-power contract against its comparables: who bought, how many MW, for how long, at what price, and which deals of the same kind stand beside it.
**The five cases:** (1) Google and Constellation Energy's nuclear PPA, signed 6 October 2026 (3,600 MW stated, USD 4.3 billion, 20 years); (2) a nuclear PPA at USD 85 per MWh in PJM, placed against the disclosed prices on the comparables view; (3) the 2025 comparables the analyst already knows: Constellation and Meta at Clinton and Talen and Amazon at Susquehanna (both June 2025); (4) every deal of 2026 with Amazon, Google or Microsoft as a party, from the AI-power view; (5) Fermi's 600 MW PPA of 13 November 2026 and its Project Matador campus beside the datacenter tracker. On the table as the live set served it at 05:37 UTC on 17 November 2026 (590 rows; 585 deals once the five folded pairs are one).
**How it was read:** the rows fetched with the replication's reader (`replication/deals/fetch_rows.py`, anon key, nothing committed: the table is held); the cases in `runs/7561_deal_cases.py` (not in git); the opening line and the placing form drawn to HTML by the site's own code (`site/scripts/test-deals-read.mjs`, 7 of 7). Not seen: no click, no hover in a browser, no layout at 390 px.
**What a visitor sees today:** `energy_deals` is held whole since 21 October 2026 (part A's row 1, default: held whole), so a visitor meets the hold and no deal. This read is of the page as it draws the rows.

## The cases, in one line each

| Case | What the page gives | Where it stops |
|---|---|---|
| 1. Google and Constellation | One row: PPA, signed, 3,600 MW, USD 4.3 billion, 20 years, nuclear, 11 stories linked | Tagged "AI no", so it is in no AI-power sum or view (row 1); no price per MWh; no state, so no grid |
| 2. USD 85 per MWh in PJM | The comparables view says 0 of the 585 deals state a price per MWh; the placing form still asks for a technology, a grid and a price, and answers only after the typing that there is nothing to place against | No PPA or offtake held states a price (row 4 fixed the order; row 5, the price itself) |
| 3. The 2025 comparables | Neither Clinton nor Susquehanna is a row. The opening line said "since 2025-10-01" while 42 rows are dated earlier, from January to May 2025 | The stories of June to September 2025 are held and not scored (the chart's note says so), so June 2025's deals are not in the table (row 3, needs the key); the line now says the rows' own span (row 2) |
| 4. Hyperscaler deals, AI view | 23 of Google's 27 deals tagged AI, 14 of Amazon's 18, 12 of Microsoft's 14 | The 14 rows with a named AI party tagged "AI no" include the two largest hyperscaler PPAs of the autumn (row 1) |
| 5. Fermi | "Fermi", PPA, signed, 600 MW, no counterparty; "Fermi; AMD", other, 222 MW, Project Matador campus, Texas | The 222 MW agrees with the datacenter tracker's Project Matador row; a PPA with one party named is shown as the story gives it |

## The rows

Kind: `site` (fixed on this branch, with a test: `site/scripts/test-deals-read.mjs`), `data machine` (a row of `docs/state/data_requests_done_line.md`), `browser` (a row of `docs/state/browser_reads_wanted.md`), `ruling`, `key` (needs the model), `license`.

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 1, 4 | The AI column and the AI-power view (`/deals?view=ai`) | 14 deals with a named AI party read "AI no": Google and Constellation (3,600 MW, 6 October 2026), Amazon and Constellation (folded with the Calvert Cliffs PPA), Amazon, AEP and X-energy (960 MW, 19 October 2026), Google and Anthropic, Microsoft and EDP Renewables, among them. Cause: the 529 rows extracted before 6 November were upgraded with "ai_power left as extracted" (`warehouse/deals/fields.py`, `upgrade`), so they carry the model's tag, not the rule's (`ai_of`); the rule's party test needs no story and no model. One row reads "False" with a capital | data machine | requested (row 305): apply `ai_of`'s party test to the upgraded rows' buyer, seller and other parties, and write the tag in one case |
| 2 | 3 | The opening line: "Energy deals reported in the news since 2025-10-01" | 42 of the 590 rows are dated before it (5 January to May 2025, each by its first story); the analyst finds a February 2025 deal under a line that says there are none | site | fixed: the line is written from the rows' own dates, "each dated by its first story, from 5 January 2025 to 13 November 2026; most are dated 1 October 2025 or later" |
| 3 | 3 | The 2025 comparables | Constellation and Meta (Clinton, June 2025) and Talen and Amazon (Susquehanna, June 2025) are not rows: the stories of June to September 2025 are held and were never scored, so no deal is extracted from them | key | the stories of June to September 2025 scored and the deals step run on them. Not run (model spend USD 0). Cost: USD 0.00365 a story (the deals step's median, `run_status.csv`) times the stories of those months, which the data machine's dry run would count |
| 4 | 2 | "Your deal against them" on the comparables view | With no priced deal the form asked for a price, then said there was nothing to place it against | site | fixed: before any typing it says no PPA or offtake held states a price in US dollars per MWh, so a price typed has nothing to be placed against |
| 5 | 1, 2 | Every PPA's price | 0 of the 68 PPAs and offtakes state a price per MWh: the stories almost never print one. The analyst's first question has no answer here | license | a price is in paid sources (broker and platform indices) or in a filing; no license is held and none is sought here |
| 6 | 1 | The USD 4.3 billion on Google and Constellation's row | The figure is the stories' own; whether it is the contract's value, an investment or a sum over 20 years the column does not say | ruling | default: the column keeps "USD" as the words state it, with its stories linked. The other choice: a field for what a dollar figure measures, read from the words (the second reading, needs the key) |
| 7 | 4 | The views' place filters | 478 of 590 rows state no country; Belgian, Turkish, South African and Australian deals stand among the US ones, and no filter keeps the US alone (part A's row 13 found the Where column nine rows in ten "not stated") | ruling | default: every row shown, the place as the story states it. The other choice: a country filter, with "not stated" as its own choice |
| 8 | 5 | Fermi's 600 MW PPA | One party named; the buyer is not stated | ruling | default: shown as the story gives it, "parties not stated" where it is so. No other choice without the story's words |
| 9 | 2 | `/deals?view=comparables#prices`, "Your deal against them" | The new line before any typing | browser | wanted (row 303) |
| 10 | 3 | `/deals`, the opening line at 390 px | The span in words, no sideways scroll | browser | wanted (row 304) |

**Counts.** Site, fixed: 2 (rows 2, 4). Data machine: 1 (row 1). Key: 1 (row 3). License: 1 (row 5). Ruling: 3 (rows 6 to 8). Browser: 2 (rows 9, 10).

**Words the reader would not know.** "Sure" (the extraction's confidence) is part A's row 16; "folded" on a merged pair has its reason on hover.

## The figures this page shares with other pages

| Figure | Here | The other page | Agree? |
|---|---|---|---|
| Project Matador, Amarillo, Texas | 222 MW, "Fermi; AMD", 14 October 2026 | `/datacenters`: Project Matador, Amarillo, 222 MW, ERCOT (session 7560) | Yes, the same figure from two tables |
| Hyperscaler deals | AI view: the rows tagged AI | `/companies`' rows for Google, Amazon and Microsoft (read in session 7562) | Not compared here |

## What this reader still cannot get from the tool, and why

- **A price.** No story of the 68 PPAs and offtakes states one (row 5).
- **June to September 2025.** Held and not scored (row 3).
- **The AI sum, whole.** Until row 1's tag is applied, the AI view misses at least 14 deals with a named AI party.
- **Where a deal is.** Nine rows in ten state no place (part A's row 13).
