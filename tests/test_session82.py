"""Session 82: the one-line email when a report is pushed (scripts/notify.py), the daily mode of CAISO's supply
connector, and California's hours (warehouse/derived/caiso_join.py).

Energy Research Warehouse (ERW). No request leaves the machine: the sender is called with a stand-in for requests.post.

    python -m unittest tests.test_session82 -v
"""

import os
import sys
import types
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("scripts", "warehouse", "warehouse/connectors", "warehouse/derived", "warehouse/news"):
    sys.path.insert(0, os.path.join(ROOT, p))

import caiso_join as cj  # noqa: E402
import notify  # noqa: E402


class Notify(unittest.TestCase):
    def env(self, **kv):
        return lambda name: kv.get(name, "")

    def test_one_line_and_the_reports_address(self):
        subject, body = notify.message(82, "wip/082-land", "  landed;\n two steps   skipped ")
        self.assertEqual(subject, "ERW session 82: report pushed")
        self.assertEqual(body.splitlines()[0], "landed; two steps skipped")
        self.assertEqual(body.strip().splitlines()[-1],
                         "https://github.com/SamuelEnrique/erw/blob/wip/082-land/archive/sessions/SESSION_82_REPORT.md")
        self.assertEqual(len([ln for ln in body.splitlines() if ln.strip()]), 2)   # the line and the address, nothing else

    def test_an_empty_or_long_line_or_an_em_dash_is_refused(self):
        for bad in ("", "   ", "x" * 301, "a line " + chr(0x2014) + " with a dash"):
            with self.assertRaises(ValueError):
                notify.message(82, "b", bad)

    def test_it_goes_to_the_fixed_recipients_only_one_message_each(self):
        calls = []

        def post(url, headers=None, timeout=None, json=None):
            calls.append((url, headers, json))
            return types.SimpleNamespace(status_code=200, text="{}")
        n = notify.send(82, "wip/x", "done", post=post,
                        env=self.env(RESEND_API_KEY="k", DIGEST_RECIPIENTS="a@example.org, b@example.org", DIGEST_FROM="ERW <e@example.org>"))
        self.assertEqual(n, 2)
        self.assertEqual([c[2]["to"] for c in calls], [["a@example.org"], ["b@example.org"]])
        self.assertTrue(all(c[0] == "https://api.resend.com/emails" for c in calls))
        self.assertTrue(all(set(c[2]) == {"from", "to", "subject", "text"} for c in calls))   # no html, no attachment
        self.assertTrue(all(c[2]["from"] == "ERW <e@example.org>" for c in calls))

    def test_nothing_is_sent_without_a_key_or_a_recipient_or_on_a_dry_run(self):
        calls = []
        post = lambda *a, **k: calls.append(1)  # noqa: E731
        with self.assertRaises(RuntimeError):
            notify.send(82, "b", "done", post=post, env=self.env(DIGEST_RECIPIENTS="a@example.org"))
        with self.assertRaises(RuntimeError):
            notify.send(82, "b", "done", post=post, env=self.env(RESEND_API_KEY="k"))
        self.assertEqual(notify.send(82, "b", "done", dry_run=True, post=post, env=self.env(RESEND_API_KEY="k", DIGEST_RECIPIENTS="a@example.org")), 0)
        self.assertEqual(calls, [])

    def test_a_refusal_is_an_error_and_names_no_address(self):
        post = lambda *a, **k: types.SimpleNamespace(status_code=403, text="no")  # noqa: E731
        with self.assertRaises(RuntimeError) as c:
            notify.send(82, "b", "done", post=post, env=self.env(RESEND_API_KEY="k", DIGEST_RECIPIENTS="someone@example.org"))
        self.assertNotIn("someone@example.org", str(c.exception))

    def test_the_script_never_reads_subscribers(self):
        with open(os.path.join(ROOT, "scripts", "notify.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("subscribers(", src)
        self.assertNotIn("supa(", src)


class DailySupply(unittest.TestCase):
    def test_days_and_start_are_alternatives(self):
        import caiso_fuel_supply as fs
        with self.assertRaises(SystemExit):
            fs.main(["--dry-run"])
        with self.assertRaises(SystemExit):
            fs.main(["--start", "2026-10-01", "--days", "3", "--dry-run"])
        self.assertEqual(fs.main(["--days", "3", "--dry-run"]), 0)
        self.assertEqual(fs.main(["--start", "2026-09-28", "--end", "2026-09-30", "--dry-run"]), 0)

    def test_the_daily_run_pulls_the_supply_then_builds_then_applies_the_join(self):
        with open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8") as f:
            sh = f.read()
        a = sh.index('run_other caiso_fuel_supply "$PYTHON" warehouse/connectors/caiso_fuel_supply.py --days "$DAYS"')
        b = sh.index('run_other carbon_intensity "$PYTHON" warehouse/derived/carbon_intensity.py')
        c = sh.index('run_other caiso_join "$PYTHON" warehouse/derived/caiso_join.py --apply')
        d = sh.index('run_other grid_network "$PYTHON" warehouse/derived/grid_network.py')
        self.assertTrue(a < b < c < d)
        with open(os.path.join(ROOT, "warehouse", "redivis", "config.yaml"), encoding="utf-8") as f:
            self.assertIn("'^caiso_fuel_supply$'", f.read())

    def test_the_carbon_builder_never_writes_eias_generation_for_california_from_the_join(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "carbon_intensity.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("if code == cj.BA and var == cj.VARIABLE:", src)
        self.assertIn("j = cj.before_join(j)", src)
        j = pd.DataFrame({"ts_utc": ["2025-12-16T07:00:00Z", "2025-12-16T08:00:00Z"], "co2": [1.0, 2.0], "mwh": [3.0, 4.0]})
        self.assertEqual(list(cj.before_join(j)["co2"]), [1.0])


if __name__ == "__main__":
    unittest.main()
