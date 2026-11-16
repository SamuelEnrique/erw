# The two trackers: a signature pack for Samuel (16 November 2026)

Energy Research Warehouse (ERW). Written by session 7407 of chain 303 (`queue/done/303-night-16-november-portable-trackers-done-line.md`), the portable laptop, for one sitting: read, run and sign both. It is in the form of the five tools' pack (`docs/reviews/five-tools-signature-pack-2026-11-14.md`). The done line asks each tool for a method note you sign, a replication a reader can run, a cross-check against published figures, and a decisions block. All four are built for the datacenter tracker (`/datacenters`) and the deal tracker (`/deals`); this pack is what you need to give the two signatures, or to say why not.

- **What a signature is.** You fill the three lines of the note's "Sign-off" block (`Signed off by`, `Date`, `Items ... ruled, and how`) and commit it, or say it in a prompt and a session writes your words there. A session never signs.
- **What you sign accepts** the rules the block lists, at the defaults of the decisions. It does not freeze the figures: they move with the tables every day.
- **Both tables are held** ("license needed" since 21 October 2026), so neither page draws a facility or a deal to anyone. "The page's figure" below is what the page's own functions compute on the live set's rows, which is what it draws when the hold allows. Signing the notes does not lift a hold.
- **The expected values below** are of the live set's rows as read on 16 November 2026: 458 rows of `datacenter_facilities` at 09:18 UTC, 590 rows of `energy_deals` at 09:49 UTC. The tables move daily, so after a new fetch compare Stata's lines with the mirror's (`python replicate.py --headline`), not with this page.
- **Before you run Stata.** A checkout that holds `wip/7400-trackers` (main, once landing row 33 has landed). Each do-file reads CSVs that `fetch_rows.py` writes from the live set into the folder's `rows/` (not in git), with `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the environment or in `.env`. Each do-file is run from its own folder and needs no package. Keep a log of each, so a session can set your printed lines beside the mirror's.
- **Order of the sitting.** The datacenter tracker, then the deal tracker, then the rulings at the end. About forty minutes.

---

## 1. The datacenter power tracker (`/datacenters`)

**You sign:** `docs/methods/datacenter_tracker.md`, section "Sign-off". It accepts what a facility is and when two rows are one (section 2); what a sum counts (section 3); megawatts only as stated, a sum of every basis, one number where the words give a range (section 4); a status only where a source states it (section 5); the grid of a facility (section 6); ERCOT's large loads as its reports state them in words (section 8); the twelve decisions of section 12, the list the page shows at its foot. It leaves open the five items of its section 13.

**The five choices that matter most** (`site/lib/decisions.ts`, `DATACENTER_TRACKER_DECISIONS`; on the page, each with its default and source on hover):

