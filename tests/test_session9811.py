"""Session 9811: a row of a table held by grid is known by its id, whatever the table's shape (site/lib/supabase.ts,
restPaged and heldRowId).

Energy Research Warehouse (ERW). No network, no model, no build: the site's own reader is run under node with fetch
stubbed (site/scripts/test-heldrow-ids.mjs), and the source is read.

    python -m unittest tests.test_session9811 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheReaderKnowsARowByItsId(unittest.TestCase):
    def test_the_filter_reads_the_three_ids(self):
        t = src("site", "lib", "supabase.ts")
        self.assertIn("return rows.filter((r) => !licenseHeldRow(t, heldRowId(r as Record<string, unknown>)));", t)
        self.assertIn('for (const k of ["entity", "entity_id", "event_id"])', t)
        # the old filter, which read only a series row's entity, is gone
        self.assertNotIn("(r as { entity?: string }).entity ?? \"\"", t)

    def test_the_chat_reads_the_same_ids(self):
        t = src("site", "lib", "chat", "heldrows.ts")
        self.assertTrue(re.search(r'for \(const k of \["entity", "id", "entity_id"\]\)', t))

    def test_the_grid_page_says_a_held_queue_is_held(self):
        # a held grid's queue positions no longer reach the page: its cell says "license needed", never "not yet"
        t = src("site", "components", "grid", "YourGrid.tsx")
        held = t.index('} else if (licenseHeldRow("energy_projects", `${g.queue_table.replace(/_interconnection_queue$/, "_queue")}:x`)) {')
        self.assertLess(held, t.index("} else if (!d.queue.length) {"))
        self.assertIn('title={licenseTitle("energy_projects")}>{LICENSE_NEEDED}</span>;', t)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_reader_under_node(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/test-heldrow-ids.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-1500:])
        self.assertIn("5 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
