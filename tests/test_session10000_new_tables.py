"""Session 10000 (chain 701, the desk): two tables asked for by chain 740 (data requests 6 and 7 of
docs/state/data_requests_forecast.md): census_cbp_construction_annual and datacenter_announced.

The figures below are made up for the tests and are in no table. Nothing here makes a request.
"""
import importlib.util
import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *rel.split("/")))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def zip_of(lines):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("cbp99st.txt", "\n".join(lines) + "\n")
    return b.getvalue()


HEAD = "fipstate,naics,lfo,emp_nf,emp,qp1_nf,qp1,ap_nf,ap,est"


class TheConstructionTrades(unittest.TestCase):
    cbp = load("warehouse/connectors/census_cbp_construction.py", "cbp_construction_t")

    def test_the_two_codes_all_legal_forms_and_nothing_else(self):
        rows = self.cbp.parse(zip_of([HEAD,
                                      "48,236///,-,G,100,G,1,G,900,10",      # the three-digit 236: not taken
                                      "48,2362//,-,G,60,G,1,G,500,4",
                                      "48,2362//,C,G,50,G,1,G,400,3",       # a legal form, not all of them: not taken
                                      "48,238///,-,H,70,G,1,J,600,5",
                                      "06,2362//,-,G,11,G,1,G,222,2",
                                      "06,238///,-,G,13,G,1,G,333,3"]), 2023, {"source": "s"})
        got = {(r["entity"], r["variable"]): (r["value"], r["unit"], r["x_naics"]) for r in rows}
        self.assertEqual(len(rows), 12)
        self.assertEqual(got[("census_cbp_2362:tx", "employment")], (60.0, "count", "2362"))
        self.assertEqual(got[("census_cbp_2362:tx", "annual_payroll")], (500000.0, "USD", "2362"))
        self.assertEqual(got[("census_cbp_238:tx", "establishments")], (5.0, "count", "238"))
        tx238 = [r for r in rows if r["entity"] == "census_cbp_238:tx"][0]
        self.assertEqual((tx238["x_emp_noise"], tx238["x_ap_noise"], tx238["x_naics_vintage"]), ("H", "J", "2022"))

    def test_a_state_twice_or_a_code_missing_stops(self):
        with self.assertRaises(RuntimeError):
            self.cbp.parse(zip_of([HEAD, "48,2362//,-,G,60,G,1,G,500,4", "48,2362//,-,G,61,G,1,G,501,4", "48,238///,-,G,1,G,1,G,1,1"]), 2023, {})
        with self.assertRaises(RuntimeError):
            self.cbp.parse(zip_of([HEAD, "48,2362//,-,G,60,G,1,G,500,4"]), 2023, {})

    def test_it_reads_the_hosting_connectors_saved_files(self):
        self.assertEqual(self.cbp.RAW_STORE, "census_cbp_hosting")


class TheAnnouncedDatacenters(unittest.TestCase):
    dca = load("warehouse/derived/datacenter_announced_table.py", "dca_t")
    ROW = {"id": "xx_example", "name": "Example campus", "company": "Example Co", "state": "xx", "county": "Example County",
           "doc": {"title": "t", "publisher": "p", "date": "2025-08", "url": "https://example.invalid/a", "request": 1},
           "mw": None,
           "investment": {"value": 1e9, "year": 2025, "says": "$1 billion", "qualifier": "", "quote": "It will invest $1 billion here."},
           "construction_jobs": None, "permanent_jobs": {"value": 50, "measure": "jobs", "says": "50 jobs", "qualifier": "at least",
                                                         "quote": "at least 50 jobs"},
           "incentive": "", "years": "", "note": ""}

    def test_a_month_dated_document_is_the_months_first_day_and_says_so(self):
        r = self.dca.row_of(self.ROW, "2026-11-26T00:00:00Z")
        self.assertEqual((r["event_date"], r["x_doc_date"], r["x_date_precision"]), ("2025-08-01", "2025-08", "month"))
        self.assertEqual(r["x_investment_usd"], 1e9)
        self.assertEqual(r["mw"], "")                       # not stated: empty, never filled
        self.assertEqual(r["x_permanent_jobs_qualifier"], "at least")

    def test_a_phrase_outside_its_sentence_or_a_row_twice_stops(self):
        bad = dict(self.ROW, investment=dict(self.ROW["investment"], says="$2 billion"))
        with self.assertRaises(RuntimeError):
            self.dca.check([bad])
        with self.assertRaises(RuntimeError):
            self.dca.check([self.ROW, self.ROW])
        self.dca.check([self.ROW])

    def test_the_table_is_internal_and_model_extracted(self):
        bc = load("warehouse/metadata/build_coverage.py", "bc_t")
        self.assertEqual(next(t for t, p in bc.TIER_RULES if __import__("re").match(p, "datacenter_announced")), "model_extracted")
        with open(os.path.join(ROOT, "warehouse", "derived", "datacenter_announced_table.py"), encoding="utf-8") as f:
            self.assertIn('"license": "internal"', f.read())


class EveryForecastIssueKept(unittest.TestCase):
    """Data request 4 of docs/state/data_requests_predict.md: weather_forecast_issued_hourly keeps each NWS issue."""

    def test_the_lead_is_in_the_variable_so_a_later_issue_never_replaces_an_earlier(self):
        import pandas as pd
        nws = load("warehouse/connectors/weather_nws.py", "nws_t")
        f = pd.DataFrame({"entity": ["nws:KDFW"] * 3, "variable": ["temperature_f"] * 3,
                          "ts_utc": ["2026-11-27T18:00:00Z", "2026-11-27T18:00:00Z", "2026-11-26T23:00:00Z"],
                          "vintage": ["2026-11-26T12:30:00Z", "2026-11-25T12:30:00Z", "2026-11-26T12:30:00Z"]})
        out = nws.issued(f)
        self.assertEqual(list(out["variable"]), ["temperature_f_lead1d", "temperature_f_lead2d", "temperature_f_lead0d"])
        self.assertFalse(out.duplicated(["entity", "variable", "ts_utc"]).any())
        with self.assertRaises(RuntimeError):
            nws.issued(f.assign(vintage=["", "x", "y"]))

    def test_the_runner_restores_a_rolling_table_the_archive_holds(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        rt = load("warehouse/restore_tables.py", "rt_t")
        with open(os.path.join(ROOT, "warehouse", "restore_tables.py"), encoding="utf-8") as f:
            self.assertIn("names |= set(pd.read_csv(ARCHIVE_MANIFEST", f.read())
        with open(os.path.join(ROOT, "warehouse", "redivis", "config.yaml"), encoding="utf-8") as f:
            self.assertIn("^weather_(obs|forecast|forecast_issued)_hourly$", f.read())
        self.assertTrue(callable(rt.rolling_tables))


if __name__ == "__main__":
    unittest.main()
