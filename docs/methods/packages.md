# The ERW in Python, Stata and R: one specification for three packages

Version 0, session 1000, 23 October 2026 (chain 070, `queue/done/070-evening-22-october-code-packages.md`); session 1001 closed the Python package's gaps and settled two points while doing so (decisions 6 and 7). The one specification the three packages follow: the Python package `erw` (`package/`), the Stata command `erw` (`packages/stata/`, from session 1003) and the R package `erw` (`packages/r/`, from session 1005). A call, a word or a column type that one package does differently from this note is a fault of that package. Internal: the site is in review, like every page, and nothing here is published to PyPI, CRAN or SSC (the owner's).

## What a reader gets

A researcher who works in Python, Stata or R reads any public table of the Energy Research Warehouse (ERW) with the same six calls, gets the same rows in the same column types, and cites the same line. Three places hold the tables:

| Backend | Name in the calls | What it holds | Who can read it |
|---|---|---|---|
| Redivis | `redivis` | the record: every public table, each released version kept. The Stanford dataset `datapages.erw:b9wm` (Datapages's, DOI `10.57761/4f55-6d55`) | anyone with a Redivis account and its API token (`REDIVIS_API_TOKEN`) |
| The live set | `live` | the latest rows: a public subset in Supabase, the price and demand tables for their last 35 days, some small tables whole (`warehouse/supabase/live_set.yaml`) | anyone with the live set's address and anon key (`ERW_LIVE_URL`, `ERW_LIVE_KEY`); row-level security returns public rows only |
| Local | `local` | the CSVs of a directory: a clone's `warehouse/output`, or `ERW_DATA_DIR` | whoever holds the files |

## The six calls

Python names them as below; Stata as subcommands (`erw tables`, `erw coverage <table>`, `erw fetch <table>, ...`, `erw cite <table>`, `erw license <table>`, `erw standard <table>`); R as functions of the same names with an `erw_` prefix (`erw_tables()`, `erw_fetch()`, and so on), since `tables` and `fetch` are common words.

### `tables()`

Every table of the warehouse, one row each: `table`, `shape` (`series`, `entities` or `events`), `interval`, `ts_min`, `ts_max`, `n_rows`, `verdict` (the ERW's one word for its license: `public`, `internal` or `unsettled`), `in_live` (`yes` or `no`) and `title` (the provenance header's first line, where the backend can say it without reading the rows). Read from the coverage table of the backend the call uses (Redivis's `erw_coverage`, the live set's `catalogue`, a clone's `warehouse/metadata/coverage.csv`). A held table is listed, with its verdict, so a reader learns it exists and why it is not served.

### `coverage(table)`

The coverage row of one table (with no table, every row): `table`, `iso`, `market`, `n_nodes`, `interval`, `ts_min`, `ts_max` (the first and last interval starts, UTC), `n_rows`, `source_report`, `last_run`, `validator_status`, `license` (the flag: `public` or `internal`), `sector`, `derived`, `tier` (`source`, `derived` or `model_extracted`), `verdict` (as in `tables()`) and `live_window` (`whole`, `<N> days`, `some rows` or `none`). An unknown table is an error that names the tables with a close name.

### `fetch(table, entity=, variable=, start=, end=, backend=)`

One table's rows as a data frame (Python: pandas; Stata: the dataset in memory, replaced; R: a tibble).

- `entity`: one or several values of `entity` (series) or `entity_id` (entities), as the table writes them (`ercot:HB_NORTH`). A series table's `node` (`HB_NORTH`) is also accepted. An events table filters on `source`.
- `variable`: one or several values of `variable` (series), `entity_type` (entities) or `event_type` (events).
- `start`, `end`: rows whose interval starts in `[start, end)`, in UTC. A date or a UTC time (`2025-01-01`, `2025-01-01T06:00:00Z`); a time without a zone is UTC. An entities table filters on `status_date`, an events table on `event_date`.
- `backend`: `auto` (the default), `local`, `redivis` or `live`. `auto` takes the first that answers:
  1. `local`, when the table's CSV is on disk;
  2. `live`, when the table is in the live set and the window starts within its last 30 days (a whole table: always);
  3. `redivis`, the latest released version.
- Python keeps three more arguments for the partitioned tables (`market`, `ba`, `year`), and `node` as another name for `entity`. Stata and R take them as options of the same names.

Every frame carries its **version line** (below) and its table's license verdict: Python in `df.attrs["erw"]`, Stata in the dataset's characteristics (`_dta[erw_version]`, `_dta[erw_license]`), R in the attributes `erw_version` and `erw_license`.

### `cite(table)`

The citation line, in these words, from `warehouse/redivis/release_v1.py`'s `citation()`:

> `<publishers>. <reports>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `datapages.erw`, version <tag> (released <YYYY-MM-DD>).`

- `<publishers>` are the table's publishers, sorted, joined by `; `; `<reports>` the reports of the source registry (`sources.csv`) that name the table, sorted, joined by `; `. A table of the ERW's own work names the ERW as its publisher, as the source registry does (`Energy Research Warehouse (ERW), derived.`, then its report).
- `<tag>` and its date are the released Redivis version the rows came from. Rows from the live set or a clone add, in place of the version clause: `the live set, fetched <YYYY-MM-DDTHH:MM:SSZ>` or `ERW commit <12 characters>`. Redivis's tag is cited as Redivis writes it (`v1.0`, `v2.0`); the ERW's documents call the release after v1.0 "version 1" (`docs/reviews/redivis-v1-release-note-2026-10-23.md`, item 1, for the owner), and the citation follows what Redivis shows.
- An unreleased draft is never cited: a fetch from the draft says so in its version line and `cite` names no version.

### `license(table)`

The table's license: `verdict` (`public`, `internal`, `unsettled`), `status` (`license needed` from its day, or empty), `publishers` (the publishers whose sentence decides it) and `words` (one sentence a reader can act on). The verdict is the ERW's one word a table (`docs/licenses.md`, "Every table", session 378's rule in `scripts/licenses.py`, `erw_verdict`): `public` when the table is flagged public and every publisher's sentence read allows it; `internal` when flagged internal; `unsettled` for anything else (a publisher not read, a "license needed" ruling waiting for its permission, a flag and a verdict that disagree).

### `standard(table)`

The table's shape and its columns: `name`, `type` (below), `required` (`yes`, `reserved`, `partition` or `extra`), in the table's own order, and the key (`entity, variable, ts_utc` for a series, plus `vintage` where the table keeps revisions; `entity_id`; `event_id`), from `docs/datastandard.md`.

## One line a table (session 1008)

Each table's row on `/data` gives the one line that fetches it in each package, from the table's name:

- Python: `erw.fetch("<table>")`
- Stata: `erw fetch <table>, clear`
- R: `erw_fetch("<table>")`

and its shape (series, entities or events). A table whose verdict is not `public` gives, in place of the three lines, the refusal the packages give for it (`<table> is not public: <verdict>. <words> The ERW's license record: <address>`). The verdicts reach the site in `site/data/table_verdicts.json`, which `package/tools/build_tables.py` writes with the package's own copy of the record.

## The column types, by shape

One rule in all three packages. Every column not named here stays text as the table writes it; an empty cell is missing (Python `NaN` or `NaT`, Stata `.` or `""`, R `NA`).

| Shape | Column | Type | Python | Stata | R |
|---|---|---|---|---|---|
| series | `value` | number | `float64` | `double` | `double` |
| series | `ts_utc` | UTC time | `datetime64[ns, UTC]` | `double`, format `%tc` (milliseconds since 1960, UTC) | `POSIXct`, `tz = "UTC"` |
| entities | `lat`, `lon`, `capacity_mw`, every `*_mw` | number | `float64` | `double` | `double` |
| entities | `status_date`, every `*_date` | date | `datetime64[ns]` | `long`, format `%td` | `Date` |
| entities | `retrieved_at` | UTC time | as series | as series | as series |
| events | `event_date` | UTC time (a bare date is midnight UTC) | as series | as series | as series |
| events | `mw`, `price`, `significance`, `ai_power_relevance` | number | `float64` | `double` | `double` |

A series table's `retrieved_at` and `vintage` stay text (decision 7). Stata reads every column with `import delimited ..., stringcols(_all)` and then `destring ..., replace force` the number columns only, so that a code such as `0102` stays text; a time is read with `clock(..., "YMDhms")`.

## The version line

Every fetch says what it read, in one line:

> `ERW <table>: <backend> <version>; ERW commit <12 characters or "unknown">; fetched <YYYY-MM-DDTHH:MM:SSZ>; <n> rows`

- `<backend> <version>`: `Redivis datapages.erw:b9wm v1.0`, `the live set`, or `local files`. A Redivis draft reads `Redivis datapages.erw:b9wm draft (not citable)`.
- The ERW commit is the data commit a clone's tables were written at, or the commit the release package names (`docs/redivis/release-v1-stanford/`), or `unknown` for the live set (which is rebuilt daily from the tables).

## What a held table does

A table whose verdict is not `public` is never served by Redivis or the live set. Asked for one there, the package stops with the license's words, never with an empty frame or "not found":

> `<table> is not public: <verdict>. <words> The ERW's license record: https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md`

where `<words>` are `license(table)$words`, for example "NYISO's terms ask for written permission, which the ERW has not recorded (license needed since 2026-10-21)." A table that is in no backend at all is "not found", with the names of tables close to it.

Read from local files, a held table is the reader's own copy under its own license: the rows are returned, with a warning in the same words, and the frame's license verdict says what it is (decision 2).

## Errors, in words

Each failure a reader can hit answers with one sentence that says what to do, the same in the three packages (session 1013: `package/src/erw/errors.py`, the Stata command's and the R package's messages, and `packages/conformance/conformance.json`, `errors`). `{tables_call}` is each language's own call (`erw.tables()`, `erw tables`, `erw_tables()`); the other placeholders are filled the same way in the three.

- no_network: "The ERW's {where} could not be reached ({reason}). Check the network connection, then try again."
- not_found: "No ERW table named {table}. {tables_call} lists every table{near}."
- held: "{table} is not public: {verdict}. {words} The ERW's license record: {url}"
- empty_window: "No rows of {table} start in [{start}, {end}); its rows run from {ts_min} to {ts_max}."
- redivis_token: "Set REDIVIS_API_TOKEN to a token from https://redivis.com/workspace/settings/tokens, then try again."
- live_keys: "Set ERW_LIVE_URL and ERW_LIVE_KEY to the live set's address and key (the ERW gives them on request), then try again."
- row_limit: "The live set answered a page of {got} rows where {page} were asked for: a fault of the package, not of your call; please tell the ERW (https://github.com/SamuelEnrique/erw/issues)."

A held table and a table not found stop the call. An empty window does not: the frame (or dataset) comes back empty, with the sentence as a warning (Python, `erw.api.ERWEmptyWindow`), a note (Stata) or a message (R).

## Requests

Every call that reaches Redivis or the live set is counted by the package (Python: `erw.requests()`), so a session can say how many it made. A Redivis table read through the uploader's listing costs about 5 requests (chain 043's lesson); `tables()` and `coverage()` read the coverage table once a session and keep it.

## The Python package against this note (session 1000)

What `package/src/erw/` did on 23 October 2026 before session 1001, call by call, and (below the table) what session 1001 did about each gap.

| Call | Today | Gap |
|---|---|---|
| `tables()` | `erw.list_tables()`: the backend's table names only | add `tables()`: one row a table with shape, interval, window, rows, verdict, `in_live`, title; `list_tables()` stays |
| `coverage(table)` | `erw.coverage()`: every row, no table argument; `license` is the flag (`public` or `internal`), not the verdict; no `live_window` | the table argument; the verdict; `live_window` |
| `fetch(...)` | `node=` (node or entity), `start`, `end`, `market`, `ba`, `year`; one backend for the session (`ERW_BACKEND` or `set_backend`) | `entity=` and `variable=`; `backend=` per call with `auto`; a held table refused with the license's words on Redivis and the live set (today: "No ERW table named ...") and warned on local; the version line (today `attrs["erw"]["backend"]` names the backend, without a version, commit or fetch time) |
| `cite(table)` | the publishers and reports, then "Retrieved <date> via the Energy Research Warehouse (ERW), table <table>, data commit <12>." and the provenance tier | the release's words: "Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `datapages.erw`, version <tag> (released <date>)", or the live set's or a commit's clause; the tier stays in `coverage`, not in the citation |
| `license(table)` | none (`coverage()["license"]` is the flag; `warehouse/metadata/license_status.csv` holds the 42 "license needed" rows) | add `license()`: the verdict, the status, the publishers, the words; the verdict needs a per-table file the package can read without the repository (Redivis `erw_coverage` gains it, or a small file shipped in the package) |
| `standard(table)` | none (`_typed` applies the types, `docs/datastandard.md` says them) | add `standard()` |
| Redivis | `RedivisBackend()` defaults to the owner's `energy_research_warehouse` and the draft (`version="next"`), which a public reader cannot read or cite; the Stanford dataset only with `ERW_REDIVIS_DATASET` | default to `datapages.erw:b9wm` and its latest released version; the draft only when asked |
| The live set | `SupabaseBackend` through the `supabase` client, the service key by default (`ERW_SUPABASE_ROLE=anon` for the anon key); `SUPABASE_URL` and `SUPABASE_ANON_KEY` | the anon key by default; `ERW_LIVE_URL` and `ERW_LIVE_KEY` as the reader's names (the old ones still read); the REST address read directly, as Stata and R will, so the three call the same addresses (the `supabase` client becomes optional) |
| Requests | not counted | `erw.requests()` |
| Distribution | `pyproject.toml` names the package `erw`, version `0.1.0` | the distribution name `erw-energy` (the import stays `erw`), session 1002 |

### What session 1001 did, gap by gap

- `tables()`, `license()`, `standard()` and `requests()` added; `coverage(table)` takes a table and gains `verdict` and `live_window`.
- `fetch` takes `entity=`, `variable=` and `backend=` (`auto`, `local`, `live`, `redivis`); `auto` routes each table (local, then the live set within its window, then Redivis). Every frame carries `attrs["erw"]["version_line"]` and its license.
- A table that is not public is refused with the license's words (`ERWLicenseHeld`) on the live set and the Stanford dataset, and read with an `ERWLicenseWarning` from local files.
- `cite` gives the release's words (tested for every table of coverage against `release_v1.py`'s own `citation()`); the last clause names the Redivis version, the live set's fetch time, or the ERW commit.
- `RedivisBackend()` reads `datapages.erw:b9wm` at its latest released version (`version="next"` for the draft); its requests are counted.
- `LiveBackend` reads the live set's REST address with the anon key and sends the filters to the server; `ERW_LIVE_URL` and `ERW_LIVE_KEY` (or `SUPABASE_URL` and `SUPABASE_ANON_KEY`). `SupabaseBackend` stays for the service key.
- Five tables through the three backends (`package/tests/test_backends_three.py`): every row both backends hold agrees before the table's newest 92 days; inside them, the rows a publisher revises differ (18 of `carbon_intensity_monthly`'s, its newest two months; 114 of `ercot_peak_premium_annual`'s, the current year's rows, recomputed each day). The counts: `package/tests/three_backends.json`.
- Not done here: the distribution name `erw-energy` (session 1002).

