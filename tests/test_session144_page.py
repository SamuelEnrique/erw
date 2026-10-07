"""Session 144, the page half: the one curtailment page (/curtailment) and the file behind its Texas section.

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written under warehouse/output
or site/data.

    ErcotPage      warehouse/derived/ercot_estimate_page.py on the saved real sample of ERCOT's own files
                   (tests/fixtures/session144/ercot/: two postings each of NP4-742-CD and NP4-745-CD, and six days of
                   the 2025 yearly workbook): the month's sums equal the days' sums, a share never passes 100, a month
                   under 95 percent of its hours carries a reason and no figure, a region has output and no limit
    TheSiteFiles   the files the page reads, as committed: every CAISO month has a share, nothing reads
                   "not computable", a negative-price hour is in the count under USD 5 once
    ThePage        the page's rules, read from its source: one address, the redirect, in review, the face holds no
                   method words and no em dash, every chart is the site's chart library with a tooltip, the
                   placeholders, the Method note holds what the two old pages said
On the built site: node site/scripts/check-curtailment.mjs <base> (run here when ERW_SITE_URL names a served site).

    python -m unittest tests.test_session144_page
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import ercot_wind_solar_history as c  # noqa: E402
import ercot_estimate_page as ep  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session144", "ercot")
POSTINGS = (("14787_cdr.00014787.0000000000000000.20260930.005513154.WPPHRLYAVGACTGEONP4742_csv.zip", "wind"),
            ("14787_cdr.00014787.0000000000000000.20260930.235512549.WPPHRLYAVGACTGEONP4742_csv.zip", "wind"),
            ("21809_cdr.00021809.0000000000000000.20260930.005512599.PVGRHRLYAVGACTGEONP4745_csv.zip", "solar"),
            ("21809_cdr.00021809.0000000000000000.20260930.235512454.PVGRHRLYAVGACTGEONP4745_csv.zip", "solar"))
WORKBOOK = "ERCOT_2025_Hourly_WindSolar_Output_sample.xlsx"
FACE_FILES = (("site", "app", "curtailment", "page.tsx"), ("site", "app", "curtailment", "Sections.tsx"), ("site", "app", "curtailment", "Charts.tsx"))
# words of method or limitation: none of them belongs on the page's face (they are in docs/methods/curtailment.md)
METHOD_WORDS = re.compile(r"upper bound|cannot see|limitation|caveat|does not say|does not locate|How it is computed|is computed|assum|methodology|not computable|"
                          r"never scaled|is not credited|round-trip|as if the two", re.I)
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def body(name):
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def site_file(name):
    return json.loads(src("site", "data", "curtailment", name))


def hourly_table():
    """The four sample postings as the hourly table's rows, the newest posting winning, as the connector builds them."""
    best = {}
    for name, fuel in POSTINGS:
        d, _ = c.parse_posting(body(name), fuel)
        for ts, entity, variable, value in d.itertuples(index=False):
            best[(entity, variable, ts)] = value
    rows = pd.DataFrame([(ts, e, v, x, "https://www.ercot.com/x", "2026-10-07T09:32:00Z") for (e, v, ts), x in best.items()],
                        columns=["ts", "entity", "variable", "value", "url", "retrieved"])
    return c.series(rows, c.SRC_REGION, c.region_of)


def output_table():
    """The six days of the 2025 workbook's sample as the output table's rows."""
    rows, _ = c.workbook_rows(body(WORKBOOK))
    rows["url"], rows["retrieved"] = "https://www.ercot.com/y", "2026-10-07T09:32:00Z"
    return c.series(rows, c.SRC_WORKBOOK)


class ErcotPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hourly, cls.output = hourly_table(), output_table()
        cls.e = ep.build(cls.hourly, cls.output)

    def test_the_days_of_the_sample(self):
        e = self.e
        self.assertEqual(sorted(e["days"]), ["2026-09-28", "2026-09-29", "2026-09-30"])
        self.assertEqual([e["days"][d]["whole"] for d in sorted(e["days"])], [True, True, False])       # the last day stops at 23:00
        self.assertEqual((e["days"]["2026-09-30"]["hours_held"], e["days"]["2026-09-30"]["hours_in_day"]), (23, 24))
        self.assertEqual((e["whole_days"], e["first_day"], e["last_day"], e["hours_held"]), (2, "2026-09-28", "2026-09-29", 71))
        self.assertEqual(len(e["hours"]), 71)
        self.assertEqual(e["hours"][0], {"ts": "2026-09-28T05:00:00Z", "local": "2026-09-28 00:00", "wind_gen": 9499.69, "wind_hsl": 9945.47,
                                         "solar_gen": e["hours"][0]["solar_gen"], "solar_hsl": e["hours"][0]["solar_hsl"]})     # ERCOT's own first hour

    def test_a_day_is_the_hours_added_by_hand(self):
        w = c.wide(self.hourly)
        g = w[(w["entity"] == "ercot:system") & (w["fuel"] == "wind") & (w["ts"] >= "2026-09-29T05:00:00Z") & (w["ts"] < "2026-09-30T05:00:00Z")]
        self.assertEqual(len(g), 24)
        by_hand = sum(max(0.0, h - x) for x, h in zip(g["gen"], g["hsl"]))
        self.assertAlmostEqual(self.e["days"]["2026-09-29"]["wind"]["below_hsl_mwh"], by_hand, delta=0.06)
        self.assertAlmostEqual(self.e["days"]["2026-09-29"]["wind"]["hsl_mwh"], float(g["hsl"].sum()), delta=0.06)

    def test_the_monthly_sums_equal_the_daily_sums(self):
        with mock.patch.object(ep, "NEAR_HOURS", 0.05):       # the rule lowered so that the sample's month is written
            e = ep.build(self.hourly, self.output)
        m = e["months"]["2026-09"]
        self.assertNotIn("missing", m)
        self.assertEqual(m["hours_held"], sum(d["hours_held"] for d in e["days"].values()))
        for fuel in ("wind", "solar"):
            for k in ("generation_mwh", "hsl_mwh", "below_hsl_mwh"):
                self.assertAlmostEqual(m[fuel][k], sum(d[fuel][k] for d in e["days"].values()), delta=0.2, msg=(fuel, k))       # each day is rounded to 0.1
        self.assertAlmostEqual(m["both"]["below_hsl_mwh"], m["wind"]["below_hsl_mwh"] + m["solar"]["below_hsl_mwh"], delta=0.11)
        # and the window is the whole days' sum, the all-hours figure every day's
        for fuel in ("wind", "solar"):
            self.assertAlmostEqual(e["window"][fuel]["below_hsl_mwh"], sum(d[fuel]["below_hsl_mwh"] for d in e["days"].values() if d["whole"]), delta=0.2)
            self.assertAlmostEqual(e["all_hours"][fuel]["below_hsl_mwh"], sum(d[fuel]["below_hsl_mwh"] for d in e["days"].values()), delta=0.2)
        self.assertAlmostEqual(sum(r["wind_below_mwh"] for r in e["by_hour_of_day"]), e["window"]["wind"]["below_hsl_mwh"], delta=1.3)        # 24 hours, each rounded to 0.1
        self.assertTrue(all(r["hours"] == 2 for r in e["by_hour_of_day"]))                                                                    # two whole days

    def test_a_month_under_95_percent_has_a_reason_and_no_figure(self):
        m = self.e["months"]["2026-09"]
        self.assertEqual((m["hours_held"], m["hours_in_month"]), (71, 720))
        self.assertTrue(m["missing"].startswith("71 of the month's 720 hours are held, under 95%"))
        self.assertEqual(set(m), {"hours_held", "hours_in_month", "missing"})

    def test_a_share_never_exceeds_100(self):
        e = self.e
        shares = [x[k]["share_pct"] for x in [*e["days"].values(), e["window"], e["all_hours"]] for k in ("wind", "solar", "both")]
        self.assertTrue(all(s is None or 0 <= s <= 100 for s in shares), shares)
        self.assertEqual(len([s for s in shares if s is not None]), len(shares))
        self.assertIsNone(ep.share(5.0, 0.0))            # no limit to divide by
        self.assertIsNone(ep.share(6.0, 5.0))            # above 100: left out, never clipped
        self.assertEqual(ep.share(1.0, 4.0), 25.0)

    def test_above_the_limit_is_kept_apart_and_nets_nothing(self):
        w = c.wide(self.hourly)
        g = w[(w["entity"] == "ercot:system") & (w["fuel"] == "solar") & (w["ts"] < "2026-09-30T05:00:00Z")]
        above = float((g["gen"] - g["hsl"]).clip(lower=0).sum())
        self.assertGreater(above, 0)                      # the morning pattern is in the sample
        self.assertAlmostEqual(self.e["window"]["solar"]["above_hsl_mwh"], above, delta=0.06)
        self.assertAlmostEqual(self.e["window"]["solar"]["below_hsl_mwh"], float((g["hsl"] - g["gen"]).clip(lower=0).sum()), delta=0.06)

    def test_a_region_has_output_and_no_limit(self):
        e = self.e
        self.assertEqual(sorted(r["id"] for r in e["regions"]["wind"]), ["COASTAL", "NORTH", "PANHANDLE", "SOUTH", "WEST"])
        self.assertEqual(sorted(r["id"] for r in e["regions"]["solar"]), ["CenterEast", "CenterWest", "FarEast", "FarWest", "NorthWest", "SouthEast"])
        for fuel in ("wind", "solar"):
            for r in e["regions"][fuel]:
                self.assertEqual(set(r), {"id", "entity", "hours_held", "generation_mwh", "share_of_fuel_pct"})          # no HSL, no estimate, no share of a limit
                self.assertEqual(r["hours_held"], 48)
            self.assertAlmostEqual(sum(r["share_of_fuel_pct"] for r in e["regions"][fuel]), 100, delta=0.05)
        self.assertEqual((e["region_limit"], e["year_limit"], e["history"]), ("no limit published", "no limit published", "not held yet"))
        self.assertIn("system-wide only", e["region_reason"])

    def test_a_year_of_the_sample_is_not_whole(self):
        y = self.e["years"]["2025"]
        self.assertEqual((y["wind_hours_held"], y["solar_hours_held"], y["hours_in_year"], y["whole"]), (144, 144, 8760, False))
        self.assertNotIn("hsl", json.dumps(self.e["years"]))

    def test_the_command_writes_only_where_it_is_told(self):
        site = os.path.join(SITE, "data", "curtailment", "ercot.json")
        before = os.path.getmtime(site)
        with tempfile.TemporaryDirectory() as d:
            for name, frame in ((ep.HOURLY, self.hourly), (ep.OUTPUT, self.output)):
                with open(os.path.join(d, f"{name}.csv"), "w", encoding="utf-8", newline="") as f:
                    f.write("# a sample of ERCOT's own files (tests/fixtures/session144/ercot)\n")
                    frame.to_csv(f, index=False)
            out = os.path.join(d, "out")
            with mock.patch("builtins.print"):
                self.assertEqual(ep.main(["--in-dir", d, "--out-dir", out]), 0)
                self.assertEqual(ep.main(["--in-dir", out, "--out-dir", out]), 1)          # no table there: it fails, and writes nothing more
            with open(os.path.join(out, "ercot.json"), encoding="utf-8") as f:
                text = f.read()
            self.assertEqual(json.loads(text)["days"], self.e["days"])
            self.assertNotIn("NaN", text)
        self.assertEqual(os.path.getmtime(site), before)


