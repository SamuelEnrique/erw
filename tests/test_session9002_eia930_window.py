"""Session 9002 (chain 601, data request 569): the daily run's EIA-930 window heals missed runs.

The runs of 17, 18 and 19 November 2026 stopped before their archive step; with a 3-day window the run of
16 November reached 15 November and the run of 20 November began at 17 November, so no hour of 16 November
reached the warehouse or the live set. The three EIA-930 tables merged into their histories now pull the last
7 complete UTC days (or $DAYS when that is more).
"""
import os
import subprocess
import shutil
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "warehouse", "run_daily.sh")


def text():
    with open(SCRIPT, encoding="utf-8") as f:
        return f.read()


class TheWindow(unittest.TestCase):
    def test_the_three_merged_tables_use_the_wider_window(self):
        t = text()
        for name in ("eia930", "eia930_storage", "eia930_interchange"):
            line = f'pull {name} "$PYTHON" warehouse/connectors/{name}.py --days "$EIA930_DAYS"\n'
            self.assertIn(line, t, name)
            self.assertNotIn(f'warehouse/connectors/{name}.py --days "$DAYS"', t, name)

    def test_the_window_is_seven_days_or_days_when_more(self):
        t = text()
        self.assertIn('EIA930_DAYS="${EIA930_DAYS:-$(( DAYS > 7 ? DAYS : 7 ))}"\n', t)
        self.assertLess(t.index('DAYS="${DAYS:-3}"'), t.index("EIA930_DAYS="))
        self.assertLess(t.index("EIA930_DAYS="), t.index("pull eia930 "))

    def test_the_expression_in_bash(self):
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("no bash")
        line = 'EIA930_DAYS="${EIA930_DAYS:-$(( DAYS > 7 ? DAYS : 7 ))}"; echo "$EIA930_DAYS"'
        for days, want in (("3", "7"), ("7", "7"), ("30", "30")):
            env = {k: v for k, v in os.environ.items() if k != "EIA930_DAYS"}
            env["DAYS"] = days
            out = subprocess.run([bash, "-c", line], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(out.stdout.strip(), want, (days, out.stderr))
        env = dict(os.environ, DAYS="3", EIA930_DAYS="10")
        out = subprocess.run([bash, "-c", line], env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.stdout.strip(), "10")


if __name__ == "__main__":
    unittest.main()
