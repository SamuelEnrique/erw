# Session 450 report: the two research reports, read into a roadmap v4 draft

21 October 2026, about 07:16 to 07:30 UTC, unattended, on portable-laptop (the code role), in the main checkout on `wip/441-450-third` (from `origin/main` at `d25da8d8` plus the queue commit). The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 450). Model spend USD 0; no web request; no warehouse data written; no `site/` change, so no build. `docs/roadmap.md` is unchanged.

## Read these first

- **The draft is `docs/reviews/roadmap-v4-draft.md`**, for the review of Wednesday. For each of the master plan's twenty tools: what the two reports say (with report and section, as links to their headings), what the ERW has on main and on branches (read with read-only git), and one recommendation in one of four places: first, second, third, later. No tool is cut.
- **The order it proposes.** First: the Digest and the Roundup (1, 14), by Samuel's ruling; the cost-of-power model and the deal tracker (16, 6), on AG's evidence; downloads and data products (15, 19), the one rank both reports agree on. Second: the datacenter tracker, the policy monitor, the explorers (4, 12, 5). Third: the live views (2, 7, 8, 20, 3), kept current, in parallel with Ask the Grid. Later: 9, 13, 10, 11, 17, 18.
- **"This week" rewritten** in the roadmap's own format (seven items, each with machine, where, done, and the standing rulings as `rulings:` lines), with a table of where each v2 item went.
- **Where the reports disagree** (six items: ISO licensing, an API, live maps, what comes second, the audience, the launch) and **what neither checked** (nine, the first being the ERW itself).
- **"02_master_plan" is not in the repository.** The draft takes tools 1 to 20 of `docs/platform-tools.md` as the master plan's twenty: AG numbers the tools the same way, and the chain of 20 October calls tool 5 the explorer and tool 9 the newsletter as that file does. `docs/platform-tools.md` lists 31; 21 to 31 are not ranked.
- **"Donor Grids and Taker Grids"**, which AG names as the ERW's paper, is not in the repository under that name (`git grep -i donor` finds it only in AG). The draft says so and asks Samuel where it is.

## What to review

- The draft: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/roadmap-v4-draft.md`
- The test: `tests/test_session450.py`.
- The sources: `docs/reviews/research/deep-research-report.md` (DR) and `docs/reviews/research/ask-the-grid-landscape-2026-10.md` (AG), both unchanged.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s450/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session450` | 0 | 9 tests OK: no em or en dash; tools 1 to 20 each with "The reports", "The ERW today", a recommendation and a link; the order table places every tool once and agrees with each recommendation; no tool cut; both closing sections with at least three items; "This week" in the roadmap's format; every local link exists and every heading anchor into a report exists; every github.com link exists on the branch it names; `docs/roadmap.md` equal to `HEAD`'s |
| The same tests against a copy with a dash, a broken link and a recommendation out of the table's place | 1 | 3 failures, as it should (`negative.out`) |
| Whole suite, build, snapshot, browser checks | not run | documents and one test only; the chain's note (session 451) runs what the landing needs |

## Decisions made without you

1. **The master plan's twenty are tools 1 to 20 of `docs/platform-tools.md`**, since no 02_master_plan file is in the repository and AG's numbering matches it.
2. **Four places, not a strict rank of twenty.** Ties are real (16 and 6 share AG's first rank); a strict order would invent a precision neither report has.
3. **The owner's rulings govern where a report disagrees**: DR's long-form pieces and newsletter are "later"; the live views are "third", kept, not cut, not raced.
4. **Links go to the reports' headings** (GitHub anchors, checked by the test), so each claim can be found in its section; a branch file is linked on github.com with its branch.
5. **Tonight's other sessions' files are named in backticks, not linked**, because they may not be committed when this one is.
6. **DR's untraceable figures are not repeated as facts.** DR has no source list; the draft quotes it only to say what it recommends, and lists its figures under "What neither report checked" as needing a person's check before any is quoted.

## For Samuel's ruling

- Adopt, change or drop the draft's "This week" as v4 (only a person writes `docs/roadmap.md`).
- Where "Donor Grids and Taker Grids" is, or whether it is still to be written.
- Modo's ERCOT battery figure as a calibration (a new source, under the roadmap's hold).
- Ask the Grid's MCP for the ERW's own research, after a person reads its terms.
- AG's "before the Oct 30 LOI": whether the date stands.

## To finish

- Land `wip/441-450-third`'s draft and test with the code machine's next landing (a document and a test; no build needed for them).

## Files

- `docs/reviews/roadmap-v4-draft.md` (new).
- `tests/test_session450.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s450/test.out`, `negative.out`.