class TheSiteFiles(unittest.TestCase):
    def test_texas_as_committed(self):
        e = site_file("ercot.json")
        self.assertEqual(e["tables"], ["ercot_wind_solar_hsl_hourly", "ercot_wind_solar_output_hourly"])
        self.assertGreaterEqual(e["whole_days"], 9)
        self.assertEqual(len(e["hours"]), e["hours_held"])
        whole = [d for d in e["days"].values() if d["whole"]]
        for fuel in ("wind", "solar"):
            self.assertAlmostEqual(e["window"][fuel]["below_hsl_mwh"], sum(d[fuel]["below_hsl_mwh"] for d in whole), delta=0.06 * len(whole))
        for m, r in e["months"].items():
            self.assertTrue(("missing" in r) != ("both" in r), m)                                        # a reason or a figure, never both
            if "both" in r:
                self.assertGreaterEqual(r["hours_held"], 0.95 * r["hours_in_month"], m)
        self.assertTrue(all(0 <= d["both"]["share_pct"] <= 100 for d in e["days"].values()))
        self.assertEqual(sorted(e["years"]), ["2023", "2024", "2025"])
        self.assertTrue(all(y["whole"] for y in e["years"].values()))

    def test_every_caiso_month_has_a_share_and_none_passes_100(self):
        s = site_file("shares.json")
        ca, spp = s["grids"]["caiso"], s["grids"]["spp"]
        self.assertEqual((ca["months_with_share"], len(ca["months"]), ca["missing"]), (149, 149, {}))
        self.assertEqual(min(spp["months"]), "2018-09")
        for g in (ca, spp):
            self.assertTrue(all(0 <= r["share_pct"] <= 100 for r in g["months"].values()))
            self.assertTrue(all(len(why) > 10 for why in g["missing"].values()))
        self.assertNotIn("not computable", json.dumps(s))
        d = node("import fs from 'node:fs'; import * as c from './lib/curtailment.ts'; const s = JSON.parse(fs.readFileSync('./data/curtailment/shares.json', 'utf-8'));"
                 "console.log(JSON.stringify({y: c.yearShare(s.grids.caiso, '2025'), none: c.yearShare(s.grids.spp, '2015'), m: c.periodShare(s.grids.caiso, '2026-04'), marks: c.shareMarks(s.grids.caiso),"
                 "why: c.shareReason(s.grids.spp, '2018-07')}));")
        ms = [r for m, r in ca["months"].items() if m.startswith("2025-")]
        cur, out = sum(r["curtailed_mwh"] for r in ms), sum(r["output_mwh"] for r in ms)
        self.assertAlmostEqual(d["y"]["share"], 100 * cur / (cur + out), places=9)                        # a year: the months' own figures, one definition
        self.assertEqual((d["y"]["months"], d["none"]), (12, None))
        self.assertEqual(d["m"]["share"], ca["months"]["2026-04"]["share_pct"])
        self.assertEqual(d["marks"]["highest"], max(ca["months"], key=lambda m: ca["months"][m]["share_pct"]))
        self.assertEqual(d["why"], spp["missing"]["2018-07"])

    def test_a_negative_price_hour_is_counted_once(self):
        f = site_file("free_energy.json")
        n = 0
        for g in f["grids"].values():
            for loc in g["locations"]:
                self.assertIsNone(loc["lat"])                                                                # no coordinate is held, none is made up
                self.assertIsNone(loc["lon"])
                for w in ("month", "year"):
                    x = loc[w]
                    if "missing" in x:
                        self.assertNotIn("under5", x)
                        continue
                    n += 1
                    self.assertLessEqual(x["negative"], x["under5"])                                         # the hours below zero are among the hours under 5
                    self.assertLessEqual(x["under5"], x["hours_held"])
                if loc["heat"]["whole"] and "missing" not in loc["year"]:
                    self.assertEqual(sum(map(sum, loc["heat"]["under5"])), loc["year"]["under5"])            # an hour is in one cell and no other
                    self.assertEqual(sum(map(sum, loc["heat"]["negative"])), loc["year"]["negative"])
        self.assertGreater(n, 30)
        self.assertEqual({k: v["words"] for k, v in f["blank"].items()}, {"miso": "paused while terms are reviewed", "pjm": "licensed source needed"})


