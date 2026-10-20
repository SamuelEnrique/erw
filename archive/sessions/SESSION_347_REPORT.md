# Session 347 report: the /impact page

20 October 2026, about 08:45 to 09:35 UTC, unattended, on portable-laptop (the third machine), the fourth session of the chain of 20 October, night. Branch `wip/345-impact`, not landed. Model spend USD 0. No pull.

## Read these first

- **`/impact`, "What a project does for a state", in review**, in the Economics menu under its own line ("Economic impact", after Severance tax). The battery page's layout: the Assumptions box at the left, then three questions.
  1. **How many jobs?** A summary sentence, three headline numbers (job-years built, jobs each year, wages while built), and two tables (construction; each year of operation) by effect: JEDI's jobs per MW, then the reader's jobs, earnings and output. Each effect's hover names JEDI's cell (model, release, sheet, row, column, state).
  2. **What does it pay the state?** Property tax: "no rule held" for every treatment in Texas, Louisiana and New Mexico, each row with its note; the abatement scenario (off by default) says it applies nothing. Severance: the rules are held and cited on /severance, and none is computed for a plant. Any other state: no rule held.
  3. **What matters most?** The swing of each lever (size +50 percent, capital cost +25 points, local content +25 points, life +5 years) on job-years built, jobs each year and job-years over the life; the state's rank; a chart of the same project in the ten states with the most construction jobs, the reader's state and the five with the fewest (Chart | Table), and every state in a table under it.
- **Every figure is a checked Num:** JEDI's per-MW figures, the project's MW and the local shares are `series|nlr_jedi_multipliers|...` keys; every computed figure is `impact|<tech>|<state>|<mw>|<capex>|<local>|<life>|<stat>`, which `check-values.mjs` recomputes with the page's own `site/lib/impact.ts` from its own read. **340 of 340** on the four addresses added to its list.
- **Every default is JEDI's** (its project's size, cost and local shares). JEDI states no plant life, so the life has no default.
- **The table gained three rows a location** (the project's MW and the two local shares), because the live set's series table keeps only entity, variable, time and value: 5,562 rows, loaded, drafted and archived again under the data lock.
- **The review pack** `docs/reviews/packs/impact.md`, in the five tools' form (`tests/test_session262.py` holds it now); its part 9 has ten questions for you.

## What to review

In the internal view (`https://erw-flame.vercel.app/internal/open` first), once the branch has landed:

1. `/impact`; `/impact?tech=utility_pv&state=la&mw=200&life=30`; `/impact?tech=natural_gas&state=dc`.
2. `docs/brand/review-347/` (six shots, 1280 and 390).
3. `docs/reviews/packs/impact.md`, part 9.

## Checks

| Check | Exit | Result |
|---|---|---|
| `eslint` on the three page files | 0 | no finding |
| `npm run build` (three times, the last after the chart and format fixes) | 0 | |
| `CHECK_VALUES_PAGES=/impact check-values.mjs` on the local build | 0 | 340 of 340 (a restricted run: not the landing's gate) |
| `check-routes.mjs` on the local build | 0 | every page, 0 failed; `/impact`, its DC address and `/data/methods/economic_impact` answer |
| `shot.mjs`, three addresses at 1280 and 390 | 0 | `docs/brand/review-347/` |
| Impeccable `detect` | not run | not installed on this machine (`docs/tooling.md`); under "To finish" |
| tests 345, 346, 347, 262, 53 | 0 | 45 tests |
| the whole suite (`unittest discover -s tests`), started before session 347's changes | 1 | failures read below |

**The suite's failures.** Two were this chain's and are fixed: `test_session53` (the tools inventory lacked `/impact`: `docs/tools.md` has its row now) and `test_session345` (the suite read the table while it was being rewritten with its new rows; it passes now). One is this chain's and is left: `test_session275` (the release-v1 package does not list the two new tables; `release_v1.py` on this machine, which holds only some tables, would have rewritten the package without most of them, so it was reverted at once and listed under "To finish" for the data machine). The others read data tables that are absent or older on this machine and touch no file of this chain: sessions 49, 51, 78, 80, 89, 90, 92, 156, 164, 273 and 308.

## Decisions made without you

1. **A plain GET form**, as the battery page's own form is: every figure is drawn on the server from the address, so check-values reads it, and the page works without script.
2. **Capital cost and local content as percents of JEDI's defaults**, acting in proportion; the local content's single factor per phase is the page's one approximation, said in its hover, the decisions block and the method.
3. **No default life** (JEDI states none; the prompt asks every default to be JEDI's or a statute's); the generator page's Lazard lives are offered to you as the pack's question 3.
4. **`impact_tax_rules` is not offered for download** (its terms are not read: "not settled"); the line under the downloads says so. `nlr_jedi_multipliers` is offered through the shared downloads line, which shows the table once the live set releases it from review.
5. **The chart shows 16 of the 51 places** (the top ten, the reader's, the bottom five): all 51 in one stacked chart were unreadable at both widths. Every state is in the checked table under it.
6. **Dollars under a million** are written to two decimals, those above as "63.46 million", the two forms check-values reads.

## For Samuel's ruling

- The pack's part 9 (ten questions).

## To finish (for the code machine, when it lands this branch)

- `~/.claude/skills/impeccable/scripts/impeccable detect --json site/app/impact/page.tsx site/app/impact/StateChart.tsx site/lib/impact.ts`.
- The landing gate: the full `check-values.mjs` with `CHECK_VALUES_WRITE_FLOOR=1` once it passes in full (the four `/impact` addresses have no floor yet).

## Files

- New: `site/app/impact/page.tsx`, `site/app/impact/StateChart.tsx`, `site/lib/impact.ts`, `docs/reviews/packs/impact.md`, `tests/test_session347.py`, `docs/brand/review-347/`, this report.
- Changed: `site/lib/release.ts`, `site/lib/pages.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-routes.mjs`, `docs/tools.md`, `tests/test_session262.py`, `warehouse/connectors/jedi_multipliers.py`, `tests/test_session345.py`, `docs/methods/economic_impact.md`, the metadata of the table's new load.
