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

Session 118: one rule for every impossible value, in three parts. Every derived table that reads such a value calls
this module (docs/methods/impossible_hours.md lists them, with what each changed).

  A. An hour of demand or of net generation is used when it is held, above zero, within JUMP of the median of the four
     hours around it (the rule above, word for word), and within the grid's own range: between RANGE[0] and RANGE[1]
     times the median of the grid's hours that pass the first three tests, over the history read. The range catches what
     the hours around cannot: a run of faulty hours in a row (California's net generation sliding to 727 MW on
     2023-11-10, twelve hours in a row).
  B. A zero is a missing value. A grid's demand or net generation is never zero, so an hour at or below zero is a
     blank, not a quantity (New York's twelve hours of zero). This is test 2 of A, stated on its own because a zero
     passes every test that only asks whether a value is held.
  C. A day of interchange between two balancing authorities is used when it is within MADS times the pair's median
     absolute deviation of the pair's own median over the history read, a deviation under FLOOR MWh counting as FLOOR
     (so a day is never left out for less than 5,000 MWh). SPP to MISO at 2,159,056 MWh on 2026-07-21, more than
     SPP's whole daily demand, is the case. The rule ba_supply.py has had since session 62, moved here.

Tables behind a live page (HELD): the rule is written into their builders and not applied until a person approves the
numbers it moves. applies(table) is False for them, so their builders write what they wrote before. A trial build with
ERW_SCREEN_TRIAL=1 and a trial output folder applies it, and that is how the before and after of each held table is
measured. To approve a table, remove its line from HELD.

Usage: screened = impossible_hours.screen(series)        # a pandas Series of MW indexed by the hour's start, sorted
       table = impossible_hours.left_out(series)          # the hours not used, each with its reason
       x = impossible_hours.screen_extract(x, "table")    # an EIA-930 extract's demand_mwh and net_generation_mwh
       bad = impossible_hours.pair_days_far(frame)        # rule C: True for a pair-day not used
"""
import os

import numpy as np
import pandas as pd

JUMP = 0.25  # an hour further than this share from the median of the four hours around it is not used
RANGE = (1 / 3, 3.0)  # session 118: an hour outside this band of the grid's own median hour is not used
MADS, FLOOR = 10, 500.0  # rule C: how many median absolute deviations, and the least a deviation counts as, MWh
REASONS = ("blank", "not above zero", "apart from the hours around it", "outside the grid's range")

# Session 118: tables a live page reads. The rule is in their builders and waits for a person's approval, because
# applying it moves a number a visitor sees (the report of session 118 lists each number before and after).
HELD = {
    "carbon_intensity_hourly": "the live /network page shows each grid's newest hour of it, and the home page counts its rows",
    "carbon_intensity_daily": "built with carbon_intensity_hourly in one run; the home page counts its rows",
    "carbon_intensity_monthly": "built with carbon_intensity_hourly in one run; the home page counts its rows",
    "cost_of_power_monthly": "the home page reads it and counts its rows",
    "cost_of_power_carbon": "built with cost_of_power_monthly in one run; the home page counts its rows",
    "ba_supply_monthly": "the live /network page's supply table",
    "ai_power_regions": "its shares rest on the same demand and the same pair-days as ba_supply_monthly; the home page counts its rows",
    "caiso_reliability_daily": "the home page counts its rows",
    "event_window_daily": "the live seller page's stress days come from it, and the home page reads it",
}


# Session 118, measured on the workbook retrieved 2026-10-04: EIA's file holds no hydro for California (CISO) in every
# one of the 7,869 hours from the hour starting 2019-10-01T21:00Z to the hour starting 2020-08-24T17:00Z (both
# included), and EIA's total leaves it out too. The hours before and after hold it (1,278 MW and 1,898 MW).
CISO_NO_HYDRO = ("2019-10-01T21:00:00Z", "2020-08-24T17:00:00Z")


def in_hydro_gap(ts_utc):
    """True for the hours of California's hydro gap. ts_utc: hour starts as ISO strings (a Series) or UTC timestamps."""
    s = pd.Series(ts_utc)
    if s.dtype == object:
        return ((s >= CISO_NO_HYDRO[0]) & (s <= CISO_NO_HYDRO[1])).to_numpy()
    t = pd.to_datetime(s, utc=True)
    return ((t >= pd.Timestamp(CISO_NO_HYDRO[0])) & (t <= pd.Timestamp(CISO_NO_HYDRO[1]))).to_numpy()


def without_hydro_gap(x, ba, table=None, col="net_generation_mwh"):
    """An extract with California's net generation blank in the hours of the hydro gap: EIA's total leaves hydro out
    there, so the hour's generation, and any CO2 divided by it, is short. Another balancing authority's extract comes
    back as it came, and so does a held table's outside a trial build. Demand is not touched: it does not rest on
    generation by source."""
    if str(ba).lower() != "ciso" or (table is not None and not applies(table)):
        return x
    out = x.copy()
    out.loc[in_hydro_gap(out["ts_utc"]), col] = np.nan
    return out


def applies(table):
    """Whether the rule is applied when this table is built: always, except for a table in HELD, where it is applied
    only in a trial build (ERW_SCREEN_TRIAL=1)."""
    return table not in HELD or os.environ.get("ERW_SCREEN_TRIAL") == "1"


def _local(d, jump):
    v = d.where(d > 0)
    around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
    ok = v.notna() & ~((v - around).abs() > jump * around)
    return around, v.where(ok)


def screen(d, jump=JUMP, rng=RANGE):
    """The hours used: held, above zero, within `jump` of the median of the four hours around them, and within `rng` of
    the median of the hours that pass those three tests. The others come back blank (NaN). d: a Series by hour, in time
    order, one row an hour. rng=None leaves the range test out (the rule as it stood before session 118)."""
    _, kept = _local(d, jump)
    if rng is None or not kept.notna().any():
        return kept
    med = kept.median()
    return kept.where((kept >= rng[0] * med) & (kept <= rng[1] * med))


def left_out(d, jump=JUMP, rng=RANGE):
    """The hours the rule does not use: a frame indexed as d with columns value (as the source gave it), around (the
    median of the four hours around it, of those held and above zero) and reason."""
    around, local = _local(d, jump)
    kept = screen(d, jump, rng)
    out = pd.DataFrame({"value": d, "around": around, "local": local})[kept.isna()]
    out["reason"] = [REASONS[0] if pd.isna(x) else REASONS[1] if x <= 0 else REASONS[2] if pd.isna(loc) else REASONS[3]
                     for x, loc in zip(out["value"], out["local"])]
    return out.drop(columns="local")


def screen_extract(x, table=None, cols=("demand_mwh", "net_generation_mwh"), log=None):
    """An EIA-930 extract (eia930_emissions.read_extract: one row an hour, ts_utc the hour's start) with rule A applied to
    its demand and net generation: an hour that fails becomes a blank in that column and stays a row. With `table`, the
    rule is applied only when applies(table). The extract may skip hours, so the hours around an hour are taken by the
    clock, not by the row. `x` is indexed by a UTC DatetimeIndex or carries ts_utc; it comes back in the shape it came."""
    if table is not None and not applies(table):
        return x
    out = x.copy()
    idx = out.index if isinstance(out.index, pd.DatetimeIndex) else pd.DatetimeIndex(pd.to_datetime(out["ts_utc"], utc=True))
    if idx.has_duplicates:
        raise ValueError("screen_extract: two rows for one hour")
    full = pd.date_range(idx.min(), idx.max(), freq="h")
    for c in cols:
        if c not in out:
            continue
        raw = pd.Series(pd.to_numeric(out[c], errors="coerce").to_numpy(), index=idx)
        kept = screen(raw.reindex(full)).reindex(idx)
        out[c] = kept.to_numpy()
        if log:
            log(f"  impossible hours: {int((raw.notna() & kept.isna()).sum())} held hours of {c} not used "
                "(docs/methods/impossible_hours.md)")
    return out


def pair_days_far(it, entity="entity", value="v"):
    """Rule C. True for a pair-day further from its pair's own median than MADS times the pair's median absolute
    deviation, a deviation under FLOOR MWh counting as FLOOR. it: a frame of pair-days with the pair's name in
    `entity` and the day's MWh in `value`."""
    g = it.groupby(entity)[value]
    med = g.transform("median")
    mad = (it[value] - med).abs().groupby(it[entity]).transform("median")
    return (it[value] - med).abs() > MADS * np.maximum(mad, FLOOR)
