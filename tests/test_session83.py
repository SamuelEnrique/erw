"""Session 83: FERC's Electric Quarterly Report contracts (warehouse/connectors/ferc_eqr_contracts.py), the internal
table ferc_eqr_contracts, and the review page /contracts.

Energy Research Warehouse (ERW). No request leaves the machine: the filings read here are made in memory, and they
are made up (company names that do not exist), only to exercise the shaping. The table itself is tested where the
machine holds it.

    python -m unittest tests.test_session83 -v
"""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
for p in ("warehouse", "warehouse/connectors", "warehouse/supabase"):
    sys.path.insert(0, os.path.join(ROOT, p))

import ferc_eqr_contracts as eqr  # noqa: E402

TABLE = os.path.join(ROOT, "warehouse", "output", "ferc_eqr_contracts.csv")


def row(**kv):
    d = dict.fromkeys(eqr.FERC_COLS, "")
    d.update(contract_unique_id="C1", seller_company_name="Made Up Wind, LLC", customer_company_name="Made Up Utility Co",
             contract_execution_date="20260415", product_name="ENERGY", product_type_name="MB")
    d.update(kv)
    return [d[c] for c in eqr.FERC_COLS]


def filing(contracts, cid="C000001", cname="Made Up Wind, LLC", header=None):
    """A filing's zip as FERC lays it out: a contracts file and an ident file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        lines = [",".join(header or eqr.FERC_COLS)] + [",".join('"' + c.replace('"', '""') + '"' for c in r) for r in contracts]
        z.writestr("x_contracts.csv", "\n".join(lines) + "\n")
        z.writestr("x_ident.csv", "company_identifier,company_name,filing_quarter,contact_name\n"
                   f'{cid},"{cname}",202606,Somebody\n')
        z.writestr("x_transactions.csv", "a,b\n1,2\n")
    return buf.getvalue()


class Shaping(unittest.TestCase):
    def test_dates_and_numbers_are_read_or_left_alone(self):
        self.assertEqual(eqr.ymd("20260415"), "2026-04-15")
        for bad in ("", "2026-04-15", "20261340", "N/A", None):
            self.assertIsNone(eqr.ymd(bad))
        self.assertEqual(eqr.number("1,250.5"), 1250.5)
        for bad in ("", "Market Based Rate", "nan", "inf"):
            self.assertIsNone(eqr.number(bad))

    def test_a_filing_gives_its_contract_rows_and_only_three_fields_of_its_identity(self):
        rows, raw, cid, cname, fq = eqr.read_filing(filing([row(), row(contract_unique_id="C2")]))
        self.assertEqual((len(rows), cid, cname, fq), (2, "C000001", "Made Up Wind, LLC", "202606"))
        self.assertIn(b"Made Up Utility Co", raw)
        self.assertNotIn(b"Somebody", raw)     # the contact person is in the ident file, which is not kept

    def test_a_changed_layout_stops_the_read(self):
        with self.assertRaises(RuntimeError):
            eqr.read_filing(filing([row()], header=["seller"] + eqr.FERC_COLS[1:]))

    def test_no_column_of_the_table_names_a_person(self):
        self.assertFalse([c for c in eqr.COLS if "contact" in c or "person" in c or "phone" in c or "email" in c])

    def test_one_row_per_contract_row_with_nothing_filled(self):
        rows = [row(rate="42.5", rate_units="$/MWH", quantity="100", units="MW"),
                row(contract_unique_id="C2", rate="", rate_description="Market Based Rate", quantity="", units=""),
                row(contract_unique_id="C3", rate="5.25", rate_units="$/KW-MO", quantity="50", units="MWH",
                    actual_termination_date="20260601"),
                row(contract_unique_id="C4", contract_execution_date="")]
        out, counts = eqr.events([("f_1_1.zip", "C000001", "Made Up Wind, LLC", rows)], "2026_Q2", "https://x/DownloadRepositoryProd/k/y.zip", "r")
        self.assertEqual(counts, dict(companies=1, superseded_filings=0, undated_rows=1, out_of_range_rows=0, out_of_range_dates=[]))
        self.assertEqual(len(out), 3)                                     # the undated row is left out, not dated by guess
        a, b, c = out
        self.assertEqual((a["event_date"], a["event_type"], a["parties"]), ("2026-04-15", "contract", "Made Up Wind, LLC;Made Up Utility Co"))
        self.assertEqual((a["mw"], a["price"], a["currency"], a["status"]), (100.0, 42.5, "USD", "in_force"))
        self.assertEqual((b["mw"], b["price"], b["currency"]), ("", "", ""))  # words for a price: no number
        self.assertEqual(b["x_rate_description"], "Market Based Rate")
        self.assertEqual((c["mw"], c["price"], c["status"]), ("", "", "terminated"))   # not MW, not USD per MWh
        self.assertEqual(c["x_rate"], "5.25")                              # as filed, in its own units
        self.assertEqual(set(out[0]), set(eqr.COLS))

    def test_a_date_no_table_can_hold_is_left_out_and_counted_and_a_late_one_stays_as_filed(self):
        rows = [row(contract_execution_date="29150101"), row(contract_unique_id="C2", contract_execution_date="21010101"),
                row(contract_unique_id="C3", contract_execution_date="16000101")]
        out, counts = eqr.events([("f_1_1.zip", "C000001", "A", rows)], "2026_Q2", "u", "r")
        self.assertEqual([e["event_date"] for e in out], ["2101-01-01"])     # as filed: not corrected, not dropped
        self.assertEqual((counts["out_of_range_rows"], counts["out_of_range_dates"]), (2, ["1600-01-01", "2915-01-01"]))

    def test_a_company_is_read_from_its_newest_filing_and_ids_do_not_repeat(self):
        old = [row(rate="1")]
        new = [row(rate="2"), row(rate="3")]                               # one agreement, two products: the same contract id twice
        out, counts = eqr.events([("f_100_1.zip", "C000001", "A", old), ("f_100_2.zip", "C000001", "A", new),
                                  ("f_200_1.zip", "C000002", "B", [row()])], "2026_Q2", "u", "r")
        self.assertEqual(counts["superseded_filings"], 1)
        self.assertEqual([e["x_rate"] for e in out if e["x_company_id"] == "C000001"], ["2", "3"])
        ids = [e["event_id"] for e in out]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith("ferc_eqr:2026Q2:") for i in ids))

    def test_the_ceiling_cannot_be_raised(self):
        self.assertEqual(eqr.CEILING, 400_000)
        with contextlib.redirect_stderr(io.StringIO()):                   # argparse states the refusal on stderr
            with self.assertRaises(SystemExit):
                eqr.main(["--quarter", "2026_Q2", "--ceiling", "400001"])
            with self.assertRaises(SystemExit):
                eqr.main(["--quarter", "2026Q2"])


class Table(unittest.TestCase):
    """The table, where the machine holds it."""

    def setUp(self):
        if not os.path.exists(TABLE):
            self.skipTest("ferc_eqr_contracts.csv is not on this machine")
        with open(TABLE, encoding="utf-8") as f:
            self.header = []
            for ln in f:
                if not ln.startswith("#"):
                    break
                self.header.append(ln)
        # the header lines are skipped by count: a company name can hold a "#" (pandas' comment option would cut the row)
        self.t = pd.read_csv(TABLE, skiprows=len(self.header), dtype=str, keep_default_na=False)

    def test_under_the_ceiling_internal_and_keyed(self):
        self.assertLessEqual(len(self.t), eqr.CEILING)
        self.assertTrue(any(re.search(r"license:\s*internal\b", h, re.I) for h in self.header))
        self.assertFalse(self.t["event_id"].duplicated().any())
        self.assertEqual(set(self.t["event_type"]), {"contract"})
        self.assertTrue(self.t["event_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all())

    def test_a_price_is_a_number_only_where_the_filer_gave_usd_per_mwh(self):
        priced = self.t[self.t["price"] != ""]
        self.assertTrue((priced["x_rate_units"].str.upper() == "$/MWH").all())
        self.assertTrue((priced["x_rate"] != "").all())
        self.assertEqual(set(self.t["status"]), {"in_force", "terminated"})
        self.assertEqual(set(self.t["x_quarter"]), {"2026_Q2"})

    def test_coverage_calls_it_internal(self):
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        hit = cov[cov["table"] == "ferc_eqr_contracts"]
        if hit.empty:
            self.skipTest("coverage.csv does not list the table on this machine")
        self.assertEqual(set(hit["license"]), {"internal"})


class LiveSet(unittest.TestCase):
    def test_the_live_set_holds_the_recent_rows_only_and_the_page_reads_them_with_the_token(self):
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertIn("^ferc_eqr_contracts$", live["full"])
        self.assertEqual(live["select"]["ferc_eqr_contracts"], {"event_days": 1000})
        with open(os.path.join(ROOT, "warehouse", "supabase", "migrations", "020_eqr_contracts.sql"), encoding="utf-8") as f:
            sql = f.read()
        for fn in ("internal_eqr_contracts", "internal_eqr_summary"):
            body = sql[sql.index(f"function public.{fn}("):]
            body = body[:body.index("end $$;")]
            self.assertIn("security definer", body)
            self.assertIn("internal_costs_token", body)
            self.assertIn("raise exception 'not authorized'", body)
            self.assertIn("table_name = 'ferc_eqr_contracts'", body)
        self.assertNotRegex(sql, r"(?i)grant\s+select")              # no table is opened: only the two functions answer
        self.assertNotRegex(sql, r"(?i)create\s+policy")

    def test_the_loader_keeps_events_of_the_last_n_days(self):
        import load
        with open(os.path.join(ROOT, "warehouse", "supabase", "load.py"), encoding="utf-8") as f:
            self.assertIn('sel.get("event_days")', f.read())
        self.assertTrue(callable(load.filtered))


class Page(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(SITE, *parts), encoding="utf-8") as f:
            return f.read()

    def test_in_review_not_indexed_and_the_three_limits_are_stated(self):
        self.assertRegex(self.read("lib", "release.ts"), r'"/contracts":\s*"review"')
        page = self.read("app", "contracts", "page.tsx")
        self.assertIn("robots: { index: false, follow: false }", page)
        limits = page[page.index("function Limits("):page.index("export default")]
        self.assertEqual(limits.count("<li>"), 3)
        for words in ("No column says what technology", "price as words, not a number", "filed again each quarter"):
            self.assertIn(words, limits)
        self.assertIn("<Limits rows=", page[page.index("export default"):])
        for col in ("Signed", "Seller", "Buyer", "Product", "Term", "Delivered"):
            self.assertIn(f'"{col}"', page)
        self.assertIn("INTERNAL_COSTS_TOKEN", self.read("app", "contracts", "read.ts"))
        self.assertNotIn("SERVICE", self.read("app", "contracts", "read.ts").upper().replace("SERVICE_AGREEMENT", ""))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("site/app/contracts/page.tsx", "site/app/contracts/read.ts", "site/lib/contracts.ts",
                    "warehouse/connectors/ferc_eqr_contracts.py", "warehouse/supabase/migrations/020_eqr_contracts.sql",
                    "docs/methods/ferc_eqr_contracts.md", "tests/test_session83.py"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)

    def test_the_pages_model(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        js = """
