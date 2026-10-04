# Session 85 report: more grids' reserve prices

**Built.** Four connectors, four tables, day-ahead ancillary service prices from 2024-09-01, each under its ceiling of 500,000 rows, USD 0. **No day and no hour is missing in any of them.** Two are public (NYISO, SPP) and two are internal because the operator's terms forbid republishing (ISO-NE, MISO). Not PJM. One deploy, with a snapshot before and after: no number on a live page changed.

**Read these four first:**

1. **MISO's terms forbid reading its website by script.** The same page that forbids republishing says: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." The ERW has read MISO's market report files by script every day since session 5, and this session read 763 more (one small file a day, a second apart). You asked for the MISO connector, so I built it and quote the sentence in the connector, the method note and here. Whether the daily MISO pulls should continue is yours to rule.
2. **ISO-NE starts on 1 March 2025, not 1 September 2024.** Its day-ahead ancillary services market began that day; the report answers nothing earlier (I asked for 1 February 2025: a header and no rows). Nothing was invented for the six months before.
3. **SPP is public with a condition.** Its terms allow copying and distributing with citation, "EXCEPT when such materials will be used, in whole or in part, within a commercial publication". The ERW cites SPP in every row, so the table is public. If the platform ever sells something built on these rows, that sentence applies.
4. **A new public table would have moved the home page's numbers at 14:00 UTC.** The home page counts the catalogue's public tables and rows, and the daily run loads the catalogue. So the loader now has a hold: a table named in `live_set.yaml` under `catalogue_hold` stays out of Supabase until you take its name off. `nyiso_as_prices` and `spp_as_prices` are on it. They are in coverage, the archive and the public Redivis draft like any other table.

