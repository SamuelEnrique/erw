# Session 2894 report: CenterPoint's own revenue

6 November 2026, about 03:31 UTC, on lab-desktop (the data machine), chain 148, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Held:** `eia861_delivery_only` (EIA-861's delivery-only sheet) holds the Texas wires companies' revenue and sales: CenterPoint, Oncor, AEP Texas and TNMP among the seven EIA lists in Texas. `ercot_node_wires_utilities` already reads it.
- **Not yet wired into the tab's Utility cell for Harris County.** The cell's builder (`siting_page.py`, `utility.json`) reads `eia861_utility_sales` for a county's own utilities and names the kind (bundled, delivery, energy). A delivery-only company's revenue per MWh would be drawn as "delivery only". That is a site change for chain 151's session 2909, the wiring session.

## Decisions made without you

- **Left to the wiring session** rather than a gate of its own.

## For Samuel's ruling

- None.
