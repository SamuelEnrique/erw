# The deal tracker (`/deals`) read as its reader, 16 November 2026

Energy Research Warehouse (ERW). Session 7604, chain 305 (part C), the portable laptop, 17 November 2026. The six views (`/deals`, `?tab=tracker`, `?view=comparables`, `?view=ai`, `?view=charts`, `/deals/capital`) as built from origin/main of that morning, served here and read in a browser at 1280 and 390 px in the internal view. The tool's note is `docs/methods/deal_tracker.md`; its signature pack `docs/reviews/trackers-signature-pack-2026-11-16.md`.

## The reader and the five cases

The reader: **an AI lab's infrastructure lead, or a fund analyst, checking what power deals for datacenters were struck, by whom, how large and at what price**, against the press and the parties' own releases.

1. **The restart of NextEra's Duane Arnold plant in Iowa for Google** (announced in October 2025): is it a row, with what size, term and status?
2. **Meta's nuclear agreements of January 2026** (Vistra, TerraPower and Oklo): one deal or three, tagged AI power, by which kind?
3. **The disclosed price of power purchase agreements in ERCOT** since October 2025: the comparables' median, and on how many deals.
4. **The AI-power deals by buyer:** Microsoft's, Amazon's, Google's and Meta's counts and megawatts.
5. **Capital flows in the third quarter of 2026:** project finance and acquisitions by the kind of company that brings the money.

## What the reader got

Every view draws the hold's sentence and nothing of a row: "All 583 rows of energy_deals are held from 2026-10-21: each deal was extracted from news stories, and the outlets' own pages ask for permission, which is not yet recorded." So no case gets its answer on the page; the reader is told why, and where the method note counts which rows rest on a public source.

| Case | On the page | Without leaving it? |
|---:|---|---|
| 1, 2 | The tracker's filters (type, kind with "Nuclear restart" and "Small modular reactor", grid, counterparty, year, status) and "The selection applies once the table's hold is lifted; no count is shown while every row is held." | no (row 1) |
| 3 | "Nothing is computed from fewer than 3 deals that state a figure", then the hold | no (row 1) |
| 4 | The AI-power rule in words ("a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load the deal serves is a datacenter"), then the hold | no (row 1) |
| 5 | "No figure of them is drawn here until it is." | no (row 1) |

## The rows

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | all | Every view | Held whole since 21 October 2026 (583 rows on 17 November) | license | only a license or a recorded permission closes it; showing the rows that rest on a public source waits for a license column a row and a ruling, as the page says |
| 2 | all | The note's figures beside the page's | The note quotes 590 rows (16 November, 09:49 UTC); the page reads 583 on 17 November: the data machine folded duplicates overnight (chain 301). The note says its figures move with the table every day | none | seen; not a fault |
| 3 | 4 | `/research`, the list "the public tables of the live set" for an analysis | `energy_deals` and `deal_counterparties` are in a list called public, beside this page's hold | site | taken in the read of Automated Analysis (`docs/reviews/research-read-2026-11-16.md`), where the list is drawn |
| 4 | all | `/companies`, the filter "Has" | "Deals (license needed)": the same hold, the same words | none | seen |
| 5 | all | At 390 px | The page 390 px wide with every fold open; 13 marks, each box inside the screen | none | seen |

## Two pages that share a figure

- The count of deal rows held: 583 on every view of `/deals` and on `/deals/capital`, the same.

## Needs the key

- Nothing. (The re-extraction of the 529 rows extracted before the stricter list of 6 November stays under "Needs the key" in chain 303's note; it is not this read's.)
