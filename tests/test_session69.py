"""Session 69: storage_buildout_monthly, the storage build-out tracker's table.

Energy Research Warehouse (ERW). No request leaves the machine. The rules are tested on small made-up inventories
with made-up numbers (never written to a table); the sums are tested again on the scratch table built from the real
EIA-860M tables when this machine holds it (runs/session69/, skipped elsewhere), and on the page's fixture
(tests/fixtures/session69/, real values).

    python -m unittest tests.test_session69 -v
"""

import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived", "warehouse/validate"):
    sys.path.insert(0, os.path.join(ROOT, p))

import iso_prices as ip  # noqa: E402
import erw_validate  # noqa: E402
import storage_buildout as sb  # noqa: E402

SCRATCH = os.path.join(ROOT, "runs", "session69", "storage_buildout_monthly", "storage_buildout_monthly.csv")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session69", "storage_buildout_monthly.csv")
COLS = ["entity_id", "vintage", "source", "source_url", "balancing_authority", "technology_group", "prime_mover",
        "nameplate_mw", "status", "operating_year", "operating_month", "retirement_date", "planned_operation_date",
        "energy_capacity_mwh"]
NET = ["battery_operating_mw_net_added_12m", "battery_operating_mwh_net_added_12m"]
SUMS = (["battery_operating_mw", "battery_operating_mwh", "battery_operating_units", "solar_operating_mw"]
        + [f"battery_operating_mw_{b}" for b in sb.BUCKETS + [sb.NOT_REPORTED]]
        + [f"battery_operating_mwh_{b}" for b in sb.BUCKETS])


def unit(i, ba="ERCO", mw="10", mwh="20", y="2024", m="1", kind="battery", retired="", planned="", status="operating"):
    return dict(entity_id=f"eia860:{i}:1", vintage="2026-08", source="eia:860m", source_url="https://www.eia.gov/x.xlsx",
                balancing_authority=ba, technology_group="storage" if kind == "battery" else "solar",
                prime_mover="BA" if kind == "battery" else "PV", nameplate_mw=mw, status=status, operating_year=y,
                operating_month=m, retirement_date=retired, planned_operation_date=planned,
                energy_capacity_mwh=mwh if kind == "battery" else "")


def frame(rows):
    return pd.DataFrame(rows, columns=COLS).fillna("")


def inventory():
    """A made-up inventory: one unit per bucket edge, one without energy, units outside the ISOs, a retirement."""
    op = frame([
        unit(1, mw="10", mwh="19.9"),                      # 1.99 h: lt2h
        unit(2, mw="10", mwh="20"),                        # exactly 2 h: 2to4h
        unit(3, mw="10", mwh="40", y="2025", m="6"),       # exactly 4 h: 4to6h
        unit(4, mw="10", mwh="60", ba="CISO"),             # exactly 6 h: ge6h
        unit(5, mw="7.5", mwh="", ba="CISO"),              # no energy value
        unit(6, mw="3", mwh="6", ba="AZPS"),               # a balancing authority outside the seven
        unit(7, mw="2", mwh="1", ba=""),                   # no code at all
        unit(8, mw="100", kind="solar", y="2010"),
        unit(9, mw="50", kind="solar", ba="FPL", y="2026", m="8"),
    ])
    rt = frame([unit(10, mw="5", mwh="5", ba="PJM", y="2016", m="3", retired="2025-07-01", status="retired")])
    pl = frame([
        unit(11, mw="200", mwh="", y="", m="", planned="2027-03-01", status="planned"),
        unit(12, mw="80", mwh="", y="", m="", planned="2026-12-01", status="under_construction", ba="NEVP"),
        unit(13, mw="999", kind="solar", y="", m="", planned="2027-01-01", status="planned"),  # not a battery
    ])
    return op, pl, rt


def table(rows):
    return {(r.entity, r.variable, r.month): r.value for r in rows.itertuples()}


