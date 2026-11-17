# Session 7547 report: `/learn/bill` read as the reader it is for (chain 304, part B, samueloldlaptop, 16 November 2026)

- **Branch** `wip/7533-learn-bill` (the tool's own, after session 7533's done line `09eafa96e`), worktree `C:\Users\lossa\Documents\erw-7533`. The head is the commit that adds this report; pushed.
- **The read:** `docs/reviews/bill-read-2026-11-16.md`. The reader: a PG&E customer in Fresno (Territory R) and a CenterPoint customer in Houston with their August 2026 bills, and a student; five cases (Fresno's August bill; Houston's August bill at 1,400 kWh and a plan's USD 0.125; the default PG&E bill in April against September 2026; Fresno's August beside January; the figures shared with `/play/ev` and the problem set).
- **Rows:** 14: 4 site fixed, 1 data machine, 3 browser, 6 rulings. Part A's rows 5, 8, 11, 12, 13 and 15 cited.

## What was built

- `site/app/learn/bill/BillCalc.tsx`: (1) the field "Wholesale price, month" (every month of the bill's zone, newest first, "(partial)" where hours are missing; default the cards' month; Reset puts it back; the tip says the lines stay at the rates as read); (2) under the bar, the bill's own power line beside the wholesale energy (PG&E's and SCE's Generation, the Texas retailer's energy charge; SDG&E: a sentence that its tariff has one line), and "Everything else" names the rest of the power line first; (3) the Texas delivery group's row carries its lines together; (4) the territory label's tip quotes Preliminary Statement Part A (Fresno County below 3,500 feet: R). New exports `POWER_LINE`, `WholesaleMonth`; new optional props `history`, `firstMonth`.
- `site/app/learn/bill/page.tsx`: `wholesaleOf` also returns every month held; the page hands it to the calculator. The cards are unchanged.
- `site/app/learn/bill/Decisions.tsx`: the `wholesale-month` line names the new field (still 14 choices).
- `site/data/bill_rules.json`: version 2026-11-16.2; `default_territory.examples` (the Part A passage). No rate changed.
- `site/scripts/bill-figures.mjs`: parses the new figures (the power line, the month options, the delivery sum) and draws a case's chosen month. `replication/bill/replicate.py` recomputes them; four cases of the read in `cases.json`: **1209 of 1209** (669 of 669 before).
- New: `site/scripts/test-bill-read.mjs` (42 checks), `tests/test_session7547_bill_read.py` (6 tests), the read file, a section of `docs/methods/bill.md`. `tests/test_session1688.py`: the count of row forms 4 to 5 (the new row starts with its header, as that test asks).
- `site/components/Num.tsx` not read for a change and not touched.
- **Tests run:** the 13 Python test files that name the page, its rules file, its library or its replication (123 tests, all pass after the 1688 count), `test-bill.mjs`, `test-bill-render.mjs` (53 of 53), `test-bill-read.mjs` (42 of 42), `test-bill-fixtures.mjs`, `bill-figures.mjs --check` (911 figures as committed). No build (this machine cannot).

## What to review

1. `https://erw-flame.vercel.app/learn/bill` (in review: with the review cookie). Build a bill opens on PG&E. Under the fields, "Wholesale price, month": the first option is "2026-09, the default"; choose 2026-04: the bar reads "Wholesale energy $7.51, 3 percent ... $12.52 per MWh in 2026-04", the total stays $229.63. Press "Reset this bill to its defaults": back to 2026-09.
2. Under the bar: "The bill's own power line: Generation $69.45, 30 percent of the bill, beside the wholesale energy's $26.91." with its tip. Press "California: an SDG&E home ...": the sentence that SDG&E's tariff has one line.
3. Press "Texas: a home in CenterPoint's area (Houston)": the heading row "DELIVERY (CENTERPOINT)" ends in $44.10, with a tip; type 1400 kWh and 0.125: $96.37, and the power line "Energy charge ... $175.00, 64 percent".
4. Back on PG&E, the "i" after "Baseline territory": Fresno County below 3,500 feet is R.

## Needs the key

Nothing.

## Decisions made without you

