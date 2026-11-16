"""Session 7200 (chain 302): the large-load rules page file, site/data/siting/large_load_rules.json.

The three tables are written into a temporary folder by their own connector from the committed research files (no
request, no model, no lock: a write outside warehouse/output), the page file is built from them, and the committed page
file must equal it. Then every value and cite the file prints is found in its table row; the counts by status equal
the tables'; no held row carries more than its id, name and place; no value of a held row or a withheld field of the
research file is anywhere in the page file; every EIA number the file maps to is one the tab's utility file names.
"""
import contextlib
import csv
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import large_load_research as llr  # noqa: E402
import large_load_rules_page as page  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "siting", "large_load_rules.json")
UTILITY_FILE = os.path.join(ROOT, "site", "data", "siting", "utility.json")
RESEARCH_RULES = os.path.join(ROOT, "docs", "research", "large_load", "utilities_2026-11-13.csv")


def research_rows(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(io.StringIO("".join(ln for ln in fh if not ln.startswith("#")))))


class ThePageFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw7200_")
        saved = (llr.ip.OUT_DIR, llr.ip.LOG_DIR)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = llr.main(["--out-dir", cls.tmp])
        finally:
            llr.ip.OUT_DIR, llr.ip.LOG_DIR = saved
        assert rc == 0, "the connector refused the committed research files"
        cls.built = page.build(cls.tmp)
        with open(SITE_FILE, encoding="utf-8") as fh:
            cls.file = json.load(fh)
        with open(SITE_FILE, encoding="utf-8") as fh:
            cls.text = fh.read()
        cls.tables = {t: page.rows_of(os.path.join(cls.tmp, f"{t}.csv")) for t in (page.RULES, page.CHANGES, page.LAWS)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_committed_file_is_the_build_of_the_committed_tables(self):
        # "built" is the builder's clock and "retrieved" the tables' own stamp: the test's tables are written now, the
        # committed file's on the day the data machine wrote them (the rows are the same research files' either way)
        strip = lambda d: {k: v for k, v in d.items() if k not in ("built", "retrieved")}
        self.assertEqual(strip(self.file), strip(self.built))
        for t in (page.RULES, page.CHANGES, page.LAWS):
            self.assertRegex(self.file["retrieved"][t], r"^2026\d{4}T\d{6}Z$")

    def test_every_value_and_cite_is_its_table_rows(self):
        rows = {r["x_row_id"]: r for r in self.tables[page.RULES]}
        n = 0
        for r in self.file["rules"]:
            t = rows[r["id"]]
            self.assertEqual((r["utility"], r["state"], r["status"], r["status_date"], r["docket"], r["url"]),
                             (t["x_utility"], t["x_state"], t["status"], t["x_status_date"], t["x_docket"], t["source_url"]))
            for f, c in r["fields"].items():
                if c["kind"] == "value" and not c.get("registry"):
                    self.assertEqual(c["v"], t[f"x_{f}"], (r["id"], f))
                    self.assertEqual(c["cite"], t[f"x_{f}_cite"], (r["id"], f))
                    n += 1
                elif c["kind"] == "not published":
                    self.assertEqual(t[f"x_{f}"], "not published", (r["id"], f))
        self.assertGreater(n, 300)
        changes = {r["x_change_id"]: r for r in self.tables[page.CHANGES]}
        for c in self.file["changes"]:
            t = changes[c["id"]]
            self.assertEqual((c["date"], c["what"], c["cite"], c["affects"], c["kind"]), (t["event_date"], t["x_what"], t["x_cite"], t["x_affects"], t["status"]))
        laws = {r["x_law_id"]: r for r in self.tables[page.LAWS]}
        for x in self.file["laws"]:
            t = laws[x["id"]]
            self.assertEqual((x["status"], x["bill"], x["requirements"], x["status_cite"]), (t["status"], t["x_bill"], t["x_requirements"], t["x_status_cite"]))

    def test_the_counts_by_status_are_the_tables(self):
        for key, table in (("rules", page.RULES), ("laws", page.LAWS)):
            want = {}
            for r in self.tables[table]:
                want[r["status"]] = want.get(r["status"], 0) + 1
            self.assertEqual(self.file["counts"][key], want)
        self.assertEqual(self.file["counts"]["changes"], len(self.tables[page.CHANGES]))
        self.assertEqual((len(self.file["rules"]), len(self.file["held_rules"]), len(self.file["changes"]), len(self.file["held_changes"]),
                          len(self.file["laws"]), len(self.file["held_laws"])), (100, 22, 94, 4, 27, 1))

    def test_a_held_row_is_its_name_and_place_only(self):
        for r in self.file["held_rules"]:
            self.assertEqual(set(r), {"id", "utility", "state", "region", "grid"})
        for r in self.file["held_changes"]:
            self.assertEqual(set(r), {"id", "utility"})
        for r in self.file["held_laws"]:
            self.assertEqual(set(r), {"id", "bill", "state"})

    def test_no_internal_value_is_in_the_file(self):
        """Every field value and cite of a held research row, and every withheld field of a public one, is absent."""
        # A held row's cite can be words a public row of the same table also prints (one PJM page lists every AEP company's
        # additions, and Kentucky Power's public row cites it whole): those words are the public table's, not the held row's.
        public = "\n".join(v for t in self.tables.values() for r in t for v in r.values() if v)
        checked, shared = 0, []
        for r in research_rows(RESEARCH_RULES):
            internal = r["license"] == "internal"
            fields = page.FIELDS if internal else [f for f in (r.get("internal_fields") or "").split(";") if f]
            for f in fields:
                for col in (f, f"{f}_cite"):
                    v = (r.get(col) or "").strip()
                    if len(v) < 40 or v.startswith(("not published", "held:", "see row:", "searched:")):
                        continue
                    if v in public:
                        shared.append((r["row_id"], col))
                        continue
                    self.assertFalse(json.dumps(v, ensure_ascii=False)[1:-1] in self.text, (r["row_id"], col))
                    checked += 1
            if internal:
                for col in ("rule_name", "quoted_clause", "notes", "source_url"):
                    v = (r.get(col) or "").strip()
                    if len(v) >= 40 and v not in public:
                        self.assertFalse(json.dumps(v, ensure_ascii=False)[1:-1] in self.text, (r["row_id"], col))
                        checked += 1
        self.assertGreater(checked, 100)
        self.assertLessEqual(len(shared), 4, shared)  # the words a public row prints too: few, and each one named here on a failure
        for r in self.file["rules"]:
            for f in r["withheld"]:
                self.assertEqual(r["fields"][f], {"kind": "withheld"}, (r["id"], f))

    def test_every_eia_number_is_one_the_tab_names(self):
        with open(UTILITY_FILE, encoding="utf-8") as fh:
            u = json.load(fh)
        nums = {v["number"] for v in u["by"].values()}
        for c in u["county"].values():
            nums |= {x["number"] for x in c["utilities"]}
            nums |= {x["number"] for x in (c.get("delivery") or {}).get("companies", [])}
        self.assertTrue(set(self.file["eia"]) <= nums, sorted(set(self.file["eia"]) - nums))
        ids = {r["id"] for r in self.file["rules"]} | {r["id"] for r in self.file["held_rules"]}
        for n, e in self.file["eia"].items():
            self.assertTrue(set(e["rules"]) <= ids, n)
            self.assertTrue(e["rules"] or e.get("none", "").startswith("No large-load rule found."), n)

    def test_a_queue_pointer_names_a_row_of_the_file(self):
        ids = {r["id"] for r in self.file["rules"]}
        held = {r["id"] for r in self.file["held_rules"]}
        for r in self.file["rules"]:
            c = r["fields"]["queue_size"]
            if c["kind"] == "see":
                self.assertIn(c["row"], held if c.get("held") else ids, r["id"])


if __name__ == "__main__":
    unittest.main()