class ThePage(unittest.TestCase):
    def test_one_tool_one_page_one_address(self):
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "curtailment", "page.tsx")))
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "curtailment", "v2")))
        for kept in ("curtailment-original", "curtailment-v2"):                                              # nothing was deleted
            self.assertTrue(os.path.exists(os.path.join(SITE, "app", "_retired", kept, "page.tsx")), kept)
        self.assertIn('{ source: "/curtailment/v2", destination: "/curtailment", permanent: true }', src("site", "next.config.ts"))
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/curtailment'), statusOf('/curtailment/v2'), statusOf('/data/methods/curtailment')]));")
        self.assertEqual(d, ["review", "review", "review"])
        self.assertIn('"/curtailment/v2": "review"', src("site", "lib", "release.ts"))                       # its line stays: an address typed by hand has a status
        self.assertNotIn("/curtailment/v2", src("site", "lib", "audience.ts"))
        self.assertIn('href: "/curtailment", label: "Curtailment", line: "Wind and solar output curtailed, by grid', src("site", "lib", "pages.ts"))
        import scheduled
        self.assertEqual(scheduled.JOBS["curtailment_profile"]["page"], "/curtailment")

    def test_the_address_of_a_choice(self):
        d = node("import * as c from './lib/curtailment.ts'; import * as v from './lib/curtailmentv2.ts';"
                 "console.log(JSON.stringify({a: c.link({grid: 'ercot', place: 'HB_WEST'}, 'free-energy'), b: c.link({grid: 'caiso', period: '2026-04', dur: 4}), n: c.link({grid: 'nyiso', place: 'N.Y.C.', win: 'month', dur: 8}),"
                 "c: [c.choiceOf({}), c.choiceOf({grid: 'miso'}), c.choiceOf({grid: 'pjm', dur: '3'}), c.choiceOf({grid: 'ercot', place: 'HB_WEST', dur: '8', win: 'month'})], old: v.href('2024-04'),"
                 "open: c.GRIDS.filter((g) => g.open).map((g) => g.id), shut: c.GRIDS.filter((g) => !g.open).map((g) => [g.id, g.words]), names: [c.placeName('TH_SP15_GEN-APND'), c.placeName('.Z.MAINE'), c.placeName('HB_WEST'), c.usd(-41173948), c.usd(812400.4)]}));")
        self.assertEqual(d["a"], "/curtailment?grid=ercot&place=HB_WEST#free-energy")                        # the address session 145's page links
        self.assertEqual(d["b"], "/curtailment?period=2026-04")
        self.assertEqual(d["n"], "/curtailment?grid=nyiso&place=N.Y.C.&win=month&dur=8")
        self.assertEqual([x["grid"] for x in d["c"]], ["caiso", "caiso", "caiso", "ercot"])                  # MISO and PJM cannot be chosen
        self.assertEqual([x["dur"] for x in d["c"]], [4, 4, 4, 8])
        self.assertEqual((d["c"][3]["place"], d["c"][3]["win"]), ("HB_WEST", "month"))
        self.assertEqual(d["old"], "/curtailment?period=2024-04")
        self.assertEqual(d["open"], ["caiso", "spp", "ercot", "isone", "nyiso"])
        self.assertEqual(d["shut"], [["miso", "paused while terms are reviewed"], ["pjm", "licensed source needed"]])
        self.assertEqual(d["names"], ["SP15", "MAINE", "HB WEST", "-41.2 million", "812,400"])

    def test_the_face_holds_no_method_words_and_no_em_dash(self):
        for parts in FACE_FILES:
            text = src(*parts)
            self.assertNotIn(DASH, text, parts)
            # what a visitor can read: the comments of the source are not the face
            shown = re.sub(r"/\*[\s\S]*?\*/", " ", "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//")))
            self.assertIsNone(METHOD_WORDS.search(shown), (parts, METHOD_WORDS.search(shown)))
        page = src(*FACE_FILES[0])
        self.assertIn("data-face={c.grid}>{face?.line}", page)                                               # one line per grid, the library's own
        self.assertIn("FACE[x.id]?.line", page)
        self.assertIn('const METHOD = "/data/methods/curtailment"', page)
        face = node("import { FACE } from './lib/freeenergy.ts'; console.log(JSON.stringify(FACE));")
        self.assertEqual(sorted(face), ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"])
        self.assertEqual((face["miso"]["line"], face["pjm"]["line"]), ("Paused while terms are reviewed.", "Licensed source needed."))
        self.assertTrue(face["ercot"]["line"].startswith("The ERW's estimate") and face["caiso"]["line"].startswith("CAISO's own figure"))
        self.assertTrue(all(len(v["line"]) < 170 for v in face.values()))                                    # a line, not a paragraph

    def test_every_chart_answers_the_mouse(self):
        charts = src(*FACE_FILES[2])
        self.assertTrue(charts.startswith('"use client";'))
        self.assertIn('from "@/components/echarts"', charts)
        parts = re.split(r"\nexport function ", charts)[1:]
        self.assertEqual([p.split("(")[0] for p in parts], ["XY", "Heat"])
        for p in parts:
            self.assertRegex(p, r"tooltip: \{ \.\.\.st\.tooltip, trigger: \"(axis|item)\"", p[:20])
            self.assertIn("formatter:", p)
            self.assertIn("data-chart={id}", p)
        used = 0
        for parts_ in FACE_FILES[:2]:
            text = src(*parts_)
            self.assertNotIn("<svg", text, parts_)                                                           # no bare drawing without a hover
            for static in ("StackedArea", "LineChart", "Sparkline", "BoxChart"):
                self.assertNotIn(static, text, (parts_, static))
            used += len(re.findall(r"<(XY|Heat) id=\"", text))
        self.assertGreaterEqual(used, 11)
        ids = re.findall(r"<(?:XY|Heat) id=\"([a-z-]+)\"", src(*FACE_FILES[0]) + src(*FACE_FILES[1]))
        self.assertEqual(sorted(ids), sorted(["days", "months", "hours", "months-reason", "battery", "months-fuel", "free-heat", "worth-months", "battery-months", "texas-hours", "texas-pattern"]))
        self.assertIn("title={text}", src(*FACE_FILES[1]))                                                   # the schematic's tiles say their count on hover

    def test_the_placeholders(self):
        sections, page = src(*FACE_FILES[1]), src(*FACE_FILES[0])
        self.assertIn('words = "not held yet"', sections)
        self.assertIn('data-missing="1" title={why}', sections)
        self.assertIn("<Blank words={file.region_limit} why={file.region_reason} />", sections)             # Texas by region: no limit published
        self.assertIn("<Blank words={file.history} why={file.history_reason} />", sections)
        self.assertIn("file.blank[x.id]?.words ?? x.words", sections)
        self.assertIn("A schematic, not a map", sections)
        self.assertIn('data-open="0"', page)
        self.assertNotIn("not computable", page + sections)
        for anchor in ('id="free-energy"', 'id="worth"', 'id="texas"', 'id="whose"', 'id="days"', 'id="months"', 'id="hours"', 'id="reason"', 'id="batteries"'):
            self.assertIn(anchor, page + sections, anchor)
        self.assertIn("Built {profile.built.slice(0, 10)}", page)

    def test_the_method_note_holds_what_the_pages_said(self):
        note = src("docs", "methods", "curtailment.md")
        for words in ("## Session 144", "The data does not say where.", "SPP's own figure: wind and solar curtailed by redispatch", "MISO publishes no wind or solar curtailment series",
                      "It includes curtailment and anything else that keeps", "CAISO's two output sources disagree in 2026", "11 to 20 percent", "The schematic is not a map",
                      "29,190 MWh above", "Any duplication of the Content", "Operations Performance Metrics Monthly Report", "One cycle a day", "the fleet's highest five-minute charging rate",
                      "each hour once", "NP4-737-CD", "9,241 five-minute rows", "That the two fall in the same hours does not say", "licensed source needed", "paused while terms are reviewed",
                      "no curtailment by weather zone can be built from open data"):
            self.assertIn(words, note, words)
        self.assertIn("## What each ISO's figure means", note)                                               # the note was extended, not replaced
        self.assertNotIn(DASH, note)

    def test_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-curtailment.mjs <base>")
        r = subprocess.run([exe, "scripts/check-curtailment.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (*FACE_FILES, ("site", "lib", "curtailment.ts"), ("site", "scripts", "check-curtailment.mjs"), ("warehouse", "derived", "ercot_estimate_page.py"),
                      ("site", "data", "curtailment", "ercot.json"), ("tests", "test_session144_page.py"), ("site", "next.config.ts")):
            self.assertNotIn(DASH, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
