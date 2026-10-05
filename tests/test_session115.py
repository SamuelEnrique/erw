"""Session 115: what Texas's storage resources were awarded day-ahead.

    python -m unittest tests.test_session115

On a saved real sample, never on rows made for the test:

- tests/fixtures/session115/ercot_dam_esr_awards_sample.csv.gz: the rows of ercot_dam_esr_awards for the operating
  days 6 and 8 December 2025 (12,672 rows, every resource), cut from the month the connector wrote. The day between
  them, the 7th, is left out on purpose: it is the missing day.
- tests/fixtures/session115/60d_DAM_ESR_Data-04-FEB-26_first400.csv: the first 400 rows of ERCOT's own file for the
  operating day 6 December 2025, every one of its columns, as it came in the zip.

The sums are computed again here with exact decimals, without the builder's code.
"""
import calendar
import datetime as dt
import gzip
import io
import os
import re
import sys
import tempfile
import unittest
import zipfile
from collections import defaultdict
from decimal import Decimal

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ercot_dam_esr as esr  # noqa: E402
import ercot_storage_dam_awards as awards  # noqa: E402
import iso_prices as ip  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session115")
SAMPLE = os.path.join(FIX, "ercot_dam_esr_awards_sample.csv.gz")
RAW = os.path.join(FIX, "60d_DAM_ESR_Data-04-FEB-26_first400.csv")
SERVICES = {"regup": (["x_regup_award_mw"], "x_regup_mcpc"), "regdn": (["x_regdn_award_mw"], "x_regdn_mcpc"),
            "rrs": (["x_rrspfr_award_mw", "x_rrsffr_award_mw", "x_rrsufr_award_mw"], "x_rrs_mcpc"),
            "ecrs": (["x_ecrs_award_mw"], "x_ecrs_mcpc"), "nspin": (["x_nonspin_award_mw"], "x_nonspin_mcpc")}


def sample():
    with gzip.open(SAMPLE, "rt", encoding="utf-8", newline="") as f:
        return pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[])


def D(x):
    return Decimal(x) if x != "" else Decimal(0)


def by_hand(df):
    """The month's sums from the rows, in exact decimals, by a path that shares nothing with the builder."""
    s = defaultdict(Decimal)
    hsl = {}
    awarded = set()
    for r in df.to_dict("records"):
        hsl[r["entity"]] = max(hsl.get(r["entity"], Decimal("-1e9")), Decimal(r["value"]))
        q = D(r["x_energy_award_mw"])
        if q > 0:
            s["energy_sold_usd"] += q * Decimal(r["x_energy_price_usd_per_mwh"])
            s["energy_sold_mwh"] += q
        elif q < 0:
            s["energy_bought_usd"] += -q * Decimal(r["x_energy_price_usd_per_mwh"])
            s["energy_bought_mwh"] += -q
        if q != 0:
            awarded.add(r["entity"])
        for name, (cols, price) in SERVICES.items():
            a = sum((D(r[c]) for c in cols), Decimal(0))
            if a != 0:
                s[f"revenue_{name}_usd"] += a * Decimal(r[price])
                awarded.add(r["entity"])
    s["revenue_energy_usd"] = s["energy_sold_usd"] - s["energy_bought_usd"]
    s["revenue_ancillary_usd"] = sum((s[f"revenue_{n}_usd"] for n in SERVICES), Decimal(0))
    s["revenue_total_usd"] = s["revenue_energy_usd"] + s["revenue_ancillary_usd"]
    return s, hsl, awarded


def build(df):
    res, days = awards.combine([awards.by_resource(df)])
    return awards.monthly(res, days)


