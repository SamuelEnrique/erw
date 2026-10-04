# Session 101 report: the early years

**Done, on `wip/101-early-years`, analysis only: no table, no page and no word of the page changed, nothing deployed.** For ERCOT, by year, the battery model's figure taken apart: what part of it rests on each thing a battery of those years did not have. With it, the wording I recommend for the page.

## To make it live

```bash
# Nothing below was run. No preview address: this session changed no page.

# 1. THE WORDING. The page's sentence is in site/app/cost-of-power/battery/page.tsx (the string that begins "This is
#    an upper bound: the battery is assumed to sell as much of its power as reserves as it likes"), and the same words
#    are described in docs/methods/battery_stack.md under "How the page reads the tables". Replace the ERCOT branch of
#    that string with the wording under "The wording I recommend" below, and the method note's bullet with it.
#    This changes a live page: after the freeze, with its snapshots:
cd site && node scripts/snapshot-live.mjs take before-101 && cd ..
git push origin <the branch>:task/101-wording
cd site && node scripts/snapshot-live.mjs take after-101 && node scripts/snapshot-live.mjs compare before-101 after-101

# 2. THE ANALYSIS can be run again at any time; it reads the warehouse and writes two files outside git:
python warehouse/analysis/battery_early_years.py           # about two minutes; warehouse/output/analysis_internal/
```

**Read these four first:**

1. **The warehouse cannot say that the model earns more than real batteries did, because it holds nothing on what real batteries earned.** No settlement, no award, no revenue of an actual resource, in any year. The page says the years before 2024 "show more than real batteries earned"; that is a belief, and a reasonable one, but not something the ERW has measured. So this session could not decompose a gap. It decomposed the model: how much of the page's own figure rests on each assumption. That is a different and smaller answer than the one you asked for, and the note says so in its first section. The source that would close it exists: ERCOT publishes resource-level awards and dispatch sixty days after the operating day. It is a pull to approve.
2. **Before 2024 the figure is payment for holding reserves.** From 2018 to 2023, 68 to 99 percent of what the page shows is reserve capacity. Energy arbitrage alone, for a battery of the size the fleet then had, is USD 15 to 93 per kW a year: 1 to 18 percent of the page's figure. From 2025 energy is two thirds of it. The early years and the recent years are different kinds of number.
3. **The two reasons the page gives are the two the warehouse's own analyses find to matter least.** "Sells as much as it likes at the posted price": until 2023 the whole fleet was smaller than the Responsive Reserve ERCOT bought in every hour (session 74), so one battery was a price-taker in the stream that carried 2018 to 2021; for regulation, selling none at all takes 2 to 14 percent. "Never called": with ERCOT's own list of deployments the model is within 1 percent of the page from 2018 to 2021 (session 79). What does matter, in the model's own terms: the page's battery is longer than the fleet was, real-time prices are known in advance, and 2021 is one week.
4. **The largest step rests on an assumption the model marks as unverified, and I say so rather than lean on it.** At the fleet's own duration (half an hour in 2018, 1.3 hours in 2023) the model earns 37 to 80 percent of the page's figure. But that is because a short battery cannot back a reserve the model requires an hour of energy behind, and that hour, for ERCOT before December 2022, is the model's own assumption (`ONE_HOUR`: "could not be checked against the market operator's own document"). If ERCOT then asked less of a battery, the fleet could sell more than this rung allows. So it is what the model's rules give a battery of the fleet's size, not an estimate of what the fleet earned.

Energy Research Warehouse (ERW), session 101, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 11:54 to 12:10 UTC, unattended. **Model spend: USD 0.00.** No pull, no request, no model call, no force push, no deploy. The data lock was not taken: the analysis writes only under `warehouse/output/analysis_internal/`, as sessions 74's and 79's do.

## The ladder

`warehouse/analysis/battery_early_years.py`. Each rung is the page's own program (`battery_stack.solve_day`) on the page's own prices, over the same 3,197 days (2018-01-01 to 2026-10-02; none left out). USD per kW of rated power:

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
| 2026, to 2 October | 1.58 | 60.5 | 54.4 | 33.3 | 26.1 | 19.2 | 55.0 |

The first rung equals the page's table to within a dollar per MW in every year (the script stops if it does not). The fleet's duration is ERCOT's operating battery MWh over its MW, the mean of the year's months, from EIA-860M; the fleet was 87 MW at the end of 2018 and 4,174 MW at the end of 2023.

What each step takes, as a share of the page's figure:

