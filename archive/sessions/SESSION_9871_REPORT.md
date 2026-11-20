# Session 9871: the five least-tested pages read as a reader (chain 610, part E)

Energy Research Warehouse (ERW). 20 November 2026, 20:41 to 20:50 UTC. The desktop's third window.

## What was done

- Counted, for every page, the test files that name its address or its files (`runs/c610w3/tests_per_page.py`, not in git). The ordinary pages with the fewest: `/curtailment/where-when`, `/queues/places`, `/storage/places` (two each), `/ai-energy`, `/industry` (three each); the pages with a bracket in their address are undercounted by the method and were left.
- `site/scripts/test-reader-pages-render.mjs` draws those five with the site's own code, without a build, and checks what a reader and a screen reader meet: one h1, no skipped level, named buttons, tips with their targets, captioned tables, images with words, and `/ai-energy`'s headline against its file. 29 of 29. `tests/test_session9871.py` wraps it.
- Branch `wip/9871-reader-pages-tests` (`e8318d9e1`), landing requested as row 13. No page changes.

## Noted, not changed

- The drawing prints React's warning that a list's children lack a unique key on one of the five pages; a reader sees nothing of it. Left for a session that builds.

## Needs the key

- Nothing.
