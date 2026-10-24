# EIA-930's balance for the seven ISO grids, reported against adjusted

Session 360 (the chain of 20 October 2026). The Grid pack's item 3 (`docs/reviews/packs/grid.md`, section 6): for
CAISO, PJM, MISO and SPP the sum of a grid's ties does not equal its net generation minus its demand. This note reruns
that test on EIA's adjusted series, as the owner asked, and splits the gap into its two parts. The script is
`warehouse/analysis/eia930_balance.py`; its figures are in `docs/methods/eia930_balance.json`.

## The answer

**EIA's adjusted series do not close the balance, and cannot.** EIA's own notes, in the workbook it publishes for each
balancing authority: an adjusted value "displays the [value] reported by the balancing authority unless imputation was
required", and EIA imputes only an anomaly (a value missing, negative or zero, or 1.5 times past the authority's own
extremes). In the window below EIA imputed nothing for six of the seven grids and two hours of ISO-NE's demand and
generation; every mean gap is the same reported and adjusted. Nothing is switched, and no ruling on which series the
Grid tool draws is needed for the balance: the adjusted series would draw the same figures.

**What remains** is in the grids' own reports, and it is of two kinds:

| Grid | The pack's test (sum of ties less NG minus D), 13 to 28 September | The tie gap (sum of ties less TI) | The total gap (TI less NG minus D) | Where the gap is |
|---|---|---|---|---|
| CAISO | 3,199.1 MW (reproduced) | 0.7 MW | 3,002.8 MW (9.6 percent of demand) | its own total interchange does not equal its net generation minus demand |
| MISO | 1,397.9 (reproduced) | 0.0 | 1,430.1 (1.9 percent) | the same |
| PJM | 2,042.1 (reproduced) | 1,646.6, in the 615 hours all seven ties are held | 2,021.0 (2.2 percent) | both: its ties do not sum to its total, and its total does not equal NG minus D (the two partly offset) |
| SPP | 978.1 (reproduced) | 6,132.6; 1,023.2 (2.9 percent) without two hours | 26.0 | its ties do not sum to its total. Two hours carry an impossible SPP to MISO tie, minus 2,148,411 MW (4 October 12:00 and 6 October 19:00 UTC); the rule for impossible values is not applied to an hour of interchange (the pack's item 10) |
| ERCOT | 1.6 (reproduced) | 0.3 | 1.7 | closes |
| NYISO | 0.4 (reproduced) | 0.4 | 0.0 | closes |
| ISO-NE | 0.0 (0.7 in the pack, before EIA's revisions) | 0.0 | 0.0 | closes |

The gaps are mean absolute values over 840 hours, 13 September to 17 October 2026 (the span the live interchange table
holds), from EIA's workbooks as published on 19 October 2026; the pack's test is reproduced over its own 360 hours from
the live tables, as session 49 computed it.

**EIA's own tolerance.** EIA's workbooks carry a sheet "Imbalance Thresholds": an acceptable imbalance of net
generation, demand and total interchange, and of total interchange against the sum of the ties, for each grid (10 for
every grid's first; 10 for the second except ISO-NE's 13 and SPP's 200). The sheet states no unit. Read as a percent
of demand: CAISO's total gap passes it in 277 of 840 hours, SPP's tie gap in 2 (the two impossible hours) and its total
gap in 4; every other grid stays within it. Read as MW: CAISO's and MISO's total gaps pass it in nearly every hour (837 and 840), PJM's
in 836 and its tie gap in 542 of 615, SPP's tie gap in 723. Which reading EIA means is EIA's to say; the percent
reading is the one under which most grids would be published as they are.

## What it means for the Grid tool

- Its ties are as reported, and for CAISO and MISO they agree with the grid's own total interchange to the MW. The gap
  a reader sees there is EIA-930's net generation and demand against that total, not the ties.
- SPP's two impossible hours enter any sum of its interchange taken over them. A screen of impossible values for an
  hour of interchange (the pack's item 10) would remove them; nothing was changed tonight.

## On the Grid tool (session 1165, chain 078)

Chain 078 in this note (sessions 1164 to 1177): 1165 (this section).

The Network tab of `/grid` states the gap for the grid in view, each of the seven: in the hour the panel shows, net
generation, demand, the net export over the ties and the gap (net generation less demand less net export, the sign
the other way from the pack's test), and over the snapshot's week the mean of the gap's absolute value and the count
of hours that hold every tie and both series. It reads the live tables the tab already reads, not EIA's workbooks, so
the gap there is the total of the two parts above; its note says where this note found each grid's gap, and its hover
tip the split in one line. The keys and their rule: `grid_network.md`, "The balance, said where the figures are".

Decisions (session 1165): in `grid_network.md`, that section's Decisions. This note's answer is used as it stands
(the split, the mean of the absolute gap); nothing in it changed.

## The pull

EIA's API (`/v2/electricity/rto/region-data`) offers the region data as four types only (its facet "type", read on 20
October 2026: D, DF, NG, TI), and its routes hold no adjusted or imputed series. The adjusted and imputed columns are
in the workbooks EIA publishes for each grid (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx),
which the emissions connector had saved on 19 October 2026 at 17:24 UTC (`warehouse/raw/eia930_emissions/20261019T172418Z/`):
no new request was needed for them. Requests to EIA's API: 2 of the ceiling of 200 (the facet and the route list).

    python warehouse/analysis/eia930_balance.py     # reads the live tables and the newest saved workbooks; no request
