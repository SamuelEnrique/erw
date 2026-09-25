#!/usr/bin/env python3
"""ERCOT trading hub settlement point prices, last 30 operating days.

Energy Research Warehouse (ERW) connector. Pulls day-ahead (DAM) and real-time
(RTM) settlement point prices for five ERCOT trading hubs with the gridstatus
Ercot class, reshapes them into the ERW `series` shape (docs/datastandard.md),
and writes:

    warehouse/output/ercot_dam_hub_prices.csv
    warehouse/output/ercot_rtm_hub_prices.csv
    warehouse/output/logs/ercot_prices_<run>.log

Sources (all public ERCOT MIS reports, www.ercot.com):
  DAM  NP4-190-CD  DAM Settlement Point Prices (one file per operating day)
  RTM  NP6-785-ER  Historical RTM Load Zone and Hub Prices (one file per year,
                   updated by ERCOT periodically)
  RTM  NP6-905-CD  Settlement Point Prices at Resource Nodes, Hubs and Load
                   Zones (one file per 15-minute interval, kept about 8 days)

The live NP6-905-CD files only reach back about a week, so RTM rows come from
the yearly NP6-785-ER archive wherever it covers the window, and from
NP6-905-CD for the intervals after the archive ends. Every row records the
exact ERCOT document it was read from (source, source_url, vintage).

Window: the 30 complete ERCOT operating days (America/Chicago) before the day
the script runs. Interval timestamps are converted to UTC interval start.

Fails loudly: if any document cannot be read, or any hub is missing any
interval in the window, no output file is written for that market and the
script exits non-zero. Nothing is filled, interpolated or invented.

Run:  python warehouse/connectors/ercot_prices.py

Session 2: the logic moved to warehouse/connectors/iso_prices.py (pull_ercot),
shared with the other ISOs. This file is kept as the session 1 entry point and
is equivalent to `python warehouse/connectors/iso_prices.py ercot --days 30`.
Since session 2 the DAM file also includes any already-published forward
operating day, and every raw ERCOT file is saved under warehouse/raw/ercot/.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iso_prices  # noqa: E402

if __name__ == "__main__":
    sys.exit(iso_prices.main(["ercot", "--days", "30"]))
