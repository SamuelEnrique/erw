"""Audit of "What a battery earns", finding 1 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the model's
reserves are never called, but ERCOT's storage telemetry shows a regulation award moving energy in its hour.

The test takes the model's own schedule for every day of the page's last twelve months (the public dispatch file's
prices, solved by battery_stack.solve_day exactly as the page is paid for them), adds the energy a regulation award
moves when it is called (F of the award each hour: Reg Down charges the battery at eta, Reg Up discharges it at 1/eta),
and asks the model's own check_day whether the schedule still holds. F = 0.17 is what ERCOT's storage resources showed
in ercot_sced_esr_hourly (February to August 2026, hours holding regulation and no other reserve: 0.168 of Reg Up and
0.181 of Reg Down, least squares, net per hour). On a machine with that table the second test measures F again.

It passes on the code as it is: it shows the fault, it does not fix it. Nothing is written."""
import csv
import math
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
F = 0.17


def last_twelve_days():
    """{local day: (energy prices, reserve prices by product key)} for the file's last twelve months."""
    out = {}
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    head = rows[0]
    ix = {c: i for i, c in enumerate(head)}
    for r in rows[1:]:
        if r[ix["in_last_twelve"]] != "1":
            continue
        d = r[ix["local_day"]]
        e, a = out.setdefault(d, ([], {k: [] for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}))
        e.append(float(r[ix["price_energy_usd_mwh"]]))
        for k in a:
            a[k].append(float(r[ix[f"price_{k}_usd_mw"]]))
    return out


class RegulationCalled(unittest.TestCase):
    def test_paid_schedule_breaks_once_regulation_is_called(self):
        eta = math.sqrt(bs.RTE)
        days = last_twelve_days()
        self.assertEqual(len(days), 365)
        broken = 0
        for d, (energy, prices) in sorted(days.items()):
            prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
            spec = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
            sol = bs.solve_day(energy, [prices[p["key"]] for p in prods], spec, 4)
            self.assertEqual(bs.check_day(sol, spec, 4), [])          # the model's schedule, as paid, holds
            keys = [p["key"] for p in prods]
            up, dn = sol["awards"][keys.index("regup")], sol["awards"][keys.index("regdn")]
            soc = np.cumsum(eta * sol["charge"] - sol["discharge"] / eta + F * dn * eta - F * up / eta)
            if bs.check_day(dict(sol, soc=soc), spec, 4):
                broken += 1
        # session 9840 measured 342 of 365: the schedule the page is paid for cannot be delivered once regulation moves
        self.assertGreaterEqual(broken, 300, f"{broken} of 365 days break a limit once regulation is called")

    def test_measured_share_of_award_called(self):
        path = os.path.join(ROOT, "warehouse", "output", "ercot_sced_esr_hourly.csv")
        if not os.path.exists(path):
            self.skipTest("ercot_sced_esr_hourly is not on this machine")
        import pandas as pd
        import iso_prices as ip
        cols = ["value", "x_sced_runs", "x_base_point_mwh", "x_as_regup_mwh", "x_as_regdn_mwh", "x_as_rrspfr_mwh",
                "x_as_rrsffr_mwh", "x_as_rrsufr_mwh", "x_as_ecrs_mwh", "x_as_nspin_mwh"]
        x = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=cols).apply(pd.to_numeric, errors="coerce")
        x = x[x["x_sced_runs"] >= 12]
        other = x[cols[5:]].abs().sum(axis=1)
        reg = x[((x["x_as_regup_mwh"] > 0.5) | (x["x_as_regdn_mwh"] > 0.5)) & (other < 1e-9)]
        dev = (reg["value"] - reg["x_base_point_mwh"]).to_numpy()
        coef, *_ = np.linalg.lstsq(np.column_stack([reg["x_as_regup_mwh"], -reg["x_as_regdn_mwh"]]), dev, rcond=None)
        self.assertTrue(0.10 < coef[0] < 0.25 and 0.10 < coef[1] < 0.25, f"called share up {coef[0]:.3f}, down {coef[1]:.3f}")


if __name__ == "__main__":
    unittest.main()
