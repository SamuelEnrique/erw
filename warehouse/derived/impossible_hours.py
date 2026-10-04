"""Energy Research Warehouse (ERW): the screening rule for impossible hours (session 103).

EIA-930's hourly demand holds hours that did not happen: PJM at 224,345 MW at 18:00 UTC on 13 July 2020 between hours
near 140,000; New York at zero; California at 12,000 to 14,000 MW between hours of 23,000 in the spring of 2019; SPP at
1,505 MW at 04:00 UTC on 21 June 2025. Session 97 met them building the demand growth table and screened them there.
This module is that rule, stated once, for every derived table that reads those hours (docs/methods/impossible_hours.md).

The rule. An hour of demand is used when it is

  1. held (not blank),
  2. above zero, and
  3. within JUMP (25 percent) of the median of the four hours around it: the two before and the two after, those of
     them that are held and above zero.

An hour that fails is used for nothing. Nothing is filled, smoothed or replaced: the hour becomes a blank, and each
table's own completeness rule then decides what a blank costs it (a day short of an hour is not a complete day).

Why a quarter. The steepest real ramps of these grids move demand about a tenth in an hour; no real hour stands a
quarter away from the four around it. The rule is for demand only. Solar, wind and battery output move further than
that in an hour by nature, and interchange has its own rule (ba_supply.py: 10 median absolute deviations from the
pair's own median and at least 500 MWh).

What the rule does not catch: a faulty hour inside a sum. The Lower 48's demand is EIA's sum over every balancing
authority; PJM's faulty hour is inside the Lower 48's 776,575 MW of the same hour, which stands 12 percent above its
neighbours and passes. And a run of three or more faulty hours in a row makes its own median.

Usage: screened = impossible_hours.screen(series)        # a pandas Series of MW indexed by the hour's start, sorted
       table = impossible_hours.left_out(series)          # the hours not used, each with its reason
"""
import pandas as pd

JUMP = 0.25  # an hour further than this share from the median of the four hours around it is not used
REASONS = ("blank", "not above zero", "apart from the hours around it")


def screen(d, jump=JUMP):
    """The hours used: held, above zero, and within `jump` of the median of the four hours around them. The others
    come back blank (NaN). d: a Series by hour, in time order, one row an hour."""
    v = d.where(d > 0)
    around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
    ok = v.notna() & ~((v - around).abs() > jump * around)
    return v.where(ok)


def left_out(d, jump=JUMP):
    """The hours the rule does not use: a frame indexed as d with columns value (as the source gave it), around (the
    median of the four hours around it, of those held and above zero) and reason."""
    v = d.where(d > 0)
    around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
    kept = screen(d, jump)
    out = pd.DataFrame({"value": d, "around": around})[kept.isna()]
    out["reason"] = [REASONS[0] if pd.isna(x) else REASONS[1] if x <= 0 else REASONS[2] for x in out["value"]]
    return out
