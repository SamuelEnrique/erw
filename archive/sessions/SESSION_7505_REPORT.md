# Session 7505 report: `/cost-of-power/battery/awards` at the done line (chain 304, part A)

16 November 2026, unattended, on samueloldlaptop (code role). Worktree `erw-7505`, branch `wip/7505-battery-awards`,
not pushed. Model spend USD 0. No table written, nothing loaded, nothing published. The page stays in review.

## At the top

- **No figure of the page is wrong on the rows it was computed on.** 307 of 307 figures recomputed inside half the
  page's last shown digit; the two monthly tables behind them equal ERCOT's disclosure rows in 297 of 297 rows.
- **One thing the page said wrong, fixed:** the last part of the real-time section called 21 days of node prices "one
  week" three times, beside its own "Over the 21 whole days held" (faults file, row 1).
- **Not seen from here:** the worktree has no key, so the rows the built page reads in the live set were not read.
  The figures are those of the tables on this machine, whose three monthly tables stop at 5 August 2026 while their
  own inputs reach 27 and 29 August (row 4, one data request).
- **The disclosure is no longer pulled** (the owner's ruling 2 of 6 November 2026: ERCOT's robots file disallows
  `/misapp` and `/misdownload`). The tool's newest month stays August 2026, partial. The page does not say so (row 5).
- A tolerance was widened once and is named in the script: a month's dollar sum agrees with the table inside three
  cents (the first run used half a cent and 9 of 135 dollar sums stood 0.6 to 1.3 cents off, on sums of USD 0.7 to
  14.6 million; every figure per MW, which is what the page reads, agreed to the fourth decimal on both runs).

## The five parts

- **Method note:** `docs/methods/battery_awards.md` (new; no note for the tool existed under another name). Every
  view, each figure's table and rule, the 15 choices, what the tool does not hold. It points to the five tables'
  notes and repeats none. Two of those notes got a dated section each (`ercot_storage_dam_awards.md`: a zero is not
  an award, and where the days stop; `ercot_storage_dam_offers.md`: two sentences that no longer hold).
- **Replication:** `replication/battery_awards/replicate.py`, standard library, written from the notes. As printed:
  - `The page: 307 of 307 figures within half the page's last shown digit, 0 named, 0 failed`
  - `The file battery_awards_beside.json: 24 of 24 figures within half the file's last digit, 0 named, 0 failed`
  - `The monthly tables from ERCOT's disclosure: 297 of 297 rows agree, 9 months (2025-12 to 2026-08), 0 differ`
  - The third line is every month of both monthly tables (not a sample of three), from `ercot_dam_esr_awards`
    (2,026,149 rows), `ercot_sced_esr_hourly` (1,637,727 rows) and the hub's 15-minute real-time prices. It includes
    the real-time deviations at the hub price, recomputed interval by interval.
  - The page's side is `site/scripts/battery-awards-figures.mjs`: the page's own library on the same rows, and the
    offers and real-time sections drawn to HTML, where each of their 217 figures was found. `page.tsx` is an async
    server component and does not draw; its cells are written with the same library calls.
  - `monthly_rows.csv`: the 1,699 public rows the page reads, so `python replication/battery_awards/replicate.py`
    runs on any copy. `page_figures.json`, `page_figures.csv` (331 rows), `source_rows.csv` (297 rows).
  - `replicate.do`: five headline figures, expected values at its top. Not run (no Stata on this machine).
- **Cross-check:** eight rows in the note, section 5; the table is under "For the pack".
- **Decisions block:** `site/app/cost-of-power/battery/awards/Decisions.tsx`, mounted at the foot of the page. 15
  choices; each one's default, source and session in a hover tip; no grey text. The page has no input, so none is
  editable, and the note says so.
- **Faults:** `docs/reviews/battery-awards-faults-2026-11-16.md`, 9 rows: 1 site fault fixed, 2 notes completed, 1 for
  the data machine, 5 rulings.

## Tests

