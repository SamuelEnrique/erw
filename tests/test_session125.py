"""Session 125: the contracts tracker, to useful. Megawatts where a quantity is stated, a price read from the words only
where number and unit leave one reading, tags from the product fields, contracts new and gone by quarter, and the
approved pull of three earlier quarters.

Energy Research Warehouse (ERW). The tables are internal: every name and every rate description in this file is made
up. The rules of warehouse/derived/eqr_terms.py one by one; the ranking and the changes on rows made here; the loader's
summary (warehouse/supabase/load.py eqr_terms) from tables written to a temporary folder; the connector's pull ceiling
and history mode; the page's pure part, run by node; and that nothing of the real tables is in the repository.

    python -m unittest tests.test_session125 -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eqr_terms as et  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
TABLES = ("ferc_eqr_contracts_history", "ferc_eqr_contract_terms", "ferc_eqr_party_mw", "ferc_eqr_quarter_changes")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def table(path):
    import iso_prices as ip
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, low_memory=False)


class APriceFromTheWords(unittest.TestCase):
    def test_one_amount_with_its_unit_is_read(self):
        for text, want in (("$42.50 per MWh", (42.5, "$/MWH")), ("$42.50/mwh", (42.5, "$/MWH")), ("Contract price of $27.00/MWh.  Bundled RECs.", (27.0, "$/MWH")),
                           ("$0.045/kWh", (0.045, "$/KWH")), ("$6.25/kw-month", (6.25, "$/KW-MO")), ("$4.50 per kw month", (4.5, "$/KW-MO")), ("$6.8/KW-mo", (6.8, "$/KW-MO")),
                           ("Firm Capacity Price=$14,250.00/MW-month", (14250.0, "$/MW-MO")), ("$163/MW-day", (163.0, "$/MW-DAY")), ("$ 3.25/kW-Month", (3.25, "$/KW-MO")),
                           ("$30.00 per kW-yr", (30.0, "$/KW-YR")), ("$2.00 per KW-WK", (2.0, "$/KW-WK"))):
            self.assertEqual(et.read_price(text), (want[0], want[1], ""), text)

    def test_a_quantity_beside_the_amount_is_allowed_and_no_other_number_is(self):
        self.assertEqual(et.read_price("40 MW; $8.00/kW-month"), (8.0, "$/KW-MO", ""))
        self.assertEqual(et.read_price("7.5 MW; $8.50/kw-mo"), (8.5, "$/KW-MO", ""))
        self.assertEqual(et.read_price("3rd Amendment; $1.50/MWh")[2], "other_numbers")
        self.assertEqual(et.read_price("Rate Schedule No. 96, section 3, $2.78/MWH")[2], "other_numbers")

    def test_each_reason_a_row_stays_unread(self):
        for text, why in (("Market Based Rate", "no_dollar_amount"), ("Per Schedule 4 of the Tariff", "no_dollar_amount"), ("", "no_dollar_amount"),
                          ("2027: $40.00/MWh, 2028: $41.00/MWh", "several_amounts"), ("On-peak $50/MWh; off-peak $30/MWh", "several_amounts"),
                          ("Deposit: $10,000", "no_unit"), ("$1.50 per kW of demand", "no_unit"), ("Rate is $0.00", "no_unit"), ("($44.00 less the settlement price)", "no_unit"),
                          ("$50/MWh, escalating at 2 percent a year", "conditional"), ("$0.004/kwh, plus charges for ancillary services", "conditional"),
                          ("At a rate agreed before the transaction but in no case more than $2.00 per KW-WK.", "conditional"),
                          ("If inadvertent flow occurs the rate will be at $2.77 per KW Month.", "conditional"),
                          ("Standard Energy = [(Delivered Energy)($79.90/MWH)](Time of Day Factor)", "conditional"),
                          ("Capacity charge of $3/MWH, which may be revised by mutual agreement.", "conditional"),
                          ("$65/MWh in 2030", "conditional"), ("$12.00/kW-month through 12/31/2030", "conditional"), ("LMP minus $15/MWh", "conditional")):
            self.assertEqual(et.read_price(text), (None, "", why), text)

    def test_the_filed_unit_must_agree_with_the_words(self):
        self.assertEqual(et.read_price("$16.00/MWh", "$/MWH"), (16.0, "$/MWH", ""))
        self.assertEqual(et.read_price("$16.00/MWh", "$/KW-MO"), (None, "", "units_disagree"))
        self.assertEqual(et.read_price("$16.00/MWh", "FLAT RATE"), (None, "", "units_disagree"))
        self.assertEqual(et.read_price("$16.00/MWh", ""), (16.0, "$/MWH", ""))

    def test_only_an_energy_price_becomes_usd_per_mwh(self):
        self.assertEqual(et.PER_MWH, {"$/MWH": 1.0, "$/KWH": 1000.0})          # a capacity price per kW and month is kept in its unit, never converted
        d = made([dict(n=1, rate="", rate_units="", text="$40.00 per MWh"), dict(n=2, rate="", rate_units="", text="$0.04/kWh"), dict(n=3, rate="", rate_units="", text="$8.00/kW-month"),
                  dict(n=4, rate="25", rate_units="$/MWH", text="words beside a number"), dict(n=5, rate="132000", rate_units="$/MW-MO", text=""), dict(n=6, rate="", rate_units="", text="Market Based")])
        t = terms_of(d)
        self.assertEqual(list(t["price"]), [40.0, 40.0, "", 25.0, "", ""])
        self.assertEqual(list(t["x_price_source"]), ["words", "words", "", "filed", "", ""])
        self.assertEqual(list(t["x_price_words"]), [40.0, 0.04, 8.0, "", "", ""])
        self.assertEqual(list(t["x_price_words_unit"]), ["$/MWH", "$/KWH", "$/KW-MO", "", "", ""])
        self.assertEqual(list(t["x_price_unread"]), ["", "", "", "", "", "no_dollar_amount"])
        self.assertEqual(list(t["x_rate_kind"]), ["words", "words", "words", "number", "number", "words"])
        self.assertEqual(list(t["currency"]), ["USD", "USD", "", "USD", "", ""])   # the known fault (a monthly rate that cannot be one) is a filed number and is not read as a price


def made(rows):
    """Contract rows in the connector's columns, from short made-up dicts."""
    out = []
    for r in rows:
        n = r["n"]
        out.append({"event_id": f"ferc_eqr:2026_Q2:C{r.get('company', 1)}:K{r.get('contract', n)}:{n}", "event_date": "2025-01-01T00:00:00Z", "entity_ids": "", "status": r.get("status", "in_force"),
                    "x_seller_company_name": r.get("seller", "Example Generating LLC"), "x_customer_company_name": r.get("buyer", "Example Power Co"), "x_company_id": f"C{r.get('company', 1)}",
                    "x_contract_unique_id": f"K{r.get('contract', n)}", "x_quantity": r.get("quantity", ""), "x_units": r.get("units", ""), "x_rate": r.get("rate", ""),
                    "x_rate_units": r.get("rate_units", ""), "x_rate_description": r.get("text", ""), "x_product_name": r.get("product", "ENERGY"), "x_product_type_name": r.get("type", "MB"),
                    "x_class_name": "F", "x_term_name": "LT", "x_increment_name": "Y", "x_contract_service_agreement_id": r.get("agreement", "SA-1"), "x_ferc_tariff_reference": r.get("tariff", "Tariff 1"),
                    "x_quarter": r.get("quarter", "2026_Q2")})
    return pd.DataFrame(out)