| Choice | Default | Source |
|---|---|---|
| What a sum counts | A facility in a named US state (the 50 states, the District of Columbia, Puerto Rico) whose status is not withdrawn; 274 of the 458 | No source the ERW reads records a country, so the state is the only test (session 166) |
| Megawatts | Only what a source states in words; a facility that states none is counted beside the sum, never as zero, never estimated; 21 of the 274 state it | Session 16's ruling: nothing inferred beyond the stated words |
| The basis of a megawatt | One sum of every basis (IT load, total, a tenant's share, a phase, unstated); 54 of the 58 stated sizes have no basis stated | The basis is read from the story's own words (session 2236); no public rule converts one basis to another |
| Status | Kept only where a source states it; most operators' listed sites carry none, so megawatts by status are not a measure of what is running (301 of 458 rows have no status) | Session 17's ruling: a status without its words is left empty |
| The grid of a facility | The grid a story names, else its queue position's, else the grid that serves most of its state; a split state has none (175 by state, 3 by queue, none named) | A reading of the state, with its basis shown a row (sessions 2236 and 2243) |

**Cross-checks** (`docs/methods/crosschecks/datacenter_tracker.md`, ten rows; no figure adjusted):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| 75 MW stated by facilities marked operating | 176 TWh used by US datacenters in 2023, a mean draw of 20,091 MW | Berkeley Lab, *2024 United States Data Center Energy Usage Report*, 19 December 2024 | -20,016 MW | the operators' listed sites are running and state neither a status nor a size |
| 28,254 MW stated, every counted facility | 74,000 to 132,000 MW of datacenter demand in 2028 | the same report | -45,746 to -103,746 MW | theirs is the whole fleet; ours is what the news stated for named facilities since January 2025 |
| Texas: 47 sites, 457 MW stated by 4 | 8,927 MW approved to energize, 3,900 MW observed, 19 June 2026 | ERCOT, Large Load Interconnection Status Update | -8,470 and -3,443 MW | ERCOT counts every approved load of 75 MW or more and names none; 43 of our 47 Texas sites state no size |
| PJM: 11,618 MW stated by 3 of 60 facilities | 65,733 MW of summer peak growth in ten years | PJM, *2026 Load Forecast Report*, 14 January 2026 | 17.7 percent of theirs | a forecast of peak from every cause, against three stated sizes |
| Virginia: 33 facilities, none stating MW | about 54,000 MW under contract; a datacenter billing peak of 4,800 MW in August 2026 | Dominion Energy, presentation to PJM's Load Analysis Subcommittee, 29 September 2026 | -4,800 MW | the largest market in the world is 33 rows without a megawatt in the tracker |
| 28,254 MW stated, the whole country | 84,000 MW of incremental contracted load by 2031 | American Electric Power, third-quarter release, 28 October 2026 | -55,746 MW | one utility's contracts are three times every megawatt our news stated |

The other four rows (EIA's outlook as a scale check, Berkeley Lab's implied growth, ERCOT's preliminary forecast of 367,790 MW and its 140,000 MW of submissions) are in the file. What the table says: **the tracker is a list of named sites, not a measure of megawatts**, and its note, its decisions and its cross-check now say so.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\datacenter_tracker"
log using "datacenter_tracker_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/datacenter_tracker/fetch_rows.py` from the repository's root.)

**Expected**, on the rows of 16 November 09:18 UTC:

- 1. facilities held: 458
- 2. counted in the sums (a named US state, not cancelled): 274
- 3. megawatts stated by the counted facilities: 28,254
- 4. counted facilities that state megawatts: 21
- 5. ERCOT, megawatts approved to energize, newest report (2026-06-19): 8,927

The whole replication (`python replication/datacenter_tracker/replicate.py`): **454 of 454 inside the tolerance**, every keyed figure of both views against the page's own functions.

---

## 2. The deal tracker (`/deals`)

**You sign:** `docs/methods/deal_tracker.md`, section "Sign-off". It accepts what a deal is and is not, with the stricter list reaching only the rows extracted since 6 November until the older rows are read again (section 2); one deal, one row (section 3); megawatts, US dollars and a price only as the story's words state them (section 4); the AI-power tag as a tag of the parties and the load, not of the asset (section 5); a median only from three deals that state the figure (section 7.3); "Sure" as the extraction's own confidence, with no floor (section 7.1); the thirteen decisions of section 11. It leaves open the six items of its section 12 and the second reading of its section 10.

**The five choices that matter most** (`site/lib/decisions.ts`, `DEAL_TRACKER_DECISIONS`):

| Choice | Default | Source |
|---|---|---|
| What a deal is | A named transaction between named parties that a scored story reports; a plan, a pledge, a seeking, a permission are not deals. The stricter list has reached 61 of the 590 rows | The extraction's prompt and the audit of 6 November 2026 |
| A figure | Megawatts, US dollars, a price and a term only where the story's words state them and parse to the same number; else "not stated". 39 of 585 deals state megawatts, none a price per MWh | Session 16's ruling |
| One deal, one row | The extraction, then the code (the same type and parties within 30 days), then the register; a folded pair is counted once as the row kept, which stands as extracted | `warehouse/deals/dedupe.py`; `warehouse/deals/duplicates.csv`, each pair with its reason |
| The AI-power tag | A named AI lab, hyperscaler or datacenter operator is a party, or the load is a datacenter. It does not say the asset is power: 104 of the 217 tagged deals are capital deals | `warehouse/deals/fields.py`, `ai_of` |
| A median | Only where three or more deals of a group state the figure; today no group has three prices, and fourteen have a median size | `site/lib/deals2.ts`, `medianOf` (session 466) |

**Cross-checks** (`docs/methods/crosschecks/deal_tracker.md`; no figure adjusted):

| Our figure | Published figure | Source | Gap | Why |
|---|---|---|---|---|
| Power purchases dated 2025: 3, none stating MW | 27,300 MW contracted by US companies in 2025 | CEBA, press release of 17 March 2026 | -27,300 MW | the tracker reads only the scored news, in earnest from October 2025, and keeps megawatts only where a headline states them |
| The same | 29,500 MW in the United States, 55,900 MW worldwide | BloombergNEF, release of 19 February 2026 | -29,500 MW | the same; the two publishers differ from each other by 2,200 MW |
| Power purchases dated 2026: 36, 14 stating 11,990.5 MW | no full-year tally yet; about 2,300 to 2,500 MW a month at 2025's pace | the same two | not a gap | ours is of every country and of the 14 that state a size |
| Deals naming Meta, Amazon, Google or Microsoft: 72, 7 stating 7,198 MW | Meta and Amazon contracted 20,400 MW in 2025 | BloombergNEF, the same | -20,400 MW for 2025 | most of our 72 are funding rounds, compute contracts and acquisitions |
| Deals stating a price per MWh: 0 of 585 | offered prices rose in the first quarter of 2026 (percent only on the public page) | LevelTen Energy, 14 April 2026 | none to set beside | the news almost never states a price |
| The twenty largest AI-power rows | each row's own story | this machine's copy of the stories | 17 of 20 figures are in a headline; 3 not checkable here | three rows of 11 and 13 November: their stories are not on this machine |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\deals"
log using "deals_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/deals/fetch_rows.py` from the repository's root.)

**Expected**, on the rows of 16 November 09:49 UTC:

- 1. deals held, the register's folded pairs counted once: 585
- 2. deals that state a size in MW: 39
- 3. megawatts stated by them: 43,119
- 4. deals that state a value in US dollars: 298
- 5. deals tagged AI power: 217
- 6. deals that state a price in US dollars per MWh: 0
- then a table by year and kind; for the power purchases (kind `ppa`): 2025, 3 deals, none stating MW; 2026, 29 deals, 10 stating 9,911.5 MW

The whole replication (`python replication/deals/replicate.py`): **1,123 of 1,124 inside the tolerance; the one difference is named**: the capital view's file says 529 rows, the count of 6 November, and the table holds 590.

---

## 3. What waits for your ruling, with the default each stands on

The work is built on the defaults; none of these stops a signature.

**The datacenter tracker** (`docs/reviews/datacenter-faults-2026-11-11.md`):

1. Do the facilities stay held whole? Default: held whole.
2. Do each grid's peak hour and capacity (EIA's public data) show while the facilities are held? Default: hidden, with the hold's footnote.
3. May the map draw the facilities the tracker holds? Default: the map unchanged. One of the two is wrong until this is ruled.
4. Does every figure on the site show its source on hover? Default: unchanged (the change reaches every page).
5. New: do the views by operator read the developer where no operator is named? "Operator not stated" holds 26,124 of the 28,254 MW stated. Default: the operator alone.

**The deal tracker** (`docs/reviews/deals-faults-2026-11-11.md`):

6. Do the deals stay held whole? Default: held whole.
7. Does the table open at a floor of "Sure"? Default: no floor.
8. Does the grey explanatory text become hover tips, on every tool? Default: unchanged.
9. New: do the tracker's three views read a grid a story names, as the table's own column does? Default: the state alone.
10. New: does a folded pair carry over a figure only the folded row states? 433 MW of one loan is in no sum. Default: no.
11. New: is "a deal is energy's where its asset is energy" written into the extraction's prompt? It is written nowhere today. Default: not written.

**Both:**

12. The repository is public and tracks the held tables' own files (`warehouse/output/energy_deals.csv`, `datacenter_facilities.csv`, the two evidence tables and three more). Default: nothing changed.
13. PJM's two figures in the datacenter cross-check (its load report, and Dominion's presentation on its committee page), against PJM's data license. Default: kept, as facts with links.

## 4. What needs the key (nothing was run; the key is at its limit until 1 December)

| What | What it would do | Estimated cost |
|---|---|---|
| A second reading of the 529 deals extracted before 6 November | Takes out about 22 plans, pledges and seekings; changes about 4 kinds; settles about 19 a title cannot; fills the stage and the place. It takes out the about 51 rows that are not energy's only if ruling 11 writes the rule first | USD 3.0 for the 814 stories behind those rows; USD 10.6 for every story the extraction has checked (2,899) |
| A second reading of four datacenter rows (faults rows 18 to 21) | Corrects a tenant named as operator (1,000 MW), a fuel-cell plant's 702 MW, a turbine project's 1,200 MW, and the Utah join (9,400 MW) | under USD 1 for their stories; USD 2.9 for every story the datacenter extraction has checked (1,077) |
| **Sum** | | **about USD 4 for the two narrow readings; about USD 13.5 for both tables whole** |

Each cost is the step's median cost a story in `warehouse/metadata/run_status.csv` (USD 0.00365 for deals, USD 0.00273 for datacenters) times the stories; the data machine's own dry run would price it from the ledger.
