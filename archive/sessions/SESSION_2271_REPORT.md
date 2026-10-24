# Session 2271 report: the licenses' twenty-seventh round (Statistics Finland, Taipower, XM)

24 October 2026, from 04:29 UTC to 04:31 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: none of 20. Each verdict rests on a page this chain's sessions had already read and saved.

## Read these first

- **Three verdicts, each from a read recorded with the outcome `read`.** Each sentence was taken word for word from the saved page (`runs/license_reads/s2268/`, `s2269/`, `s2273/`, on the data machine).
  - **Statistics Finland** (read 445): "Statistics Finland's open data materials and public content of the web service are covered by the Creative Commons Attribution 4.0 International licence." The verdict is **may be public**, sold or not. The page allows commercial use and asks for "Source: Statistics Finland". `statfi_finland_electricity_monthly` is now public by both its flag and its verdict.
  - **Taiwan Power Company (Taipower)** (read 442): the website open data declaration, in Chinese. The sentence is kept in Chinese, with an English reading in the note: free, non-exclusive and sublicensable reuse, irrevocable, without the company's authorisation, the source cited. The verdict is **may be public**, sold or not. The ERW holds no Taipower table (session 2269 took none).
  - **XM S.A. E.S.P. (Colombia)** (read 440): article six of the website's legal terms, in Spanish. The user abstains from reproducing, distributing or giving the public access to the contents without the holder's authorisation. The verdict is **needs written permission**, sold or not. The ERW holds no XM table.
- **Energy-Charts has no verdict from this chain.** Chain 102's session 2257 wrote one (read 392 on `wip/2252-2265-data`, may be public, CC BY 4.0). Its agent said so, and a second row would double at the merge. Until chain 102's verdict reaches main, `energy_charts_central_europe` is "not settled", flag internal. Session 2279 sets the flag public at the landing if chain 102's verdict is on main by then.
- **Not given a verdict, and why:**
  - **Eskom** and **Swissgrid:** chain 101 wrote them on `wip/2238-2251-data`.
  - **Stats SA** (read 432, a bot challenge), the **Coordinador** (409, HTTP 403) and **UNdata** (407, HTTP 404): no page was read. A second request to a host that refused the reader was not made.
  - **The Comision Nacional de Energia:** only its robots file was read (410).
- **The record:** `licenses.py tables`, `write` and `check`: 466 tables, 119 publishers with a verdict, 0 problems. The tests that read the verdicts (sessions 205, 207, 441, 471, 887, 888, 2020, 2123, 2126, 2162, 2168 and 2169) pass. `tests/test_session205.py`'s bound needed no change (420 reads, 379 later reads against 402 allowed; after session 2275's merge with chain 101's landing, 447 reads, 406 against 422).

## Decisions made without you

- **The Chinese and Spanish sentences kept in their own language,** each with an English reading in the note, so that the sentence is the publisher's own words.
- **No request this round.** Every host left had refused the reader or been read already.

## For Samuel's ruling

- **XM's terms:** "needs written permission". Whether to write to XM for Colombia's market data is yours.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `warehouse/metadata/license_tables.csv`, `docs/licenses.md`.
- New: this report.
