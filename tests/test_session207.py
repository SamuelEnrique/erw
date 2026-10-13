"""Session 207: licenses and desktop tools (the owner's chain prompt of 12 October 2026).

1. The two FRED-sourced series moved to their original public-domain sources: the spot prices are EIA's own table
   (eia_fuel_spot_prices), the Treasury yields the Board's own H.15 download (warehouse/connectors/frb_treasury.py,
   frb_treasury_yields); the FRED tables are retired (warehouse/metadata/retired_tables.csv) and coverage drops them.
2. A license status for the tables flagged public whose publisher asks for permission: from 20 October 2026 they show
   "license needed" unless a permission is recorded (scripts/licenses.py status, warehouse/metadata/license_status.csv,
   warehouse/metadata/license_status.py, site/data/license_status.json, site/lib/license.ts); nothing before that day.
"""
import csv
import json
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for p in ("warehouse/connectors", "warehouse/metadata", "scripts"):
    sys.path.insert(0, os.path.join(ROOT, p))
import frb_treasury as frb  # noqa: E402
import license_status as ls  # noqa: E402
import licenses  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


H15 = '\n'.join([
    '"Series Description","Market yield on U.S. Treasury securities at 1-month   constant maturity, quoted on investment basis","at 2-year","at 10-year","at 30-year"',
    '"Unit:","Percent:_Per_Year","Percent:_Per_Year","Percent:_Per_Year","Percent:_Per_Year"',
    '"Multiplier:","1","1","1","1"',
    '"Currency:","NA","NA","NA","NA"',
    '"Unique Identifier: ","H15/H15/RIFLGFCM01_N.B","H15/H15/RIFLGFCY02_N.B","H15/H15/RIFLGFCY10_N.B","H15/H15/RIFLGFCY30_N.B"',
    '"Time Period","RIFLGFCM01_N.B","RIFLGFCY02_N.B","RIFLGFCY10_N.B","RIFLGFCY30_N.B"',
    '2019-01-01,ND,ND,ND,ND',
    '2019-01-02,2.40,2.50,2.66,2.97',
    '2019-01-03,2.42,2.39,2.56,2.92',
    '2019-01-04,2.40,2.50,2.67,2.98',
]) + "\n"


class TheBoardsTreasuryYields(unittest.TestCase):
    def test_the_package_csv_is_read_as_the_three_series(self):
        table, empty, days = frb.parse(H15, "https://x", "2026-10-13T00:30:03Z")
        self.assertEqual((days, empty), (4, 3))  # four business days listed, the holiday's ND counted once a series
        self.assertEqual(sorted(table["entity"].unique()), ["frb:tcm_10y", "frb:tcm_2y", "frb:tcm_30y"])
        two = table[table["entity"] == "frb:tcm_2y"].set_index("ts_utc")["value"]
        self.assertEqual(two.to_dict(), {"2019-01-02T00:00:00Z": 2.50, "2019-01-03T00:00:00Z": 2.39, "2019-01-04T00:00:00Z": 2.50})
        self.assertEqual(set(table["node"][table["entity"] == "frb:tcm_30y"]), {"H15/H15/RIFLGFCY30_N.B"})
        self.assertEqual(set(table["unit"]), {"pct"})
        self.assertEqual(set(table["variable"]), {"yield"})
        self.assertEqual(set(table["source"]), {"frb:h15_treasury_yields"})
        self.assertEqual(list(table.columns), ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source",
                                               "source_url", "retrieved_at", "vintage"])

    def test_a_column_missing_or_a_value_that_is_not_a_number_stops_it(self):
        with self.assertRaises(RuntimeError):
            frb.parse(H15.replace("RIFLGFCY30_N.B", "RIFLGFCY20_N.B"), "u", "t")
        with self.assertRaises(RuntimeError):
            frb.parse(H15.replace("2019-01-03,2.42,2.39", "2019-01-03,2.42,n/a"), "u", "t")

    def test_the_source_is_the_boards_own_and_public(self):
        self.assertEqual(frb.NAME, "frb_treasury_yields")
        self.assertIn("federalreserve.gov/datadownload/Output.aspx?rel=H15", frb.URL)
        self.assertEqual(frb.SOURCE_ENTRY["license"], "public")
        self.assertNotIn("fred", frb.SOURCE_ENTRY["publisher"].lower())
        self.assertIn("User-Agent", frb.HEADERS)

    def test_the_readers_moved_with_it(self):
        self.assertIn('table_daily("frb_treasury_yields")', src("warehouse", "derived", "board_page.py"))
        self.assertNotIn('table_daily("fred_treasury_yields")', src("warehouse", "derived", "board_page.py"))
        sh = src("warehouse", "refresh_board.sh")
        self.assertIn('--step "frb_treasury" -- "$PY" warehouse/connectors/frb_treasury.py', sh)
        self.assertNotIn("fred_treasury.py", sh)
        self.assertIn("frb_treasury_yields", sh.split("\n")[24])
        daily = src("warehouse", "run_daily.sh")
        self.assertNotIn("run_other fred_series", daily)
        self.assertIn("run_other eia_fuels", daily)
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertNotIn("'^fred_daily_spot_prices$'", live)
        self.assertIn("frb_treasury_yields", live)
        self.assertIn("frb:h15_treasury_yields", live)
        self.assertNotIn('"fred_daily_spot_prices"', src("warehouse", "analysis", "watch.py"))  # no longer a listed table (a comment names it)
        for f in ("questions.yaml", "questions_s13.yaml", "questions_s20.yaml", "expected.py"):
            self.assertNotIn("fred_daily_spot_prices", src("warehouse", "chat", "eval", f), f)