def terms_of(d, names=None, ceiling=6809.0):
    key = et.contract_key(d)
    return et.terms(d, names or {}, pd.Series(dtype=str), pd.Series(dtype=int), "2026-10-05T00:00:00Z", ceiling)


class Megawatts(unittest.TestCase):
    def test_only_mw_and_kw_are_megawatts(self):
        self.assertEqual(et.stated_mw("50", "MW"), (50.0, "MW"))
        self.assertEqual(et.stated_mw("2,500", "kW"), (2.5, "KW"))
        for q, u in (("50", "MWH"), ("50", "MW-MO"), ("50", ""), ("", "MW"), ("0", "MW"), ("n/a", "MW"), ("50", "FLAT RATE")):
            self.assertEqual(et.stated_mw(q, u), (None, ""), (q, u))

    def test_a_figure_above_the_largest_station_is_kept_as_filed_and_not_ranked(self):
        d = made([dict(n=1, quantity="100", units="MW"), dict(n=2, quantity="600000", units="MW"), dict(n=3, quantity="6809", units="MW"), dict(n=4, quantity="", units="")])
        t = terms_of(d)
        self.assertEqual(list(t["mw"]), [100.0, 600000.0, 6809.0, ""])
        self.assertEqual(list(t["x_mw_ranked"]), ["yes", "no", "yes", ""])

    def test_the_ceiling_is_read_from_the_warehouse(self):
        code = src("warehouse", "derived", "eqr_terms.py")
        self.assertIn('PLANTS = "eia860m_operating_generators"', code)
        self.assertNotIn("6809.0", code)                                           # never typed in as a constant
        if not os.path.exists(os.path.join(OUT, et.PLANTS + ".csv")):
            self.skipTest("the generator inventory is not on this machine")
        mw, vintage = et.largest_plant(OUT)
        self.assertTrue(5000 < mw < 10000, mw)
        self.assertRegex(vintage, r"^\d{4}-\d{2}$")

    def test_the_ranking_takes_a_contract_once_and_leaves_out_what_is_over(self):
        d = made([dict(n=1, contract=1, quantity="100", units="MW"), dict(n=2, contract=1, quantity="80", units="MW"),           # one contract, two periods: 100, not 180
                  dict(n=3, contract=2, quantity="50", units="MW"), dict(n=4, contract=3, quantity="500000", units="MW"),          # over: left out, counted
                  dict(n=5, contract=4, quantity="", units=""),                                                                    # states nothing
                  dict(n=6, contract=5, company=2, seller="Sample Wind LLC", buyer="Sample City Light", quantity="30000", units="KW"),
                  dict(n=7, contract=6, quantity="75", units="MW", status="terminated"),                                          # not in force
                  dict(n=8, contract=7, quantity="20", units="MW", product="TRANSMISSION")])                                       # not one of the three products
        t = terms_of(d)
        scope = t.assign(seller=d["x_seller_company_name"].values, company_id=d["x_company_id"].values)
        rows = et.party_mw(scope)
        buyers = {r["name"]: r for r in rows if r["role"] == "buyer"}
        self.assertEqual((buyers["Example Power Co"]["mw"], buyers["Example Power Co"]["contracts_with_mw"], buyers["Example Power Co"]["contracts"], buyers["Example Power Co"]["contracts_over"]), (150.0, 2, 4, 1))
        self.assertEqual((buyers["Sample City Light"]["mw"], buyers["Sample City Light"]["rank_mw"]), (30.0, 2))
        sellers = {r["name"]: r for r in rows if r["role"] == "seller"}
        self.assertEqual(sellers["Example Generating LLC"]["mw"], 150.0)
        self.assertEqual({r["product"] for r in rows}, {"energy"})


