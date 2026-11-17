# The attention page (`/attention`) read as the reader it is for (session 7563, samueloldlaptop, 16 November 2026 Pacific, 17 November UTC)

Energy Research Warehouse (ERW). Asked by Samuel: the reader's read of chain 304's part B for the six tools of the first ten that had none. The tool reached the done line in chain 301 and 303 (`replication/attention/`, faults `docs/reviews/attention-faults-2026-11-11.md`, 25 rows).

**The reader:** the community-relations lead of a datacenter developer choosing between Virginia, Ohio and Texas for a 300 MW campus, who wants to know whether the news about datacenters, and about the power they draw, is turning against them, and where.
**The five cases:** (1) data centers in Virginia, week by week; (2) solar and wind in Ohio, and the Ohio places the stories name; (3) "What rose" for Texas in the newest week; (4) data centers in the United States, the newest week's Friction Index beside the weeks before; (5) a trend over the year 2026. On the page's own file, `site/data/attention.json` built 2026-11-16 09:24 UTC: 8,119 of 27,419 stories held are classified, the weeks of 5 October to 2 November 2026.
**How it was read:** the file's cells, kinds, places and rising rows read by `runs/7563_att_cases.py` (not in git); the view drawn to HTML by its own component as it opens (`site/scripts/test-attention-read.mjs`, 5 of 5). Not seen: no click, no hover in a browser, not the charts or the map (canvases), no layout at 390 px.

Part A's rows are cited by number and not written again.

## The cases, in one line each

| Case | What the page gives | Where it stops |
|---|---|---|
| 1. Data centers, Virginia | 2, 4, 2 and 1 stories in the weeks of 5, 12, 19 and 26 October, none on 2 November. Friction Index 50.00, 75.00, 50.00, 0.00 (1 of 2, 3 of 4, 1 of 2, 0 of 1): a political opposition; a moratorium, a rate case and one other; a permit denied | A Friction Index of three stories in four is printed as large as one of 16 in 49 (row 1) |
| 2. Ohio | No story of solar and wind named Ohio in any of the five weeks; the page says so in one line (part A's row 6). Places: Licking County (26 October) and Youngstown (19 October), each one datacenter story, no opposition | Five weeks cannot say more (row 5) |
| 3. Texas, "What rose" | All energy, Texas: 2.22 percent in the week of 2 November against 1.19 in the four before, +1.03, the only state that moved by more than one point | The week of 2 November holds 631 stories, the four before 1,954 to 3,146, and nothing on the table said so (row 2, fixed; row 3) |
| 4. Data centers, the United States | Friction Index 32.65 in the week of 2 November (16 of 49 stories; 10 political opposition, 5 protest) against 11.11, 16.48, 11.50 and 11.21 before | The same thin week; it is not hatched, since all its 631 stories are judged and it ended before the build (row 4) |
| 5. A trend over 2026 | The charts draw from the first classified week, 5 October 2026; the weeks from January 2025 are held and not classified | 19,300 held stories are not classified (row 5, needs the key) |

## The rows

Kind: `site` (fixed on this branch, with a test: `site/scripts/test-attention-read.mjs`), `data machine`, `browser`, `ruling`, `key`.

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 1 | The headline "Friction Index" for data centers in Virginia, week of 12 October | "75.00" in the headline's size, from 3 of 4 stories; the counts are in the note and the chart's hover (part A's row 12) | ruling | default: every index printed, its counts beside it. The other choice: a cell with fewer than ten stories prints its counts and no index |
| 2 | 3, 4 | "What rose in the week of 2 November 2026", its note | The change is a share of 631 stories against weeks of 1,954 to 3,146, and the table did not say so | site | fixed: the note says how many stories the week holds beside the classified weeks before it, and, where it holds fewer than half the fewest of them, that a share of so thin a week moves more with each story (`weekBesideBefore`, `besideWords` in `site/lib/attention.ts`) |
| 3 | 3, 4 | The week of 2 November 2026 | 631 stories held, against 1,954 to 3,146 in the four weeks before and 981 in the week after: a third or a fifth of a normal week | data machine | requested (row 308): find whether the news ingest missed stories from 2 to 8 November 2026 (the daily run was red from 6 November) and, if it did, read them again |
| 4 | 4 | The charts' hatching | A week is hatched when partly classified or still open at the build (part A's row 4); a closed, fully judged but thin week is drawn solid, and the page opens on it | ruling | default: the rule as it stands, with row 2's words. The other choice: hatch a week that holds fewer than half the stories of the fewest of the four weeks before |
| 5 | 2, 5 | Every chart | Five classified weeks of the 98 held: no year's trend, and a state's datacenter coverage is 0 to 4 stories a week | key | classify the 19,300 held stories not yet classified (January 2025 to September 2026). Not run (model spend USD 0); its cost is the classification step's cost a story times 19,300, which the data machine's dry run would price from the ledger |
| 6 | 1, 2 | The place select | One place at a time: Virginia beside Ohio or Texas, the reader's question, is two visits | ruling | default: one place at a time. The other choice: a second place drawn beside the first (A and B), as the page standard asks where a reader compares |
| 7 | 3 | `/attention`, "What rose", as it opens | The new sentence at the end of the note | browser | wanted (row 307) |
| 8 | 1 | `/attention` with Data centers and Virginia chosen, at 390 px | The friction chart's hover gives "3 of 4 stories report opposition" for 12 October; no sideways scroll | browser | wanted (row 308) |

**Counts.** Site, fixed: 1 (row 2). Data machine: 1 (row 3). Ruling: 3 (rows 1, 4, 6). Key: 1 (row 5). Browser: 2 (rows 7, 8).

**Words the reader would not know.** "judged stories" (the scorer's read; the headline's note gives the counts); "classified" (the model's sector and place reading). Both have hovers (part A's row 23).

**A test that fails before and after.** `site/scripts/test-attention-view.mjs` passes 33 of 44 in this worktree and in the main copy at `0ab3ec772` alike: the same 11 checks, not touched here.

## The figures this page shares with other pages

None: the indices are the page's own, counted from `attention_story_links`. The Roundup's memo figures that cite them are part A's rows 18 to 20. The places named (Loudoun County, Licking County, Youngstown) are the same places as rows of the datacenter tracker (session 7560), but a count of stories is no figure of the tracker.

## What this reader still cannot get from the tool, and why

- **A trend.** Five weeks are classified (row 5).
- **A sure figure for one state.** A state's datacenter cell is 0 to 4 stories a week (row 1).
- **Two states side by side** (row 6).
