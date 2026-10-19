"""Session 293: the problem sets for a class (Samuel's ruling 8a of 14 October 2026).

Energy Research Warehouse (ERW). No network, no model.
A dated edition of each set beside the live one: its numbers frozen with its date (site/data/problem_editions/), a
students' copy without answers, a teacher's copy with them, and the rows each question needs in its download
(site/public/problems/<date>/). The live sets still rebuild from the newest data.

    python -m unittest tests.test_session293 -v
"""

import csv
import io
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheEdition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(src("site", "data", "problem_editions", "index.json"))["editions"]
        cls.ed = json.loads(src("site", "data", "problem_editions", f"{cls.index[0]}.json"))

    def test_held_and_dated(self):
        self.assertIn("2026-10-15", self.index)
        self.assertEqual(self.index, sorted(self.index, reverse=True))
        self.assertEqual(self.ed["date"], self.index[0])
        self.assertRegex(self.ed["built_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_all_five_sets_of_five(self):
        self.assertEqual([s["slug"] for s in self.ed["sets"]], ["know-your-grid", "prices-and-your-bill", "when-the-grid-broke", "storage-and-taxes", "networks-and-money"])
        for s in self.ed["sets"]:
            self.assertEqual(len(s["questions"]), 5, s["slug"])
            for q in s["questions"]:
                self.assertTrue(any(isinstance(p, dict) for p in q["answer"]), q["id"])

    def test_each_question_has_its_rows(self):
        for s in self.ed["sets"]:
            for q in s["questions"]:
                path = os.path.join(SITE, "public", *q["csv"].strip("/").split("/"))
                self.assertTrue(os.path.exists(path), path)
                with open(path, encoding="utf-8") as f:
                    lines = f.read().splitlines()
                self.assertTrue(lines[0].startswith(f"# ERW problem sets, the edition of {self.ed['date']}"))
                body = [ln for ln in lines if not ln.startswith("#")]
                rows = list(csv.DictReader(io.StringIO("\n".join(body))))
                self.assertEqual(len(rows), q["rows"], q["csv"])
                self.assertGreater(len(rows), 0, q["csv"])
                for r in rows:
                    self.assertTrue(r["note"] == "computed" or r["source"] in q["tables"] or r["source"] in ("cost_of_power_monthly", "eia_fuel_spot_prices"), (q["id"], r["source"]))
                self.assertNotIn(chr(0x2014), "\n".join(lines))

    def test_the_rows_give_back_the_answer(self):
        # set A question 1: the two peaks are the largest of the 24 hours of each grid in the download
        s = next(x for x in self.ed["sets"] if x["slug"] == "know-your-grid")
        q = s["questions"][0]
        with open(os.path.join(SITE, "public", *q["csv"].strip("/").split("/")), encoding="utf-8") as f:
            rows = list(csv.DictReader(io.StringIO("\n".join(ln for ln in f.read().splitlines() if not ln.startswith("#")))))
        peaks = [p["v"] for p in q["answer"] if isinstance(p, dict)][:2]
        for ent, peak in zip(("eia930:ERCO", "eia930:CISO"), peaks):
            vals = [float(r["value"]) for r in rows if r["entity"] == ent]
            self.assertEqual(len(vals), 24)
            self.assertEqual(max(vals), peak)


class ThePages(unittest.TestCase):
    def test_students_copy_has_no_answers(self):
        p = src("site", "app", "learn", "problems", "[slug]", "[edition]", "page.tsx")
        self.assertNotIn("q.answer", p)
        self.assertNotIn("q.steps", p)
        self.assertIn("<a href={q.csv} download data-rows={q.rows}>", p)
        self.assertIn("teacherPath(slug, d)", p)

    def test_teachers_copy_has_them_and_prints(self):
        p = src("site", "app", "learn", "problems", "[slug]", "[edition]", "teacher", "page.tsx")
        self.assertIn("<FrozenParts parts={q.answer} />", p)
        self.assertIn("<PrintButton", p)
        self.assertIn("window.print()", src("site", "app", "learn", "problems", "PrintButton.tsx"))

    def test_the_live_set_and_the_index_link_the_edition(self):
        self.assertIn("data-editions", src("site", "app", "learn", "problems", "[slug]", "page.tsx"))
        self.assertIn("editionPath(s.slug, editions()[0])", src("site", "app", "learn", "problems", "page.tsx"))
        self.assertIn("<Num check={p.k}", src("site", "app", "learn", "problems", "[slug]", "page.tsx"))   # the live set is still checked

    def test_frozen_figures_carry_no_live_check(self):
        f = src("site", "app", "learn", "problems", "Frozen.tsx")
        self.assertNotIn("<Num", f)
        self.assertIn("data-frozen={p.k}", f)

    def test_the_builder(self):
        b = src("site", "scripts", "build-problem-edition.mjs")
        self.assertIn('await import("@/lib/problems")', b)
        self.assertIn('"x-erw-check": "1"', b)
        self.assertIn("## Dated editions, the teacher's copy and the rows (session 293", src("docs", "methods", "problem_sets.md"))


if __name__ == "__main__":
    unittest.main()
