# Session 93 report: the network, version 3 (and the branch cleanup you asked for)

**Built, on `wip/093-network-v3`, nothing deployed.** Version 3 of the network is the review page `/network/v3`: the same network with the same look, and the four additions you asked for, each tested and each checked in a real browser. The live page `/network` is as it was: the older browser test of it (session 68) still passes without a change.

## The branch cleanup (your instruction during session 92), done first

Every remote `wip/` and `task/` branch was checked against `origin/main` before anything was deleted, and each branch to delete was checked a second time in the command that deleted it. Deleting a remote branch is not a deploy; nothing was built.

**Deleted, 18: every commit of each is on main.**

| Branch | Its tip | Branch | Its tip |
|---|---|---|---|
| `wip/066-battery-game-v4` | `4165908` | `wip/080-shoulder-worst` | `c5eb595` |
| `wip/071-presend` | `307cbd2` | `wip/081-eqr-scope` | `8b13b57` |
| `wip/072-finish` | `5477b4d` | `wip/082-land` | `355cdeb` |
| `wip/073-caiso-break` | `acfbc77` | `wip/083-contracts` | `8e580cc` |
| `wip/074-fleet-limited` | `ad7e728` | `wip/085-reserve-prices` | `37bffc6` |
| `wip/075-shoulder` | `4ccd8ac` | `wip/086-battery-grids` | `5472821` |
| `wip/077-housekeeping` | `658ddc2` | `wip/087-storage-owners` | `87f7ce0` |
| `wip/078-california` | `e79199b` | `wip/088-battery-customer` | `01f8acb` |
| `wip/079-called` | `33dfd23` | `wip/089-findings` | `ef5a620` |

**Kept, 4 then and 5 now: each holds commits that are not on main.**

| Branch | Commits not on main | What they hold |
|---|---|---|
| `wip/076-land` | 1 | Session 76's report. The file it adds is identical, line for line, to the copy main already has, so nothing would be lost by deleting it; but the commit itself is not on main, and your rule is the commits. To delete it: `git push origin --delete wip/076-land` |
| `wip/090-fixes` | 1 | Session 90's report and the 25-page snapshot script |
| `wip/091-alerts` | 4 | Session 91: the alerts and the allowlist |
| `wip/092-ask-ercot` | 6 | Session 92: Ask ERCOT |
| `wip/093-network-v3` | this session | pushed after the cleanup |

No `task/` branch existed (the workflow deletes each when it merges). Two things to know. **The emails' links to the reports of sessions 82 to 89 pointed at their `wip/` branches** and now answer "not found"; the same reports are on main, under `archive/sessions/`. And **tonight's branches are a chain**: each of `wip/091`, `092` and `093` contains the one before, so `wip/090-fixes`, `091-alerts` and `092-ask-ercot` hold nothing that `wip/093-network-v3` does not. I kept them because their commits are not on main; if previews are what fills Vercel, deleting those three loses nothing: `git push origin --delete wip/090-fixes wip/091-alerts wip/092-ask-ercot`. From here on I delete a branch's remote when it has been merged to main (none will be tonight: sessions 91 to 101 merge nothing).

## To make version 3 live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's pushes.

# 1. AS A PAGE IN REVIEW (/network/v3). A push to a task branch redeploys the site; /network does not change:
git fetch origin && git checkout wip/093-network-v3 && git merge origin/main
python -m unittest tests.test_session93                                   # read its exit code
cd site && node scripts/snapshot-live.mjs take before-093 && cd ..
git push origin wip/093-network-v3:task/093-network-v3
cd site && node scripts/snapshot-live.mjs take after-093 && node scripts/snapshot-live.mjs compare before-093 after-093

# 2. AS THE LIVE PAGE, when you have used it. Two edits, then the same push with its snapshots:
#    site/app/network/page.tsx:   <Network snap={snap} supply={supply} live={extras} v3={{ index }} />
#                                 with, at the top:  import indexJson from "@/public/network/daily_index.json";
#                                                    const index = indexJson as unknown as DailyIndex;
#    and move the three folds of site/app/network/v3/page.tsx under the live page's own; then delete app/network/v3/
#    and its line in site/lib/release.ts. This changes a live page: after the freeze.

