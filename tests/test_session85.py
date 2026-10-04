"""Session 85: day-ahead reserve prices of four more grids (nyiso_as_prices, isone_as_prices, miso_as_prices,
spp_as_prices), their shared loop (iso_as_common), and the hold that keeps a new public table out of the live catalogue.

Energy Research Warehouse (ERW). No request leaves the machine: every file read here is made in the test, with made-up
prices, only to exercise the reading. The tables themselves are tested where the machine holds them.

    python -m unittest tests.test_session85 -v
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/supabase"):
    sys.path.insert(0, os.path.join(ROOT, p))

import iso_as_common as common  # noqa: E402
import iso_prices as ip  # noqa: E402
import isone_as_prices as isone  # noqa: E402
import miso_as_prices as miso  # noqa: E402
import nyiso_as_prices as nyiso  # noqa: E402
import spp_as_prices as spp  # noqa: E402

LOG = lambda *_: None  # noqa: E731
SPECS = {"nyiso": nyiso.SPEC, "isone": isone.SPEC, "miso": miso.SPEC, "spp": spp.SPEC}


def utc(s):
    return pd.Timestamp(s, tz="UTC")


def nyiso_day(day, change=None, tz=None):
    """A made-up NYISO file for one day: every zone, every hour; change(zone, hour, column) may alter a cell."""
    d = pd.Timestamp(day)
    lines = [",".join(nyiso.COLS)]
    for h, start in enumerate(common.day_hours(day, nyiso.TZ)):
        local = start.tz_convert(nyiso.TZ)
        for z in nyiso.ZONES:
            vals = [1.0 + h, 2.0 + h, 3.0 + h, 4.0 + h]
            if change:
                vals = [change(z, h, k, v) for k, v in enumerate(vals)]
            lines.append(",".join([f"{d:%m/%d/%Y} {local.hour:02d}:00", "EDT" if local.utcoffset().total_seconds() == -14400 else "EST",
                                   z, "1"] + ["" if v is None else f"{v:.2f}" for v in vals]))
    return "\n".join(lines) + "\n"


class CompleteDays(unittest.TestCase):
    def rows(self, day, tz, drop=0, region="A", variable="v"):
        hours = common.day_hours(day, tz)[drop:]
        return pd.DataFrame({"region": region, "variable": variable, "ts": hours, "value": 1.0, "day": day})

    def test_a_day_has_23_24_or_25_hours(self):
        self.assertEqual([common.hours_in(d, "America/New_York") for d in ("2025-03-09", "2025-06-01", "2025-11-02")], [23, 24, 25])
        self.assertEqual(common.hours_in("2025-11-02", "Etc/GMT+5"), 24)          # MISO's file does not change clocks

    def test_a_whole_day_is_kept_and_a_short_one_is_left_out_and_named(self):
        tz = "America/Chicago"
        rows = pd.concat([self.rows("2025-06-01", tz), self.rows("2025-06-02", tz, drop=1), self.rows("2025-11-02", tz)])
        kept, gaps = common.complete(rows, {"A": ["v"]}, tz, LOG)
        self.assertEqual(sorted(set(kept["day"])), ["2025-06-01", "2025-11-02"])
        self.assertEqual(len(kept), 24 + 25)
        self.assertEqual(gaps, ["A v 2025-06-02: 23 of 24 hours"])

    def test_a_product_missing_from_a_day_is_a_gap_and_a_region_not_yet_in_the_file_is_not(self):
        tz = "America/Chicago"
        rows = self.rows("2025-06-01", tz)
        kept, gaps = common.complete(rows, {"A": ["v", "w"], "B": ["v"]}, tz, LOG)
        self.assertEqual(len(kept), 24)
        self.assertEqual(gaps, ["A w 2025-06-01: 0 of 24 hours"])

    def test_a_repeated_hour_stops_the_run(self):
        rows = pd.concat([self.rows("2025-06-01", "America/Chicago")] * 2)
        with self.assertRaises(RuntimeError):
            common.complete(rows, {"A": ["v"]}, "America/Chicago", LOG)


class Nyiso(unittest.TestCase):
    def setUp(self):
        nyiso.differing.update(hours=0, files=0)

    def test_five_zones_three_reserves_and_one_regulation_price(self):
        r = nyiso.parse_day(nyiso_day("2025-06-01"), "2025-06-01", LOG)
        self.assertEqual(sorted(set(r["region"])), ["CAPITL", "HUD VL", "LONGIL", "N.Y.C.", "NYCA", "WEST"])
        self.assertEqual(len(r), 24 * (5 * 3 + 1))
        self.assertEqual(set(r[r["region"] == "NYCA"]["variable"]), {"as_price_dam_reg"})
        first = r[(r["region"] == "WEST") & (r["variable"] == "as_price_dam_spin10")].sort_values("ts").iloc[0]
        self.assertEqual((first["ts"], first["value"]), (utc("2025-06-01T04:00:00Z"), 1.0))   # midnight EDT
        self.assertEqual(nyiso.differing, {"hours": 0, "files": 1})

    def test_the_day_the_clocks_go_back_has_25_hours_each_once(self):
        r = nyiso.parse_day(nyiso_day("2025-11-02"), "2025-11-02", LOG)
        s = r[(r["region"] == "N.Y.C.") & (r["variable"] == "as_price_dam_op30")]
        self.assertEqual(len(s), 25)
        self.assertFalse(s["ts"].duplicated().any())
        kept, gaps = common.complete(r, nyiso.WANTED, nyiso.TZ, LOG)
        self.assertEqual((len(kept), gaps), (len(r), []))

    def test_a_zone_not_kept_that_differs_is_counted_not_hidden(self):
        text = nyiso_day("2025-06-01", change=lambda z, h, k, v: v + 5 if (z, h, k) == ("GENESE", 3, 0) else v)
        nyiso.parse_day(text, "2025-06-01", LOG)
        self.assertEqual(nyiso.differing["hours"], 1)

    def test_regulation_must_be_one_price_and_an_empty_cell_is_no_row(self):
        with self.assertRaises(RuntimeError):
            nyiso.parse_day(nyiso_day("2025-06-01", change=lambda z, h, k, v: v + 1 if (z, k) == ("NORTH", 3) else v), "2025-06-01", LOG)
        r = nyiso.parse_day(nyiso_day("2025-06-01", change=lambda z, h, k, v: None if (h, k) == (5, 1) else v), "2025-06-01", LOG)
        kept, gaps = common.complete(r, nyiso.WANTED, nyiso.TZ, LOG)
        self.assertEqual(len(gaps), 5)                                             # the five kept zones lose that product's day
        self.assertTrue(all("as_price_dam_nsync10" in g and "23 of 24" in g for g in gaps))
        self.assertFalse((kept["variable"] == "as_price_dam_nsync10").any())       # left out whole, never filled

    def test_a_changed_layout_or_a_file_of_another_day_stops_the_read(self):
        with self.assertRaises(RuntimeError):
            nyiso.parse_day(nyiso_day("2025-06-01").replace("PTID", "Ptid"), "2025-06-01", LOG)
        with self.assertRaises(RuntimeError):
            nyiso.parse_day(nyiso_day("2025-06-01"), "2025-06-02", LOG)

    def test_a_month_is_its_daily_files(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for d in ("2025-06-01", "2025-06-02"):
                z.writestr(d.replace("-", "") + "damasp.csv", nyiso_day(d))
        r = nyiso.parse(buf.getvalue(), {"label": "2025-06"}, LOG)
        self.assertEqual(sorted(set(r["day"])), ["2025-06-01", "2025-06-02"])


def isone_file(days, hours=None, total=None, location="7000"):
    lines = ['"C","made up"', ",".join(f'"{c}"' for c in isone.COLS), '"H","Date","Number"']
    n = 0
    for day in days:
        d = pd.Timestamp(day)
        for k, he in enumerate(hours or [lab for lab, _ in isone.labels(day)]):
            lines.append(f'"D","{d:%m/%d/%Y}",{he},{location},1,2,3,4,{10 + k}.5,{9 + k}.25,{8 + k}.0,0.00,5,6,7,8')
            n += 1
    lines.append(f'"T","{n if total is None else total} lines"')
    return ("\n".join(lines) + "\n").encode()


class Isone(unittest.TestCase):
    def test_four_prices_an_hour_from_the_hour_ending(self):
        r = isone.parse(isone_file(["2025-06-01"]), {"label": "2025-06"}, LOG)
        self.assertEqual(len(r), 24 * 4)
        s = r[r["variable"] == "as_price_dam_tmsr"].sort_values("ts")
        self.assertEqual((s["ts"].iloc[0], s["value"].iloc[0]), (utc("2025-06-01T04:00:00Z"), 10.5))  # hour ending 01, EDT
        self.assertEqual(set(r["region"]), {"7000"})
        self.assertEqual(set(r["variable"]), set(isone.PRICES.values()))

    def test_the_repeated_hour_and_the_missing_hour(self):
        self.assertEqual([lab for lab, _ in isone.labels("2025-11-02")][:4], ["01", "02", "02", "03"])
        self.assertNotIn("03", [lab for lab, _ in isone.labels("2026-03-08")])
        for day, n in (("2025-11-02", 25), ("2026-03-08", 23)):
            r = isone.parse(isone_file([day]), {"label": day}, LOG)
            kept, gaps = common.complete(r, isone.WANTED, isone.TZ, LOG)
            self.assertEqual((len(kept), gaps), (n * 4, []))
            self.assertFalse(kept.duplicated(["variable", "ts"]).any())

    def test_a_day_whose_hours_are_not_the_days_hours_is_left_out(self):
        hours = [f"{h:02d}" for h in range(1, 24)]                                 # an ordinary day one hour short
        r = isone.parse(isone_file(["2025-06-01"], hours=hours), {"label": "x"}, LOG)
        kept, gaps = common.complete(r, isone.WANTED, isone.TZ, LOG)
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(gaps), 4)

    def test_the_files_own_count_another_location_or_another_layout_stop_the_read(self):
        with self.assertRaises(RuntimeError):
            isone.parse(isone_file(["2025-06-01"], total=23), {"label": "x"}, LOG)
        with self.assertRaises(RuntimeError):
            isone.parse(isone_file(["2025-06-01"], location="7001"), {"label": "x"}, LOG)
        with self.assertRaises(RuntimeError):
            isone.parse(isone_file(["2025-06-01"]).replace(b"FER Price", b"EIR Price"), {"label": "x"}, LOG)

    def test_the_window_starts_when_the_market_did(self):
        self.assertEqual(isone.FIRST, "2025-03-01")
        docs = isone.documents(pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-11"), LOG, True)
        self.assertEqual([d["label"] for d in docs], ["2025-03", "2025-04"])
        self.assertTrue(docs[1]["url"].endswith("start=20250401&end=20250410"))


def miso_file(day, zone_change=None, empty=None):
    d = pd.Timestamp(day)
    lines = ["Dayahead Market MCPs.", "", f"{d:%m/%d/%Y},,All Hours-Ending are Eastern Standard Time (EST)", "",
             ",,MCP Type, " + ",".join(miso.HOURS)]
    base = {"REG": 10.0, "SPIN": 2.0, "SUPP": 0.5}

    def vals(kind, shift=0.0, blank=None):
        return ",".join("" if blank == h else f"{base[kind] + h + shift:g}" for h in range(24))
    for t in ("DEMREGMCP", "GENREGMCP", "DEMSPINMCP", "GENSPINMCP", "DEMSUPPMCP", "GENSUPPMCP", "SERREGMCP"):
        kind = "REG" if "REG" in t else "SPIN" if "SPIN" in t else "SUPP"
        lines.append(f"MISO Wide,-,{t}," + vals(kind, blank=empty if t == "GENSPINMCP" else None))
    for unit, zone in (("MADE.UP1", "Zone 1"), ("MADE.UP2", "Zone 4")):
        for t in ("GENREGMCP", "GENSPINMCP", "GENSUPPMCP"):
            kind = "REG" if "REG" in t else "SPIN" if "SPIN" in t else "SUPP"
            lines.append(f"{unit},{zone},{t}," + vals(kind, shift=1.0 if zone_change == (zone, t) else 0.0))
    return ("\n".join(lines) + "\n").encode()


class Miso(unittest.TestCase):
    def setUp(self):
        miso.differing.update(cells=0, files=0)

    def test_three_system_prices_in_eastern_standard_time_all_year(self):
        for day in ("2025-07-01", "2025-01-15", "2025-11-02"):
            r = miso.parse(miso_file(day), {"day": day}, LOG)
            self.assertEqual(len(r), 24 * 3)
            s = r[r["variable"] == "as_price_dam_reg"].sort_values("ts")
            self.assertEqual((s["ts"].iloc[0], s["value"].iloc[0]), (utc(day + "T05:00:00Z"), 10.0))   # hour ending 1 EST
            kept, gaps = common.complete(r, miso.WANTED, miso.TZ, LOG)
            self.assertEqual((len(kept), gaps), (72, []))
        self.assertEqual(set(r["region"]), {"MISO Wide"})
        self.assertEqual(miso.differing["cells"], 0)

    def test_a_zone_priced_apart_is_counted(self):
        miso.parse(miso_file("2025-07-01", zone_change=("Zone 4", "GENSPINMCP")), {"day": "2025-07-01"}, LOG)
        self.assertEqual(miso.differing["cells"], 24)

    def test_an_empty_cell_leaves_the_products_day_out(self):
        r = miso.parse(miso_file("2025-07-01", empty=7), {"day": "2025-07-01"}, LOG)
        kept, gaps = common.complete(r, miso.WANTED, miso.TZ, LOG)
        self.assertEqual(gaps, ["MISO Wide as_price_dam_spin 2025-07-01: 23 of 24 hours"])
        self.assertEqual(len(kept), 48)

    def test_another_day_another_clock_or_another_layout_stops_the_read(self):
        with self.assertRaises(RuntimeError):
            miso.parse(miso_file("2025-07-01"), {"day": "2025-07-02"}, LOG)
        with self.assertRaises(RuntimeError):
            miso.parse(miso_file("2025-07-01").replace(b"Eastern Standard Time (EST)", b"Eastern Prevailing Time"), {"day": "2025-07-01"}, LOG)
        with self.assertRaises(RuntimeError):
            miso.parse(miso_file("2025-07-01").replace(b"MISO Wide,-,SERREGMCP", b"MISO Wide,-,NEWTYPE"), {"day": "2025-07-01"}, LOG)


def spp_file(day, zones=("1", "2", "SPP"), change=None):
    lines = [",".join(spp.COLS)]
    for h, start in enumerate(common.day_hours(day, spp.TZ)):
        end = start + pd.Timedelta(hours=1)
        local = end.tz_convert(spp.TZ)
        for z in zones:
            base = 20.0 if z in ("21", "SWPW") else 3.0
            vals = [base + h + k for k in range(7)]
            if change == z:
                vals[2] += 9
            lines.append(f"{local:%m/%d/%Y %H:%M:%S},{end:%m/%d/%Y %H:%M:%S},{z}," + ",".join(f"{v:.4f}" for v in vals))
    return "\n".join(lines) + "\n"


class Spp(unittest.TestCase):
    def setUp(self):
        spp.differing.update(cells=0, files=0)

    def test_the_named_rows_seven_products_from_the_hours_end(self):
        r = spp.parse_day(spp_file("2025-06-01"), "2025-06-01", LOG)
        self.assertEqual(set(r["region"]), {"SPP"})
        self.assertEqual(len(r), 24 * 7)
        s = r[r["variable"] == "as_price_dam_regup"].sort_values("ts")
        self.assertEqual((s["ts"].iloc[0], s["value"].iloc[0]), (utc("2025-06-01T05:00:00Z"), 3.0))  # midnight Central, daylight time
        self.assertEqual(spp.differing["cells"], 0)

    def test_the_second_named_row_is_kept_from_the_day_it_appears(self):
        a = spp.parse_day(spp_file("2026-03-31"), "2026-03-31", LOG)
        b = spp.parse_day(spp_file("2026-04-01", zones=("1", "21", "SPP", "SWPW")), "2026-04-01", LOG)
        kept, gaps = common.complete(pd.concat([a, b]), spp.WANTED, spp.TZ, LOG)
        self.assertEqual(gaps, [])                                                 # SWPW absent before April is not a gap
        self.assertEqual(sorted(set(kept[kept["day"] == "2026-04-01"]["region"])), ["SPP", "SWPW"])
        self.assertEqual(spp.differing["cells"], 0)                                # zone 21 carries SWPW's price, zone 1 SPP's

    def test_a_numbered_zone_with_a_price_of_its_own_is_counted(self):
        spp.parse_day(spp_file("2025-06-01", change="2"), "2025-06-01", LOG)
        self.assertEqual(spp.differing["cells"], 24)

    def test_the_clock_changes_and_a_changed_layout(self):
        for day, n in (("2025-03-09", 23), ("2025-11-02", 25)):
            r = spp.parse_day(spp_file(day), day, LOG)
            kept, gaps = common.complete(r, spp.WANTED, spp.TZ, LOG)
            self.assertEqual((len(kept), gaps), (n * 7, []))
        with self.assertRaises(RuntimeError):
            spp.parse_day(spp_file("2025-06-01").replace("UncUP", "UncDN"), "2025-06-01", LOG)
        with self.assertRaises(RuntimeError):
            spp.parse_day(spp_file("2025-06-01", zones=("1", "2")), "2025-06-01", LOG)   # no row named SPP

    def test_an_archived_year_is_one_zip_and_a_missing_day_is_not_invented(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("2024/09/DA-MCP-202409010100.csv", spp_file("2024-09-01"))
        r = spp.parse(buf.getvalue(), {"year": 2024, "label": "2024", "days": ["2024-09-01", "2024-09-02"]}, LOG)
        self.assertEqual(sorted(set(r["day"])), ["2024-09-01"])


class Licenses(unittest.TestCase):
    def test_each_grid_states_its_license_with_the_terms_quoted(self):
        self.assertEqual({k: s["license"] for k, s in SPECS.items()},
                         {"nyiso": "public", "isone": "internal", "miso": "internal", "spp": "public"})
        quotes = {
            "nyiso": "does not confer any",
            "isone": "Any duplication of the Content or non-personal use may violate copyright",
            "miso": "You are not permitted to modify, publish, transmit",
            "spp": "Permission is implicitly granted to copy and distribute",
        }
        mods = {"nyiso": nyiso, "isone": isone, "miso": miso, "spp": spp}
        for k, q in quotes.items():
            doc = " ".join(mods[k].__doc__.split())
            self.assertIn(" ".join(q.split()), doc, k)
            self.assertIn("https://", SPECS[k]["license_line"])
            self.assertTrue(SPECS[k]["license_line"].startswith(f"License: {SPECS[k]['license']}"))
        self.assertIn("automated means", " ".join(miso.__doc__.split()))          # the sentence a person has to rule on
        self.assertIn("commercial", " ".join(spp.__doc__.split()))

    def test_not_pjm_and_the_window_and_ceiling_are_the_sessions(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", "pjm_as_prices.py")))
        self.assertEqual((common.START, common.CEILING), ("2024-09-01", 500_000))
        for s in SPECS.values():
            self.assertGreaterEqual(s["first"], common.START)


class Run(unittest.TestCase):
    """The loop end to end on a made-up source, in a scratch directory: nothing in warehouse/output."""

    def spec(self, days):
        def documents(start, until, log, offline):
            return [dict(url=f"https://made.up/{d}", label=d, day=d, settled=True) for d in days]

        def fetch(doc, log, offline):
            return miso_file(doc["day"]), {"url": doc["url"], "retrieved_at": "2026-10-04T00:00:00Z", "cached": True}
        # a made-up namespace: MISO itself is paused since session 89 and its connector makes no request and writes nothing
        return dict(miso.SPEC, name="madeup_as_prices", connector="madeup_as_prices", namespace="madeup", documents=documents, fetch=fetch)

    def run_in(self, tmp, spec, argv):
        keep = (ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return common.run(spec, ["--out-dir", tmp] + argv)
        finally:
            ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = keep

    def test_a_table_is_written_with_its_license_and_nothing_past_the_ceiling(self):
        days = ["2025-07-01", "2025-07-02"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_in(tmp, self.spec(days), ["--start", days[0], "--until", "2025-07-03"]), 0)
            path = os.path.join(tmp, "madeup_as_prices.csv")
            with open(path, encoding="utf-8") as f:
                head = [ln for ln in f if ln.startswith("#")]
            t = pd.read_csv(path, comment="#")
            self.assertEqual(len(t), 2 * 24 * 3)
            self.assertEqual(set(t["unit"]), {"USD/MW-hour"})
            self.assertTrue(any(h.startswith("# License: internal") for h in head))
            reg = pd.read_csv(os.path.join(tmp, "metadata", "sources.csv"))
            self.assertEqual(list(reg["license"]), ["internal"])
        old = common.CEILING
        try:
            common.CEILING = 100
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(self.run_in(tmp, self.spec(days), ["--start", days[0], "--until", "2025-07-03"]), 1)
                self.assertFalse(os.path.exists(os.path.join(tmp, "madeup_as_prices.csv")))   # no file, not a cut one
        finally:
            common.CEILING = old

    def test_the_window_cannot_start_before_the_approved_day(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            self.run_in(tmp, self.spec([]), ["--start", "2024-08-31"])


class Hold(unittest.TestCase):
    """A public table named in live_set.yaml's catalogue_hold stays out of the live catalogue and the live set, so the
    home page's count of public tables and rows does not move while the live site is frozen for its reviewer."""

    def test_held_tables_leave_the_catalogue_and_the_plan(self):
        import load
        cov = pd.DataFrame({"table": ["a", "b", "c"], "license": ["public", "public", "internal"]})
        plan = [("a", "full", None), ("b", "full", None)]
        c, p, held = load.hold(cov, plan, ["b", "zzz"])
        self.assertEqual((list(c["table"]), p, held), (["a", "c"], [("a", "full", None)], ["b"]))
        c, p, held = load.hold(cov, plan, [])
        self.assertEqual((len(c), p, held), (3, plan, []))

    def test_the_new_public_tables_are_held_and_the_internal_ones_need_no_hold(self):
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        held = set(live.get("catalogue_hold") or [])
        self.assertLessEqual({"nyiso_as_prices", "spp_as_prices"}, held)
        import load
        for t in held | {"isone_as_prices", "miso_as_prices"}:
            self.assertIsNone(load.live_rule(t), t)                                # none of them is in the live set


