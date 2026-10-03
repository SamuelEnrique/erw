"""Session 67: the battery revenue stack (warehouse/derived/battery_stack.py).

Energy Research Warehouse (ERW). No request leaves the machine and no table is read: every day here is a toy day
with made-up prices, used only to test the solver's arithmetic.

    python -m unittest tests.test_session67 -v
"""

import itertools
import math
import os
import re
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import battery_stack as bs  # noqa: E402

quiet = lambda msg: None  # noqa: E731
GRID = (0.0, 0.5, 1.0)
BASE = dict(entity="caiso:X", freq="P1M", geo="US-CA", market="caiso", node="X", source="s", source_url="u",
            retrieved_at="r", vintage="")


def brute(energy, reserves, spec, duration):
    """The best day by exhaustive search at a round trip of 1: every hour takes each combination of charge, discharge
    and awards in steps of half the rated power, and every reachable (state of charge, energy cycled) is kept with its
    best revenue. Independent of the solver: it reads the rules, not the constraint matrix."""
    layer = {(0.0, 0.0): 0.0}
    for t in range(len(energy)):
        nxt = {}
        for (soc, cyc), val in layer.items():
            for c, d in itertools.product(GRID, GRID):
                if c > 0 and d > 0:
                    continue
                s2, c2 = soc + c - d, cyc + d
                if s2 < 0 or s2 > duration or c2 > duration:
                    continue
                for aw in itertools.product(GRID, repeat=len(spec)):
                    up = sum(a for a, (is_up, _) in zip(aw, spec) if is_up)
                    dn = sum(a for a, (is_up, _) in zip(aw, spec) if not is_up)
                    if d + up > 1 or c + dn > 1:
                        continue
                    need_up = sum(a * h for a, (is_up, h) in zip(aw, spec) if is_up)
                    need_dn = sum(a * h for a, (is_up, h) in zip(aw, spec) if not is_up)
                    if need_up > min(soc, s2) or need_dn > duration - max(soc, s2):
                        continue
                    v = val + energy[t] * (d - c) + sum(a * r[t] for a, r in zip(aw, reserves))
                    if v > nxt.get((s2, c2), -math.inf):
                        nxt[(s2, c2)] = v
        layer = nxt
    return max(layer.values())


def energy_only(prices, duration, rte):
    """The energy-only optimum at the same resolution, written on its own: charge and discharge only."""
    from scipy.optimize import linprog
    T, eta = len(prices), math.sqrt(rte)
    p = np.asarray(prices, dtype=float)
    low = np.tril(np.ones((T, T)))
    soc = np.hstack([eta * low, -low / eta])
    A = np.vstack([soc, -soc, np.hstack([np.zeros(T), np.ones(T) / eta])])
    b = np.concatenate([np.full(T, duration), np.zeros(T), [duration]])
    res = linprog(np.concatenate([p, -p]), A_ub=A, b_ub=b, bounds=(0, 1), method="highs")
    return -res.fun


