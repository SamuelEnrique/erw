# The interconnection queue, summarized by grid and technology

One derived table, `interconnection_queue_summary`, behind the page `/queues` ("The interconnection queue", in
review), built by `warehouse/derived/queue_summary.py`. No request is made: the builder reads
`lbnl_interconnection_queue`, which the warehouse already holds.

Tables: `interconnection_queue_summary` (named here by session 2960).

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

## The replication (session 7014, chain 301)

`replication/queues/replicate.py` rebuilds every figure of `site/data/queues.json` from `lbnl_interconnection_queue` by this note alone (the 76 views, the years entered, the operation years, the whole file and the counts): 17,254 of 17,254 equal on 16 November 2026. One rule the note leaves implicit: Berkeley Lab writes the region `ISO-NE`, and its grid is `isone`. `replicate.do` rebuilds five figures of the whole United States in Stata, its expected values at its top. The file is the 2026 edition's, built 4 October 2026; the next edition replaces it whole.

## The cross-checks (session 7018, chain 301)

Berkeley Lab's own summary of the same edition, "Queued Up: 2026 Edition, Characteristics of Power Plants Seeking Transmission Interconnection As of the End of 2025" (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics, read 16 November 2026): "As of the end of 2025, there were ~8,200 projects actively seeking grid interconnection in the U.S., representing 1,312 GW of generation and approximately 749 GW of storage", and "solar (773 GW, -19%), storage (749 GW, -16%) and wind (220 GW, -19%)", "natural gas capacity (253 GW, +86%)". The file's active requests, by the parts of each request (type and MW of each part):

| Figure | Berkeley Lab's summary | The file, active requests |
|---|---|---|
| Active | ~8,200 projects | 8,513 requests |
| Solar | 773 GW | 772.6 GW |
| Natural gas | 253 GW | 252.8 GW |
| Wind | 220 GW | 219.7 GW (onshore 196.3, offshore 23.4) |
| Storage | approximately 749 GW | 552.7 GW (battery 544.1, other storage 8.6) |

Solar, gas and wind agree within 0.4 GW. Storage does not: the summary does not say on that page how its storage figure is built, and the difference (about 196 GW) is not reconciled here. The page's own technology groups count a request once by its cleaned type (a solar and storage hybrid is "solar with storage"), so its figures by group are not the summary's figures by part. The count of active requests is 4 percent above the summary's approximate count of projects.

**Active MW by part type (session 7051, done-line request 190).** Each grid's `all` row also holds `active_mw_parts_battery`, `_solar`, `_wind` (onshore and offshore), `_gas` and `_other_storage`: over the active requests, the MW of every part (`type_1` to `type_3` with `mw_1` to `mw_3`) of that type, so a hybrid's battery counts beside a battery standing alone. In the 2026 edition the United States' battery parts are 544,128 MW, the cross-check's 544.1 GW above (ERCOT 165,315; CAISO 109,820; the West outside CAISO 118,927). `replication/queues/replicate.py` recomputes them.

The replication recomputes every figure of the page's file from the table (17,254 of 17,254).

## The decisions on the page (session 7018, chain 301)

The page draws these at its foot (`site/lib/decisions.ts`, `QUEUES_DECISIONS`), each choice's default and source on hover:

1. Every figure is from Berkeley Lab's yearly Queued Up data file, one row a request through the end of 2025; a newer request is not in it, and the next edition replaces every figure. **Default:** The 2026 edition, through 2025. **Source:** Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file (CC BY 4.0). (session 95)
2. A request is counted once, under the region of the queue that holds it: the seven ISOs, Berkeley Lab's West and Southeast outside them, and the United States as every request of the file. **Default:** Berkeley Lab's region; the US as every request. **Source:** The data file's region field; docs/methods/interconnection_queue_summary.md, "Grids and technologies". (session 95)
3. Technologies follow Berkeley Lab's cleaned type: solar, solar with storage, storage alone, onshore wind, offshore wind and gas each on its own, and every other type and hybrid in one "other"; storage alone and solar with storage are kept apart from solar. **Default:** Seven groups from the cleaned type, hybrids apart. **Source:** The data file's cleaned type field (type_clean). (session 95)
4. A request's MW is the sum of its parts as filed (all parts of a hybrid together); a request with no positive capacity is counted and adds no MW. **Default:** Every part's MW summed; none filled. **Source:** The data file's capacity of each part. (session 95)
5. Status is Berkeley Lab's: active, suspended, operational and withdrawn; a request of unknown status is counted as entered and in no status, and suspended requests are not in the active figures. **Default:** Berkeley Lab's four statuses; unknown counted as entered only. **Source:** The data file's queue status field. (session 95)
6. Completion and withdrawal shares are taken over requests that entered from 2000 to five years before the edition's last year, with a known status, so recent years, still mostly open, do not read as a low completion rate. **Default:** Entered 2000 to 2020 for the 2026 edition. **Source:** docs/methods/interconnection_queue_summary.md, "Past requests". (session 95)
7. A share is written only from at least 20 past requests and a median only from at least 5 dated ones; below that the cell reads "not held", since one project would move a smaller share by five points or more. **Default:** 20 requests for a share; 5 for a median. **Source:** docs/methods/interconnection_queue_summary.md, "When a figure is not written". (session 95)
8. Years to operation are the days from the request to the operation date over 365.25, for requests that reached operation with both dates in order; a request dated the other way round is left out, and ISO-NE, whose operating requests carry no date, has no median. **Default:** Dated requests only, both dates in order. **Source:** The data file's request and operation dates. (session 95)
9. The figures are of what the queues record: operators keep finished and withdrawn requests for different lengths of time, and the file holds no cost, developer, network upgrade or reason for a withdrawal, and no forecast of what will be built. **Default:** What the queues record, nothing inferred. **Source:** docs/methods/interconnection_queue_summary.md, "What the table does not hold". (session 95)

## What waits for the owner (session 7018)

- The storage difference against Berkeley Lab's summary (552.7 GW in the file's parts, approximately 749 GW in the summary): a question for Berkeley Lab, or a reading of its slide deck.

## Sign-off

- Signed off by:
- Date:
- Items of the section above ruled, and how:
