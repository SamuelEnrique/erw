# The five tools' replications, run in a clean environment (22 October 2026)

Energy Research Warehouse (ERW), session 582 of chain 034, on samueloldlaptop (the code machine), from `wip/582-s` (cut from `wip/506-combined`, merged with `main` of 22 October 00:00 UTC). Roadmap item 2 asks of each of the five tools "a replication a reader can run". Each replication the method note names was run as a reader would run it: in a new virtual environment outside the repository, from a folder holding only the files the page links, reading nothing of the warehouse; the one file that needs the live set (the Grid tool's) was written with the public (anon) key. Each figure it printed was set beside the page's own figure, read from production (`https://erw-flame.vercel.app`, the pages in review opened with the internal cookie as `check-values.mjs` opens them, 00:11 UTC) by the page's check keys (`data-check`, as `check-values.mjs` reads them) and its scenario cells (`data-cell`, `data-stat`). No Stata is on this machine: no do-file was run.

## The environment

```
C:/Users/lossa/AppData/Local/Programs/Python/Python314/python.exe -m venv C:/Users/lossa/Documents/erw-582-venv/venv   (exit 0; Python 3.14.7, pip only)
```

Each tool's files were copied from `site/public/<folder>/` to a folder of their own (`erw-582-venv/reader/<folder>/`), and each mirror run there. The four mirrors that say "standard library only" ran in the bare environment, before any package was installed. Research's mirror needs numpy: it exited 1 in the bare environment (`ModuleNotFoundError: No module named 'numpy'`, as its docstring warns), then 0 after `python -m pip install --no-deps -r requirements-py314.txt` from the repository (exit 0; the file for Python 3.14, as `requirements.txt` directs). The environment was removed at the end.

## The table

| Tool | Page | Replication (method note) | Command, in the clean environment | Figures set beside the page | Result |
|---|---|---|---|---|---|
| What a battery earns | `/cost-of-power/battery` (ERCOT, 4 hours, perfect foresight, 100 MW) | `erw_2026_battery_replication.py` on `erw_2026_battery_dispatch.csv` (`battery_earns_algorithm.md`) | `python erw_2026_battery_replication.py`: exit 0 | 23: the eight streams of the last twelve months, USD per kW, the ancillary share, debt payments, coverage, scenario A's coverage, NPV, IRR, toll and merchant tail, 2024 and 2025 by stream, the months held, the bad month | 23 of 23 equal |
| What a generator earns | `/cost-of-power/seller` (ERCOT solar, `HB_HUBAVG`, real time, 100 MW) | `erw_2026_generator_replication.py` on `erw_2026_generator_hourly.csv` (`cost_of_power.md`) | `python erw_2026_generator_replication.py erw_2026_generator_hourly.csv`: exit 0 | 16: revenue (twelve months, three years, every year), price received, flat average, capture rate, debt payments, coverage, energy sold, the contract price for 1.25 times, NPV, the breakeven PPA, the worst month, and scenario A's cells | 16 of 16 equal |
| What a datacenter pays | `/cost-of-power` (ERCOT `LZ_NORTH`, a flat 100 MW load, real time) | `erw_2026_datacenter_replication.py` on `erw_2026_datacenter_hourly.csv` and `erw_2026_datacenter_carbon.csv` (`datacenter_pays_algorithm.md`) | `python erw_2026_datacenter_replication.py`: exit 0 | 36: the price, cost, GPU-hour, bad month, the scarce hours and what they cost, the carbon (twelve months, tonnes, the hourly window, nine years), the hub, the zone less the hub, GPUs, day-ahead (the page at `?buy=da`), twelve years | first run 33 of 36: the three carbon figures of the hourly file differed (below); after the carbon file was rewritten from the live set, 36 of 36 equal |
| The Grid tool | `/grid?view=network` and the Now view of the seven ISO grids | `erw_2026_grid_replication.py` on `erw_2026_grid_replication.csv` (`grid_network.md`); `site/scripts/write-grid-replication.mjs` writes the CSV from the page's reads | `python erw_2026_grid_replication.py erw_2026_grid_replication.csv` (the committed file, the hour 2026-10-12 03:00 UTC): exit 0; `node write-grid-replication.mjs <scratch>.csv` (public key): exit 0, the hour 2026-10-20 03:00 UTC; the mirror on it: exit 0 | 60, by `site/scripts/check-grid-replication.mjs` (its Python run in the clean environment, `PYTHON=` set to it): for each of the seven ISO grids its ties, its net imports or exports and the hour's lag in the Now view; the hour shown, the lag and the count of balancing authorities in the Network view; each grid's generation, net imports, share, radius and distance in the gravity shape (in a browser, under the build lock), on a file written at 00:27 UTC from the snapshot built 00:05:36 UTC | 59 of 60 equal (exit 1, twice): the Network view's lag read 44 hours where the mirror read 45. Its check key shows why: the Network view was still served from the previous snapshot (built 2026-10-21 23:05:39 UTC, the hour 2026-10-20 03:00 UTC, so 44 hours) while the Now views carried the new one (45); the mirror on a file written from that previous snapshot (00:09 UTC) printed 44. A difference of the page's cache, not of the replication: nothing mended |
| Research | `/research` (the findings library, default inputs) | `erw_2026_research_replication.py` on the cards' CSVs (`automated_analysis_findings.md`, the pack) | `python erw_2026_research_replication.py . --json <repo>/site/data/findings`: exit 1 bare (numpy), exit 0 with the repository's requirements | the mirror against the cards' JSON: 304 figures of nine cards, then 363 of ten; the page's 110 checked figures (callouts and the table of estimates) against the same JSON | 304 of 304, then 363 of 363 equal; 110 of 110 equal. A tenth card, `peak_hour_moved`, was on the page and in no mirror: added (below) |

Every comparison, figure by figure: the battery's, the generator's and the datacenter's in the appendix below; the scratch scripts that read the pages and set the figures side by side (`dump_keys.mjs`, `compare.py`, `compare_research.py`) lived in the scratch folder, removed at the end as the session's prompt asked; their method is stated here so a session can write them again. A figure counts as equal when the replication's printed number equals the page's raw value rounded half up to the number of decimals the replication prints (scaled where one prints per kW and the other for 100 MW); a figure the page writes only in words (the hub, the zone less the hub, the GPUs, ten of the twelve years) counts as equal when the page's text holds it.

## What failed, and what was mended

1. **The datacenter tool's carbon file was a copy of 14 October.** `erw_2026_datacenter_carbon.csv` is written from the live set by `site/scripts/write-datacenter-carbon.py`, and until now only by a session (265 last). The page reads the same two tables live. Since 14 October the monthly table's September 2026 moved from 340.6896 to 340.6904 kg per MWh (its days complete) and the 430-day hourly window moved on eight days, so the mirror printed 265,548 tonnes a year (the page 265,549), 10,160 hours in the window (the page 10,141) and 313.01 kg per MWh over them (the page 311.74). Mended: the file rewritten from the live set with the public key (`write-datacenter-carbon.py`, exit 0: 87 months, 10,160 hours, 2025-08-17T16 to 2026-10-18T23 UTC), after which the mirror gave the page's three figures; the data machine's run now rewrites it after the hourly CSV (`soft_step dm_datacenter_carbon` in `warehouse/run_data_machine.sh`, the file added to the files it commits); `datacenter_pays_algorithm.md` section 8 says the file goes stale and how. A first guess, that the file's four decimals were the cause, was wrong: the live set holds four decimals, and the change was reverted before any commit.
2. **Research's mirror rebuilt nine of the ten cards `/research` shows.** `peak_hour_moved` (ERCOT and CAISO, `erw_2026_peak_hour_solar.csv`) carries six callouts on the page and no mirror rebuilt them. Mended: `peak_hour_moved()` in `erw_2026_research_replication.py`, from the card's own `numbers_from_rows`, standard library; its 59 figures equal the card's JSON, 363 of 363 in all (`tests/test_session422.py`'s count follows).
3. **Not mended, waiting for Samuel (session 381's item):** the cards' own `.py` downloads exit 1 when a reader runs them from the folder, 11 of 11 (`ModuleNotFoundError: No module named 'findings_common'`: each is the card's generator and reads the warehouse's tables). Whether to ship `findings_common.py` beside them or to say on the card that the do-file and the mirror are the replication is a ruling.

## What this run does not show

- No do-file was run (no Stata on this machine); the Python mirrors are said to follow them step for step.
- The battery's figures that need years before October 2023 (the long-run averages, the stress days, the sensitivity chart) are not in its CSV; `check-values.mjs` recomputes them from the table, a reader cannot (session 381's note).
- The battery, generator and datacenter files are rewritten by the data machine's daily run; a file equals the page only beside a page built from the same day's files. The Grid tool's committed file is of 14 October; a reader compares a Grid file with the page only by writing it the same hour.
- The Grid tool's pages are cached by view: a file written in the hour a snapshot changes can meet one view of the old snapshot and one of the new (above). `check-grid-replication.mjs` sets the file against the pages as they answer; write the file and run it again after the page's hour if the lag alone differs.
- Production serves `main`; this branch's changes (the carbon file, the mirror's tenth card) change no page figure. Nothing was built locally for the datacenter, battery, generator and Research comparisons: production's pages were read.