import * as c from './lib/contracts.ts';
const r = (o) => ({ event_id: 'e', event_date: '2026-04-15', status: null, mw: null, price: null, seller: 'S', buyer: 'B', affiliate: 'N',
  agreement: 'A1', product_type: null, product: 'ENERGY', class: null, term: null, commencement: '20260101', termination: '20360101',
  quantity: '', units: '', rate: '', rate_units: '', rate_description: '', pod_ba: 'PJM', pod_location: null, quarter: '2026_Q2', ...o });
const rows = [r({}), r({ product: 'Capacity', rate: '5', rate_units: '$/KW-MO', agreement: 'A2', pod_ba: '' }),
  r({ product: 'TOLLING ENERGY', seller: 'S2', affiliate: 'Y', rate_description: 'Market Based Rate' }), r({ product: 'SPINNING RESERVE' })];
const s = { rows: 4, priced: 1, first: '2025-12-30', last: '2026-04-15', quarters: ['2026_Q2'],
  by_month: [{ month: '2025-12', rows: 1, priced: 0 }, { month: '2026-01', rows: 2, priced: 1 }, { month: '2026-04', rows: 1, priced: 0 }], by_product: [], by_ba: [] };
console.log(JSON.stringify({
  q: [c.quarterOf('2026-01'), c.quarterOf('2026-12'), c.quarterDates('2026-Q4'), c.quarterDates('2026-Q1')],
  held: c.quarters(s),
  pick: [c.choices({}, ['2026-Q2', '2026-Q1']).quarter, c.choices({ q: '1999-Q1' }, ['2026-Q2']).quarter, c.choices({}, []).quarter,
         c.choices({ product: 'nonsense' }, []).product.slug, c.choices({ ba: "PJM'; drop" }, []).ba, c.choices({ ba: 'PJM' }, []).ba],
  n: Object.fromEntries(c.PRODUCTS.map((p) => [p.slug, c.filter(rows, p, null).length])),
  ba: c.filter(rows, c.PRODUCTS[4], 'PJM').length,
  date: [c.fercDate('20250723'), c.fercDate('upon notice'), c.fercDate(null)],
  term: [c.termYears(rows[0]), c.termYears(r({ termination: '' })), c.termYears(r({ commencement: '20360101', termination: '20260101' }))],
  rate: [c.rateText(rows[1]), c.rateText(rows[2]), c.rateText(rows[0])],
  counts: c.counts(rows), byBa: c.byBa(rows),
  filed: [c.filedQuarter(s), c.filedQuarter({ ...s, quarters: [] })],
  listed: c.listed([{ quarter: '2915-Q1', rows: 1, priced: 0 }, { quarter: '2026-Q3', rows: 4, priced: 1 }, ...c.quarters(s)], '2026-Q2'),
}));
"""
        r = subprocess.run([node, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        d = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(d["q"], ["2026-Q1", "2026-Q4", {"from": "2026-10-01", "to": "2027-01-01"}, {"from": "2026-01-01", "to": "2026-04-01"}])
        self.assertEqual(d["held"], [{"quarter": "2026-Q2", "rows": 1, "priced": 0}, {"quarter": "2026-Q1", "rows": 2, "priced": 1},
                                     {"quarter": "2025-Q4", "rows": 1, "priced": 0}])
        self.assertEqual(d["pick"], ["2026-Q2", "2026-Q2", None, "power", None, "PJM"])
        self.assertEqual(d["n"], {"power": 3, "energy": 1, "capacity": 1, "tolling": 1, "all": 4})
        self.assertEqual(d["ba"], 3)
        self.assertEqual(d["date"], ["2025-07-23", "upon notice", ""])
        self.assertAlmostEqual(d["term"][0], 10.0, places=2)
        self.assertEqual(d["term"][1:], [None, None])                      # no end filed, or an end before the start: no term
        self.assertEqual(d["rate"], [{"text": "5 $/KW-MO", "numeric": True}, {"text": "Market Based Rate", "numeric": False},
                                     {"text": "not stated", "numeric": False}])
        self.assertEqual(d["counts"], {"rows": 4, "agreements": 3, "sellers": 2, "buyers": 1, "priced": 1, "affiliate": 1})
        self.assertEqual(d["byBa"], [{"ba": "PJM", "rows": 3}, {"ba": "not stated", "rows": 1}])
        self.assertEqual(d["filed"], ["2026-Q2", None])
        self.assertEqual([h["quarter"] for h in d["listed"]["upTo"]], ["2026-Q2", "2026-Q1", "2025-Q4"])   # nothing after the quarter filed for
        self.assertEqual((d["listed"]["laterRows"], d["listed"]["laterLast"]), (5, "2915-Q1"))               # counted, not listed


if __name__ == "__main__":
    unittest.main()