class Solver(unittest.TestCase):
    def test_equals_brute_force_on_toy_days(self):
        rng = np.random.default_rng(67)
        spec = ((True, 1.0), (False, 1.0), (True, 2.0))
        for _ in range(12):
            T = 5
            energy = rng.integers(5, 90, T).astype(float)
            reserves = [rng.integers(0, 30, T).astype(float) for _ in spec]
            for duration in (2, 4):
                sol = bs.solve_day(energy, reserves, spec, duration, rte=1.0)
                self.assertAlmostEqual(sol["total"], brute(energy, reserves, spec, duration), places=6)
                self.assertEqual(bs.check_day(sol, spec, duration, rte=1.0), [])

    def test_a_known_day_by_hand(self):
        # 1 MW, 2 hours, no losses, one upward product of one hour. Charge in the two cheap hours (cost 20), hold the
        # reserve in hour 3 at 50 with the energy stored, then discharge both hours at 100: 200 - 20 + 50 = 230.
        energy = [10, 10, 60, 100, 100]
        res = [[0, 0, 50, 0, 0]]
        sol = bs.solve_day(energy, res, ((True, 1.0),), 2, rte=1.0)
        self.assertAlmostEqual(sol["total"], 230.0, places=6)
        self.assertAlmostEqual(sol["energy"], 180.0, places=6)
        self.assertAlmostEqual(sol["reserve"][0], 50.0, places=6)

    def test_no_double_counting_in_one_hour(self):
        # energy at 100 and a reserve at 90 in the same priced hour: the battery is paid one or the other, never both
        energy = [0, 0, 100]
        res = [[0, 0, 90]]
        sol = bs.solve_day(energy, res, ((True, 1.0),), 4, rte=1.0)
        self.assertAlmostEqual(sol["total"], 100.0, places=6)
        self.assertLessEqual(sol["discharge"][2] + sol["awards"][0][2], 1 + 1e-9)

    def test_zero_ancillary_prices_reproduce_the_energy_only_optimum(self):
        rng = np.random.default_rng(3)
        spec = tuple((p["up"], 1.0) for p in bs.MARKETS["ercot"]["products"])
        compared = 0
        for T in (23, 24, 25):
            for lo in (-20, 5):
                energy = rng.uniform(lo, 200, T)
                zeros = [np.zeros(T) for _ in spec]
                for duration in bs.DURATIONS:
                    sol = bs.solve_day(energy, zeros, spec, duration)
                    if not sol["mip"]:
                        self.assertAlmostEqual(sol["total"], energy_only(energy, duration, bs.RTE), places=5)
                        compared += 1
                    self.assertAlmostEqual(sum(sol["reserve"]), 0.0, places=9)
                    self.assertAlmostEqual(sol["total"], sol["energy"], places=9)
        self.assertGreaterEqual(compared, 9)

    def test_energy_only_matches_the_seller_tab_battery_without_losses(self):
        import merchant_revenue as mr
        self.assertEqual(bs.RTE, mr.RTE)
        rng = np.random.default_rng(5)
        for _ in range(5):
            energy = rng.uniform(5, 120, 24)
            for duration in (2, 4):
                sol = bs.solve_day(energy, [], (), duration, rte=1.0)
                self.assertAlmostEqual(sol["total"], mr.battery_day(list(energy), duration, rte=1.0)[0], places=5)
                # with losses the seller tab battery moves at full power or not at all, so it can only earn less
                lossy = bs.solve_day(energy, [], (), duration)
                self.assertGreaterEqual(lossy["total"] + 1e-6, mr.battery_day(list(energy), duration)[0])

    def test_constraints_hold_in_every_hour(self):
        rng = np.random.default_rng(11)
        m = bs.MARKETS["ercot"]
        for day in ("2019-08-13", "2023-08-17", "2026-03-01"):
            prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
            spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
            energy = rng.uniform(-30, 400, 24)
            reserves = [rng.uniform(0, 60, 24) for _ in spec]
            for duration in bs.DURATIONS:
                sol = bs.solve_day(energy, reserves, spec, duration)
                self.assertEqual(bs.check_day(sol, spec, duration), [])
                up = sum(a for a, (is_up, _) in zip(sol["awards"], spec) if is_up)
                dn = sum(a for a, (is_up, _) in zip(sol["awards"], spec) if not is_up)
                self.assertTrue(np.all(sol["discharge"] + up <= 1 + 1e-6))
                self.assertTrue(np.all(sol["charge"] + dn <= 1 + 1e-6))
                self.assertAlmostEqual(sol["total"], sol["energy"] + sum(sol["reserve"]), places=9)

    def test_never_charges_and_discharges_in_one_hour(self):
        # a negative price pays a battery to charge; the relaxation would also discharge in the same hour to charge more
        energy = [-50.0] * 4
        sol = bs.solve_day(energy, [], (), 2)
        self.assertTrue(sol["mip"])
        self.assertTrue(np.all(np.minimum(sol["charge"], sol["discharge"]) < 1e-6))
        self.assertEqual(bs.check_day(sol, (), 2), [])

    def test_longer_duration_never_earns_less(self):
        rng = np.random.default_rng(8)
        spec = tuple((p["up"], bs.required_hours(p, "2024-06-01")[0]) for p in bs.MARKETS["ercot"]["products"])
        for _ in range(10):
            energy = rng.uniform(-10, 300, 24)
            reserves = [rng.uniform(0, 40, 24) for _ in spec]
            two, four, eight = (bs.solve_day(energy, reserves, spec, d)["total"] for d in (2, 4, 8))
            self.assertGreaterEqual(four + 1e-6, two)
            self.assertGreaterEqual(eight + 1e-6, four)


