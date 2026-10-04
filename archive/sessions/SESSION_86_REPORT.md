# Session 86 report: the battery model on those grids

**Built.** The battery model now runs on the two other grids whose energy and reserve prices are both public: **NYISO and SPP**. On the live battery page they stay greyed for a visitor, exactly as before, and open only with the internal cookie. ISO-NE and MISO, whose reserve prices are internal, are not modeled and say "held, not shown: license needed". One deploy, with a snapshot before and after: no number on a live page changed.

**Read these four first:**

1. **Do not release these two grids as they are. The numbers are an upper bound that is far too loose.** Over the last twelve months the model gives a 4-hour battery USD 193 per kW in New York and USD 167 in SPP on the day-ahead schedule, against USD 73 in ERCOT on the same page. **In both, most of it is regulation** (New York 64 percent, SPP 78 percent). Regulation is the smallest market there is, the model lets one battery sell all the regulation it likes at the posted price, and it is never called. This is the same fault session 74 found in ERCOT before 2024, larger. The page says so in a box at the top of each of the two grids; it is why they are in review and not live.
2. **Every duration rule for the two grids is labeled assumed, one hour. I could verify neither.** New York: I read NYISO's Ancillary Services Manual (September 2026, 158 pages) as text; it states no time a regulation or reserve supplier must sustain an award. The rule is in the tariff, which I did not read. SPP: the only copies of its market protocols I could find are of 2016 and 2017, before storage had rules of its own. A real requirement longer than an hour would lower the 2-hour battery's numbers most.
3. **New York's regulation is one product, up and down together.** The daily program had only one-way products. It now has a two-way one: an award counts against the battery's power in both directions and needs both stored energy and room. ERCOT's and California's programs are unchanged (their tests pass, and the live table was not rebuilt).
4. **The live table was not touched.** The two grids are in a table of their own, `battery_stack_review_monthly`, held out of the live catalogue; the page reads the site's own copy of it. `battery_stack_monthly` still holds ERCOT and California only, and a test says so.

Energy Research Warehouse (ERW), session 86, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 04:10 to 05:00 UTC, unattended. **Model spend: USD 0.00.** No data pull: the tables of session 85 and the hub prices already held. Two documents fetched to check duration rules (NYISO's manual, 4.2 MB; two old copies of SPP's protocols, 15 MB), three web searches to find their addresses. No model call, no force push. No instruction arrived for session 84. The data lock was held for the table's write (about a minute) and from about 04:36 to 04:38 UTC for coverage, the archive and the upload; released each time.

## To finish

```bash
# Nothing is left half done. What is yours:

# 1. Whether NYISO and SPP are ever shown. My advice: not until the model limits what one battery can sell of a small
#    market (session 74's fleet-limited estimate, built for ERCOT, is the tool) and the two duration rules are read
#    from the operators' own documents. To release a grid when you are satisfied:
#      warehouse/derived/battery_stack.py: move its entry from REVIEW_MARKETS to MARKETS
#      site/lib/batterystack.ts: in GRIDS, ready: true (and drop review: true)
#      warehouse/supabase/live_set.yaml: nothing to add; battery_stack_monthly is already loaded
#    then rebuild and load; the live table gains the grid's rows and the home page's row count goes up.

# 2. The two duration rules. NYISO: the Market Administration and Control Area Services Tariff, section 15.4 (rate
#    schedule 4), is where I expect it; I did not read it and do not cite it. SPP: its current Integrated Marketplace
#    protocols. Each is one line in battery_stack.py (the product's hours and source) and one in batterystack.ts.

# 3. To rebuild the review table after the reserve tables are refreshed (they are not in the daily run):
python warehouse/lock.py run --task "battery review" -- python warehouse/derived/battery_stack.py --review-only --snapshot
#    then commit site/data/battery_stack_review.json. The daily run does not build this table.

# 4. The Vercel token (session 77's step, still open): until INTERNAL_COSTS_TOKEN on Vercel is this warehouse's, the
#    internal cookie cannot be set on production, so on production the two grids are greyed for everyone. I read them
#    on this machine's build with this machine's token.
```

## In plain words

### Which grids, and why only two

"Each grid whose energy and reserve prices are both public." After session 85:

| Grid | Energy price | Reserve prices | In this session |
|---|---|---|---|
| ERCOT, CAISO | public | public | already live; untouched |
| **NYISO** | public (the N.Y.C. zone) | public, with a caution (`nyiso_as_prices`) | **modeled, in review** |
| **SPP** | public (SPPNORTH_HUB) | public, with citation (`spp_as_prices`) | **modeled, in review** |
| ISO-NE | public | internal (`isone_as_prices`) | not modeled: "held, not shown: license needed" |
| MISO | public | internal (`miso_as_prices`) | not modeled: "held, not shown: license needed" |
| PJM | internal | not held | unchanged: "license needed" |

A result built on an internal table is internal too (Decision 23), so ISO-NE and MISO are not built at all, not built and hidden.

### What is modeled in each

| Grid | Products | Direction | Required duration | Left out, and why |
|---|---|---|---|---|
| NYISO | Regulation Capacity | up and down together | 1 hour, **assumed** | 10-minute non-synchronous and 30-minute reserve: a battery that can hold spinning reserve is paid at least as much for it. Checked: priced above spinning reserve in 0 of 18,336 hours, each |
| | 10-Minute Spinning Reserve | up | 1 hour, **assumed** | |
| SPP | Regulation Up, Spinning Reserve, Supplemental Reserve | up | 1 hour, **assumed** | The ramp capability and uncertainty products: what a battery must hold behind them was not read, and adding a paid product on an assumption would only raise the result |
| | Regulation Down | down | 1 hour, **assumed** | |

