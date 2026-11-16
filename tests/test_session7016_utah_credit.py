"""Session 7016 (chain 301, done-line request 10): Utah's $966, printed in the Tax Foundation table's deduction column as
"$966 credit", is a credit against the tax, not a deduction from income. The builder tested the word only in the
exemption's column. With it held as a credit, /impact?tech=geothermal&state=ut&mw=86&start=2026 reads USD 23.4 million
of state income tax over the life (USD 28.4 million before; present value USD 9.27 million, 11.56 before). No request,
no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Utah(unittest.TestCase):
    def test_the_file_holds_a_credit_and_no_deduction(self):
        with open(os.path.join(ROOT, "site", "data", "forecast", "income_tax.json"), encoding="utf-8") as f:
            ut = json.load(f)["states"]["ut"]
        self.assertEqual(ut["standard_deduction_text"], "$966 credit")
        self.assertIsNone(ut["standard_deduction_single"])
        self.assertEqual(ut["personal_credit_single"], 966.0)

    def test_the_builder_reads_a_credit_in_either_column(self):
        with open(os.path.join(ROOT, "warehouse", "forecast", "params.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('ded_credit = money(ded) if "credit" in ded.lower() else None', s)
        self.assertIn('"standard_deduction_single": money(ded) if ded_credit is None else None', s)
        self.assertIn('"personal_credit_single": sum(credits) if credits else None', s)


if __name__ == "__main__":
    unittest.main()