Energy Research Warehouse (ERW), session 85, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 03:25 (the probes and the connectors, written while session 83's pull ran) to 04:45 UTC, unattended. **Model spend: USD 0.00.** Pulls: 26 monthly archives from NYISO, 20 monthly files from ISO-NE, 763 daily files from MISO (493 MB), one yearly archive and 641 daily files from SPP; and each operator's terms page. No model call, no force push. No instruction arrived for session 84. The data lock was held for seconds at a time for each table's write and from about 04:21 to 04:28 UTC for coverage, the archive and the uploads; released each time.

## To finish

```bash
# Nothing is left half done. What is yours:

# 1. MISO's sentence about automated means (above). If you rule against it, the daily run's MISO hub prices
#    (iso_prices.py, since session 5) are the larger question; this session's connector is not in the daily run.

# 2. The four connectors are not in the daily run. You asked for the tables from 2024-09-01, not for a schedule.
#    To refresh one (it merges; a day already in the raw files is not asked for again):
python warehouse/lock.py run --task "reserve prices" -- python warehouse/connectors/nyiso_as_prices.py
#    and the same for isone_as_prices.py, miso_as_prices.py, spp_as_prices.py. To put them in the daily run, add four
#    run_other lines to warehouse/run_daily.sh and four restore patterns to warehouse/redivis/config.yaml.

# 3. When the reviewer is done (6 October), release the two public tables to the live catalogue: delete their two
#    lines under catalogue_hold in warehouse/supabase/live_set.yaml. The next load adds them, and the home page's
#    count of public tables goes up by two and its rows by 452,808.

# 4. NYISO's license is "public, with a caution" (its notice grants no license and forbids republishing only images
#    and video). The same call session 65 left with you for NYISO's capacity prices.
```

## In plain words

### The four tables

| Table | Rows | Days | From | What a row is | License |
|---|---|---|---|---|---|
| `nyiso_as_prices` | 293,376 | 764 | 2024-09-01 | Five load zones, three reserve prices each (10-minute spinning, 10-minute non-synchronous, 30-minute); regulation once, for the control area | public, with a caution |
| `isone_as_prices` | 55,964 | 583 | 2025-03-01 | The system: three reserve clearing prices and the forecast energy requirement price | internal |
| `miso_as_prices` | 54,936 | 763 | 2024-09-01 | The system ("MISO Wide"): regulating, spinning and supplemental reserve | internal |
| `spp_as_prices` | 159,432 | 763 | 2024-09-01 | The rows SPP names `SPP` and, from 2026-04-01, `SWPW`: seven products | public, with citation |

All four are hourly, in USD per MW of capacity held for one hour, with the hour's start in UTC. Each passed the validator, is in coverage, in the archive, and in a Redivis draft by its license (NYISO and SPP in the public dataset's draft, ISO-NE and MISO in the internal one; the counts there equal the files'). The license check passes: 17 internal tables, none in the public dataset.

### Which regions were kept, and what that lost: nothing, measured

Every region of every product would pass the ceiling in New York (806,000 rows) and SPP (about a million). So each connector keeps the regions that can carry a price of their own, and for every daily file compares the regions it does not keep with the ones it does.

| Grid | Kept | Not kept | Result over the whole window |
|---|---|---|---|
| NYISO | WEST, CAPITL, HUD VL, N.Y.C., LONGIL; NYCA for regulation | Six load zones that sit in a kept zone's reserve region | 764 files: a zone not kept differed from its kept zone in **0** hours. LONGIL, kept beside HUD VL to be safe, differed from it in 3 hours: it was right to keep it |
| MISO | The "MISO Wide" rows | The rows that repeat a price for each resource with its reserve zone | 763 files: a zone's price differed from the system's in **0** hours (checked a second way on 60 files chosen at random) |
| SPP | The rows named SPP and SWPW | The numbered reserve zones (1 to 5; 21 from April 2026) | 763 files: a numbered zone carried a price of neither named row in **0** hours |

What `SWPW` stands for is not stated in SPP's file and I did not guess. It appears on 2026-04-01 together with zone 21, and its prices differ from the SPP row's in nearly every hour.

### Never filled

A (region, product, operating day) is written only when every hour of that day is there exactly once: 24, or 23 and 25 at the clock changes. MISO's file keeps Eastern Standard Time all year and says so; the connector stops if that line ever changes. ISO-NE names an hour by its ending and repeats "02" on the day the clocks go back; a day is read only when its hours are exactly the hours that day has, in order. An empty cell is not a price. In this window no day was short, so no gap is recorded.

### The licenses, with the terms quoted

Each page was fetched on 2026-10-04 and read as text; nothing was summarised by a model.

| Grid | Ruling | The terms |
|---|---|---|
| NYISO | public, with a caution | `https://www.nyiso.com/legal-notice`: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety. Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited". No license is granted; the prohibition names images and video, not data |
| ISO-NE | **internal** | `https://www.iso-ne.com/legal-privacy`: "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." |
| MISO | **internal** | `https://www.misoenergy.org/meet-miso/legal-and-privacy/`: "You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content on this Website or the App in whole or in part." |
| SPP | public, with citation | `https://www.spp.org/terms-conditions/`: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication (printed or otherwise) or when the author(s) or SPP will be quoted in commercial materials, forums or publications. Any commercial use of these materials requires prior, express written authorization from the author(s) or a duly authorized officer of SPP." |

ISO-NE's and MISO's rulings are the ones session 65 made for those operators' capacity prices, on the same sentences. They are stricter than the ERW's treatment of the same operators' hub prices, which are public; session 65 left that difference with you and it is still open.

### The hold

`warehouse/supabase/load.py` reads `catalogue_hold` from `live_set.yaml` and leaves those tables out of the live catalogue and the live set. A dry run of the loader prints "held out of the live catalogue: nyiso_as_prices, spp_as_prices" and selects the same 68 tables as before. The two internal tables need no hold: row-level security hides an internal table from the public key, and neither is in a live-set rule.

### The deploy, and every difference

One push, `task/085-reserve-prices`; the checks passed (run 37177212758) and the workflow merged it into `main` as `f3d73a3`. The push changes no page, but a merge to `main` redeploys the site, so the snapshots were taken: before at 04:30 UTC, after at 04:38 UTC, 20 pages and 4,098 checked numbers each.

**30 differences, all on the home page, all its own 15-minute refresh of the six latest real-time prices** (12 number keys and 18 lines of text). The other 19 pages: 0 differences each. The home page's catalogue numbers did not move.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session85.py` | 31 tests pass: each reader on a made-up file (the clock changes, an empty cell, a zone priced apart, a changed layout, a file of another day), the complete-day rule, the ceiling (a run past it writes no file), the window, the licenses and their quoted terms, the hold, and the four tables (every (region, product, day) holds every hour of its day) |
| The suite on the runner | passed (run 37177212758) |
| Validator, the four tables | pass, exit 0 |
| Coverage | exit 0: 116 tables |
| Archive | exit 0: 563,708 rows of the four tables |
| Redivis upload by name, and the license check | exit 0 both; the counts in the drafts equal the files' |
| The loader, dry run | exit 0; the two public tables held |

## Errors and decisions

- **Decision: one shared loop.** The repository's rule is no shared code between connectors until two need it. Four need this (the arguments, the complete-day rule, the ceiling, the write), so it is `iso_as_common.py`; each connector keeps only what differs. The California connector of session 65 is left as it is.
- **Decision: the full window was fetched into a scratch directory first**, while session 83's pull held the data lock. Raw files are kept once, so the real runs under the lock read them back and asked for nothing twice.
- **My first NYISO docstring said Long Island is its own reserve region "in NYISO's rules".** I had not read that in a document. I replaced it with what the data shows: three hours in which its price differed.
- **Nothing failed.**

## For Samuel

1. **MISO and automated means** (first item above).
2. **ISO-NE and MISO: hub prices public, capacity and reserve prices internal.** One reading for each operator would be cleaner than two.
3. **The daily run** (To finish, 2).
