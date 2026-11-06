"""Session 815: the chart of the day at a phone's width. daily_chart.section draws a second picture, <date>-600.png (600 by
760, the type at 0.8 of the digest's sizes), beside the 1200 px one and records it (image_phone); the build copies it and
records it (image_600), and the Digest's page offers it under 640 px through srcset (site/lib/markdown.ts). The markdown
line of the chart, the figures' keys and the checker are unchanged. No model, no network, no scan: the fixture candidates of
session 232.
"""

import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "analysis", "findings")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import card_image  # noqa: E402
import daily_chart  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json")


def candidates():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)["candidates"]


def quiet(_):
    pass


def png_size(path):
    with open(path, "rb") as f:
        b = f.read(24)
    return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")


class ThePhonePicture(unittest.TestCase):
    def test_the_size(self):
        self.assertEqual(card_image.SIZES["phone"], (600, 760))
        self.assertEqual(card_image.SCALE["phone"], 0.8)
        self.assertEqual(card_image.CALLOUTS["phone"], 3)

    def test_the_section_draws_both_and_records_the_phone_one(self):
        c = candidates()
        waited = {x["key"] for x in c if (daily_chart.record_jump(x) or 0) > daily_chart.RECORD_JUMP}
        with tempfile.TemporaryDirectory() as d:
            lines = daily_chart.section("2026-10-13", quiet, chart_dir=d, candidates=c, waited=waited)
            self.assertTrue(lines)
            self.assertEqual(png_size(os.path.join(d, "2026-10-13.png")), (1200, 880))
            self.assertEqual(png_size(os.path.join(d, "2026-10-13-600.png")), (600, 760))
            with open(os.path.join(d, "2026-10-13.json"), encoding="utf-8") as f:
                rec = json.load(f)
            self.assertEqual(rec["image"], "2026-10-13.png")
            self.assertEqual(rec["image_phone"], "2026-10-13-600.png")
        # the markdown names the 1200 px picture as before: the page chooses
        self.assertTrue(any(ln.startswith("![") and ln.endswith("](charts/2026-10-13.png)") for ln in lines))

    def test_the_build_and_the_page_offer_it(self):
        with open(os.path.join(ROOT, "site", "scripts", "build-content.mjs"), encoding="utf-8") as f:
            build = f.read()
        self.assertIn("(?:-600)?\\.png$", build)
        self.assertIn("image_600 = `${m[1]}-600.png`", build)
        with open(os.path.join(ROOT, "site", "lib", "markdown.ts"), encoding="utf-8") as f:
            md = f.read()
        self.assertIn('srcset="/digest-charts/${phone} 600w, ${escapeHtml(href)} 1200w" sizes="(max-width: 640px) 100vw, 640px"', md)
        self.assertIn("image_600?: string", md)
        self.assertRegex(md, r"docs\\/digest\\/charts\\/\(\\d\{4\}-\\d\{2\}-\\d\{2\}\(\?:-600\)\?\\\.png\)")

    def test_no_dash(self):
        for rel in (("warehouse", "analysis", "findings", "card_image.py"), ("warehouse", "analysis", "findings", "daily_chart.py"),
                    ("site", "lib", "markdown.ts"), ("site", "scripts", "build-content.mjs")):
            with open(os.path.join(ROOT, *rel), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)


if __name__ == "__main__":
    unittest.main()


class ThePointsForThePage(unittest.TestCase):
    """Session 1461 (chain 150, fault 41 of docs/reviews/periodicals-faults-2026-11-05.md): the record keeps the series the
    card draws, so the page draws the chart with a hover on each point; the picture stays the email's."""

    def test_the_record_keeps_the_points(self):
        c = candidates()
        waited = {x["key"] for x in c if (daily_chart.record_jump(x) or 0) > daily_chart.RECORD_JUMP}
        with tempfile.TemporaryDirectory() as d:
            daily_chart.section("2026-10-13", quiet, chart_dir=d, candidates=c, waited=waited)
            with open(os.path.join(d, "2026-10-13.json"), encoding="utf-8") as f:
                rec = json.load(f)
        chosen = next(x for x in c if x["key"] == rec["key"])
        ch = chosen["card"]["chart"]
        p = rec["points"]
        self.assertEqual(len(p["x"]), min(len(ch["x"]), daily_chart.POINTS_MAX))
        self.assertEqual(p["x"][-1], str(ch["x"][-1])[:10])
        self.assertEqual(p["series"][0]["values"][-1], float(ch["series"][0]["values"][-1]))
        self.assertEqual(p["decimals"], ch.get("decimals", 2))
        self.assertEqual(p["unit"], (chosen.get("flag") or {}).get("unit", "") or ch.get("unit", ""))

    def test_a_chart_of_another_shape_keeps_none(self):
        self.assertIsNone(daily_chart.chart_points({"kind": "scatter", "points": [[1, 2]]}))
        self.assertIsNone(daily_chart.chart_points({"x": ["a", "b"], "series": [{"name": "s", "values": [1]}]}))
        got = daily_chart.chart_points({"x": ["2026-01-01", "2026-02-01"], "series": [{"name": "s", "values": [1.5, "n/a"]}], "decimals": 1}, "MW")
        self.assertEqual(got, {"x": ["2026-01-01", "2026-02-01"], "series": [{"name": "s", "values": [1.5, None]}], "unit": "MW", "decimals": 1})