| Year | Not knowing real time | The fleet's duration | Regulation, at most | The other reserves | What is left: energy |
|---|---|---|---|---|---|
| 2018 | 14.1 percent | 48.7 | 1.9 | 29.2 | 6.1 |
| 2019 | 19.6 | 30.4 | 4.8 | 35.5 | 9.7 |
| 2020 | 13.0 | 22.6 | 13.7 | 42.3 | 8.4 |
| 2021 | 1.2 | 19.1 | 4.7 | 73.8 | 1.2 |
| 2022 | 19.9 | 15.0 | 9.9 | 41.9 | 13.3 |
| 2023 | 13.3 | 26.4 | 11.8 | 30.9 | 17.6 |

**February 2021:** the storm week, 13 to 19 February, is USD 2,841.6 per kW of the page's 3,430.6, 82.8 percent of the year in seven days. Without it 2021 is USD 589.0 per kW on the page.

**Which reserve:** Responsive Reserve is 56, 49, 35 and 72 percent of the page's figure in 2018 to 2021, then 12 and 3 percent in 2022 and 2023, when regulation, Non-Spin (2022) and ECRS (35 percent of 2023) take its place.

**Duration above two hours hardly matters in those years:** the page's own 2-hour battery earns within 1 to 15 percent of its 4-hour one from 2018 to 2023. The step is below one hour, where the reserve rule binds.

## The wording I recommend

Now, under the ERCOT chart: "This is an upper bound: the battery is assumed to sell as much of its power as reserves as it likes at the posted price, and is never called, so years before 2024 show more than real batteries earned. Recent years are the ones to read."

**In its place:**

> This is an upper bound. Before 2024 nearly all of it is payment for holding reserves, to a battery Texas did not have: the fleet then held half an hour to an hour and a third of energy, and the shortest battery here holds two hours. Under this page's own rules a battery of the fleet's size earns 37 to 80 percent of the figure shown for 2018 to 2023, and four fifths of 2021 is one week of February. What real batteries earned is not in this warehouse. Recent years are the ones to read.

**If it must stay one line:**

> This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read.

**What to stop saying:** "so years before 2024 show more than real batteries earned", which states as a result something the warehouse does not measure; and "never called" and "as much as it likes" as the reasons, for the third point above.

**Two things beyond wording, yours to decide:** a one-hour battery among the page's durations, since that is what the fleet was until 2020 and near what it is now (1.6 hours); and the pull of ERCOT's disclosure data, after which the page could show what batteries earned beside what the prices offered.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session101.py` | 7 tests pass. On prices made for the test: a rung that only adds a limit never earns more than the rung above; the page's program holds for a battery of half an hour; energy only pays no reserve; a cap of 1 is no cap. The fleet's duration from the build-out table: under two hours in every year to 2023, and growing. The analysis writes no table and makes no request; no file of the site, of the derived builders or of the connectors, and not the page's method note, differs from the chain's branch before this session. On the results: the rungs of every year go down and cover the same days; the first rung is the page's table and its streams add up to it; every figure of the ladder in the method note is the analysis's |
| The whole suite, at the end of the chain | 753 tests; one failure, old and known (`test_session49`) |

No site build this session: no file of the site changed.

## Errors and decisions

- **Decision: I answered a narrower question than the one asked, and put that first.** "Why the model earns more than real batteries did" needs what real batteries earned. I did not invent a figure for it, and I did not quote one from memory.
- **Decision: the fleet's duration from EIA-860M's MWh over MW.** It is the fleet's average; a year's fleet held both shorter and longer batteries.
- **Decision: "no regulation" as a bound,** since ERCOT's regulation quantities before September 2026 are not held and session 74's cap cannot be computed for those years.
- **Decision: a separate method note** (`docs/methods/battery_early_years.md`), not an edit of `battery_stack.md`, which a live tool links to.
- **Error, mine, caught before the commit:** the note first said the page's 2-hour battery earns "within 4 to 15 percent" of its 4-hour one; the analysis gives 1 to 15.

## For Samuel

1. **The page's sentence** (above): the long form, the short form, or your own.
2. **ERCOT's 60-day disclosure data:** the pull that would let the ERW say what batteries earned. It is large (resource-level, every interval); a first pull could be one resource type and the awards only.
3. **ERCOT's duration rules before December 2022** for regulation, Responsive Reserve and Non-Spin: the one assumption on which the largest step of this ladder rests. Sessions 76 and 100 found the equivalent rules for California, New York and SPP in the operators' own documents; ERCOT's protocols of those years have not been read.