class Rules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.stats = sb.build(*inventory())
        cls.t = table(cls.rows)
        cls.months = sorted(set(cls.rows["month"]))

    def v(self, entity, variable, month="2026-08"):
        return self.t.get((entity, variable, month))

    def test_months_run_to_the_inventory_month(self):
        self.assertEqual((self.months[0], self.months[-1]), ("2015-01", "2026-08"))
        self.assertEqual(len(self.months), 140)

    def test_bucket_edges(self):
        self.assertEqual(sb.bucket_of(10, 19), "lt2h")
        self.assertEqual(sb.bucket_of(10, 20), "2to4h")
        self.assertEqual(sb.bucket_of(10, 39), "2to4h")
        self.assertEqual(sb.bucket_of(10, 40), "4to6h")
        self.assertEqual(sb.bucket_of(10, 60), "ge6h")
        self.assertEqual(sb.bucket_of(10, None), sb.NOT_REPORTED)
        with self.assertRaises(RuntimeError):
            sb.bucket_of(0, 5)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw_lt2h"), 10.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw_2to4h"), 10.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw_4to6h"), 10.0)
        self.assertEqual(self.v("iso:caiso", "battery_operating_mw_ge6h"), 10.0)

    def test_mw_by_bucket_sums_to_the_total(self):
        for e in sb.ENTITIES:
            for m in self.months:
                parts = sum(self.v(e, f"battery_operating_mw_{b}", m) for b in sb.BUCKETS + [sb.NOT_REPORTED])
                self.assertAlmostEqual(parts, self.v(e, "battery_operating_mw", m), places=6, msg=f"{e} {m}")
                mwh = sum(self.v(e, f"battery_operating_mwh_{b}", m) for b in sb.BUCKETS)
                self.assertAlmostEqual(mwh, self.v(e, "battery_operating_mwh", m), places=6, msg=f"{e} {m}")

    def test_no_energy_lands_in_not_reported_and_nowhere_else(self):
        self.assertEqual(self.v("iso:caiso", "battery_operating_mw_energy_not_reported"), 7.5)
        self.assertEqual(self.v("iso:caiso", "battery_operating_mw"), 17.5)
        # the duration buckets hold only the 10 MW unit; the 7.5 MW unit is in none of them
        self.assertEqual(sum(self.v("iso:caiso", f"battery_operating_mw_{b}") for b in sb.BUCKETS), 10.0)
        # its energy is not estimated: CAISO's MWh is the 60 MWh unit alone, and the average duration ignores its MW
        self.assertEqual(self.v("iso:caiso", "battery_operating_mwh"), 60.0)
        self.assertEqual(self.v("iso:caiso", "battery_operating_mwh_per_mw"), 6.0)
        self.assertEqual(self.stats["battery_no_energy"], 1)
        self.assertNotIn(("iso:caiso", "battery_operating_mwh_energy_not_reported", "2026-08"), self.t)

    def test_us_total_is_the_regions_plus_unassigned(self):
        for var in SUMS:
            for m in self.months:
                parts = sum(self.v(e, var, m) for e in sb.REGIONS)
                self.assertAlmostEqual(parts, self.v(sb.TOTAL, var, m), places=6, msg=f"{var} {m}")
        for var in ("battery_planned_mw", "battery_planned_units", "battery_planned_mw_under_construction",
                    "battery_planned_mw_online_2026", "battery_planned_mw_online_2027"):
            self.assertAlmostEqual(sum(self.v(e, var) for e in sb.REGIONS), self.v(sb.TOTAL, var), places=6, msg=var)

    def test_unassigned(self):
        self.assertEqual(self.v(sb.OUTSIDE, "battery_operating_mw"), 5.0)
        self.assertEqual(self.v(sb.OUTSIDE, "battery_operating_units"), 2.0)
        self.assertEqual(self.v(sb.OUTSIDE, "solar_operating_mw"), 50.0)
        o = self.stats["outside_battery"]
        self.assertEqual((o["units"], o["mw"], o["no_code_units"], o["no_code_mw"], o["codes"]), (2, 5.0, 1, 2.0, 1))
        self.assertEqual(self.stats["outside_planned"]["units"], 1)

    def test_a_unit_counts_from_its_first_month_to_the_month_before_it_retires(self):
        self.assertEqual(self.v("iso:pjm", "battery_operating_mw", "2016-02"), 0.0)
        self.assertEqual(self.v("iso:pjm", "battery_operating_mw", "2016-03"), 5.0)
        self.assertEqual(self.v("iso:pjm", "battery_operating_mw", "2025-06"), 5.0)
        self.assertEqual(self.v("iso:pjm", "battery_operating_mw", "2025-07"), 0.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw", "2025-05"), 20.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw", "2025-06"), 30.0)
        self.assertEqual(self.v("iso:ercot", "solar_operating_mw", "2015-01"), 100.0)  # operating before the first month

    def test_net_added_over_twelve_months(self):
        self.assertNotIn(("iso:ercot", "battery_operating_mw_net_added_12m", "2015-12"), self.t)  # no month twelve before
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw_net_added_12m", "2016-01"), 0.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mw_net_added_12m", "2024-12"), 20.0)
        self.assertEqual(self.v("iso:ercot", "battery_operating_mwh_net_added_12m", "2025-06"), 40.0)
        self.assertEqual(self.v("iso:pjm", "battery_operating_mw_net_added_12m", "2025-07"), -5.0)   # the retirement
        for m in self.months[12:]:
            for e in sb.ENTITIES:
                prev = f"{int(m[:4]) - 1}{m[4:]}"
                self.assertAlmostEqual(self.v(e, "battery_operating_mw_net_added_12m", m),
                                       self.v(e, "battery_operating_mw", m) - self.v(e, "battery_operating_mw", prev), places=6)

    def test_ratios_are_omitted_where_the_denominator_is_zero(self):
        self.assertNotIn(("iso:pjm", "battery_operating_mwh_per_mw", "2026-08"), self.t)   # no battery
        self.assertNotIn(("iso:caiso", "battery_mwh_per_solar_mw", "2026-08"), self.t)     # no solar
        self.assertEqual(self.v("iso:ercot", "battery_mwh_per_solar_mw"), 0.799)           # 79.9 MWh over 100 MW
        self.assertEqual(self.v("iso:ercot", "battery_operating_mwh_per_mw"), 2.6633)      # 79.9 over 30, half up

    def test_planned_by_year_online_and_no_planned_mwh(self):
        self.assertEqual(self.v("iso:ercot", "battery_planned_mw"), 200.0)
        self.assertEqual(self.v("iso:ercot", "battery_planned_mw_online_2027"), 200.0)
        self.assertEqual(self.v("iso:ercot", "battery_planned_mw_online_2026"), 0.0)
        self.assertEqual(self.v(sb.OUTSIDE, "battery_planned_mw_under_construction"), 80.0)
        self.assertEqual(self.v(sb.TOTAL, "battery_planned_mw"), 280.0)   # the planned solar unit is not a battery
        self.assertEqual(self.v(sb.TOTAL, "battery_planned_units"), 2.0)
        planned = self.rows[self.rows["variable"].str.startswith("battery_planned")]
        self.assertEqual(set(planned["month"]), {"2026-08"})              # at the inventory month only
        self.assertFalse(self.rows["variable"].str.contains("planned_mwh").any())  # never invented

    def test_fails_loudly(self):
        op, pl, rt = inventory()
        with self.assertRaises(RuntimeError):  # two vintages
            sb.build(op, pl.assign(vintage="2026-07"), rt)
        with self.assertRaises(RuntimeError):  # a unit in both tables
            sb.build(op, pl, frame([unit(1, retired="2025-07-01")]))
        with self.assertRaises(RuntimeError):  # no operating month
            sb.build(frame([unit(1, m="")]), pl, rt)
        with self.assertRaises(RuntimeError):  # a number the exact sum cannot hold
            sb.build(frame([unit(1, mw="1.00001")]), pl, rt)
        with self.assertRaises(RuntimeError):  # a planned battery with no date
            sb.build(op, frame([unit(11, y="", m="", planned="", status="planned")]), rt)