class MonthlySums(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = sample()
        cls.months = build(cls.df)
        cls.hand, cls.hsl, cls.awarded = by_hand(cls.df)

    def test_the_sample_is_the_two_real_days(self):
        self.assertEqual(len(self.df), 12672)
        days = sorted(set(pd.to_datetime(self.df["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d")))
        self.assertEqual(days, ["2025-12-06", "2025-12-08"])
        self.assertEqual(set(self.df["source"]), {"ercot:NP3-966-ER"})
        self.assertEqual(list(self.months), ["2025-12"])

    def test_monthly_sums_equal_the_sum_of_the_rows(self):
        v = self.months["2025-12"]
        for name in ["energy_sold_usd", "energy_bought_usd", "energy_sold_mwh", "energy_bought_mwh", "revenue_energy_usd", "revenue_regup_usd", "revenue_regdn_usd",
                     "revenue_rrs_usd", "revenue_ecrs_usd", "revenue_nspin_usd", "revenue_ancillary_usd", "revenue_total_usd"]:
            self.assertGreater(abs(self.hand[name]), 0, name)  # the sample holds every stream: no sum is checked against nothing
            self.assertAlmostEqual(v[name], float(self.hand[name]), delta=0.011, msg=name)
        self.assertEqual(v["resource_hours"], len(self.df))
        self.assertEqual(v["resource_hours_energy_award"], int(sum(1 for x in self.df["x_energy_award_mw"] if D(x) != 0)))

    def test_per_mw_is_the_sum_over_the_mw_and_the_mw_is_each_resources_highest_limit(self):
        v = self.months["2025-12"]
        mw = float(sum(self.hsl.values()))
        self.assertAlmostEqual(v["mw"], mw, places=3)
        self.assertEqual(v["resources"], len(self.hsl))
        self.assertEqual(v["resources_with_award"], len(self.awarded))
        for r in awards.REVENUES:
            self.assertAlmostEqual(v[f"revenue_{r}_usd_per_mw"], float(self.hand[f"revenue_{r}_usd"]) / mw, delta=0.0002, msg=r)

    def test_a_resource_with_no_award_contributes_nothing_and_is_counted_in_the_mw(self):
        idle = sorted(e for e in self.hsl if e not in self.awarded and self.hsl[e] > 0)
        self.assertTrue(idle, "the sample holds no resource without an award")
        e = idle[0]
        without = build(self.df[self.df["entity"] != e])["2025-12"]
        v = self.months["2025-12"]
        for name in ["revenue_energy_usd", "revenue_ancillary_usd", "revenue_total_usd", "energy_sold_mwh", "energy_bought_mwh"]:
            self.assertEqual(v[name], without[name], name)  # it adds nothing to any sum
        self.assertAlmostEqual(v["mw"] - without["mw"], float(self.hsl[e]), places=3)  # and its limit is in the MW
        self.assertEqual(v["resources"] - without["resources"], 1)
        self.assertEqual(v["resources_with_award"], without["resources_with_award"])
        self.assertLess(v["revenue_total_usd_per_mw"], without["revenue_total_usd_per_mw"])

    def test_nothing_is_filled_for_a_missing_day(self):
        v = self.months["2025-12"]
        self.assertEqual((v["days_held"], v["days_missing"], v["days_in_month"]), (2, 1, 31))
        local = pd.to_datetime(self.df["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d")
        a, b = build(self.df[local == "2025-12-06"])["2025-12"], build(self.df[local == "2025-12-08"])["2025-12"]
        for name in ["energy_sold_usd", "energy_bought_usd", "revenue_regup_usd", "revenue_regdn_usd", "revenue_rrs_usd", "revenue_ecrs_usd", "revenue_nspin_usd"]:
            self.assertAlmostEqual(v[name], a[name] + b[name], delta=0.011, msg=name)  # two days' awards, not three
        self.assertEqual(v["resource_hours"], a["resource_hours"] + b["resource_hours"])
        self.assertEqual((a["days_held"], a["days_missing"]), (1, 0))  # one day alone: nothing between its first and last day
        rows = awards.rows_of(self.months, "2026-10-05T00:00:00Z")
        self.assertFalse((rows["value"] == "").any())
        self.assertFalse(rows["value"].str.contains("nan", case=False).any())

    def test_an_award_without_its_price_stops_the_build(self):
        df = self.df.copy()
        i = df.index[df["x_energy_award_mw"].map(lambda x: D(x) != 0)][0]
        df.loc[i, "x_energy_price_usd_per_mwh"] = ""
        with self.assertRaises(ValueError):
            awards.by_resource(df)
        df = self.df.copy()
        i = df.index[df["x_nonspin_award_mw"].map(lambda x: D(x) != 0)][0]
        df.loc[i, "x_nonspin_mcpc"] = ""
        with self.assertRaises(ValueError):
            awards.by_resource(df)

    def test_the_table_the_builder_writes_passes_the_validator(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "ercot_dam_esr_awards.csv")
            self.df.to_csv(src, index=False, lineterminator="\n")
            self.assertEqual(awards.main(["--out-dir", d, "--input", src]), 0)
            path = os.path.join(d, awards.NAME + ".csv")
            sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
            import erw_validate
            self.assertEqual(erw_validate.main([path]), 0)
            with open(path, encoding="utf-8") as f:
                head = [x for x in f if x.startswith("#")]
            text = "".join(head)
            self.assertIn("Derived from: ercot_dam_esr_awards", text)
            self.assertIn("License: public", text)
            self.assertIn("not what any battery earned", text)
            t = pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)
            self.assertEqual(set(t["entity"]), {"ercot:esr_fleet"})
            self.assertEqual(set(t["unit"]), {"count", "MW", "MWh", "USD", "USD/MW"})
            self.assertEqual(set(t["ts_utc"]), {"2025-12-01T00:00:00Z"})


class Connector(unittest.TestCase):
    def raw(self):
        with open(RAW, "rb") as f:
            return f.read()

    def zip_of(self, files):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            for name, content in files.items():
                z.writestr(name, content)
        return b.getvalue()

    def test_an_operating_day_is_the_day_published_less_60(self):
        self.assertEqual(esr.operating_day({"PublishDate": "2026-02-04T17:53:35-06:00"}), dt.date(2025, 12, 6))

    def test_ercots_file_becomes_rows_as_printed(self):
        name, df = esr.read_esr(self.zip_of({"60d_DAM_ESR_Data-04-FEB-26.csv": self.raw(), "60d_DAM_EnergyBids-04-FEB-26.csv": b"a\n1\n"}))
        self.assertEqual(name, "60d_DAM_ESR_Data-04-FEB-26.csv")
        self.assertEqual(len(df), 400)
        src = pd.read_csv(RAW, dtype=str, keep_default_na=False)
        rows = esr.to_rows(df, dt.date(2025, 12, 6), "https://example.org/zip", "2026-10-05T03:14:02Z", "2026-02-04T23:53:35Z")
        self.assertEqual(list(rows.columns), esr.COLS)
        self.assertEqual(len(rows), 400)
        self.assertFalse(any(c.startswith("x_qse_submitted") or "curve" in c for c in rows.columns))  # the offer curve is left out
        one = src.iloc[0]
        r = rows[(rows["entity"] == "ercot:" + one["Resource Name"]) & (rows["ts_utc"] == "2025-12-06T06:00:00Z")].iloc[0]  # hour ending 1, Central standard time
        self.assertEqual(one["Hour Ending"], "1")
        self.assertEqual(r["value"], one["HSL"])
        self.assertEqual(r["x_energy_award_mw"], one["Awarded Quantity"])
        self.assertEqual(r["x_energy_price_usd_per_mwh"], one["Energy Settlement Point Price"])
        self.assertEqual(r["node"], one["Settlement Point Name"])
        # a blank award in ERCOT's file is a blank in the table, never a zero
        self.assertEqual(int((rows["x_regup_award_mw"] == "").sum()), int((src["RegUp Awarded"].str.strip() == "").sum()))
        self.assertGreater(int((rows["x_regup_award_mw"] == "").sum()), 0)

    def test_a_file_of_another_day_or_a_zip_without_the_file_is_a_missing_day(self):
        _, df = esr.read_esr(self.zip_of({"60d_DAM_ESR_Data-04-FEB-26.csv": self.raw()}))
        with self.assertRaises(ValueError):
            esr.to_rows(df, dt.date(2025, 12, 7), "u", "r", "v")
        with self.assertRaises(ValueError):
            esr.read_esr(self.zip_of({"60d_DAM_Gen_Resource_Data-02-FEB-26.csv": b"a\n1\n"}))

    def test_a_repeated_hour_is_refused_not_guessed(self):
        _, df = esr.read_esr(self.zip_of({"60d_DAM_ESR_Data-04-FEB-26.csv": self.raw()}))
        twice = pd.concat([df, df.iloc[:1]], ignore_index=True)
        with self.assertRaises(ValueError):
            esr.to_rows(twice, dt.date(2025, 12, 6), "u", "r", "v")

    def _doc(self, content, published="2026-02-04T17:53:35-06:00"):
        return {"ConstructedName": "ext.test.zip", "DocID": "1", "ContentSize": str(len(content)), "PublishDate": published}

    def test_the_pull_stops_before_either_ceiling_and_never_asks_twice(self):
        content = self.zip_of({"60d_DAM_ESR_Data-04-FEB-26.csv": self.raw()})
        doc = self._doc(content)
        day = dt.date(2025, 12, 6)
        calls = []

        class Answer:
            status_code = 200

            def __init__(self, c):
                self.content = c

        def get(url, **kw):
            calls.append(url)
            return Answer(content)

        keep = (esr.RAW, esr.ZIPS, esr.MONTHS, esr.MANIFEST, esr.MAX_BYTES, esr.MAX_ROWS, esr.PAUSE, esr.requests.get)
        with tempfile.TemporaryDirectory() as d:
            try:
                esr.RAW, esr.ZIPS, esr.MONTHS = d, os.path.join(d, "zips"), os.path.join(d, "months")
                esr.MANIFEST = os.path.join(esr.ZIPS, "manifest.csv")
                esr.PAUSE = 0
                esr.requests.get = get
                log = lambda m: None  # noqa: E731
                # the download ceiling: the request is never made
                esr.MAX_BYTES = len(content) - 1
                with self.assertRaises(esr.Ceiling):
                    esr.get_zip(doc, day, log, False, {"bytes": 0, "requests": 0, "rows": 0})
                self.assertEqual(calls, [])
                # under it: asked once, saved, and read from the disk the second time
                esr.MAX_BYTES = 10 * len(content)
                state = {"bytes": 0, "requests": 0, "rows": 0}
                esr.get_zip(doc, day, log, False, state)
                esr.get_zip(doc, day, log, False, state)
                self.assertEqual(len(calls), 1)
                self.assertEqual(state["bytes"], len(content))
                self.assertEqual(esr.downloaded_bytes(), len(content))
                self.assertEqual([r["how"] for r in esr.manifest()], ["requested"])
                # the row ceiling: the month stops before the day that would pass it, and writes nothing
                esr.MAX_ROWS = 399
                with self.assertRaises(esr.Ceiling):
                    esr.do_month("2025-12", [day], {day: doc}, log, True, {"bytes": 0, "requests": 0, "rows": 0})
                self.assertFalse(os.path.exists(esr.month_paths("2025-12")[0]))
                # a day ERCOT lists no zip for is a missing day with its reason, and has no rows
                esr.MAX_ROWS = 9_000_000
                rec = esr.do_month("2025-12", [day, dt.date(2025, 12, 7)], {day: doc}, log, True, {"bytes": 0, "requests": 0, "rows": 0})
                self.assertEqual((len(rec["days_held"]), len(rec["days_missing"]), rec["rows"]), (1, 1, 400))
                self.assertEqual(rec["days_missing"][0]["day"], "2025-12-07")
                self.assertEqual(len(calls), 1)
            finally:
                esr.RAW, esr.ZIPS, esr.MONTHS, esr.MANIFEST, esr.MAX_BYTES, esr.MAX_ROWS, esr.PAUSE, esr.requests.get = keep

    def test_the_approved_ceilings_and_the_pause_rule(self):
        self.assertEqual((esr.MAX_ROWS, esr.MAX_BYTES), (9_000_000, 3_000_000_000))
        self.assertGreaterEqual(esr.PAUSE, 1)
        with open(os.path.join(ROOT, "warehouse", "connectors", "ercot_dam_esr.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('ip.paused("ercot")', src)
        self.assertIn("raw data provided in public", esr.TERMS_QUOTE)


class Records(unittest.TestCase):
    """Where the two tables are, and are not."""

    def text(self, *path):
        with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
            return f.read()

    def test_the_row_level_table_is_out_of_the_sites_database_and_the_monthly_one_is_held(self):
        import yaml
        live = yaml.safe_load(self.text("warehouse", "supabase", "live_set.yaml"))
        rules = list(live["full"]) + list((live.get("recent") or {}).get("tables") or [])
        self.assertFalse([r for r in rules if re.match(r, "ercot_dam_esr_awards")], "a live-set rule loads the row-level table")
        self.assertIn("ercot_dam_esr_awards", live["catalogue_hold"])
        self.assertTrue([r for r in live["full"] if re.match(r, "ercot_storage_dam_awards_monthly")])
        self.assertIn("ercot_storage_dam_awards_monthly", live["review_hold"])
        for s in ["ercot:NP3-966-ER", "erw:ercot_storage_dam_awards"]:
            self.assertIn(s, live["sources_hold"])

    def test_the_method_and_the_standard_say_what_it_is_not(self):
        m = " ".join(self.text("docs", "methods", "ercot_storage_dam_awards.md").lower().split())
        for phrase in ["day-ahead awards only", "no real-time settlement", "not what any battery earned", "raw data provided in public portions"]:
            self.assertIn(phrase, m)
        self.assertIn("ercot_storage_dam_awards_monthly", self.text("docs", "datastandard.md"))

    def test_no_em_dash_in_this_sessions_files(self):
        for p in [("warehouse", "connectors", "ercot_dam_esr.py"), ("warehouse", "derived", "ercot_storage_dam_awards.py"),
                  ("docs", "methods", "ercot_storage_dam_awards.md"), ("tests", "test_session115.py")]:
            self.assertNotIn(chr(0x2014), self.text(*p), p)

    def test_the_table_on_this_machine_adds_up(self):
        path = os.path.join(ROOT, "warehouse", "output", awards.NAME + ".csv")
        if not os.path.exists(path):
            self.skipTest("the table is not on this machine")
        t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        w = t.pivot(index="ts_utc", columns="variable", values="value").astype(float)
        for ts, r in w.iterrows():
            self.assertAlmostEqual(r["revenue_total_usd"], r["revenue_energy_usd"] + r["revenue_ancillary_usd"], delta=0.02)
            self.assertAlmostEqual(r["revenue_energy_usd"], r["energy_sold_usd"] - r["energy_bought_usd"], delta=0.02)
            self.assertAlmostEqual(r["revenue_total_usd_per_mw"], r["revenue_total_usd"] / r["mw"], delta=0.001)
            self.assertLessEqual(r["days_held"] + r["days_missing"], r["days_in_month"])
            self.assertEqual(r["days_in_month"], calendar.monthrange(int(ts[:4]), int(ts[5:7]))[1])
            self.assertLessEqual(r["resources_with_award"], r["resources"])


if __name__ == "__main__":
    unittest.main()
