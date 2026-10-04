"""Session 99: who is buying. The buyer names of ferc_eqr_contracts by rule, the doubtful pairs, and the largest buyers
and sellers on /contracts.

Energy Research Warehouse (ERW). The table is internal: every name in this file is made up. The rules of
warehouse/derived/eqr_buyers.py one by one; what is merged and what is only listed; the totals on rows made here; the
loader's summary of the largest (warehouse/supabase/load.py eqr_largest) from tables written to a temporary folder; the
page's pure part, run by node; and that nothing of the real tables is in the repository. The view on a built site, against
a stand-in for the database, is site/scripts/check-contracts-largest.mjs.

    python -m unittest tests.test_session99 -v
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
import eqr_buyers as eb  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


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


def key(name):
    return eb.normalized(name)


class TheRules(unittest.TestCase):
    def test_each_rule_and_what_it_records(self):
        self.assertEqual(key("EXAMPLE POWER CO"), ("EXAMPLE POWER CO", []))
        self.assertEqual(key("Example  Power Co"), ("EXAMPLE POWER CO", ["case_space"]))
        self.assertEqual(key("Example Light & Power, Inc."), ("EXAMPLE LIGHT AND POWER INC", ["case_space", "punctuation"]))
        self.assertEqual(key("EXAMPLE LIGHT AND POWER INC")[0], key("Example Light & Power, Inc.")[0])
        self.assertEqual(key("Tri-Example Generation/Transmission")[0], "TRI EXAMPLE GENERATION TRANSMISSION")
        self.assertEqual(key("The Example Edison Company"), ("EXAMPLE EDISON CO", ["case_space", "leading_the", "abbreviation"]))
        self.assertEqual(key("Example Elec Coop")[0], key("EXAMPLE ELECTRIC COOPERATIVE")[0])
        self.assertEqual(key("Example Wind, L.L.C."), ("EXAMPLE WIND LLC", ["case_space", "punctuation"]))          # the periods gone, it is LLC already
        self.assertEqual(key("Example Wind L L C"), ("EXAMPLE WIND LLC", ["case_space", "legal_suffix"]))
        self.assertEqual(key("Example Hydro Limited Partnership")[0], "EXAMPLE HYDRO LP")
        self.assertEqual(key("Example Hydro, L. P.")[0], "EXAMPLE HYDRO LP")
        self.assertEqual(key("Example Bank, N.A.")[0], "EXAMPLE BANK NA")
        self.assertEqual(key("Example Power (US) Inc.")[0], "EXAMPLE POWER US INC")
        self.assertEqual(key("THE")[0], "THE")                                      # a name that is only "The" keeps it

    def test_co_is_left_alone_where_it_may_be_colorado(self):
        self.assertEqual(key("City of Example, CO")[0], "CITY OF EXAMPLE CO")
        self.assertEqual(key("Example Power Company")[0], "EXAMPLE POWER CO")
        self.assertEqual(key("Example Service Co of Somewhere")[0], "EXAMPLE SERVICE CO OF SOMEWHERE")
        self.assertEqual(eb.stem_and_form("EXAMPLE POWER CO"), ("EXAMPLE POWER", "CO"))
        self.assertEqual(eb.stem_and_form("CITY OF EXAMPLE CO"), ("CITY OF EXAMPLE CO", ""))   # not a legal form there
        self.assertEqual(eb.stem_and_form("EXAMPLE WIND"), ("EXAMPLE WIND", ""))

    def test_what_is_merged_and_what_is_only_listed(self):
        counts = {"Example Power Company": 50, "EXAMPLE POWER CO.": 5, "Example Power": 3,                  # one legal form: the bare name joins it
                  "Sample Energy LLC": 40, "Sample Energy, Inc.": 2, "Sample Energy": 1,                       # two legal forms: nothing merged
                  "Model Light Company d/b/a Model Lighting": 4, "Model Light Company": 30,                    # an extra clause
                  "Specimen Califormia Edison Company": 1, "Specimen California Edison Company": 90,           # a typing error
                  "Pattern Wind Farm I LLC": 6, "Pattern Wind Farm II LLC": 7,                                 # two projects
                  "Pattern Wind Farm II, L.L.C.": 1}
        mapping, doubtful = eb.groups_of(counts)
        group = lambda n: mapping[n][0]
        self.assertEqual(len({group(n) for n in ("Example Power Company", "EXAMPLE POWER CO.", "Example Power")}), 1)
        self.assertIn("suffix_left_off", mapping["Example Power"][1])
        self.assertEqual(len({group(n) for n in ("Sample Energy LLC", "Sample Energy, Inc.", "Sample Energy")}), 3)
        self.assertNotEqual(group("Model Light Company d/b/a Model Lighting"), group("Model Light Company"))
        self.assertNotEqual(group("Specimen Califormia Edison Company"), group("Specimen California Edison Company"))
        self.assertNotEqual(group("Pattern Wind Farm I LLC"), group("Pattern Wind Farm II LLC"))
        self.assertEqual(group("Pattern Wind Farm II LLC"), group("Pattern Wind Farm II, L.L.C."))
        self.assertEqual(len(set(g for g, _ in mapping.values())), 10)                                         # 13 names as filed are counted as 10
        pairs = {(frozenset((a, b)), reason) for a, b, reason, _ in doubtful}
        self.assertIn((frozenset(("SAMPLE ENERGY LLC", "SAMPLE ENERGY INC")), "different_legal_form"), pairs)
        self.assertIn((frozenset(("SAMPLE ENERGY LLC", "SAMPLE ENERGY")), "different_legal_form"), pairs)
        self.assertIn((frozenset(("MODEL LIGHT CO D B A MODEL LIGHTING", "MODEL LIGHT CO")), "extra_clause"), pairs)
        self.assertIn((frozenset(("SPECIMEN CALIFORMIA EDISON CO", "SPECIMEN CALIFORNIA EDISON CO")), "near_spelling"), pairs)
        self.assertFalse([p for p in doubtful if "PATTERN" in p[0]])                                           # a project's I and II are not a doubt
        self.assertEqual(len(doubtful), 5)
        shown = eb.display_names(mapping, counts)
        self.assertEqual(shown[group("Example Power")], "Example Power Company")                               # the spelling filed on the most rows

    def test_nothing_is_merged_by_likeness(self):
        code = src("warehouse", "derived", "eqr_buyers.py")
        merge = code[code.index("def groups_of"):code.index("    # extra_clause")]
        self.assertNotIn("difflib", merge)                                                                     # likeness is used only to list a pair
        self.assertNotIn("anthropic", code.lower())
        self.assertNotIn("requests", code)


class TheTotals(unittest.TestCase):
    def frame(self):
        rows = [("C1", "K1", "Example Power Company", "ENERGY", "in_force", "50"), ("C1", "K1", "Example Power Company", "CAPACITY", "in_force", ""),
                ("C1", "K2", "EXAMPLE POWER CO.", "Energy", "in_force", ""), ("C2", "K1", "Example Power", "ENERGY", "in_force", "10"),
                ("C2", "K9", "Sample Energy LLC", "ENERGY", "terminated", "99"), ("C2", "K3", "Sample Energy LLC", "TOLLING ENERGY", "in_force", ""),
                ("C3", "K1", "Sample Energy LLC", "NETWORK", "in_force", "")]
        return pd.DataFrame([dict(x_company_id=c, x_contract_unique_id=k, x_customer_company_name=b, x_product_name=p, status=s, mw=mw,
                                  x_seller_company_name=f"Seller {c}", x_quarter="2026_Q2") for c, k, b, p, s, mw in rows])

    def test_buyers_by_merged_name_and_sellers_by_identifier(self):
        d = self.frame()
        counts = d["x_customer_company_name"].value_counts().to_dict()
        mapping, _ = eb.groups_of(counts)
        totals, scope = eb.party_totals(d, mapping, eb.display_names(mapping, counts))
        self.assertEqual(len(scope), 5)                                                                        # in force, and one of the three products
        t = {(r["role"], r["product"], r["rank"]): r for r in totals}
        b = t[("buyer", "energy", 1)]
        self.assertEqual((b["name"], b["contracts"], b["rows"], b["counterparties"], b["mw_filed"], b["rows_with_mw"]), ("Example Power Company", 3, 3, 2, 60.0, 2))
        self.assertEqual({(r["role"], r["product"]) for r in totals}, {("buyer", "energy"), ("buyer", "capacity"), ("buyer", "tolling"), ("seller", "energy"), ("seller", "capacity"), ("seller", "tolling")})
        s = t[("seller", "energy", 1)]
        self.assertEqual((s["name"], s["company_id"], s["contracts"], s["counterparties"]), ("Seller C1", "C1", 2, 1))   # two spellings of its buyer are one counterparty
        self.assertEqual(t[("buyer", "tolling", 1)]["name"], "Sample Energy LLC")

    def test_the_loaders_summary_of_the_largest(self):
        import load
        d = self.frame()
        counts = d["x_customer_company_name"].value_counts().to_dict()
        mapping, doubtful = eb.groups_of(counts)
        shown = eb.display_names(mapping, counts)
        totals, _ = eb.party_totals(d, mapping, shown)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load.eqr_largest(out_dir=tmp))                                                   # no tables: no view, and the summary is as it was
            pd.DataFrame([dict(entity_id=f"p{i}", entity_type="company", name=r["name"], x_role=r["role"], x_product=r["product"], x_rank=r["rank"], x_contracts=r["contracts"],
                               x_rows=r["rows"], x_counterparties=r["counterparties"], x_mw_filed=r["mw_filed"], x_rows_with_mw=r["rows_with_mw"], x_quarter="2026_Q2")
                          for i, r in enumerate(totals)]).to_csv(os.path.join(tmp, "ferc_eqr_party_totals.csv"), index=False)
            pd.DataFrame([dict(entity_id=f"n{i}", name=raw, x_key=g, x_merged="yes" if sum(1 for v in mapping.values() if v[0] == g) > 1 else "no")
                          for i, (raw, (g, _)) in enumerate(mapping.items())]).to_csv(os.path.join(tmp, "ferc_eqr_buyer_names.csv"), index=False)
            pd.DataFrame([dict(event_id=f"d{i}", parties=f"{a};{b}") for i, (a, b, _, _) in enumerate(doubtful)], columns=["event_id", "parties"]).to_csv(os.path.join(tmp, "ferc_eqr_buyer_doubtful.csv"), index=False)
            got = load.eqr_largest(top=1, out_dir=tmp)
        self.assertEqual(got["names"], {"filed": 4, "after_rules": 2, "merged_groups": 1, "merged_names": 3, "doubtful_pairs": 0})
        e = got["lists"]["buyer"]["energy"]
        self.assertEqual((e["parties"], e["contracts"], e["rows"], len(e["top"]), e["top"][0]["name"], e["top"][0]["contracts"]), (1, 3, 3, 1, "Example Power Company", 3))
        self.assertEqual(got["lists"]["seller"]["energy"]["parties"], 2)
        json.dumps(got)
        ts = src("site", "lib", "contracts.ts")
        for k in ("quarter", "top", "names", "lists", "merged_names", "doubtful_pairs", "counterparties", "rows_with_mw"):
            self.assertIn(k, ts)
        d2 = node("import * as c from './lib/contracts.ts';"
                  "console.log(JSON.stringify([c.viewOf({}), c.viewOf({view:'largest', product:'tolling'}), c.viewOf({view:'x', product:'y'}), c.largestHref('capacity')]));")
        self.assertEqual([d2[0]["view"], d2[0]["product"]["slug"], d2[1]["view"], d2[1]["product"]["slug"], d2[2]["view"], d2[3]],
                         ["quarter", "energy", "largest", "tolling", "quarter", "/contracts?view=largest&product=capacity"])


class TheTablesStayInternal(unittest.TestCase):
    def test_the_tables_are_internal_and_out_of_git(self):
        code = src("warehouse", "derived", "eqr_buyers.py")
        self.assertEqual(code.count('license="internal"'), 1)
        self.assertIn("License: internal", code)
        r = subprocess.run(["git", "ls-files", "warehouse/output", "site/data", "site/public"], cwd=ROOT, capture_output=True, text=True)
        self.assertFalse([f for f in r.stdout.splitlines() if "eqr" in f.lower()])
        r = subprocess.run(["git", "check-ignore", "warehouse/output/ferc_eqr_buyer_names.csv", "warehouse/output/ferc_eqr_buyer_doubtful.csv",
                            "warehouse/output/ferc_eqr_party_totals.csv", "runs/session99/summary.json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(len(r.stdout.split()), 4)
        fixture = src("warehouse", "supabase", "eqr_fixture.py")
        self.assertIn("must stay out of git", fixture)
        page = src("site", "app", "contracts", "page.tsx")
        self.assertNotIn("@/data/", page)                                                                      # the page reads the database's stored summary, never a file of the site
        self.assertIn('export const dynamic = "force-dynamic"', page)

    def test_no_name_of_the_real_tables_is_in_the_repository(self):
        path = os.path.join(OUT, "ferc_eqr_party_totals.csv")
        if not os.path.exists(path):
            self.skipTest("the tables are not on this machine")
        import load
        top = load.eqr_largest(top=10)
        names = {r["name"] for role in top["lists"].values() for lst in role.values() for r in lst["top"] if len(r["name"]) >= 12}
        self.assertGreater(len(names), 20)
        for parts in (("docs", "methods", "eqr_buyers.md"), ("tests", "test_session99.py"), ("site", "app", "contracts", "page.tsx"), ("site", "lib", "contracts.ts"),
                      ("site", "scripts", "check-contracts-largest.mjs"), ("warehouse", "derived", "eqr_buyers.py"), ("warehouse", "supabase", "eqr_fixture.py")):
            text = src(*parts)
            self.assertFalse([n for n in names if n in text], parts)
        report = os.path.join(ROOT, "archive", "sessions", "SESSION_99_REPORT.md")
        if os.path.exists(report):
            with open(report, encoding="utf-8") as f:
                text = f.read()
            self.assertFalse([n for n in names if n in text])

    def test_the_tables_as_built(self):
        path = os.path.join(OUT, "ferc_eqr_buyer_names.csv")
        if not os.path.exists(path):
            self.skipTest("the tables are not on this machine")
        import load
        got = load.eqr_largest()
        n = got["names"]
        self.assertEqual(n["filed"], 17955)
        self.assertLess(n["after_rules"], n["filed"])
        self.assertGreater(n["doubtful_pairs"], 0)
        self.assertEqual(n["filed"] - n["after_rules"], n["merged_names"] - n["merged_groups"])               # every name less is a name merged into a group
        for product in ("energy", "capacity", "tolling"):
            b, s = got["lists"]["buyer"][product], got["lists"]["seller"][product]
            self.assertEqual((b["contracts"], b["rows"]), (s["contracts"], s["rows"]))                         # each contract has one buyer and one seller
            self.assertEqual([r["rank"] for r in b["top"]], list(range(1, len(b["top"]) + 1)))
            self.assertEqual(sorted((r["contracts"] for r in b["top"]), reverse=True), [r["contracts"] for r in b["top"]])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "derived", "eqr_buyers.py"), ("warehouse", "supabase", "eqr_fixture.py"), ("docs", "methods", "eqr_buyers.md"),
                      ("site", "scripts", "check-contracts-largest.mjs"), ("site", "app", "contracts", "page.tsx"), ("tests", "test_session99.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
