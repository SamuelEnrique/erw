"""Session 2238 (chain 156): the deals table (site/lib/dealsview.ts, site/app/deals/DealsTable.tsx).

Node runs the pure module on rows shaped as the live set serves them: one extracted before session 2232 (the old
columns only) and ones with the new fields. The filters, the sort (a missing value last either way), the CSV (no
outlet text, its header lines) and the readers are checked; the component's source is read for the owner's layout
(inputs left, results right) and the hover tips.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


ROWS = [
    # extracted before session 2232: no kind, no grid
    {"event_id": "deal:old", "event_date": "2026-09-30T21:24:49Z", "status": "signed", "mw": "190", "price": "",
     "source": "Reuters", "source_url": "https://example.org/a",
     "extra": {"deal_type": "ppa", "buyer": "Amazon", "seller": "Constellation", "state": "MD", "ai_power": "true",
               "story_urls": "https://example.org/a;https://example.org/b"}},
    {"event_id": "deal:new", "event_date": "2026-10-19T18:00:00Z", "status": "signed", "mw": "960", "price": "",
     "source": "Utility Dive", "source_url": "https://example.org/c",
     "extra": {"deal_type": "ppa", "buyer": "Amazon", "seller": "AEP", "state": "IN", "ai_power": "true", "kind": "smr",
               "kind_basis": "the deal's words: smr", "stage": "signed", "seller_name": "American Electric Power",
               "buyer_name": "Amazon", "flags": "headline: 960 MW; record: none", "status_history": "2026-10-19 rumored (first record); 2026-10-19 signed (news:x)",
               "ai_power_basis": "party Amazon", "fields_version": "2232", "story_urls": "https://example.org/c"}},
    {"event_id": "deal:gas", "event_date": "2025-12-01T00:00:00Z", "status": "", "mw": "", "price": "",
     "source": "Hart Energy", "source_url": "https://example.org/d",
     "extra": {"deal_type": "other", "seller": "BKV", "asset": "1.2 GW, gas", "state": "TX", "kind": "gas_buildout",
               "usd": "800000000", "dollars": "800000000", "grid": "ERCOT", "fields_version": "2232",
               "story_urls": "https://example.org/d"}},
    {"event_id": "deal:price", "event_date": "2026-03-01T00:00:00Z", "status": "signed", "mw": "100", "price": "68",
     "source": "pv magazine USA", "source_url": "https://example.org/e",
     "extra": {"deal_type": "ppa", "buyer": "Google, \"X\"", "seller": "NextEra", "state": "CA", "kind": "ppa",
               "usd_per_mwh": "68", "fields_version": "2232", "story_urls": "https://example.org/e"}},
]


class View(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        js = (
            "const m = await import('./lib/dealsview.ts');"
            f"const raw = {json.dumps(ROWS)};"
            "const rows = raw.map(m.rowOf);"
            "const f = (o) => m.filterRows(rows, {...m.NO_INPUTS, ...o}).map((d) => d.id);"
            "const csv = m.toCsv(rows, {url: 'https://erw/deals', when: '2026-11-06 10:00 UTC', filters: 'kind=smr'});"
            "console.log(JSON.stringify({rows, csv,"
            " kind: f({kind: 'smr'}), grid: f({grid: 'PJM'}), gridNone: f({grid: 'none'}), party: f({party: 'electric power'}),"
            " mwMin: f({mwMin: '500'}), mwMax: f({mwMax: '200'}), year: f({year: '2025'}), ai: f({ai: 'no'}),"
            " stage: f({stage: 'signed'}), stageNone: f({stage: 'none'}), price: f({price: 'yes'}),"
            " mwDesc: m.sortRows(rows, 'mw', 'desc').map((d) => d.id), mwAsc: m.sortRows(rows, 'mw', 'asc').map((d) => d.id),"
            " py: m.pythonReader('erw_energy_deals.csv'), stata: m.stataReader('erw_energy_deals.csv')}));")
        cls.r = node(js)

    def test_an_old_row_reads_its_kind_and_grid_from_its_own_columns(self):
        old = self.r["rows"][0]
        self.assertEqual(old["kind"], "ppa")
        self.assertIn("extracted before session 2232", old["kindBasis"])
        self.assertEqual(old["grid"], "PJM")
        self.assertEqual(old["gridBasis"], "the main grid of MD")
        self.assertEqual(self.r["rows"][2]["gridBasis"], "named in a story")

    def test_every_filter(self):
        r = self.r
        self.assertEqual(r["kind"], ["deal:new"])
        self.assertEqual(r["grid"], ["deal:old"])
        self.assertEqual(r["party"], ["deal:new"])            # the canonical name, American Electric Power
        self.assertEqual(r["mwMin"], ["deal:new"])
        self.assertEqual(sorted(r["mwMax"]), ["deal:old", "deal:price"])   # a deal that states no MW is left out
        self.assertEqual(r["year"], ["deal:gas"])
        self.assertEqual(r["ai"], ["deal:gas", "deal:price"])
        self.assertEqual(sorted(r["stage"]), ["deal:new", "deal:old", "deal:price"])
        self.assertEqual(r["stageNone"], ["deal:gas"])
        self.assertEqual(r["price"], ["deal:price"])

    def test_a_missing_value_sorts_last_either_way(self):
        self.assertEqual(self.r["mwDesc"], ["deal:new", "deal:old", "deal:price", "deal:gas"])
        self.assertEqual(self.r["mwAsc"], ["deal:price", "deal:old", "deal:new", "deal:gas"])

    def test_the_csv_has_its_header_and_no_outlet_text(self):
        lines = self.r["csv"].splitlines()
        self.assertEqual(sum(1 for x in lines if x.startswith("#")), 4)
        self.assertIn("filters: kind=smr", lines[1])
        self.assertTrue(lines[4].startswith("event_id,date,kind,deal_type,buyer,seller"))
        self.assertEqual(len(lines), 4 + 1 + 4)
        self.assertIn('"Google, ""X"""', self.r["csv"])         # a comma and a quote escaped
        self.assertNotIn("title", lines[4])
        self.assertNotIn("evidence", lines[4])

    def test_the_readers_read_that_file(self):
        self.assertIn('pd.read_csv("erw_energy_deals.csv", comment="#"', self.r["py"])
        self.assertIn("varnames(5) rowrange(6)", self.r["stata"])   # four comment lines, then the header


