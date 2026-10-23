"""Session 1009 (chain 070): the download route, finished. Until the owner rules whether downloads are public (the rule
of 12 October 2026), it answers only a request that carries the internal view's cookie. A table whose license verdict
is not public is refused with the packages' own words; the reader's filters (entity, variable, a UTC window) are the
Python package's, filter for filter (site/lib/downloadfilter.ts, run here with Node); the header carries the citation in
the release's words and the license verdict; the cap and the hourly limit may be set lower from the environment.
No request, no model call."""
import json
import os
import shutil
import subprocess
import sys
import unittest
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))

from erw import live  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


ROUTE = src("site", "app", "api", "download", "route.ts")
CASES = [
    ("series", {"entity": "eia:henry_hub", "start": "2025-01-01", "end": "2026-01-01"}),
    ("series", {"entity": "eia:wti_cushing,eia:brent", "variable": "spot_price"}),
    ("series", {"entity": "HB_NORTH,HB_WEST", "start": "2026-10-01T06:00:00Z"}),
    ("entities", {"entity": "eia860:10004:TG1", "variable": "generator", "start": "2025-01-01"}),
    ("events", {"variable": "eea_watch", "start": "2022-09-01", "end": "2022-09-15"}),
]


def python_query(shape, p):
    ents = [x for x in p.get("entity", "").split(",") if x] or None
    vars_ = [x for x in p.get("variable", "").split(",") if x] or None
    f = live.series_filters(ents, vars_, p.get("start"), p.get("end"), shape)
    return "".join("&" + urllib.parse.urlencode([kv], safe=",.():*") for kv in f)


def node_strips_types():
    """Node 22.18 and 23.6 on run a .ts file as it is; an older Node (a runner's system one) cannot."""
    if shutil.which("node") is None:
        return False
    v = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip().lstrip("v").split(".")
    major, minor = int(v[0]), int(v[1])
    return (major, minor) >= (22, 18) and not (major == 23 and minor < 6)


@unittest.skipUnless(node_strips_types(), "no Node here that runs a .ts file as it is (22.18 or later)")
class Filters(unittest.TestCase):
    def node(self, shape, p):
        code = ("import { downloadFilter } from './site/lib/downloadfilter.ts';"
                f"console.log(JSON.stringify(downloadFilter({json.dumps(shape)}, {json.dumps(p)})));")
        out = subprocess.run(["node", "--input-type=module", "-e", code], cwd=ROOT, capture_output=True, text=True,
                             timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr[-400:])
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_the_filters_are_the_python_package_s(self):
        for shape, p in CASES:
            got = self.node(shape, p)
            self.assertEqual(got["query"], python_query(shape, p), (shape, p))

    def test_a_bad_filter_is_refused_before_any_read(self):
        self.assertIn("error", self.node("series", {"entity": "ercot:HB_NORTH,HB_WEST"}))
        self.assertIn("error", self.node("series", {"start": "yesterday"}))
        self.assertIn("error", self.node("series", {"entity": "a;drop"}))


class Route(unittest.TestCase):
    def test_the_internal_view_only_before_anything_else(self):
        gate = "if (!(await cookieOpens(cookie, process.env.INTERNAL_COSTS_TOKEN))) {"
        self.assertIn(gate, ROUTE)
        self.assertLess(ROUTE.index(gate), ROUTE.index("if (licenseNeeded(table)) return text("))
        self.assertLess(ROUTE.index(gate), ROUTE.index('const lim = await limited(req, "download", PER_HOUR, 3600);'))

    def test_a_table_not_public_is_refused_with_the_packages_words(self):
        self.assertIn("const refused = refusal(table);", ROUTE)
        self.assertLess(ROUTE.index("if (refused) return text(refused, 403);"), ROUTE.index("const lim = await limited("))

    def test_the_header_cites_and_says_the_verdict(self):
        self.assertIn("# Cite: ${head} Via the Energy Research Warehouse (ERW), table \\`${table}\\`, the live set, fetched ${at}.", ROUTE)
        self.assertIn("# ERW license verdict: ${verdictOf(table)", ROUTE)
        self.assertIn("const it = pages(shape, table, select, filter.query);", ROUTE)
        cites = json.loads(src("site", "data", "table_citations.json"))
        self.assertTrue(cites["eia_fuel_spot_prices"].startswith("U.S. Energy Information Administration (EIA)."))

    def test_the_limits_from_the_environment_never_above_the_cap(self):
        self.assertIn("const ROW_CAP = Math.min(Number(process.env.ERW_DOWNLOAD_MAX_ROWS) || MAX_ROWS, MAX_ROWS);", ROUTE)
        self.assertIn("const PER_HOUR = Number(process.env.ERW_DOWNLOAD_PER_HOUR) || 60;", ROUTE)


if __name__ == "__main__":
    unittest.main()
