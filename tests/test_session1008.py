"""Session 1008 (chain 070): each table's row on /data gives the three one-line calls that fetch it (site/lib/packages.ts,
oneLineCalls), or the packages' refusal of a table that is not public (refusal). The lines are the specification's
("One line a table") for ten tables; the refusal is the Python package's own, word for word; the verdicts the site
reads (site/data/table_verdicts.json) are the record's. No request, no model call."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
sys.path.insert(0, os.path.join(ROOT, "package", "tools"))

import erw  # noqa: E402
from erw import api, licenses  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


LIB = src("site", "lib", "packages.ts")
SPEC = src("docs", "methods", "packages.md")
TEN = ["eia_fuel_spot_prices", "eia930_all_demand", "caiso_grid_emergencies", "eia860m_retired_generators",
       "carbon_intensity_monthly", "iso_curtailment_monthly", "utility_service_territories", "energy_deals",
       "iso_rtm_hub_prices", "pjm_rpm_capacity_prices"]


def ts_template(name):
    m = re.search(rf"{name}: `([^`]*)`", LIB)
    return m.group(1)


class OneLine(unittest.TestCase):
    def test_the_lines_are_the_specification_s(self):
        forms = {"python": ts_template("python"), "stata": ts_template("stata"), "r": ts_template("r")}
        spec = {"python": 'erw.fetch("<table>")', "stata": "erw fetch <table>, clear", "r": 'erw_fetch("<table>")'}
        for k in forms:
            self.assertEqual(forms[k].replace("${table}", "<table>"), spec[k], k)
            self.assertIn(f"`{spec[k]}`", SPEC, k)
        for t in TEN:
            self.assertEqual(forms["python"].replace("${table}", t), f'erw.fetch("{t}")')

    def test_the_refusal_is_the_package_s(self):
        self.assertIn("`${table} is not public: ${v[0]}. ${v[1]} The ERW's license record: ${LICENSE_RECORD}`", LIB)
        self.assertIn(f'LICENSE_RECORD = "{licenses.LICENSES_URL}"', LIB)
        verdicts = json.loads(src("site", "data", "table_verdicts.json"))
        for t in TEN:
            if t not in verdicts:   # an internal table is never named on the site (session 1014, test 149)
                self.assertEqual(erw.license(t)["verdict"], "internal", t)
                continue
            v, words = verdicts[t]
            self.assertEqual(v, erw.license(t)["verdict"], t)
            if v != "public":
                self.assertEqual(f"{t} is not public: {v}. {words} The ERW's license record: {licenses.LICENSES_URL}",
                                 api.refusal(t))

    def test_the_site_s_verdicts_are_the_record_s(self):
        verdicts = json.loads(src("site", "data", "table_verdicts.json"))
        record = {r["table"]: [r["verdict"], r["words"]] for r in licenses.build(__import__("pathlib").Path(ROOT))}
        # every verdict the site shows is the record's (a stale one is a fault: python package/tools/build_tables.py);
        # a table the record has and the site's file not yet (a new table of the data machine's) is listed, not failed
        stale = sorted(t for t in verdicts if record.get(t) != verdicts[t])
        self.assertEqual(stale, [], "run python package/tools/build_tables.py")
        import csv
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            public = {r["table"] for r in csv.DictReader(f) if r["license"] == "public"}
        self.assertFalse(set(verdicts) - public, "an internal table is never named on the site (test 149)")
        new = sorted((set(record) & public) - set(verdicts))
        if new:
            print(f"site/data/table_verdicts.json lacks {len(new)} new table(s): {', '.join(new[:10])}")

    def test_the_page_draws_them(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn("data-tool-lines={r.table_name}", page)
        self.assertIn("refusal(r.table_name)", page)
        self.assertIn("oneLineCalls(r.table_name).python", page)


if __name__ == "__main__":
    unittest.main()
