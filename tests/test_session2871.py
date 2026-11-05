"""Session 2871 (chain 147): large loads' filed tariffs, the registry and its table (utility_large_load_tariffs).

Energy Research Warehouse (ERW). The connector warehouse/connectors/large_load_tariffs.py turns the registry's files
(warehouse/sources/large_load_tariffs/, one a schedule) into the table the All grids tab's builder already reads
(siting_page.tariffs_file, session 730), without a rename; it refuses a file whose figure lacks its page or words; the
validator refuses a row without its filing. A fixture registry here, no request, no model call.
"""
import os
import sys
import tempfile
import textwrap
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import large_load_tariffs as llt  # noqa: E402

GOOD = textwrap.dedent("""\
    utility: Fixture Power Company
    eia_id: 99001
    state: OH
    grid: PJM
    sector: Industrial
    schedule: Large Load Schedule X
    tariff_sheet: P.U.C.O. No. 1, Sheet 10
    effective: 2025-07-09
    voltage: {text: "138 kV or above", page: 1}
    commission: Public Utilities Commission of Ohio
    docket: 99-0001-EL-ATA
    document: Opinion and Order, Attachment A
    document_url: https://example.org/order.pdf
    retrieved_at: 2026-11-05T22:00:00Z
    license: public
    terms:
      min_bill: {text: "85 percent of contract capacity", page: 3}
      term: "12 years"
    figures:
      - {variable: min_demand_mw, value: 25, printed: "25 MW", page: 1}
      - {variable: demand_charge_transmission, value: 9.01, printed: "$9.01 per kW", page: 2}
      - {variable: energy_charge, value: 4.12, printed: "0.412 cents per kWh", page: 2}
      - {variable: min_contract_years, value: 12, printed: "twelve (12) years", page: 3}
      - {variable: min_bill_pct, value: 85, printed: "85%", page: 3}
    """)


def registry(**files):
    d = tempfile.mkdtemp()
    for name, text in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(text)
    return d


class TheRows(unittest.TestCase):
    def setUp(self):
        regs, problems = llt.read_registry(registry(**{"fixture_x.yaml": GOOD}))
        self.assertEqual(problems, [])
        self.d = llt.rows(regs)

    def test_one_row_a_printed_figure_with_its_page_and_words(self):
        d = self.d
        self.assertEqual(len(d), 5)
        self.assertEqual(set(d["entity"]), {"filed:99001:large_load_schedule_x"})
        self.assertEqual(set(d["ts_utc"]), {"2025-07-09T00:00:00Z"})
        e = d.set_index("variable")
        self.assertEqual((e.loc["energy_charge", "value"], e.loc["energy_charge", "unit"], e.loc["energy_charge", "x_printed"], e.loc["energy_charge", "x_page"]),
                         (4.12, "USD/MWh", "0.412 cents per kWh", "2"))
        self.assertEqual(e.loc["demand_charge_transmission", "unit"], "USD/kW-month")
        self.assertEqual(e.loc["min_bill_pct", "unit"], "pct")
        self.assertEqual(e.loc["min_demand_mw", "x_voltage"], "138 kV or above (p. 1)")
        self.assertEqual(e.loc["min_demand_mw", "x_min_bill"], "85 percent of contract capacity (p. 3)")
        self.assertEqual(e.loc["min_demand_mw", "x_term"], "12 years")
        self.assertEqual(list(d.columns[:4]), ["entity", "variable", "ts_utc", "value"])
        self.assertTrue((d["source_url"] == "https://example.org/order.pdf").all())

    def test_the_tabs_builder_reads_the_table_without_a_rename(self):
        import siting_page
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "utility_large_load_tariffs.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                self.d.to_csv(f, index=False, lineterminator="\n")
            out = siting_page.tariffs_file(p)
        r = out["utilities"]["99001"][0]
        self.assertEqual((r["rate"], r["start"], r["utility"], r["energy"], r["min_mw"]), ("filed:99001:large_load_schedule_x", "2025-07-09", "Fixture Power Company", 4.12, 25.0))
        self.assertIsNone(r["demand"])            # the schedule prints its parts, not one demand charge: none is made up

    def test_the_written_table_passes_the_validator_and_one_without_a_page_does_not(self):
        import erw_validate
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "utility_large_load_tariffs.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                self.d.to_csv(f, index=False, lineterminator="\n")
            self.assertEqual(erw_validate.validate(p)["errors"], [])
            bad = self.d.copy()
            bad.loc[0, "x_page"] = ""
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                bad.to_csv(f, index=False, lineterminator="\n")
            self.assertEqual([e["check"] for e in erw_validate.validate(p)["errors"]], ["filing_cited"])


class TheRefusals(unittest.TestCase):
    def problems(self, text):
        return llt.read_registry(registry(**{"f.yaml": text}))[1]

    def test_a_figure_without_its_page_or_words_or_a_known_variable(self):
        self.assertTrue(any("no page" in p for p in self.problems(GOOD.replace('printed: "25 MW", page: 1', 'printed: "25 MW"'))))
        self.assertTrue(any("no printed words" in p for p in self.problems(GOOD.replace('printed: "25 MW", ', ""))))
        self.assertTrue(any("is not one of" in p for p in self.problems(GOOD.replace("min_demand_mw", "all_in_price"))))

    def test_a_licence_a_date_and_a_demand_charge_beside_its_parts(self):
        self.assertTrue(any("license" in p for p in self.problems(GOOD.replace("license: public", "license: internal"))))
        self.assertTrue(any("effective" in p for p in self.problems(GOOD.replace("2025-07-09", "July 2025"))))
        both = GOOD + '  - {variable: demand_charge, value: 12, printed: "$12 per kW", page: 2}\n'
        self.assertTrue(any("beside its parts" in p for p in self.problems(both)))

    def test_a_refused_registry_writes_nothing(self):
        d = registry(**{"f.yaml": GOOD.replace("license: public", "license: internal")})
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(llt.main(["--registry", d, "--out-dir", out]), 1)
            self.assertFalse(os.path.exists(os.path.join(out, "utility_large_load_tariffs.csv")))

    def test_a_trial_writes_the_table_under_its_folder(self):
        d = registry(**{"f.yaml": GOOD})
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(llt.main(["--registry", d, "--out-dir", out]), 0)
            with open(os.path.join(out, "utility_large_load_tariffs.csv"), encoding="utf-8") as f:
                text = f.read()
        self.assertIn("# Energy Research Warehouse (ERW): large loads' filed tariffs", text)
        self.assertNotIn(chr(0x2014), text)


class TheRegistryAsCommitted(unittest.TestCase):
    def test_every_file_of_the_registry_is_written(self):
        regs, problems = llt.read_registry()
        self.assertEqual(problems, [])
        for p, _ in regs:
            self.assertTrue(os.path.basename(p).endswith(".yaml"))

    def test_no_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "connectors", "large_load_tariffs.py"), ("docs", "methods", "large_load_tariffs.md"),
                      ("warehouse", "sources", "large_load_tariffs", "README.md")):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(chr(0x2014), text, parts)
            self.assertNotIn(chr(0x2013), text, parts)


if __name__ == "__main__":
    unittest.main()
