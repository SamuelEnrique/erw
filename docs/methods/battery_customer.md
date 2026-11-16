# What a battery saves a customer, as a reader meets it (`/battery/customer`)

Energy Research Warehouse (ERW). Written by session 7504 (chain 304, 16 November 2026) as the one note for the tool: its one view, the nine numbers it asks for, the arithmetic of every figure it prints, every choice that moves a figure with its default and its source, what real tariffs do to those choices, the cross-check against published work, and what the tool does not hold. The tool was built in session 88 and had no note until this one.

**The tool reads no ERW table.** Every figure on the page is arithmetic on what the reader types, done in the reader's browser by `site/lib/customerbattery.ts`. Nothing typed is sent, stored or put in the address (`site/scripts/check-no-request.mjs` proves it in a browser on a served build). So there is no table note to point to, and the replication reads no table: it reads the cases of `replication/battery_customer/cases.json`.

The page is in review (`site/lib/release.ts`): a visitor sees the in-review page.

## 1. The view

One address, one view. From the top:

| Part | What it is |
|---|---|
| The lead | What the tool is for, and a link to What a battery earns (`/cost-of-power/battery`), which is the other question: a battery selling to the grid |
| The box "This page uses your own numbers, not ERW data" | The two promises: no ERW data, nothing typed sent or stored |
| "Your numbers" | Nine fields (section 2) |
| The result | Nothing until all nine fields hold a number: "Fill in every field to see what the battery saves. N of 9 still needed. No number is assumed for you." Then the summary sentence, three headline figures and "How the two numbers are made" (section 4) |
| "What this assumes", "What it leaves out" | Two folds of words |
| "Decisions on this page" | Session 7504: the ten choices of section 5, each with its default and its source on hover, tap or focus |
| The source line | "Source: none." |

## 2. The nine fields

| Field | Unit | Starts at | Takes | Zero |
|---|---|---|---|---|
| Your peak demand | kW | empty | more than 0, up to 1,000,000 | refused |
| Demand charge | USD per kW a month | empty | 0 to 500 | taken |
| Energy rate, peak hours | USD per kWh | empty | 0 to 5 | taken |
| Energy rate, off-peak hours | USD per kWh | empty | 0 to 5 | taken |
| Battery power | kW | empty | more than 0, up to 1,000,000 | refused |
| Battery energy | kWh | empty | more than 0, up to 10,000,000 | refused |
| How long your peak lasts | hours | 2 | more than 0, up to 24 | refused |
| Days a month it runs | days | 21 | 0 to 31 | taken |
| Round trip | percent | 86 | 1 to 100 | refused |

- **A typed value is a number or it is nothing.** Spaces at the ends and commas are taken out. What is left must be digits with at most one decimal point (`1,200`, `0.25`, `.5`, `5.`). A sign, an exponent, a letter, a value outside the field's limits, or a zero where the field refuses it: the field counts as not filled, and the line under it says so with its range. No number is guessed.
- **The limits are not data.** They only keep a typing slip from giving a result: a rate typed in cents (25 for 0.25) is over 5 and is refused.
- **Six fields start empty**: they are the reader's bill and the reader's battery. Three have a starting value the reader can change (section 5, rows 1, 5 and 6).

## 3. The arithmetic

Write P for the peak (kW), D for the demand charge (USD per kW a month), p and q for the peak and off-peak energy rates (USD per kWh), K and E for the battery's power (kW) and energy (kWh), H for the hours the peak lasts, n for the days a month, and r for the round trip as a share (86 percent is 0.86).