Each file in its own process, one at a time: `.venv\Scripts\python.exe -m pytest -q tests\<file>.py` with
`ERW_SPEND_CAP_USD=0`; the node scripts with `node --import ./scripts/tsx-register.mjs scripts/<file>.mjs` in `site`.

| File | Result |
|---|---|
| `tests/test_session7505_battery_awards.py` (new) | 12 passed |
| `site/scripts/test-battery-awards-render.mjs` (new) | 25 of 25 passed |
| `site/scripts/battery-awards-figures.mjs` (new, on the tables of this machine) | exit 0: 307 figures, 217 of 217 found in the drawn sections |
| `tests/test_session115_page.py` | 12 passed, 1 skipped |
| `tests/test_session116_page.py` | 20 passed, 2 skipped |
| `tests/test_session120_page.py` | 15 passed, 2 skipped |
| `tests/test_session120.py` | 30 passed, 3 skipped |
| `tests/test_session178.py` | 30 passed, 4 skipped |
| `tests/test_session241a.py` | 17 passed, 199 subtests |
| `tests/test_session408.py` | 7 passed |
| `tests/test_session142.py`, `147`, `158`, `160` (they sweep the method notes) | 42, 65, 58 and 40 passed |
| `site/scripts/test-usage.mjs` | 16 passed |
| `tsc` with the site's own settings on the page's four files and all they import (a scratch project file, removed after) | exit 0, no error |

The skips are tests that read a warehouse table, which the worktree does not hold. No failure in any file.

No site build, no full suite, no landing gate, no `check-values` or `check-routes` (they need the built or live site).

## What to review

`https://erw-flame.vercel.app/cost-of-power/battery/awards` (in review; after the branch lands).

1. Scroll to the last section, "The real-time side", and its last heading. With the table as this machine holds it,
   it reads "What the hub price misses: 21 real days at the batteries' own nodes", then "the 21 whole days of node
   prices kept from ERCOT's public list, which holds seven days at a time, from 28 September 2026, at the 293
   settlement points", and the last paragraph begins "It is 21 days of one autumn." No sentence says "one week".
2. Scroll to the foot, under the source line. A closed fold: "Decisions on this page (15): each choice that moves a
   figure, with its default and its source". Open it: 15 lines. Hover the small "i" after the second line ("Per kW is
   per kW of the fleet's MW"): "Default: The highest limit of the month, every resource. July 2026: 21,365 MW. The
   EIA's monthly inventory lists 18,070 MW of batteries operating in ERCOT that month." then "Source:" and "Made in:".
3. Everything else is as it was: the lead "What this is not", the chart, "By month", "By year", "Why the two differ",
   the offers section and its three parts (9.70, 14.53, -0.62 of a gap of 23.61).

## For the pack

**What Samuel signs.** That the page's figures are ERCOT's disclosed day-ahead awards and real-time output of every
storage resource, valued as the method note says, and that each can be recomputed from ERCOT's rows: July 2026, 332
resources and 21,365 MW, USD 0.68 per kW awarded day-ahead; January to July 2026, USD 6.53 per kW awarded against the
model's 30.14 (22 percent); February to July 2026, day-ahead awards 4.17 plus real-time deviations at the hub price
3.00, together 7.17 against the model's 18.81. And that it is not what any battery earned.

**The five choices that matter most.**

| Choice | Default | Source |
|---|---|---|
| Per kW of what | The sum of each resource's highest High Sustained Limit in the month, every resource in the file (21,365 MW in July 2026) | ERCOT, 60-Day DAM Disclosure (NP3-966-ER); the EIA's 18,070 MW would make each figure 18 percent higher |
| The price of real-time energy | The hub average, each 15 minutes, not the battery's node | ERCOT Nodal Protocols 6.6.3.1 settle at the node; the node price of a disclosed day is not public |
| The model beside the awards | One 2-hour battery, day-ahead schedule, hub average, whole months only | `battery_stack.md`; the market monitor's 17,000 MW and 31,500 MWh, about 1.9 hours |
| "Never offered" | The model's average on the 32.2 percent of limit-hours with no day-ahead offer: an allocation | `ercot_storage_dam_offers.md`, "The gap in three parts" |
| Months | Central months; nothing filled; a partial month never scaled or set beside the model | ERCOT's Delivery Date |

