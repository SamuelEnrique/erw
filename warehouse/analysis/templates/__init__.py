"""The Automated Analysis template library (platform tool 26, session 23). See common.py for the interface."""
import importlib
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ORDER = ["peak_premium_block", "da_rt_spread_by_hour", "forecast_error", "curtailment_midday", "implied_heat_rate",
         "storage_evening_peak", "negative_price_hours", "deals_by_month", "datacenters_by_state", "chokepoint_transits"]


HERE = os.path.dirname(os.path.abspath(__file__))


def _template(n):
    """A template module from this folder. Session 8013: warehouse/derived/forecast_error.py (chain 505, part D1) shares
    a name with the template forecast_error; where that one is already imported, or found first on the path, the
    template is loaded from its own file under its own name, and the other is left as it is."""
    m = sys.modules.get(n)
    if m is None:
        m = importlib.import_module(n)
    if os.path.dirname(os.path.abspath(getattr(m, "__file__", "") or "")) == HERE:
        return m
    key = f"erw_template_{n}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, n + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def load_all():
    """The ten template modules, then the lines of the watch list (session 119: warehouse/analysis/watch.py). ORDER
    gains the lines' names, so that a tie between two measures still goes to the earlier one."""
    mods = [_template(n) for n in ORDER if not n.startswith("watch_")]
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import watch
    lines = watch.load()
    for t in lines:
        if t.NAME not in ORDER:
            ORDER.append(t.NAME)
    return mods + lines
