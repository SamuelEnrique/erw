"""Session 402: the Energy Digest audited, every number traced.

What is held here, without a network and without a database: the Digest's figures each get a table and a key on the
page (site/lib/digest.ts, tested by site/scripts/test-digest-numbers.mjs, run here), a held grid's figure reads
"license needed" from 21 October, the archive names every day (a weekday without a Digest says so, today before it is
written says so, and /digest shows no other day's Digest in today's place), scripts/check_digest.py recomputes each
figure by the Digest's own rule and fails on a wrong one, and scripts/check-values.mjs reads the Digest's pages.
"""
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def node(*args):
    return subprocess.run([NODE, "--no-warnings", "--import", "./scripts/alias-register.mjs", *args], cwd=SITE, capture_output=True,
                          text=True, encoding="utf-8", timeout=300)


@unittest.skipUnless(NODE, "node is not on this machine")
class TheSiteSide(unittest.TestCase):
    def test_the_node_tests_pass(self):
        r = node("scripts/test-digest-numbers.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("tests passed", r.stdout)

    def test_every_digest_held_has_its_figures_and_the_holds_of_21_october(self):
        r = node("scripts/digest-figures.mjs", "--now", "2026-10-21")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        d = json.loads(r.stdout)
        self.assertEqual(d["holds_on"], "2026-10-21")
        self.assertIn("2026-10-20", d["digests"])
        for date, v in d["digests"].items():
            for f in v["figures"]:
                grid = f["entity"].split(":", 1)[0]
                if f["part"] in ("dam", "rt"):
                    # NYISO's and ISO-NE's tables are held, and MISO's rows of the consolidated tables; ERCOT, CAISO and SPP are not
                    self.assertEqual(f["held"], grid in ("nyiso", "isone", "miso"), (date, f["key"]))
                if f["part"] in ("fuel", "chart"):
                    self.assertFalse(f["held"], (date, f["key"]))
        r = node("scripts/digest-figures.mjs", "--now", "2026-10-20")
        self.assertFalse(any(f["held"] for v in json.loads(r.stdout)["digests"].values() for f in v["figures"]), "nothing is held before 21 October")


class ThePages(unittest.TestCase):
    def test_the_index_shows_todays_digest_or_says_there_is_none(self):
        s = src("site", "app", "digest", "page.tsx")
        self.assertIn("dayKind(today, dates, today)", s)
        self.assertIn('kind === "digest"', s)
        self.assertIn("renderDigest(DOCS.digests[today], today, new Date(), revisions)", s)
        self.assertNotIn("DOCS.digests[newest]", s, "the newest Digest is no longer drawn in today's place")
        self.assertIn("No Digest yet for", s)
        self.assertIn("No Digest on", s)

    def test_a_day_of_the_archive_without_a_digest_says_so(self):
        s = src("site", "app", "digest", "[date]", "page.tsx")
        self.assertIn("if (kind === null) notFound();", s)
        self.assertIn("No Digest was published for", s)
        self.assertIn("renderDigest(DOCS.digests[date], date, new Date(), revisions)", s)
        self.assertNotIn(" render(md", s)
        m = src("site", "lib", "markdown.ts")
        self.assertIn("export function renderDigest", m)
        self.assertIn("return archiveOf(digestDates(), today);", m)

    def test_check_values_reads_the_digest(self):
        s = src("site", "scripts", "check-values.mjs")
        for k in ('p[0] === "digest_dam"', 'p[0] === "digest_rt"', 'p[0] === "digest_fuel"', 'PAGES.push("/digest"', "digestChartText"):
            self.assertIn(k, s)

    def test_no_em_dash_in_the_files_of_the_session(self):
        for parts in (("site", "lib", "digest.ts"), ("site", "scripts", "digest-figures.mjs"), ("site", "scripts", "test-digest-numbers.mjs"),
                      ("scripts", "check_digest.py"), ("site", "app", "digest", "page.tsx"), ("site", "app", "digest", "[date]", "page.tsx"),
                      ("site", "app", "about", "page.tsx")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


class TheChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = load("s402_check_digest", "scripts", "check_digest.py")

    def test_the_rules(self):
        c = self.c
        self.assertEqual(c.mean2([44.29, 44.30]), "44.30")          # half up, on the values as written
        self.assertEqual(c.mean2([-5.335, -5.335]), "-5.34")
        self.assertEqual(c.chart_text(1658262.63), "1,658,263")
        self.assertEqual(c.chart_text(321.5), "321.5")
        self.assertEqual(c.current("miso_dam_hub_prices"), "iso_dam_hub_prices")
        self.assertEqual(c.current("nyiso_rtm_zone_prices"), "nyiso_rtm_zone_prices")
        start, end, hours = c.day_bounds("2026-11-01", "America/Chicago")
        self.assertEqual(hours, 25)                                  # the day the clocks go back
        self.assertEqual(c.iso_z(start), "2026-11-01T05:00:00Z")
        self.assertEqual(c.day_bounds("2026-11-01", "Etc/GMT+5")[2], 24)   # MISO's day is EST all year

    def _csvs(self, d, rows):
        cols = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]
        for table, rs in rows.items():
            with open(os.path.join(d, f"{table}.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a test table\n")
                w = csv.DictWriter(f, cols)
                w.writeheader()
                for e, v, ts, val in rs:
                    w.writerow({"entity": e, "variable": v, "ts_utc": ts, "value": val})

    def test_a_figure_is_ok_failed_or_not_held(self):
        c = self.c
        with tempfile.TemporaryDirectory() as d:
            # ERCOT's operating day 2026-10-19 in Chicago: 05:00 UTC to 05:00 UTC, 24 hours of 10 and 20
            hours = [(f"ercot:HB_NORTH", "spp_dam", f"2026-10-{19 + (h + 5) // 24:02d}T{(h + 5) % 24:02d}:00:00Z", 10 if h % 2 else 20) for h in range(24)]
            self._csvs(d, {"iso_dam_hub_prices": hours,
                           "eia_fuel_spot_prices": [("eia:henry_hub", "spot_price", "2026-10-14T00:00:00Z", 3.215)],
                           "nyiso_rtm_zone_prices": [("nyiso:N.Y.C.", "lmp_rtm_15m_mean", "2026-10-19T12:00:00Z", 192.894)]})
            src_ = c.Csv(d)
            fig = lambda key, raw, entity="": {"key": key, "raw": raw, "text": raw, "entity": entity, "table": key.split("|")[2], "held": False}   # noqa: E731
            self.assertEqual(c.check_figure(src_, "2026-10-20", fig("digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-19", "15.00"), {}), ("ok", "15.00"))
            self.assertEqual(c.check_figure(src_, "2026-10-20", fig("digest_dam|ERCOT|ercot_dam_hub_prices|HB_NORTH|2026-10-19", "15.01"), {})[0], "FAIL")
            self.assertEqual(c.check_figure(src_, "2026-10-20", fig("digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-18", "15.00"), {})[0], "not here")
            self.assertEqual(c.check_figure(src_, "2026-10-20", fig("digest_dam|NYISO|nyiso_dam_zone_prices|N.Y.C.|2026-10-19", "1.00"), {})[0], "not here")
            rt = fig("digest_rt|nyiso_rtm_zone_prices|N.Y.C.|lmp_rtm_15m_mean|2026-10-19T12:00:00Z", "192.89", "nyiso:N.Y.C.")
            rt["table"] = "nyiso_rtm_zone_prices"
            self.assertEqual(c.check_figure(src_, "2026-10-20", rt, {}), ("ok", "192.89"))
            fu = fig("digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-10-14", "3.21")
            fu["table"] = "eia_fuel_spot_prices"
            self.assertEqual(c.check_figure(src_, "2026-10-20", fu, {})[0], "ok")
            fu["raw"] = "3.22"
            self.assertEqual(c.check_figure(src_, "2026-10-20", fu, {})[0], "FAIL")

    def test_the_run_fails_on_a_wrong_figure_and_on_nothing_checked(self):
        c = self.c
        with tempfile.TemporaryDirectory() as d:
            self._csvs(d, {"eia_fuel_spot_prices": [("eia:brent", "spot_price", "2026-10-14T00:00:00Z", 126.55)]})
            def run(raw):
                figs = {"holds_on": "2026-10-21", "digests": {"2026-10-20": {"chart": None, "figures": [
                    {"part": "fuel", "key": "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-10-14", "raw": raw, "text": raw, "table": "eia_fuel_spot_prices",
                     "entity": "eia:brent", "held": False, "title": ""}]}}}
                path = os.path.join(d, "figures.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(figs, f)
                return c.main(["--figures", path, "--in-dir", d, "--date", "2026-10-20"])
            self.assertEqual(run("126.55"), 0)
            self.assertEqual(run("126.56"), 1)
            os.remove(os.path.join(d, "eia_fuel_spot_prices.csv"))
            self.assertEqual(run("126.55"), 1)   # nothing could be checked


if __name__ == "__main__":
    unittest.main()
