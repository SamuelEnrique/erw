# The early years: why the battery model earns so much in ERCOT before 2024

Session 101, analysis only. `warehouse/analysis/battery_early_years.py`. No table of the live set, no strategy of the
page and no word of the page was changed. Its files are under `warehouse/output/analysis_internal/` (not in git).

## The question, and what can and cannot be answered here

The page "What a battery earns" shows, for a 4-hour battery in ERCOT with perfect foresight, USD 244 to 530 per kW a
year from 2018 to 2023 (USD 3,431 in 2021), then 148, 87 and 61 in 2024, 2025 and 2026. Under its chart it says the
years before 2024 "show more than real batteries earned".

**The warehouse holds no measure of what real batteries earned** in ERCOT in any year: no settlement, no award and no
revenue of an actual resource. So the gap between the model and real batteries cannot be measured here, and the
sentence on the page is a belief, not a finding. What can be measured is how much of the model's own figure rests on
each thing a battery of those years did not have. That is what follows: the page's figure taken down a ladder, one
assumption at a time, each rung solved with the page's own program (`battery_stack.solve_day`) on the page's own
prices, over the same days.

## The ladder, USD per kW of rated power

| Year | The fleet's duration, hours | 1. The page: foresight, 4 hours | 2. Day-ahead prices, 4 hours | 3. Day-ahead, the fleet's duration | 4. And no regulation | 5. Energy only | Rung 3 over rung 1, percent |
|---|---|---|---|---|---|---|---|
| 2018 | 0.54 | 243.7 | 209.4 | 90.7 | 86.1 | 14.8 | 37.2 |
| 2019 | 0.78 | 402.2 | 323.4 | 201.2 | 181.8 | 39.0 | 50.0 |
| 2020 | 1.05 | 187.5 | 163.1 | 120.7 | 95.0 | 15.7 | 64.4 |
| 2021 | 1.23 | 3,430.6 | 3,390.1 | 2,735.1 | 2,573.4 | 41.1 | 79.7 |
| 2022 | 1.33 | 393.1 | 314.9 | 256.1 | 217.1 | 52.4 | 65.1 |
| 2023 | 1.32 | 530.1 | 459.6 | 319.6 | 257.0 | 93.0 | 60.3 |
| 2024 | 1.45 | 147.7 | 127.1 | 85.9 | 70.5 | 39.3 | 58.2 |
| 2025 | 1.50 | 87.4 | 78.7 | 46.2 | 36.7 | 28.5 | 52.8 |
| 2026 | 1.58 | 60.5 | 54.4 | 33.3 | 26.1 | 19.2 | 55.0 |

2026 is to 2 October (275 days). Every other year holds every day; no day was left out of any rung.

1. **The page:** perfect foresight of real-time prices, four hours. The first rung equals the page's table
   (`battery_stack_monthly`) to within a dollar per MW in every year; the script stops if it does not.
2. **Day-ahead prices:** the page's other strategy. Energy is sold at day-ahead prices; nothing of real time is known.
3. **The fleet's duration:** ERCOT's operating battery MWh over its MW, the mean of the year's months (EIA-860M, via
   `storage_buildout_monthly`). Half an hour in 2018, an hour in 2020, 1.3 hours in 2023. The page's shortest battery
   holds two hours.
