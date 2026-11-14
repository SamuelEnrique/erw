"""Session 5300: the large-load research pass (docs/research/large_load/), every row cited.

Energy Research Warehouse (ERW). No network, no model, no build. The research CSV of US utilities' large-load
connection rules (utilities_<date>.csv, built by build_csv.py from rows/*.json) must hold, row by row:
- a source URL and the date it was read;
- in each of the eleven value fields either a value with its cite (a page or section, and the words in quotes), or
  "not published", or "held: <registry>/<file>.yaml" naming a file of window A's registries that exists, or
  "see row: <rule name>" naming another row of the same utility;
- a status of proposed, approved or in effect;
- a license of public or internal, and a notes file that exists;
- no em or en dash in any file of the folder.

    python -m unittest tests.test_session5300_large_load_research -v
"""

import csv
import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FOLDER = os.path.join(ROOT, "docs", "research", "large_load")
FIELDS = ("threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
          "connection_timeline", "queue_size")
STATUSES = {"proposed", "approved", "in effect", "denied", "withdrawn"}  # a proposal a commission rejected, or the filer withdrew
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_OR_DATE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")  # a status date the document states only to the month
# One cite as build_csv.py writes it: an optional other document's address and read date, then the place (a page,
# a section or heading), then the words in quotes. "the document" is what build_csv.py writes when neither a page
# nor a section was given: a value's cite must name one.
CITE = re.compile(r'^(?:(?P<url>https?://\S+) \(read [^)]*\) )?(?P<where>[^"]+?): "')


def placed(cite):
    """Every cite in a field (joined by ' | ') names a page or a section and quotes words."""
    parts = re.split(r'(?<=") \| (?=(?:https?://|p\. |[^"]+?: "))', cite)
    for part in parts:
        m = CITE.match(part)
        if not m or m.group("where").strip() in ("", "the document"):
            return False
    return True


def csv_files():
    return sorted(glob.glob(os.path.join(FOLDER, "utilities_*.csv")))


