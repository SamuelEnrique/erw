"""Session 10414 (chain 720, part E): the table of every company on /equities shows the newest period each filed.

Window A's desk met this window's data requests 578 and 579 (landing 19, 27 November 2026, 11:53 UTC): each company of
`site/data/equities/index.json` carries `newest_filed` (the period's end, its form, the day filed and the filing's
address; revenue, net income and capital spending each with the months its period covers; debt and shares at the
period's end), and `fundamentals_why` may hold a note while the figures are shown (a new registrant, a filer that
stopped). The page reads both:

- the table's "Filed figures" column, which said only "shown", is the newest period filed (its end and form, opening
  the filing) and the revenue of that period in USD million with its months, each revenue keyed into the list;
- the table sorts by the newest period, newest first on the first press;
- a note is marked on the company's row and written under its figures when the company is drawn;
- the list's download carries the newest period's twelve columns after the thirteen it had.

A list none of whose companies carries the field is drawn as before.

    python -m pytest tests/test_session10414_equities_newest.py
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_sees(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-equities-filed.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of /equities on the filed figures")


class TheListsField(unittest.TestCase):
    def test_the_type_is_the_contracts(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn("export type FiledSum = { months: number | null; v: number };", lib)
        self.assertIn("export type NewestFiled = { period_end: string; form: string | null; filed: string | null; url: string | null; revenue: FiledSum | null; net_income: FiledSum | null; capex: FiledSum | null; debt: number | null; shares_outstanding: number | null };", lib)
        self.assertIn("  newest_filed?: NewestFiled | null;", lib)

    def test_the_sort_is_by_the_periods_end_then_the_day_filed(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn('export const SORTS = ["name", "ticker", "segment", "exchange", "first", "last", "filed"] as const;', lib)
        self.assertIn('f.sort === "filed" ? `${c.newest_filed?.period_end ?? ""} ${c.newest_filed?.filed ?? ""}`', lib)
        # a company with no newest period is last in either direction
        self.assertIn('const last = f.sort === "filed" ? rows.filter((c) => !c.newest_filed) : [];', lib)
        self.assertIn("rows = [...rows, ...last];", lib)

    def test_a_list_without_the_field_is_the_table_as_it_was(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("const withNewest = list.companies.some((c) => c.newest_filed !== undefined);", view)
        self.assertIn('if (!withNewest) return ["shown"];', view)
        self.assertIn('] : ["Filed figures"]),', view)


class TheCells(unittest.TestCase):
    def test_the_revenue_is_keyed_into_the_list_by_the_companys_place_in_the_file(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('<Num check={pfKey(LIST, ["companies", i, "newest_filed", "revenue", "v"])} raw={r.v}>{millions(r.v)}</Num>', view)
        self.assertIn("const n = c.newest_filed, i = list.companies.indexOf(c);", view)

    def test_only_an_address_of_the_sec_is_a_link(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('{secUrl(n.url) ? <a href={secUrl(n.url)!} className="inline-block py-1 -my-1" rel="noopener"', view)

    def test_the_months_are_said_beside_the_figure(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('{r.months !== null ? <span className="text-muted"> ({r.months} months)</span> : null}', view)
        self.assertIn("Two companies' figures compare only where the months are the same.", view)

    def test_a_note_is_said_in_the_files_words(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("data-eq-filed-note-mark={c.id}", view)
        self.assertIn("<p key={x.slot.mark} className=\"mb-3 max-w-3xl text-sm\" data-eq-filed-note={x.slot.pick.id}>A note on what {x.slot.company!.ticker} filed: {x.slot.company!.fundamentals_why}.</p>", view)


class TheValueCheck(unittest.TestCase):
    def test_it_reads_the_lists_revenue_in_millions(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const equitiesNewest = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        self.assertRegex("pf|equities/index.json|companies/12/newest_filed/revenue/v", rule)
        self.assertNotRegex("pf|equities/index.json|companies/12/newest_filed/revenue/months", rule)
        self.assertNotRegex("pf|equities/index.json|companies/12/market_value/v", rule)
        self.assertNotRegex("pf|equities/series/DUK.json|quarterly/1/7", rule)


class TheDownload(unittest.TestCase):
    def test_the_list_keeps_its_columns_and_gains_the_newest_periods(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn('export const LIST_HEAD = ["ticker", "name", "cik", "exchange", "sic", "sic_label", "segments", "price_status", "price_why", "fundamentals_status", "fundamentals_why", "first_day", "last_day",', lib)
        self.assertIn('"newest_period_end", "newest_form", "newest_filed_day", "newest_filing", ...LIST_FILED_FIGURES];', lib)
        reader = src("site", "app", "equities", "reader.ts")
        self.assertIn("text: LIST_HEAD.filter((c) => !LIST_FILED_FIGURES.includes(c)), figures: LIST_FILED_FIGURES,", reader)


class TheRealFile(unittest.TestCase):
    """The list on main carries the field since landing 19; where it does, it is of the contract's shape."""

    def test_the_lists_entries_are_of_the_shape_the_page_reads(self):
        import json
        path = os.path.join(SITE, "data", "equities", "index.json")
        if not os.path.isfile(path):
            self.skipTest("the equities list is not on this machine")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        with_field = [c for c in doc.get("companies", []) if "newest_filed" in c]
        if not with_field:
            self.skipTest("the list on this machine is an older one")
        for c in with_field:
            n = c["newest_filed"]
            if n is None:
                continue
            self.assertRegex(n["period_end"], r"^\d{4}-\d{2}-\d{2}$", c["id"])
            for k in ("revenue", "net_income", "capex"):
                self.assertTrue(n[k] is None or (isinstance(n[k].get("v"), (int, float)) and (n[k].get("months") is None or isinstance(n[k]["months"], int))), (c["id"], k))
            for k in ("debt", "shares_outstanding"):
                self.assertTrue(n[k] is None or isinstance(n[k], (int, float)), (c["id"], k))


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        self.assertNotIn(EM, src("site", "app", "equities", "view.tsx"))
        self.assertNotIn(EM, src("site", "app", "equities", "reader.ts"))
        self.assertNotIn(EM, src("tests", "test_session10414_equities_newest.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
