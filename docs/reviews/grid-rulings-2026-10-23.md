# The Grid tool: what waits for Samuel (chain 077, 23 October 2026)

Session 1162. Every item under "For Samuel's ruling" in the reports of sessions 1150 to 1161 (`archive/sessions/SESSION_1150_REPORT.md` to `SESSION_1161_REPORT.md`), one a line, in plain words, each with a recommendation and the session it came from. Sessions 1150, 1151, 1152, 1153, 1154 and 1157 put none. Nothing here was changed by the chain: each waits for a yes or a no.

## The page's words

- The Mix tab says "the latest EIA has published" (and "EIA publishes each grid's hourly demand an hour or so after the hour") of the newest hour the warehouse holds, which was 21.6 hours old when read. Recommendation: say "the latest hour the warehouse holds", with its age in hours, as the energy mix panel already does. (Session 1161)
- The Flex Alert scorecard (`/grid/caiso/alerts`, "Limits") says CAISO's emergencies report "runs to 2025-04-30"; since its revision of 9 October 2026 it runs to 8 October 2026, with no alert after 2024. Recommendation: "runs to 2026-10-08, with no alert after 2024". (Session 1155)
- The scorecard's "Year by year" note says the bars are "green where demand was below the model", but they have been drawn in ink since session 319, and the other sign in cardinal. Recommendation: both signs in ink, the sign written on the bar, the note "ink bars: the estimate; whiskers: the 90 percent interval". (Session 1159)
- California's hourly mix is called "not held yet" in one place and "Not shown: ..." in another, for the same ruling. Recommendation: the withheld panel's words in both places. (Session 1159)
- A fuel with no share leaves its cell blank in the energy mix tables, where the brand writes "not held". Recommendation: "not held". (Session 1159)
- Each new panel gives its headline figures in sentences and ends with its own source sentence, not the shared source line. Recommendation: keep the sentences (they say the window and the age); add the shared source line only if you want every table named the same way. (Session 1159)

## The design

- The scorecard's pooled answer is set at 18 px, off the type scale, in a box with a cardinal left bar. Recommendation: the brand's summary sentence (serif, 20 px), no bar. (Session 1159)
- A cardinal left bar on fog marks several notes (California's withheld mix, the data-break note, the carbon note, held rows, and on the battery page), which is not one of cardinal's three jobs. Recommendation: a fog panel with a rule-coloured edge, changed site-wide in one landing. (Session 1159)
- The energy mix's chips and view links mark the chosen one in cardinal fill, where the grid picker and the tabs use ink. Recommendation: ink, as the shared segments. (Session 1159)
- The hover cards of the map and the gravity shape are white with tight padding on a fog frame; the brand's card is fog with 8 by 12 px padding. Recommendation: a white frame with a rule-coloured edge, and the shared charts' card. (Session 1159)
- The grid in view, highlighted in a table, also takes the ink rule a total row has above it. Recommendation: fog only, no rule, for a highlight. (Session 1159)
- "Stored answers" in the Ask column is drawn at 20 px, the size of the column's own "Ask" heading. Recommendation: 16 px sans, weight 600, for a heading inside the Ask column. (Session 1159)
- The energy mix's and the Clean tab's own titles are drawn at 24 px, above 20 px section titles. Recommendation: keep them (a view's title is the page's second size, as on the battery page). (Session 1159)
- A line of the map and of the gravity shape answers a mouse and a tap but not the keyboard; its figure is in the keyed panel under the drawing, which the keyboard reaches. Recommendation: keep it so; a keyboard stop on each of about a hundred lines would bury the regions. (Session 1158)
- The shared charts answer a mouse or a tap, not the keyboard; their Chart and Table switch carries every value. Recommendation: keep the switch as the keyboard's route now, and name a session for a keyboard walk through a chart's points, a shared change across the site. (Session 1158)

## The data and licenses

- The map gives a line's MW only for the grid in view's ties, in the hour the checked panel holds. Recommendation: keep it (every MW written is then a checked figure); allowing every tie's MW would write numbers the server panel does not hold. (Session 1156)
- Migration 036 (the indexes of session 580) is still neither applied nor refused. Recommendation: leave it unapplied; session 1160 timed every read of the three pages and none needed an index. (Session 1160, carried from session 580)
- Colour contrast was not judged on the three pages: no stylesheet could be read without a build. Recommendation: not a ruling but a check, run AccessLint's live scan on the next build and rule only on what it finds. (Session 1158)

## To finish: needs a person or a build, not a ruling

- The combined landing of sessions 1152 to 1162 (landing B): `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the commit, `compare`, every difference listed. Waits for `db_probe` to answer 0 and memory enough for a build. (Sessions 1152 to 1161)
- At that landing, rewrite the check-values floors from a passing run (`CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid,/network`), so the new panels' keys and the new addresses (`mixp=month`, CAISO's Network tab) have floors. (Sessions 1151, 1152, 1154, 1155)
- Then rewrite `site/scripts/check-methods-keys.json` from that run (`node scripts/check-methods.mjs --values <file> --write`) and run `check-methods.mjs` again: today it reads keys recorded before the chain. (Sessions 1154, 1162)
- On that build: `check-values` on `/grid`, `/grid/caiso/alerts` and `/network`; `test-network.mjs` and `check-network-map.mjs`; `check-390.mjs`, `check-links.mjs` and AccessLint's live scan; the build's time (under 60 seconds asked; 65 and 69 seconds at the last gates). (Sessions 1153, 1156, 1158, 1159, 1160)
- Screenshots at 1280 and 390 px, never taken for lack of a build: `docs/brand/review-1153/` (after), `review-1154/`, `review-1155/`, `review-1156/`, `review-1158/`, `review-1159/` (before and after), and the Grid steps 17 to 27 under `review-1161/`. (Sessions 1153 to 1161)
- Walk the trader's path Grid steps marked "from the code" (19, 20, 21, 24, parts of 22 and 25) on landing B's build and fill their values. (Session 1161)
- `npx tsc --noEmit -p .` unbounded, once memory allows (session 1161's run hit the heap limit; no TypeScript changed since session 1160's pass). (Session 1161)
- The after snapshot of chain 077's queue pushes, compared with `runs/snapshots/q077-before`. (Session 1150)
- When chain 075 records an evaluation with its tool results, add it to `RUNS` in `site/scripts/build-grid-ask-examples.mjs` and rebuild the stored answers. (Session 1157)
