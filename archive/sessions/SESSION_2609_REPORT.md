# Session 2609 report: French Polynesia's electricity a year, 2010 to 2024 (the Observatoire Polynesien de l'Energie's energy balance, edition 2024), internal, a second source of the session's own choosing

25 October 2026, about 05:20 to 05:28 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2609.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 fetch the connector reads offline).

## Why this source

- **The ERW held French Polynesia in no table but EIA's international one,** and no chain or queue file had taken it (the record, the queue and the unlanded chains' branches searched). The territory publishes a full annual energy balance with fifteen years of electricity figures, beside New Caledonia's (session 2608).

## Read these first

- **The host:** www.service-public.pf's robots file closes only `/wp-admin/` (read 1212). The Direction Polynesienne de l'Energie's WordPress media list (read 1213, one request, chain 127's rule) gives the energy balance's editions 2023 and 2024.
- **The terms:**
  - The site's pages list (read 1214) gives the Mentions legales. They read (read 1215): "Tous les droits de reproduction ou de representation et d'extraction sont reserves. Toute reproduction ou representation et extraction, partielle ou totale, des elements du site ne peut etre faite sans autorisation prealable" (with its accents in the record).
  - The balance states no terms of its own. **Verdict: needs written permission.** The table is **internal**.
- **The source:** the Bilan energetique de la Polynesie francaise, edition 2024 (79 pages, 14.0 MB, last modified 21 November 2025), by the Observatoire Polynesien de l'Energie. Its figures come from EDT Engie, the SPL, the EPIC and the municipal utilities.
- **A new table, `ope_pf_electricity_annual`** (series, 52 rows, 4 entities, `power`):
  - total production and final electricity consumption, 2010 to 2024, from the "Principaux chiffres" table;
  - renewable production, 2014 to 2024 (Figure 17's table);
  - transmission and distribution losses, 2014 to 2024.
  - Production was 721.8 GWh in 2024, 36.0% of it renewable (259.9 GWh: hydro 189.5, solar 70.4). Consumption was 683.8 GWh and losses 38.0 GWh.
  - Checks: Figure 17's total equals the main table's in all eleven years; the printed renewable rate is renewable over total within 0.1 point; Figure 23's consumption equals the main table's. The PDF's "ti" ligature, read as `(cid:31)`, is restored.
  - Written by run `20261025T052458Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T052522Z-local`), held from the live set and from Redivis (internal).
- **One conflict, resolved:** the write's metadata patch met session 2602's source row beside its own in `sources.csv` (the two sort next to each other). It was resolved as the union of both sides (`runs/c124/resolve_union.py`), then the finish was run again (0 problems). Each metadata file holds the table once.
- **Not taken:** the 2024 table by archipelago (its labels split over lines), the balance in ktep, prices and emissions.

## Cross-checks

- EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives 712.2 GWh of generation in 2022 and 2023 (the same figure both years) and 719.2 GWh in 2024, against the balance's 680.3, 697.9 and 721.8. EIA's consumption, 676.1 GWh in 2024, is close to the balance's 683.8.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.service-public.pf's robots file | 200 |
| 2 | the SDE site's media list, search "bilan" | 200 |
| 3 | the site's pages list, search "mentions" | 200 |
| 4 | the Mentions legales | 200 |
| 5 | the energy balance, edition 2024 (the fetch) | 200, 14.0 MB |

Reads recorded: 1212 to 1215. Read 1214's address ends at `_fields=link`: the list's comma in `link,title` split the probe's own list file. The request asked for that address, and the record keeps it.

## Decisions made without you

- **French Polynesia as the second own choice.**
- **The archipelago table not taken,** as its labels cannot be read without guessing.
- **Internal** under the Government site's Mentions legales.

## For Samuel's ruling

- **Whether to ask the Direction Polynesienne de l'Energie** for permission to publish the table.

## Files

- New: `warehouse/connectors/ope_pf_electricity.py`, `tests/test_session2609.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1212 to 1215, the Government of French Polynesia's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c129/s2609/`, `runs/license_reads/s2609/`, `warehouse/raw/sde_pf/`, `warehouse/output/ope_pf_electricity_annual.csv`.
