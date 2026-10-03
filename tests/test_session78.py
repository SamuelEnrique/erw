"""Session 78: California from the join (warehouse/derived/caiso_join.py).

Energy Research Warehouse (ERW). The toy frames here are made-up numbers used only to test the join's arithmetic and
its one rule: no series mixes the two sources on one side of the join. The last class reads the built tables where a
machine holds them, and skips where it does not. No request leaves the machine.

    python -m unittest tests.test_session78 -v
"""

import os
import re
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import caiso_join as cj  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SCRATCH = os.path.join(ROOT, "runs", "session78")


def hours(first, n):
    return list(pd.date_range(first, periods=n, freq="h", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"))


def toy(first="2025-12-14T00:00:00Z", n=24 * 21, caiso_gap=()):
    """EIA hours (CO2 generated 100 t, net generation 1,000 MWh, so 100 kg/MWh) and CAISO hours from the join (net
    generation 1,250 MWh, so 80 kg/MWh), every hour, less the hours in caiso_gap."""
    idx = hours(first, n)
    eia = pd.DataFrame({"co2_emissions_generated": 100.0, "co2_emissions_consumed": 150.0, "co2_emissions_natural_gas": 81.02,
                        "net_generation_mwh": 1000.0, "demand_mwh": 1500.0}, index=idx)
    c = [h for h in idx if h >= "2025-12-10" and h not in caiso_gap]
    caiso = pd.DataFrame({"net_generation_mwh": 1250.0, "natural_gas_mw": 200.0}, index=c)
    return eia, caiso


class Constant(unittest.TestCase):
    def test_the_join_is_the_hour_session_73_found(self):
        self.assertEqual(cj.JOIN, "2025-12-16T08:00:00Z")
        self.assertEqual((cj.JOIN_DAY, cj.JOIN_MONTH), ("2025-12-16", "2025-12"))

    def test_no_other_code_names_the_date(self):
        """One constant: the join's date is written in caiso_join.py and in the site's copy of it, and nowhere else in
        the code that builds tables or pages (documents, reports, tests and session 73's analysis of the break aside)."""
        allowed = {"warehouse/derived/caiso_join.py", "site/lib/caisoJoin.ts", "warehouse/analysis/eia930_break.py",
                   "warehouse/analysis/eia930_break_numbers.py"}
        found = []
        for top, exts in (("warehouse", (".py", ".sh", ".yaml")), ("site/app", (".ts", ".tsx")), ("site/lib", (".ts", ".tsx")),
                          ("site/components", (".ts", ".tsx")), ("package/src", (".py",))):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("node_modules", "__pycache__", "output", "raw", ".next")]
                for f in files:
                    if not f.endswith(exts):
                        continue
                    rel = os.path.relpath(os.path.join(d, f), ROOT).replace("\\", "/")
                    with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                        text = fh.read()
                    if re.search(r"2025-12-16|16 December 2025|December 16, 2025", text) and rel not in allowed:
                        found.append(rel)
        # session 75's shoulder table stops California a month before the break and says why (its builder's comment and
        # its page's note); session 73's connector names the break in its header: notes, not a second join date
        found = [f for f in found if f not in ("warehouse/derived/shoulder_hours.py", "warehouse/connectors/caiso_fuel_supply.py",
                                               "site/lib/shoulder.ts")]
        self.assertEqual(found, [])

    def test_the_site_holds_the_same_constant(self):
        with open(os.path.join(ROOT, "site", "lib", "caisoJoin.ts"), encoding="utf-8") as f:
            m = re.search(r'CAISO_JOIN = "([^"]+)"', f.read())
        self.assertEqual(m.group(1), cj.JOIN)


class Sides(unittest.TestCase):
    def test_period_side(self):
        self.assertEqual(cj.period_side("2025-12-16T07:00:00Z", "PT1H"), "before")
        self.assertEqual(cj.period_side("2025-12-16T08:00:00Z", "PT1H"), "after")
        self.assertEqual([cj.period_side(f"2025-12-{d}T00:00:00Z", "P1D") for d in (15, 16, 17)], ["before", "both", "after"])
        self.assertEqual([cj.period_side(f"{m}-01T00:00:00Z", "P1M") for m in ("2025-11", "2025-12", "2026-01")],
                         ["before", "both", "after"])

    def test_before_the_join_every_hour_is_eia_and_from_it_every_hour_is_caiso(self):
        eia, caiso = toy()
        j = cj.joined(eia, caiso)
        self.assertEqual(set(j.loc[j.index < cj.JOIN, "side"]), {"eia930"})
        self.assertEqual(set(j.loc[j.index >= cj.JOIN, "side"]), {"caiso"})
        self.assertTrue((j.loc[j.index < cj.JOIN, "net_generation_mwh"] == 1000).all())   # CAISO's hours before it are not used
        self.assertTrue((j.loc[j.index >= cj.JOIN, "net_generation_mwh"] == 1250).all())  # EIA's generation from it is not used
        self.assertEqual(len(j), len(eia))

    def test_an_hour_caiso_does_not_hold_is_absent_never_eia(self):
        gap = hours("2025-12-20T05:00:00Z", 3)
        eia, caiso = toy(caiso_gap=gap)
        j = cj.joined(eia, caiso)
        for h in gap:
            self.assertNotIn(h, j.index)
        self.assertEqual(len(j), len(eia) - 3)

    def test_before_join_keeps_only_the_hours_before_it(self):
        f = pd.DataFrame({"ts_utc": ["2025-12-16T07:00:00Z", "2025-12-16T08:00:00Z", "2026-01-01T00:00:00Z"], "v": [1, 2, 3]})
        self.assertEqual(list(cj.before_join(f)["v"]), [1])


class Rows(unittest.TestCase):
    def test_values_by_hand_and_the_periods_that_hold_the_join_are_left_out(self):
        eia, caiso = toy(first="2025-11-01T00:00:00Z", n=24 * 92)  # November 2025 to January 2026
        rows = cj.intensity_rows(cj.joined(eia, caiso), "2026-10-03T00:00:00Z")
        h, d, m = (rows[t] for t in cj.TABLES)
        self.assertEqual(set(h["value"]), {80.0})                       # 100 t x 1000 / 1,250 MWh
        self.assertEqual(h["ts_utc"].min(), cj.JOIN)
        self.assertNotIn("2025-12-16T00:00:00Z", set(d["ts_utc"]))      # the day that holds the join: 16 hours of CAISO's
        self.assertEqual(d["ts_utc"].min(), "2025-12-17T00:00:00Z")
        self.assertEqual(list(m["ts_utc"]), ["2026-01-01T00:00:00Z"])   # December holds the join and is not written
        for t in (h, d, m):
            self.assertEqual(set(t["source"]), {cj.SOURCE_JOIN})
            self.assertEqual(set(t["variable"]), {cj.VARIABLE})
            self.assertEqual(list(t.columns), cj.COLS)

    def test_a_day_short_of_an_hour_and_its_month_are_not_written(self):
        eia, caiso = toy(first="2025-12-01T00:00:00Z", n=24 * 62, caiso_gap=["2026-01-10T03:00:00Z"])
        rows = cj.intensity_rows(cj.joined(eia, caiso), "2026-10-03T00:00:00Z")
        self.assertNotIn("2026-01-10T00:00:00Z", set(rows["carbon_intensity_daily"]["ts_utc"]))
        self.assertEqual(len(rows["carbon_intensity_monthly"]), 0)

    def test_the_gas_ratio_is_eia_co2_over_caiso_gas(self):
        eia, caiso = toy()
        ratio, n = cj.gas_ratio(eia, caiso)
        self.assertAlmostEqual(ratio, 81.02 / 200.0)
        self.assertEqual(n, int((eia.index >= cj.JOIN).sum()))


class Splice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inp, self.out = os.path.join(self.tmp, "in"), os.path.join(self.tmp, "out")
        os.makedirs(self.inp)
        os.makedirs(self.out)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def held(self, name, freq, stamps):
        base = "kgCO2/MWh,{f},{g},,,erw:carbon_intensity,u,r,,{b}"
        lines = ["# a held table", ",".join(cj.COLS)]
        for ent, geo, ba in (("eia930:AAAA", "US-AA", "aaaa"), ("eia930:CISO", "US-CA", "ciso"), ("eia930:ERCO", "US-TX", "erco")):
            for var in ("intensity_demand", "intensity_generation"):
                for ts in stamps:
                    lines.append(f"{ent},{var},{ts},100.0," + base.format(f=freq, g=geo, b=ba))
        with open(os.path.join(self.inp, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines) + "\n")

    def test_only_californias_generation_from_the_join_changes(self):
        stamps = ["2025-12-15T00:00:00Z", "2025-12-16T00:00:00Z", "2025-12-17T00:00:00Z", "2025-12-18T00:00:00Z"]
        self.held("carbon_intensity_daily", "P1D", stamps)
        new = pd.DataFrame([dict(entity=cj.ENTITY, variable=cj.VARIABLE, ts_utc="2025-12-17T00:00:00Z", value=80.0, unit="kgCO2/MWh",
                                 freq="P1D", geo="US-CA", market="", node="", source=cj.SOURCE_JOIN, source_url="u", retrieved_at="r",
                                 vintage="", ba="ciso")])[cj.COLS]
        c = cj.splice("carbon_intensity_daily", new, self.inp, self.out, ["a note"])
        self.assertEqual((c["kept"], c["dropped"], c["added"]), (21, 3, 1))
        a = pd.read_csv(os.path.join(self.inp, "carbon_intensity_daily.csv"), comment="#", dtype=str, keep_default_na=False)
        b = pd.read_csv(os.path.join(self.out, "carbon_intensity_daily.csv"), comment="#", dtype=str, keep_default_na=False)
        ours = lambda d: (d["entity"] == cj.ENTITY) & (d["variable"] == cj.VARIABLE)  # noqa: E731
        self.assertTrue(a[~ours(a)].reset_index(drop=True).equals(b[~ours(b)].reset_index(drop=True)))
        got = b[ours(b)]
        self.assertEqual(list(got["ts_utc"]), ["2025-12-15T00:00:00Z", "2025-12-17T00:00:00Z"])  # the 16th and the 18th are gone
        self.assertEqual(list(got["source"]), [cj.SOURCE_EIA, cj.SOURCE_JOIN])
        self.assertEqual(list(b["entity"]), sorted(b["entity"]))  # the file's order is kept: California's rows stay in its block
        with open(os.path.join(self.out, "carbon_intensity_daily.csv"), encoding="utf-8") as f:
            head = [ln for ln in f if ln.startswith("#")]
        self.assertEqual(head, ["# a held table\n", "# a note\n"])

    def test_check_joined_names_a_row_on_the_wrong_side(self):
        for name, freq, stamps in (("carbon_intensity_hourly", "PT1H", ["2025-12-16T07:00:00Z", "2025-12-16T08:00:00Z"]),
                                   ("carbon_intensity_daily", "P1D", ["2025-12-15T00:00:00Z", "2025-12-17T00:00:00Z"]),
                                   ("carbon_intensity_monthly", "P1M", ["2025-11-01T00:00:00Z", "2026-01-01T00:00:00Z"])):
            self.held(name, freq, stamps)
            shutil.copy(os.path.join(self.inp, name + ".csv"), os.path.join(self.out, name + ".csv"))
        bad = cj.check_joined(self.inp, self.out)  # the held tables themselves: EIA's rows from the join
        self.assertEqual(len(bad), 3)
        self.assertTrue(all(cj.SOURCE_JOIN in b for b in bad), bad)

    def test_the_scratch_build_refuses_warehouse_output(self):
        with self.assertRaises(RuntimeError):
            cj.build(out_dir=cj.OUT_DIR)
        with self.assertRaises(RuntimeError):
            cj.build(out_dir=None)


HAVE = all(os.path.exists(os.path.join(SCRATCH, t + ".csv")) and os.path.exists(os.path.join(OUT, t + ".csv")) for t in cj.TABLES)


@unittest.skipUnless(HAVE, "the built tables (runs/session78) or the held ones are not on this machine")
class Built(unittest.TestCase):
    def test_no_series_mixes_the_two_sources_on_one_side_of_the_join(self):
        self.assertEqual(cj.check_joined(OUT, SCRATCH), [])
        for name, freq in cj.TABLES.items():
            b = pd.read_csv(os.path.join(SCRATCH, name + ".csv"), comment="#", dtype=str, keep_default_na=False)
            ca = b[b["entity"] == cj.ENTITY]
            gen = ca[ca["variable"] == cj.VARIABLE]
            side = gen["ts_utc"].map(lambda ts: cj.period_side(ts, freq))
            self.assertEqual(set(gen.loc[side == "before", "source"]), {cj.SOURCE_EIA}, name)
            self.assertEqual(set(gen.loc[side == "after", "source"]), {cj.SOURCE_JOIN}, name)
            self.assertFalse((side == "both").any(), name)
            self.assertGreater(int((side == "after").sum()), 0, name)
            # the consumed intensity is EIA's on both sides, one source throughout
            self.assertEqual(set(ca.loc[ca["variable"] == "intensity_demand", "source"]), {cj.SOURCE_EIA}, name)
            # and no other balancing authority carries the join's source
            self.assertEqual(set(b.loc[b["source"] == cj.SOURCE_JOIN, "entity"]), {cj.ENTITY}, name)
            with open(os.path.join(SCRATCH, name + ".csv"), encoding="utf-8") as f:
                head = "".join(ln for ln in f if ln.startswith("#"))
            self.assertIn(cj.JOIN, head, name)
            self.assertIn("docs/methods/eia930_caiso_break.md", head, name)

    def test_from_the_join_the_value_is_eia_co2_over_caisos_own_generation(self):
        eia, caiso = cj.eia_hours(), cj.caiso_hours()
        b = pd.read_csv(os.path.join(SCRATCH, "carbon_intensity_hourly.csv"), comment="#", dtype=str, keep_default_na=False)
        g = b[(b["entity"] == cj.ENTITY) & (b["variable"] == cj.VARIABLE) & (b["ts_utc"] >= cj.JOIN)].set_index("ts_utc")
        for ts in list(g.index[:3]) + list(g.index[-3:]) + list(g.index[len(g) // 2:len(g) // 2 + 3]):
            want = cj.r4(eia.loc[ts, "co2_emissions_generated"] * 1000 / caiso.loc[ts, cj.OWN].sum())
            self.assertEqual(float(g.loc[ts, "value"]), want, ts)
        self.assertTrue(set(g.index) <= set(caiso.index))  # every hour from the join is an hour CAISO holds

    def test_eias_gas_is_still_caisos_gas(self):
        ratio, n = cj.gas_ratio(cj.eia_hours(), cj.caiso_hours())
        self.assertGreater(n, 5000)
        self.assertLess(abs(ratio / cj.F_GAS - 1), cj.GAS_TOLERANCE)


class Page(unittest.TestCase):
    def test_the_sentence_no_longer_says_under_review_and_links_the_method(self):
        with open(os.path.join(ROOT, "site", "components", "CaisoBreakNote.tsx"), encoding="utf-8") as f:
            note = f.read()
        shown = note.split("export function CaisoBreakNote", 1)[1]
        self.assertNotIn("under review", shown)
        self.assertIn('href="/data/methods/eia930_caiso_break"', shown)
        self.assertIn("caisoJoinDay()", shown)
        for page, kind in (("app/network/page.tsx", "<CaisoBreakNote "), ("app/emissions/page.tsx", "<CaisoBreakNote />"),
                           ("app/cost-of-power/page.tsx", "<CaisoBreakNote />"), ("app/mix/page.tsx", '<CaisoBreakNote kind="mix" />'),
                           ("app/grid/page.tsx", '<CaisoBreakNote kind="mix" />'), ("app/grid/[iso]/page.tsx", '<CaisoBreakNote kind="both" />'),
                           ("app/reports/draft/ai-gigawatts/page.tsx", "<CaisoBreakNote />")):
            with open(os.path.join(ROOT, "site", *page.split("/")), encoding="utf-8") as f:
                self.assertIn(kind, f.read(), page)

    def test_no_em_dash_in_the_session_files(self):
        for rel in ("warehouse/derived/caiso_join.py", "warehouse/analysis/caiso_join_before_after.py",
                    "warehouse/analysis/caiso_solar_seller.py", "site/lib/caisoJoin.ts", "site/components/CaisoBreakNote.tsx",
                    "docs/methods/eia930_caiso_break.md", "tests/test_session78.py"):
            with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)


if __name__ == "__main__":
    unittest.main()