## The conformance file (session 1006)

`packages/conformance/conformance.json` holds twenty calls and the answers the Python package gave on 23 October 2026 (the fetches, the refusal and the standard on the live set; the citations, the licenses and the table list from the record). Each package's runner makes the same calls: `run_python.py`, `run_stata.do` and `run_r.R`, the last two written from the file by `write_runners.py`. Where the packages say something another way (the clause naming where the rows came from; the fetch time's clock), a runner compares what this note fixes: the words before the clause, the refusal's words (Python, R) or its code, 498 (Stata).

| Calls | Python | Stata | R |
|---|---|---|---|
| 10 fetches (rows, first and last time) | 10 of 10 | not run (no Stata here); the ten addresses equal Python's (`check_ado.py`) | not run (no R here); the ten addresses equal Python's (`check_r.py`) |
| 4 citations (the words before the clause) | 4 of 4 | not run | not run |
| 3 licenses (verdict and words) | 3 of 3 | not run | not run |
| 1 refusal of a held table | 1 of 1 | not run | not run |
| 1 standard (shape and key) | 1 of 1 | not run | not run |
| the table list of the record | 1 of 1 | not run | not run |

The fetch of `eia930_all_demand` for 18 October 2026 is in the live set's 35 days until about 22 November 2026; after that the live set no longer holds it, and the file is made again (`python packages/conformance/make.py`, then `write_runners.py`).

