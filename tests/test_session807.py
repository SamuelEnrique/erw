"""Session 807: a dry run of the Digest on a past day (--now, the end of the window, with --out only), so tomorrow's
Digest can be read before the schedule writes it (runs/periodicals_dryrun/, never docs/digest/). The window is the hours
to --now, and a story dated after the window's end (a feed's future date) is not in it. No model, no network here.
"""

import io
import os
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402


class WhatTheDryRunShowed(unittest.TestCase):
    def test_a_source_is_named_once(self):
        # session 2701 (rulings item 15): a held outlet keeps its link, so it prints as any outlet does: once a link
        self.assertEqual(brief.link_text([("POWER Magazine", "https://a"), ("POWER Magazine", "https://a")], {"POWER Magazine"}), "[POWER Magazine](https://a)")
        self.assertEqual(brief.link_text([("X", "https://a"), ("X", "https://b")], set()), "[X](https://a), [X](https://b)")

    def test_the_fallback_is_not_the_headline_again(self):
        head = "Crusoe plans Spark Liquid modular data center with 3.5MW deployments for Nvidia GPUs"
        self.assertEqual(brief.why_line("Crusoe plans 3.5MW modular units for Nvidia GPUs.", head), "")
        self.assertEqual(brief.why_line("A 3.5MW unit adds load.", "Crusoe plans 3.5MW units, Reuters reports"), "A unit adds load.")
        # the fallback prints only when the headline's clause is not the headline itself (a publisher's suffix off)
        self.assertEqual(brief.why_line("Totaling 3.5MW of units.", "Crusoe plans 3.5MW units, Reuters reports"), "Crusoe plans 3.5MW units.")
        self.assertEqual(brief.why_line("Totaling 3.5MW of units.", "Crusoe plans 3.5MW units"), "")

    def test_a_bullet_without_a_why_line_still_reads(self):
        import inspect
        src = inspect.getsource(brief.main)
        self.assertEqual(src.count('" ".join(x for x in (why_line(r[\'why\'], heads[r[\'cluster_id\']]), link_text(r[\'links\'][:1])) if x)'), 2)


class TheWindow(unittest.TestCase):
    def test_now_needs_out(self):
        with self.assertRaises(SystemExit):
            with mock.patch("sys.stderr", io.StringIO()):
                brief.main(["--now", "2026-10-21T15:45Z"])

    def test_the_window_ends_at_now_and_takes_nothing_after_it(self):
        import inspect
        src = inspect.getsource(brief.main)
        self.assertIn("(when <= now)", inspect.getsource(brief.window_rows))   # session 2206's window_rows, which main calls
        self.assertIn("window_rows(df, now, hours, start)", src)
        self.assertIn('ap.add_argument("--now"', src)
        t = pd.Timestamp("2026-10-21T15:45Z")
        self.assertEqual(t.tz_convert("UTC").strftime("%Y-%m-%d %H:%M"), "2026-10-21 15:45")

    def test_a_naive_now_is_read_as_utc(self):
        now = pd.Timestamp("2026-10-21T15:45")
        self.assertIsNone(now.tzinfo)
        self.assertEqual(now.tz_localize("UTC").strftime("%H:%M %Z"), "15:45 UTC")


if __name__ == "__main__":
    unittest.main()
