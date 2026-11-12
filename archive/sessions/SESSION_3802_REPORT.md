# Session 3802 report: the tab and the siting gaps file

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 17:02 to 17:10 UTC. Opus 5.5. Model spend USD 0. Requests: none.

## Read these first

- **The All grids tab draws the CAISO's own reserve margin** on its CAISO rows (on `wip/c215-data`, commit `9e69d839e`):
  - "reserve margin 30.8%, summer 2026", keyed `allgrids|reservereport|<row>`;
  - the tip adds the 25 percent the CAISO finds is needed for a 0.1 LOLE, the 2,547 MW surplus and the CEC's 1-in-2 peak of 46,844 MW, each with its page in the assessment.
  - ERCOT's line stays its CDR. The other grids read "reserve margin not held", whose reason now names both held reports.
- **How:**
  - `warehouse/derived/siting_page.py` reads `iso_reserve_margin_reports` into `headroom.json`'s `reserve_reports` (the newest document of each grid, its figures as printed, with pages);
  - `site/lib/siting.ts` has `reserveReport` and the key;
  - `AllGridsView.tsx` draws the line.
  - Only the new key was added to the committed `headroom.json`; every other figure stands.
- **Checks:**
  - the tab's 41 test files (169 tests, OK);
  - `npx tsc --noEmit` on the branch's two site files in the main checkout (0 errors);
  - the read at 390 and 1280 with the internal view runs on the gate's build (session 3807).
- **The method:** `docs/methods/siting.md` version 12 and decision 37 (an operator's own seasonal assessment fills the reserve line where held, never compared across grids).
- **The siting gaps file:** a new dated state section, "12 November 2026, evening (chain 215)".

## Decisions made without you

- **The CAISO's achieved margin is the figure drawn,** not the required one or the surplus. It is the reserve margin the assessment finds, the same kind of figure as ERCOT's line; the others are in the tip.

## For Samuel's ruling

- None.
