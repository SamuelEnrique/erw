# Sessions 570 to 573 report: meters, power plants' CO2, coal prices by rank and in trade

21 October 2026, from 23:35 UTC (the probes and trials ran while chain 031's landing waited for its checks), on lab-desktop (the data machine), the first four sessions of `queue/done/033-night-22-october-sources.md`, reported together. Model spend USD 0.

## Read these first

- **Four new tables**, each from EIA's API v2, each written under the data lock (23:48 UTC) with `--offline` (0 requests), validated, covered, archived, and held from `/data` and Redivis v1. Not in the live set.

  | Session | Table | Rows | Route | Cross-check |
  |---|---|---|---|---|
  | 570 | `eia_meters_state_annual`, 2013 to 2024 | 8,578 | `electricity/state-electricity-profiles/meters` | AMI, AMR and standard meters sum to all meters every time; residential meters are a median 1.015 of EIA-861's residential customers (510 state-years) |
  | 571 | `eia_power_co2_state_annual`, 1990 to 2024 | 10,640 | `.../emissions-by-state-by-fuel` | a median 5% above session 530's electric power sector (1,590 state-years), which fits the profiles' inclusion of commercial and industrial CHP plants |
  | 572 | `eia_coal_price_rank_annual`, 2001 to 2024 | 2,843 | `coal/price-by-rank` | all ranks equal all markets (session 519) within a cent in 93.7% of 1,005 area-years |
  | 573 | `eia_coal_trade_price_annual`, 2000 to 2025 | 24,623 | `coal/exports-imports-quantity-price` | exports' median price about 4 times the U.S. mine price (2.4 to 8.4 by year), an order of magnitude only: metallurgical coal at the port |

- **Units**:
  - meters as `count`;
  - CO2 as `tCO2` (EIA's thousand metric tons times 1,000) and its rate as `kgCO2/MWh` (EIA's pounds per MWh times 0.453592);
  - coal prices as `USD/short_ton`.
- **Not taken, for want of a unit**: SO2 and NOx (short tons, pounds per MWh; 571) and coal trade quantities (short tons; 573). The tonnage ruling is already asked; SO2 and NOx are a new unit question, listed below.
- A price EIA withholds ("w") has no row. Each table is unique on its key.
- Tests: `tests/test_session570.py`, 7, covering all four.

## Pulls against their ceilings

| Session | Host | Requests | Ceiling |
|---|---|---|---|
| 570 | api.eia.gov | 4 | 10 |
| 571 | api.eia.gov | 4 | 10 |
| 572 | api.eia.gov | 2 | 10 |
| 573 | api.eia.gov | 8 | 20 |

## For Samuel's ruling

- Units for SO2 and NOx: short tons, and pounds per MWh, or metric tons converted (571).

## Files

- New: `warehouse/connectors/eia_meters.py`, `eia_power_co2_state.py`, `eia_coal_price_rank.py`, `eia_coal_trade_price.py`, `tests/test_session570.py`, this report. Changed: the shared metadata, holds and package.
