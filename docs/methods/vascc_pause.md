# Virginia SCC pulls are paused (10 October 2026)

Energy Research Warehouse (ERW). Samuel's ruling of 9 October 2026 (the chain prompt of 9 October, session 172 part D, on what session 171 read): **every request of the Virginia State Corporation Commission's own servers is paused, pending the commission's written permission or a person's ruling.** Every row held from the commission and every page stays exactly as it is. Nothing is deleted.

## Why

The commission's robots file, `https://www.scc.virginia.gov/robots.txt`, read by session 171 at 07:44:27 UTC on 9 October 2026 (one request, 707 bytes, HTTP 200; saved as `warehouse/raw/large_load_waits/vascc/20261009074426_robots.txt`, sha256 `33f96f5c9080365c333c66b98064d269cff79840a057c3964bdb2cf5879a7338`, on the branch of session 171), names six agents it allows and ends, word for word:

> User-agent: *
> Disallow: /

Every path, for every agent not named. The ERW is none of the named agents. Session 171 stopped there by its own rule and fetched nothing more. Until then the policy monitor's daily refresh (session 157) had asked the docket search's case list and a case's document list on the daily schedule, and sessions 151, 154 and 157 had read filings from the docket search. The robots file as read forbids those requests too.

The commission's Accessibility and Web Policy (`https://www.scc.virginia.gov/accessibility-and-web-policy/`, read by session 157 on 8 October 2026) speaks of fair use and attribution ("Permission is granted to make fair use of the contents of the SCC website.", "Attribution of the source of the information is encouraged."), not of automated requests. The robots file does, and it governs the request.

## What is paused

One list holds the pause: `warehouse/metadata/paused_sources.csv`, one row per publisher (scope `vascc`), with the date, the reason, the terms quoted, who ruled, and what it waits for. Every connector that requests the commission asks `iso_prices.paused("vascc")` first, and since session 172 `iso_prices.paused_host()` refuses the host itself whatever the caller, so no path reaches `scc.virginia.gov` while the row is there.

| Pull | Where it ran | What it wrote | Now |
|---|---|---|---|
| The docket search's case list by caption and each held case's document list | the daily run (`policy_monitor_refresh.py`, a soft step) | new rows of `large_load_rules_internal` for Virginia's dockets | not requested: the step records "Paused since 2026-10-10" for `vascc` and asks the other regulators as before |
| Filings read from the docket search | by hand (sessions 151, 154, 157) | rows of `large_load_rules`, `large_load_rules_internal`, `large_load_statements` | no further reading; the rows held stay |
| Dominion's large-load queue filings (case PUR-2026-00011) | session 171's Virginia stage of the waits connector (branch `wip/171-virginia`) | nothing: it stopped after the robots file | stays stopped; the stage also reads the pause file |

Not paused: Dominion's documents already held and quoted on `/cost-of-power` under PJM (seven stated timelines, each a link to the commission's or PJM's own page). A visitor's click on a link-out is not a request of ours. The saved lists and documents under `warehouse/raw/` stay and may be read again without a request.

## What the pause waits for

`docs/reviews/scc-permission-email.md` is a short draft asking the commission for permission to read docket documents programmatically for an academic research project. Samuel sends it himself. If the commission grants it, a person deletes the row of `paused_sources.csv` and records the permission (its date, its words, who gave it) in this note. If it refuses, the alternative stands: link-outs to the docket, or filings placed by hand under `warehouse/raw/large_load_waits/vascc/` for a session to read without a request.

## To lift the pause

Delete the `vascc` row of `warehouse/metadata/paused_sources.csv` and record why here. Nothing else needs to change: the refresh step and the waits connector read the file on each run.
