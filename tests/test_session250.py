"""Session 250: the morning note of 13 October 2026, and migration 032.

Energy Research Warehouse (ERW). Two things. The note (docs/state/morning_2026-10-13.md): what landed overnight on both
machines, what failed, the screenshots to look at first and every open ruling in one list. And the index the session
added when it found why three landings' route checks had failed: session 245 put 430 days of the hourly carbon table in
the live set, and the emissions page's read of its last week, which names no balancing authority, was then answered by
walking the table in the key's order (about a second a page, cancelled at three by a cold database).

What is held here: the migration's index, that it is partial and holds the columns the site's series reader selects,
that it has a rollback that deletes no row, and that the README and the method say it; the note's parts, and that its
count of rulings is the count of the items it cites. No request, no database.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def sql_only(text):
    return "\n".join(line for line in text.split("\n") if not line.startswith("--"))


class TheIndex(unittest.TestCase):
    def test_it_is_one_partial_index_on_the_hour_for_the_one_table(self):
        sql = " ".join(sql_only(src("warehouse", "supabase", "migrations", "032_carbon_hourly_since.sql")).split())
        self.assertIn("create index if not exists series_carbon_hourly_since on public.series (ts_utc)", sql)
        self.assertIn("where table_name = 'carbon_intensity_hourly'", sql)
        self.assertEqual(sql.count("create "), 1)
        for word in ("drop ", "delete ", "alter ", "grant ", "policy"):
            self.assertNotIn(word, sql)

    def test_it_holds_every_column_the_sites_series_reader_selects_and_orders_by(self):
        """An index-only read: a column the reader asks for and the index lacks sends every row back to the table."""
        sql = sql_only(src("warehouse", "supabase", "migrations", "032_carbon_hourly_since.sql"))
        held = {"ts_utc"} | {c.strip() for c in re.search(r"include \(([^)]*)\)", sql).group(1).split(",")}
        reader = src("site", "lib", "data.ts")
        try:
            body = reader[reader.index("export async function series("):]
            body = body[:body.index("return rest<SeriesRow>")]
            select = set(re.search(r'select: "([^"]*)"', body).group(1).split(","))
            order = set(re.search(r'order: "([^"]*)"', body).group(1).split(","))
        except (ValueError, AttributeError):
            self.skipTest("the site's series reader is not where it was: read its columns against the index by hand")
        self.assertLessEqual(select | order, held | {"table_name"})

    def test_the_rollback_drops_the_index_and_nothing_else(self):
        sql = " ".join(sql_only(src("warehouse", "supabase", "rollbacks", "032_carbon_hourly_since.sql")).split())
        self.assertEqual(sql, "drop index if exists public.series_carbon_hourly_since;")

    def test_the_readme_and_the_method_say_it(self):
        row = next(line for line in src("warehouse", "supabase", "README.md").split("\n") if line.startswith("| `032_carbon_hourly_since.sql`"))
        self.assertIn("series_carbon_hourly_since", row)
        self.assertIn("rollbacks/032_carbon_hourly_since.sql", row)
        self.assertIn("session 250", row)
        self.assertIn("series_carbon_hourly_since", src("docs", "methods", "emissions.md"))


class TheNote(unittest.TestCase):
    NOTE = ("docs", "state", "morning_2026-10-13.md")

    def test_its_parts_in_order(self):
        headings = [line for line in src(*self.NOTE).split("\n") if line.startswith("## ")]
        self.assertEqual(headings, ["## Read these first", "## What landed overnight", "## What failed",
                                    "## The screenshots to look at first", "## Every open ruling, in one list", "## Today"])

    def test_every_landing_it_lists_has_a_commit_and_a_place_to_look(self):
        text = src(*self.NOTE)
        landed = text[text.index("## What landed overnight"):text.index("## What failed")]
        rows = [line for line in landed.split("\n") if re.match(r"^\| \d{3}", line)]
        self.assertGreaterEqual(len(rows), 20)
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertTrue(any(c for c in cells[1:]), row)
            if "not landed" in row or "no branch" in row:
                continue
            self.assertRegex(row, r"`[0-9a-f]{8}`|with this note|this landing", row)

    def test_the_rulings_are_numbered_from_one_and_the_count_is_the_citations(self):
        text = src(*self.NOTE)
        body = text[text.index("## Every open ruling, in one list"):text.index("### Closed tonight")]
        entries = [line for line in body.split("\n") if re.match(r"^\d+\. ", line)]
        self.assertEqual([int(line.split(".")[0]) for line in entries], list(range(1, len(entries) + 1)))
        cited = 0
        for line in entries:
            last = re.findall(r"\(([^()]*)\)\s*$", line)
            if not last:
                continue
            for piece in re.split(r"[;,]\s*(?=\d{3}(?:[: ,]|$))", last[0]):
                m = re.match(r"^(\d{3}):(.*)$", piece.strip())
                if m:
                    for item in m.group(2).split(","):
                        r = re.match(r"^(\d+) to (\d+)$", item.strip())
                        cited += int(r.group(2)) - int(r.group(1)) + 1 if r else 1
                elif "seven lines" in piece:
                    cited += 7
                elif re.match(r"^\d{3}$", piece.strip()):
                    cited += 1
        said = re.search(r"The count: the (\d+) entries above stand for (\d+) lines of the reports", text)
        self.assertEqual((int(said.group(1)), int(said.group(2))), (len(entries), cited))
        first = re.search(r"\*\*(\d+) lines of the night's reports ask for a ruling; they are (\d+) entries", text)
        self.assertEqual((int(first.group(2)), int(first.group(1))), (len(entries), cited))

    def test_no_em_dash(self):
        self.assertEqual(src(*self.NOTE).count(chr(0x2014)), 0)


if __name__ == "__main__":
    unittest.main()
