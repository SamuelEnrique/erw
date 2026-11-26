"""Audit of the Digest and the Roundup, finding 6 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): since
21 October 2026 news_index is held whole for a licence (site/data/license_status.json; "the stories ... come from the
news index, whose outlets ask for permission"), and the Digest's page holds its story sections (lib/digest.ts
STORY_SECTIONS). The hold stops there. On 26 November 2026, through the site's own library:

  the Digest of 12 November: four story sections held, while the opening number ("USD 74 billion: SpaceX plans ... as
    Bloomberg.com reported") and the numbers block's two story rows (pv magazine USA's 580 MW, JPT's USD 2.1 billion)
    are drawn, each the same index's story;
  the Roundup of W45: no story held at all (holdRoundupGrids holds grids, not stories): eight story items and six Google
    News links drawn, no word of the hold.

The test passes on main: it shows the hold as it stands. Extending it changes what visitors see of the issues and is
the owner's to rule (item 2 of his rulings set the Digest's hold), so it is for Samuel's ruling, not done here."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheNewsHoldStopsAtTheStorySections(unittest.TestCase):
    def test_what_the_pages_draw_of_the_held_index(self):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-audit-digest-6.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        if not out["news_index_held"]:
            self.skipTest("news_index is no longer held")
        self.assertEqual(out["digest_story_sections_held"], 4)
        self.assertTrue(out["digest_opening_story_shown"])
        self.assertEqual(out["digest_block_story_rows_shown"], [True, True])
        self.assertEqual(out["roundup_story_items_shown"], 8)
        self.assertEqual(out["roundup_google_news_links_shown"], 6)
        self.assertFalse(out["roundup_says_held"])


if __name__ == "__main__":
    unittest.main()
