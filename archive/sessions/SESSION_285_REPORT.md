# Session 285 report: the tables behind the tracker, deals, policy and events

14 October 2026, 18:43 to about 19:00 UTC, unattended, on lab-desktop (the data machine), the second session of the daytime chain of 14 October. Branch `task/285-tracker-tables`. Model spend USD 0: no model call. Pulls: none (ERCOT's documents were read from the copies this machine's daily run saved at 17:30 UTC; the live set was read with the anon key). Nothing from NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher.

## Read these first

- **Every table /datacenters, /deals, /policy and /events read is on a schedule and at its cadence.** Nothing was refreshed: nothing was behind. The table below has each with its newest row and its schedule.
- **ERCOT's newest large-load reports state none of the figures the table holds, and say why: ERCOT paused approvals to energize data centers and crypto loads of 75 MW or more on 3 August 2026,** after the Governor's directive of that day, until its "Batch Zero" eligibility check is done (TAC, 26 August 2026, "Large Load Issues", `Batch_Zero_Update_TAC_08262026.pptx`). The last report that states "Of the N MW that have received Approval to Energize" and the observed peaks in words is that of 19 June 2026, which is the table's newest. The decks since (TAC LLWG July and August 2026, the CTP and Batch 1 updates, September's LLWG page) are the working group chair's summaries and ERCOT's process updates; their queue figures are pictures. **The tracker page says nothing of the pause.** A ruling (1).
- **The policy page's future dates are printed as filed, and each is in the filing.** 56 dates after today sit inside 33 reads (the timeline, the plain read, what changes: comment deadlines, effective dates, license terms to 2053); 55 are in a quoted evidence span of their read and the 56th in the saved text of the filing. No event date is in the future, here or in the live set (checked with the anon key: 0 rows of `events` dated 15 October or later outside the news index). The page's wording ("as filed") is the code machine's (`site/app/policy`): a ruling (2).
- **The event tables are closed windows by design:** `event_window_daily` holds eight events, each with its baseline years: COVID (2020), CAISO's heat of 2020 and 2022, Uri (2021), Elliott (2022), ERCOT's heat of 2023, the cold of January 2025 and the eastern heat of June 2025, the last window ending 28 June 2025. No event after that is defined; adding one is a method change, not a refresh. A ruling (3).

## The tables, newest row against cadence

| Table | Page | Newest row | Cadence | Verdict | Schedule |
|---|---|---|---|---|---|
| `datacenter_facilities` | /datacenters | snapshot, built 14 Oct 15:36 | daily | fresh | runner, daily |
| `datacenter_projects`, `datacenter_projects_evidence` | /datacenters | evidence to 14 Oct 13:49 | daily | fresh | runner, daily (from the news) |
| `datacenter_operator_sites` | /datacenters | snapshot, 12 Oct | weekly (Mondays) | on cadence | runner, Mondays |
| `ercot_large_load_status` | /datacenters | report of 19 Jun 2026; read again 14 Oct 17:30 | monthly report | at source (above) | this machine, daily (`dm_ercot_large_load`); the runner's monthly job |
| `large_load_public` | /datacenters (public since session 272) | to 30 Sep 2026 | built from research passes | by design: no pass since 8 Oct | none; a pass is a model spend |
| `energy_deals`, `energy_deals_evidence` | /deals | 14 Oct 12:40 and 14:42 | daily | fresh | runner, daily |
| `energy_companies` | /deals | snapshot, 14 Oct 15:35 | daily | fresh | runner, daily |
| `news_stories` | /deals | 14 Oct 15:20 | daily | fresh | runner, daily (43 feeds) |
| `policy_actions` | /policy | 14 Oct | daily | fresh | runner, daily (`policy_sources`) |
| `policy_reads`, `policy_reads_evidence` | /policy | 14 Oct | daily | fresh | runner, daily (`policy_reads`, a model step of the runner's own cap) |
| `large_load_rules`, `large_load_rules_internal` (the policy monitor) | /policy, "What changed this week" | 22 Sep and 7 Oct | docket lists, daily | at source: no new filing found today | runner daily; Oregon on this machine |
| `event_window_daily` | /events | 28 Jun 2025 | closed windows | by design | none |

## ERCOT's newest large-load documents, read

| Meeting | Document | What it states in words |
|---|---|---|
| LLWG, 19 Jun 2026 | `June-19-LLWG-Report.pptx` | the last status update with the three figures: the table's newest rows |
| TAC, 29 Jul 2026 | `TAC LLWG July 2026.pptx` (in `9.-LLWG-Report.zip`) | the chair's summary: "ERCOT Peak Demand for 2026 ~ 92GW. New loads are mostly AI Data Centers"; the queue as a picture |
| LLWG, 21 Aug 2026 | `4.-ERCOT_CTP-and-Batch-1-LLWG-update-20260821_v2.pptx` and five more | not read by the connector (its name rule); ERCOT's process update |
| TAC, 26 Aug 2026 | `Batch_Zero_Update_TAC_08262026.pptx` (in `10.-Large-Load-Issues.zip`) | the pause of 3 August; "Data centers and crypto facilities large load impact through end of 2026: 17 large loads (6,608 MW total peak demand over 5 years)"; "April snapshot had 157 medium data center and crypto loads totaling approximately 8,766 MW" |
| LLWG, 17 Sep 2026 | `LLWG_Update_CTP-and-Batch-Process_20260917.pptx`, QSA results | not read by the connector |

- The connector reads a document whose first page is a status update. These are not, so it is right to write no row; the figures above are written here, with their sentences, and are in no table.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 285"` | 0 | six of six |
| the freshness read (`runs/session284/fresh.py`) | 0 | above |
| the future dates (`runs/session284/policy_future.py`) | 0 | 56 dates: 55 in a span, 1 in the text |
| the live set's `events` after 14 October (anon key) | | 0 rows outside `news_index` |
| the saved ERCOT decks, read by the connector's own `pages_of` (`runs/session284/llis_probe.py`) | 0 | no status update after 19 June |

## Decisions made without you

1. **Nothing was refreshed:** every table was at its cadence or at its source; a pull to show "no change" would only spend requests.
2. **The future dates are left printed as filed.** Holding them would hide deadlines a reader needs; each was checked against its filing.
3. **The connector's name rule was not widened** to the CTP and Batch decks: they are not status updates, and a wider rule would read and drop them every day.
4. **The pause is written here and in the method, not in a table:** the statements table is built from research passes, which are a model spend.

## For Samuel's ruling

1. ERCOT's pause of approvals to energize data centers (3 August 2026): say it on the tracker beside the June figures (the code machine's page), and add the Batch Zero deck's two figures to `large_load_statements` by hand, with their sentences?
2. /policy and /contracts: the words "as filed" beside a future date, as the review of 12 October asked (item 19)?
3. /events: define an event after June 2025 (a 2026 heat or cold spell the warehouse holds whole), so the page has a window from this year?

## Files

- Changed: `docs/methods/ercot_large_load_status.md` (what ERCOT has posted since June).
- New: this report.
- On this machine, not in git: `runs/session284/` (shared with session 284: the probes).

## The landing of session 284, recorded here

- Before `s284-before` 18:27:02 UTC; pushed 18:41:02 (`task/284-board-supply`, `8da94a1f`); check run 116035320563 success 18:48:25 (workflow run 38617229115); merged `78b876d3`; deployed 18:50:24; after `s284-after` 18:50:27; `compare`: 0 differences. Expected: no page is live; the board's files changed behind the in-review page.
