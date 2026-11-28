"""Ready branch for /impact (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "Georgia's exemption
ends in 2031 as the act reads, or 2033 as the state auditor writes": the other choice, 2033). Not the default: it waits
for Samuel's ruling.

site/data/forecast/datacenter_rules.json, Georgia's sales_exemption: last_year 2033, invest_before_year 2034, its tip
naming the auditor and the act; the act's term quote kept as read. Measured through the page's own model
(lib/dcimpact.ts) with main's file against this one: at the defaults nothing moves (forgone USD 618.71 million, the
build of 2027 and 2028); with a 3-year refresh USD 618.71 million to 1,237.42 million (the 2032 purchase); a build of
2030 to 2033 USD 51.56 million to 103.12 million.

1. The rule in the file and the words.
2. site/scripts/test-datacenter.test.mjs (Georgia's case turned: a build of 2032 forgoes, one of 2034 does not), run
   by Node's test runner, where node and the site's packages are installed."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class GeorgiaTo2033(unittest.TestCase):
    def test_the_rule(self):
        ga = json.loads(src("site", "data", "forecast", "datacenter_rules.json"))["states"]["ga"]["sales_exemption"]
        self.assertEqual((ga["last_year"], ga["invest_before_year"]), (2033, 2034))
        self.assertIn("2029 2032", ga["term"]["quote"])                    # the act's own words, as read, kept
        self.assertIn("for equipment bought through 31 December 2033, as the state auditor's evaluation writes", ga["tip"])
        self.assertIn("13. **Georgia's exemption ends with 2033, as the state auditor writes", src("docs", "methods", "forecast.md"))
        self.assertIn("dc_sales 2000000000 0.682 0.0756 2 20 2027 5 1 2033 999", src("replication", "impact", "datacenter", "replicate_datacenter.do"))

    @unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules", "react")), "node or the site's packages are not installed")
    def test_the_model(self):
        r = subprocess.run([NODE, "--no-warnings", "--test", "--test-name-pattern=Georgia",
                            "scripts/test-datacenter.test.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
