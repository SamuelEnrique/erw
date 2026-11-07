"""Session 3716 (chain 208): /internal/health's green streak read against the health summaries (roadmap item 6).

/internal/health draws the streak from site/data/health_days.json, which warehouse/health.py writes from erw_health with
each day's summary (queue/summary/<day>-health.md). This recomputes every day's status of the last fourteen days the
summaries hold, from the summaries alone, and holds the record to it: the failures that count, the day's colour, and the
streak counted back from the newest day. It reads no table and makes no request; the days are whatever the repository
holds, so the daily run's new day never turns it red by itself.
"""
import datetime as dt
import importlib.util
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "queue", "summary")
DAYS = os.path.join(ROOT, "site", "data", "health_days.json")
WINDOW = 14


def summary_of(day):
    """(the failures the summary counts, the stale-at-source lines it lists) for one day, or None when no summary."""
    path = os.path.join(SUMMARY, f"{day}-health.md")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"\*\*(\d+) failures?\*\*", text)
    failures = int(m.group(1)) if m else (0 if re.search(r"\*\*No failure", text) or "**0 failures**" in text else None)
    listed = 0
    if "## Failures" in text:
        listed = len(re.findall(r"^- ", text.split("## Failures", 1)[1].split("\n## ", 1)[0], re.M))
    return {"failures": failures, "listed": listed}


def health():
    spec = importlib.util.spec_from_file_location("health_s3716", os.path.join(ROOT, "warehouse", "health.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheStreak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DAYS):
            raise unittest.SkipTest("site/data/health_days.json is not in this copy")
        with open(DAYS, encoding="utf-8") as f:
            cls.record = json.load(f)
        cls.days = cls.record["days"]
        newest = dt.date.fromisoformat(cls.record["counted_to"])
        cls.window = [(newest - dt.timedelta(days=i)).isoformat() for i in range(WINDOW)]
        cls.summaries = {d: summary_of(d) for d in cls.window}
        if sum(1 for s in cls.summaries.values() if s) < WINDOW // 2:
            raise unittest.SkipTest("fewer than half of the fourteen days' summaries are in this copy")

    def test_every_days_failures_are_the_summarys(self):
        differ = []
        for day, s in self.summaries.items():
            if not s or s["failures"] is None or day not in self.days:
                continue
            if self.days[day]["failed"] != s["failures"] or len(self.days[day].get("failures", [])) != s["failures"]:
                differ.append((day, s["failures"], self.days[day]["failed"]))
        self.assertEqual(differ, [])

    def test_every_listed_failure_is_counted(self):
        for day, s in self.summaries.items():
            if s and s["failures"] is not None:
                self.assertEqual(s["listed"], s["failures"], day)

    def test_the_days_colour_and_the_streak(self):
        # a day is green when the summary counts no failure and no job that runs every day is missing from the record
        colour = {}
        for day in self.window:
            s, rec = self.summaries.get(day), self.days.get(day)
            if not s or rec is None:
                colour[day] = None
                continue
            colour[day] = "green" if s["failures"] == 0 and not rec.get("missing") else "red"
        n = 0
        for day in self.window:              # newest first
            if colour[day] != "green":
                break
            n += 1
        if n < WINDOW:
            self.assertEqual(self.record["green_days"], n)
        h = health()
        self.assertEqual(h.green_streak(self.days), (self.record["green_days"], self.record["counted_to"]))

    def test_the_rule_is_written_in_machines_md(self):
        with open(os.path.join(ROOT, "docs", "machines.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("### The green streak, as counted (session 3716)", text)
        for words in ("stale at source", "a missing day ends the count", "SHORT_ENDS_STREAK", "dm_"):
            self.assertIn(words, text.split("### The green streak, as counted (session 3716)", 1)[1].split("\n### ", 1)[0])


if __name__ == "__main__":
    unittest.main()
