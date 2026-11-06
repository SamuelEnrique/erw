"""Session 3018 (chain 164): /internal/findings lists every draft, not the newest 100.

Energy Research Warehouse (ERW). scanner_drafts_list (migration 029) returns 100 rows unless asked for more and at
most 500. On 6 November 2026 the review list held 222 rows, and the page, which asked for no limit, showed 100: the
findings hunt's 156 drafts pushed the scanner's 66 older rows (one approved) off the page. The page now asks for the
function's most.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class DraftsList(unittest.TestCase):
    def test_the_page_asks_for_the_functions_most(self):
        lib = src("site", "lib", "scanner.ts")
        cap = re.search(r"limit least\(greatest\(coalesce\(p_limit, 100\), 1\), (\d+)\)", src("warehouse", "supabase", "migrations", "029_scanner_drafts.sql"))
        self.assertIsNotNone(cap)
        self.assertIn(f"export const LIST_LIMIT = {cap.group(1)};", lib)
        body = lib[lib.index("export async function listDrafts"):]
        body = body[: body.index("\n}\n")]
        self.assertIn("p_limit: String(LIST_LIMIT)", body)

    def test_the_page_still_lists_through_listDrafts(self):
        self.assertIn("drafts = await listDrafts();", src("site", "app", "internal", "findings", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
