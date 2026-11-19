# Session 8400 report: the evidence behind the 88 rulings that had no recommendation (chain 503, part A)

19 November 2026, samueloldlaptop (code role), unattended. On `main`. Model spend USD 0: no model API was called. **Part A changed nothing:** no page, no default, no branch landed, no table. A recommendation is not a ruling, and no ruling was taken.

## What was done

- **The ground:** the chain file saved as pasted (`a37adf1af`), the resume file `queue/next/530-resume-chain-503.md` (`b447803e2`), the progress file `docs/state/progress_c503.md`. Precheck passed; no freeze; session numbers 8400 to 8599 free.
- **The 88 entries of `docs/reviews/rulings-ranked-2026-11-17.md` that said "no basis to recommend":** each now has a block "Evidence" under it with three parts (published practice, Samuel's own rulings on a like question, the tool's own method note) and a line "Recommendation after the evidence". The first recommendation is left as it was written.
- **How:** five groups looked up side by side (taxes 18 entries, storage 16, prices 16, grid 16, trackers 22), each entry written to its own file and merged into the list in its own order by `runs/c503/merge_evidence.py`, pushed six times while it grew.
- **The sheet for one sitting:** `docs/reviews/rulings-one-sitting-2026-11-19.md`, one line for each of the 129 questions with its link into the ranked list.

## The counts

| | Switch | Keep | No basis to recommend |
|---|---:|---:|---:|
| Before (17 November) | 26 | 15 | 88 |
| The 88, after the evidence | 28 | 33 | 27 |
| The whole list now | 54 | 48 | 27 |

- By group, after the evidence (keep, switch, no basis): taxes 10, 6, 2; storage 2, 6, 8; prices 5, 5, 6; grid 5, 5, 6; trackers 11, 6, 5.
- **What decided most often:** a ruling Samuel had already made on a like question (his rulings of 12, 14, 18, 19 and 24 October and of 6 November, and the page standard), then the tool's own method note where it states the rule, then a publisher's practice where the trusted publishers agree.
- **The defaults list** (`docs/reviews/rulings-defaults-2026-11-17.md`) holds the other 227 questions; one "defaults stand" closes them.

## What to review

- `https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-one-sitting-2026-11-19.md`: read the counts and the three notes at the top; rule "as recommended" for the switch group and the keep group with the numbers he rules otherwise; then the 27 lines of "Samuel's call alone". Each line's link opens its entry in the ranked list, where the `Ruling:` line is.
- `https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-ranked-2026-11-17.md`: under any entry, the block "Evidence (looked up on 19 November 2026)" and "Recommendation after the evidence"; at the foot, "Figures that do not agree" (session 8402) and "Wording corrected on 19 November 2026".

## What the evidence found beside the recommendations

- **Entry 77 gave ICE's fee as the price of either purchase.** PJM's membership is USD 2,500 a year for an associate member and USD 5,000 for a voting member (`docs/licenses_costs.md`); the USD 25,000 to 30,000 is ICE's license. Corrected in the entry.
- **Entry 75's 210 "public rows" are not public by the test of ruling 4 of 6 November:** the license record gives the datacenter operators' own sites as needing written permission.
- **Entry 23 had the direction wrong** (EIA's figures run under the operator's load in the base weeks, not above). Corrected.
- **Entry 94's zones are ERCOT's weather zones**, not load zones. Corrected.
- **Entry 107:** the market monitor prints the fleet's duration itself, 1.83 hours; the awards page's hover says "about 1.9". Not changed here; it is a fault for the page's next session.
- **Entry 98's branch does not cut the day as the board does** (holidays, California's Saturday), **entry 113's branch is 504 px wide at 390 px** (row 362, in work in session 8401), **entry 53's branch gives the Austin zone Oncor's rate**, **entry 119's branch still draws the "By day" share**: each said in its Evidence block or at the foot.
- **A stale address:** Lazard's June 2025 report address, cited 69 times in the repository, answers 404. Nothing changed; the current address is in `runs/c503/notes_storage.md` on this machine.
- **Kansas:** the Property Valuation Division's memorandum gives the rule after the ten exempt years, which the forecast tool says it does not hold.

## Web reads

- Every host's robots file was read before a page was asked. Hosts that refused and were not read: `www.nerc.com` (robots file), `www.ice.com` (terms), `www.puc.texas.gov` (HTTP 402), `www.ferc.gov` (HTTP 403 on the report's page), `www.ncsl.org` (robots file), `www.cdc.gov` (HTTP 403), `www.congress.gov` (robots file), `www.fueleconomy.gov` (refused the connection), `soltax.coopercenter.org` (HTTP 400), EIA's `/survey` path (robots file), `emp.lbl.gov` (HTTP 403). `comptroller.texas.gov` was left alone (the standing record reads its robots file as a refusal).
- Never asked: MISO, the Virginia commission, the Illinois and Ohio docket hosts, EDGAR, ERCOT's `/misapp` and `/misdownload`.
- **A shortfall, being closed:** the rule asks for each host's terms as well as its robots file. The taxes group opened no terms page, and the other groups recorded terms for some hosts only. Session 8403 reads the terms of every host a page was read from and writes which, if any, forbid automated access; an entry that rests on such a host alone goes back to "no basis to recommend". Its result is in the progress file and the chain's last note.

## Needs the key

- Nothing.

## Decisions made without you

- **The evidence blocks were written by five research agents and merged by a script** that refuses a block not in the form (three parts, a recommendation in exactly keep, switch or no basis, no dash).
- **A method note that only describes the present rule was not let decide;** it decided where it states the rule on the very question, calls a figure impossible, or records a ruling.
- **The first recommendation of each entry was left as written,** so ten entries still say "see the foot" for a disagreement that session 8402 has since traced.
- **Session numbers:** 8400 (this), 8401 (the six screenshot faults), 8402 (the twelve figures), 8403 (the terms check), 8410 (the events pages), 8420 (`/demand`), 8430 (`/supply`).

## For Samuel's ruling

- **Berkeley Lab's two addresses.** `emp.lbl.gov` answered HTTP 403; the queue report was read at `eta-publications.lbl.gov`, the address the repository's own method note gives. Default taken: used. If it counts as a second door to a host that refused, entries 20 and 92 go back to "no basis to recommend".
- **Entry 42 (Louisiana) is a license question and reads "switch":** ruling 4 of 6 November on the large-load table is read as deciding the like case (a rate whose only source is a state host that asks permission is held and its cell blank). If that ruling covers the large-load table only, entry 42 is his call alone.
- **Entry 36:** how the Texas Comptroller's robots file is read. It disallows every folder and then allows `/taxes/`; by the standard's longest-match rule the cited pages are allowed, and the standing record reads the file as a refusal. Default taken: the refusal stands, no page asked.