# 3. THE REPLAY'S FILES are built by hand, not by the daily run. To carry the year so far forward:
python warehouse/derived/network_daily.py              # all years, about a minute; or --years 2026
#    then commit site/public/network/daily_*.json. To put it in the daily run: one line after grid_network in
#    warehouse/run_daily.sh.
```

**Read these three first:**

1. **The live page was not changed, and I can show it.** Everything new in the component is behind one prop, `v3`, which `/network` does not pass. In the browser check `/network` has no date picker, no Prices switch, no "Play the year" and no trace; it writes nothing to its address; and session 68's own browser test of it passes, every assertion, on this build. The page's three reads moved to a shared file, word for word, so that both pages read the same things the same way.
2. **A replayed day is thinner than a live hour, and the page says where.** EIA's daily history gives each pair's MWh by day. It gives no demand by day (so a day's net imports come in MW with no share of demand), no batteries, and prices only where the warehouse's history holds them: ERCOT from 2019, the other five from September 2024, PJM never. On 15 February 2021 the replay shows one price ring; on 15 July 2025, six.
3. **The replay leaves out 1,072 pair-days as days no tie can carry**, by the rule the monthly supply table already uses (further than 10 median absolute deviations and at least 500 MWh from the pair's own median). Without it one such day sets the scale of a whole year and every other link becomes a hair. The count is in each year's file and printed on the page.

Energy Research Warehouse (ERW), session 93, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 08:04 to about 08:35 UTC, unattended. **Model spend: USD 0.00.** No pull, no table, no model call, no force push, no deploy. The data lock was not taken: the replay's files are written to the site's folder, not to `warehouse/output`.

## The four additions

### a. Replay any day since 2019

`warehouse/derived/network_daily.py` reads `eia930_daily_interchange` (945,130 rows) and writes one file per year to `site/public/network/`, in the shape the network already draws, a frame per day:

| Year | Days | Pairs | Pair-days not reported | Screened | Grids with a price | Size |
|---|---|---|---|---|---|---|
| 2019 | 365 | 144 | 144 | 190 | ERCOT | 356 kB |
| 2020 | 366 | 144 | 373 | 171 | ERCOT | 356 kB |
| 2021 | 365 | 144 | 3 | 106 | ERCOT | 356 kB |
| 2022 | 365 | 144 | 173 | 151 | ERCOT | 358 kB |
| 2023 | 365 | 144 | 314 | 38 | ERCOT | 356 kB |
| 2024 | 366 | 145 | 390 | 25 | 6 | 367 kB |
| 2025 | 365 | 149 | 8,585 | 174 | 6 | 365 kB |
| 2026, to 30 September | 273 | 158 | 2,225 | 217 | 6 | 294 kB |

A flow is the day's MWh over the day's hours (23 or 25 on the two days the clocks change): its average MW. Each pair is counted once by the network's own rule. Nine balancing authorities of those years have no place in today's network and are named, not drawn.

On the page: a date picker beside the Watch buttons shows a day, and "Play the year" plays the year's days, about five a second. The 2025 and 2026 counts of pair-days not reported are high because pairs that began reporting in 2025 are blank for the days before they began.

### b. The address holds the view

`?view=day&t=2021-02-15&grid=CISO&prices=1&trace=1`. The view, the moment (a day, or an hour of a story or of the live week), the grid and the three switches. Only what differs from the page as it opens is written, so the plain page keeps a bare address. Opening an address restores the view without playing it. An hour that has left the rolling week cannot be shown: the page says so and shows the newest. Anything it does not understand is ignored.

### c. Prices

Off by default. On: a second ring, outside the batteries' ring, on each grid with a public hub price held for the moment; its weight follows the price (the square root of its share of the period's highest, so one scarcity hour does not turn the rest into hairs). The panel already showed the hub price; with the switch on it adds the lowest and highest of the period shown. On 15 February 2021 the panel reads ERCOT's day at USD 6,704.67 per MWh, the file's value.

**Decision:** the panel's "Hub price" line stays whether the switch is on or off, as on the live page today. Your words were "adding the hub price to the panel"; it is already there, and taking it away when the switch is off would have removed something the live page shows.

### d. Trace the power

A button in the panel. For the grid selected, over the period shown: its suppliers (the neighbours with a positive net flow into it), largest first, with MWh and the share of what all of them supplied; and under each, its own suppliers over the same period, the four largest. For California over 2021: Bonneville 21.05 percent, Los Angeles 20.58, Salt River 19.83, Nevada Power 15.09, Arizona Public Service 10.94, and four more; the shares sum to 100. Under the list: "These are physical flows over the ties, as each balancing authority reported them: not contracts, and not where the power was generated. A supplier's own suppliers are its net inflows over the same period; nothing says their power is the power passed on."

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session93.py` | 14 tests pass. The builder on rows made for the test: the pair rule, the other side's report with its sign flipped, a screened day left blank, a 23-hour day, a price only for a complete day. The files as built: every array as long as its year, pairs in code order and in today's network, no PJM price, a frame equal to the table's row for three pairs on 15 February 2021. In Node: the address there and back, and what it ignores; a day held to the replay's range; the hours of four days; the ring's weight; the trace on a small network whose answer is known. The live page passes no `v3`; everything new is behind the prop; the page's reads moved without a change |
| `site/scripts/check-network-v3.mjs`, a real browser (Edge, software 3D) | 26 checks pass: the page opens as the live week with a bare address; **a** a day of 2021 loads, a frame per day, the panel's net imports equal the file's arithmetic (886 MW), the year plays and the day moves on; **c** no ring by default, one ring on 15 February 2021 and six on 15 July 2025, counted in the 3D scene itself, the panel's price equal to the file's, PJM without one; **d** the trace closed until asked for, California's nine suppliers in the model's order with the model's shares, each supplier's own suppliers, never California itself, the sentence about physical flows; **b** the address holds all of it, the same address opens the same view not playing, a story's hour and switch are restored, a nonsense address opens the default; and `/network` has none of it |
| `site/scripts/test-network.mjs` (session 68, unchanged) on `/network` | every assertion passes |
| Site: types, build, route check | exit 0 each; no statement cancelled in the build |
| `check-values.mjs` | exit 0: 7,454 of 7,485 values match; the other 31 are latest prices a newer interval replaced during the run, counted as late, not wrong |
| The whole suite, here | 658 tests; one failure, old and known (`test_session49`) |
| A screenshot of version 3 with prices on | looked at: the same light network, the rings thin circles around six grids, the panel beside it |

## Errors and decisions

- **Decision: a review page, not a change to the live page.** You asked for no change to how a live page behaves and for every new page to be in review. Version 3 is the live component with a prop, so making it live is a one-line change, not a second implementation to keep in step.
- **Decision: static files, one per year, in the site.** The daily history is not in the site's database (945,130 rows). A year is 360 kB and loads when its first day is asked for; nothing is read from the database for the replay. It adds 2.8 MB to the repository.
- **Decision: the screen.** Above, "Read first", 3.
- **Decision: the trace is over the period shown, not the moment.** One hour's suppliers are already in the panel ("Who is supplying it"). Over a period the list is stable enough to rank.
- **Error, mine:** my first scene check looked for the network's frame by a selector that found the site's wordmark; the check failed, not the page.

## For Samuel

1. **The three branches that are one chain** (the cleanup, above): your call whether to delete them now.
2. **Demand by day.** The replay's weakest point is that a day has no demand, so no share. EIA publishes daily demand by balancing authority in the same API as the daily interchange; it would be a pull to approve (public domain, perhaps 200,000 rows for the seven ISOs since 2019).
3. **The price history of the other five grids begins in September 2024.** Before that the replay has ERCOT's ring only.
