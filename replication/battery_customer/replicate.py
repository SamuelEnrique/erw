#!/usr/bin/env python3
"""ERW, What a battery saves a customer (/battery/customer): the replication a reader can run (session 7504, chain 304).

The page reads no ERW table: every figure on it is arithmetic on nine numbers a reader types. So this script reads no
table either. It reads the cases of this folder (cases.json: the page as it opens, the numbers the page's browser proof
types, and nine cases typed from published commercial tariffs with a demand charge, each cited to its document),
recomputes every figure the page prints for each case from the rules of the method note
(docs/methods/battery_customer.md, sections 2 to 4), and sets each beside the figure the page shows for the same case
(page_figures.json, read off the page's own calculator by site/scripts/battery-customer-figures.mjs), with the
difference and whether it is inside the tolerance: half of the page's last shown digit.

It was written from the note, not from the page's code, and shares nothing with it.

    python replication/battery_customer/replicate.py              every figure, N of N
    python replication/battery_customer/replicate.py --headline   the five headline figures of the do-file
    python replication/battery_customer/replicate.py --seasons    the year by a tariff's own seasons (the note, section 6)
    python replication/battery_customer/replicate.py --crosscheck the figures set beside the published ones (section 7)

Exit 0 when every figure is inside its tolerance, 1 when one is not, 2 when the inputs cannot be read. Standard
library only. No request is made and nothing is written.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The note, section 2: the nine fields in the page's order, the least and the most each takes, whether it takes zero,
# and its starting value (None: the field opens empty).
FIELDS = [
    ("peakKw", 0, 1e6, False, None),
    ("demandCharge", 0, 500, True, None),
    ("peakRate", 0, 5, True, None),
    ("offPeakRate", 0, 5, True, None),
    ("batteryKw", 0, 1e6, False, None),
    ("batteryKwh", 0, 1e7, False, None),
    ("peakHours", 0, 24, False, "2"),
    ("days", 0, 31, True, "21"),
    ("roundTrip", 1, 100, False, "86"),
]


def read_field(text, low, high, zero):
    """The note, section 2: a typed value is a number or it is nothing. Digits with at most one decimal point, commas
    taken out, inside the field's limits, zero only where the field takes it."""
    s = text.strip().replace(",", "")
    if not s or s.count(".") > 1 or not s.replace(".", "").isdigit() or not s.isascii():
        return None
    v = float(s)
    if v < low or v > high or (v == 0 and not zero):
        return None
    return v


def read_all(typed):
    values, missing = {}, []
    for key, low, high, zero, _start in FIELDS:
        v = read_field(typed.get(key, ""), low, high, zero)
        if v is None:
            missing.append(key)
        else:
            values[key] = v
    return values, missing


def saving(x):
    """The note, section 3: the nine numbers to every figure of the page."""
    eta = x["roundTrip"] / 100.0
    by_power, by_energy, by_peak = x["batteryKw"], x["batteryKwh"] / x["peakHours"], x["peakKw"]
    shaved = min(by_power, by_energy, by_peak)
    # a tie is named in this order: the peak itself, then the power, then the energy
    limit = "your peak itself" if shaved == by_peak else "the battery's power" if shaved == by_power else "the battery's energy"
    demand = shaved * x["demandCharge"]
    out_full = min(x["batteryKwh"], x["peakKw"] * x["peakHours"])   # ruling alternative 4 (wip/alt-battery-customer-4): capped by the peak; main: the whole battery
    in_full = out_full / eta
    per_day = out_full * x["peakRate"] - in_full * x["offPeakRate"]
    shifts = per_day > 0
    for_peak = shaved * x["peakHours"]
    if shifts:
        out_kwh, in_kwh, energy = out_full, in_full, per_day * x["days"]
    else:
        out_kwh, in_kwh = for_peak, for_peak / eta
        energy = (out_kwh * x["peakRate"] - in_kwh * x["offPeakRate"]) * x["days"]
    month = demand + energy
    return {
        "shaved": shaved, "limit": limit, "by_energy": by_energy, "demand": demand, "demand_before": x["peakKw"] * x["demandCharge"],
        "hours": x["batteryKwh"] / x["batteryKw"], "shifts": shifts, "per_day": per_day, "out_kwh": out_kwh, "in_kwh": in_kwh,
        "energy": energy, "month": month, "year": 12 * month, "break_even": x["offPeakRate"] / eta, "for_peak": for_peak,
    }


