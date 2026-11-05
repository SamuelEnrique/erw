# Session 2785 report: the mix of electricity provided to Luxembourg's end users, 2009 to 2024 (STATEC's LUSTAT), a second own choice

26 October 2026, about 01:58 to 02:03 UTC, on lab-desktop (the data machine), chain 141, unattended. Precheck passed (`runs/c141/pre2785.out`). Model spend USD 0. Pulls: 6 requests of 20 (4 by the probe, 2 by the fetch).

## Read these first

- **Statbel's energy balance views tried first and set aside:** statbel.fgov.be's robots file is as session 2770 read it, and beSTAT has no robots file (reads 1583 and 1584). Its energy statistics page links six beSTAT views of the 2024 balance by product (read 1585). The electricity view was fetched: one year (2024), in kilotonnes of oil equivalent. Belgium's 2024 electricity consumption by sector is already held through Eurostat's nrg_cb_e (session 2757), so it was not written.
- **`statec_lu_supplier_mix_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statec_supplier_mix.py`, 196 rows, 13 entities, 2009 to 2024):
  - From LUSTAT dataflow DF_A4209, "National mix of electricity provided to the end-users (in %)", every key in one request.
  - `supply_mix_share` in pct: fossil, nuclear, renewable and other sources, and nine sources below them (hard coal, brown coal, natural gas, other fossil; biomass and biogas, wind, hydro, solar, other renewables).
  - **The suppliers' disclosed mix, not the generation in Luxembourg:** most of the electricity Luxembourg's end users take is imported. The renewable share was 21.3 per cent in 2009, 55.2 in 2016 and 66.5 in 2024.
  - **Compared every year within 0.15 points:** the four groups make 100, and fossil and renewable their sources. STATEC's figures differ in three cases, kept as published: renewables in 2019 (by 2.8 points), and the groups and renewables in 2022 (by 0.3).
- **Context, not a cross-check:** no held table measures the disclosed mix. Against `eurostat_renewable_shares_annual`'s electricity share for Luxembourg (6.2 per cent in 2015, 13.9 in 2020, 20.5 in 2024), the suppliers' renewable share is far higher (55.0, 64.3, 66.5): the disclosed mix counts the certificates attached to imported power, and the directive's share counts generation against consumption. The note says so.
- **Terms:** lustat.statec.lu's robots address asked again in its own request (read 1586): no robots file. STATEC's verdict (read 1564) covers it; the license record shows the table as agreed, public.
- **The write's patch conflicted** in three files beside session 2784's rows, which main does not yet hold; each block was the two new rows, resolved as unions. No marker is left, and both tables appear once in each file (610 tables, 700 sources). `finish_table.sh`: the release and license checks pass.

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | statbel.fgov.be's and beSTAT's robots files (each its own request) | 200; 404 |
| 3 | Statbel's energy statistics page | 200, six views |
| 4 | the electricity view's CSV (the fetch) | 200, one year in ktoe |
| 5 | lustat.statec.lu's robots address (its own request) | no file |
| 6 | DF_A4209, every key, CSV (the fetch) | 200 |

Reads recorded: 1583 to 1586.

## Decisions made without you

- **Statbel's one-year ktoe view not written,** as Eurostat's consumption table holds the same year by sector in MWh.
- **The disclosed mix taken as its own measure,** named as such in the header and the note.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statec_supplier_mix.py`, `tests/test_session2785.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1583 to 1586), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c141/s2785/`, `runs/license_reads/s2785/`, `warehouse/raw/statec/s2785a4209/`, `warehouse/raw/statbel/s2785elec/`.
