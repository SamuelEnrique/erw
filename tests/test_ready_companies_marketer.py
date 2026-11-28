"""Session 11407 (chain 770, part C): the owner's other choice on the companies audit's finding 5 (session 10228,
docs/reviews/companies-model-audit-2026-11-26.md; the audit's test was tests/test_audit_companies_9.py on
wip/audit-companies-9), readied, not landed until Samuel rules.

The Kind choices of /companies are the index's kinds in the order of KIND_ORDER (site/lib/companydb.ts), and a kind
not in that list is not offered (app/companies/page.tsx, opt: order.filter((k) => k in rec)). On origin/main
KIND_ORDER left out "power marketer", so the 439 power marketers in the page files of 16 November 2026 could not be
chosen. On this branch KIND_ORDER carries it after "operator", in the builder's own order
(warehouse/derived/companies.py), so the choice "power marketer (439)" is drawn and every kind the index counts is
offered; the hover's sentence on kinds not offered then prints nothing."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def site_order():
    return re.findall(r'"([^"]+)"', re.search(r"KIND_ORDER = \[(.*?)\]", src("site", "lib", "companydb.ts")).group(1))


class PowerMarketersCanBeChosen(unittest.TestCase):
    def test_every_kind_is_offered(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        order = site_order()
        offered = [k for k in order if k in ix["kinds"]]          # opt(ix.kinds, KIND_ORDER)
        unoffered = {k: n for k, n in ix["kinds"].items() if k not in offered}
        self.assertEqual(unoffered, {})
        self.assertEqual(ix["kinds"]["power marketer"], 439)
        self.assertIn("power marketer", offered)
        self.assertEqual(sum(ix["kinds"][k] for k in offered), ix["n_listed"])
        labels = [f"{k} ({ix['kinds'][k]:,})" for k in offered]   # the label opt draws: `${k} (${count(rec[k])})`
        self.assertIn("power marketer (439)", labels)
        self.assertIn("order.filter((k) => k in rec)", src("site", "app", "companies", "page.tsx"))
        self.assertIn('kind: pick(one("kind"), ix.kinds)', src("site", "lib", "companydb.ts"))

    def test_the_site_order_is_the_builders(self):
        b = src("warehouse", "derived", "companies.py")
        builder = re.findall(r'"([^"]+)"|(LAB_KIND)', re.search(r"^KIND_ORDER = \[(.*?)\]", b, re.S | re.M).group(1))
        builder = ["lab or hyperscaler" if lab else k for k, lab in builder]
        self.assertEqual(site_order(), builder)

    def test_the_note_says_so(self):
        note = " ".join(src("docs", "methods", "companies.md").split())
        self.assertIn("power marketer included after operator", note)
        self.assertNotIn("which leaves out power marketer", note)


if __name__ == "__main__":
    unittest.main()
