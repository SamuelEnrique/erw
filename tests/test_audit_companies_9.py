"""Audit of the company database, finding 5, the choice for the owner's ruling (session 10228,
docs/reviews/companies-model-audit-2026-11-26.md). A test only, not for landing: it changes nothing and shows what the
other choice would do.

The Kind choices of /companies are the index's kinds in the order of KIND_ORDER (site/lib/companydb.ts), and a kind
not in that list is not offered (app/companies/page.tsx, opt: order.filter((k) => k in rec)). KIND_ORDER leaves out
"power marketer", so the 439 power marketers in the page files of 16 November 2026 cannot be chosen (an address that
names the kind, ?kind=power%20marketer, still filters them: queryOf reads the index's kinds). The other choice adds
"power marketer" to KIND_ORDER after "operator": the choice "power marketer (439)" would be drawn, a new count on the
page. Default: left as it is."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class PowerMarketersCannotBeChosen(unittest.TestCase):
    def test_the_choices_leave_them_out(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        order = re.findall(r'"([^"]+)"', re.search(r"KIND_ORDER = \[(.*?)\]", src("site", "lib", "companydb.ts")).group(1))
        offered = [k for k in order if k in ix["kinds"]]          # opt(ix.kinds, KIND_ORDER)
        unoffered = {k: n for k, n in ix["kinds"].items() if k not in offered}
        self.assertEqual(unoffered, {"power marketer": 439})
        self.assertEqual(sum(ix["kinds"][k] for k in offered) + 439, ix["n_listed"])
        self.assertIn("order.filter((k) => k in rec)", src("site", "app", "companies", "page.tsx"))
        self.assertIn('kind: pick(one("kind"), ix.kinds)', src("site", "lib", "companydb.ts"))


if __name__ == "__main__":
    unittest.main()
