# Session 7001 report: the company database's data faults (companies rows 17 to 24)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0. No request to a publisher (the EIA-861 file read was the one held under `warehouse/raw/eia861/`).

## What a reader of `/companies` now sees that was wrong (the files rebuilt on the branch; they reach the page when the branch lands)

- **Callaway** (1,190 MW) is on Union Electric's page (`/companies/eia-19436`: reactors 0 before, 1 now); **Brunswick 1 and 2, Harris and Robinson** on Duke Energy Progress (`eia-3046`: 0 before, 4 now); **Millstone 2 and 3** on Dominion Energy Nuclear Connecticut (`eia-5221`: 2). The NRC's "Union Electric Co.", "Ameren UE" and "AmerenUE" no longer stand as three companies of their own.
- **NextEra Energy Resources Interconnection Holding(s)** is one company (three ERCOT queue positions); **EDP Renewables North America's** ERCOT queue name joins EIA's operator `eia-61785`.
- **Eight wrong merges split:** `/companies/eia-56982` is PBF Power Marketing (a power marketer), and Kern Community College District's plant is `/companies/eia-56982-860`; the same for DRW Energy Trading and Santa Teresa Solar (`eia-67114-860`), and six more.
- **Kinds and segments from public rows only:** Constellation Energy Corporation's kind was "IPP, set by energy_deals seller of a PPA" (a held table); it is now "other, no rule" until a public row says more. Google's segment was "nuclear" from held deals; it is now "storage" from its 7 public rows.
- **Grids:** Florida Power & Light listed "MISO, PJM" (EIA-861's "Operating in these RTOs", which EIA's own 2025 file marks for FPL); now no grid. Trico Electric Cooperative (Arizona) no longer lists ERCOT; Liberty Power Corp. (Florida) no longer six grids.
- **A power marketer kind:** 439 listed companies that were "other" are "power marketer" (EIA-861 ownership); "other" falls from 3,114 to 2,707 listed.
- **`owned_mw`** in the index: Calpine Corp's footprint of 1,045 MW now has its column (the page's column is a code row).
- **Built 2026-11-16** (the files were built 2026-11-06).

## Commits (on `wip/c301-data`)

- `b67b7cf92` the code: `norm` drops EIA-861's state tag and reads "Conn" as Connecticut; six reviewed aliases with their rows as evidence; `split_anchors` (a power marketer's number whose EIA-860 names share no word with its EIA-861 names: exactly the eight the review found); `RTO_STATES`; the kind "power marketer"; `segment_of_mentions` shared by the builder and the pages; `companies_page.public_kind`; `capital_page` writes `buyers` a kind; test 7001 (14 tests: all fail on main's code, all pass here).
- `8645fe138` the method note `docs/methods/companies.md` brought to the rules.
- `347fde024` the tables rebuilt under the data lock (14,033 companies, 25,986 aliases, 97,198 links), validated (exit 0), coverage `--only`, archived (bucket and local), the page files (12,724 listed) and `capital.json` (held: the count only).

## Each row's new state

- Rows 17 to 23: fixed (`b67b7cf92`, rebuild `347fde024`). Row 22's buyer count and kind list, and row 23's column, need a page change: `docs/state/data_ready_c301.md` rows 1 to 3.
- Row 24: fixed (the rebuild).

## Decisions made without you

- **Which side of a split keeps the id:** the EIA-861 rows (the utility number's own registry) keep `company:eia-<id>`; the EIA-860 rows take `company:eia-<id>-860` with the same `eia_utility_id`.
- **EDP's queue name** is read as EIA-860's operator id 61785 (seven plants operated under it); 61757 appears only as an owner id.
- **RTO footprints by state** are written in the builder from each RTO's own member map (SPP with Colorado for its western expansion); a utility in a state two RTOs share keeps both flags it marks.
- **Union Electric's parent** stays the NRC's "AmerenUE" (the field as written); no reviewed parent was added without a held row naming Ameren Corporation.

## For Samuel's ruling

- None new.
