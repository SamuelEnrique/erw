# Chain of the night of 23 October 2026: sessions 820 to 833, code machine (personal laptop), unattended: the periodicals landed, then the deal tracker's public rows

machine: portable-laptop

Fourteen sessions for the personal laptop (`portable-laptop`, C:\Users\samen\Documents\erw), written on the owner's instruction on the evening of 22 October. Model: Fable 5.1, high effort (the worker is registered with `-Model claude-fable-5-1`). This machine runs at night only: the chain is sized for about ten hours and stops in the morning (session 833). Two jobs in order. First, the landing that chains 060 and 061 left under "To finish": sessions 801 to 817's periodicals code sits on `wip/818-periodicals` and nothing of it is on main, so tomorrow's Digest is still written by the old code; session 820 lands it. Second, roadmap v4's "first" item behind the license (`docs/reviews/roadmap-v4-draft.md`, tool 6): the deal tracker shows nothing public because `energy_deals` rests on news publishers; the rows whose evidence is a company's own announcement or a regulator's filing can be shown, and the tracker gets its public subset, keyed and traced, with the held rows counted and named as "license needed" in place. Nothing here waits for a ruling: no past issue changes, no license flag changes, no page's default figure moves except where the landing of 801 to 817 is the change the owner already read in `docs/state/review_2026-10-24_portable.md`, nothing is sent or posted, the site stays in review.

Session numbers 820 to 833 are this chain's; 834 to 849 are this machine's for later nights. The old laptop holds 700 to 799, 970 to 999 and 1000 to 1049; the desktop numbers from 850 and skips those. A number found taken is skipped upward inside 820 to 849 and said so.

