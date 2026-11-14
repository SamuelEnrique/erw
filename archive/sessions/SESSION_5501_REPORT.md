# Session 5501 report: chain 269, item 1: the five read on main, six faults fixed

Energy Research Warehouse (ERW). Chain 269, portable laptop window P1, 14 November 2026, about 08:35 to 09:00 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5500-closeout`.

- **Where read:** production (`https://erw-flame.vercel.app`), main at `85e5b2eeb` as deployed at 08:28 UTC, the tree this stack was cut from, in the internal view (the token posted as the site's form does), at 1280 by 900 and 390 by 844 as a phone, with `site/scripts/browser.mjs`. **No local build:** 1.0 GB free at 08:26 UTC and 1.7 GB at 08:50, under the chain's 2 GB rule.
- **Pages:** the five defaults, then MISO's and ERCOT's Grid pages, the Grid's Network tab, the battery's CAISO case, the datacenter's all-grids view and the generator's CAISO solar: 22 reads. Every one: page width equal to the window, no element past the right edge, no exception, no "NaN" or "undefined".
- **Accessibility:** `site/scripts/a11y-axe.mjs` at 390 on the five defaults: 0 rules broken on each (`runs/a11y_5500_390.out` in the main checkout).
- **Grid row 4 holds on production:** MISO reads "6:00 PM EST" in the Mix sentence, the hour cards and the conditions.
- **Against each done line** (roadmap item 2): the three economics pages carry the method note, the replication (CSV, do-file, Python mirror), "Checked against" and the decisions block on the face; Research links its notes and each card's three files; the Grid is one page with its decisions block, but no view links its replication or cross-checks (the note's open ruling, now G1 of the signature pack). No note is signed.
- **Six new faults, each fixed with a test** (`tests/test_session5501.py`, 11 tests):
  - Battery row 12: "1 days in all" under the income table: "day" when one.
  - Battery row 13: "Price years" named its leave-out windows by the table's ids ("less uri 2021"; on CAISO "less caiso notices 20230815", ten of them): now "less Winter Storm Uri (February 2021)", "less CAISO's notice days from 15 August 2023" (`site/lib/priceyears.ts`; the names held to `lib/batterystack.ts`'s EVENTS by the test).
  - Generator row 4: the spans table's capture price 23.20 and price of every hour 32.10 beside the headline's 23.27 and 32.17, with nothing on the face to say why: a line under the table names the two weighings and gives the four figures with their existing keys (solar and wind); the note's section 9 updated.
  - Datacenter row 5: `ercot_large_load_status` named twice in the source line: dropped; `SourceLine` names each table once.
  - Automated Analysis row 7: today's chart printed its record's figures as raw floats ("sigma 26822.265161999996"): rounded as the chart-maker does ("26,822"; whole numbers whole), the form the value checker's `digest_chart` rule already accepts (`site/lib/researchrules.ts` figureText).
  - Grid row 6: "US Lower 48: today so far" over 13 November on 14 November: the heading now names "the latest day EIA has published, so far"; `tests/test_session133.py` and `site/scripts/check-mix.mjs` follow the words.
- **Known rows still open, unchanged:** battery 7 and 10, datacenter 4 (the price years and ERCOT's October: window A), generator 2 (the snapshot: Samuel's ruling 1 and window A).
- **Tests:** the new file, 11 passed; the 101 test files that name a changed file, 1,391 passed, 79 skipped, 0 failed (8 min 13 s).

## Decisions made without you

- Production read in place of a local build for item 1: production is main's own build of the same tree; the stack's build waits for 2 GB free.
- The Grid heading's new words ("the latest day EIA has published, so far") are a fix of a false word, made here; tell me if you want other words.
- The CAISO events are named by their first day ("CAISO's notice days from 15 August 2023"), the only day the window's id carries; the leave-out boxes give each event's full days.

## For Samuel's ruling

- None new beyond the signature pack's (G1: the Grid page's "Checked against" line).