class RetiredTables(unittest.TestCase):
    def test_the_three_fred_tables_are_retired_with_their_replacements(self):
        rows = {r["table"]: r for r in csv.DictReader(open(os.path.join(ROOT, "warehouse", "metadata", "retired_tables.csv"), encoding="utf-8"))}
        self.assertEqual(set(rows), {"fred_daily_spot_prices", "fred_treasury_yields", "fred_imf_commodity_prices"})
        self.assertEqual(rows["fred_daily_spot_prices"]["replaced_by"], "eia_fuel_spot_prices")
        self.assertEqual(rows["fred_treasury_yields"]["replaced_by"], "frb_treasury_yields")
        self.assertEqual(rows["fred_imf_commodity_prices"]["replaced_by"], "imf_commodity_prices")
        for r in rows.values():
            self.assertEqual(r["retired_on"], "2026-10-13")

    def test_coverage_knows_them_and_holds_none(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
        import build_coverage as bc
        self.assertEqual(bc.retired_tables(), {"fred_daily_spot_prices", "fred_treasury_yields", "fred_imf_commodity_prices"})
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        self.assertEqual([t for t in cov["table"] if t.startswith("fred_")], [])
        self.assertIn("frb_treasury_yields", set(cov["table"]))
        self.assertEqual(cov.set_index("table").loc["frb_treasury_yields", "license"], "public")
        doc = src("docs", "coverage.md")
        self.assertNotIn("`fred_", doc)
        self.assertIn("`frb_treasury_yields`", doc)
        # the source registry keeps the FRED rows as history; the package's briefing no longer offers the tables
        self.assertNotIn("fred_daily_spot_prices (public", src("package", "llms.txt"))
        self.assertIn("frb_treasury_yields", src("package", "llms.txt"))

    def test_the_licenses_document_settles_the_boards_table(self):
        self.assertIn("| `frb_treasury_yields` | FRB | may be public |", src("docs", "licenses.md"))
        verdicts = {r["key"]: r for r in csv.DictReader(open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8"))}
        self.assertIn("public domain", verdicts["FRB"]["sentence"])
        self.assertEqual(verdicts["FRB"]["verdict"], "may be public")


class LicenseStatus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "license_status.csv")
        with open(self.path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=licenses.STATUS_COLS, lineterminator="\n")
            w.writeheader()
            w.writerow({"table": "iso_hub_prices_history", "status": "license needed", "from": "2026-10-20", "publishers": "ISO-NE; MISO; NYISO",
                        "verdict": "needs written permission", "permission": "", "permission_ref": "", "note": ""})
            w.writerow({"table": "news_index", "status": "license needed", "from": "2026-10-20", "publishers": "Bloomberg; Reuters",
                        "verdict": "needs written permission", "permission": "", "permission_ref": "", "note": ""})
            w.writerow({"table": "energy_projects", "status": "permission recorded", "from": "2026-10-20", "publishers": "ISO-NE",
                        "verdict": "needs written permission", "permission": "granted by email, 2026-10-15", "permission_ref": "runs/x", "note": ""})

    def test_nothing_is_needed_before_the_day_and_everything_listed_from_it(self):
        self.assertFalse(ls.needed("iso_hub_prices_history", "2026-10-19", self.path))
        self.assertEqual(ls.needed_tables("2026-10-19", self.path), set())
        self.assertEqual(ls.held_grids("2026-10-19", self.path), set())
        self.assertTrue(ls.needed("iso_hub_prices_history", "2026-10-20", self.path))
        self.assertTrue(ls.needed("news_index", "2026-11-01", self.path))
        self.assertEqual(ls.needed_tables("2026-10-20", self.path), {"iso_hub_prices_history", "news_index"})

    def test_a_recorded_permission_and_an_unlisted_table_are_not_held(self):
        self.assertFalse(ls.needed("energy_projects", "2026-10-20", self.path))
        self.assertFalse(ls.needed("eia_fuel_spot_prices", "2026-10-20", self.path))

    def test_the_grids_among_the_deciding_publishers(self):
        self.assertEqual(ls.held_publishers("2026-10-20", self.path), {"ISO-NE", "MISO", "NYISO", "Bloomberg", "Reuters"})
        self.assertEqual(ls.held_grids("2026-10-20", self.path), {"ISO-NE", "MISO", "NYISO"})
        self.assertIn("written permission", ls.note("NYISO"))
        self.assertIn("Held, not shown", ls.note("NYISO"))

    def test_the_real_file_is_the_sweeps_40_tables_from_20_october_with_no_permission_yet(self):
        rows = ls.rows()
        self.assertEqual(len(rows), 40)
        self.assertEqual({r["status"] for r in rows}, {"license needed"})
        self.assertEqual({r["from"] for r in rows}, {"2026-10-20"})
        self.assertEqual({r["permission"] for r in rows}, {""})
        names = {r["table"] for r in rows}
        for t in ("iso_hub_prices_history", "price_board_latest", "news_index", "nyiso_dam_zone_prices", "datacenter_projects"):
            self.assertIn(t, names)
        for t in ("fred_daily_spot_prices", "fred_treasury_yields", "frb_treasury_yields", "eia_fuel_spot_prices", "pjm_rpm_capacity_prices"):
            self.assertNotIn(t, names)
        # today nothing is held: the rule begins on 20 October 2026
        self.assertEqual(ls.held_grids("2026-10-13"), set())
        self.assertEqual(sorted(ls.held_grids("2026-10-20")), ["ISO-NE", "MISO", "NYISO"])

    def test_the_sites_copy_says_the_same(self):
        with open(os.path.join(ROOT, "site", "data", "license_status.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["from"], "2026-10-20")
        self.assertEqual(set(d["tables"]), {r["table"] for r in ls.rows()})
        self.assertEqual({v["status"] for v in d["tables"].values()}, {"license needed"})
        self.assertEqual(d["tables"]["iso_hub_prices_history"]["publishers"], ["ISO-NE", "MISO", "NYISO"])

    def test_the_status_command_keeps_a_recorded_permission(self):
        lines = licenses.status_lines()
        self.assertEqual(len(lines), 40)
        self.assertTrue(all(v != licenses.PUBLIC for _, v, _ in lines))
        self.assertIn("iso_hub_prices_history", {t for t, _, _ in lines})
        # write_status against temporary paths: a permission a person recorded survives a rebuild
        tmp_status, tmp_site = os.path.join(self.tmp, "s.csv"), os.path.join(self.tmp, "s.json")
        with open(tmp_status, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=licenses.STATUS_COLS, lineterminator="\n")
            w.writeheader()
            w.writerow({"table": "news_index", "status": "permission recorded", "from": "2026-10-20", "publishers": "Bloomberg",
                        "verdict": "needs written permission", "permission": "granted 2026-10-15", "permission_ref": "runs/x", "note": "n"})
        saved = licenses.STATUS, licenses.SITE_STATUS
        try:
            licenses.STATUS, licenses.SITE_STATUS = tmp_status, tmp_site
            out = {r["table"]: r for r in licenses.write_status(today="2026-10-13")}
        finally:
            licenses.STATUS, licenses.SITE_STATUS = saved
        self.assertEqual(out["news_index"]["status"], "permission recorded")
        self.assertEqual(out["news_index"]["permission"], "granted 2026-10-15")
        self.assertEqual(out["iso_hub_prices_history"]["status"], "license needed")
        self.assertEqual(len(out), 40)
        self.assertEqual(json.load(open(tmp_site, encoding="utf-8"))["written"], "2026-10-13")

    def test_the_board_and_the_data_page_read_the_status(self):
        bp = src("warehouse", "derived", "board_page.py")
        self.assertIn("import license_status as ls", bp)
        self.assertEqual(bp.count("held = ls.held_grids()"), 2)  # the power rows and the ancillary services
        self.assertIn('b.grey("power", f"{iso}:{node}|{kind}", f"{grid} {HUB_WORDS.get(node, node)}", "licensed", ls.note(grid)', bp)
        page = src("site", "app", "data", "page.tsx")
        self.assertIn('from "@/lib/license"', page)
        self.assertIn("licenseNeeded(r.table_name)", page)
        ts = src("site", "lib", "license.ts")
        self.assertIn('import status from "@/data/license_status.json"', ts)
        self.assertIn('export const LICENSE_NEEDED = "license needed"', ts)
        self.assertIn("utcDay(now) >= r.from", ts)


class NoDashes(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for f in ("warehouse/connectors/frb_treasury.py", "warehouse/metadata/retired_tables.csv", "warehouse/metadata/license_status.py",
                  "warehouse/metadata/license_status.csv", "warehouse/metadata/build_coverage.py", "warehouse/derived/board_page.py",
                  "scripts/licenses.py", "site/lib/license.ts", "site/app/data/page.tsx", "site/data/license_status.json",
                  "docs/methods/price_board.md", "package/llms.txt", "tests/test_session207.py"):
            self.assertNotIn(chr(0x2014), src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