## Appendix: the battery, the generator and the datacenter, figure by figure

The keys shorten three prefixes: `B|` is `bs|grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=2261119|`, `G` is `iso=ercot&asset=solar&mw=100&mwh=0&ds=7078769&hr=10.725&vom=4.25&fom=12.5` and `D|` is `dc|grid=ercot&region=LZ_NORTH&buy=rt&run=flat&n=100&pct=5&shift=20&mw=100|`.

| Tool | Figure | The replication | The page's key or cell | The page's raw value (as rounded) | Equal |
|---|---|---|---|---|---|
| battery | last twelve months, energy, USD for 100 MW | 5,459,858 | `B\|l12:energy` | 5459858 (as 5459858) | yes |
| battery | last twelve months, regup, USD for 100 MW | 664,224 | `B\|l12:regup` | 664224 (as 664224) | yes |
| battery | last twelve months, regdn, USD for 100 MW | 998,971 | `B\|l12:regdn` | 998971 (as 998971) | yes |
| battery | last twelve months, rrs, USD for 100 MW | 402,471 | `B\|l12:rrs` | 402471 (as 402471) | yes |
| battery | last twelve months, ecrs, USD for 100 MW | 194,068 | `B\|l12:ecrs` | 194068 (as 194068) | yes |
| battery | last twelve months, nspin, USD for 100 MW | 420,627 | `B\|l12:nspin` | 420627 (as 420627) | yes |
| battery | last twelve months, ancillary, USD for 100 MW | 2,680,361 | `B\|l12:ancillary` | 2680361 (as 2680361) | yes |
| battery | last twelve months, total, USD for 100 MW | 8,140,219 | `B\|l12:total` | 8140219 (as 8140219) | yes |
| battery | USD per kW, last twelve months | 81.40 | `B\|l12_kw:total` | 81.4021896 (as 81.40) | yes |
| battery | share from ancillary services, percent | 33 | `B\|l12_share:ancillary` | 33 (as 33) | yes |
| battery | annual debt payments, USD | 2,261,119 | `B\|ds` | 2261119 (as 2261119) | yes |
| battery | debt coverage, times | 2.63 | `B\|cover` | 2.627114698518742 (as 2.63) | yes |
| battery | scenario A, debt coverage, times | 2.63 | data-cell a\|coverage | 2.6271146568380694 (as 2.63) | yes |
| battery | scenario A, NPV, USD per kW | -697.80 | data-cell a\|npv | -697.7988263942754 (as -697.80) | yes |
| battery | scenario A, IRR, percent | -8.8 | data-cell a\|irr | -8.809085053629502 (as -8.8) | yes |
| battery | scenario A, breakeven toll, USD per kW-month | 4.19 | data-cell a\|toll | 4.188665662368691 (as 4.19) | yes |
| battery | scenario A, merchant tail, years | 0 | data-cell a\|tail | 0 (as 0) | yes |
| battery | 2024, energy, USD per kW | 62.70 | `B\|yr:2024:energy / 100,000` | 6269647 (as 62.70) | yes |
| battery | 2024, ancillary, USD per kW | 84.98 | `B\|yr:2024:ancillary / 100,000` | 8497829 (as 84.98) | yes |
| battery | 2025, energy, USD per kW | 57.39 | `B\|yr:2025:energy / 100,000` | 5738909 (as 57.39) | yes |
| battery | 2025, ancillary, USD per kW | 30.05 | `B\|yr:2025:ancillary / 100,000` | 3005052 (as 30.05) | yes |
| battery | months held of the 36 | 36 | `B\|n36` | 36 (as 36) | yes |
| battery | a bad month (2024-12), USD for 100 MW | 475,477 | `B\|p10_36` | 475477 (as 475477) | yes |
| generator | revenue, last twelve months, USD per kW | 59.85 | `ms\|G\|twelve\|revenue` | 59.852264600000005 (as 59.85) | yes |
| generator | the same, scenario A | 59.85 | data-cell a\|revenue | 59.852264600000005 (as 59.85) | yes |
| generator | long-run average, last three full years, USD per kW | 102.24 | `ms\|G\|three\|revenue` | 102.24048083333332 (as 102.24) | yes |
| generator | long-run average, every full year, USD per kW | 130.80 | `ms\|G\|every\|revenue` | 130.79718865714293 (as 130.80) | yes |
| generator | price received, USD per MWh | 23.27 | `cap\|ercot\|HB_HUBAVG\|rt\|solar\|l12\|price` | 23.27094202790795 (as 23.27) | yes |
| generator | price received, scenario A | 23.27 | data-cell a\|capture | 23.27094202790795 (as 23.27) | yes |
| generator | flat average, USD per MWh | 32.17 | `cap\|ercot\|HB_HUBAVG\|rt\|solar\|l12\|flat` | 32.17396634615385 (as 32.17) | yes |
| generator | capture rate, percent | 72 | `cap\|ercot\|HB_HUBAVG\|rt\|solar\|l12\|rate` | 72 (as 72) | yes |
| generator | annual debt payments, USD | 7,078,769 | `mr\|G\|ds` | 7078769 (as 7078769) | yes |
| generator | debt coverage, times | 0.67 | `mr\|G\|ttm_last` | 0.668933604133713 (as 0.67) | yes |
| generator | debt coverage, scenario A | 0.67 | data-cell a\|coverage | 0.6689335733029786 (as 0.67) | yes |
| generator | energy sold, MWh per MW | 2,580 | `ms\|G\|twelve\|energy` | 2580 (as 2580) | yes |
| generator | contract price for 1.25 times, USD per MWh | 39.14 | data-cell a\|contract | 39.14255770083028 (as 39.14) | yes |
| generator | NPV, USD million for 100 MW | -76.66 | data-cell a\|npv (per kW) x 0.1 | -766.62141878456 (as -76.66) | yes |
| generator | breakeven PPA price, USD per MWh | 58.36 | data-cell a\|ppa | 58.359138950395035 (as 58.36) | yes |
| generator | worst month (2024-02), USD for 100 MW | 139,298.97 | data-cell a\|month | 139298.97 (as 139298.97) | yes |
| datacenter | market energy, a flat load, USD per MWh | 33.73 | data-cell a\|price | 33.72888698630137 (as 33.73) | yes |
| datacenter | the same, the summary's figure | 33.73 | data-stat l12_per | 33.73 (as 33.73) | yes |
| datacenter | cost for 100 MW, USD million | 29.55 | data-stat l12_cost (text) | 29.55 (as 29.55) | yes |
| datacenter | power per GPU-hour, USD | 0.0684 | data-cell a\|gpu | 0.06840218280821918 (as 0.0684) | yes |
| datacenter | a bad month (2026-08), USD per MWh | 37.88 | data-cell a\|bad | 37.88271505376341 (as 37.88) | yes |
| datacenter | hours at or above USD 1000 | 4 | `D\|scarce:hours` | 4 (as 4) | yes |
| datacenter | paid in them, USD for 100 MW | 446,175 | `D\|scarce:flat_usd` | 446175 (as 446175) | yes |
| datacenter | carbon, last twelve months, kg per MWh | 303.14 | `D\|co2:l12:kg:flat` | 303.1376056886227 (as 303.14) | yes |
| datacenter | tonnes of CO2 a year for 100 MW | 265,549 | `D\|co2:l12:tonnes:flat` | 265549 (as 265549) | yes |
| datacenter | hours of the hourly window (2025-08-17T16:00:00Z to 2026-10-18T04:00:00Z) | 10141 | `D\|co2:window:hours` | 10141 (as 10141) | yes |
| datacenter | a flat load's own hours, kg per MWh | 311.74 | `D\|co2:window:flat` | 311.7389038161923 (as 311.74) | yes |
| datacenter | carbon, year 2018, kg per MWh | 468.57 | `D\|co2:year:2018` | 468.5746 (as 468.57) | yes |
| datacenter | carbon, year 2019, kg per MWh | 414.04 | `D\|co2:year:2019` | 414.0386699999999 (as 414.04) | yes |
| datacenter | carbon, year 2020, kg per MWh | 375.45 | `D\|co2:year:2020` | 375.4481916666667 (as 375.45) | yes |
| datacenter | carbon, year 2021, kg per MWh | 363.44 | `D\|co2:year:2021` | 363.43838 (as 363.44) | yes |
| datacenter | carbon, year 2022, kg per MWh | 353.76 | `D\|co2:year:2022` | 353.75624999999997 (as 353.76) | yes |
| datacenter | carbon, year 2023, kg per MWh | 339.46 | `D\|co2:year:2023` | 339.46076666666664 (as 339.46) | yes |
| datacenter | carbon, year 2024, kg per MWh | 325.72 | `D\|co2:year:2024` | 325.7208181818182 (as 325.72) | yes |
| datacenter | carbon, year 2025, kg per MWh | 314.26 | `D\|co2:year:2025` | 314.25602727272724 (as 314.26) | yes |
| datacenter | carbon, year 2026, kg per MWh | 300.95 | `D\|co2:year:2026` | 300.9512111111111 (as 300.95) | yes |
| datacenter | the hub beside it, USD per MWh | 32.51 | the page's text (no key) | found | yes |
| datacenter | the zone less its hub, USD per MWh | 1.22 | the page's text (no key) | found | yes |
| datacenter | GPUs that 100 MW powers | 49,310 | the page's text (no key) | found | yes |
| datacenter | bought day-ahead, USD per MWh (/cost-of-power?buy=da) | 35.33 | data-stat l12_per on ?buy=da | 35.33 (as 35.33) | yes |
| datacenter | year 2015, a flat load, USD per MWh | 24.04 | the page's text (no key) | found | yes |
| datacenter | year 2016, a flat load, USD per MWh | 21.68 | `series\|price_years_by_window\|ercot:LZ_NORTH\|datacenter_flat_rt_year_2016\|2016-01-01T00:00:00+00:00` | 21.679029 (as 21.68) | yes |
| datacenter | year 2017, a flat load, USD per MWh | 23.88 | the page's text (no key) | found | yes |
| datacenter | year 2018, a flat load, USD per MWh | 30.82 | the page's text (no key) | found | yes |
| datacenter | year 2019, a flat load, USD per MWh | 36.35 | the page's text (no key) | found | yes |
| datacenter | year 2020, a flat load, USD per MWh | 21.82 | the page's text (no key) | found | yes |
| datacenter | year 2021, a flat load, USD per MWh | 150.61 | `series\|price_years_by_window\|ercot:LZ_NORTH\|datacenter_flat_rt_year_2021\|2021-01-01T00:00:00+00:00` | 150.606437 (as 150.61) | yes |
| datacenter | year 2022, a flat load, USD per MWh | 62.93 | the page's text (no key) | found | yes |
| datacenter | year 2023, a flat load, USD per MWh | 48.69 | the page's text (no key) | found | yes |
| datacenter | year 2024, a flat load, USD per MWh | 26.41 | the page's text (no key) | found | yes |
| datacenter | year 2025, a flat load, USD per MWh | 32.66 | the page's text (no key) | found | yes |
| datacenter | year 2026, a flat load, USD per MWh | 34.02 | the page's text (no key) | found | yes |

75 figures, 75 equal, 0 not (after the carbon file was rewritten).
