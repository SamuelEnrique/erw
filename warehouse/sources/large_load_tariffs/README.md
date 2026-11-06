# Large loads' filed tariffs: the registry

Energy Research Warehouse (ERW), session 2871 (chain 147). One file a schedule, `<utility>_<schedule>.yaml`, read by
`warehouse/connectors/large_load_tariffs.py` into `utility_large_load_tariffs`. Method: `docs/methods/large_load_tariffs.md`.

A session fills a file by reading the filed tariff itself: the commission's docket copy or the utility's filed tariff
book, after the host's robots file and terms. Each figure is written as the page prints it, with the page. A figure the
schedule does not print is left out, never estimated.

```yaml
utility: Ohio Power Company (AEP Ohio)      # as the filing names it
eia_id: 14006                               # EIA-861 utility number
state: OH
grid: PJM                                   # the ISO or balancing authority the load is in
sector: Industrial
schedule: Data Center Tariff (Schedule DCT) # the schedule's own name
tariff_sheet: P.U.C.O. No. 21, Original Sheet No. 3xx-1
effective: 2025-07-09                       # YYYY-MM-DD, the day the schedule took effect
voltage: {text: "subtransmission or transmission voltage", page: 1}
commission: Public Utilities Commission of Ohio
docket: 24-0508-EL-ATA
document: the Commission's Opinion and Order of 9 July 2025, Attachment A
document_url: https://...                   # the filed copy read
retrieved_at: 2026-11-06T01:00:00Z          # when it was read
license: public
terms:                                      # the schedule's own words, each with its page; any may be left out
  min_bill: {text: "...", page: 3}
  collateral: {text: "...", page: 4}
  exit_fee: {text: "...", page: 4}
  ramp: {text: "...", page: 3}
  term: {text: "...", page: 2}
figures:                                    # one a variable, each with the words printed and the page
  - {variable: min_demand_mw, value: 25, printed: "25 MW", page: 1}
  - {variable: demand_charge_transmission, value: 9.01, printed: "$9.01 per kW", page: 2}
  - {variable: energy_charge, value: 4.12, printed: "0.412 cents per kWh", page: 2}   # value in USD/MWh
```

The variables and their units: `min_demand_mw` (MW), `demand_charge` or its parts `demand_charge_transmission`,
`demand_charge_distribution`, `demand_charge_generation` (USD/kW-month), `energy_charge` (USD/MWh), `fixed_charge` (USD a
month), `min_contract_years` (year), `min_bill_pct` (pct), `collateral_months` and `exit_fee_months` (month). A value is
the printed figure in the unit, converted only between units: cents per kWh times 10 is USD per MWh, kW divided by
1,000 is MW. The connector refuses a file without a page or the printed words for every figure.
