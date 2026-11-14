"""Session 3940 (chain 267): request 28 of docs/state/data_requests_licenses.md.

A grid in license_status.held_grids() builds no row data and no series file in any group of the price board. On
14 November 2026 a scratch build of board_page.py on the data machine wrote, of the held grids, only the spark, heat
and dark rows of NYISO's N.Y.C. and ISO-NE's Internal Hub (six series files): build_spreads drew every operator's main
hub without asking the hold. Held here on the real rows of tests/fixtures/board_1606/ with an empty spark input set,
and with held_grids() answering as the license file did on that day. No network, no model.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheHeldGridsSpreads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bp = cls.bp = builder()
        saved = bp.ls.held_grids
        bp.ls.held_grids = lambda today=None, path=None: {"ISO-NE", "MISO", "NYISO"}
        try:
            b = cls.b = bp.Board()
            day = {"2026-08-20": 30.0, "2026-08-21": 31.0}
            import pandas as pd
            frame = pd.DataFrame({"mean": day}).rename_axis("date")
            frame.index = pd.to_datetime(frame.index).date
            daily = {(f"{iso}:{bp.MAIN[iso]}", "da"): frame for iso in bp.ISO}
            gas = {d: 3.0 for d in frame.index}
            bp.build_spreads(b, daily, {"eia:henry_hub": gas}, {})
        finally:
            bp.ls.held_grids = saved
        cls.rows = {r["id"]: r for r in b.rows}

    def test_no_held_grid_row_has_values(self):
        for r in self.rows.values():
            if r.get("group") == "spark" and r.get("tags", {}).get("grid") in ("ISO-NE", "NYISO", "MISO", "PJM"):
                self.assertNotIn("last", r, r["id"])
                self.assertIn(r["status"], ("licensed", "paused"), r["id"])

    def test_one_licensed_row_a_held_grid(self):
        for iso, grid in (("nyiso", "NYISO"), ("isone", "ISO-NE")):
            r = self.rows[f"{iso}-spark"]
            self.assertEqual((r["group"], r["status"]), ("spark", "licensed"))
            self.assertIn("written permission", r["note"])
            main = self.bp.slug(f"{iso}:{self.bp.MAIN[iso]}")
            for kind in ("spark", "heat", "dark"):
                self.assertNotIn(f"{main}-{kind}", self.rows)

    def test_no_series_file_for_a_held_grid(self):
        held = ("nyiso", "isone")
        files = [k for k in getattr(self.b, "series", {}) if k.startswith(held)]
        self.assertEqual(files, [])

    def test_a_public_grid_keeps_its_rows(self):
        main = self.bp.slug(f"ercot:{self.bp.MAIN['ercot']}")
        self.assertEqual(self.rows[f"{main}-spark"]["status"], "ok")



class TheOutletNames(unittest.TestCase):
    """Request 1 of the same file: an en or em dash in a news outlet's name is folded to a hyphen before the registry,
    the citations and the release list copy it; the registry's two IEA rows are one."""

    def test_the_fold(self):
        news = os.path.join(ROOT, "warehouse", "news")
        if news not in sys.path:
            sys.path.insert(0, news)
        import ingest  # noqa: E402
        self.assertEqual(ingest.fold_dashes("IEA " + chr(0x2013) + " International Energy Agency"), "IEA - International Energy Agency")
        self.assertEqual(ingest.fold_dashes("A " + chr(0x2014) + " B"), "A - B")
        self.assertEqual(ingest.fold_dashes("Utility Dive"), "Utility Dive")

    def test_the_registry_holds_no_dash_in_an_outlet(self):
        import csv
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8", newline="") as f:
            names = [r["source"] for r in csv.DictReader(f)]
        self.assertEqual([n for n in names if chr(0x2013) in n or chr(0x2014) in n], [])
        self.assertEqual(names.count("IEA - International Energy Agency"), 1)



class TheRefusingHosts(unittest.TestCase):
    """Requests 13, 14, 15 and 23 to 26 of docs/state/data_requests_licenses.md: no feed on a host whose robots file
    refuses Anthropic's agents by name, and the CFTC's page only linked, never requested."""
    REFUSED = ("heatmap.news", "datacenterdynamics.com", "oilprice.com", "ans.org", "pv-magazine-usa.com")

    def test_no_refused_feed(self):
        import yaml
        with open(os.path.join(ROOT, "warehouse", "news", "feeds.yaml"), encoding="utf-8") as f:
            feeds = yaml.safe_load(f)["feeds"]
        hosts = [f["url"] for f in feeds]
        self.assertEqual([u for u in hosts if any(h in u for h in self.REFUSED)], [])
        self.assertIn("https://www.utilitydive.com/feeds/news/", hosts)

    def test_the_cftc_page_is_not_requested(self):
        src = open(os.path.join(ROOT, "warehouse", "connectors", "release_schedule.py"), encoding="utf-8").read()
        self.assertIn('if r["publisher"] == "EIA":', src)



class TheWildcardReading(unittest.TestCase):
    """Request 27: each of the three fetchers reads a robots file's "*" and "$" as the convention does and keeps the
    stricter of that and urllib.robotparser's answer. The Texas Comptroller's "Disallow: /*/" (read 2038) refuses /taxes/."""
    LINES = ["User-agent: *", "Disallow: /*/", "Allow: /$"]

    def mods(self):
        import importlib
        for sub in (("warehouse", "connectors"), ("warehouse", "thesis")):
            d = os.path.join(ROOT, *sub)
            if d not in sys.path:
                sys.path.insert(0, d)
        return [importlib.import_module(n) for n in ("eia_ba_boundaries", "large_load_filings")] + [self.series()]

    def series(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("thesis_series_3940", os.path.join(ROOT, "warehouse", "thesis", "series.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_the_comptrollers_rule(self):
        for m in self.mods():
            self.assertFalse(m.wildcard_allows(self.LINES, "*", "/taxes/"), m.__name__)
            self.assertTrue(m.wildcard_allows(self.LINES, "*", "/"), m.__name__)
            self.assertTrue(m.wildcard_allows(["User-agent: *", "Disallow:"], "*", "/a/b"), m.__name__)
            self.assertEqual(m.url_path("https://x.example/a/b?c=1"), "/a/b?c=1")

    def test_the_answer_does_not_rest_on_the_python(self):
        # urllib.robotparser reads "*" literally on the runner's Python 3.12 and as a wildcard on 3.14 (this machine):
        # the wildcard reading gives the same refusal on both
        for m in self.mods():
            self.assertFalse(m.wildcard_allows(["User-agent: *", "Disallow: /*/"], "ClaudeBot", "/taxes/"), m.__name__)

    def test_the_saved_file_check_refuses(self):
        import tempfile
        m = self.mods()[0]
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(chr(10).join(self.LINES))
        try:
            self.assertFalse(m.robots_allows(f.name, "https://comptroller.texas.gov/taxes/"))
        finally:
            os.remove(f.name)


if __name__ == "__main__":
    unittest.main()