class Durations(unittest.TestCase):
    def test_required_hours_by_period(self):
        p = {x["key"]: x for x in bs.MARKETS["ercot"]["products"]}
        self.assertEqual(bs.required_hours(p["nspin"], "2022-12-08")[0], 1.0)
        self.assertEqual(bs.required_hours(p["nspin"], "2022-12-09")[0], 4.0)
        self.assertEqual(bs.required_hours(p["ecrs"], "2023-06-10")[0], 2.0)
        self.assertEqual(bs.required_hours(p["ecrs"], "2025-12-05")[0], 1.0)
        self.assertEqual(bs.required_hours(p["regup"], "2025-12-04")[0], 1.0)
        self.assertEqual(bs.required_hours(p["rrs"], "2025-12-05")[0], 0.5)
        self.assertIn("NPRR1282", bs.required_hours(p["rrs"], "2026-01-01")[1])
        self.assertIn("not verified", bs.required_hours(p["regup"], "2020-01-01")[1])
        # session 76: California's rules are the tariff's (Section 8): Regulation one hour day-ahead, 8.4.1.1(g);
        # Spinning and Non-Spinning Reserve 30 minutes, 8.4.3. None is assumed any more.
        for x in bs.MARKETS["caiso"]["products"]:
            hours, src = bs.required_hours(x, "2025-01-01")
            self.assertEqual(hours, 0.5 if x["key"] in ("spin", "nonspin") else 1.0)
            self.assertIn("8.4.3" if x["key"] in ("spin", "nonspin") else "8.4.1.1(g)", src)
            self.assertNotIn("not verified", src)


def hours(start, n):
    return pd.date_range(start, periods=n, freq="h", tz="UTC")


