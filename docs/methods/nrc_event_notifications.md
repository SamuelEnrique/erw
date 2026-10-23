# Power reactor event reports, a report and unit (the NRC's Event Notification Reports)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2043).

Tables: `nrc_event_notifications`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC), Operations Center, Event Notification Reports (`https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports`), read from two of the NRC's publications of the same reports: the pipe-separated raw data file `https://www.nrc.gov/sites/default/files/doc_library/reading-rm/doc-collections/event-status/event/event-notification-rpt-lastmonth.txt` (the fields of the NRC's data dictionary), and the daily pages `.../event-notification-reports/<YEAR>/<YYYYMMDD>en` listed by the year's index page. Source id `nrc:event_notification_reports`. Connector: `warehouse/connectors/nrc_event_reports.py` (session 2043).

## Vintage and revision

Written by run `20261023T183912Z` (23 October 2026), which reused every saved file (`--offline`, session 2043's report). Header: "The raw file's last modification: 2025-08-05T16:32:13Z; the daily pages read: 9, 20261013 to 20261023."

The raw file stopped updating on 5 August 2025: its 16 power reactor reports were notified from 30 June to 30 July 2025, for events from 6 May to 30 July 2025 (local). The pages give 4 reports, events of 10 to 16 October 2026, from the pages of 13, 16 and 19 October. Nothing lies between.

The table is a snapshot, written whole each run. The raw file and the year's index are asked fresh (unless `--no-refresh`); a daily page saved by an earlier run is reused and not counted, and at most `--pages` new pages (default 10), newest first, are asked a run. Only the index of `--year` (default the current year) is read, and only its pages.

## Shape and variables

Events, 25 rows of 20 reports (a report about two or three units is a row a unit): 21 rows of 16 reports from the raw file, 4 of 4 from the pages. `event_id` `nrc_en:<event number>:<unit>`; `event_date` the event's time in UTC, from the NRC's date, time and zone (`EDT`, `CDT`; `x_event_local`, `x_event_tz` keep them; `ET` is read with daylight saving); `event_type` `reactor_scram` when the unit's scram code is not N or the report cites 50.72(b)(2)(iv)(B), else `reactor_event`; `parties` the licensee; `mw`, `price`, `currency`, `status`, `entity_ids` empty.

- 7 scrams (7 rows, 7 reports: 6 A/R or M/R, and Monticello's of 28 July 2025, code N under 50.72(b)(2)(iv)(B)); 13 other reports (18 rows).
- `event_date` from 2025-05-07T01:08:00Z (Millstone 3) to 2026-10-17T03:45:00Z (Waterford 3's trip at 22:45 CDT on 16 October).
- 18 facilities in 14 states; 12 rows in EDT, 13 in CDT; every row's emergency class is Non Emergency. `x_cfr` holds every 10 CFR section, joined by "; ", with its words in `x_cfr_words`.
- `x_initial_power_pct` and `x_current_power_pct` the unit's power in percent before the event and at the report; the modes beside them.
- `parties` is empty in the 4 rows read from the pages (the NRC's page gave no `Rep Org` or `Licensee` value that was read).
- `x_last_update` is the date of the report's last update, `YYYY-MM-DD`, in all 25 rows (the raw file's "7/2/2025 12:17:00 PM" read through the same date parser as the pages'; this note's first draft found the raw file's kept as text, and session 2052 corrected the code and wrote the table again).

## Reading the source

- Only reports filed under "Power Reactor" are kept; agreement state, materials, fuel cycle and Part 21 reports are not, nor the event text and the staff notified.
- A raw file whose fields are not the data dictionary's, a page label not in the map, a time zone not in `ZONES`, a unit table not in the expected form, or a page that lists event numbers and yields no block stops the run.
- A report in both publications keeps the daily page's row when the two agree on the scram code, the powers and the time; if they differ the run stops.
- Ceiling: the raw file, the index, and at most `--pages` new daily pages a run.

## License

`license_verdicts.csv` records the NRC, read 16: "may be public", for public and for commercial use: "NRC's website constitutes a U.S. Government Work under federal copyright law and as such, it is not subject to copyright. It is freely available for non-exclusive rights in publication or reproduction for any purpose, in any form, and there are no restrictions on use." Its note: the NRC "would appreciate the courtesy of credit". `license_tables.csv` lists the table under the NRC; `docs/licenses.md` as may be public, flagged public, agreeing.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines; the header's six counts (daily_page 2 and 2, raw_file 16 and 5) sum to the 25. No `event_id` is given twice; the rows are in (event_date, event_id) order. Each row's UTC time is its local time plus 4 hours (EDT) or 5 (CDT).
- Each scram against `nrc_reactor_status` (the morning's power, read here): Watts Bar 2, Prairie Island 1, Monticello, Braidwood 1 and Hatch 1 at 100 that morning, Susquehanna 1 at 96, Waterford 3 at 91; all seven at 0 the next morning. Session 2043's report has the same table; Waterford 3 reported 75 percent before its trip.

## What it does not hold

- August 2025 to 12 October 2026: the raw file stopped and the pages read began on 13 October 2026. The code reads only the index of the year `--year` names (the current year by default), so 2025's pages are reached only with `--year 2025`; session 2043's report, which first said a run a day would reach two years back, now says so.
- Reports other than power reactors, and the event text.
- Megawatts: power in percent only.
- The raw file's reports were notified in June and July 2025, of events from May to July (the docstring, corrected by session 2052, says both).