class Tables(unittest.TestCase):
    """The four tables, where the machine holds them."""

    def test_under_the_ceiling_whole_days_and_the_stated_license(self):
        seen = 0
        for k, s in SPECS.items():
            path = os.path.join(ROOT, "warehouse", "output", s["name"] + ".csv")
            if not os.path.exists(path):
                continue
            seen += 1
            with open(path, encoding="utf-8") as f:
                head = [ln for ln in f if ln.startswith("#")]
            t = pd.read_csv(path, comment="#", dtype={"value": float}, keep_default_na=False)
            self.assertLessEqual(len(t), common.CEILING, k)
            self.assertTrue(any(h.startswith(f"# License: {s['license']}") for h in head), k)
            self.assertGreaterEqual(t["ts_utc"].min(), "2024-09-01T04:00:00Z", k)
            self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any(), k)
            ts = pd.to_datetime(t["ts_utc"], utc=True).dt.tz_convert(s["tz"])
            per_day = t.assign(day=ts.dt.strftime("%Y-%m-%d")).groupby(["entity", "variable", "day"]).size()
            want = {d: common.hours_in(d, s["tz"]) for d in per_day.index.get_level_values("day").unique()}
            self.assertTrue(all(n == want[d] for (_, _, d), n in per_day.items()), k)   # no (region, product, day) is short
            self.assertEqual(set(t["unit"]), {"USD/MW-hour"}, k)
        if not seen:
            self.skipTest("none of the four tables is on this machine")


if __name__ == "__main__":
    unittest.main()
