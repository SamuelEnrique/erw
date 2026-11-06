# Session 1441 report: the chart of the day

Energy Research Warehouse (ERW), session 1441 (chain 149's "1438"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 01:53 to 01:56 UTC. Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1441-periodicals` over `wip/1440-periodicals`.

## What it did, with commits

- **`43bf867a6`**, `warehouse/analysis/findings/daily_chart.py` (faults 14, 15):
  - `readable(c)`: a candidate whose series name (its fact's text before the first ": ") holds an id (a colon, an underscore, a code of six capitals or digits; a node's code in parentheses is not the name) is never the chart of the day, whatever its relevance or strength. The two charts a reader could not read, 23 October's "eia_padd_movements:MGAMT1XP31 tanker_barge_receipts" and 26 October's "onrr_revenue:federal:onshore:22081_red_river:...", and the ids whose tokens ("oil_gas") the relevance rule matched to the day's oil stories, are gone.
  - `degenerate(c)`: a flag past `STRENGTH_CAP` (50 robust standard deviations) is a step from zero, not a finding (the Red River line item: 552).
  - `choose` passes both over before the floor and the dismissed drafts, and its note counts them ("2 candidate(s) whose series has no plain name passed over"); with nothing left it says so and the issue's small table stands in (`brief.no_chart_lines`, session 2703).
  - `plain_name` gives `storage_buildout_monthly`'s series a name ("PJM battery operating MW net added over 12 months"), so the scanner's next flags on it are readable; the 7 October chart was that series' id.
  - Tests: `Session1441ChartOfTheDay` (the two ids and the step from zero passed over; a readable step from zero too; the stored records the rule refuses); `test_session805`'s PJM fixture carries the plain name.
- The faults file: rows 14, 15 fixed; row 41 added (the chart on the page is a PNG; the owner's rule that nothing reads as an image wants a hover with values: session 1449, the pages).

## The 13 stored charts under the rule (`docs/digest/charts/*.json`, and the two dry runs)

| Issue | Chart | Under the rule |
|---|---|---|
| 6, 13 Oct | Net generation from natural gas in Wyoming (9.9) | stands |
| 7 Oct | iso:pjm battery_operating_mw_net_added_12m (2.6) | refused: an id (now named) |
| 8, 14 Oct | Retail electricity price in the District of Columbia, industrial (1.8) | stands |
| 9, 20 Oct | Retail electricity sales in Utah, residential (1.0) | stands (under item 6's floor of 1.5 since 2701) |
| 12, 21 Oct | Retail electricity price in Iowa, industrial (0.8) | stands (under the floor since 2701) |
| 22 Oct | eia861m:4911:NE industrial_sales (4.1) | refused: an id |
| 23 Oct | eia_padd_movements:MGAMT1XP31 tanker_barge_receipts (8.6) | refused: an id |
| 26 Oct (dry run), 6 Nov (the 00:48 UTC issue) | onrr_revenue:federal:onshore:22081_red_river:... (552.5) | refused: an id and a step from zero |

Five of thirteen refused. What stands is the EIA state series the scanner names in words; what the day's stories point to (a price of the commodity named, a demand or flow of the region) is a matter of which tables the scanner scans, the data machine's (item 17 and the chain's fault 35 for the Roundup).

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_periodicals`, `test_session805`, `232`, `267` | 0 | 143 passed |
| the classification script over the records | 0 | the table above |

## Decisions made without you

- Readability is the rule, not a table deny-list: a series the scanner cannot name in words is not shown, whichever table it is from; the fix for a table is a `plain_name` case (done for the storage series).
- The cap is 50 robust standard deviations: the stored flags that stand are under 10; the degenerate one is 552.
- The caption of a refused series is not rewritten (it is never shown); the relevance rule's token matching stays, since with ids out its words are the plain names'.

## For Samuel's ruling

- None new. Item 17 (the related measure's chart rendered on the data machine) stands.
