"""Session 1018 (chain 070): seven days of the code's jobs (docs/reviews/scheduled-jobs-2026-10-24.md). No scheduled
job failed; the six failures were code branches' own checks, each branch landed after. The review names every workflow
read. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Review(unittest.TestCase):
    def test_every_workflow_is_named(self):
        with open(os.path.join(ROOT, "docs", "reviews", "scheduled-jobs-2026-10-24.md"), encoding="utf-8") as f:
            doc = f.read()
        for name in ("chain watch", "hourly network", "latest prices", "daily prices", "energy roundup", "weekly vacuum"):
            self.assertIn(f"| {name} |", doc)
        self.assertIn("## No fault of the repository's code", doc)
        self.assertNotIn(chr(0x2014), doc)


if __name__ == "__main__":
    unittest.main()
