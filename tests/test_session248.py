"""Session 248: the license table for 21 October 2026.

Energy Research Warehouse (ERW). docs/state/licenses_2026-10-21.md and site/data/license_status.json: every table
public, "license needed" or internal, and the pages each one darkens. The public day moved from 20 to 21 October
(Samuel's ruling of 12 October 2026, night; docs/roadmap.md), and the status file's day moves with it.

What is held here: the three statuses and the rule for each; held whole or by grid; when a page is dark and when
partly; that the day moved in the code, the status file and the site's file together and a recorded permission's own
day is left as a person wrote it; that the document and the site's file are what the sources give (the script's own
check); and that the key the site reads is as session 207 left it. No request.
"""

import csv
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("scripts", os.path.join("warehouse", "metadata")):
    sys.path.insert(0, os.path.join(ROOT, p))
import license_state as ls  # noqa: E402
import licenses  # noqa: E402
import page_tables  # noqa: E402

EM = chr(0x2014)
DAY = "2026-10-21"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


class TheThreeStatuses(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        p = lambda n: os.path.join(self.d.name, n)  # noqa: E731
        self.cov, self.status, self.tables = p("coverage.csv"), p("license_status.csv"), p("license_tables.csv")
        write_csv(self.cov, ["table", "license", "sector"], [
            {"table": "eia_fuel_spot_prices", "license": "public", "sector": "gas"}, {"table": "iso_hub_prices_history", "license": "public", "sector": "power"},
            {"table": "news_index", "license": "public", "sector": "news"}, {"table": "energy_projects", "license": "public", "sector": "power"},
            {"table": "isone_as_prices", "license": "internal", "sector": "power"}, {"table": "news_stories", "license": "internal", "sector": "news"}])
        write_csv(self.status, licenses.STATUS_COLS, [
            {"table": "iso_hub_prices_history", "status": "license needed", "from": DAY, "publishers": "ISO-NE; MISO; NYISO", "verdict": "needs written permission"},
            {"table": "news_index", "status": "license needed", "from": DAY, "publishers": "Bloomberg; ISO-NE", "verdict": "needs written permission"},
            {"table": "energy_projects", "status": "permission recorded", "from": DAY, "publishers": "ISO-NE", "verdict": "needs written permission",
             "permission": "a letter", "permission_ref": "2026-10-15"}])
        write_csv(self.tables, ["table", "publishers", "how"], [
            {"table": "eia_fuel_spot_prices", "publishers": "EIA"}, {"table": "iso_hub_prices_history", "publishers": "CAISO; ISO-NE; MISO; NYISO; SPP"},
            {"table": "news_index", "publishers": "Bloomberg; ISO-NE"}, {"table": "energy_projects", "publishers": "EIA; ISO-NE"},
            {"table": "isone_as_prices", "publishers": "ISO-NE"}, {"table": "news_stories", "publishers": "Bloomberg"}])
        self.st = ls.table_status(self.cov, self.status, self.tables)

    def test_every_table_has_one_of_three(self):
        self.assertEqual({t: v["status"] for t, v in self.st.items()}, {
            "eia_fuel_spot_prices": "public", "iso_hub_prices_history": "license needed", "news_index": "license needed",
            "energy_projects": "public",          # a permission is recorded: public again, and the table says so
            "isone_as_prices": "internal", "news_stories": "internal"})
        self.assertEqual(self.st["energy_projects"]["permission"], "a letter")
        # an internal table is internal whatever the status file says of it: it was never shown
        self.assertEqual(self.st["isone_as_prices"]["hold"], "")

    def test_held_by_grid_when_only_grid_operators_decide_and_whole_otherwise(self):
        self.assertEqual(self.st["iso_hub_prices_history"]["hold"], "by grid")
        self.assertEqual(self.st["iso_hub_prices_history"]["publishers"], ["ISO-NE", "MISO", "NYISO"])       # the deciding ones, not every publisher of the table
        self.assertEqual(self.st["news_index"]["hold"], "whole")                                               # a news outlet among them: the table is held whole
        # the rule is the site's own (site/lib/license.ts, licenseByGrid): every deciding publisher is a grid operator
        self.assertIn("licenseByGrid", src("site", "lib", "license.ts"))
        self.assertEqual(ls.GRIDS, {"CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"})

    def test_a_page_is_dark_only_when_every_table_it_reads_is_held_whole(self):
        pages = {
            "/digest": {"label": "Digest", "tables": {"news_index": ["app/digest/page.tsx"]}, "declared": []},
            "/deals": {"label": "Deals", "tables": {"news_index": ["x"], "news_stories": ["x"]}, "declared": []},
            "/prices": {"label": "Prices", "tables": {"iso_hub_prices_history": ["x"]}, "declared": []},
            "/mix": {"label": "Mix", "tables": {"news_index": ["x"]}, "declared": ["eia_fuel_spot_prices"]},
            "/severance": {"label": "Severance", "tables": {"eia_fuel_spot_prices": ["x"], "energy_projects": ["x"]}, "declared": []},
            "/about": {"label": "", "tables": {}, "declared": []},
            "/gone": {"label": "Gone", "error": "no page file"}}
        got = {p["route"]: p for p in ls.page_rows(self.st, pages)}
        self.assertEqual({r: p["dark"] for r, p in got.items()}, {
            "/digest": "all",        # its one table is held whole
            "/deals": "all",         # a held table and an internal one: nothing is left to show
            "/prices": "part",       # held by grid: the other grids' rows stay
            "/mix": "part",          # one held, one public (named in the menu's line)
            "/severance": "none", "/about": "none"})
        self.assertNotIn("/gone", got)
        self.assertEqual(got["/about"]["label"], "About")
        self.assertEqual(got["/deals"]["internal"], ["news_stories"])


class TheDayMoved(unittest.TestCase):
    def test_the_public_day_is_21_october_in_the_code_and_in_both_files(self):
        self.assertEqual(licenses.STATUS_FROM, DAY)       # the ruling of 12 October 2026, night (docs/roadmap.md, "public day")
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(rows)
        self.assertEqual({r["from"] for r in rows if not r["permission"]}, {DAY})
        site = json.loads(src("site", "data", "license_status.json"))
        self.assertEqual(site["from"], DAY)
        self.assertTrue(all(v["from"] == DAY for v in site["tables"].values() if v["status"] == "license needed"))

    def test_moving_the_day_moves_a_row_without_a_permission_and_leaves_a_recorded_one(self):
        self.assertEqual(licenses.moved_day({"from": "2026-10-20", "permission": ""}), DAY)
        self.assertEqual(licenses.moved_day({"from": "", "permission": ""}), DAY)
        self.assertEqual(licenses.moved_day({}), DAY)
        self.assertEqual(licenses.moved_day({"from": "2026-10-20", "permission": "a letter of 15 October"}), "2026-10-20")   # a person's row is a person's
        self.assertEqual(licenses.moved_day({"from": "2026-11-01", "permission": ""}), "2026-11-01")                          # a later day someone set stands

    def test_the_readers_follow_the_file_not_a_date_of_their_own(self):
        import license_status
        self.assertTrue(license_status.needed("iso_hub_prices_history", DAY))
        self.assertFalse(license_status.needed("iso_hub_prices_history", "2026-10-20"))        # a day earlier: nothing is held yet
        self.assertIn("status.from", src("site", "lib", "license.ts"))                         # the site's day is the file's, not one written in its code


class TheTableAsWritten(unittest.TestCase):
    def setUp(self):
        self.site = json.loads(src("site", "data", "license_status.json"))
        self.doc = src("docs", "state", f"licenses_{DAY}.md")
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            self.cov = {r["table"]: r for r in csv.DictReader(f)}

    def test_every_table_it_was_written_from_is_in_both_with_one_status(self):
        # Held to the files as they were written, not to coverage as it stands on a later day: a session that adds a
        # table runs `python scripts/licenses.py state` (its own --check says when), and until then the table written
        # here is a day old, not wrong. So a table coverage has gained since is allowed; one written here is checked.
        self.assertGreaterEqual(len(self.site["all"]) + self.site["internal_tables"], 197)
        self.assertEqual({v["status"] for v in self.site["all"].values()}, {"public", "license needed"})
        for t, v in self.site["all"].items():
            self.assertIn(f"| `{t}`", self.doc, t)
            if t in self.cov:
                self.assertEqual(self.cov[t]["license"], "public", t)
            self.assertEqual(v["status"] == "license needed", t in self.site["tables"] and self.site["tables"][t]["status"] == "license needed", t)
        n = {s: sum(1 for v in self.site["all"].values() if v["status"] == s) for s in ("public", "license needed")}
        total = len(self.site["all"]) + self.site["internal_tables"]
        self.assertIn(f"- **{total} tables: {n['public']} public, {n['license needed']} \"license needed\", {self.site['internal_tables']} internal.**", self.doc)

    def test_an_internal_table_is_counted_in_the_sites_file_and_never_named(self):
        # tests/test_session149.py holds one internal table's name out of every file under site/, and this session's
        # first build put it in this file. The file names no internal table now: it has their count, and the document
        # under docs/state/ has their names
        text = src("site", "data", "license_status.json")
        internal = sorted(t for t, r in self.cov.items() if r["license"] != "public")
        self.assertGreater(len(internal), 20)
        for t in internal:
            self.assertNotIn(f'"{t}"', text, t)
        section = self.doc.split("## Every internal table", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(section.count("\n| `"), self.site["internal_tables"])
        self.assertTrue(all(isinstance(p["internal"], int) for p in self.site["pages"].values()))

    def test_the_key_the_site_reads_is_as_session_207_left_it(self):
        self.assertEqual(set(self.site), {"from", "written", "what", "tables", "all", "internal_tables", "pages"})
        for t, v in self.site["tables"].items():
            self.assertEqual(set(v), {"status", "from", "publishers"}, t)
        self.assertIn("status.tables", src("site", "lib", "license.ts"))        # the one key the site reads; "all" and "pages" are beside it

    def test_each_dark_page_is_named_with_the_tables_that_darken_it(self):
        pages = self.site["pages"]
        dark = sorted(r for r, p in pages.items() if p["dark"] == "all")
        part = sorted(r for r, p in pages.items() if p["dark"] == "part")
        self.assertIn(f"- **{len(dark)} pages go dark and {len(part)} go partly dark.**", self.doc)
        for r in dark + part:
            self.assertIn(f"| `{r}` |", self.doc, r)
            self.assertTrue(pages[r]["license_needed"], r)
            for t in pages[r]["license_needed"]:
                self.assertIn(r, self.site["all"][t]["pages"], (r, t))
        for r in dark:                       # nothing public is left on a dark page, and nothing it reads is held by grid only
            self.assertEqual(pages[r]["public"], 0, r)
            self.assertTrue(all(self.site["all"][t]["hold"] == "whole" for t in pages[r]["license_needed"]), r)

    def test_the_reader_of_pages_reads_names_from_a_pages_own_code(self):
        # On a stand-in site, so that a page the code machine changes tonight cannot turn this red
        with tempfile.TemporaryDirectory() as d:
            site = os.path.join(d, "site")
            for rel, text in {
                "lib/pages.ts": 'export const PAGES = [\n  { href: "/prices", label: "Prices", line: "Hub prices.", tables: "ISO price tables, eia_fuel_spot_prices" },\n'
                                '  { href: "/mix", label: "Mix", line: "The mix.", tables: "" },\n];\n',
                "lib/data.ts": 'export async function hubs() { return series("iso_dam_hub_prices"); }\nexport async function other() { return series("news_index"); }\n',
                "app/prices/page.tsx": 'import { hubs } from "@/lib/data";\nimport board from "@/data/board.json";\n// news_stories is named in a comment only\nexport default function P() { return null; }\n',
                "app/mix/page.tsx": 'import { other } from "../../lib/data";\nexport default function M() { return null; }\n',
                "app/page.tsx": "export default function H() { return null; }\n",
                "data/board.json": '{"sources": ["EIA (eia_crude_stream_prices)"], "rows": []}\n',
            }.items():
                os.makedirs(os.path.dirname(os.path.join(site, *rel.split("/"))), exist_ok=True)
                with open(os.path.join(site, *rel.split("/")), "w", encoding="utf-8") as f:
                    f.write(text)
            cov = os.path.join(d, "coverage.csv")
            write_csv(cov, ["table", "license"], [{"table": t, "license": "public"} for t in
                                                  ("iso_dam_hub_prices", "news_index", "news_stories", "eia_fuel_spot_prices", "eia_crude_stream_prices")])
            got = page_tables.read(site, cov)
        # the function the page imports, the table its data file names, the table the menu's line names; not the
        # other function of the same module, and not a name in a comment
        self.assertEqual(page_tables.tables_of(got["/prices"]), ["eia_crude_stream_prices", "eia_fuel_spot_prices", "iso_dam_hub_prices"])
        self.assertEqual(page_tables.tables_of(got["/mix"]), ["news_index"])
        self.assertEqual(page_tables.tables_of(got["/"]), [])
        self.assertEqual(got["/about"].get("error"), "no page file")

    def test_the_scripts_check_says_when_the_document_is_not_what_the_sources_give(self):
        with tempfile.TemporaryDirectory() as d:
            doc, site = os.path.join(d, "licenses.md"), os.path.join(d, "license_status.json")
            with open(site, "w", encoding="utf-8") as f:
                json.dump({k: self.site[k] for k in ("from", "written", "what", "tables")}, f)
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(ls.write(day=DAY, out_doc=doc, site_status=site, branch="a test", written="2026-10-13"), 0)
                self.assertEqual(ls.write(day=DAY, check=True, out_doc=doc, site_status=site), 0)        # as written: it agrees
                with open(doc, "a", encoding="utf-8") as f:
                    f.write("a line a person added\n")
                self.assertEqual(ls.write(day=DAY, check=True, out_doc=doc, site_status=site), 1)        # the document moved
            self.assertIn("is not what the four sources give today", out.getvalue())

    def test_no_em_dash_and_the_words_of_the_ruling(self):
        for f in ("scripts/license_state.py", "scripts/page_tables.py", "scripts/licenses.py", f"docs/state/licenses_{DAY}.md", "tests/test_session248.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)
        self.assertTrue(self.doc.startswith("# The license table for 21 October 2026\n"))
        self.assertTrue(re.search(r"The public day moved from 20 to 21 October by the ruling of 12 October 2026, night", self.doc))


if __name__ == "__main__":
    unittest.main()