## The package reads what the pages read (session 1012)

Ten figures of the site, each with the check key the page writes (the key check-values reads), recomputed by the Python package's `fetch` from the same table, entity, variable and window (`package/tests/test_page_figures.py`, remote; the figures in `page_figures.json`, recorded from a build of `wip/1011-packages` in the internal view on 23 October 2026). A key `series|...` is the value at a time; `series_max|...` and `series_sum|...` the largest value and the sum over a window.

| Page | Key | Shown | Backend | Result |
|---|---|---|---|---|
| `/grid/ercot` | `series|eia930_all_demand|eia930:ERCO|demand_mw|2026-10-21T23:00:00+00:00` | 61145 | live | reproduced |
| `/grid/ercot` | `series_max|eia930_all_demand|demand_mw|2026-10-21T00:00:00Z|2026-10-22T00:00:00Z|eia930:ERCO` | 63026 | live | reproduced |
| `/grid/ercot` | `series_sum|eia930_all_generation|net_generation_mw|2026-10-21T00:00:00Z|2026-10-22T00:00:00Z|eia930:ERCO` | 1263288 | live | reproduced |
| `/grid/ercot` | `series|carbon_intensity_hourly|eia930:ERCO|intensity_demand|2026-10-19T23:00:00+00:00` | 327.4974 | live | reproduced |
| `/grid/ercot` | `series|storage_daily_cycle|eia930:ERCO|mwh_discharged|2026-10-20T00:00:00+00:00` | 31650 | live | reproduced |
| `/grid/ercot` | `series|price_board_latest|ercot:HB_HUBAVG|da_avg_30d|2026-10-22T00:00:00+00:00` | 38.8049 | local | skipped: held whole by the record, so refused on the live set; this machine's copy predates the day |
| `/grid/ercot` | `series|price_board_peak_offpeak|ercot:HB_HUBAVG|da_peak_mean|2026-10-22T00:00:00+00:00` | 35.3575 | local | skipped: held whole by the record, so refused on the live set; this machine's copy predates the day |
| `/grid/ercot` | `series|state_generation_mix_monthly|eia:US|net_generation_solar_mwh|2026-07-01T00:00:00+00:00` | 41411776.3 | live | reproduced |
| `/cost-of-power/battery` | `series|node_basis_summary|ercot:HB_HUBAVG|dam_storage_hub_spread_4h|2026-09-01T00:00:00+00:00` | 52.3975 | local | reproduced |
| `/cost-of-power/battery` | `series|price_years_by_window|ercot:HB_HUBAVG|battery_foresight_4h_year_2025|2025-01-01T00:00:00+00:00` | 87.439609 | local | reproduced |