Everything else is the model of session 67: round trip 86 percent, each local day from empty, at most one full cycle a day, hourly, per MW, reserves paid and never called, a day solved only when every hour of every price is held.

### What it gives: read with the warning above

Last twelve months, October 2025 to September 2026, USD per kW of rated power:

| Grid | Strategy | 2 hours | 4 hours | 8 hours | Of the 4-hour total: energy | regulation | other reserves |
|---|---|---|---|---|---|---|---|
| NYISO | day-ahead schedule | 188.35 | 192.75 | 194.57 | 19.49 | 123.95 | 49.32 |
| NYISO | perfect foresight | 198.90 | 214.78 | 222.11 | 49.79 | 115.50 | 49.48 |
| SPP | day-ahead schedule | 154.96 | 167.28 | 178.50 | 36.28 | 131.00 (up 105.59, down 25.41) | 0.00 |
| SPP | perfect foresight | 190.15 | 213.98 | 228.59 | 85.25 | 128.72 (up 104.19, down 24.53) | 0.01 |

Three things in that table are the model talking, not the market:

- **Duration barely matters.** A 2-hour battery earns 98 percent of what a 4-hour one does in New York. That is what "one hour assumed, never called" produces: a small battery can hold nearly its whole power in reserve all day.
- **SPP's spinning and supplemental reserve earn nothing.** Regulation up pays more in every hour that matters, and the model lets the battery sell only that. A real battery cannot.
- **New York's 2-hour battery on the day-ahead schedule earns USD 0.35 per kW from energy in a year.** It is almost never used as a battery.

Days solved: NYISO 764 on the day-ahead schedule (none left out) and 730 with perfect foresight (32 left out: an hour of the real-time price not held); SPP 762 each (one day left out of the day-ahead schedule, 2026-06-04).

### The page

For a visitor, `/cost-of-power/battery` is as it was, with these words changed and no number:

- The grid list: NYISO and SPP still read "coming" and cannot be chosen. **ISO-NE and MISO read "held, not shown: license needed"** where they read "coming".
- The "Other grids" table, ancillary services column: "not yet in the warehouse" was no longer true of four grids after session 85. NYISO and SPP read "Held: this page's model of it is in review"; ISO-NE and MISO read "Held, not shown: license needed". PJM is unchanged.

A visitor who types `?grid=nyiso` into the address gets ERCOT, as before. With the internal cookie the two grids can be chosen; each opens with a box: in review, shown in the internal view only, durations assumed, and what is left out. The internal view cannot open ISO-NE or MISO either.

Checked on this machine's build, with this machine's token: as a visitor the two grids' radio buttons are disabled; in the internal view they are enabled and the page reads "a 100 MW, 4-hour battery in NYISO earned USD 192.75 per kW" (the table's number).

### The deploy, and every difference

One push, `task/086-battery-grids`; the checks passed (run 37177950376) and the workflow merged it into `main` as `c426761`. Snapshots of the 20 live pages before (04:45 UTC) and after (04:52 UTC), 4,098 checked numbers each.

**186 differences in all. 12 are numbers, and all 12 are the home page's latest prices moving with its own refresh. No number on the battery page changed.**

| Where | Differences | What |
|---|---|---|
| The 13 battery pages (the page and its 12 grid, duration and strategy views) | 12 each, 156 | Words only, the same 12 lines on each: "ISO-NE coming" and "MISO coming" became "held, not shown: license needed"; four rows of the "Other grids" table changed their ancillary services cell as described above |
| `/` | 30 | The six latest real-time prices and their lines of text: the site's 15-minute refresh (12 number keys, 18 lines of text) |
| The other 6 pages | 0 | |

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session86.py` | 16 tests pass: the two-way product (an award never earns more than the same award one way; power and energy limits hold hour by hour on both sides; from empty, nothing can be delivered upward in the first hour); the one-way programs as they were; the live table's grids are ERCOT and California only; a review grid is one whose reserve table is public and a held one is internal; every duration rule in the model is cited or labeled assumed; the review table's streams add up; the page's copy is the table, row for row; a visitor's address cannot open a grid in review and the internal view cannot open a held one |
| The battery tests of sessions 67 and 74 | pass unchanged |
| The whole suite, here | 541 tests; the one old failure (`test_session49`, known since session 82) and the unfinished registrations of sessions 87 and 88, which were not in this commit |
| The suite on the runner | passed (run 37177950376) |
| Validator, coverage, archive, upload by name, license check | exit 0 each; 3,744 rows, counted equal in the public Redivis draft |
| Site: types, build, route check on this machine | exit 0 each |

## Errors and decisions

- **Decision: a table of their own.** Adding the two grids' rows to `battery_stack_monthly` would have changed a live public table and the home page's row count. A separate table, held out of the live catalogue, and the page's own copy of it, change nothing a visitor sees. Releasing a grid is three lines (To finish, 1).
- **Decision: the review table is built only on request** (`--review-only`), not by the daily run. The daily run's path through `battery_stack.py` is the one of session 67, line for line.
- **Decision: New York's energy is priced at the N.Y.C. zone and its reserves at the same zone.** That is the "main" node the rest of the site uses for New York. It is the dearest zone; a battery upstate would show less.
- **A claim I removed.** My first draft of the method note said regulation markets are "a few hundred megawatts". The warehouse holds prices, not quantities, for these grids, so I cannot support the figure and took it out.
- **Nothing failed.**

## For Samuel

1. **Release or not** (To finish, 1). I would not.
2. **The fleet-limited estimate for these two grids** needs the quantities each operator buys, which the warehouse does not hold for New York or SPP. That is a pull, and yours to approve.
3. **The two duration rules** (To finish, 2).
