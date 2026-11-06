# Session 1440 report: the opening number

Energy Research Warehouse (ERW), session 1440 (chain 149's "1437"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 01:55 to 02:05 UTC (beside session 1439's landing gate, which ran as its own process). Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (reads for the survey). Branch `wip/1440-periodicals` over `wip/1439-periodicals`.

## What it did, with commits

- **The survey** (`runs/s1440/before.md`, `after.md`): for each of the 13 issues and the 26 October dry run, the day's candidates from the live set (bounded by the issue's cutoff, session 1439's rule) with which a story of the day names, and the opening number the chooser picks, before and after. Three issues of September carry the older stamp and give no window.
- **`31cc0b447`**, `brief.opening_number` (fault 2): a move no story names needs `UNNAMED_FACTOR` (1.5) times the bar (a benchmark 4.5 percent, a hub 15 percent); an unnamed single hub never opens the issue while a named move, an unnamed benchmark past its bar, or a top story's structural figure exists (it is the last resort). `PRICE_WORDS`: a story that says "oil prices" or "crude price" names Brent and WTI, "gas prices" names Henry Hub, so the consequence tier reads the day's stories as a reader does. Tests: `Session1440OpeningNumber` (the 14, 21 and 26 October cases, the price words); `V2TheOpeningNumber.test_the_rule_on_fixtures`, `V2TheNumbersBlock`'s two cases and `test_session804`'s reason case re-pinned to the rule.
- The faults file: rows 1 and 2 fixed.

## The opening number each issue would open with (the survey; the live set as read on 6 November)

| Issue | Before (the landed chooser) | After | Reason |
|---|---|---|---|
| 28 Sep | Brent +3.4% (named) | WTI +16.6% (named: the stories say "oil prices") | two named benchmarks, the larger move |
| 2 Oct | Brent +18.0% (named) | same | |
| 7 Oct | Henry Hub +4.3% (named) | same | a named benchmark before a named hub (ERCOT -15.6%) |
| 8 Oct | WTI +3.4% (named) | same | SPP +69.4% named is a hub |
| 9 Oct | Henry Hub -4.3% (named) | same | |
| 12 Oct | WTI -3.8% (named) | same | |
| 13 Oct | Brent -3.2% (unnamed) | Brent -3.2% (named: "oil prices") | |
| 14 Oct | **SPP SPPSOUTH_HUB day-ahead +676.7%** (unnamed, from a near-zero day) | **USD 4.4 billion, Taiwan's commitment to Alaska LNG** (the day's top story) | an unnamed hub is the last resort |
| 20 Oct | Brent -3.0% (named) | Henry Hub -5.5% (named: "gas prices") | two named benchmarks, the larger move |
| 21 Oct | WTI -3.6% (unnamed) | WTI -3.6% (named: "oil prices") | |
| 22 Oct | Brent +6.8% (unnamed) | same: past 4.5 | |
| 23 Oct | WTI +5.2% (named) | Henry Hub -5.8% (named) | the larger named move |
| 26 Oct (dry run) | Henry Hub +3.5% dated 3 November (fault 1) | Henry Hub -9.3% on 26 October against the 23rd (unnamed, past 4.5) | Brent -0.1% named is under the bar |

No issue opens with a hub's percentage move after the change; before, 14 October did (and 20 October would have, SPP +1,850.9 percent, had Brent not been named).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1439"` (this session ran beside 1439's gate; precheck's duty window covers it) | 0 | |
| `tests.test_periodicals`, `test_session804`, `807`, `2206` | 0 | 114 passed |
| the survey, before and after | 0 | 13 issues read, 3 without a window |

## Decisions made without you

- The unnamed bar is 1.5 times, not 2: at 2 (6 percent for a benchmark) 22 October's Brent +6.8 percent still opens and 26 October's Henry Hub -9.3 does too, but a 5 percent unnamed benchmark move would fall to a story's figure, which the survey's days do not show as better.
- A story that names "oil prices" names both crude benchmarks: the consequence tier then ties and the larger move decides (28 Sep, 23 Oct), which reads right (the stories were about oil, the larger oil move leads).
- The survey reads the live set as held now; a day whose prices the live set no longer holds (the 25 to 27 September issues, older stamps) is not re-read.

## For Samuel's ruling

- None.