**The cross-check.**

| Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|
| Fleet, December 2025: 16,392 MW (January 2026: 17,180) | "more than 17,000 MW and 31,500 MWh by the end of 2025" | Potomac Economics, 2025 State of the Market Report for ERCOT, June 2026, page ii | at least -608 MW | Highest day-ahead limit in the days held against capacity installed at the year's end |
| Fleet, July 2026: 21,365 MW | 18,070 MW operating | EIA, Form EIA-860M (the warehouse's `storage_buildout_monthly`) | +3,296 MW, 18 percent | ERCOT lists a resource from the day it can be dispatched, testing included; the EIA once its owner reports it operating |
| Energy offered at USD 100 or less: 8.0 percent of day-ahead curves, January to July 2026 | "55% of energy offers were priced between $0-100 per MWh" in 2025 | The same report, page 24 | -47 points | Theirs is real-time offers in 2025, ours day-ahead curves in 2026; the fleet prices most power out of the day-ahead market |
| Day-ahead ancillary share of the two markets: 20 percent, February to July 2026 | 24 percent from services in June 2025 | Modo Energy, 19 May 2026 (from the battery tool's cross-check) | -4 points | Another period; ours leaves out real-time ancillary money |
| The same, 20 percent by dollars | "8.1 GW of battery capacity, half of which was primarily used for arbitrage" | EIA, Today in Energy, 22 September 2025 | none computed | Capacity by stated primary use against dollars |
| Revenue per kW: 7.17 over February to July 2026 | None for these months; "falling by almost 37% from 2024"; Modo's USD 55 per kW in 2024 | The report, page 22; Modo Energy, 19 March 2025 | none computed | Six months, hub price, no real-time ancillary money, every MW in the file |
| Awarded share of the fleet's own limit-hours: Regulation Up 2.6 percent, Down 2.1, Responsive Reserve 6.9 | "ESRs provided 94%, 86%, and 51% of Reg-Up, Reg-Down, and RRS" in 2025 | The report, page 42 | none computed | A share of what ERCOT bought against a share of the fleet; the plan quantities for these months are not held |
| The gap's three parts, the node spread, the 7.0 percent of hours | Nothing published stands against them | | | The ERW's own arithmetic on ERCOT's rows |

**Stata.** `cd replication/battery_awards` then `do replicate.do`. Not run here (no Stata on this machine). It should
print these five lines, the spacing of the numbers aside:

1. `1. July 2026, awarded day-ahead, USD per kW: 0.6815`
2. `2. 2026, 7 months held whole: awarded 6.5282, the model 30.1379, share 21.66 percent`
3. `3. the gap 23.6097: never offered 9.7041, offered and not awarded 14.5278, price -0.6222`
4. `4. day-ahead awards 4.1713, real-time deviations 2.9974, together 7.1688, the model 18.8081`
5. `5. resource-hours with a day-ahead energy award: 7.0 percent (127,958 of 1,833,357)`

**The rulings, in plain words** (each with the default taken): see "For Samuel's ruling".

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 11:25 | 7505 | `ercot_storage_dam_awards_monthly`, `ercot_storage_dam_offers_monthly`, `ercot_storage_rt_monthly` | On samueloldlaptop these three stop at operating day 5 August 2026 (built 5 October), while `ercot_dam_esr_awards` holds 267 days to 29 August and `ercot_sced_esr_hourly` 208 days to 27 August. Say which days the data machine's copies and the live set hold; if they also stop early, rebuild the three from the rows held (no request to ERCOT is needed) and load them, so August 2026 holds 27 or 29 of 31 days. Then `site/scripts/battery-awards-figures.mjs` and `replication/battery_awards/replicate.py --write` are run again on the new rows. | `docs/reviews/battery-awards-faults-2026-11-16.md`, row 4 | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 11:25 | 7505 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards` | The foot of the page: the fold "Decisions on this page (15)"; open it; hover, then tab to, the "i" after three lines | 15 lines; each tip opens on hover and on focus with "Default:", "Source:" and "Made in:", stays inside the page at 1280 and at 390 px, and no line of the block is grey | wanted |
| 2026-11-16 11:25 | 7505 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards#real-time` | The last heading of the section and the three sentences under it | With `whole_days` above 7 in the live set: "N real days at the batteries' own nodes" and no "one week" in the part; with 7 or fewer: the words as before. The N equals the "Over the N whole days held" of the same paragraph | wanted |
| 2026-11-16 11:25 | 7505 | `wip/7505-battery-awards` | `https://erw-flame.vercel.app/cost-of-power/battery/awards` | The whole page at 390 px | No sideways scroll of the page with the fold open (the wide tables scroll inside their own frames, as before) | wanted |

## Landing request

- **Head:** the commit of this report on `wip/7505-battery-awards` (the reply gives its hash). Stacked on
  `wip/7500-done-line` (31757a20c).
- **Test files:** `tests/test_session7505_battery_awards.py` and `site/scripts/test-battery-awards-render.mjs` (new),
  with the files under "Tests".
- **What changes:** `site/app/cost-of-power/battery/awards/RealTime.tsx` (the node part's words), `page.tsx` (one
  import, one mount), `Decisions.tsx` (new); two node scripts; the note, two dated sections in two tables' notes, the
  faults file, `replication/battery_awards/`, this report.
- **What does not:** no library (`site/lib/storageawards.ts` and `storagerealtime.ts` are untouched), no shared
  component, no table, no builder, `release.ts`, `check-values.mjs`, the battery page and its files.
- **A snapshot would differ on:** no page a visitor sees (the page is in review, and a visitor is shown the in-review
  page at its address). Behind the review gate: this one page, in the two places under "What to review".

## Needs the key

- None. No step of this tool calls a model, and none was run.

## Decisions made without you

- The tool's note is new (`battery_awards.md`); the tables' notes were extended by a dated section each, not rewritten.
- The note carries no "Tables:" line, so the coverage page keeps linking each table to its own note.
- The replication recomputes every month of the two monthly tables, not three: the files are read once either way.
- The dollar-sum tolerance of three cents (see "At the top"); named in the script, not hidden.
- The public rows the page reads are committed beside the replication (1,699 rows, fleet totals only, no resource
  named), so it runs without the warehouse. The rows by resource and hour are not committed (1.1 GB).
- ERCOT's own storage reports were not requested: its robots file disallows the paths its files are served from, and
  ruling 2 holds. ERCOT's figures stand through its disclosure and its market monitor's report.
- The market monitor's revenue per kW is on a chart axis; it was not read off the picture.
- The decisions block is the tool's own file with the session inside the tip, not the shared `DecisionsBlock`, which
  prints the session in grey and is being edited on another branch.
- Fault 1's words for more than seven days are mine ("N real days", "It is N days of one autumn"); the words for a
  week are unchanged.

## For Samuel's ruling

1. **Say on the page that the disclosure is no longer pulled?** Default: no change; the note says it. The other
   choice: one sentence in the lead giving the last operating day held.
2. **Turn the page's grey notes into hover tips** (the page standard)? Default: left as they are, since it moves
   words three older test files hold and wants a browser. The new block already follows the standard.
3. **A second model column for the 4-hour battery** (the battery page's own default duration)? Default: the 2-hour
   battery stays alone, since the fleet averages about 1.9 hours.
4. **End the offers list's "it is not in these tables" with a link to the real-time section?** Default: unchanged.
5. **Draw the page's figures through the checked-number component** so `check-values` holds them on the built site?
   Default: not done on a machine that cannot build; the replication holds them meanwhile.
6. **Fault 1's new words**, above: keep, or give your own.

## Seen in another tool (one line)

- `site/components/tool/DecisionsBlock.tsx` prints each decision's session as grey text on the battery, generator and
  datacenter pages, which the page standard of 16 November forbids; not touched here.
