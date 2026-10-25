# French Polynesia's electricity a year, 2010 to 2024 (the Observatoire Polynesien de l'Energie's energy balance, edition 2024)

Energy Research Warehouse (ERW), method note written in session 2611 (chain 129) for a table first written on 25 October 2026 (session 2609).

Tables: `ope_pf_electricity_annual`

## Publisher and address

The Observatoire Polynesien de l'Energie of the Direction Polynesienne de l'Energie (Government of French Polynesia), Bilan energetique de la Polynesie francaise, edition 2024, from EDT Engie's, the SPL's, the EPIC's and the municipal utilities' figures: `https://www.service-public.pf/sde/wp-content/uploads/sites/15/2025/11/Bilan_energetique_de_la_Polynesie_francaise_-_edition_2024.pdf`, found through the SDE site's WordPress media list (`/sde/wp-json/wp/v2/media?search=bilan`, read 1213). One GET, no key. Source id `sde_pf:bilan_energetique_2024`. Connector: `warehouse/connectors/ope_pf_electricity.py` (session 2609), whose raw store is `warehouse/raw/sde_pf/`. www.service-public.pf's robots file closes only `/wp-admin/` (read 1212).

## Vintage and revision

Written by run `20261025T052458Z` (the write under the lock, offline), which read the balance saved at 2026-10-25T05:21:43Z. `vintage` is its last-modified time, 2025-11-21T20:12:34Z. Each year's edition has its own address and gives the series again.

## Shape and variables

Series, 52 rows, 4 entities. `entity` `ope:pf:<item>`:
- `total` (`variable` `generation`): total production, 2010 to 2024;
- `final_consumption` (`consumption`): final electricity consumption, 2010 to 2024;
- `renewable` (`generation`): renewable production, 2014 to 2024;
- `losses` (`losses`): transmission and distribution losses, 2014 to 2024.

`unit` MWh (the balance's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` PF; `node` the balance's label.

In 2024: production 721.8 GWh, 259.9 GWh of it renewable (36.0%; hydro 189.5 and solar 70.4 in the balance's island table), consumption 683.8 GWh, losses 38.0 GWh.

## Reading the source

- The run stops at once, asking nothing, while `sde_pf` or www.service-public.pf is paused.
- One request a run; `--offline` reads the saved balance.
- The PDF's "ti" ligature is extracted as `(cid:31)` and restored before reading.
- **The "Principaux chiffres" table:** its row of years (from 2010, consecutive), then the lines "Production totale d'electricite GWh" and "Consommation finale d'electricite GWh", each with fifteen figures. Each line is found once.
- **Figure 17's table:** the row of years before "Production d'EnR electrique (GWh)", then "Production totale d'electricite (GWh)", then the EnR rate.
- **The losses table:** "Pertes" and its years, then the line beginning "en GWh".
- **Checks:**
  - Figure 17's total equals the main table's in each of its years;
  - the printed EnR rate is renewable over total within 0.1 point;
  - Figure 23's consumption ("d'electricite" then "GWh ...") equals the main table's.
- The run stops, and no file is written, for: a line found other than once, a row of years out of order, a line of the wrong count, a check missed.

Nothing is filled. Not taken: the 2024 table by archipelago (its labels split over lines), the balance in ktep, prices and emissions.

## License

Internal. www.service-public.pf's Mentions legales (read 1215): "Toute reproduction ou representation et extraction, partielle ou totale, des elements du site ne peut etre faite sans autorisation prealable" (with its accents in the record). The balance states no terms of its own. Verdict: needs written permission. Held from the live set and from Redivis.

## Cross-check

EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives 712.2 GWh of generation in 2022 and in 2023, and 719.2 GWh in 2024, against the balance's 680.3, 697.9 and 721.8. EIA's consumption in 2024, 676.1 GWh, is close to the balance's 683.8.
