"""Session 330 (the chain of 20 October 2026, night): /map and /storage finished to the five tools' standard, lighter.
Each page offers the tables it is drawn from (session 328's shared line) and the two notes say what the pages draw
today. Energy Research Warehouse (ERW)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDownloads(unittest.TestCase):
    def test_the_map_offers_the_four_tables_its_file_is_built_from(self):
        page = src("site", "app", "map", "page.tsx")
        self.assertIn("<TableDownloads tables={(mapJson as unknown as MapFile).tables} />", page)
        tables = json.loads(src("site", "data", "map.json"))["tables"]
        self.assertEqual(sorted(tables), sorted(["eia860m_operating_generators", "eia860m_planned_generators", "energy_projects", "datacenter_facilities"]))

    def test_each_storage_tab_offers_its_tables(self):
        page = src("site", "app", "storage", "page.tsx")
        self.assertIn('<TableDownloads tables={tab === "buildout" ? ["storage_buildout_monthly"] : tab === "owners" ? ["storage_owners_monthly"]', page)
        self.assertIn(': ["storage_capacity", "storage_daily_cycle", "eia930_all_storage", "caiso_battery_storage"]} />', page)
        # the fleet tab's list is its source line's
        self.assertIn('<SourceLine tables={["storage_capacity", "storage_daily_cycle", "eia930_all_storage", "caiso_battery_storage"]}', page)


class TheNotes(unittest.TestCase):
    def test_both_notes_say_what_the_pages_draw_today(self):
        self.assertIn("### The page as it stands (session 330, 20 October 2026)", src("docs", "methods", "energy_projects.md"))
        self.assertIn("## The page `/storage` as it stands (session 330, 20 October 2026)", src("docs", "methods", "storage.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "map", "page.tsx"), ("site", "app", "storage", "page.tsx"), ("docs", "methods", "energy_projects.md"),
                      ("docs", "methods", "storage.md"), ("tests", "test_session330.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
