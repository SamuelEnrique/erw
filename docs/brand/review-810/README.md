# Review 810: the Digest and Roundup pages and the emails at 390 and 1280

Session 810 (22 October 2026, portable-laptop) read `/digest`, `/digest/2026-10-21`, `/roundup` and `/roundup/2026-W41` and the two emails (the Digest of 21 October, the Roundup of W41) at 1280 by 800 and 390 by 844 over the DevTools protocol (`shot-810.mjs`: a shot of each and the measures in `measures-810.txt`; `links-810.mjs`: which links sit beyond 390 px). `before/` is production's internal view (erw-flame.vercel.app, main at 11:05 UTC) and the stored emails under `docs/digest/email/`; `after/` is a local build of `wip/807-periodicals` served on port 3807 by the landing gate (the pages) and the emails rendered by this chain's `email_digest.py` from the dry runs of sessions 807 and 808. No page's code changes in this session, so the pages measure the same before and after; no issue's text changes.

| What | Before | After |
|---|---|---|
| The pages' tables (1 on a Digest day, 4 on a Roundup) | each in a scroll container (`.prose-erw table`, `globals.css`), the page 390 px wide | the same |
| The chart image on a page at 390 | 358 px wide, whole | the same; its labels are the 1200 px drawing at a third, legible on a phone only by zooming (for the owner) |
| Links beyond 390 px on a page | 11 on every page: the header's collapsed menu items (The grid, Demand growth, Research, Terms and so on), hidden until their menu opens; the rest (73 on a Roundup) are the deals and datacenter tables' story links, inside their scroll containers | the same |
| The Digest email at 390 | laid out 980 px wide and scaled down (no viewport), its two tables not in a scroll container (570 px) | 390 px wide; the numbers table in a scroll container; the chart 360 px wide |
| The Roundup email at 390 | 980 px wide, three tables not in a scroll container (640 px) | 390 px wide; the two numbers tables in scroll containers |

What changed (`warehouse/news/email_digest.py`): every markdown table of an email is wrapped in a scroll container (`overflow-x:auto`), and the HTML has a head with the charset and the viewport (`width=device-width, initial-scale=1`). `tests/test_session810.py` holds both. AccessLint's unattended scan was not run: its MCP server is not reachable in this session (it is a user-level tool of the desktop app; `docs/tooling.md`).