**The next file is written first.** Session 820 begins by writing `queue/next/081-<slug>.md` for this machine (`machine: portable-laptop`, at most eight sessions numbered 834 upward, for tomorrow night: the open items of this chain's reports and the periodicals rulings the owner has answered by then), commits it alone and pushes it to main before any other work. Session 833 updates it from this chain's results. The worker takes it tomorrow night; this machine does not run in the day.

Read first: `docs/state/review_2026-10-24_portable.md` ("To finish" is session 820's script), `docs/reviews/periodicals-rulings-2026-10-23.md` (19 items; none is decided by a session), `docs/methods/energy_deals.md`, `site/app/deals/` (`Held.tsx`, `Decisions.tsx`, `DealsTable.tsx`, `comparables/`), `warehouse/metadata/license_status.csv` and `docs/licenses.md` (which publishers ask for permission), the evidence table `energy_deals_evidence` (its columns in `coverage.csv` and the method), `docs/brand.md`, `docs/tooling.md`. Files this chain owns: `site/app/deals/`, `site/lib/deals*.ts`, `warehouse/deals/` (readers only; no warehouse write), `docs/methods/energy_deals.md`, `docs/reviews/deals-*.md`, and for session 820 only the landing of `wip/818-periodicals`. It does not touch `site/app/cost-of-power/`, `package/`, `site/app/data/` or any connector.

## Rules for every session

Every python command uses `.venv\Scripts\python.exe`. Precheck first (exit 1: stop). Unattended: never stop to ask, never wait for a time of day; any wait over 20 minutes is stopped and the step done directly or left under "To finish"; reversible choices under "Decisions made without you", irreversible ones under "For Samuel's ruling", undone, one item a line so `/internal/waits` lists it. One Claude Code session on this machine at a time; each in its own git worktree beside the main checkout, on its own `wip/<N>-deals` branch cut from origin/main, removed once landed. THE DATABASE: `python scripts/db_probe.py` before a build; exit 1: code, tests and documents first, probe again at the end; the probe's limit and check-values' timeout as session 818's "To finish" sets them (`CHECK_VALUES_TIMEOUT_MIN=45 CHECK_VALUES_REQUEST_S=120`) when the database is slow. A build over 30 minutes is stopped. `python scripts/buildlock.py acquire <who>` and `release <who>`; `python scripts/duty.py beat` before each build. Landing through the full gate, `python scripts/land_check.py --ref wip/<N>-deals`, snapshot before, push to `task/`, snapshot after, `compare`, every difference listed; no landing between 14:00 and 16:15 UTC (this machine will not be running then; said for completeness), and no change to `warehouse/news/brief.py` or `email_digest.py` lands between 15:00 and 16:00 UTC. No warehouse data written; no web request (the deal rows and their evidence are read from the live set and the archive only). Model spend USD 0 for the chain. Screenshots at 1280 and 390 for every page touched under `docs/brand/review-<N>/`. tokens.css and the shared components only. No em dashes anywhere. Reports as the chain of 20 October's, short bullets, "Read these first", "What to review" with addresses and clicks, checks with their exits, the landing, "Decisions made without you", "For Samuel's ruling".

## Session 820: the next file, then the periodicals landed

Long end 2:30. First the next file (above). Then the "To finish" of `docs/state/review_2026-10-24_portable.md`, command by command, each its own, its exit read: merge origin/main into `wip/818-periodicals`, the probe, `land_check.py --ref wip/818-periodicals --lock-as s820 --port 3820` with the timeouts, the snapshot before, the push to `task/818-periodicals`, the snapshot after once production serves the merge (at most 20 minutes; past that, the compare is left under "To finish" for session 821 and the session goes on), `compare`, `check_digest.py --supabase --then-csv` (131 of 131). Then the "Not landed by this chain" paragraphs of sessions 801 to 811's reports and the "LANDING_PENDING" lines of 814 to 817's replaced by the outcome; the branches `wip/801-periodicals` to `wip/818-periodicals` and `task/818-periodicals` deleted once each is an ancestor of main (`git merge-base --is-ancestor`). If the gate fails: the failure named, the fix made if it is in the periodicals' code and needs no ruling, one more try; else the exact remaining commands under "To finish" and the chain goes on to 821.

## Session 821: the deal rows, sorted by who stands behind them

Long end 2:00. Read every row of `energy_deals` and `energy_deals_evidence` from the live set and the archive: for each deal, the evidence rows and each one's publisher; the publisher's verdict from `license_status.csv` and `docs/licenses.md` (asks for permission; public; not read). Sort the deals into three: shown (at least one evidence row from the company's own announcement, a regulator's or an ISO's filing, a government page, or a publisher whose verdict is public), held (every evidence row rests on a publisher who asks for permission), unsettled (a publisher not read). `docs/reviews/deals-public-rows-2026-10-23.md`: the three counts, the shown rows' list with their public evidence, the top ten publishers behind the held rows. No row's data changes. Land (a document).

## Session 822: the tracker shows its public rows

Long end 2:30. `site/app/deals`: the table draws the shown rows with every column, each row's source line naming the public evidence only (never a held publisher's address or words); the held rows are counted in a line above the table ("N deals rest on publishers whose terms ask for permission; license needed") and drawn as rows with the deal's own name and date only where the name comes from a public filing, else as a count; the unsettled as a count. `Held.tsx` carries the words of `docs/brand.md` section 7. Every figure a check-values key; check-values on the page. Tests on fixtures of five rows of each kind. Land.

## Session 823: the public subset's figures

Long end 2:00. The tracker's summary figures (MW, USD, count by type, by month, by grid) computed over the shown rows only, said so in the hover tip, with the held count beside each; `comparables/` the same; the deals-by-month chart over the shown rows, the shared chart, the held months hatched in the shared style with the tip. Keys; no public figure drawn from a held row. Land.

## Session 824: what a lab's power trader reads here

Long end 2:00. From the two research reports (AG's section 4 and its TL;DR; DR's roles): the fields a power trading lead or an infrastructure-finance lead reads in a deal (counterparties, MW, term, price structure where filed, delivery point or grid, the product: PPA, tolling, hedge, swap, capacity), and whether the tracker holds each. For the shown rows, every held field that a public filing in `energy_deals_evidence` gives is drawn; every field the warehouse does not hold is listed in `docs/reviews/deals-gaps-2026-10-23.md` with the source that would (FERC EQR for the filed terms, the companies' own announcements, ISO filings), for the desktop's data chain. Land.

## Session 825: the FERC EQR rows beside the deals

Long end 2:30. `/contracts` ("Where power contracts are being struck", session 83) reads `ferc_eqr_contracts`, which is internal by the ERW's own record. Join, read only: for each shown deal, the EQR contract rows whose seller and buyer match the deal's parties within the deal's quarter (the party names through `ferc_eqr_buyer_names`); the matches as a panel on the deal's row ("filed terms"), drawn as "license needed" in place while the EQR tables are internal (the figures computed and keyed, the words shown), so that the owner sees the join is done and only his ruling on the EQR tables' flag is missing. The join's precision on twenty deals checked by hand in the report. Land.

## Session 826: the tracker's A and B

Long end 2:00. Two deals picked from the table compare side by side (parties, MW, term, USD, USD per MW, grid, the evidence's publisher), in the battery page's A and B form, no verdict; the pair kept in the address. Keys. Land.

## Session 827: the datacenter tracker's power side, the same way

Long end 2:30. `/datacenters`: the four tables are held whole; the same sort as session 821 for `datacenter_projects` and its evidence (the operators' own announcements and the utilities' and ISOs' filings are public evidence); the shown rows drawn with their power-side fields only (MW requested, the grid, the queue position from `datacenter_queue_positions` where its evidence is an ISO's own list, the utility), the held counted as "license needed" in place. Keys. `docs/reviews/datacenters-public-rows-2026-10-23.md`. Land.

## Session 828: the method notes

Long end 1:30. `docs/methods/energy_deals.md` and `docs/methods/datacenter_facilities.md` gain "What is shown and what is held" with the three sorts' rules, dated, and the decisions block; `/data/methods/` links hold. Land.

## Session 829: 390 pixels, accessibility, links

Long end 1:30. `/deals`, `/deals/comparables`, `/datacenters`, `/contracts` at 390 by 844 and 1280; AccessLint's unattended scan; `check-links.mjs`; mechanical fixes in the shared components. Counts before and after. No figure moves. Land.

## Session 830: the brand pass on the two trackers

Long end 2:00. `/deals` and `/datacenters` restyled to `docs/brand.md`: structure, density and every figure kept; tokens.css and the shared components only; screenshots before and after under `docs/brand/review-830/`. Land.

## Session 831: the investor's path, walked

Long end 2:00. `docs/reviews/deals-path.md`: the questions an infrastructure investor asks of a deal list (from the reports, cited), click by click on `/deals` in the internal view, walked on a build; what the page showed, whether it answered, what broke; fixes that need no ruling made. Screenshots of each step. Land.

## Session 832: the rulings in plain words

Long end 1:00. `docs/reviews/deals-rulings-2026-10-23.md`: every item of this chain that waits for the owner (the EQR tables' flag, the unsettled publishers to read, the held rows' names, the fields to add), one a line, in plain words with a recommendation; and `periodicals-rulings-2026-10-23.md` re-read after the landing, each item's state updated. Push to main (documents).

## Session 833: the note, the next file updated, and the queue

Long end 0:45. `docs/state/review_2026-10-25_portable.md`: one line a session with its branch, every decision made without the owner, every item waiting for him, the landing's outcome. Update `queue/next/081-<slug>.md` from this chain's results, commit and push it to main, say so in the note. Push. Then, if the time on this machine is before 07:00 Pacific, `python scripts/chain_queue.py next` and run the file it takes; otherwise say "CHAIN DONE" and stop without the queue step: the next file stays in `queue/next`, marked for this machine, and the worker takes it the next time the laptop is on.
