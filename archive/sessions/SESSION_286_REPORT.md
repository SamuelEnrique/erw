# Session 286 report: the second round of findings

14 October 2026, 18:46 to about 19:35 UTC, unattended, on lab-desktop (the data machine), the third session of the daytime chain of 14 October (the hunt was started at 18:46, while session 285's checks ran). Branch `task/286-findings-round-two`. Model spend USD 0: no model call. Pulls: none. Writes: 12 rows to the review list (`public.scanner_drafts`, by the hunt itself, state draft); no draft's state changed.

## Read these first

- **The hunt raised 12 drafts; the scanner raised none** (its 5 flags of today were raised before). All 12 reproduce exactly: each draft's own Python mirror on its own CSV (45 to 47 stored values a draft), and the CSV rebuilt from today's tables (every year equal).
- **Verdicts: 2 strong, 6 usable, 4 drop.** Appended to `docs/reviews/findings-verified-2026-10-13.md` as blocks 29 to 40, after session 251's section.
  - **Strong:** PJM's evening ramp (the median day's steepest hour, 2,484 to 3,805 MW per hour, 2019 to 2025, EIA's rows); ERCOT's demand growth that weather does not explain (7.8 to 24.2 percent above the 2019 to 2021 base, 2022 to 2025; four times the fit's uncertainty).
  - **Drop:** the South hub's night spread (the whole claim is 2025), the West hub's implied heat rate (a hump), PJM's evening carbon premium (the 4 PM to 9 PM window says the opposite), the Houston load zone's negative hours (the whole claim is 2015).
- **This hunt drafted weaker claims than the last** (strengths 1.24 to 3.74, against 2.46 to 11.23 on 13 October), and four of the twelve repeat a story already on the list: ERCOT's negative hours have now been drafted at three hubs and four load zones.
- **Motion proofs of the two strong drafts:** `docs/research/motion/hunt-2026-10-14/` (README first), 15 seconds each, both sizes, with stills. The first render had two faults, seen in the stills and fixed in the specs' words (no number): an end label that ran off the frame, and a six-line title that pushed the axis off. Nothing was posted.

## The landing of session 285, recorded here

- Before `s285-before` 18:51:16 UTC; pushed 18:51:22 (`task/285-tracker-tables`, `f89cf21f`); check run 116040360840 success 19:02:08 (workflow run 38618713188); merged `a5963d3e`; deployed 19:03:41; after `s285-after` 19:03:42; `compare`: 0 differences. Expected: documents only.

## How it was checked

- `docs/reviews/findings-verified-2026-10-14-session286/`: `fetch_drafts.py` (session 251's, its folder changed), `verify_286.py` (session 251's verifier imported and run as it stands, with the finding-pattern rebuild of session 252 and four new "asked another way" cuts), `build_286.py` (session 251's block writer imported; the verdicts are this session's). The result files are beside them.
- The one draft of a finding's pattern (Houston hub's negative hours) is rebuilt by its finding's own compute; its tables are checked as a part of the pattern's `OWN_TABLES` entry (session 258 narrows a draft's list).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 286"` | 0 | six of six |
| `hunt.py --weekly` (18:46 to 18:49 UTC) | 0 | 20 patterns, 143 claims, 50 pass, 12 drafted and loaded |
| `findings_scanner.py --daily` (18:51 to 18:53) | 0 | 118 tables, 11 flags, 5 drafts, 0 added |
| `fetch_drafts.py` | 0 | 40 rows, 12 new |
| `verify_286.py` | 0 | 12 of 12 exact |
| `build_286.py` | 0 | 12 blocks: 2 strong, 6 usable, 4 drop |
| `node specs.mjs`, `node render.mjs` (three renders) | 0 | four videos, four stills, looked at |
| `tests.test_session286`; `test_session251`, `252`, `274`, `233` | 0, 0 | 7; 61 |
| the branch's checks, first push (`3d253b55`, 19:10) | failure | check run 116049437758 at 19:14: two tests of earlier sessions, reproduced here with `GITHUB_ACTIONS=true` (below) |
| the same two, after the fix, with `GITHUB_ACTIONS=true` | 0 | with 251, 252, 262, 274, 286: 77 tests |

## The first push failed its checks, and why

- **`test_session258`:** no committed file outside a named list may carry a hunt draft's source line ("Found by the weekly hunt"), so that a later fix of the stored drafts' source lines cannot miss a copy. The two motion specs and `verify_286.json` carry it. Both folders are records of one day's drafts as they then stood, like session 251's, which the list names: added to the list, with that reason.
- **`test_session267_findings`:** `site/lib/findingverdicts.ts` must hold every verdict of the document, and the document now holds 40. The internal page prints each as "Verdict of 13 October 2026", in `site/app`, which this chain may not edit; adding today's twelve would misdate them. The test now reads the 13 October sections only, and today's twelve show "no verdict" on the page until it can date a verdict. A ruling (4).

## Decisions made without you

1. **The hunt ran with `--weekly`, which loads its drafts,** as the prompt asked ("run the weekly hunt"); it is Wednesday, not its Saturday. Its memory (`runs/hunt/state.json`) now holds today's claims, so Saturday's hunt drafts only what is new or moved after today.
2. **The scanner ran with `--daily`** after this machine's daily run had already run it today: it raised nothing new and re-published the day's chart of flags with the same day.
3. **The verdicts are mine, by session 252's rule,** and the reasons name their numbers.
4. **The motion specs live beside their videos,** not in `motion/specs/`, whose seven proofs session 274's tests hold. Words of the two specs were shortened after the first render showed them running off the frame; every number is the draft's (a test holds it).
5. **The render used session 274's installed packages in `../erw-274`:** this checkout has none under `motion/`, and installing them again would be a 120 MB download for the same versions.

## For Samuel's ruling

1. The 12 drafts on `/internal/findings`: approve the two strong ones, dismiss the four to drop?
2. The hunt: fold a draft whose years agree with one already on the list into it (ERCOT's negative hours, seven times now), and stop a pattern whose measure has ended (the reserve adder, ended 4 December 2025)?
3. The motion frame: fit a long title and a long unit by itself (a smaller size, or the unit beneath only), so a hunt card can be rendered with its own words?
4. The review list's verdicts: let the page date each verdict (a `day` in `site/lib/findingverdicts.ts`, the words in `site/app/internal/findings/page.tsx`, the code machine's), then add the twelve of 14 October?

## Files

- Changed: `docs/reviews/findings-verified-2026-10-13.md` (blocks 29 to 40), `tests/test_session258.py` (two folders allowed), `tests/test_session267_findings.py` (the 13 October sections only).
- New: `docs/reviews/findings-verified-2026-10-14-session286/` (three scripts, their outputs, `verify_286.json`), `docs/research/motion/hunt-2026-10-14/` (README, two specs, four videos, four stills), `tests/test_session286.py`, this report.
- On this machine, not in git: `runs/session286/` (the hunt's and scanner's logs, the drafts as read), `runs/hunt/2026-10-14/`.
