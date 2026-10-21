# Session 406 report: the newsletter's first issue, drafted, nothing sent

21 October 2026, about 03:10 to 04:20 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-406` on `wip/406-s` (from `wip/381-382-land` at `61c4c309`). Chain `queue/done/015-day-20-october-code-pm.md`, session 406; master plan tool 9 (the flagship newsletter), the draft only. Model spend USD 0; no pull from any publisher; no warehouse data written; nothing sent anywhere.

## Read these first

- **The draft is `docs/reviews/newsletter/issue-001.md`**: "What a battery in Texas earns, and why it earns a sixth of what it did". The question: what a grid battery in ERCOT earns, from which stream, and how that changed as the fleet grew. The battery page's default (100 MW, 4 hours, ERCOT's hub average, perfect foresight) year by year from 2018: 530.14 USD per kW in 2023, 87.44 in 2025, 81.40 over the last twelve months; ancillary services from 37.81 million dollars (2023) to 3.01 million (2025); ERCOT's battery fleet from 4,174 MW (end 2023) to 13,909 MW (end 2025); the day-ahead case and CAISO beside it; and the page's own comparison with ERCOT's real awards (the model is 5.66 times them), which the draft uses to say every figure is a ceiling. About 1,300 words with the tables and captions; 10 footnotes, each with the page address and the check-values key.
- **The notes are `docs/reviews/newsletter/issue-001-notes.md`**: 28 claims in the draft's order, each marked figure, arithmetic, reading, method or outside, with its source and what a sceptic would push back on.
- **The three charts are not made.** The local build failed three times (03:13, 03:36, 03:55 UTC) on the home page's required read (`Supabase entities: HTTP 500 ... 57014 statement timeout`), as the chain's rules foresaw. The draft marks where each chart goes, the page and element it is cut from, and says they wait. `docs/reviews/newsletter/issue-001/shots-406.mjs` makes all three from the next build ("To finish").
- **The figures were not read from the pages.** With no build, every figure was read from tonight's Supabase through the page's own code, as check-values computes the value it compares a page against: the `bs|` keys by `lib/batterystack.ts` over `battery_stack_monthly` and `battery_stack_stress_daily`, the `series|storage_buildout_monthly` keys directly, rounded as the pages round them (`lib/batterystack.ts`, `lib/buildout.ts` `whole`); the `bsa|` keys from the committed snapshot the page reads. The ERCOT figures equal, to the dollar, the full passing check-values run of 19 October (session 301). The CAISO figures moved since then (2025: 91.74 then, 92.00 tonight), so the draft uses tonight's. Reading them off the pages is under "To finish".

## What to review

- The draft: `https://github.com/SamuelEnrique/erw/blob/wip/406-s/docs/reviews/newsletter/issue-001.md`
- The notes: `https://github.com/SamuelEnrique/erw/blob/wip/406-s/docs/reviews/newsletter/issue-001-notes.md`
- The pages it reads, in the internal view: `/cost-of-power/battery`, `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead`, `/cost-of-power/battery?grid=caiso&dur=4&strat=foresight`, `/storage?tab=buildout&grid=ercot`.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s406/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `duty.py beat` before `npm ci` and the first build | 0 | |
| `npm ci` in the worktree's `site/` | 0 | |
| `npm run build`, try 1 (03:13) | 1 | `/` failed to prerender: `Supabase entities: HTTP 500 ... statement timeout` (`build-1.txt`) |
| `duty.py beat` before tries 2 and 3 | 1, 1 | `TimeoutError: The read operation timed out` (Supabase) |
| `npm run build`, try 2 (03:36) | 1 | the same (`build-2.txt`) |
| `npm run build`, try 3 (03:55) | 1 | the same (`build-3.txt`); the mutex released after each try |
| The `bs\|` figures from Supabase through `lib/batterystack.ts` (four cases) | 0, 0, 0, 0 | `bs_ercot_foresight.txt`, `bs_ercot_foresight_span.txt`, `bs_ercot_dayahead.txt`, `bs_caiso_foresight.txt`, `bs_caiso_dayahead.txt` |
| The same with Uri left out of 2021 (`win_kw:2021:2021:uri_2021:total`) | 1 | six statement timeouts; the draft no longer says the storm's days carry the year (notes, claim 20) |
| `storage_buildout_monthly` for ERCOT from Supabase | 0, 0 | MW at the first try, MWh and the twelve-month additions at the second; the unit counts timed out (not used) |
| `tests.test_session406` | 0 | 12 tests OK |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,794 tests, 252 skipped, one failure: `test_session156` (the ask fixtures), which the chain's rules say may fail tonight; nothing else (`suite.txt`) |

## Decisions made without you