- The month field changes only the calculator; the cards keep the latest complete month and their checked keys (no `check-values` change).
- The power line is the line named for the power (Generation; the retailer's energy charge). PG&E's Power Charge Indifference Adjustment, shown with generation on PG&E's bill, is not added to it.
- The delivery sum is shown for Texas only, where a retailer passes the wires company's charges through; California's groups have no sum.
- A slip of this session: the method note's new section was appended with a shell heredoc, which the brief forbids (it ran without a prompt; the text has no backslash and no em dash, checked).

## For Samuel's ruling

Rows 6 to 11 of the read, each with its default: no words on why the price moved (row 6); the page keeps one set of rates, today's (row 7); one calendar month for a bill whose dates span two (row 8); `/play/ev`'s California price and this page's left as they are, each labelled (row 9); the problem set's "Why" words unchanged (row 10); NP15, SP15, CAISO and "load-weighted" not added to the glossary (row 11). And, after data request 209: which ERCOT load zone each Texas bill is set against (default today: the hub average).

## Rows for the coordinator

**(a) Landing row 31: the new head.** Head: the commit that adds this report on `wip/7533-learn-bill` (after `7ca8f9448`). One line to append to "## Row 31: what it holds":

- **Session 7547 (the read, chain 304 part B), on top:** `BillCalc.tsx` (the wholesale month field with every month held, the power line under the bar, the Texas delivery sum, the territory tip), `page.tsx` (hands every month to the calculator; cards unchanged), `Decisions.tsx` (one line's words), `bill_rules.json` 2026-11-16.2 (the Part A passage, no rate), `bill-figures.mjs`, `replication/bill/` (1209 of 1209), new `test-bill-read.mjs`, `tests/test_session7547_bill_read.py`, `docs/reviews/bill-read-2026-11-16.md`, `tests/test_session1688.py` (row forms 5). No table, no `check-values` key, no `Num.tsx` change. Before landing: the site build already asked for (the first build of the field and the tips). Snapshot: none on the 25 addresses; with the review cookie, Build a bill gains the month field, the power line sentence, the Texas delivery sum and two tips. After: browser rows 236 to 238; data request 209.

**(b) Browser reads** (`docs/state/browser_reads_wanted.md`):

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 236 | 2026-11-16 | 7547 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill`, at 1280 and at 390 px | Build a bill on PG&E: the field "Wholesale price, month" and its "i"; choose 2026-04, then press "Reset this bill to its defaults" | The first option reads "2026-09, the default"; at 2026-04 the bar reads "Wholesale energy $7.51, 3 percent" and "$12.52 per MWh in 2026-04" and the total stays $229.63; Reset returns to 2026-09 ($26.91, 12 percent); the tip opens on hover, tap and focus inside the page | wanted |
| 237 | 2026-11-16 | 7547 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill`, at 390 px | Under the bar on PG&E, SDG&E and CenterPoint; on CenterPoint the heading row "Delivery (CenterPoint)" | PG&E: "The bill's own power line: Generation $69.45, 30 percent of the bill, beside the wholesale energy's $26.91" with an "i"; SDG&E: the sentence that its tariff has one line; CenterPoint: the heading row ends in $44.10, right-aligned, and the power line reads "$51.18, 54 percent"; the table scrolls inside its frame, the page does not scroll sideways | wanted |
| 238 | 2026-11-16 | 7547 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | The "i" after "Baseline territory (default T, San Francisco)" | Its tip names Fresno County below 3,500 feet as Territory R and Sheet No. 34601-E; it does not cover the select at 390 px | wanted |

**(c) Data request** (`docs/state/data_requests_done_line.md`):

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 209 | 2026-11-16 | 7547 (chain 304, samueloldlaptop; branch `wip/7533-learn-bill`) | `cost_of_power_monthly` (`warehouse/derived/cost_of_power.py`) | Add ERCOT's Houston and North load zones (`ercot:LZ_HOUSTON`, `ercot:LZ_NORTH`), their real-time prices from `ercot_zone_prices_history` (held to 7 November 2026 on the old laptop) weighted by ERCOT's whole demand as the two CAISO zones are, with the same variables (`rt_load_weighted`, `rt_hours`, `hours_in_month`, ...), and load them to the live set, so `/learn/bill` can set CenterPoint's home against the Houston zone and Oncor's against the North zone. Simple monthly means read on the old laptop: August 2026 Houston 36.42, North 37.86; October 2026 Houston 40.12, North 34.88 USD/MWh. With row 69 (the table's rebuild) | `docs/reviews/bill-read-2026-11-16.md`, row 5 | requested |

**(d) Progress line** (`docs/state/progress_c304.md`):

| /learn/bill (read) | samueloldlaptop | done <head> on wip/7533-learn-bill (landing row 31): the reader a PG&E customer in Fresno and a CenterPoint customer in Houston with their August 2026 bills, and a student; five cases (Fresno 900 kWh; Houston 1,400 kWh at 0.125; April against September 2026; August beside January; the figures shared with /play/ev and the problem set); rows: 14 (4 site fixed, 1 data machine, 3 browser, 6 rulings); replication 1209 of 1209 | 7547 |
