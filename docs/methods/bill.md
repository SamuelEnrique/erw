# What is on an electricity bill

The learning page `/learn/bill`. Written by session 335 (20 October 2026) from the page's code (`site/app/learn/bill/`,
`site/lib/bill.ts`) and its rules file; until then the page's citations were its only note.

## The five bills

Five homes on five published tariffs: a PG&E home on time-of-use rate E-TOU-C, an SCE home on TOU-D-4-9PM and an
SDG&E home on TOU-DR1 in California; a home in Oncor's area and one in CenterPoint's area (Houston) of ERCOT. Every
rate, credit and fixed charge is in the site's own file, `site/data/bill_rules.json`, each with the tariff passage it
is read from (the schedule and its sheet), and each line of a bill opens to say what the charge is, why it exists and
that passage. A bill's defaults (its monthly use, its territory, its season) are in the same file, each with its own
words (every default home uses 600 kWh a month, an assumption the file says is one).

## The numbers

- **A default bill** is computed on the server from the file (`defaultBill` in `site/lib/bill.ts`), and every figure of
  it is a checked number: `check-values` computes it again from the same file (`bill|...` keys).
- **The wholesale share**: the load-weighted real-time price of the latest complete month in `cost_of_power_monthly`
  (the ERW's cost of power, `cost_of_power.md`), else the latest month held, said to be partial; the share is what that
  price, times the bill's kilowatt-hours, makes of the bill's total.
- **Build a bill**: the same rules in the reader's browser, with the reader's use and choices; "Reset this bill to its
  defaults" puts every input back to the file's.
- The words of the glossary and of each line are written for this site with their sources named, marked "written,
  cited" (not data).

## Downloads

At the foot of the page, `cost_of_power_monthly` as the live set's CSV with a Python and a Stata reader of that CSV
(session 328's shared line). The rates are the site's own file, not a table of the warehouse.

## The figures on the page and their keys

Each number `/learn/bill` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `cost_of_power_monthly`, `rt_load_weighted`: the wholesale price each default bill is set against, USD/MWh, the load-weighted real-time price of the bill's zone (`wholesale_entity` in `site/data/bill_rules.json`) in the latest complete month (one whose `rt_hours` equal its `hours_in_month`), else the latest month held, marked "a partial month". It stands beside the bill's wholesale energy in USD and its share of the bill.

## The tool as a reader meets it (session 7533, chain 304, 16 November 2026)

Session 7533 took the page to the done line: this note completed (the sections above are kept as written), a
replication written from it and from the rules file alone (`replication/bill/`), a cross-check against EIA's published
figures and the tariffs as posted on 16 November 2026, a decisions fold on the page, and a faults file
(`docs/reviews/bill-faults-2026-11-16.md`). The page reads one ERW table, `cost_of_power_monthly` (its own note:
`cost_of_power.md`); everything else on it is tariff arithmetic on `site/data/bill_rules.json`.

### The views

1. **The five cards** ("The default bills (600 kWh a month, an assumption)"): for each bill its name, its total in USD
   for its kWh, and, when the bill's wholesale price is held, the wholesale energy in USD, its share of the bill in
   percent and the price in USD/MWh with its month (", a partial month" when it is not complete); under them the bill's
   default words (season, shares, territory or region, tier, days, or the Texas energy charge). Each number is a checked
   number (`bill|<bill>|total`, `bill|<bill>|wholesale|<ts>`, `bill|<bill>|share|<ts>`, and the price's
   `series|cost_of_power_monthly|<entity>|rt_load_weighted|<ts>`).
2. **Build a bill**: five buttons, one a bill; the bill's note; its fields (below); "Reset this bill to its defaults";
   the bill line by line in groups (each line's name opens its words: what it is, why, the kWh and rates it is made of,
   its effective date and the tariff passage, linked); the total; "Per kWh, all in"; a bar and its sentence: the
   wholesale energy in USD and its share in whole percent, the kWh, the price and its month, and "Everything else" in
   USD.
3. **Ten terms**: written for the site, each with its source named, no number but "4 to 9 p.m.".
4. **Decisions on this page** (session 7533): a fold, closed to start, 14 lines, each with its default and source on
   hover or focus (`site/app/learn/bill/Decisions.tsx`).
5. **Downloads**: `cost_of_power_monthly` as CSV with its readers.

### The fields of Build a bill

| Bill | Fields (default) |
|---|---|
| PG&E (`CA`) | kWh (600); share of use from 4 to 9 p.m. (20 percent); season (winter); baseline territory (T, San Francisco); income tier (3); the climate credit box (off) |
| SCE (`SCE`) | kWh (600); share from 4 to 9 p.m. (20 percent); share in super off-peak hours (33.33 percent); season (winter); baseline region (9); the climate credit box (off) |
| SDG&E (`SDGE`) | kWh (600); share from 4 to 9 p.m. (20 percent); share in super off-peak hours (34.52 percent); season (winter); the reader's baseline allowance (0 kWh) |
| Oncor (`TX`), CenterPoint (`TXC`) | kWh (600); the plan's energy charge (USD 0.0907 and 0.0853 per kWh) |

The days (30) and SCE's share of weekdays (5 of 7) are not fields. The two shares of a time-of-use bill hold at most 100
percent together: the one just typed is held to what the other leaves, and a line under the fields says so (Samuel's
ruling 10b of 14 October 2026). Since session 7533 the SCE share in super off-peak hours carries a line in summer: SCE's
summer has none, so the share moves nothing until the season is winter.

### The arithmetic, line by line

- **PG&E (E-TOU-C).** Each unbundled component of Sheet 3 is a line. A time-of-use component is kWh x (peak share x
  its peak rate + (1 - peak share) x its off-peak rate), the season's (Sheet 1's pro-rating: the peak share applies to
  all use, inside the baseline and above it). The baseline is the territory's daily quantity (Sheet 5, Code B, basic)
  for the season times the days, never more than the use. The Conservation Incentive Adjustment is the baseline kWh at
  its baseline rate (a credit) plus the kWh above at its over-baseline rate. Every other component is kWh x its rate.
  Then the Base Services Charge: the days x the income tier's rate a day; then the climate credit, once, when chosen.
  The lines add up to the same bill by Sheet 2's total rates: kWh x the TOU totals, plus the baseline kWh x the baseline
  credit, plus the daily charge (the replication checks this for every PG&E case).
- **SCE (TOU-D-4-9PM) and SDG&E (TOU-DR1).** Each period's share of the month: SCE in summer, the share of 4 to 9 p.m.
  times the share of weekdays on-peak and times the share of weekend days mid-peak, the rest off-peak; SCE in winter,
  4 to 9 p.m. mid-peak, the super off-peak share, the rest off-peak; SDG&E, 4 to 9 p.m. on-peak, the super off-peak
  share, the rest off-peak. A per-period component is the sum over periods of kWh x share x the period's rate (SCE's
  delivery and generation lines; SDG&E's one total line); SCE's Fixed Recovery Charge is kWh x its rate. The baseline
  credit: SCE's region's daily quantity (Preliminary Statement Part H) for the season times the days, no more than the
  use; SDG&E's 130 percent of the reader's allowance, no more than the use; times the credit rate. Then the Base
  Services Charge, days x the rate a day, and SCE's climate credit when chosen.
- **Oncor and CenterPoint.** kWh x the plan's energy charge; each fixed monthly charge; kWh x each per-kWh charge and
  rider.
- **The total** is the sum of the lines; **per kWh, all in** is the total over the kWh (blank at 0 kWh).
- **In a line's words**, a computed kWh is printed to a tenth (since session 7533: in floating point 16.9 x 30 is
  506.99999999999994, and SCE's Region 9 in summer printed that); a rate as the tariff prints it, a credit as
  "-$0.08140".
- **The wholesale share.** The price is the bill's `wholesale_entity` in `cost_of_power_monthly`, variable
  `rt_load_weighted`, in the latest month whose `rt_hours` equal its `hours_in_month`, else the latest month held,
  marked partial. The wholesale energy is kWh x price / 1000. On a card the share is that over the default bill's total,
  times 100, printed to two decimals; on the bar it is held between 0 and 100 percent and printed as a whole percent;
  "Everything else" is the total less the wholesale energy.

### The choices that move a figure

The fold's 14 lines, by their keys in `Decisions.tsx`: `kwh` (600 kWh), `peak-share` (20 percent), `super-share` (SCE
33.33, SDG&E 34.52 percent), `weekdays` (5 of 7), `season` (winter), `baseline` (PG&E T, SCE 9, SDG&E 0 kWh),
`income-tier` (3), `days` (30), `climate-credit` (off), `texas-energy` (USD 0.0907 and 0.0853 per kWh), `wholesale-zone`
(NP15; SP15; ERCOT's hub average), `wholesale-month` (the latest complete month), `wholesale-energy` (metered kWh times
the price, no losses) and `left-out` (taxes, local fees, SCE's Modified Cost Allocation Mechanism charge, SCE's Regions
15 and 16). Each line says where to change it on the page, or that it is not a field. The default and source of each are
in the fold's tips; the Texas default's arithmetic is in the rules file (`energy_default.arithmetic`) and printed by
`replicate.py --texas-default`.

