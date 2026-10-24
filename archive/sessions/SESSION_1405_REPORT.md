# Session 1405 report: the Ask column's examples by tab

24 October 2026, from about 06:55 to 07:10 UTC, on samueloldlaptop (the code machine, the old laptop), the sixth session of `queue/done/100-day-26-october-code-grid-tool-4.md`. Branch `wip/1405-grid`, cut from `wip/1404-grid` (sessions 1152 to 1404 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1405`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; same-figures read Supabase with the anon key through its proxy (90 distinct reads).

## Read these first

- **The stored answers under the Ask box are ordered by the tab on screen.** The page now gives the panel its tab (`<AskExamples grid={grid} tab={view} />`); `site/lib/gridask.ts` `orderByTab` puts first the answers that read a table of that tab, then the rest, each part in the stored order (ties keep the stored order).
- **The selection is unchanged.** The five at most a grid are chosen as before (`slice(0, max_examples)`), then ordered. No answer is added, dropped or changed; each `<details>` stays closed; the held ones are held as before.
- **An answer's tab comes from its own tables**, the `sources[].tables` of the data file, through `ASK_TABLE_TAB`. That map is built once in `gridask.ts` from `lib/gridtables.ts`'s `GRID_VIEW_TABLES`, and names no table itself, so the two cannot part. The test checks this.
  - **Network** (which Gravity shares, since it reads the same list): a table of the Network list that the Mix list does not name, or an interchange table.
  - **Clean**: a table of the Clean list that the Mix list does not name, or a carbon, emissions or clean energy table.
  - **Mix**: any other table of the Mix list (generation, demand, prices, the mix, storage).
  - **No tab**: a table no list names.
- **What moves, on the committed data file:**
  - ERCOT on Clean: q05 (carbon) first.
  - PJM on Clean: q29 first.
  - ISO-NE on Clean: q18 and q26 (its two public carbon answers) first, then the two held.
  - The Lower 48 on Mix: p09 (hourly demand) first.
  - The Lower 48 on Clean: p02 and q19 (carbon) first.
- **What stands:**
  - CAISO, SPP, MISO and NYISO keep their order on every tab. Their answers read the cost of power, merchant revenue, the battery stack, curtailment, day-ahead hub prices and the NYISO queue, and no tab lists those tables.
  - Every grid keeps its order on Network and Gravity, because no stored answer reads an interchange or network table yet.
- **Two new attributes in the markup, no new words:** `data-ask-order` on the section (the tab used) and `data-ask-example-tab` on each `<details>` (its tabs). Neither has a `data-check` key.

## What to review

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=us48&view=mix#ask`. Under "Stored answers", the first question is "What was the highest hourly demand in the US Lower 48 ...".
3. Open `https://erw-flame.vercel.app/grid?grid=us48&view=clean#ask`. The first two are the carbon questions ("What was the average of the nine monthly carbon intensities ...", then "What was the average monthly carbon intensity of US Lower 48 generation over 2024?"), then the demand question.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean#ask`. The first is "What was the carbon intensity of ERCOT's demand in January 2025 ...". On `view=mix` the order is the stored one.
5. Open `https://erw-flame.vercel.app/grid?grid=isone&view=clean#ask`. The two carbon answers come first, then the two in "license needed" words.
6. Open `https://erw-flame.vercel.app/grid?grid=caiso&view=clean#ask`. The order is the same as on Mix.

These addresses show the change only once the chain's combined landing has deployed. Until then, read it on `wip/1405-grid`.

## Checks

- Precheck: run by the orchestrator, exit 0.
- `node --import ./scripts/alias-register.mjs scripts/test-grid-ask.mjs`: exit 0, 602 of 602. Added:
  - the map: every listed table has one tab, and it is a tab whose list names it; 23 tables' tabs named; 7 unlisted tables have none; `gridask.ts` names no listed table itself; Gravity orders as Network;
  - each of the eight grids on each of the four tabs: the same examples, count, label and holds; the tab's examples first, each part in the stored order; the exact order;
  - without a tab, the stored order; Gravity and Network give one order;
  - fixtures: ties; an answer of two tabs is first on both; a refusal; the five are chosen before the order; the input list is not changed.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs`: exit 0, 72 cases (was 68).
  - New check `order`: the given words appear in the block in that order.
  - The four existing `ask` cases now carry their order.
  - Four cases added: ISO-NE on Clean, the Lower 48 on Clean and on Network, ERCOT on Clean.
  - Mutation: with the tab not passed (`null`), exit 1, and exactly the four reordered cases fail (ISO-NE on Clean, the Lower 48 on Mix and on Clean, ERCOT on Clean). The source was restored.
- `test-grid-files.mjs`, `test-grid-failed-reads.mjs`, `test-grid-390.mjs`, `test-grid-addresses.mjs`: exit 0 each.
- `same-figures.mjs`: before `833be774` (the tip of `wip/1404-grid`, a temporary detached worktree with its own junction, both removed), after this tree. 8 addresses, the four tabs of ERCOT and of the Lower 48. Exit 0, every page the same, 592 figures, 90 distinct requests, 0 new after.
- `python -m unittest`, one module at a time, each exit 0:
  - the modules that read the changed site files: `test_session1152`, `1153`, `1154`, `1155`, `1157`, `1158`, `1159`, `1165`, `1166`, `1167`, `1170`, `1171`, `1172`, `1174`, `1179`, `1180`, `1181`, `1183`, `1184`, `1185`, `1404`, `168_network`, `237`, `266`, `299`, `401`, `416`, `473`, `502`, `538`, `54`, `78`;
  - the modules that read `docs/methods/grid_network.md`: `109`, `1156`, `1162`, `1175`, `1176`, `1182`, `1186`, `1188`, `124`, `180`, `180b`, `193`, `247`, `381`.
- `npx eslint` on the five changed site files: exit 0.
- Type check through the junction: `npm run content`, `npx next typegen` and `npx tsc --noEmit -p .`, exit 0 each. The junction was removed with `rmdir`; the main copy's `node_modules` is intact.
- Not run, as the brief says: the build, check-values (no figure added or changed), check-routes and screenshots (not taken, no build).

## The landing

- None in this session. It lands with the chain's combined landing. Pushed: `wip/1405-grid`.

## To finish

- Land with the chain. The visitor-facing difference is the order of the stored answers on the Clean tab (ERCOT, PJM, ISO-NE, the Lower 48) and on the Mix tab (the Lower 48), plus the two `data-ask-` attributes. No figure moves.

## Decisions made without you

- **A table's tab is decided in the order network, clean, mix.** The lists overlap: the Mix and Clean tabs draw the same files, and the Network list names carbon, demand and hub price tables too. By list membership alone, a carbon table would be on three tabs.
- **Tables on no tab's list get no tab**, rather than one guessed from their names (for example, `iso_dam_hub_prices` is not called a price table of Mix). This keeps the map the lists' own, so it cannot drift from them. It also means CAISO's and SPP's price answers stay unordered on Mix.
- **An answer that reads tables of two tabs is first on both.**
- **The five are chosen first, then ordered**, so a tab never brings in a sixth answer.
- **`tests/test_session1157.py`'s pin of the page's line was changed** from `<AskExamples grid={grid} />` to `<AskExamples grid={grid} tab={view} />`, because the panel needs the tab. Both of its assertions are kept and one is added (the panel is drawn once). No assertion was removed.
- **The order is computed in `gridAskExamples` (a fourth optional argument)**, so the test and the panel share one function. Without a tab, the order is the stored one.

## For Samuel's ruling

- Whether the tables on no tab's list (the cost of power, merchant revenue, day-ahead hub prices) should count as Mix for this order. That would move CAISO's and SPP's answers on Mix, and would need a list of their own in `lib/gridtables.ts`.

## Files

- Changed:
  - `site/lib/gridask.ts`: `AskTab`, `askTabOfView`, `ASK_TABLE_TAB`, `askTabsOf`, `orderByTab`, and `gridAskExamples`'s `view`.
  - `site/components/grid/AskExamples.tsx`: the `tab` prop and the two attributes.
  - `site/app/grid/page.tsx`: one line, `tab={view}`.
  - `site/scripts/test-grid-ask.mjs`: assertions added.
  - `site/scripts/test-grid-render.mjs`: the `order` check, `order` on the four existing ask cases, four new cases.
  - `tests/test_session1157.py`: the pin updated, one assertion added.
  - `docs/methods/grid_network.md`: the new section "The Ask column, by tab (chain 100, 24 October 2026)", with its Decisions line.
- New: this report.
