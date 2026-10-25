# Session 2723 report: Yukon's electricity not taken (Yukon Energy's hourly workbook states no time base, and its thermal columns are unsound)

25 October 2026, about 19:18 to 19:22 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2723.out`). Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 fetch of the workbook).

## Read these first

- **The ERW held Yukon only in Statistics Canada's tables;** no source or read named Yukon Energy.
- **Yukon Energy** (yukonenergy.ca):
  - It has no robots file (HTTP 404, read 1452).
  - Its page Electricity Generation (read 1454) links a workbook, `YEC_data_2021_2025_Aug_2026.xlsx`, fetched under a run name of its own (16.9 MB, last modified 18 August 2026).
  - The workbook's only terms are a disclaimer: "This material is provided 'as is' for informational purposes only". It grants no reuse, so any table from it would be **internal**.
- **The workbook:**
  - One reading an hour from 1 February 2020 15:00 to 1 January 2026 00:00 by its own clock. The last hour is given twice, and the file's name says August 2026.
  - Columns: total Yukon demand (from 6 January 2022), Yukon Energy's generation, hydro and thermal totals, four hydro plants and each unit.
- **Why no table:**
  - **The clock is not stated, and only part of it can be inferred.** Both of 2020's daylight-saving days have 24 rows. The morning rise of the load sits an hour earlier by the workbook's clock after 8 March 2020 (when Yukon moved to permanent UTC-7) and stays there in every later winter and summer. So the clock is a fixed UTC-8, but that is my inference, not Yukon Energy's statement.
  - **Whether a label marks an hour's start, its end, or an instant is not said.** The standard's `ts_utc` is the interval's start, so the hourly rows could sit an hour off throughout. Daily or monthly sums would carry the same doubt and add another: whether a reading is an hour's mean.
  - **The thermal columns are unsound:**
    - The thermal total reaches about 3,090 MW in December 2025, far above Yukon Energy's whole generation (about 96 MW in those hours).
    - The thermal units do not add to their total (median gap -4 MW).
    - Hydro, by contrast, is sound: the four plants add to its total in every hour but one (0.1 MW off).
- **No table.** The workbook is saved (`warehouse/raw/yukonenergy/s2723probe1/`) for a ruling.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | yukonenergy.ca's robots file (its own request) | 404 |
| 2 | Electricity 101 | 200 |
| 3 | Electricity Generation | 200 |
| 4 | the workbook (the fetch) | 200 |

Reads recorded: 1452 to 1454.

## Decisions made without you

- **Not written:** a time base I inferred, and a reading convention I would have to guess, are not the source's.
- **The workbook kept on the machine,** so that a ruling can be acted on without asking Yukon Energy again.

## For Samuel's ruling

- **Yukon Energy's hourly workbook:**
  - **The question:** may the ERW place its readings at a fixed UTC-8 (inferred from the load's daily shape), each label read as the hour's end, and take demand, generation and hydro only?
  - **The licence:** internal, as the workbook states no reuse terms.
  - **Or:** ask Yukon Energy for the time base and the reading convention.

## Files

- New: this report. Changed: the license record (reads 1452 to 1454) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2723/`, `runs/license_reads/s2723/`, `warehouse/raw/yukonenergy/s2723probe1/`.
