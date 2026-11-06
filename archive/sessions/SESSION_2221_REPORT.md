# Session 2221 report: the Colorado River Storage Project's power reservoirs above Lake Powell, a third source of the session's own choosing

24 October 2026, from 02:08 UTC, on lab-desktop (the data machine), the twelfth session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended, run beside session 2218's last steps. Model spend USD 0. Pulls: 18 requests of 20 (below).

## Read these first

- **Why this source:** session 2211 took Lake Powell and Lake Mead. Upstream of Powell, the Colorado River Storage Project runs four more federal power plants on its own reservoirs: Flaming Gorge on the Green River (Utah), and Blue Mesa, Morrow Point and Crystal, the Aspinall Unit on the Gunnison (Colorado). Their levels and turbine releases set WAPA's CRSP hydropower. Reclamation's hydrodata publishes all four in the same form, under the same host and the same verdict (record 173). No queue file plans them, and the chains running beside this one take Ontario, Europe's supply, the UK's gas, Norway, France, Spain, Brazil, Australia and FTA's and EPA's data.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `usbr_crsp_reservoirs_daily`, 330,293 rows, 1962-11-01 to 2026-10-22.
  - Four reservoirs: 917 Flaming Gorge, 913 Blue Mesa, 914 Morrow Point, 915 Crystal. The ids come from Reclamation's own site map, read first, not guessed.
  - Four variables: pool elevation (ft), storage (acre-ft), power release and total release (ft3/s). The data type numbers come from the dashboard's list (49, 17, 39, 42).
  - A day not yet ended when its file was fetched is left out (the connector's `ended_days`, Mountain time). None was: every series ends on 22 October.
- **The cross-check** (`runs/c098/s2221/cross.py`, `cross.out`), against the Aspinall Unit page read in this session:
  - **Elevations agree with the full pools:** Blue Mesa's highest is 7,519.64 ft (page 7,519), Morrow Point's 7,163.79 (7,160), Crystal's 6,763.19 (6,755).
  - **Storage agrees at Morrow Point only:** at full pool it is a median 116,937 acre-ft, 0.998 of the page's 117,190.
    - Blue Mesa's is 824,289 (0.876 of 940,800) and Crystal's 17,490 (0.673 of "about 26,000"), steady across the decades.
    - The pages read do not say what Reclamation's storage figure leaves out. The docstring says so.
  - **Downstream order holds:** each year from 2016 to 2025, total release grows from Blue Mesa to Morrow Point to Crystal, as tributaries join between them.
  - **Reclamation's own oddities, kept as published:**
    - Power release is above total release by more than 0.5 cfs on 5,275 of 82,560 days. Of these, 5,015 are Flaming Gorge's, most from 1969 to 2004, by a median 2.4%.
    - Morrow Point has 49 negative releases (1973 to 2001).
    - Blue Mesa's and Morrow Point's first years are month-end values.
- **Its method note** (drafted by session 2218's helper, `docs/methods/usbr_crsp_reservoirs_daily.md`) found those points. The docstring now states them, and the note's Method cell is filled.

## The pulls

1. Reclamation's hydrodata site map (read 357), for the site ids.
2. The Aspinall Unit page (read 358), for the full pools, capacities and nameplate (Blue Mesa 86.4 MW, Morrow Point 173.3, Crystal 31.5).
3. to 18. The sixteen data files, four sites by four data types, all HTTP 200. They were seeded into the raw store, and the trial and the write read them offline.

www.usbr.gov's robots file was read in session 2211 (it disallows only /pn-bin and /gp-bin) and not asked again.

## Errors

- **The first write's validation failed:** `ft` and `acre-ft` (Decisions 71 and 72) are on this branch's validator, not yet main's. Run again with the branch's validator, it passed.
- **The write's metadata patch met session 2218's rows in the same working tree.** Three later patches did too, leaving duplicate rows in coverage, the archive manifest and `docs/coverage.md`. Each table's newest row was kept (`runs/c098/s2218/dedupe.py`); no row is twice.

## Decisions made without you

- **The CRSP power reservoirs as the session's own choice,** for the reasons above. Navajo and Fontenelle (also on the site map) were left out to keep within the ceiling.
- **A table of its own,** beside `usbr_mead_powell_daily` rather than inside it, with its own source id.
- **Power release taken beside total release,** since the turbine flow is what makes the power.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usbr_crsp_reservoirs.py`, `tests/test_session2221.py`, `docs/methods/usbr_crsp_reservoirs_daily.md`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (357, 358)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c098/s2221/`, `runs/license_reads/s2221/`, `runs/s2221_*`, `warehouse/raw/usbr_crsp_reservoirs/`.
