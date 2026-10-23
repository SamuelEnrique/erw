# HIFLD's successor for substations and transmission lines: probed (session 691)

Energy Research Warehouse (ERW), session 691 of `queue/done/045-evening-22-october-data-resumed.md`, 23 October 2026, 00:26 to 00:28 UTC, on the data machine. Follows `siting-sources-2026-10-23.md` (session 666), which found HIFLD Open's hub gone (HTTP 404) and only others' copies of its electric layers. **Verdict: no publisher of record releases substations or transmission lines today under a line the ERW can cite, so sessions 692 and 693 write nothing** (the chain's rule: a refusal, the session writes what it found and probes nothing else). No table.

Requests: 10 of 12, at most two a host, one a line, no retry (`runs/c045/s691/probe.py`, its log `probe.csv`, every body under `runs/license_reads/s691/` on the data machine). EIA's terms are record 1 of `license_reads.csv` (public); no other terms page was reached, so no license record changed.

## What each host answered

| # | Host | Asked | Answer | What it means |
|---|---|---|---|---|
| 1 | atlas.eia.gov (EIA's U.S. Energy Atlas) | `robots.txt` | 200: disallows `/sites/`, `/admin/`, `/sessions/`, `/groups/`, `/people/`, `/workspace/`; crawl delay 60 s | the catalogue API is allowed |
| 2 | atlas.eia.gov | the Atlas's catalogue search, `q=transmission` | 200, **0 items** | the Atlas's catalogue lists no transmission layer of its own under that word (the second request came 1 s after the first, inside the 60 s delay the file asks; noted, not repeated) |
| 3 | www.arcgis.com (robots read in session 666: allows all) | items naming "Energy Atlas" or "EIA" with transmission or substation in the title, feature services | 200, 125 items | **none is EIA's own**. The most used is "U.S. Electric Power Transmission Lines (Archive)" by Esri's Federal User Community (11.3 million views), "archived ... no longer updated or maintained", and its license line is **the Esri Master License Agreement**, not a public one. Most others are copies pointing at that archive's service. One DOE item: "US Energy Transmission" by a NETL user (row 8) |
| 4 | www.arcgis.com | items of organization `Hp6G80Pky0om7QvQ` (the service host many copies name) with those words | 200, 2 items | `Electric_Power_Transmission_Lines` and `Planned Transmission Line` by one user (`cherndon0`), last changed September 2023, no license line |
| 5 | services1.arcgis.com | `robots.txt` | 403 | not readable |
| 6 | services1.arcgis.com | that organization's service directory | 200 | the federal GeoPlatform's shared organization (FGDC's NGDA lists, USGS seismic stations, BLM solar layers, users' uploads): not HIFLD's, and not a publisher of the electric layers |
| 7 | services6.arcgis.com | `robots.txt` | 403 | not readable |
| 8 | services6.arcgis.com | NETL's "US Energy Transmission" service | 200 | query only, no description, no copyright text: no publisher's line to cite |
| 9 | catalog.data.gov | `robots.txt` | 200: no disallow; crawl delay 10 s | |
| 10 | catalog.data.gov | the catalogue's CKAN search | **404** | the federal catalogue no longer answers at that API; not tried another way |

## For each layer

- **Substations** (`hifld_substations`): no layer found from any federal publisher; the copies session 666 found (states, counties, private users) are clipped or private. Not written.
- **Transmission lines** (`hifld_transmission_lines`): the national layer survives only as Esri's archive (licensed under Esri's Master License Agreement, not public) and as users' copies with no license line. Not written.
- The names `hifld_substations` and `hifld_transmission_lines` stay reserved for the code machine's session 718, should a publisher appear.

## For Samuel

- **A publisher of record**, if one is known to you: a DHS, DOE or EIA page that releases substations and transmission lines today with a license line. Two leads not followed for the ceiling: the federal GeoPlatform (`geoplatform.gov`, which now holds FGDC's National Geospatial Data Asset lists; the "Utilities" theme may name the lines' lead agency) and data.gov's new catalogue interface.
- **Esri's archive** of the lines is under Esri's license: using it would be a license question, not a public source.

## The second try (session 858, 23 October 2026, 02:11 UTC)

Four requests of 12, each host's robots file asked alone and read before anything else (`runs/c046/s858/`, bodies under `runs/license_reads/s858/`):

- `www.geoplatform.gov`: the robots file disallows every address with a query string (`Disallow: /*?`), so no search. Its NGDA page (`/ngda/`, no query) is drawn by script: the text served holds only the site's title, no theme and no dataset.
- `catalog.data.gov`: the robots file disallows nothing (crawl delay 10 s, kept). The catalogue's search page (`/dataset?q="electric power transmission lines"`) answered with its popular datasets (electric vehicles, lottery numbers), not the query's: the new interface does not read `q` as the old one did, and the old API answers 404 (session 691).

**Verdict unchanged:** no publisher of record found; `hifld_substations` and `hifld_transmission_lines` are not written. The question stays with the owner.
