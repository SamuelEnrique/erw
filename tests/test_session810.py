"""Session 810: the pages and the email at 390 (docs/brand/review-810/). The pages' tables already sit in scroll containers
(.prose-erw table in site/app/globals.css); the email's did not, and the email had no viewport, so a 390 px screen laid it
out 980 px wide. Now every table of the email's HTML is in a scroll container and the head carries the viewport and the
charset. No issue's text changes. No model, no network.
"""

import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import email_digest  # noqa: E402

MD = """# ERW's Energy Digest, 2026-10-21

ERW's weekday brief of energy news for the 24 hours to 2026-10-21 15:45 UTC, from 256 scored stories.

## Top of the industry

1. **A** (oil)
   Why. Sources: [X](https://example.org/1)
2. **B** (gas)
   Why. Sources: [X](https://example.org/2)
3. **C** (lng)
   Why. Sources: [X](https://example.org/3)
4. **D** (nuclear)
   Why. Sources: [X](https://example.org/4)
5. **E** (policy)
   Why. Sources: [X](https://example.org/5)

## ERW's Numbers Today

**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day, and the day before):

| ISO | Hub or zone | Operating day | Average USD/MWh | Table | Day before USD/MWh | Change |
|---|---|---|---|---|---|---|
| ERCOT | HB_NORTH | 2026-10-20 | 28.38 | [1] | 23.41 | +4.97 (+21.2%) |

Tables: [1] `iso_dam_hub_prices` (x).

ERW

---
"""


class TheEmailAt390(unittest.TestCase):
    def render(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "digest.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(MD)
            return email_digest.render(p, "daily", unsubscribe="x")

    def test_every_table_is_in_a_scroll_container(self):
        _, _, _, html = self.render()
        tables = re.findall(r"<table style=\"border-collapse", html)
        self.assertEqual(len(tables), 1)
        self.assertEqual(html.count('<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%"><table'), len(tables))
        self.assertEqual(html.count("</table></div>"), len(tables))

    def test_the_head_carries_the_viewport_and_the_charset(self):
        _, _, _, html = self.render()
        self.assertTrue(html.startswith('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body'))

    def test_the_text_part_is_unchanged_by_it(self):
        _, _, text, _ = self.render()
        self.assertIn("  ISO: ERCOT; Hub or zone: HB_NORTH; Operating day: 2026-10-20; Average USD/MWh: 28.38; Table: [1]; Day before USD/MWh: 23.41; Change: +4.97 (+21.2%)", text)
        self.assertNotIn("overflow", text)

    def test_the_page_s_tables_scroll(self):
        with open(os.path.join(ROOT, "site", "app", "globals.css"), encoding="utf-8") as f:
            css = f.read()
        self.assertRegex(css, r"\.prose-erw table \{[^}]*overflow-x: auto")


if __name__ == "__main__":
    unittest.main()
