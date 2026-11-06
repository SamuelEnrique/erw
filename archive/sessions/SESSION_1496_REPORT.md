# Session 1496 report: the explorers' method note and the rows they draw as a download

Energy Research Warehouse (ERW), session 1496, chain 158, samueloldlaptop, 6 November 2026, 09:32 to 09:42 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1494-explorers`.

## What it did, with commits

- `fd5afc32e`:
  - `docs/methods/explorers.md`: for each of the three explorers, the question, the tables, the computation (none on the page), the tolerance, the limits and the download. The peak premium's eight thesis figures are written down as matched to the cent on 6 November.
  - The rows drawn as a download of their own. `ExploreFrame` takes `rows` (a table and the filters the site's download reads: entity, variable, a UTC window), and under the method link it prints "The rows drawn here, as CSV with the table's header: ..." linking `/api/download` with them.
  - The peak premium passes its hub over the years drawn; with a month chosen, the words say the download holds every month of those years. Demand growth passes its window's variables, every grid and year. Interconnection's rows are its queue's entities by prefix, which the route's filter does not read, so it keeps its whole-table download and the note says so.
- Tests: `tests/test_session1496.py` (the frame's line and its address; the route's filters; each page's rows; the note's six parts for each explorer): 6 passed. `tsc` with the main copy's packages: no error in the changed files (the 15 known ones are the build's generated content).

## Decisions made without you

- A link line under the method link, in the frame's own words and classes: content, not a change to the layout.

## For Samuel's ruling

- Whether `/api/download` should take an entity prefix, so the interconnection explorer can offer its queue's rows alone.