class TheComponent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SITE, "app", "deals", "DealsTable.tsx"), encoding="utf-8") as f:
            cls.src = f.read()

    def test_inputs_left_results_right(self):
        self.assertIn("lg:grid-cols-[15rem_minmax(0,1fr)]", self.src)
        self.assertLess(self.src.index("<aside"), self.src.index("<table"))

    def test_every_column_sorts_and_has_a_tip(self):
        for key in ("date", "kind", "parties", "asset", "where", "grid", "mw", "usd", "price", "stage", "ai", "sources"):
            self.assertIn(f'["{key}", ', self.src)
        self.assertIn("aria-sort", self.src)
        self.assertIn("data-sort={key}", self.src)

    def test_downloads_and_the_checked_keys(self):
        for d in ("csv", "py", "do"):
            self.assertIn(f'data-download="{d}"', self.src)
        self.assertIn("event|energy_deals|${d.id}|mw", self.src)
        self.assertIn("event|energy_deals|${d.id}|dollars", self.src)

    def test_no_dash_in_the_new_files(self):
        for p in (os.path.join(SITE, "lib", "dealsview.ts"), os.path.join(SITE, "app", "deals", "DealsTable.tsx")):
            with open(p, encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn("—", t)
            self.assertNotIn("–", t)


if __name__ == "__main__":
    unittest.main()
