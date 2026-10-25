# Paraguay's electricity balance, 2023 and 2024 (VMME's Balance Energetico Nacional 2024, cuadro 3)

Energy Research Warehouse (ERW), method note written in session 2572 (chain 126) for a table first written on 25 October 2026 (session 2572).

Tables: `vmme_paraguay_electricity_annual`

## Publisher and address

The Viceministerio de Minas y Energia (VMME) of Paraguay's Ministerio de Obras Publicas y Comunicaciones, its Balance Energetico Nacional 2024 (64 pages, August 2025; its 2024 figures preliminary, VMME's own word), "Cuadro 3: Comparativo balance de electricidad": `https://minasyenergia.mopc.gov.py/pdf/balance2024/BEN 2024_Paraguay.pdf` (2.8 MB). One GET, no key. Source id `vmme_py:ben_2024_cuadro_3`. Connector: `warehouse/connectors/vmme_paraguay_electricity.py` (session 2572). minasyenergia.mopc.gov.py's robots file closes Joomla's system folders only, not `/pdf/` (read 1091).

## Vintage and revision

The years 2023 and 2024, written by run `20261025T013116Z` (the write under the lock, offline), which read the balance saved at 2026-10-25T01:28:24Z. `vintage` is its last-modified time, 2025-09-26T19:27:00Z. Each year's balance has its own address.

## Shape and variables

Series, 38 rows (19 rows of the balance times two years), 13 entities. `entity` `vmme:py:<item>`; `unit` MWh (VMME's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` PY; `node` VMME's label.

| `variable` | Items | 2024, GWh |
|---|---|---|
| `gross_generation` | `total`; `power_plants` (`acaray_hydro`, `binational_hydro`: Paraguay's share of Itaipu and Yacyreta, `thermal`); `autoproducers` | 42,676.2 (binational 41,669.1, Acaray 767.7) |
| `imports` | `total` | 0.0 |
| `exports` | `total` | 15,998.6 |
| `own_use` | `total` (the plants' and ANDE's own consumption) | 293.4 |
| `losses` | `total`, `transmission`, `distribution` | 6,940.1 |
| `supply` | `total` | 19,444.2 |
| `final_consumption` | `total`, `industrial`, `residential`, `other_sectors` (`commercial_public`, `unspecified`) | 19,444.2 (residential 7,672.2) |

The balance prints exports, own use and losses with a minus sign, as they leave the supply; they are written positive here. The totals hold their parts.

## Reading the source

- The run stops at once, asking nothing, while `vmme_py` or minasyenergia.mopc.gov.py is paused.
- One request a run; `--offline` reads the saved balance.
- **The page** is found by the table's title line as printed above it (the contents page prints it with a page number after it) and read from the title to "CONSUMO FINAL"; the years' line ("2023 2024") must stand in it once.
- **Lines:** a label, the two years' figures and the change. The page's text carries the letters of the rotated unit label ("GWh") at the start of some lines; a single letter before a label is passed over. Figures print a point between thousands and a comma before the decimal. The 19 labels must come once each, in the balance's order.
- **Checks** within 0.2 GWh each year: the power plants and autoproducers to gross generation; Acaray, the binational plants and thermal to the power plants; transmission and distribution to the losses; gross generation, imports, exports, own use and losses to the supply; industrial, residential and other sectors to final consumption; commercial and public and unspecified to the other sectors; the supply to final consumption.
- The run stops, and no file is written, for: the title found other than once, a row missing or out of order, a quantity leaving the supply printed positive, a negative figure elsewhere, a check missed.

Nothing is filled. Not taken: the year-on-year changes; Cuadro 2's exports by destination, which are in thousand tonnes of oil equivalent.

## License

Internal. VMME's home page (read 1092) states no terms of reuse, no copyright line and no terms page. Verdict: needs written permission (RGGI's precedent). Held from the live set and from Redivis.

## Cross-check

EIA's Paraguay (`eia_world_electricity_annual`): 2023 exports 30.390 TWh, VMME's 30.390; 2024, EIA's 30.000 (a round estimate) against VMME's 15.999, as more of Paraguay's share of Itaipu stayed at home (final consumption up 21.6%). EIA's generation (44.244 TWh in 2023) is below VMME's gross 53.042.