class Run(unittest.TestCase):
    """main() into a temporary directory: the table passes the validator, and a second run changes nothing."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw69_")
        self.saved = (ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)
        self.inputs = os.path.join(self.tmp, "inputs")
        os.makedirs(self.inputs)
        for name, df in zip(("operating", "planned", "retired"), inventory()):
            with open(os.path.join(self.inputs, sb.INPUTS[name] + ".csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a made-up inventory for tests/test_session69.py\n")
                df.to_csv(f, index=False, lineterminator="\n")

    def tearDown(self):
        ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scratch_run_validates_and_reruns_unchanged(self):
        out = os.path.join(self.tmp, "out")
        self.assertEqual(sb.main(["--inputs-dir", self.inputs, "--out-dir", out]), 0)
        path = os.path.join(out, sb.NAME + ".csv")
        rep = erw_validate.validate(path)
        self.assertEqual(rep["errors"], [], rep["errors"])
        first = ip.read_series(path)
        with open(path, encoding="utf-8") as f:
            head = [ln for ln in f if ln.startswith("#")]
        self.assertTrue(any(ln.startswith("# Derived from: eia860m_operating_generators; eia860m_planned_generators; "
                                          "eia860m_retired_generators") for ln in head))
        self.assertTrue(any(ln.startswith("# License: public.") for ln in head))
        self.assertFalse(any("—" in ln for ln in head))
        self.assertEqual(sb.main(["--inputs-dir", self.inputs, "--out-dir", out]), 0)
        second = ip.read_series(path)
        pd.testing.assert_frame_equal(first, second)  # Decision 26: unchanged rows keep their retrieved_at

    def test_missing_inputs_skip(self):
        os.remove(os.path.join(self.inputs, sb.INPUTS["retired"] + ".csv"))
        out = os.path.join(self.tmp, "out")
        self.assertEqual(sb.main(["--inputs-dir", self.inputs, "--out-dir", out]), 0)
        self.assertFalse(os.path.exists(os.path.join(out, sb.NAME + ".csv")))


def held(path):
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    d = pd.read_csv(path, skiprows=n)
    return {(r.entity, r.variable, r.ts_utc[:7]): r.value for r in d.itertuples()}, sorted(set(d["ts_utc"].str[:7]))


class RealSums(unittest.TestCase):
    """The same three sums on real values: the scratch table (this machine only) and the page's fixture."""

    def sums(self, path, every_month):
        t, months = held(path)
        newest = months[-1]
        for m in months:
            for e in sb.ENTITIES:
                parts = sum(t[(e, f"battery_operating_mw_{b}", m)] for b in sb.BUCKETS + [sb.NOT_REPORTED])
                self.assertAlmostEqual(parts, t[(e, "battery_operating_mw", m)], places=3, msg=f"{e} {m}")
                mwh = sum(t[(e, f"battery_operating_mwh_{b}", m)] for b in sb.BUCKETS)
                self.assertAlmostEqual(mwh, t[(e, "battery_operating_mwh", m)], places=3, msg=f"{e} {m}")
            for var in SUMS:
                self.assertAlmostEqual(sum(t[(e, var, m)] for e in sb.REGIONS), t[(sb.TOTAL, var, m)], places=3, msg=f"{var} {m}")
        for var in NET:  # the net additions are sums too, and each is its month less the month twelve before
            for (e, v, m), val in list(t.items()):
                if v != var:
                    continue
                base = var.replace("_net_added_12m", "")
                prev = f"{int(m[:4]) - 1}{m[4:]}"
                if (e, base, prev) in t:
                    self.assertAlmostEqual(val, t[(e, base, m)] - t[(e, base, prev)], places=3, msg=f"{e} {var} {m}")
                if e == sb.TOTAL:
                    self.assertAlmostEqual(sum(t[(r, var, m)] for r in sb.REGIONS), val, places=3, msg=f"{var} {m}")
        planned = sorted({k[1] for k in t if k[1].startswith("battery_planned")})
        self.assertIn("battery_planned_mw", planned)
        for var in planned:
            self.assertAlmostEqual(sum(t[(e, var, newest)] for e in sb.REGIONS), t[(sb.TOTAL, var, newest)], places=3, msg=var)
        years = [v for v in planned if v.startswith("battery_planned_mw_online_")]
        for e in sb.ENTITIES:  # the years online sum to the planned total
            self.assertAlmostEqual(sum(t[(e, v, newest)] for v in years), t[(e, "battery_planned_mw", newest)], places=3, msg=e)
        self.assertEqual(len(months) == 140, every_month)

    @unittest.skipUnless(os.path.exists(SCRATCH), "the scratch table is not on this machine")
    def test_scratch_table(self):
        self.sums(SCRATCH, True)

    @unittest.skipUnless(os.path.exists(FIXTURE), "the page's fixture is not written yet")
    def test_fixture(self):
        self.sums(FIXTURE, False)

    @unittest.skipUnless(os.path.exists(SCRATCH) and os.path.exists(FIXTURE), "needs the scratch table and the fixture")
    def test_fixture_is_the_scratch_tables_rows(self):
        a, _ = held(SCRATCH)
        b, _ = held(FIXTURE)
        self.assertTrue(b)
        for k, v in b.items():
            self.assertEqual(a[k], v, k)


if __name__ == "__main__":
    unittest.main()