Eight of ten are reproduced exactly; no fault was found in the package or in the pages' library. The two others are the price board's tables (`price_board_latest`, `price_board_peak_offpeak`), whose license verdict is `unsettled` (held whole for their ISO-NE, MISO and NYISO rows). The package refuses them on the live set, as this note says it must, while the Grid tool shows their ERCOT figures. Whether a held table's public rows may be shown is the owner's ruling (`docs/licenses.md`, "Held figures that still show").

## Where the three still differ (session 1014)

Session 1014 read the Stata command and the R package line by line against this note and the conformance file (no result of the owner's run in Stata or R was there yet: `docs/reviews/packages-owner-run.md` does not exist). Three divergences were fixed:

- **Redivis's streaming cap**: the Stata and R packages now read a table through Redivis's export when its rows are refused (`POST /tables/<reference>/exports`, the export's status until `completed`, then each file part), as the Python package does. Unproven: the owner's token is over the cap, and no session has a Redivis request to spend on an export of the Stata or R form.
- **The citation's version**: `erw cite` and `erw_cite()` name the released version's tag as Redivis shows it (one request), as Python does, in place of `<the version you read>`.
- **The table list's titles**: Stata and R read them from the release package's table list (`docs/redivis/release-v1-stanford/tables.csv`, its `description`, the header's title line), so `tables()` has a title in all three.

What still differs, by design or by what each language can do:

- **The fetch time** in Stata is the computer's clock, which Stata cannot set against UTC; Python and R write UTC.
- **A table's own extra columns** from the live set are one JSON text column, `extra`, in Stata and R; the Python package spreads them into columns.
- **`standard()` on the live set** names the live set's columns for the shape (with `extra`) in Stata and R, and the table's own columns in Python (the live set's catalogue).
- **The not-found sentence** names the tables of a close name in Python only; Stata and R end it after "lists every table".

## Decisions (each dated, and reversible unless said)

1. 2026-10-23, session 1000: six calls, the same names in the three packages (R with an `erw_` prefix, Stata as subcommands). `list_tables`, `filter`, `sources`, `info` and `version` stay in Python as they are.
2. 2026-10-23, 1000: a held table is refused where the ERW would be serving it (Redivis, the live set) and warned, not refused, from local files. The ERW's own code (`warehouse/chat/`, `warehouse/news/`, `warehouse/analysis/`) reads internal tables through the package from local files, and an outside reader holds no held table's CSV (the tables are not in git, and the site's download route answers a "license needed" table with 403, `site/app/api/download/route.ts`).
3. 2026-10-23, 1000: `auto` prefers local, then the live set for a window within its last 30 days (the live set keeps 35, so a day or two of lag never reaches its edge), then Redivis's latest released version. A reader names a backend to override it.
4. 2026-10-23, 1000: the citation follows Redivis's tag (`v1.0`, `v2.0`), not the ERW's "version 1", until the owner settles the release's number (the release note's item 1).
5. 2026-10-23, 1000: Stata reads every column as text and destrings the number columns with `force`, as the owner writes Stata; no line continuation.
6. 2026-10-23, 1001: the verdict is its own column, `verdict`, in `tables()` and `coverage()`; `coverage()`'s `license` stays the flag (`public` or `internal`), which `filter(license=)`, the chat's tools and the package's tests read.
7. 2026-10-23, 1001: a series table's `retrieved_at` and `vintage` stay text: the tables write `vintage` in more than one form (a month, `2026-08`; a time), and the ERW's own code reads them as text.
8. 2026-10-23, 1001: the default backend is the session's (local files in a clone, or `ERW_BACKEND`), as before; `auto` is the default only where no local tables are found and `ERW_DATA_DIR` names none, so the ERW's own code and tests never reach the network unasked. `backend="auto"` routes any call.
9. 2026-10-23, 1001: the license record is read from the clone's own files when the package runs in one, else from `erw/data/tables.csv`, which `python package/tools/build_tables.py` writes before a build of the package.