def read_rows(path):
    with open(path, encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def valued(v):
    v = (v or "").strip()
    return v and v != "not published" and not v.startswith("held: ") and not v.startswith("see row: ")


class LargeLoadResearch(unittest.TestCase):
    def setUp(self):
        self.files = csv_files()
        if not self.files:
            self.skipTest("no utilities_<date>.csv yet")
        self.rows = read_rows(self.files[-1])

    def test_there_are_rows(self):
        self.assertGreater(len(self.rows), 0)

    def test_every_row_has_a_source_url_and_a_date_read(self):
        for r in self.rows:
            self.assertRegex(r["source_url"], r"^https?://", r["row_id"])
            self.assertRegex(r["date_read"], DATE, r["row_id"])

    def test_every_field_is_a_value_or_not_published_or_a_pointer(self):
        for r in self.rows:
            for f in FIELDS + ("docket",):
                v = (r[f] or "").strip()
                self.assertTrue(v, f"{r['row_id']} {f} is empty")
                if valued(v):
                    cite = r[f + "_cite"]
                    self.assertIn('"', cite, f"{r['row_id']} {f}: a value without quoted words")
                    self.assertTrue(placed(cite), f"{r['row_id']} {f}: a cite without a page or section: {cite[:200]}")

    def test_status_is_one_of_three_and_dated_or_not_published(self):
        for r in self.rows:
            self.assertIn(r["status"], STATUSES, r["row_id"])
            sd = r["status_date"]
            self.assertTrue(MONTH_OR_DATE.match(sd) or sd == "not published", f"{r['row_id']} status_date {sd}")
            self.assertIn('"', r["status_cite"], f"{r['row_id']}: the status has no quoted words")

    def test_a_held_pointer_names_a_registry_file_that_exists(self):
        for r in self.rows:
            for f in FIELDS + ("docket",):
                v = (r[f] or "").strip()
                if v.startswith("held: "):
                    target = v[len("held: "):].split()[0]
                    path = os.path.join(ROOT, "warehouse", "sources", target)
                    self.assertTrue(os.path.exists(path), f"{r['row_id']} {f}: {target} is not in a registry")

    def test_a_see_row_pointer_names_a_row_of_the_same_group(self):
        # the same utility's row, or the group's row holding a figure a holding company states for several utilities
        names = {}
        for r in self.rows:
            names.setdefault(r["group"], set()).add(r["rule_name"])
        for r in self.rows:
            for f in FIELDS:
                v = (r[f] or "").strip()
                if v.startswith("see row: "):
                    self.assertIn(v[len("see row: "):], names[r["group"]], f"{r['row_id']} {f}")

    def test_license_and_notes_file(self):
        for r in self.rows:
            self.assertIn(r["license"], ("public", "internal"), r["row_id"])
            self.assertTrue(os.path.exists(os.path.join(FOLDER, r["notes_file"])), f"{r['row_id']} {r['notes_file']}")

    def test_the_csv_holds_every_checked_row(self):
        n = 0
        for fp in glob.glob(os.path.join(FOLDER, "rows", "*.json")):
            with open(fp, encoding="utf-8") as fh:
                n += len(json.load(fh).get("rows") or [])
        self.assertEqual(n, len(self.rows))

    def test_row_ids_are_unique(self):
        ids = [r["row_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))


CHANGES = {"filed", "approved", "in effect", "amended", "denied", "withdrawn", "suspended", "hearing set",
           "order issued", "other"}
LAW_STATUSES = {"introduced", "passed one chamber", "passed", "enacted", "in effect", "vetoed", "died"}


def latest(prefix):
    files = sorted(glob.glob(os.path.join(FOLDER, f"{prefix}_*.csv")))
    return read_rows(files[-1]) if files else None


class SecondAndThirdPasses(unittest.TestCase):
    def test_every_change_is_dated_and_cited(self):
        rows = latest("changes")
        if rows is None:
            self.skipTest("no changes_<date>.csv yet")
        for r in rows:
            self.assertRegex(r["source_url"], r"^https?://", r["change_id"])
            self.assertRegex(r["date_read"], DATE, r["change_id"])
            self.assertIn(r["change"], CHANGES, r["change_id"])
            self.assertTrue(MONTH_OR_DATE.match(r["date"]) or r["date"] == "not published", r["change_id"])
            self.assertTrue(placed(r["cite"]), f"{r['change_id']}: {r['cite'][:120]}")
            self.assertIn(r["license"], ("public", "internal"), r["change_id"])

    def test_every_law_is_read_in_its_own_text(self):
        rows = latest("legislation")
        if rows is None:
            self.skipTest("no legislation_<date>.csv yet")
        for r in rows:
            self.assertRegex(r["source_url"], r"^https?://", r["law_id"])
            self.assertRegex(r["date_read"], DATE, r["law_id"])
            self.assertIn(r["status"], LAW_STATUSES, r["law_id"])
            self.assertTrue(MONTH_OR_DATE.match(r["status_date"]) or r["status_date"] == "not published", r["law_id"])
            self.assertTrue(placed(r["status_cite"]), f"{r['law_id']}: {r['status_cite'][:120]}")
            if valued(r["threshold_mw"]):
                self.assertTrue(placed(r["threshold_mw_cite"]), r["law_id"])


class StableIdsAndPointers(unittest.TestCase):
    """Session 5304: row ids are stored in the rows and never move; a change points at a real row or registry file."""

    def rows_json(self):
        out = {}
        for fp in glob.glob(os.path.join(FOLDER, "rows", "*.json")):
            with open(fp, encoding="utf-8") as fh:
                for r in json.load(fh).get("rows") or []:
                    out[r.get("row_id")] = r
        return out

    def test_every_row_stores_its_id_and_the_csv_uses_it(self):
        files = csv_files()
        if not files:
            self.skipTest("no CSV")
        rj = self.rows_json()
        self.assertNotIn(None, rj)
        self.assertEqual(sorted(rj), sorted(r["row_id"] for r in read_rows(files[-1])))

    def test_a_change_points_at_a_row_of_its_utility_or_a_registry_file(self):
        rj = self.rows_json()
        for fp in glob.glob(os.path.join(FOLDER, "changes", "*.json")):
            with open(fp, encoding="utf-8") as fh:
                changes = json.load(fh).get("changes") or []
            for c in changes:
                aff = c["affects"].split()[0].rstrip(";")
                if aff == "new":
                    continue
                if aff.startswith(("large_load_tariffs/", "large_load_connection_rules/")):
                    self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "sources", aff)), aff)
                    continue
                self.assertIn(aff, rj, f"{fp}: {aff}")
                key = lambda s: re.sub(r"[^a-z]", "", s.lower())[:8]
                self.assertEqual(key(rj[aff]["utility"]), key(c["utility"]), f"{aff}: {c['utility']}")


class Audit(unittest.TestCase):
    """Session 5304: every finding of the independent audit has its resolution in the audit log."""

    def test_every_wrong_finding_is_resolved_in_the_log(self):
        logs = sorted(glob.glob(os.path.join(FOLDER, "audit_*.md")))
        reports = glob.glob(os.path.join(FOLDER, "audit", "*.json"))
        if not logs or not reports:
            self.skipTest("no audit yet")
        log = open(logs[-1], encoding="utf-8").read()
        resolved = {}
        for line in log.splitlines():
            m = re.match(r"^\| (A-\d+) \| ([a-z_0-9]+-\d\d) \| ([a-z_]+) \| (wrong|unclear) \| .* \| (fixed|not changed: .+|already right: .+) \|$", line)
            if m:
                resolved[(m.group(2), m.group(3))] = m.group(5)
        for fp in reports:
            with open(fp, encoding="utf-8") as fh:
                for row in json.load(fh).get("rows") or []:
                    for v in row.get("verdicts") or []:
                        if v.get("verdict") == "wrong":
                            self.assertIn((row["row_id"], v["field"]), resolved, f"{fp}: {row['row_id']} {v['field']}")


class NoDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_the_folder(self):
        for path in glob.glob(os.path.join(FOLDER, "**", "*"), recursive=True):
            if os.path.isdir(path) or not path.endswith((".csv", ".md", ".json", ".py")):
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("\u2014", text, path)
            self.assertNotIn("\u2013", text, path)


if __name__ == "__main__":
    unittest.main()