def figures(typed):
    """Every figure the page prints for a case, by the key page_figures.json gives it (the note, section 4)."""
    x, missing = read_all(typed)
    if missing:
        f = {"waiting_needed": len(missing), "waiting_fields": len(FIELDS)}
        for key, _low, _high, _zero, start in FIELDS:
            if start is not None:
                f["start_" + key] = float(start)
        return f
    s = saving(x)
    f = {
        "sum_battery_kw": x["batteryKw"], "sum_battery_kwh": x["batteryKwh"], "sum_hours": s["hours"], "sum_month": s["month"],
        "sum_year": s["year"], "sum_demand": s["demand"], "sum_energy": s["energy"],
        "tile_year": s["year"], "tile_month": s["month"],
        "tile_demand": s["demand"], "tile_shaved_kw": s["shaved"], "tile_peak_kw": x["peakKw"], "tile_demand_before": s["demand_before"],
        "tile_energy": s["energy"], "tile_out_kwh": s["out_kwh"], "tile_in_kwh": s["in_kwh"], "tile_days": x["days"],
        "how_peak_hours": x["peakHours"], "how_power_kw": x["batteryKw"], "how_energy_kw": s["by_energy"], "how_peak_kw": x["peakKw"],
        "how_shaved_kw": s["shaved"], "how_limit": s["limit"], "how_demand_charge": x["demandCharge"], "how_demand": s["demand"],
    }
    if s["shifts"]:
        f.update({"shift_out_kwh": s["out_kwh"], "shift_in_kwh": s["in_kwh"], "shift_per_day": s["per_day"], "shift_month": s["energy"], "shift_days": x["days"]})
    else:
        f.update({"noshift_break_even": s["break_even"], "noshift_kwh": s["for_peak"], "noshift_month": s["energy"]})
    return f


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def compare(cases, page):
    """[(case, key, replicated, shown, difference, ok)] for every figure the page shows, and the keys the replication
    computed that the page does not show."""
    rows, extra = [], []
    typed = {c["id"]: c["typed"] for c in cases["cases"]}
    for c in page["cases"]:
        mine = figures(typed[c["id"]])
        seen = set()
        for fig in c["figures"]:
            seen.add(fig["key"])
            got = mine.get(fig["key"])
            if got is None:
                rows.append((c["id"], fig["key"], None, fig["shown"], None, False))
            elif fig["tolerance"] is None:
                rows.append((c["id"], fig["key"], got, fig["shown"], None, got == fig["value"]))
            else:
                diff = float(got) - float(fig["value"])
                rows.append((c["id"], fig["key"], got, fig["shown"], diff, abs(diff) <= fig["tolerance"] + 1e-9))
        extra += [(c["id"], k) for k in mine if k not in seen]
    return rows, extra


def case(cases, cid):
    c = next(c for c in cases["cases"] if c["id"] == cid)
    x, missing = read_all(c["typed"])
    if missing:
        raise ValueError(f"{cid}: {missing} cannot be read")
    return c, x, saving(x)