### The cross-check (16 November 2026)

Robots files and terms read first: `www.eia.gov` (robots allows the pages read; EIA's publications are public domain,
an acknowledgment with the date asked), `www.pge.com` (robots disallows only its mobile folders),
`assets.centerpointenergy.com` (robots allows `/api/public/`, where the tariff is). Not read: `www.oncor.com` (its robots
file did not answer in 60 seconds, so no request was made to its tariff), SCE's and SDG&E's tariff hosts (not tried this
session). No figure of the page was adjusted.

| Figure | Ours | Theirs (publisher, document, date) | Difference | Why |
|---|---|---|---|---|
| PG&E default bill, all in | 38.27 cents/kWh (229.63 USD, 600 kWh, winter) | 39.62: EIA, Electric Sales, Revenue, and Average Price 2024, Table 6, PG&E bundled residential (released October 2025) | -1.35 | Ours is one winter month on today's rates; EIA's is 2024's revenue over sales, all seasons, CARE households included |
| SCE default bill, all in | 37.46 | 32.43: the same table, SCE | +5.03 | The same: one winter month on the rates of June 2026 against 2024 revenue over sales; its average home used 506 kWh, not 600 |
| SDG&E default bill, all in | 55.48 | 43.63: the same table, SDG&E | +11.85 | Mostly the baseline credit: the default allowance is 0 (SDG&E's allowances were not read), so the default bill carries no credit; a 240 kWh credit alone is USD 25.68 (4.28 cents at 600 kWh) |
| California default bills, all in | 37.46 to 55.48 | 29.75: EIA, Electric Power Monthly, Table 5.6.A, California residential, August 2026 (released October 23, 2026) | +7.71 to +25.73 | EIA's state average includes the municipal utilities (Los Angeles, Sacramento) and the CARE and FERA households |
| PG&E bill at EIA's 2024 California average month, 503 kWh | 193.39 USD | 160.86: EIA, ESRAP 2024, Table 5A, California average monthly residential bill | +32.53 | The same reasons; at PG&E's own 2024 price (39.62 cents) 503 kWh is USD 199.29 |
| Oncor and CenterPoint default bills, all in | 15.88 cents/kWh | 15.91: EIA EPM Table 5.6.A, Texas residential, August 2026 | -0.03 | By construction: the default energy charges are set so the 600 kWh bill equals EIA's July 2026 Texas average (158.8 USD/MWh); August's is 159.1 |
| Oncor bill at EIA's 2024 Texas average month, 1,096 kWh | 170.68 USD | 163.72: EIA, ESRAP 2024, Table 5A, Texas average monthly residential bill | +6.96 | Today's rates against 2024's; EIA's 2024 Texas price was 14.94 cents |
| EIA's figures in the ERW table | California 297.5, Texas 159.1 USD/MWh, August 2026 (`eia_retail_electricity_prices`) | 29.75 and 15.91 cents/kWh (EPM Table 5.6.A) | 0 | The table is EIA's own series |
| PG&E E-TOU-C as posted | the rules file's Sheet 2 totals, baseline credit, Base Services Charge and climate credit | the tariff as posted on 16 November 2026: Sheet 2 Advice 7921-E effective June 1, 2026, the same figures; Sheets 1, 3 to 5 Advice 7846-E effective March 1, 2026 | 0 | Unchanged since the read of 30 September |
| CenterPoint tariff as posted | TC5 Refund -0.000278 USD/kWh (6th revision, effective 5/18/2026) | 0.000000: Rider TC5 Refund, 7th revision, effective 11/13/2026 | +0.000278 (USD 0.17 on 600 kWh) | The refund ended three days before this read; the page says its rates are as read on 2026-10-01 (faults file, row 6). The other residential rates read the same; the DCRF page is now its 17th revision (effective 9/30/26) at the same 0.006137 |

What the page's figures cannot be checked against: no publisher prints a bill for a named home on these five tariffs, so
the totals are checked by the arithmetic (the replication) and against averages only.

### The replication

`replication/bill/replicate.py` reads the rules file, this note's arithmetic and `replication/bill/source_rows.csv` (the
rows of `cost_of_power_monthly` the page reads, from the live set with the anon key on 16 November 2026; `--in-dir`
reads another copy of the table) and recomputes every figure the page prints: the page as it opens (the five cards,
the calculator on PG&E, the option lists) and the calculator for 19 cases (`cases.json`: the five defaults, EIA's 2024
average month in California and Texas, and cases that move each field). The page's figures are read off the page drawn
to HTML (`site/scripts/bill-figures.mjs`, into `page_figures.json` and `.csv`). **669 of 669** figures inside half the
page's last shown digit, the numbers inside each line's words included, and the PG&E lines equal Sheet 2's totals in
every PG&E case. On the page as origin/main drew it the same morning, 652 of 669: the 15 card figures printed "license
needed" and two lines printed floating-point kWh (`replicate_on_origin_main.txt`). `replicate.do` rebuilds the five
default bills (229.63, 224.76, 332.91, 95.27, 95.28 USD) and their shares (11.72, 10.28, 6.94, 24.88, 24.88 percent).

### What the tool does not hold

No tax, franchise fee or local charge; no community choice aggregator's generation rate (every California bill is
bundled); no tiered (non-time-of-use) California rate; no all-electric baseline; SCE's Regions 15 and 16; SDG&E's
baseline allowances by climate zone, its climate credit and its season dates; any Texas retail plan's price (the energy
charge is the reader's to type); ERCOT's load-zone prices (the wholesale reference is the hub average); line losses in
the wholesale share; a demand charge (none of the five tariffs has one for a home); any bill after the rates read
(PG&E and Oncor 2026-09-30; SCE, SDG&E and CenterPoint 2026-10-01).

### Tests

`site/scripts/test-bill.mjs` (the hand-computed bills, session 43), `site/scripts/test-bill-render.mjs` (session 7533:
the faults fixed and the fold, drawn to HTML), `site/scripts/bill-figures.mjs --check`, `tests/test_session7533_bill.py`.
