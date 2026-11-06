# Session 2923 report: the tab wired to what chains 147 to 153 hold

6 November 2026, about 05:33 to 05:42 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Two held tables now fill cells of the All grids tab** (commit `9ec9bfb3b` on `wip/c153-data`). Each figure is keyed, replicated and tested.
  - **Headroom, "generation with a signed interconnection agreement":** a last line, "<MW> MW signed", keyed `allgrids|signed|<row>` and written whole. Source: `interconnection_agreements_by_grid` (public, from Queued Up), the queue at the end of 2025. ERCOT 132,566 MW, CAISO 94,096, MISO 67,073, PJM 44,066, SPP 34,181, ISO-NE 8,609, NYISO 6,931. Its tip gives the requests, the active MW and the signed share.
  - **Utility, a county row's wires company:** a last line, "wires USD <x> <company>", keyed `allgrids|wiresrev|<row>`. Source: `eia861_delivery_only` (public), 2025.
    - Harris County (`ercot:HB_HOUSTON`, `ercot:LZ_HOUSTON`): CenterPoint Energy, **USD 10.5685 per MWh** (USD 500,370,500 of industrial delivery revenue over 47,345,506 MWh).
    - Travis County (`ercot:LZ_AEN`): Oncor Electric Delivery, USD 9.6730 (USD 716,457,500 over 74,067,446 MWh).
    - Both are the company's figures across Texas, as EIA files them, and the tip says so.
- **No figure the tab drew before moved.**
  - `warehouse/derived/siting_page.py` gains `signed_by_grid` and `county_delivery`, which are written from now on.
  - For this commit, the two keys were added to the committed `headroom.json` and `utility.json` (`runs/s2923/add_keys.py`, the builder's own functions). A comparison with the keys removed gives the committed files exactly.
  - A full rebuild would also have moved the planned generation, demand and carbon lines to newer months; that is the builders' daily work, not this step.
  - The Houston cell's main figure stays the county's largest seller (San Bernard Electric Coop). The wires company is a line beside it: delivery revenue is not comparable with a bundled seller's.
- **The replication** (`warehouse/replication/siting.py`, with `--tables`) counts both again from the tables' rows (`signed_figures`, `wires_figures`). Its figures equal the tab's: 132,566.1 MW; 10.568489858.
- **check-values:** `allgrids|signed|` is written whole, as an alternative of its own, so test 1069's pinned list stays as it was.
- **`docs/methods/siting.md` version 9**, decisions 33 and 34.
- **Tests:** `tests/test_session2923.py` (5), and the 37 test files that read the tab's code or files: 145 passed, 6 skipped.
- **`tariffs.json` is not wired.** No tab row sits in a registry utility's territory (Georgia Power, I&M, PGE, PG&E). PG&E's NP15 names no place, and SP15's Los Angeles County is not PG&E's.
- **The 390 and 1280 read:** chrome-devtools did not connect in this session. The tab's HTML is read from the landing gate's local build of this branch in session 2931, with the internal cookie, for the two data attributes. Each new cell gives a figure or "signed not held"; the wires line is drawn only where the county has a delivery-only company.

## Decisions made without you

- **The new keys added to the committed files rather than rebuilt whole**, so that no shown figure moves.
- **The wires company drawn beside the largest seller, not in its place** (decision 34).

## For Samuel's ruling

- **Whether the Houston rows' Utility cell should lead with CenterPoint** (the wires utility a large load connects to) rather than San Bernard Electric Coop, the largest seller among the county's filers. That would move a shown figure.
