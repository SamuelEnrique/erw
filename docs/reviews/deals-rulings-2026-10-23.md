# The deal tracker's rulings, in plain words: 23 October 2026

Energy Research Warehouse (ERW), session 832 (chain `queue/done/080-night-23-october-portable-landing-deals-.md`, portable-laptop). Every item of this chain that waits for the owner: one a line, what the choice is, what each answer changes, and the session's recommendation with its reason. No session decided any of them. The reviews are `deals-public-rows-2026-10-23.md`, `deals-gaps-2026-10-23.md`, `datacenters-public-rows-2026-10-23.md` and `deals-path.md`; the method is `docs/methods/energy_deals.md`, "What is shown and what is held".

## The rows

1. **The rule for a shown deal: one public evidence row, or every story public** (sessions 821, 822). The chain's rule shows a deal when at least one of its evidence rows comes from a publisher whose terms read as public, with every column drawn: 16 of 505 today. The stricter rule (session 441's, every story of the deal public) shows 11. The 5 that differ are deals a held outlet also reported, whose figures the model read from every story of the cluster (Vistra's loan, Amazon and Constellation, Project Star, the Netherlands' FEED studies, Amazon and AEP). Recommendation: keep the chain's rule and draw every column; the figure is a fact the public outlet also reports, and the row names only that outlet. If the owner prefers the stricter rule, one line of `public_rows.py` (the sort's `public` test to `all`) changes it.
2. **Energy-Storage.news and Electrek, not read** (session 821). Reading their terms settles 3 unsettled deals (EDP and Zelestra's PPAs; Geely and NIO; ESR and Aquila). A request, which the chain does not make. Recommendation: read both in the next licenses sweep on the data machine.
3. **Who writes `site/data/deals_public.json`** (session 822). The file is as of the extraction it was run on; `check-values` fails the counts once the live table holds more rows than the file counts (the deals tab then shows the file's rows under a failing check, and the gate fails). Recommendation: the data machine's daily run writes the file after the extraction (`warehouse/deals/public_rows.py --json site/data/deals_public.json` and `--datacenters site/data/datacenters_public.json`), committed with the day's metadata, so the shown rows follow the table. Until then a code session regenerates it by hand.
4. **An operator's own site list as a public source** (session 827; session 441's variant B). The nine datacenter operators' location pages are each company's own words; `docs/licenses.md` gives each the verdict "needs written permission" from its terms sentence. Were they ruled public, 275 of 426 rows of `datacenter_facilities` (15 with MW, 4,799 MW) would be shown; nothing of `datacenter_projects` moves. Recommendation: no change without a reading of each page's terms for the specific use (a list of a company's own sites, restated); a letter to the nine is the licenses file's standing item.

## The filed terms

5. **The EQR tables' flag** (sessions 824, 825). `ferc_eqr_contracts` and its derived tables are internal by the ERW's own record because FERC's page has not been read for the Electric Quarterly Reports. The join of the deals to the filed contracts is done (`warehouse/deals/eqr_join.py`); the panel on a shown row shows the count and draws the filed product, rate, quantity, delivery point and dates as "license needed". Recommendation: read FERC's terms page for the EQR (a federal agency's data, likely public domain, as EIA's and FERC's eLibrary are read) and, if it allows, flag the tables public and let the panel draw the terms. The EQR is the one source for a deal's filed price structure, settlement point and dates (`deals-gaps-2026-10-23.md`).
6. **A press-release feed for the deals' parties** (session 824). The companies' own announcements would give the size, the term and often the price structure the news omits. A pull, each newsroom's terms read first. Recommendation: yes, for the twenty parties the deals name most, on the data machine, as a news feed of the companies' own pages (session 803's rule on a source's words still holds for what the Digest reprints).

## The gates this chain met

7. **A past issue's figure the warehouse revised** (session 827). The Digests of 20 and 21 October print WTI at Cushing for 14 October as 101.91; the live set and the warehouse's archive hold 96.34 now. `check-values` and `check_digest.py` fail on it, and the landing gate fails for every branch while `/digest/2026-10-21` is in its page list (33 days). Recommendation: say on the two pages, in one line, that EIA's figure for the day was revised after the issue was written, and have the checks read a revision as a note, not a failure (a stored issue is a record; the rulings file's item 8 holds the same principle for the Senghenydd fact).
8. **The worker and the next file** (session 823). The chain's rule writes the next file first; the worker took it the moment it was pushed and ran sessions 834 to 841 and then 842 onward beside this chain, against the rule of one session a machine, with nothing of this chain landed to read. Recommendation: the worker's registration starts it at night only (`scripts/register_*.ps1`), or the chain writes the next file at its end (session 833) and not at its start.
9. **The probe's limit against a slow database** (session 820). The gate's probe failed at 3.5 to 4.6 seconds four times tonight; a retry loop passed it. Recommendation: the gate tries the probe three times a minute apart before it fails.
10. **`test_session705` on a machine without `interconnection_durations`** (session 822). The test falls back to Berkeley Lab's file and fails where the committed `connect.json` was built from the data machine's table. Recommendation: the test skips when the table is not on the machine (the old laptop's test; its session 718).

## State after session 2104 (23 October 2026, about 19:20 UTC)

Session 2104 of chain 084 (`queue/done/084-day-23-october-portable-deals-4.md`), read from the owner's answers wherever he wrote them (no `docs/state/rulings_*.md` newer than 11 October; no reply in a report; `license_status.csv`, `license_verdicts.csv` and `docs/licenses.md` unchanged for these publishers since 10:00 UTC) and from this chain's work. No item is decided by the session.

| Item | State | Note |
|---|---|---|
| 1, the rule for a shown deal | open | the chain's rule stands on `wip/833-deals`; 16 shown of 514 after session 2101 |
| 2, Energy-Storage.news and Electrek | open | 4 unsettled deals now (session 2101: SECI and ACME Solar, 23 October, joined the three) |
| 3, who writes the two files | open; done by hand once | session 2101 regenerated both from the 23 October extraction on `wip/833-deals` (16 shown, 494 held, 4 unsettled; 154 projects); the daily run still does not write them |
| 4, an operator's own site list | open | nothing changed |
| 5, the EQR tables' flag | open | nothing changed |
| 6, a press-release feed | open | nothing changed |
| 7, a past issue's revised figure | open | the two issues still print 101.91; the checks still fail on `/digest/2026-10-21`; every landing from this machine waits on it (sessions 1200, 2100) |
| 8, the worker and the next file | answered in practice | chains 083 and 084 write the next file at the end, not the start; the worker's registration is unchanged |
| 9, the probe's limit | open | `scripts/` is not this chain's; not changed |
| 10, `test_session705` without the table | done before this chain | session 718's test, on main, looks for `interconnection_durations.csv` in `runs/archive_restore` and `warehouse/output` of this checkout and the main one, falls back to Berkeley Lab's file and skips when neither is on the machine; it passes on this machine as it stands (5 passed, session 2104), so no branch was cut |

New since session 832, needing no ruling and listed for the desktop's data chain: `docs/reviews/datacenters-power-side-2026-10-23.md` (session 2102), two 1,400 MW ERCOT queue rows owned by data-center LLCs that the derived table's pattern misses because it reads the name and fuel fields only.