class Tags(unittest.TestCase):
    def test_tolling_is_the_product_name_and_storage_needs_a_product_field(self):
        self.assertEqual(et.tag_of({"x_product_name": "Tolling Energy"}), "tolling")
        self.assertEqual(et.tag_of({"x_product_name": "ENERGY", "x_product_type_name": "MB"}), "")
        self.assertEqual(et.tag_of({"x_product_name": "ENERGY STORAGE"}), "storage")                # would be tagged, if FERC's product list had one
        d = made([dict(n=1, seller="Example Battery Storage LLC", text="Demonstrated Storage Capacity price per the BESS test", agreement="BESS-1", tariff="Storage Schedule 2"),
                  dict(n=2, product="TOLLING ENERGY")])
        t = terms_of(d)
        self.assertEqual(list(t["x_tag"]), ["", "tolling"])                                         # the words elsewhere are not a tag
        self.assertEqual(t["x_storage_words_in"].iat[0], "rate_description;agreement_id;tariff_reference;seller_name")
        self.assertEqual(t["x_storage_words_in"].iat[1], "")
        self.assertEqual(et.PRODUCT_FIELDS, ["x_product_name", "x_product_type_name", "x_class_name", "x_term_name", "x_increment_name"])


class Buyers(unittest.TestCase):
    def test_only_rule_merges_are_applied(self):
        d = made([dict(n=1, buyer="EXAMPLE POWER CO"), dict(n=2, buyer="Example Power Company"), dict(n=3, buyer="Example Power Inc")])
        names = {"EXAMPLE POWER CO": ("Example Power Company", "yes"), "Example Power Company": ("Example Power Company", "yes")}   # the Inc form is a doubtful pair: in no mapping
        t = terms_of(d, names)
        self.assertEqual(list(t["x_buyer_counted_as"]), ["Example Power Company", "Example Power Company", "Example Power Inc"])
        self.assertEqual(list(t["x_buyer_merged"]), ["yes", "yes", "no"])
        self.assertEqual(t["parties"].iat[0], "Example Generating LLC;Example Power Company")
        self.assertEqual(list(t["x_buyer_as_filed"]), list(d["x_customer_company_name"]))
        code = src("warehouse", "derived", "eqr_terms.py")
        self.assertNotIn("ferc_eqr_buyer_doubtful.csv", code)                                       # the doubtful pairs are read by nothing here
        self.assertNotIn("import eqr_buyers as eb\neb.main", code)