1. **The question is the battery's income by stream**, of the four the chain named: it is the one where the warehouse gives, free, what a reader otherwise buys or gets only as one fleet average (one battery, every year since 2018, split by stream, the code public), and it has the most checked figures on the most pages. The node basis and the 4CP saving are good second issues.
2. **The figures came from Supabase through the page's code, not from the page**, because no page could be built. The chain allows "from Supabase with the key"; the draft and the notes both say which was done. A figure that could not be read tonight (the Uri window) is not used.
3. **No dev server instead of a build.** `next dev` would have drawn the pages without the home page's prerender, but the chain says to leave the charts under "To finish" if the build fails on the database, so it was not tried.
4. **The headline "a sixth" is 2025 against 2023**, the peak; against 2022 it is about a fifth. The notes (claim 10) offer "from 2023's peak" for the title.
5. **Claims the warehouse cannot show were cut or marked**: the storm's share of 2021 (cut to "the year of Winter Storm Uri"), the go-live of ERCOT's real-time co-optimization (cut to NPRR 1282's duration change, which the method note cites), and the reserve quantities ERCOT buys (kept as a reading, marked "outside" in the notes, with the caveat in the draft that the warehouse shows the two lines together, not the cause).
6. **The draft names no competitor.** It says the answer is "usually sold, or given as one fleet average"; the notes name Modo Energy's index as the sceptic's first reply, for Samuel to judge the sentence.
7. **Escaped bars in the notes' table**: a check key's `|` inside a table cell splits the cell on GitHub, so the keys in the notes' table carry `\|`; the test holds it.

## For Samuel's ruling

- **Issue 1's question**: send the battery's income by stream as issue 1, or hold it for one of the other three (the price years, the node basis, the 4CP saving).
- **Issue 1's title**: "why it earns a sixth of what it did" (against 2023's peak) or "from 2023's peak" or a title without the ratio.
- **The sentence on other sources**: "The answer is usually sold, or given as one fleet average with no split" (notes, "Why this question"): keep, change or cut.
- **The real-time co-optimization line**: add the go-live of 5 December 2025 from ERCOT's own notice, or keep only the NPRR's duration change (notes, claim 27).
- **The newsletter's reader**: issue 1 reads pages that are all in review; a subscriber who follows a footnote's address sees the in-review page. Send only once the pages are live, or send with the figures and charts in the mail itself.

## To finish

The charts and the read from the pages, on the next night the database answers (the mutex as the chain's rules say; port 3406):

```bash
cd C:/Users/lossa/Documents/erw-406/site
npm run build > C:/Users/lossa/Documents/erw/runs/chain_oct21/s406/build-4.txt 2>&1; echo "exit=$?"
npx next start -p 3406 > C:/Users/lossa/Documents/erw/runs/chain_oct21/s406/server.txt 2>&1 &   # in its own background call
node ../docs/reviews/newsletter/issue-001/shots-406.mjs http://localhost:3406 > C:/Users/lossa/Documents/erw/runs/chain_oct21/s406/shots.txt 2>&1; echo "exit=$?"
CHECK_VALUES_PAGES=/cost-of-power/battery,/storage?tab=buildout CHECK_VALUES_REQUEST_S=120 node scripts/check-values.mjs http://localhost:3406 > C:/Users/lossa/Documents/erw/runs/chain_oct21/s406/cv.txt 2>&1; echo "exit=$?"
```

Then: look at each PNG and check the three captions against it (chart 1's broken 2021 bar, chart 3's incomplete 2023); remove the italic paragraph "The three charts are not made yet" from the draft (the test then requires the three PNGs); compare every footnoted figure with the page's `data-raw` and text (the MW view `/storage?tab=buildout&grid=ercot` is not in check-values' list: read its table "The numbers behind both charts" by hand or with the `data-check` attributes); change "read on 21 October from Supabase" in the draft's first note; stop the server on port 3406.

Also: the Uri window, `bs|grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=2261119|win_kw:2021:2021:uri_2021:total`, from the page's "Leave out" box, before naming the storm as the cause of 2021 (notes, claim 20).

## Files

- `docs/reviews/newsletter/issue-001.md`, `docs/reviews/newsletter/issue-001-notes.md`, `docs/reviews/newsletter/issue-001/shots-406.mjs` (new).
- `tests/test_session406.py` (new).
- This report.

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The charts:** `node docs/reviews/newsletter/issue-001/shots-406.mjs http://localhost:3415` exit 0, the three PNGs (commit `92e58c48`). Looked at each: chart 1 (ERCOT, the default battery) draws 2018 to 2026 stacked, 2021 broken at the top of the 600 scale with 3,431 written above it, 2026 hatched with "9 months"; chart 2 (ERCOT, MW at each year's end) runs 2015 to 2026* with 18,205 over the last bar and the note "2026 is the year so far, to August 2026"; chart 3 (CAISO) draws 2023 hatched with "5 months", 2024 at 116, 2025 at 92 and 2026 hatched at 64. Captions: chart 1's "should be (the caption is to be checked ...)" replaced by what the PNG shows; chart 2's caption names the asterisked 2026; chart 3's caption already matched.
- **The figures against the pages:** `CHECK_VALUES_PAGES=/cost-of-power/battery,/storage?tab=buildout CHECK_VALUES_REQUEST_S=120` exit 0, 1,175 of 1,175. Every `bs|` and `bsa|` key of the footnotes (41) shows on the page the text the draft prints. The ERCOT MW view, not in check-values' list, was read in the browser (`read406.mjs`, scratchpad): its keys and its table "The numbers behind both charts" give 2,130, 4,174, 8,294, 13,909 and 18,205 MW, the draft's figures.
- **The Uri window:** on the battery page, the window 2021 to 2021 with Uri left out reads `win_kw:2021:2021:uri_2021:total` = **325.04** USD per kW (against 3,430.56 for the whole year), read at 09:26 UTC. Written into claim 20 of `issue-001-notes.md`; the draft's sentences were not changed (naming the storm as the cause stays Samuel's choice).
- **The draft:** the italic paragraph "The three charts are not made yet" removed; the first note now says the figures were computed from Supabase and read again from the built pages. `tests.test_session406` exit 0 (12 tests; it now requires the three PNGs).
