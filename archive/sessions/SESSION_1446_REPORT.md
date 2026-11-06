# Session 1446 report: the Roundup's five numbers, its opening number and its chart

Energy Research Warehouse (ERW), session 1446 (chain 149's "1443"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 02:24 to 02:30 UTC. Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (reads for the render). Branch `wip/1446-periodicals` over `wip/1445-periodicals`.

## What it did, with commits

- **`885b12af9`** (and `432a5c086`, a test's bound), `warehouse/news/roundup.py`, `email_digest.py`, `score.py`:
  - **The opening number by the brand's tests** (fault 25): `roundup.opening_number(picked, stories)` takes, in order, a benchmark's close a week apart that moved 3 percent or more and that a story of the week names (`brief.price_reason` over the week's clusters); the deal of the week at USD 1 billion or more; the largest datacenter load at 500 MW or more; the top story's structural figure (`picked["story"]`, which main fills from the first of "What mattered"); a benchmark move no story names at 1.5 times the bar; a hub's weekly mean at 10 percent or more, last (a story naming the grid first); the US48 peak. W44 opens with Brent (down 6.4 percent on the week, named by the oil stories), not SPP's hub up 37.1 percent; W43 with WTI (up 13.1 percent, named), as session 2705's preview did.
  - **An empty category stands in with the next price move, said so** (fault 27): `five_numbers` keeps every move it computed (`picked["moves"]`), and a deal or a datacenter row with nothing to show reads "no deal in `energy_deals` is dated this week; in its place, the week's next price move: ..." (the empty tables are the data machine's).
  - **The chart's row says whose week its figure is** (fault 28: "(the week before: the chart's latest period ends before this week)"); the template id and the path stay in the row as the tracer's key until session 1450 moves them.
  - **The datacenter row needs an operator or a site** (fault 29); the ids stay as the tracer's keys until 1450.
  - **The limitation says what the stories do not state** (faults 30 and 31): `evidence_gap` claims a figure as the outlet's only when the headline holds it (the Singapore story's 1 GWh is no longer printed as 1,000 MW), names an empty party field and a missing capacity or sum, keeps "one outlet so far" and "an analysis piece", and prints nothing when every field is stated and more than one outlet ran the story. `score.capacity_stated` refuses a model's `mw_mentioned` when the title and summary hold no capacity unit (GWh is not MW).
  - **The subject in plain words** (fault 34): the headline cut at a word to 70 characters, the move as "Brent down 6.4% on the week"; at most about 110 characters.
  - **The chart section** (fault 35): the reading note is written only when the engine wrote no note (the note already says the move against the weeks held), and the stories' measure is one sentence ("The week's stories point to US crude oil exports, whose chart is on /research"); the related measure's chart itself is the data machine's to render (item 17).
  - **The email's five do not print the opening number twice** (fault 26): the row that is the opening number word for word reads "the opening number, above"; the markdown keeps the row, since `scripts/check_roundup.py` traces the five by their form.
  - Tests: `Session1446TheRoundupsNumbers` (the stand-ins, the datacenter row, the scorer's refusal); `V2RTheOpeningNumber`, `V2RTheParts.test_the_evidence_gap` and `test_session806`'s two cases re-pinned to the rule.
- The faults file: rows 25, 27, 30, 31, 34 fixed; 26, 28, 29, 35 fixed in part (the tracer's keys and the data machine's chart).
- **`ffe0ab628`**: a story names a price for the opening number's choice whether or not its why line prints a reason (`brief.price_named`; `brief.opening_number` and `roundup.opening_number` read it): the first W44 render without the model opened with the top story's 1,000 MW because the oil stories' why lines said "signals" and `price_reason` printed nothing, so Brent counted as unnamed. The second render (`runs/s1446/2026-W44b.md`) opens with Brent: "closed at 120.15 USD/bbl on 2026-10-30, against 128.30 USD/bbl on 2026-10-23 (-8.15 USD/bbl, -6.3%)", subject "ERW Weekly | 1GW data centre with 5,000MWh battery storage system submitted to...; Brent down 6.3% on the week" (the publisher's title, since no model ran).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1446"` | 0 | |
| `tests.test_periodicals`, `test_session806`, `810`, `232`, `470`, `807` | 0 | 179 passed, 1 skipped (the Roundup email fixture is not in the suite) |

## Decisions made without you

- The five numbers' rows keep their ids and the chart's template and path in the markdown: `check_roundup.py` reads them as the figures' keys; session 1450 (the tracers) moves them to a Tables line with the regexes, so a reader of the page and the email stops seeing them.
- A benchmark move named by a story opens the Roundup before a USD 45 billion deal: the brand's first two tests (system scale, persistence) read a week-long move in a market-wide price as the larger fact; the deal is the next line.
- The scorer's refusal of `mw_mentioned` is applied at scoring time (no story re-scored); the stored 1000 for the Singapore story stays in `news_stories.csv`, and the Roundup no longer prints it as MW because the headline does not state it.

## For Samuel's ruling

- None new; item 17 stands for the data machine.