class Quarters(unittest.TestCase):
    def frames(self):
        q1 = made([dict(n=1, contract=1, quarter="2026_Q1"), dict(n=2, contract=2, quarter="2026_Q1"), dict(n=3, contract=3, quarter="2026_Q1", product="CAPACITY"),
                   dict(n=4, contract=9, quarter="2026_Q1", status="terminated")])
        q2 = made([dict(n=1, contract=1), dict(n=5, contract=1), dict(n=6, contract=4), dict(n=7, contract=3, product="CAPACITY")])
        return {"2026_Q1": q1, "2026_Q2": q2}

    def test_new_gone_and_kept(self):
        got = {(r["quarter"], r["product"], r["variable"]): r["value"] for r in et.quarter_changes(self.frames())}
        self.assertEqual(got[("2026_Q1", "all", "contracts_in_force")], 3)                          # the terminated one is not in force
        self.assertEqual((got[("2026_Q2", "all", "contracts_in_force")], got[("2026_Q2", "all", "rows_in_force")]), (3, 4))
        self.assertEqual((got[("2026_Q2", "all", "contracts_new")], got[("2026_Q2", "all", "contracts_gone")], got[("2026_Q2", "all", "contracts_kept")]), (1, 1, 2))
        self.assertEqual((got[("2026_Q2", "energy", "contracts_new")], got[("2026_Q2", "energy", "contracts_gone")], got[("2026_Q2", "energy", "contracts_kept")]), (1, 1, 1))
        self.assertEqual(got[("2026_Q2", "capacity", "contracts_kept")], 1)
        self.assertNotIn(("2026_Q1", "all", "contracts_new"), got)                                  # no quarter before it is held

    def test_a_gap_between_quarters_writes_no_change(self):
        f = self.frames()
        f["2025_Q3"] = f.pop("2026_Q1").assign(x_quarter="2025_Q3")
        got = {(r["quarter"], r["product"], r["variable"]) for r in et.quarter_changes(f)}
        self.assertNotIn(("2026_Q2", "all", "contracts_new"), got)                                  # two quarters' worth of change is not one quarter's
        self.assertIn(("2026_Q2", "all", "contracts_in_force"), got)
        self.assertEqual(et.quarter_start("2025_Q4"), "2025-10-01T00:00:00Z")


