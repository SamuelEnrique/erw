# The interconnection queue, summarized by grid and technology

One derived table, `interconnection_queue_summary`, behind the page `/queues` ("The interconnection queue", in
review), built by `warehouse/derived/queue_summary.py`. No request is made: the builder reads
`lbnl_interconnection_queue`, which the warehouse already holds.

## Input and license

`lbnl_interconnection_queue`: Lawrence Berkeley National Laboratory and GridTracker, *Queued Up: 2026 Edition* data
file, one row per interconnection request, through the end of 2025 (38,201 requests: the seven ISOs and Berkeley Lab's
West and Southeast regions outside them).

License, in Berkeley Lab's words: "The Queued Up data file is licensed CC BY 4.0... You may use, share, or adapt the
dataset as long as you attribute it to Lawrence Berkeley National Laboratory and GridTracker." The summary is an
adaptation; it is public, and it and the page carry the attribution.

## Grids and technologies

Entity `queue:<grid>:<technology>`.

**Grids:** `caiso`, `ercot`, `isone`, `miso`, `nyiso`, `pjm`, `spp` (Berkeley Lab's `region`), `west` and `southeast`
(its two regions outside the ISOs), and `us`, every request of the file. A request is counted once, under the region
of the queue that holds it.

**Technologies,** from Berkeley Lab's `type_clean`:

| Technology | `type_clean` |
|---|---|
| `solar` | Solar |
| `solar_battery` | Solar+Battery: solar with storage at one point of interconnection |
| `battery` | Battery: storage alone |
| `wind` | Wind (onshore) |
| `offshore_wind` | Offshore Wind |
| `gas` | Gas |
| `other` | everything else: hydro, coal, nuclear, geothermal, oil, other storage, every other hybrid (wind with storage, gas with storage, solar with wind), and a request with no type |
| `all` | every request |

Storage alone and solar with storage are kept apart from solar and from each other.

## What is counted

- **Status** is Berkeley Lab's `q_status`: active, suspended, operational (written `operating`), withdrawn. A request
  of unknown status (10 in the file) is counted as entered and in no status.
- **MW** is the request's `capacity_mw` (its `mw_1 + mw_2 + mw_3`: for a hybrid, all of its parts). A request with no
  positive capacity (16) is counted and adds no MW.
- **The year entered** is `q_year`. A request without one (665) is in the totals of the whole file and in no year.

## The rows

All `freq P1Y`.

**By year entered** (`ts_utc` the first day of that year): `requests_entered`, `mw_entered`, and `requests_` and `mw_`
for `active`, `suspended`, `operating` and `withdrawn`. A year in which no request of that kind entered has no row.

**By operation year** (`ts_utc` the first day of the year operation began, from `on_date`):
`on_median_years_to_operation` and `on_requests_dated`, written when at least five requests are dated.

**For the whole file** (`ts_utc` the first day of the edition's last year, 2025):

| Variable | Meaning |
|---|---|
| `total_requests`, `total_mw`, `requests_without_year` | every request of the view |
| `total_active_requests`, `total_active_mw` | status active |
| `total_suspended_requests`, `total_suspended_mw` | status suspended; not in the active figures |
| `past_requests`, `past_mw` | requests that entered from 2000 to 2020 with a known status |
| `past_operating_share_pct`, `past_withdrawn_share_pct`, `past_open_share_pct` | of `past_requests`; open is active or suspended |
| `past_mw_operating_share_pct`, `past_mw_withdrawn_share_pct`, `past_mw_open_share_pct` | of `past_mw` |
| `operating_requests`, `years_to_operation_n` | requests that reached operation; those of them with both dates in order |
| `median_years_to_operation` | the median over those of the days from `q_date` to `on_date`, over 365.25 |

**Past requests** entered from 2000 to five years before the edition's last year. Five years is long enough for most
outcomes to be known. Recent years are mostly still
open, and a share that included them would read as a low completion rate when it is only an early one.

**When a figure is not written.** A share, when fewer than 20 past requests are counted: under that, one project moves
it by five points or more. A median, when fewer than 5 requests are dated. The page says "not held".

**Years to operation** uses only requests that reached operation and hold both a request date and an operation date,
the operation date not before the request (48 operating requests are dated the other way round and are left out):
3,098 of the 4,789 that reached operation. ISO-NE's operating requests carry no operation date, so ISO-NE has no
median.

## What the table does not hold

- Requests after the end of 2025. The file is a yearly edition.
- Every plant that operates: a request is operational only when its operator's queue says so, and operators differ in
  how long they keep finished and withdrawn requests. A share is of what the queues record.
- The storage part of a hybrid on its own.
- Cost, the developer, network upgrades, or why a request was withdrawn.
- A forecast. Nothing says which active request will be built.

## Rebuilding

```bash
python warehouse/lock.py run --task "the queue summary" --minutes 10 -- <python> warehouse/derived/queue_summary.py --snapshot
python warehouse/derived/queue_summary.py --out-dir DIR      # a trial: nothing in warehouse/output
```

The table is rebuilt whole each run: a new edition of the file replaces every figure.

## Checks

`tests/test_session95.py`: the summary on requests made for the test (the technology groups, a hybrid kept apart, the
statuses, a request with no year, the past window, a share only from 20 requests, a median only from 5 dated ones and
never from a date before the request); the table as built against the file, counted again by hand for three views;
the site's copy equal to the table; and the page's choices, run in Node. `site/scripts/check-queues.mjs`: every number
the page shows, against the site's copy, on the built site.