4. **No regulation sold:** ERCOT buys a few hundred MW of regulation, and the fleet passed that size in 2021 (821 MW at
   the year's end) and 2022 (2,130 MW). The hourly quantities of those years are not held, so the cap session 74 used
   cannot be computed. Selling no regulation at all is the far end of what any cap could do.
5. **Energy only:** no reserve at all. Day-ahead energy arbitrage at the fleet's duration.

A rung that only adds a limit cannot earn more than the rung above it, and none does; a test holds that.

## What each step takes, as a share of the page's figure, percent

| Year | Not knowing real time (1 to 2) | The fleet's duration (2 to 3) | Regulation, at most (3 to 4) | The other reserves (4 to 5) | What is left: energy |
|---|---|---|---|---|---|
| 2018 | 14.1 | 48.7 | 1.9 | 29.2 | 6.1 |
| 2019 | 19.6 | 30.4 | 4.8 | 35.5 | 9.7 |
| 2020 | 13.0 | 22.6 | 13.7 | 42.3 | 8.4 |
| 2021 | 1.2 | 19.1 | 4.7 | 73.8 | 1.2 |
| 2022 | 19.9 | 15.0 | 9.9 | 41.9 | 13.3 |
| 2023 | 13.3 | 26.4 | 11.8 | 30.9 | 17.6 |
| 2024 | 13.9 | 27.9 | 10.4 | 21.1 | 26.6 |
| 2025 | 10.0 | 37.2 | 10.9 | 9.4 | 32.6 |
| 2026 | 10.0 | 35.0 | 11.8 | 11.4 | 31.7 |

## What the page's figure is made of

| Year | Reserve payments, percent of the page's figure | Responsive Reserve | Regulation, up and down | ECRS | Non-Spin | Earned on the year's ten best days, percent | The page's 2-hour battery, foresight, USD per kW | The same, day-ahead | The fleet at the year's end, MW |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 81.5 | 55.7 | 17.4 | 0.0 | 8.4 | 25.5 | 233.1 | 208.8 | 87 |
| 2019 | 72.5 | 49.3 | 20.6 | 0.0 | 2.6 | 38.1 | 374.5 | 323.0 | 107 |
| 2020 | 81.8 | 35.0 | 46.3 | 0.0 | 0.5 | 14.0 | 178.4 | 162.7 | 218 |
| 2021 | 99.3 | 71.8 | 26.7 | 0.0 | 0.8 | 90.0 | 3,404.0 | 3,384.5 | 821 |
| 2022 | 67.9 | 12.3 | 32.4 | 0.0 | 23.3 | 26.7 | 352.5 | 301.3 | 2,130 |
| 2023 | 71.3 | 3.4 | 31.0 | 35.0 | 1.9 | 39.7 | 451.5 | 416.9 | 4,174 |
| 2024 | 57.5 | 7.1 | 25.5 | 22.7 | 2.2 | 33.0 | 122.4 | 105.3 | 8,294 |
| 2025 | 34.4 | 7.6 | 21.5 | 0.7 | 4.5 | 14.3 | 64.4 | 56.0 | 13,909 |
| 2026 | 32.4 | 5.0 | 18.9 | 3.2 | 5.3 | 28.6 | 43.6 | 37.9 | 18,204 |

**February 2021.** The storm week, 13 to 19 February, is USD 2,841.6 per kW of the page's 3,430.6: 82.8 percent of the
year in seven days. At the fleet's duration and day-ahead prices it is 2,274.7 of 2,735.1 (83.2 percent). Without that
week 2021 is USD 589.0 per kW on the page and 460.4 at the fleet's duration.

## What the ladder says

1. **Before 2024 the page's figure is payment for holding reserves.** 68 to 99 percent of it from 2018 to 2023 is
   reserve capacity; energy arbitrage alone, at the fleet's duration, is USD 15 to 93 per kW in those years, 1 to 18
   percent of what the page shows. From 2025 energy is two thirds of the figure. That, more than any one assumption,
   is why the early years are a different kind of number from the recent ones.
2. **The page's battery is longer than the fleet was, and under the model's own rule that is the largest single
   step.** With the duration the fleet had, the model earns 37 percent of the page's figure in 2018, 50 in 2019, 64 in
   2020 and 60 to 80 from 2021 to 2023. This is not because four hours earn much more than two: the page's own
   two-hour battery earns within 1 to 15 percent of its four-hour one in those years. It is because a battery of half
   an hour cannot back a reserve the model requires an hour of energy behind.
3. **That step rests on an assumption the model itself marks as unverified.** The one hour behind ERCOT's regulation,
   Responsive Reserve and Non-Spin before the rules of December 2022 and December 2025 is "assumed, by the session's
   rule for a requirement that could not be checked against the market operator's own document"
   (`battery_stack.py`, `ONE_HOUR`). If ERCOT then asked less than an hour of a battery, the short fleet could sell
   more than rung 3 allows, and rung 3 is too low. So rung 3 is what the model's rules give a battery of the fleet's
   size, not an estimate of what the fleet earned.
4. **Not knowing real-time prices takes 13 to 20 percent** in every year but 2021, when nearly everything was a
   day-ahead reserve payment.
5. **Regulation can explain at most 2 to 14 percent.** Selling none is the outer bound of a market-size cap.
6. **Being called does not explain it, on the events held.** Session 79 solved the page's program with ERCOT's own
   list of reserve deployments: within 0.1 percent of the page in 2018, 2019 and 2020, 0.9 percent below it in 2021,
   and above it from 2022, because energy delivered on call is paid a scarcity price.
7. **The size of the reserve market does not explain the years to 2022.** Session 74: ERCOT procures at least 2,300 MW
   of Responsive Reserve in every hour, more than the whole fleet until 2023, so the cap is 1 for the stream that
   carried 2018 to 2021.
8. **In 2021 it is one week.**

So the page's present reason, "assumed to sell as much of its power as reserves as it likes at the posted price, and
is never called", is not what the warehouse's own analyses find for the early years. The fleet was small enough to be a
price-taker in Responsive Reserve; being called changes little. What the analyses do find is a battery longer than
the fleet's, real-time prices known in advance, and a year that is one week.

## What is not measured here

- **What real batteries earned.** A source exists: ERCOT publishes resource-level awards and dispatch sixty days after
  the operating day (its 60-day disclosure reports), from which an actual battery's revenue can be computed; its
  independent market monitor's yearly State of the Market report discusses storage revenue. Neither is in the
  warehouse. A pull of either would turn this note from a decomposition of the model into a comparison with the
  fleet.
- **ERCOT's rules for batteries in those years:** how long a battery had to sustain each reserve before December 2022,
  and any limit on the Responsive Reserve a battery could provide. These decide whether rung 3 is too low.
- **Outages, availability and the operators' own strategies,** including batteries built beside a plant for another
  purpose.
- **Regulation quantities before 2026,** so the regulation cap is a bound and not an estimate.

## The wording recommended for the page

The sentence under the ERCOT chart now reads: "This is an upper bound: the battery is assumed to sell as much of its
power as reserves as it likes at the posted price, and is never called, so years before 2024 show more than real
batteries earned. Recent years are the ones to read."

**Recommended, in its place:**

> This is an upper bound. Before 2024 nearly all of it is payment for holding reserves, to a battery Texas did not
> have: the fleet then held half an hour to an hour and a third of energy, and the shortest battery here holds two
> hours. Under this page's own rules a battery of the fleet's size earns 37 to 80 percent of the figure shown for 2018
> to 2023, and four fifths of 2021 is one week of February. What real batteries earned is not in this warehouse.
> Recent years are the ones to read.

**A shorter form, if the sentence must stay one line:**

> This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas
> then had, and 2021 is one week of February. Recent years are the ones to read.

**What to stop saying:** "so years before 2024 show more than real batteries earned" states as a result something the
warehouse does not measure; and "never called" and "as much as it likes" are the two reasons the warehouse's own
analyses found to matter least in those years.

**Two changes beyond wording, for a person to decide:** a one-hour battery among the page's durations, since that is
what the fleet was; and a pull of ERCOT's disclosure data, so that the page can show what batteries did earn beside
what the prices offered.

## Checks

`tests/test_session101.py`: on prices made for the test, a rung that adds a limit never earns more, the program holds
at half an hour, energy only pays no reserve, and a cap of 1 is no cap; the fleet's duration from the build-out table;
the analysis writes no table and the page, its model and its method note are unchanged against main; on the results,
the rungs of every year go down and cover the same days, the first rung is the page's table and the streams add up to
it, and every figure of the ladder's table above is the analysis's.
