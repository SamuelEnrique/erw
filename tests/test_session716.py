"""Session 716: the All grids tab reads nothing from the database. No file of the tab imports the site's database
reader (lib/supabase.ts) or the live set's reads; it reads only the site's own files. The measurements are in
docs/reviews/siting-reads-2026-10-22.md. No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILES = [("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "app", "cost-of-power", "AllGridsForm.tsx"),
         ("site", "app", "cost-of-power", "AllGridsNodes.tsx"), ("site", "lib", "siting.ts"), ("site", "lib", "sitingdata.ts")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class NoRead(unittest.TestCase):
    def test_no_file_of_the_tab_imports_a_database_reader(self):
        for p in FILES:
            imports = re.findall(r'^import[^;]*from "([^"]+)"', src(*p), re.M)
            for m in imports:
                self.assertNotIn("supabase", m, (p, m))
                self.assertNotIn("read", m.split("/")[-1].lower().replace("readme", ""), (p, m))

    def test_the_tab_s_data_are_site_files(self):
        d = src("site", "lib", "sitingdata.ts")
        for f in ("@/data/siting/nodes.json", "@/data/siting/ercot_4cp.json", "@/data/siting/capacity.json", "@/data/siting/connect.json",
                  "@/data/siting/headroom.json", "@/data/siting/carbon.json", "@/data/siting/utility.json"):
            self.assertIn(f, d)

    def test_the_measurements_are_written(self):
        r = src("docs", "reviews", "siting-reads-2026-10-22.md")
        self.assertIn("The tab reads nothing from the database", r)
        self.assertNotIn(chr(0x2014), r)


if __name__ == "__main__":
    unittest.main()
