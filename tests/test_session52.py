"""Session 52: the bill explainer v1 (SCE, SDG&E and CenterPoint bills) and the private intake for real bills.

Energy Research Warehouse (ERW). No network, no model.
1. site/scripts/test-bill.mjs: every bill, the five defaults included, matches its hand-computed figures at 600 and
   1,000 kWh (SCE also in summer; SDG&E also with a baseline allowance), and every line is cited, quoted and dated.
2. The intake drops personal data: a made-up bill with a name, address, account, ESI ID and meter number comes out
   with none of them.
3. Real bills stay out of git: private/bills/ is ignored, its README tracked; the example fixture says it is fictional.
4. site/scripts/test-bill-fixtures.mjs reports every fixture line by line.

    python -m unittest tests.test_session52 -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class Bills(unittest.TestCase):
    def test_hand_computed(self):
        r = subprocess.run([NODE, "scripts/test-bill.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        for case in ("SCE winter 600 kWh", "SCE winter 1,000 kWh", "SDG&E summer 600 kWh", "SDG&E summer 1,000 kWh", "CenterPoint 600 kWh", "CenterPoint 1,000 kWh"):
            self.assertIn(f"ok   {case}", r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_fixture_report(self):
        r = subprocess.run([NODE, "scripts/test-bill-fixtures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("txc-fictional-example.json (FICTIONAL example)", r.stdout)
        self.assertIn("only on the bill", r.stdout)
        self.assertIn("total: real", r.stdout)


@unittest.skipUnless(NODE, "node is not installed")
class Intake(unittest.TestCase):
    def test_personal_data_dropped(self):
        tmp = tempfile.mkdtemp()
        try:
            csv = os.path.join(tmp, "bill.csv")
            with open(csv, "w", encoding="utf-8") as f:
                f.write("utility,plan_type,period_start,period_end,kwh,line,amount,customer_name,service_address,account_number\n"
                        "TXC,fixed,2026-08-14,2026-09-13,900,Energy Charge,76.77,Jane Q Public,77 Elm Street,9988776655\n"
                        "TXC,,,,,Customer Charge,2.11,,,\n"
                        "TXC,,,,,ESI ID 1008901020304050,0,,,\n"
                        "TXC,,,,,Meter No 44556677,0,,,\n")
            out = os.path.join(tmp, "out")
            r = subprocess.run([NODE, os.path.join(SITE, "scripts", "bill-intake.mjs"), csv, "--out", out], capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            files = os.listdir(out)
            self.assertEqual(len(files), 1)
            text = open(os.path.join(out, files[0]), encoding="utf-8").read()
            for secret in ("Jane", "Public", "Elm", "9988776655", "1008901020304050", "44556677", "ESI", "Meter"):
                self.assertNotIn(secret, text)
            fx = json.loads(text)
            self.assertEqual([l["name"] for l in fx["lines"]], ["Energy Charge", "Customer Charge"])
            self.assertEqual(set(fx), {"fictional", "source", "utility", "plan_type", "period", "kwh", "lines"})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Privacy(unittest.TestCase):
    def test_gitignore(self):
        g = src(".gitignore")
        self.assertIn("private/bills/*", g)
        self.assertIn("!private/bills/README.md", g)
        self.assertIn("never leave this folder", src("private", "bills", "README.md"))

    def test_example_is_fictional(self):
        fx = json.loads(src("tests", "fixtures", "bills", "txc-fictional-example.json"))
        self.assertTrue(fx["fictional"])
        self.assertIn("FICTIONAL", fx["source"])

    def test_rules_sources(self):
        r = json.loads(src("site", "data", "bill_rules.json"))
        for k in ("SCE", "SDGE", "TXC"):
            self.assertIn(k, r["bills"])
        for sid in ("sce_tou_d", "sce_prelim_h", "sdge_toudr1_rates", "sdge_toudr1_sheet", "cnp_tariff"):
            self.assertTrue(r["sources"][sid]["url"].startswith("https://"))
        self.assertNotIn("—", src("site", "data", "bill_rules.json"))


if __name__ == "__main__":
    unittest.main()
