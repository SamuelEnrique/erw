"""The Automated Analysis template library (platform tool 26, session 23). See common.py for the interface."""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ORDER = ["peak_premium_block", "da_rt_spread_by_hour", "forecast_error", "curtailment_midday", "implied_heat_rate",
         "storage_evening_peak", "negative_price_hours", "deals_by_month", "datacenters_by_state", "chokepoint_transits"]


def load_all():
    """The ten template modules, then the lines of the watch list (session 119: warehouse/analysis/watch.py). ORDER
    gains the lines' names, so that a tie between two measures still goes to the earlier one."""
    mods = [importlib.import_module(n) for n in ORDER if not n.startswith("watch_")]
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import watch
    lines = watch.load()
    for t in lines:
        if t.NAME not in ORDER:
            ORDER.append(t.NAME)
    return mods + lines