class TheLoadersSummary(unittest.TestCase):
    def test_the_summary_from_made_tables(self):
        import load
        d = made([dict(n=1, contract=1, quantity="100", units="MW", text="$40.00 per MWh"), dict(n=2, contract=2, quantity="500000", units="MW", text="Market Based"),
                  dict(n=3, contract=3, rate="30", rate_units="$/MWH"), dict(n=4, contract=4, product="TOLLING ENERGY", seller="Example Battery Storage LLC", text="$9.00/kW-month"),
                  dict(n=5, contract=5)])
        t = terms_of(d)
        scope = t.assign(seller=d["x_seller_company_name"].values, company_id=d["x_company_id"].values)
        pm = pd.DataFrame([dict(name=r["name"], x_role=r["role"], x_product=r["product"], x_rank_mw=r["rank_mw"], x_mw_stated=r["mw"], x_contracts_with_mw=r["contracts_with_mw"],
                                x_contracts=r["contracts"], x_rank_contracts=r["rank_contracts"], x_contracts_over=r["contracts_over"], x_mw_ceiling=6809.0) for r in et.party_mw(scope)])
        ch = pd.DataFrame([dict(entity=f"ferc_eqr:{r['product']}", variable=r["variable"], ts_utc=et.quarter_start(r["quarter"]), value=r["value"])
                           for r in et.quarter_changes({"2026_Q1": d.assign(x_quarter="2026_Q1").iloc[:3], "2026_Q2": d})])
        tmp = tempfile.mkdtemp()
        try:
            for name, frame in (("ferc_eqr_contract_terms", t), ("ferc_eqr_party_mw", pm), ("ferc_eqr_quarter_changes", ch)):
                frame.to_csv(os.path.join(tmp, name + ".csv"), index=False)
            got = load.eqr_terms(out_dir=tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        json.dumps(got)
        self.assertEqual((got["quarter"], got["rows"], got["mw_ceiling"]), ("2026_Q2", 5, 6809.0))
        self.assertEqual(got["prices"], {"filed_number": 1, "none": 1, "words_only": 3, "read": 2, "read_usd_per_mwh": 1, "read_by_unit": {"$/MWH": 1, "$/KW-MO": 1}, "unread": {"no_dollar_amount": 1}})
        self.assertEqual(got["mw"]["by_product"]["energy"], {"contracts": 4, "contracts_with_mw": 1, "contracts_over": 1})
        self.assertEqual((got["mw"]["rows_stated"], got["mw"]["rows_over"]), (2, 1))
        self.assertEqual((got["tags"]["tolling_rows"], got["tags"]["tolling_contracts"], got["tags"]["storage_rows"], got["tags"]["storage_words_rows"]), (1, 1, 0, 1))
        self.assertEqual(got["tags"]["storage_words_elsewhere"]["seller_name"], 1)
        e = got["by_mw"]["buyer"]["energy"]
        self.assertEqual((e["parties"], e["mw"], e["contracts_with_mw"], e["top"][0]["name"], e["top"][0]["mw"], e["top"][0]["contracts_over"]), (1, 100.0, 1, "Example Power Co", 100.0, 1))
        self.assertEqual(got["by_mw"]["buyer"]["tolling"]["parties"], 0)
        last = [c for c in got["changes"] if c["quarter"] == "2026_Q2" and c["product"] == "all"][0]
        self.assertEqual((last["contracts_in_force"], last["contracts_new"], last["contracts_gone"], last["contracts_kept"]), (5, 2, 0, 3))
        self.assertIsNone(load.eqr_terms(out_dir=os.path.join(tmp, "nothing")))

    def test_the_summary_is_stored_with_the_page_s_summary(self):
        code = src("warehouse", "supabase", "load.py")
        self.assertIn('out["terms"] = terms', code)
        self.assertIn('out["largest"] = largest', code)                                             # session 99's is kept


class ThePull(unittest.TestCase):
    def test_the_ceiling_the_pause_and_the_two_modes(self):
        code = src("warehouse", "connectors", "ferc_eqr_contracts.py")
        self.assertIn("PULL_CEILING = 800_000", code)
        self.assertIn("CEILING = 400_000", code)                                                    # one run's, as session 83 set it
        self.assertIn('HISTORY = "ferc_eqr_contracts_history"', code)
        for flag in ('"--fetch-only"', '"--history"', '"--also"'):
            self.assertIn(flag, code)
        self.assertIn('ip.paused("ferc")', code)
        self.assertIn("if prior + n_rows + len(rows) > PULL_CEILING:", code)
        self.assertIn("table = HISTORY if args.history else NAME", code)
        self.assertIn("documents = kept.iloc[0] if len(kept) else documents", code)                 # the registry's row keeps naming the newest quarter's file

    def test_a_filing_that_is_not_a_zip_is_asked_for_twice_then_left_out_and_counted(self):
        code = src("warehouse", "connectors", "ferc_eqr_contracts.py")
        loop = code[code.find("unreadable = []"):code.find("if args.fetch_only:")]
        self.assertEqual(loop.count("except zipfile.BadZipFile:"), 2)                               # the first read, and the second
        self.assertEqual(loop.count("member(f, name, ctype, csize, off)"), 2)
        self.assertIn("unreadable=True", loop)
        self.assertIn("the filing is left out and counted", loop)
        self.assertIn('if name in index and index[name].get("unreadable"):', loop)                  # a later run does not ask for it again
        self.assertIn("left out because the file FERC serves for them is not a zip file (named in the run log)", code)
        self.assertNotIn("except Exception:\n                    continue", loop)                    # no other failure is passed over

    def test_the_registry_row_shown_on_terms_kept_its_words(self):
        import csv
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8", newline="") as f:
            reg = {r["source"]: r for r in csv.DictReader(f)}
        r = reg["ferc:eqr"]
        self.assertEqual((r["publisher"], r["report"], r["report_url"], r["license"]),
                         ("Federal Energy Regulatory Commission (FERC)", "Electric Quarterly Reports (EQR): contracts, quarterly filings of all companies", "https://eqrreportviewer.ferc.gov/", "internal"))
        self.assertIn("CSV_2026_Q2.zip", r["document_list"])
        self.assertEqual(reg["erw:eqr_terms"]["license"], "internal")
        self.assertEqual(set(reg["erw:eqr_terms"]["tables"].split(";")), {"ferc_eqr_contract_terms", "ferc_eqr_party_mw", "ferc_eqr_quarter_changes"})


class TheTablesStayInternal(unittest.TestCase):
    def test_none_is_loaded_and_the_source_is_held_off_the_terms_page(self):
        import load
        for t in TABLES:
            self.assertIsNone(load.live_rule(t), t)
        self.assertIn("erw:eqr_terms", load.LIVE["sources_hold"])
        self.assertEqual(load.live_rule("ferc_eqr_contracts"), ("full", None))
        import importlib.util
        spec = importlib.util.spec_from_file_location("erw_build_coverage", os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"))
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        for t in TABLES:
            self.assertEqual(bc.sector_of(t), "power", t)

    def test_internal_and_out_of_git(self):
        code = src("warehouse", "derived", "eqr_terms.py")
        self.assertEqual(code.count('license="internal"'), 1)
        self.assertIn("License: internal", code)
        r = subprocess.run(["git", "ls-files", "warehouse/output", "warehouse/raw", "site/data", "site/public"], cwd=ROOT, capture_output=True, text=True)
        self.assertFalse([f for f in r.stdout.splitlines() if "eqr" in f.lower()])
        r = subprocess.run(["git", "check-ignore"] + [f"warehouse/output/{t}.csv" for t in TABLES] + ["warehouse/raw/ferc_eqr_contracts/2026_Q1/index.json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(len(r.stdout.split()), 5)
        if os.path.exists(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")):
            cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
            mine = cov[cov["table"].isin(TABLES)]
            self.assertEqual(set(mine["license"]), {"internal"})
            self.assertEqual(len(mine), 4)

    def test_no_name_of_the_real_tables_is_in_the_repository(self):
        path = os.path.join(OUT, "ferc_eqr_party_mw.csv")
        if not os.path.exists(path):
            self.skipTest("the tables are not on this machine")
        m = table(path)
        names = {n for n in m["name"] if len(n) >= 12}
        self.assertGreater(len(names), 50)
        for parts in (("docs", "methods", "eqr_terms.md"), ("tests", "test_session125.py"), ("site", "app", "contracts", "page.tsx"), ("site", "lib", "contracts.ts"),
                      ("warehouse", "derived", "eqr_terms.py"), ("warehouse", "supabase", "load.py"), ("archive", "sessions", "SESSION_125_REPORT.md")):
            if not os.path.exists(os.path.join(ROOT, *parts)):
                continue
            text = src(*parts)
            self.assertFalse([n for n in names if n in text], parts)


class AsBuilt(unittest.TestCase):
    def setUp(self):
        self.paths = {t: os.path.join(OUT, t + ".csv") for t in TABLES + ("ferc_eqr_contracts",)}
        if not all(os.path.exists(p) for p in self.paths.values()):
            self.skipTest("the tables are not on this machine")

    def test_the_terms_follow_the_contracts_row_for_row(self):
        t, d = table(self.paths["ferc_eqr_contract_terms"]), table(self.paths["ferc_eqr_contracts"])
        d = d[d["x_quarter"] == d["x_quarter"].max()]
        self.assertEqual(list(t["event_id"]), list(d["event_id"]))
        words = t[t["x_rate_kind"] == "words"]
        read = t[t["x_price_words"] != ""]
        self.assertEqual(len(words), len(read) + int((words["x_price_unread"] != "").sum()))        # every worded rate is read or says why not
        self.assertTrue((read["x_rate_kind"] == "words").all())
        self.assertLess(len(read), 0.01 * len(words))                                               # the finding: almost none can be read
        self.assertTrue(set(words["x_price_unread"]) <= set(et.REASONS) | {""})
        by_words = t[t["x_price_source"] == "words"]
        self.assertTrue(set(by_words["x_price_words_unit"]) <= {"$/MWH", "$/KWH"})
        self.assertEqual(int((t["x_tag"] == "storage").sum()), 0)                                   # FERC's product list has no storage product
        self.assertGreater(int((t["x_tag"] == "tolling").sum()), 100)
        self.assertGreater(int((t["x_storage_words_in"] != "").sum()), 500)
        mw = pd.to_numeric(t["mw"], errors="coerce")
        ceiling, _ = et.largest_plant(OUT)
        self.assertTrue((mw[t["x_mw_ranked"] == "no"] > ceiling).all())
        self.assertTrue((mw[t["x_mw_ranked"] == "yes"] <= ceiling).all() and (mw[t["x_mw_ranked"] == "yes"] > 0).all())
        self.assertTrue((t["x_buyer_merged"].isin(["yes", "no"])).all())

    def test_the_ranking_and_the_quarters(self):
        m, c, h = table(self.paths["ferc_eqr_party_mw"]), table(self.paths["ferc_eqr_quarter_changes"]), table(self.paths["ferc_eqr_contracts_history"])
        ceiling, _ = et.largest_plant(OUT)
        for (role, product), g in m.groupby(["x_role", "x_product"]):
            mw = g.sort_values("x_rank_mw", key=lambda s: s.astype(int))["x_mw_stated"].astype(float)
            self.assertTrue(mw.is_monotonic_decreasing, (role, product))
            self.assertTrue((g["x_contracts_with_mw"].astype(int) <= g["x_contracts"].astype(int)).all())
        for product in ("energy", "capacity", "tolling"):                                           # every megawatt has a buyer and a seller
            b = m[(m["x_role"] == "buyer") & (m["x_product"] == product)]["x_mw_stated"].astype(float).sum()
            s = m[(m["x_role"] == "seller") & (m["x_product"] == product)]["x_mw_stated"].astype(float).sum()
            self.assertAlmostEqual(b, s, places=1)
        self.assertEqual(set(m["x_mw_ceiling"].astype(float)), {ceiling})
        quarters = sorted(h["x_quarter"].unique())
        self.assertNotIn("2026_Q2", quarters)                                                       # the newest quarter is the other table
        self.assertTrue(set(quarters) <= {"2026_Q1", "2025_Q4", "2025_Q3"})                         # only the pull named
        self.assertLess(len(h) + 0, 800_000)
        self.assertFalse(h["event_id"].duplicated().any())
        v = {(r.ts_utc, r.entity, r.variable): float(r.value) for r in c.itertuples()}
        last = "2026-04-01T00:00:00Z"
        self.assertEqual(v[(last, "ferc_eqr:all", "contracts_in_force")], v[(last, "ferc_eqr:all", "contracts_new")] + v[(last, "ferc_eqr:all", "contracts_kept")])
        self.assertEqual(set(c["unit"]), {"count"})


class ThePage(unittest.TestCase):
    def test_the_views_and_their_words(self):
        page = src("site", "app", "contracts", "page.tsx")
        for words in ("Ranked by megawatts stated", "What the filings state", "function MwView(", "function TermsView(", "it is not a ranking of the market",
                      "Contracts left out as not megawatts", "Why a rate in words was not read", "Never estimated", "FERC's terms for this data", "91 FR 7278", "91 FR 14306",
                      "HTTP 403", "That was not worked around", "no row is tagged", "are not merged in any figure on this page", "Contracts new and gone, by quarter"):
            self.assertIn(words, page, words)
        self.assertIn("LargestView", page)                                                          # session 99's view is as it was
        self.assertNotIn("@/data/", page)
        self.assertIn('export const dynamic = "force-dynamic"', page)
        release = src("site", "lib", "release.ts")
        self.assertNotRegex(release, r'live[^\n]*"/contracts"')                                     # still in review

    def test_the_pure_part(self):
        got = node("import * as c from './lib/contracts.ts';"
                   "const t = {changes: [{quarter:'2026_Q2', product:'all', contracts_in_force: 3, rows_in_force: 4}, {quarter:'2026_Q1', product:'all', contracts_in_force: 2, rows_in_force: 2},"
                   " {quarter:'2026_Q2', product:'energy', contracts_in_force: 1, rows_in_force: 1}]};"
                   "console.log(JSON.stringify([c.viewOf({view:'mw', product:'capacity'}), c.viewOf({view:'terms'}), c.viewOf({view:'largest'}), c.viewOf({view:'x'}), c.mwHref('tolling'),"
                   " c.changesOf(t, 'all').map((x) => x.quarter), c.UNREAD.map((u) => u.key), c.STORAGE_FIELDS.map((f) => f.key)]));")
        self.assertEqual([got[0]["view"], got[0]["product"]["slug"], got[1]["view"], got[2]["view"], got[3]["view"], got[4]], ["mw", "capacity", "terms", "largest", "quarter", "/contracts?view=mw&product=tolling"])
        self.assertEqual(got[5], ["2026_Q1", "2026_Q2"])
        self.assertEqual(got[6], et.REASONS)                                                        # the page lists the reasons the rule gives, in its order
        self.assertEqual(set(got[7]), set(et.OTHER_FIELDS.values()))


class TheWords(unittest.TestCase):
    def test_the_method_quotes_ferc_and_says_what_could_not_be_read(self):
        doc = src("docs", "methods", "eqr_terms.md")
        for words in ("while making data available\n  to the public", "public inspection in a convenient form and place", "HTTP 403", "That was not worked around", "stay internal",
                      "eia860m_operating_generators", "never turned into dollars per megawatt-hour", "1,281 doubtful pairs", "None does."):
            self.assertIn(words, doc, words)

    def test_no_em_dash_in_the_session_s_files(self):
        for parts in (("docs", "methods", "eqr_terms.md"), ("tests", "test_session125.py"), ("site", "app", "contracts", "page.tsx"), ("site", "lib", "contracts.ts"),
                      ("warehouse", "derived", "eqr_terms.py"), ("warehouse", "connectors", "ferc_eqr_contracts.py"), ("warehouse", "supabase", "load.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
