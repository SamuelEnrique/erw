# Session 95 report: the interconnection queue explorer

**Built, on `wip/095-queues`, nothing deployed.** A new tool, the review page `/queues`, in the battery page's layout: choose a grid and a technology; the capacity still active by the year it entered; the share of past requests that reached operation and the share withdrawn; the median years from request to operation; storage and solar with storage shown apart; a summary sentence; and what the file does not hold. Behind it is one new derived table.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE TABLE into the warehouse's records. It exists only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/095-queues && git merge origin/main
python warehouse/lock.py run --task "the queue summary" --minutes 10 -- <the venv's python> warehouse/derived/queue_summary.py --snapshot
python warehouse/validate/erw_validate.py warehouse/output/interconnection_queue_summary.csv        # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "interconnection_queue_summary" write
python warehouse/redivis/upload.py --tables interconnection_queue_summary   # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold, while the page is in review:
#      - interconnection_queue_summary
#    then commit coverage.csv, sources.csv, docs/coverage.md, the live set and site/data/queues.json.

# 2. THE PAGE, in review at /queues. A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session95                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-095 && cd ..
git push origin wip/095-queues:task/095-queues
cd site && node scripts/snapshot-live.mjs take after-095 && node scripts/snapshot-live.mjs compare before-095 after-095

# 3. OPEN TO VISITORS, when you have used it: in site/lib/release.ts set "/queues" (and
#    "/data/methods/interconnection_queue_summary") to "live", and add the page to the menu in site/lib/pages.ts.

