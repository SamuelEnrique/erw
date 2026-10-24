# Session 2410 report: method notes for this chain's four tables, every point acted on

24 October 2026, from 10:39 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. The notes were drafted by a helper beside sessions 2411 to 2414 and checked here. Precheck passed (`runs/c114/pre2410.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Which tables had no note:**
  - As chain 112's session 2375 found, every held table outside the running chains is described in a note, under its own name or a family note's.
  - The only tables with no note at all were this chain's four from sessions 2407 to 2409: `sne_panama_electricity_annual`, `sne_panama_generation_monthly`, `amm_guatemala_generation_monthly` and `statsmu_mauritius_electricity_annual`.
  - Sessions 2412 and 2413's two tables are left to session 2415, with its notes for the own choices.
- **Three method notes,** in `docs/methods/` (`sne_panama.md` for both Panama tables), each checked as session 960 checked its notes, against the code, the table and the workbooks. The helper found no value that differs from the workbooks. The Method cells are set.
- **Every point was acted on:**
  - **Panama:**
    - Type 2, "Vapor (Bunker)", is steam plants: mostly coal from 2011 (BLM Carbon) and wholly coal from 2015 (with Minera Panama). The variable keeps its name, and the docstring and header say so.
    - Net production is GE-13's net generation plus purchases, the purchases being the net interchange (its footnotes 2/ and 3/). It is therefore national, and above gross generation in the 14 years of positive purchases, not in 2000 only. Neither sheet says whose maximum demand is given.
    - The Canal Authority's row starts in 2000, so the total breaks there. Its footnote /c/: the Canal can pass the interconnected system only 40 MW.
    - The interconnected system's row holds wind, solar, natural gas and biogas too, though its label names only types 1 to 6.
    - The isolated systems hold 40.6 GWh of natural gas in 2021, which `generation_gross_natural_gas` does not.
    - The annual header gains a line of definitions, and the monthly one names the 2000 break.
  - **Guatemala:**
    - Generation is the interconnected system's executed dispatch, distributed renewable generation (about 3 to 4 per cent) included.
    - `demand_sni` is generation plus imports less exports, so the system's losses are inside it.
    - The workbooks' labels are "GENERACION POR TIPO DE RECURSO" and "TRANSACCIONES INTERNACIONALES (NETO)", not "por tipo de combustible" and "regional".
    - The header's retrieval range now runs earliest first.
  - **Mauritius:**
    - Capacity includes plants not exporting to the CEB (Table 7's footnote), and effective capacity is not defined.
    - Generation is every producer's, the independent producers' own use (203 to 245 GWh a year) included; their plants burn all the coal.
    - `electricity_sold` is the CEB's sales, so generation less sales is not losses.
  - **The reports, corrected in place, each saying so:**
    - session 2407's: below Ember's demand by 0.8 to 2.6 per cent from 2000 to 2018, net production above gross in 14 years, and exports already netted;
    - session 2408's: the demand falls in 2020, the 2025 workbook was asked 20 seconds before the others, and the transactions are international.
  - **The tables were written again offline,** with the same rows. The rewrites' metadata patches met the branch's rows; the union resolver and the dedupe kept each table's newest.
  - **"Not read" in `docs/licenses.md` for AMM** means no verdict, which an internal table under unstated terms does not have, as for CEB and Ghana's Energy Commission. Nothing was changed.

## Errors

- **Sessions 2407 and 2408's reports and the three connectors' headers carried the slips above.** Each is corrected in place and says so.
- **The second and third rewrites' metadata patches did not apply** while the first's conflicts were open. They were applied again after the first was resolved, and resolved in turn.

## Decisions made without you

- **`generation_gross_steam_bunker` keeps its name,** with its meaning in the header, rather than a rename that the archive would carry as a second series.
- **No note for tables already described in family notes.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/sne_panama.md`, `amm_guatemala_generation_monthly.md`, `statsmu_mauritius_electricity_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/sne_panama.py`, `amm_guatemala.py`, `statsmu_mauritius.py`
  - sessions 2407 and 2408's reports
  - `docs/coverage.md` (Method cells), the coverage and archive manifest rows
- On the data machine only: `runs/c114/s2410/` (the notes' drafts, the helper's check scripts and `POINTS.md`, `act.py`).
