# How it works: the five tools

One document a tool, written on 2026-10-13 (session 249) for the person who shows the tool and has to answer for it, and refreshed the same day (session 260) once all five pages were on `main`. Each has the same seven parts, in the same order, and a last part that says where every number in it was read.

| Tool | Address | Document | Written from |
|---|---|---|---|
| What a battery earns | `/cost-of-power/battery` | [the review pack](../reviews/packs/battery.md) (session 263; the note it replaces is removed) | `wip/263-battery-pack` from `afacb21e` (the page as merged in session 234, California as session 257 added it), 2026-10-14 |
| What a generator earns | `/cost-of-power/seller` | [the review pack](../reviews/packs/generator.md) | session 264, 14 October 2026: the review pack replaces the note (sessions 249 and 260), on `wip/264-generator-pack` at `3f694726` |
| What a datacenter pays | `/cost-of-power` | [the review pack](../reviews/packs/datacenter.md) | session 265 (14 October 2026), from `afacb21e` on `wip/265-datacenter-pack`: the pack replaces this folder's note (sessions 249 and 260), whose content it holds |
| The Grid tool | `/grid` | [grid.md](grid.md) | rewritten by session 260 from `main` at `34b468fa` (the tool landed as `01161064`) |
| Research | `/research` | [research.md](research.md) | rewritten by session 260 from `main` at `34b468fa` (the page landed as `01161064`) |

## The seven parts

1. What it is for, and for whom.
2. The model, in numbered steps.
3. Every assumption, its default and its source.
4. The cross-checks.
5. What it cannot see, ranked by how much it moves the answer.
6. The ten hardest questions, each with the honest answer and the number.
7. A five-minute demo, click by click.

## How to read them

- **Every number is one the repository already holds:** a methods document, a session report, a check script, a card's own file. The last part of each document names the file and the place. Where the repository holds no number the document says "no number held"; nothing was estimated to fill a line. The battery document's figures once marked **[c]** (computed with the page's own library from the table of 2026-10-13; the script and its output stay in [`computed/`](computed/) as the record) are, since session 263, in `docs/methods/battery_earns_algorithm.md`, section 11.2, and checked against the live table by `site/scripts/check-battery-figures.mjs`: the battery's review pack carries no [c].
- **All five pages are on `main`.** Session 249 wrote four of the five from a branch, on the night the code machine rebuilt the pages. All four landed on 13 October 2026. Session 260 rewrote the Grid tool's and Research's documents from the landed pages and read the other three against the pages as they stood on `main` that evening.
- **No demo path was clicked through in a browser.** Each was written from the page's code, its check scripts and its data. Every page is in review (`site/lib/release.ts`), so a demo starts by opening the internal view.
- **The screen is newer than the page.** Prices and the live set are rebuilt daily. A figure here names its months; when the screen differs, the screen is right and the document is due an edit.
- **A number that moves is fixed in its source first** (the method, the code), then here. `tests/test_session249.py` and `tests/test_session260.py` hold the form of these documents, the routes their demos name and the files they cite, not their numbers.