class Days(unittest.TestCase):
    """build_market on a made-up three-day market: a day without ancillary prices is left out and counted."""

    def market(self, drop=None):
        idx = hours("2024-09-01T07:00:00Z", 72)  # three Pacific days
        rng = np.random.default_rng(2)
        e = pd.Series(rng.uniform(10, 80, 72), index=idx)
        reserve = {p["key"]: pd.Series(rng.uniform(0, 10, 72), index=idx) for p in bs.MARKETS["caiso"]["products"]}
        if drop:
            reserve[drop[0]] = reserve[drop[0]].drop(idx[drop[1]])
        return {"rtm": e, "dam": e * 0.9}, reserve

    def test_a_day_missing_ancillary_prices_is_left_out_and_counted(self):
        energy, reserve = self.market(drop=("spin", 30))  # one hour of the second day
        days, left = bs.build_market("caiso", energy, reserve, quiet)
        for strat in bs.STRATEGIES:
            self.assertEqual(sorted(days[(strat, 4)]), ["2024-09-01", "2024-09-03"])
            self.assertEqual([d for d, _ in left[strat]], ["2024-09-02"])
            self.assertTrue(left[strat][0][1].startswith("ancillary: spin"))
        rows = pd.DataFrame(bs.monthly_rows("caiso", days, left, BASE))
        v = rows.set_index("variable")["value"]
        self.assertEqual(v["foresight_4h_days_held"], 2)
        self.assertEqual(v["foresight_4h_days_left_out"], 1)
        self.assertEqual(v["foresight_4h_days_left_out_ancillary"], 1)
        self.assertEqual(v["foresight_4h_days_left_out_energy"], 0)
        # the month's revenue is the two held days' and nothing else: no fill for the day left out
        want = sum(days[("foresight", 4)][d]["total"] for d in ("2024-09-01", "2024-09-03"))
        self.assertAlmostEqual(v["foresight_4h_revenue_total_usd_per_mw"], want, places=3)
        self.assertAlmostEqual(v["foresight_4h_revenue_total_usd_per_mw"],
                               v["foresight_4h_revenue_energy_usd_per_mw"] + v["foresight_4h_revenue_ancillary_usd_per_mw"], places=3)
        parts = sum(v[f"foresight_4h_revenue_{k}_usd_per_mw"] for k in ("regup", "regdn", "spin", "nonspin"))
        self.assertAlmostEqual(v["foresight_4h_revenue_ancillary_usd_per_mw"], parts, places=3)

    def test_a_day_missing_an_energy_hour_is_left_out(self):
        energy, reserve = self.market()
        energy["rtm"] = energy["rtm"].drop(energy["rtm"].index[5])
        days, left = bs.build_market("caiso", energy, reserve, quiet)
        self.assertEqual(sorted(days[("foresight", 2)]), ["2024-09-02", "2024-09-03"])
        self.assertTrue(left["foresight"][0][1].startswith("energy"))
        self.assertEqual(len(days[("dayahead", 2)]), 3)

    def test_duration_order_holds_every_day(self):
        energy, reserve = self.market()
        days, _ = bs.build_market("caiso", energy, reserve, quiet)
        for strat in bs.STRATEGIES:
            for d in days[(strat, 2)]:
                self.assertGreaterEqual(days[(strat, 4)][d]["total"] + 1e-6, days[(strat, 2)][d]["total"])
                self.assertGreaterEqual(days[(strat, 8)][d]["total"] + 1e-6, days[(strat, 4)][d]["total"])

    def test_no_month_without_a_held_day_gets_a_revenue_row(self):
        days = {(s, d): {} for s in bs.STRATEGIES for d in bs.DURATIONS}
        left = {s: [("2024-09-01", "ancillary: spin")] for s in bs.STRATEGIES}
        rows = pd.DataFrame(bs.monthly_rows("caiso", days, left, BASE))
        self.assertFalse(rows["variable"].str.contains("revenue").any())
        self.assertTrue((rows.loc[rows["x_metric"] == "days_left_out", "value"] == 1).all())


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Site(unittest.TestCase):
    """The page, the contract panel and the release gate, read as text: what they must and must not hold."""

    LIVE = ["/", "/cost-of-power/battery", "/cost-of-power/seller", "/network", "/storage", "/about", "/terms",
            "/data/methods/battery_stack", "/data/methods/cost_of_power", "/data/methods/grid_network", "/data/methods/storage"]

    def release(self):
        return dict(re.findall(r'^\s*"(/[^"]*)": "(live|review)",', read("site", "lib", "release.ts"), flags=re.M))

    def test_the_release_list_holds_every_page_and_the_live_ones_are_the_approved_ones(self):
        rel = self.release()
        self.assertEqual(sorted(k for k, v in rel.items() if v == "live"), sorted(self.LIVE))
        hrefs = set(re.findall(r'\{ href: "(/[^"]*)", label:', read("site", "lib", "pages.ts")))
        self.assertGreater(len(hrefs), 30)

        def status(path):
            while True:
                if path in rel:
                    return rel[path]
                i = path.rfind("/")
                if i <= 0:
                    return "review"
                path = path[:i]
        for h in sorted(hrefs):
            self.assertEqual(status(h), "live" if h in self.LIVE else "review", h)
            self.assertTrue(any(h == k or h.startswith(k + "/") for k in rel), f"{h} has no line in the release list")
        self.assertEqual(rel["/board"], "review")  # the price board included
        for g in ("ercot", "caiso", "pjm", "nyiso", "isone", "miso", "spp"):
            self.assertEqual(rel[f"/grid/{g}"], "review")

    def test_the_gate_leaves_the_api_and_the_internal_routes_alone(self):
        proxy = read("site", "proxy.ts")
        self.assertIn("api/", proxy)
        self.assertIn("internal/", proxy)
        self.assertIn("INTERNAL_COSTS_TOKEN", proxy)
        unlock = read("site", "app", "internal", "unlock", "route.ts")
        self.assertIn("httpOnly: true", unlock)
        self.assertIn("MAX_AGE", unlock)
        self.assertIn("90 * 24 * 3600", read("site", "lib", "release.ts"))
        self.assertNotIn("set(COOKIE, token", unlock)  # the cookie holds a digest, never the token

    def test_the_contract_terms_cannot_leave_the_browser(self):
        c = read("site", "app", "cost-of-power", "battery", "Contract.tsx")
        for bad in ("fetch(", "localStorage", "sessionStorage", "document.cookie", "useRouter", "URLSearchParams", "name=", "<form", "console.",
                    "sendBeacon", "XMLHttpRequest"):
            self.assertFalse(bad in c, f"Contract.tsx holds {bad}")
        self.assertIn("Computed on this device. Nothing you type here is sent or stored.", c)
        form = read("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        for k in ("share", "price", "end"):
            self.assertNotIn(f'name="{k}"', form)
        self.assertIn("/cost-of-power/battery", read("site", "components", "SiteLink.tsx"))  # no prefetch on the page

    def test_no_capacity_value_can_reach_the_page(self):
        for name in ("page.tsx", "Contract.tsx", "BatteryForm.tsx"):
            text = read("site", "app", "cost-of-power", "battery", name)
            self.assertFalse("capacity_prices" in text, f"{name} names a capacity table")
        self.assertFalse("capacity_prices" in read("site", "lib", "batterystack.ts"), "lib/batterystack.ts names a capacity table")
        self.assertEqual({m["as_table"] for m in bs.MARKETS.values()}, {"ercot_as_prices", "caiso_as_prices"})
        self.assertNotIn('read_table("iso_all_capacity_prices"', read("warehouse", "derived", "battery_stack.py"))
        page = read("site", "app", "cost-of-power", "battery", "page.tsx")
        for words in ("Held, not shown: publishing requires a license from the market operator", "Held: license under review", "No capacity market",
                      "not yet in the warehouse", "not held, licensed"):
            self.assertIn(words, page)
        lib = read("site", "lib", "batterystack.ts")
        self.assertIn("None: an energy-only market", lib)
        self.assertIn("Not held: California's resource adequacy prices are contract statistics, not yet in the warehouse", lib)

    def test_the_page_and_the_builder_agree(self):
        lib = read("site", "lib", "batterystack.ts")
        self.assertIn(f"export const RTE = {bs.RTE};", lib)
        self.assertEqual([int(x) for x in re.search(r"DURATIONS: Duration\[\] = \[([^\]]*)\]", lib).group(1).split(",")], bs.DURATIONS)
        block = lib[lib.index("export const PRODUCTS"):lib.index("export const CAPACITY_WORDS")]
        for iso, m in bs.MARKETS.items():
            keys = re.findall(r'key: "([a-z]+)"', block[block.index(f"{iso}: ["):].split("],")[0])
            self.assertEqual(sorted(keys), sorted(p["key"] for p in m["products"]), iso)
        self.assertIn(f'"{bs.NAME}"', lib)
        self.assertIn(f'"{bs.STRESS_NAME}"', lib)

    def test_the_daily_run_refreshes_the_stack_under_health(self):
        sh = read("warehouse", "run_daily.sh")
        for step in ("ercot_as_prices", "caiso_as_prices", "iso_capacity_prices", "battery_stack"):
            line = next(ln for ln in sh.splitlines() if ln.strip().startswith(f"run_other {step} "))
            self.assertIn("warehouse/health.py run --strict --step", line, step)
            self.assertNotIn("|", line, step)  # a gate is never piped
        self.assertLess(sh.index('if [ "$(date -u +%d)" = "01" ]'), sh.index("run_other iso_capacity_prices"))
        self.assertLess(sh.index("run_other caiso_as_prices"), sh.index("run_other battery_stack"))
        cfg = read("warehouse", "redivis", "config.yaml")
        self.assertIn("'^battery_stack_(monthly|stress_daily)$'", cfg)
        self.assertIn("'^caiso_as_prices$'", cfg)
        self.assertIn("'^battery_stack_(monthly|stress_daily)$'", read("warehouse", "supabase", "live_set.yaml"))

    def test_no_em_dash_in_the_session_files(self):
        for parts in (("warehouse", "derived", "battery_stack.py"), ("docs", "methods", "battery_stack.md"), ("docs", "release-gate.md"),
                      ("site", "lib", "batterystack.ts"), ("site", "lib", "release.ts"), ("site", "proxy.ts"), ("site", "components", "tool", "ToolPage.tsx"),
                      ("site", "app", "cost-of-power", "battery", "page.tsx"), ("site", "app", "cost-of-power", "battery", "Contract.tsx"),
                      ("site", "app", "cost-of-power", "battery", "BatteryForm.tsx"), ("site", "app", "in-review", "page.tsx"),
                      ("site", "scripts", "test-battery-stack.mjs"), ("tests", "test_session67.py")):
            self.assertFalse(chr(0x2014) in read(*parts) or chr(0x2013) in read(*parts), f"{parts[-1]} holds a dash that is not a hyphen")


class Carry(unittest.TestCase):
    """keep_fuller: a machine without the full history never replaces a month with one resting on fewer days."""

    def frame(self, rows):
        cols = bs.ip.SERIES_COLS + ["x_strategy", "x_duration_hours", "x_metric"]
        return pd.DataFrame([dict(BASE, ts_utc=t, variable=f"foresight_4h_{m}", value=v, unit="count", x_strategy="foresight",
                                  x_duration_hours=4, x_metric=m) for t, m, v in rows])[cols], cols

    def test_a_fuller_month_is_kept_and_an_unreached_month_is_carried(self):
        old, cols = self.frame([("2026-08-01T00:00:00Z", "days_held", 31.0), ("2026-08-01T00:00:00Z", "revenue_total_usd_per_mw", 500.0),
                                ("2026-09-01T00:00:00Z", "days_held", 30.0), ("2026-09-01T00:00:00Z", "revenue_total_usd_per_mw", 400.0),
                                ("2026-10-01T00:00:00Z", "days_held", 1.0), ("2026-10-01T00:00:00Z", "revenue_total_usd_per_mw", 10.0)])
        new, _ = self.frame([("2026-09-01T00:00:00Z", "days_held", 12.0), ("2026-09-01T00:00:00Z", "revenue_total_usd_per_mw", 150.0),
                             ("2026-10-01T00:00:00Z", "days_held", 3.0), ("2026-10-01T00:00:00Z", "revenue_total_usd_per_mw", 33.0)])
        with tempfile.TemporaryDirectory() as d:
            was = bs.ip.OUT_DIR
            bs.ip.OUT_DIR = d
            try:
                old.to_csv(os.path.join(d, bs.NAME + ".csv"), index=False)
                out, kept = bs.keep_fuller(bs.NAME, new, cols, quiet)
            finally:
                bs.ip.OUT_DIR = was
        v = out.set_index(["ts_utc", "x_metric"])["value"]
        self.assertEqual(v[("2026-08-01T00:00:00Z", "revenue_total_usd_per_mw")], 500.0)  # not reached: carried
        self.assertEqual(v[("2026-09-01T00:00:00Z", "revenue_total_usd_per_mw")], 400.0)  # 30 days beat 12: kept
        self.assertEqual(v[("2026-10-01T00:00:00Z", "revenue_total_usd_per_mw")], 33.0)   # 3 days beat 1: replaced
        self.assertEqual(kept, 4)
        self.assertEqual(len(out), 6)


if __name__ == "__main__":
    unittest.main()