HEADLINE = [
    ("seattle-md-city-tou", "year", "Seattle City Light, medium, City of Seattle, time of use: saved a year (USD)"),
    ("seattle-md-downtown-tou", "year", "Seattle City Light, medium, Downtown Network, time of use: saved a year (USD)"),
    ("srp-e32-summer-peak", "month", "Salt River Project E-32, summer peak: saved a month (USD)"),
    ("austin-sv2", "year", "Austin Energy, secondary voltage 10 to under 300 kW: saved a year (USD)"),
    ("sce-tou-gs-2-b-2013-summer", "month", "Southern California Edison TOU-GS-2 B, summer 2013, as NREL prints it: saved a month (USD)"),
]


def headline(cases):
    for cid, key, words in HEADLINE:
        _c, _x, s = case(cases, cid)
        print(f"{words}: {s[key]:.2f}")
    return 0


def seasons(cases):
    """The note, section 6: the page's year is twelve of the month typed. Salt River Project's E-32 prices three
    seasons (two summer peak months, four summer, six winter), so the same battery's year by the plan's own seasons
    is set beside twelve of each month."""
    months = [("srp-e32-summer-peak", 2), ("srp-e32-summer", 4), ("srp-e32-winter", 6)]
    by_season = 0.0
    for cid, n in months:
        _c, _x, s = case(cases, cid)
        by_season += n * s["month"]
        print(f"{cid}: a month {s['month']:.2f}, twelve of it {s['year']:.2f}, months of the season {n}")
    print(f"the year by the plan's seasons: {by_season:.2f}")
    for cid, _n in months:
        _c, _x, s = case(cases, cid)
        print(f"twelve of {cid} against the year by seasons: {100 * (s['year'] / by_season - 1):+.1f} percent")
    return 0


def crosscheck(cases):
    """The note, section 7: what the tool gives, in the units the published figures are in. Nothing is adjusted."""
    print("shaved kW over the battery's kW, and the saving from the peak over the saving from energy, by case")
    for c in cases["cases"]:
        if not str(c.get("kind", "")).startswith("tariff"):
            continue
        _c, x, s = case(cases, c["id"])
        ratio = s["shaved"] / x["batteryKw"]
        over = "energy is a cost" if s["energy"] <= 0 else f"{s['demand'] / s['energy']:.2f}"
        print(f"{c['id']}: demand charge {x['demandCharge']:.2f} USD per kW; shaved over battery power {ratio:.2f}; "
              f"demand saving {s['demand']:.2f}, energy saving {s['energy']:.2f}, demand over energy {over}; "
              f"demand charge {'at or above' if x['demandCharge'] >= 15 else 'below'} USD 15 per kW")
    _c, x, s = case(cases, "sce-tou-gs-2-b-2013-summer")
    print(f"sce-tou-gs-2-b-2013-summer at 85 percent of the battery's power (NREL's expectation for four hours): "
          f"demand saving {0.85 * x['batteryKw'] * x['demandCharge']:.2f} against the tool's {s['demand']:.2f}")
    return 0


def main(argv):
    try:
        cases, page = load("cases.json"), load("page_figures.json")
        if "--headline" in argv:
            return headline(cases)
        if "--seasons" in argv:
            return seasons(cases)
        if "--crosscheck" in argv:
            return crosscheck(cases)
        rows, extra = compare(cases, page)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    print("What a battery saves a customer: every figure the page prints, for each case of cases.json")
    print("case | figure | replication | the page | difference | inside the tolerance")
    for cid, key, got, shown, diff, ok in rows:
        g = "not computed" if got is None else (got if isinstance(got, str) else f"{got:,.4f}")
        d = "" if diff is None else f"{diff:+.4f}"
        print(f"{cid} | {key} | {g} | {shown} | {d} | {'yes' if ok else 'NO'}")
    for cid, key in extra:
        print(f"{cid} | {key} | computed here, not shown by the page")
    bad = [r for r in rows if not r[5]]
    print(f"{len(rows) - len(bad)} of {len(rows)} inside the tolerance, {len(page['cases'])} cases; "
          f"computed here and not shown by the page: {len(extra)}; not replicated here: nothing")
    return 0 if not bad and not extra and len(rows) == page["figures"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