1. **What comes off the peak** is the smallest of three: K (the battery's power), E / H (its energy spread over the peak's hours) and P (the peak itself). The page names which one set it. On a tie the peak itself is named first, then the power, then the energy.
2. **Saved on the demand charge, a month**: that many kW times D. The demand charge before the battery is P times D.
3. **The battery's duration** is E / K hours.
4. **One full cycle, a day**: E kWh out in the peak-rate hours and E / r kWh in at the off-peak rate. Its worth a day is E x p less (E / r) x q.
5. **Moving energy pays** when that worth is above zero, which is when p is above q / r. Then the saving from energy, a month, is the day's worth times n, and the page shows E out and E / r in.
6. **When it does not pay**, the battery is run only for the peak: (what comes off the peak) x H kWh out on each day it runs, that over r in. The saving from energy is then that out times p, less that in times q, times n: zero or a cost, shown with its minus sign. The page prints the peak rate at which moving energy would begin to pay, q / r.
7. **Saved a month** is the demand saving plus the energy saving. **Saved a year** is twelve times the month, before rounding (so the year shown can differ by a few dollars from twelve times the month shown: USD 5,608 a month and USD 67,302 a year in the browser proof's case, where twelve times 5,608 is 67,296).

**Rounding, as printed.** Dollars to the whole dollar. The kW off the peak and the kW the energy allows to one decimal. The kWh a day to the whole kWh. The duration to one decimal. The rate at which moving energy would pay to three decimals. **A number the reader typed is printed back as typed** (section 9, fault row 1).

## 4. Every figure the page prints

For a case with all nine fields filled, the page prints 30 numbers when moving energy pays and 28 when it does not. The keys are those of `replication/battery_customer/page_figures.json`.

| Where | Key | Figure | Rule (section 3) |
|---|---|---|---|
| The summary sentence | `sum_battery_kw`, `sum_battery_kwh` | The battery, as typed | typed |
| | `sum_hours` | Its duration | 3 |
| | `sum_month`, `sum_year` | Saved a month, a year | 7 |
| | `sum_demand`, `sum_energy` | From a lower peak, from moving energy | 2; 5 or 6 |
| "Saved a year" | `tile_year`, `tile_month` | The year and its month | 7 |
| "From shaving the peak" | `tile_demand`, `tile_shaved_kw`, `tile_peak_kw`, `tile_demand_before` | The saving, the kW off, the peak as typed, the demand charge before | 2, 1 |
| "From shifting energy" | `tile_energy`, `tile_out_kwh`, `tile_in_kwh`, `tile_days` | The saving, kWh a day out and in, the days as typed | 5 or 6 |
| "How the two numbers are made", the peak | `how_peak_hours`, `how_power_kw`, `how_energy_kw`, `how_peak_kw`, `how_shaved_kw`, `how_limit`, `how_demand_charge`, `how_demand` | The three limits, the smallest, which one set it (words), the demand charge as typed, the saving | 1, 2 |
| The energy, when it pays | `shift_out_kwh`, `shift_in_kwh`, `shift_per_day`, `shift_month`, `shift_days` | kWh out and in, USD a day, USD over the days | 4, 5 |
| The energy, when it does not | `noshift_break_even`, `noshift_kwh`, `noshift_month` | The peak rate it would take, the kWh a day for the peak, the cost a month | 6 |
| As the page opens | `waiting_needed`, `waiting_fields`, `start_peakHours`, `start_days`, `start_roundTrip` | 6 of 9 still needed; the three starting values | section 2 |

## 5. The choices that move a figure

The page lists these 10 in its "Decisions on this page" block (`site/app/battery/customer/Decisions.tsx`), each with its default and its source on hover. A default with no published source is said to have none (fault row 5).

| Choice | Default | Source |
|---|---|---|
| The hours the peak lasts: the battery must hold its discharge through all of them, so what comes off is the smallest of power, energy over the hours, and the peak | 2 hours, changed in the field | None published: a starting value of session 88. The peak-rate hours of the tariffs read are longer: 4 at Seattle City Light, 5 at Salt River Project. The hours a demand charge counts can be longer still (Seattle City Light's peak demand charge: 6 a.m. to midnight, Monday to Saturday); the hours to type are those the reader's own demand stays near its highest inside them (session 7513) |
| The battery knows when the peak comes and is full when it does, in every month; the load outside the peak's hours is lower than the peak by at least what comes off | All of it comes off | A choice of session 88. NREL found about 85 percent of a 4 hour battery's power a reasonable expectation on 98 buildings' measured loads (section 7) |
| One demand charge on one monthly peak; two charges on the same kW are typed as their sum; a second charge on another peak is not lowered | The one number typed | Austin Energy's tariff of October 1, 2026 (a demand and a regulatory charge on each billed kW); Salt River Project's E-32 (on-peak kW, and the highest kW of the other hours, apart) |
| Two energy rates; the battery discharges at the peak rate and charges at the off-peak rate; charging sets no new peak | The two numbers typed | Seattle City Light and Salt River Project each price three periods |
| The round trip | 86 percent, changed in the field | Lazard, *Levelized Cost of Energy+*, June 2025, page 43 (86 percent is the low end of its range); the Annual Technology Baseline 2025 gives 85. Both are figures for batteries on the grid, the same 86 percent as What a battery earns (`battery_earns_algorithm.md`). The home battery game (`/play/battery`) starts at 90 percent, inside the 88 to 91 percent the same Lazard report gives for a home battery standing alone (`site/lib/battery.ts`); no figure for a commercial customer's battery was read (session 7513) |
| The days a month the battery runs | 21 days, changed in the field | The calendar: 2026 has 261 weekdays, 21.75 a month, about 21 less a tariff's holidays. Salt River Project counts Monday to Friday; Seattle City Light Monday to Saturday, 25.6 a month in 2026 |
| One full cycle on each day it runs when moving energy pays, whatever the building uses in the peak-rate hours | One cycle a day | A choice of session 88. NREL calls a cycle every day a worst case for the energy used (section 7) |
| Moving energy is counted only when it pays (p above q / r); when it does not, the battery cycles for the peak alone and the loss is a cost | Decided by the two rates | Arithmetic. Austin Energy's secondary voltage rates have one price for every hour |
| The year is the month typed, twelve times | Twelve months alike | A choice of session 88. Section 6 measures it on a tariff with seasons |
| The saving on the bill only: no price of the battery, upkeep, wear, taxes, riders, fixed charges, solar or program payment | Left out | A choice of session 88, on the page under "What it leaves out" |

## 6. What the choices do on real tariffs

The replication's nine tariff cases (section 8) were typed from four utilities' published rates. What they show about the choices, each printed by `replicate.py`:

- **The year.** Salt River Project's E-32 has three seasons. The same customer and battery (a 400 kW peak; 100 kW, 400 kWh) save USD 1,114.70 in a summer peak month, USD 743.05 in a summer month and USD 597.00 in a winter month. The year by the plan's own seasons (two, four and six months) is USD 8,783.57. A reader who types July's rates is shown twelve Julys, USD 13,376.42: 52.3 percent more. One who types a winter month is shown USD 7,163.97: 18.4 percent less (`--seasons`).
- **The hours.** The same battery takes 100 kW off a 4 hour peak (Seattle) and 80 kW off a 5 hour peak (Salt River Project): its energy, not its power, sets it.
- **A second demand charge.** E-32 also charges USD 1.02 for each kW of the highest demand outside the on-peak hours, and Seattle City Light USD 0.31 for each off-peak kW above the peak-hours demand. The tool lowers neither, and it takes charging to set no new peak. A battery charging at 100 kW in hours that already hold the customer's highest off-peak demand would add up to USD 102 a month at Salt River Project. That figure is not in the tool.
- **Two charges on one kW.** Austin Energy bills USD 10.32 and USD 5.03 on each billed kW; the case types USD 15.35.
- **One price for every hour.** At Austin Energy the energy saving is a cost: USD 23.24 a month against USD 767.50 from the peak in the smaller case (3 percent), USD 114.52 against USD 4,555.00 in the larger.
- **A battery larger than the load.** Rule 4 moves the whole battery every day whatever the building uses in the peak-rate hours. A battery that holds more than the building uses in those hours could not discharge it all behind the meter. The tool does not know the building's use, so it cannot cap it (fault row 4).

## 7. The cross-check (16 November 2026)

Each published figure was read from its publisher's own document. Nothing was adjusted to match.

| What | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| The share of a 4 hour battery's power that comes off the monthly peak | 1.00 (the three Seattle City Light cases and the Southern California Edison case: a 4 hour battery, a 4 hour peak) | About 0.85: "85% of the rated system power is a more reasonable expectation when the rated power duration is 4 hours" | National Renewable Energy Laboratory, Neubauer and Simpson, *Deployment of Behind-The-Meter Energy Storage for Demand Charge Reduction*, NREL/TP-5400-63162, January 2015, page 16 | Ours 0.15 higher (18 percent). On the report's own tariff the tool gives USD 3,014.00 a month from the peak; 85 percent of it is USD 2,561.90 | The tool takes the battery to know the peak and be full for it, and the peak to be a block of the hours typed. NREL ran a peak-shaving controller on the measured 5-minute loads of 98 buildings over twelve months |
| The same share for a short battery | Set by the hours typed: a 30 minute battery takes 0.25 of its power off a 2 hour peak and all of it off a peak of 30 minutes | About 0.60 for a 30 minute battery under about 25 kW, lower above | The same report, page 9 | Not one figure: ours is 0.25 at the page's starting 2 hours, 1.00 at half an hour | The tool has no load shape: the hours typed are the whole of it. NREL finds the energy a deeper cut needs rising faster than the cut (page 16: 10 kW may need 5 kWh, 20 kW may need 15 kWh), which a single number of hours cannot hold |
| The saving from the peak against the saving from energy | 4.5 times on the report's own tariff (USD 3,014.00 against USD 662.97 a month); 0.94 to 2.06 times on the six cases of today's rates that differ by hour; where there is one price, energy is a cost of 3 percent of the demand saving | "In all cases, the economic savings of demand charges dwarf the impact on energy costs, often by an order of magnitude or more" | The same report, page 9, on Southern California Edison's TOU-GS-2 Option B of about April 2013 | Ours gives energy a far larger part | Two causes. The tool cycles the whole battery on each day when it pays (rule 4); NREL's batteries are small and cycle to cut the peak. And the report's tariff charged USD 30.14 for each kW in summer, 2.5 to 6.8 times the demand charges of the six cases |
| Demand charges above USD 15 per kW | 3 of the 9 tariff cases (Austin Energy USD 15.35 and USD 18.22 with the regulatory charge; Southern California Edison 2013, USD 30.14); 6 below (USD 4.45 to USD 12.19) | "Nearly 5 million commercial customers" can subscribe to tariffs with demand charges above USD 15 per kW, of 18 million | National Renewable Energy Laboratory and Clean Energy Group, *Identifying Potential Markets for Behind-the-Meter Battery Energy Storage: A Survey of U.S. Demand Charges*, NREL/BR-6A20-68963, August 2017, page 1 | None to take: the survey counts customers, the tool prices one | It places the cases: most of those read here are below the mark the survey uses |
| A customer's saving in dollars a year | USD 7,164 to USD 62,059 across the nine tariff cases | Nothing published stands against these | Seattle City Light, Salt River Project and Austin Energy print rates, not a worked example of a battery's saving, in the documents read. NREL's case studies with its System Advisor Model (DiOrio, Dobos and Janzou, NREL/TP-6A20-64987, November 2015, table 9) give net present values with the battery's cost and incentives in them (USD 31,874 and USD 60,731), not a saving on the bill | Not comparable | Said plainly: no published bill saving for the same tariff, customer and battery was found |

The figures in the first column are printed by `python replication/battery_customer/replicate.py --crosscheck`.

## 8. The cases and the hosts read

`replication/battery_customer/cases.json` holds 12 cases: the page as it opens; the numbers the browser proof types; nine tariff cases; one case of numbers with decimals. In a tariff case the rates are the publisher's, as printed; the customer's peak and the battery's size are the case, chosen inside the tariff's class, and are not data.

| Case | Document | In effect | Demand charge typed | Peak and off-peak rate typed |
|---|---|---|---|---|
| Seattle City Light, medium general service (50 to 999 kW), City of Seattle, time of use | Seattle City Light, Business Rates, "Current Rates" | As read on 16 November 2026; the page prints no date for the table and says a 4 percent surcharge was removed on April 1, 2026 | 5.36 | 0.1218, 0.0609 |
| The same, Downtown Network | The same | The same | 12.19 | 0.1360, 0.0680 |
| Seattle City Light, large general service (1,000 to 9,999 kW), City of Seattle | The same | The same | 5.18 | 0.1186, 0.0593 |
| Salt River Project, E-32 time-of-use general service, summer peak (July, August) | E-32 Standard Price Plan for Time-of-Use General Service, pages 2 and 3 | November 2025 billing cycle; the transmission adjustment from January 2026 | 6.75 | 0.1924, 0.1093 |
| The same, summer (May, June, September, October) | The same | The same | 5.05 | 0.1319, 0.0803 |
| The same, winter (November to April) | The same, pages 2 and 4 | The same | 4.45 | 0.0982, 0.0609 |
| Austin Energy, secondary voltage, 10 kW to under 300 kW, inside the city | City of Austin, Electric Tariff (October 1, 2026), the page numbered 12 | Bills rendered on or after October 1, 2026 | 15.35 (10.32 + 5.03) | 0.06797, 0.06797 (five charges per kWh added) |
| Austin Energy, secondary voltage, 300 kW or more, inside the city | The same, the page numbered 13 | The same | 18.22 (13.19 + 5.03) | 0.067, 0.067 |
| Southern California Edison, TOU-GS-2 Option B, summer, about April 2013 | As NREL/TP-5400-63162 prints it (tables 1 and 2). The tariff sheet was not read | Historic: not a rate in force | 30.14 (13.94 + 16.20) | 0.1466, 0.0582 |

**The hosts read**, each after its robots file and its terms, with the User-Agent "ERW research project, github.com/SamuelEnrique/erw":

| Host | Robots file | Terms | Read |
|---|---|---|---|
| `www.seattle.gov` | Allows all but `/searchresults/` | The terms of use page says nothing of automated access or of reuse | The Business Rates page |
| `www.srpnet.com` | Allows all | Nothing on automated access. "You may not reproduce or distribute materials found on SRP's Digital Platforms" without written permission | The E-32 and E-36 price plans (E-36 was read and not used: its energy price steps down by block, not by hour) |
| `austinenergy.com` | Disallows seven folders, none of them the tariff's | Nothing on automated access. Austin Energy holds the copyright and "no unauthorized use is permitted" | The commercial rates page and the tariff |
| `docs.nlr.gov` (the National Laboratory of the Rockies, formerly NREL) | `www.nlr.gov` allows all | Nothing on automated access; its documents may be under copyright, with a license to the government | Three reports |

Only the rates (figures) of Salt River Project and Austin Energy are kept, with the document cited and linked; no text or page of theirs is copied into the repository, and nothing of theirs is on the page (for Samuel's ruling in the session report). **Not read:** `www.duke-energy.com` (its robots file disallows the folder its tariff files are in); `www.xcelenergy.com` (it answered 404 for its robots file, and was left); `www.sce.com`, `www.portlandgeneral.com` and `www.cleanegroup.org` (robots files read, nothing else asked). No request was made of EDGAR, a MISO host, the Virginia State Corporation Commission, the Illinois or Ohio docket hosts, or any publisher in `warehouse/metadata/paused_sources.csv`.

## 9. The replication

`replication/battery_customer/`:

- `replicate.py` (standard library; no request; writes nothing): written from sections 2 to 4 of this note. It recomputes every figure of every case and sets it beside the page's.
- `cases.json`: the 12 cases, with each tariff's document, address, effective date, time read, the rates as printed and how they were typed.
- `page_figures.json`, `page_figures.csv`: what the page prints for each case, read off the page's own calculator drawn to HTML by `site/scripts/battery-customer-figures.mjs` (this machine cannot build the site; the calculator is the page's own component, with the case's numbers set in its fields for the draw).
- `replicate.do`: Stata, the five headline figures, expected values at its top. Not run: Stata is not on the machine that wrote it.

As printed on 16 November 2026: `331 of 331 inside the tolerance, 12 cases; computed here and not shown by the page: 0; not replicated here: nothing`. The tolerance is half of the page's last shown digit. No difference is named: there is none.

**Said plainly:** the session that wrote the replication had read the page's code. The script is in Python, in its own words, from this note, and the note was written before it.

**Faults found** are in `docs/reviews/battery-customer-faults-2026-11-16.md`. Row 1, fixed in this session: the page printed a typed number rounded (a demand charge of USD 5.36 read "At $5 per kW that is $536 a month"; a 13.5 kWh battery read "14 kWh"). The arithmetic used the number typed; the words beside it did not show it.

## 10. What the tool does not hold

- No tariff, no bill and no load: it cannot check that a typed rate is a real one, or that a peak lasts the hours typed.
- No season, no ratchet, no second demand charge, no third energy rate, no block prices (section 6).
- No cost of the battery, so no payback and no return.
- No solar on the same meter, no export, no program payment.
- No two cases side by side: a reader compares two batteries by typing each in turn.

## 11. Tests

- `tests/test_session88.py`: the arithmetic on hand cases; that the calculator and its arithmetic name no way to send or store; the browser proof where a built site is served.
- `site/scripts/test-battery-customer-page.mjs` (31 checks): the decisions block drawn; the calculator drawn with numbers in its fields; the page as it opens.
- `tests/test_session7504_battery_customer.py`: the above run; the page's figures as committed; the replication, N of N; the cases' cites; this note against the page's list.
- `site/scripts/test-battery-customer-read.mjs` and `tests/test_session7513_battery_customer_read.py` (session 7513): the five cases of the read (section 12) drawn; a rate typed in cents; the line under the hours field; the round trip of the site's three battery pages.

## 12. The tool read as its reader (session 7513, chain 304, part B)

`docs/reviews/battery-customer-read-2026-11-16.md`: the energy manager of a grocery chain brings five cases, each a published rate of section 8 with one real store (27,625 square feet, a peak of about 247 kW in 2012: EnerNOC facility 384 in NREL/TP-6A20-64987, page 7) and a battery of a published size (55 kW and 110 kWh, the size that report found best for the store; 100 kW and 400 kWh, a 4 hour commercial unit). What the read changed on the page:

- **A refused rate is told its unit.** A rate typed as a sheet prints it in cents (14.66 for 14.66 cents per kWh) is over the field's limit. The line under the field read "Not a number this page can use (0 to 5)." in the place of the one hint that said dollars. It now adds "The rate is typed in dollars: 12 cents is 0.12." (`refusal` in `site/lib/customerbattery.ts`), and the off-peak field's own line says dollars.
- **The line under "How long your peak lasts"** says whose hours: "How long your own demand stays near its highest, in the hours your demand charge counts." On Seattle City Light's medium rate the word peak names three spans (the customer's own, the 4 peak-rate hours, the 18 hours the peak demand charge counts), and the same battery takes USD 295, USD 147 or USD 33 a month off the demand charge at 2, 4 and 18 hours typed.
- **The round trip's source** sets the site's three battery pages side by side (the table above).

No figure of the arithmetic changed: `page_figures.json` is as committed.
