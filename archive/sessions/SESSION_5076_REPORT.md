# Session 5076 report: chain 243, the Grid as one page, read at 1280 and 390

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 19:57 to 20:08 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read` (on `wip/5072-analysis`). Precheck passed (exit 0).

- **The local build was stopped.** `npm run build` of `wip/5072-analysis` under the build lock (taken at about 19:57 UTC) compiled (42 s) and was in its type check when Claude Code stopped it because the laptop was critically low on memory (three windows on 16 GB; 0.4 to 1.9 GB free through the evening). It was not started again: Claude Code's notice says to start it only when asked. The build lock was released at once. The prebuild's rewrite of `site/data/policy/paused.json` (line endings only) was put back.
- **Read instead on production** (`https://erw-flame.vercel.app`, main), in the internal view, with the site's own browser helper and a fetch of the addresses with the view's cookies: the stack changes no page's code, so the pages read are the stack's.
- **The one page holds.** `/ask` and `/ask?q=...` answer 307 to `/grid?grid=us48&ask=1`, the question carried; `/network`, `/network?shape=gravity`, `/network?view=uri_2021&grid=ERCO`, `/mix`, `/mix?view=clean`, `/mix?view=stress` and `/emissions` answer 308 to the `/grid` view that holds them, each word carried. A visitor sees the in-review page at every address.
- **Nine views at 1280 and 390** (the Lower 48: the opening view, Network, Gravity two ways, Clean, Mix, the Ask flag; ERCOT: the opening view and Clean): no sideways scroll, no exception, no broken word; the Ask panel beside every view (below it at 390). Pictures looked at: the Ask flag and Network at 1280, Gravity at 390 (the circles, the key, both tables, the Ask panel).
- **No new fault.** `/network?view=gravity`, an address tried here, opens Network: no page wrote it (the gravity shape was always `shape=gravity`, which opens Gravity). Recorded in `docs/reviews/grid-faults-2026-11-13.md`, "The read as one page".
- Memory before each browser read: 0.7 to 1.5 GB free; each read finished.

## Decisions made without you

- Production read in place of a local build for this item, the stack being free of page code; the build waits for memory and for your word.

## For Samuel's ruling

- **The local build on this laptop while three windows run.** Default: P1 builds only when at least about 3 GB is free; otherwise it reads production, as here.