# 4. THE TABLE CHANGES ONCE A YEAR, when Berkeley Lab publishes a new edition: run the connector
#    (warehouse/connectors/lbnl_queues.py), then step 1. It does not belong in the daily run.
```

**Read these three first:**

1. **The share that "reached operation" is a share of what the queues record, and for some grids that is not every plant that was built.** A request is operational in the file only when its operator's queue says so, and operators differ in how long they keep finished requests. The plainest sign: the file has 45 operating standalone battery requests in ERCOT, and the warehouse's own EIA-860M inventory (`storage_owners_monthly`, August 2026) counts 259 operating battery units there. A unit is not a request and the file ends in 2025, but the gap is too wide for that. So ERCOT's "14.67 percent of storage requests reached operation" is true of the queue's record and too low as a statement about Texas. The page says this under "What the file does not hold"; I did not correct, scale or join anything. If the page is to open, this sentence should probably move up beside the headline number: your call.
2. **A share is given only from 20 past requests, and a median only from 5 dated ones.** Under 20, one project moves a share by five points or more. So New York's solar with storage (12 past requests) shows "not held", and ISO-NE has no median wait at all: none of its 228 operating requests carries an operation date in the file.
3. **"Past requests" are the ones that entered from 2000 to 2020,** five years or more before the file's end. Recent years are mostly still open, and a share that included them would read as a low completion rate when it is only an early one. The window is one constant (`PAST_LAG`).

Energy Research Warehouse (ERW), session 95, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 09:38 to 09:55 UTC, unattended. **Model spend: USD 0.00.** No pull, no request to any publisher, no model call, no force push, no deploy. The data lock was taken once (under a minute) and is free.

## The source and its license

`lbnl_interconnection_queue`, already in the warehouse since session 62: Lawrence Berkeley National Laboratory and GridTracker, *Queued Up: 2026 Edition* data file, 38,201 requests through the end of 2025. No new source was pulled. Its license, in Berkeley Lab's words: "The Queued Up data file is licensed CC BY 4.0... You may use, share, or adapt the dataset as long as you attribute it to Lawrence Berkeley National Laboratory and GridTracker." Republishing is allowed with attribution, so the summary is public; the attribution is in the table's header, in the method note and on the page, and a test holds it there.

## The table

`interconnection_queue_summary`: 17,246 rows, 76 pairs of a grid and a technology (four pairs have no request: offshore wind in MISO, SPP, the West and the Southeast). It passes the validator (exit 0). Built by `warehouse/derived/queue_summary.py`; method in `docs/methods/interconnection_queue_summary.md`. Nothing is estimated: every figure is a count, a sum, a share of counted requests or a median of dated ones.

- **Grids:** the seven ISOs, Berkeley Lab's two regions outside them (West, Southeast), and every region together.
- **Technologies:** solar; solar with storage; storage alone; wind; offshore wind; natural gas; everything else; all. Storage alone and solar with storage are kept apart from solar and from each other.
- **By year entered:** requests and MW entered, and of those the active, suspended, operating and withdrawn.
- **For the whole file:** active and suspended requests and MW; past requests and the shares of them (by count and by MW) that reached operation, were withdrawn, or are still open; the median years from request to operation and how many requests it rests on.
- **By operation year:** the median years to operation of the requests that began operating that year.

What the figures say, every region and technology together: 8,513 active requests for 1,864,963 MW at the end of 2025. Of 22,344 requests that entered from 2000 to 2020, 18.78 percent reached operation and 70.89 percent were withdrawn. The median wait of those built, over 3,098 dated requests, is 3.58 years; by the year operation began it rose from 3.15 years in 2015 to 5.44 in 2025.

| Grid | Active requests | Active MW | Past requests | Reached operation, percent | Withdrawn, percent | Median years |
|---|---|---|---|---|---|---|
| CAISO | 432 | 190,717 | 1,910 | 12.15 | 78.12 | 6.02 |
| ERCOT | 1,796 | 408,108 | 1,553 | 29.56 | 51.19 | 3.70 |
| ISO-NE | 72 | 14,623 | 827 | 26.84 | 70.37 | not held |
| MISO | 1,646 | 350,213 | 2,806 | 18.14 | 69.00 | 3.04 |
| NYISO | 190 | 27,119 | 1,035 | 19.42 | 71.98 | 4.61 |
| PJM | 1,134 | 130,611 | 5,589 | 20.49 | 70.35 | 3.15 |
| SPP | 683 | 151,152 | 1,682 | 16.47 | 72.12 | 4.06 |
| West, outside the ISOs | 1,603 | 448,601 | 4,870 | 16.90 | 73.41 | 2.05 |
| Southeast, outside the ISOs | 957 | 143,820 | 2,072 | 15.83 | 75.77 | 3.79 |

Storage, every region: 2,078 active standalone battery requests for 385,330 MW, and 1,716 active solar-with-storage requests for 503,794 MW. Of past requests, 9.21 percent of standalone batteries and 8.25 percent of solar with storage reached operation (subject to the first point above).

**Counted and left out, each stated on the page:** 665 requests have no year entered (in the totals, in no year); 10 have an unknown status; 16 have no positive capacity (counted, adding no MW); 48 operating requests are dated as operating before their request and are not in the median.

## The page, `/queues`

A panel on the left (ten grids, eight technologies), a sentence, four headline numbers (active capacity; reached operation; withdrawn; request to operation), then: a bar per year entered of the capacity still active; a bar per year entered of what became of that year's requests, with the years counted as past marked; the median wait by the year operation began; and a table of the grid by technology with storage and solar with storage as their own rows. Two folds: what the file does not hold (eight points), and how it is computed. The source line carries the attribution.

**Decision: the page reads the site's own copy** (`site/data/queues.json`, 400 kB), as the other review tools of tonight do: the table is not in the live set, and the freeze forbids a load.

## A fault found on the way, not mine and not fixed

**Reading a table with pandas' `comment="#"` cuts short any row whose text holds a `#`.** The queue file has 154 such rows (queue ids such as "Q#12"); read that way, they lose every column after the id, the status among them. My builder counts the header's lines and skips them instead, and a test holds the row count at 38,201. Other code in the repository reads tables with `comment="#"`; for tables whose values can hold a `#` (names, ids) that is a quiet loss of rows. I did not go looking; it is the second item under "For Samuel".

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session95.py` | 12 tests pass. The summary on requests made for the test: the technology groups, a hybrid kept apart, each status, a request with no year, a request with no capacity, the past window, a share only from 20 requests, a median only from 5 dated ones and never from a date before the request. The table as built: three views counted again from the file by hand; shares that sum to 100; no share under 20 requests; no median for ISO-NE; the attribution in the header. The site's copy equal to the table, row for row. In Node: the page's choices and its years. The page is in review and carries the attribution |
| `site/scripts/check-queues.mjs`, the built site | 55 checks pass: on seven views every number the page marks equals the copy (25 to 45 a view), and no figure the copy lacks is on the page; a bar for each year with active capacity; an outcome bar for each year with a request; a point per operation year or the sentence that says there are too few; the attribution; a view the file does not hold says so and draws nothing; an address it does not understand opens the default; a visitor gets the in-review page with no number on it |
| Site: types, build, route check | exit 0 each; no statement cancelled in the build. Route check: 100 of 100 pages, and 16 live with 84 in review as a visitor |
| `check-values.mjs` | exit 0: 7,485 of 7,485 values match |
| The validator on the table | exit 0 |
| A screenshot of ERCOT's standalone storage | looked at: the sentence, the four numbers, the three charts and the table as described |

The whole suite was not run again this session (it was run in session 94: 677 tests, one old known failure); sessions 94 and 95's own tests pass together.

## Errors and decisions

- **Error, mine, caught by the validator:** the unit "years" is not in the standard's vocabulary; it is "year". And a vintage that was a phrase, not a date: the edition is now in the header and the column is empty.
- **Decision: "everything else" holds the other hybrids** (wind with storage, gas with storage, solar with wind): 400 requests in all. Giving each its own row would have made rows of a handful of requests with no share to show.
- **Decision: suspended requests are not in "active".** They are their own figure, shown beside it.
- **Decision: capacity is the request's total.** For solar with storage that is both parts; the file gives the storage part on its own for too few requests to show it.

## For Samuel

1. **Where the sentence about operational coverage should sit** (the first point above).
2. **`comment="#"` across the repository:** which tables hold a `#` in a value, and whether any reader loses rows. A short session with a test would settle it.
3. **Not in any cloud:** the table is only in `warehouse/output` on this machine until step 1 is run. The builder and the site's copy are in git.
