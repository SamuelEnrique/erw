# The portable laptop's window P1, chain 233: the five tools against roadmap item 2 (13 November 2026)

Energy Research Warehouse (ERW), session 5010, for Samuel. Chain 233 (`queue/done/233-day-13-november-portable-p1-five-tools.md`), window P1 of the portable laptop, 09:40 to about 11:00 UTC, Opus 5.5. Sessions 5000 to 5010 (the plan's 5048 note written as 5010: the work ran out before the numbers did).

- **Model spend: USD 0.** No model was called. No request to a public host. Reads of Supabase with the anon key only (the site's build and `check-values`).
- No warehouse data written. `site/lib/release.ts` untouched. Nothing sent or posted. No layout or brand change.
- **Nothing landed** (nobody on this laptop lands). Everything waits in `docs/state/landing_request_portable.md`, rows 17 and 19 to 22. **Landing row 22 (`wip/5000-grid`) lands all five**; it holds rows 17, 19, 20 and 21 and is merged with `origin/main` of 10:50 UTC.

## Per tool, against the done line

| Tool | Method note | Replication | Cross-check table | Decisions block | Faults file (rows: fixed / ruling / other) |
|---|---|---|---|---|---|
| Battery `/cost-of-power/battery` | ready for signature: section 12 (the decisions) new; the 60 percent figures marked with today's default; CAISO's start; headings of the dropped sections | 22 of 22 from the public CSV | current | **new**: 17 lines on the page, drawn open (nothing collapsed), and in the note word for word | 9 rows: 4 / 3 / 1 data machine, 1 not a fault |
| Generator `/cost-of-power/seller` | ready for signature; item 3 of section 10 closed (session 204's schedule) | 13 of 13 | current | present | 3 rows: 1 / 0 / 1 data machine, 1 not a fault |
| Datacenter `/cost-of-power` | ready for signature; **your ruling of 12 October on the foreseen load applied** (it was not in the code); item 4 closed | 14 of 14 | five figures moved since 6 November, set to 12 November's | present (line 7 now states your ruling) | 3 rows: 2 / 0 / 0, 1 not a fault |
| Research (Automated Analysis) `/research` | ready for signature: **sign-off block new**, a section "Final form", the route | 66 of 66 computed | present | present (35 assumptions) | 5 rows: 4 / 0 / 1 the old laptop's |
| Grid `/grid` (with `/network`, `/mix`, `/ask`) | ready for signature | **runs with no argument again** (it failed the day after its figures were written): 85 of 85 network figures | present | present | 3 rows: 1 / 0 / 1 data machine, 1 not a fault |

- **None of the five notes is signed.** Signing is yours: each note's "Sign-off" block.
- **No do-file has been run.** Stata is not on this laptop. Every input the seven do-files read exists in the repository.
- **Research's final form:** every part of the page is made on a clock with no person (the note's new "Final form"); a finding is published after your approval, by your ruling. Whether that is final is your word.
- **The Grid tool is one page** since session 299: `/network`, `/mix` and `/ask` resolve into `/grid` (read today). Its design waits for the brand mockups (roadmap item 3).
- **Reads:** the site built twice under the build lock (exit 0 both, TypeScript included). 165 views read at 1280 and 390 in the internal view: no console error, no broken text, and after the fix no sideways scroll. `check-values` on the economics pages and `/research`: 2,873 of 2,873.

## Fixes that change what a reader sees (when landed)

- The battery page gains its decisions list at the foot, open.
- The datacenter page's "if perfectly foreseen" figures, for a flexible load in a year held in part, use the rule's budget. Example, the note's frozen case: 29.72 becomes 29.29 USD per MWh. No default figure moves (the default load is flat).
- `/research` fits a phone (it was 563 px wide at 390).

## For Samuel's ruling (each with its default)

1. **The five signatures.** Default: unsigned until you sign.
2. **The do-files.** Default: "never run" until you run them in Stata.
3. **Research's final form.** Default: final as described.
4. **Battery, the settings column's "Financing" fold starts closed** while the text sends the reader there (battery row 4). Default: leave it.
5. **Battery, the node-spread fold under the income table** (row 5). Default: leave it.
6. **Battery at 390: the assumptions panel stands about 1,500 px above the answer** (row 8). Default: leave it.
7. **`chain_queue.py` refuses a window's mark on its own machine** (`machine: portable-laptop-window1` on `portable-laptop`): the queue moves were made by hand. Default: leave it.

## For the data machine

- **October 2026 is not a held month** on the battery or the generator page, while the datacenter page, on the same price tables, counts it. The generator's snapshot is dated 4 October. Battery row 7, generator row 2.
- **The Grid replication's carbon and Ask groups:** `python replication/grid/figures_of_the_page.py` where the tables are held, committing the four files and `snapshot.json` (Grid row 2).

## For the old laptop

- **The daily chart of 2026-11-06** shows a raw entity id as its fact (`onrr_revenue:federal:onshore:...`; Research row 2).
