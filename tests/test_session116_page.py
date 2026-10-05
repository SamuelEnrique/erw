"""Session 116, the page: what Texas's storage resources offered day-ahead, one section of /cost-of-power/battery/awards.

Energy Research Warehouse (ERW). No request leaves the machine. The section reads ercot_storage_dam_offers_monthly
beside ercot_storage_dam_awards_monthly and the model's rows of battery_stack_monthly, and splits the gap between the
model's figure and the awards in three: capacity never offered day-ahead, offered and not awarded, and price. These
tests hold:

- the page is still in review, the method page too, and no live page knows of the section or its table;
- the section comes after "what this is not" and after the sections of session 115, which are as they were;
- the words: the allocation is called an allocation, the two cautions stand by the ancillary table (the services
  overlap; a value at the clearing price is not a forecast), "what the offers still cannot show" is there, and the
  awards are still never called what a battery made;
- no figure is written into the page: the three parts are computed by site/lib/storageawards.ts (gapOf, run in Node)
  from the tables, they add up to the gap, a partial month is never in them, and a table that is not read gives none;
- on the tables of this machine, when they are here, gapOf gives what the same arithmetic gives in Python.

The rows of the arithmetic tests are made for the tests (round numbers, never shown anywhere): they test the sums, not
the data. The tables' own tests are elsewhere.

    python -m unittest tests.test_session116_page -v
"""

import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = ("site", "app", "cost-of-power", "battery", "awards", "page.tsx")
SECTION = ("site", "app", "cost-of-power", "battery", "awards", "Offers.tsx")
LIB = ("site", "lib", "storageawards.ts")
METHOD = ("docs", "methods", "ercot_storage_dam_offers.md")
LIVE = ["site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/BatteryForm.tsx", "site/app/cost-of-power/battery/Contract.tsx"]
SERVICES = ["regup", "regdn", "rrs", "ecrs", "nspin"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def visible(text):
    """What a reader can see: the comments of a file are not the page."""
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


class Release(unittest.TestCase):
    def test_the_page_and_the_method_are_in_review(self):
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/cost-of-power/battery/awards": "review"')
        self.assertRegex(release, r'"/cost-of-power/battery": "live"')
        self.assertNotIn("ercot_storage_dam_offers", release)  # the method page is in review as every method page is, by "/data/methods"
        got = node("const r = await import('./lib/release.ts'); console.log(JSON.stringify({a: r.statusOf('/cost-of-power/battery/awards'), "
                   "b: r.statusOf('/cost-of-power/battery'), m: r.statusOf('/data/methods/ercot_storage_dam_offers')}));")
        self.assertEqual(got, {"a": "review", "b": "live", "m": "review"})

    def test_the_route_check_asks_for_the_method(self):
        self.assertIn('"/data/methods/ercot_storage_dam_offers"', src("site", "scripts", "check-routes.mjs"))
        self.assertTrue(os.path.exists(os.path.join(ROOT, *METHOD)))

    def test_no_live_page_knows_of_it(self):
        for f in LIVE + ["site/app/cost-of-power/Tabs.tsx", "site/lib/pages.ts", "site/app/about/page.tsx"]:
            text = src(*f.split("/"))
            for word in ("battery/awards", "storageawards", "ercot_storage_dam_offers", "OffersSection"):
                self.assertNotIn(word, text, f)

    def test_the_live_battery_page_is_as_main_has_it(self):
        """While the section is not on main: the three files of the live battery page are main's, byte for byte."""
        def git(*a):
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        if git("rev-parse", "--verify", "--quiet", "origin/main").returncode != 0:
            self.skipTest("origin/main is not in this checkout")
        if git("cat-file", "-e", "origin/main:" + "/".join(SECTION)).returncode == 0:
            self.skipTest("the section is on main: the session's deploy is done, and later sessions may change the battery page")
        r = git("diff", "--quiet", "origin/main", "--", *LIVE)
        self.assertEqual(r.returncode, 0, "the live battery page differs from origin/main")


class Words(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page, cls.section, cls.lib = src(*PAGE), src(*SECTION), src(*LIB)
        cls.text, cls.sec = visible(cls.page), visible(cls.section)

    def test_the_section_comes_after_what_this_is_not_and_after_session_115s_sections(self):
        at = self.text.index("<OffersSection")
        for earlier in ("What this is not", "data-awards-summary", 'title="By month"', 'title="By year"', 'title="Why the two differ"'):
            self.assertLess(self.text.index(earlier), at, earlier)
        self.assertEqual(self.text.count("<OffersSection"), 1)
        self.assertIn("Where the gap comes from: what was offered day-ahead", self.sec)
        self.assertIn('href="#offers"', self.text)   # "Why the two differ" points down to it
        self.assertIn('id="offers"', self.sec)

    def test_the_three_parts_and_the_identity_are_said(self):
        for said in ("Capacity never offered day-ahead", "Offered day-ahead and not awarded", "Price", "The three add up to the gap exactly",
                     "an allocation, not a measurement", "Energy only", "there is no price part"):
            self.assertIn(said, self.sec, said)
        for part in ("never", "unawarded", "price", "gap"):
            self.assertIn(f'data-offers-part="{part}"', self.sec)

    def test_the_two_cautions_stand_by_the_ancillary_table(self):
        table = self.sec.index("Ancillary services: what was offered and what was awarded")
        overlap, forecast = self.sec.index('data-offers-caution="overlap"'), self.sec.index('data-offers-caution="forecast"')
        cannot = self.sec.index("What the offers still cannot show")
        self.assertLess(table, overlap)
        self.assertLess(overlap, forecast)
        self.assertLess(forecast, cannot)
        self.assertIn("overlap and must not be added to a total", self.sec)
        self.assertIn("priced for several services and awarded to one", self.sec)
        self.assertIn("not a forecast", self.sec)
        self.assertIn("more awards would have lowered the price", self.sec)

    def test_what_the_offers_still_cannot_show(self):
        tail = self.sec[self.sec.index("What the offers still cannot show"):]
        for said in ("Why a resource offered nothing", "in real time", "no state of charge and no duration", "had more cleared", "Which service an unawarded block"):
            self.assertIn(said, tail, said)
        self.assertIn("by entity and not by resource", tail)

    def test_it_is_never_called_what_a_battery_made(self):
        for body in (self.page, self.section, self.lib, src(*METHOD)):
            low = body.lower()
            self.assertEqual(len(re.findall(r"earned", low)), len(re.findall(r"not what any battery earned", low)))
            for word in ("measured revenue", "earnings", "revenue earned", "what batteries earn", "what the fleet earn", "earns"):
                self.assertNotIn(word, low)
            self.assertNotIn(chr(0x2014), body)  # no em dash
        self.assertNotRegex(self.sec, r"\bno data\b")  # the route check counts those words

    def test_the_model_is_labeled_as_the_models(self):
        self.assertGreaterEqual(self.sec.count("The model&apos;s"), 3)
        self.assertIn("2-hour battery, day-ahead schedule", self.sec)
        self.assertIn("The model&apos;s figures are the model&apos;s, not ERCOT&apos;s", self.sec)

    def test_no_figure_is_written_into_the_page(self):
        """Every number of the section comes from the tables when the page is rendered: none of today's figures is in
        the code, and the arithmetic reads the tables' variables by name."""
        for body in (self.page, self.section, self.lib):
            for figure in ("9.70", "14.52", "23.61", "30.14", "6.53", "0.62", "32.2", "67.8", "10.7", "1.81", "0.41", "0.39", "45.16", "37.67"):
                self.assertNotRegex(body, r"(?<![\d.])" + re.escape(figure) + r"(?![\d])", figure)
        for name in ("Regulation Up", "Regulation Down", "Responsive Reserve", "Non-Spin"):  # which service is which is computed, not written
            self.assertNotIn(name, self.section, name)
        for variable in ("limit_mwh_no_offer", "limit_mwh_no_offer_out", "limit_mwh", "energy_sold_mwh", "energy_offer_mwh_at_clearing", "discharged_mwh_per_mw",
                         "unawarded_usd_per_mw", "offer_mwh_le_mcpc", "revenue_total_usd_per_mw", "revenue_energy_usd_per_mw"):
            self.assertIn(variable, self.lib, variable)
        self.assertIn('export const OFFERS_TABLE = "ercot_storage_dam_offers_monthly"', self.lib)
        self.assertIn("gapOf(", self.page)
        self.assertNotRegex(self.page + self.section, r"anthropic|\bfetch\(")  # no model call, no request of its own

    def test_a_table_that_is_not_read_shows_a_sentence_and_no_number(self):
        self.assertIn("The offers table could not be read, so no number is shown in this section", self.sec)
        self.assertIn("The offers table could not be read:", self.sec)
        self.assertIn("attempt(offerRows)", self.page)
        # the sections of session 115 do not wait on the offers: the read's failure reaches only the new section
        self.assertIn("unread={offersUnread}", self.page)

    def test_the_method(self):
        m = " ".join(src(*METHOD).split())
        for said in ("60d_DAM_ESR_Data", "60d_DAM_ESR_ASOffers", "straight lines between its points", "98.5 percent", "879,837", "within 0.1 MW",
                     "never exceeds the sum", "not capped", "as_offer_mwh_unlisted", "an allocation, not a measurement", "must not be added to a total",
                     "not a forecast", "ercot_dam_esr.py --daily", "warehouse/scheduled.py ercot_storage_dam", "warehouse/health.py",
                     "What the offers still cannot show", "used, reproduced, and redistributed in compilations, charts, and analyses",
                     "ercot_storage_dam_offers_daily", "ercot_storage_dam_offers_monthly", "checked against the awards table"):
            self.assertIn(said, m, said)


# rows made for the arithmetic: two whole months, a partial one before and one after
FIXTURE = r"""
const m = await import('./lib/storageawards.ts');
const P = m.PRODUCTS.map((p) => p.key);
const rows = (month, v, prefix = '') => Object.entries(v).map(([k, x]) => ({ variable: prefix + k, ts_utc: `${month}-01T00:00:00Z`, value: x }));
const award = (month, held, dim, total, energy, each) => rows(month, { days_held: held, days_in_month: dim, revenue_total_usd_per_mw: total,
  revenue_energy_usd_per_mw: energy, ...Object.fromEntries(P.map((p) => [`revenue_${p}_usd_per_mw`, each])) });
const model = (month, held, dim, total, energy, each, discharged) => rows(month, { days_held: held, days_in_month: dim, revenue_total_usd_per_mw: total,
  revenue_energy_usd_per_mw: energy, discharged_mwh_per_mw: discharged, ...Object.fromEntries(P.map((p) => [`revenue_${p}_usd_per_mw`, each])) }, m.MODEL_PREFIX);
const offer = (month, held, dim, o) => rows(month, { ...Object.fromEntries(m.OFFER_VARIABLES.map((k) => [k, 1000])), days_held: held, days_in_month: dim, ...o });
const A = [...award('2025-12', 26, 31, 400, 300, 20), ...award('2026-01', 31, 31, 2000, 1200, 160), ...award('2026-02', 28, 28, 1000, 600, 80), ...award('2026-03', 5, 31, 50, 40, 2)];
const M = [...model('2025-12', 31, 31, 4000, 2000, 400, 60), ...model('2026-01', 31, 31, 9000, 4000, 1000, 62), ...model('2026-02', 28, 28, 6000, 3000, 600, 56),
  ...model('2026-03', 31, 31, 2800, 1800, 200, 60)];
const O = [...offer('2025-12', 26, 31, { mw: 100 }),
  ...offer('2026-01', 31, 31, { mw: 100, limit_mwh: 74400, limit_mwh_no_offer: 18600, limit_mwh_no_offer_out: 3720, energy_sold_mwh: 1550, energy_offer_mwh: 20000,
    energy_offer_mwh_le_100: 2000, energy_offer_mwh_le_1000: 4000, regup_unawarded_usd_per_mw: 900, regup_offer_mwh: 10000, regup_award_mwh: 1000 }),
  ...offer('2026-02', 28, 28, { mw: 100, limit_mwh: 67200, limit_mwh_no_offer: 26880, limit_mwh_no_offer_out: 6720, energy_sold_mwh: 1400, energy_offer_mwh: 20000,
    energy_offer_mwh_le_100: 2000, energy_offer_mwh_le_1000: 4000, regup_unawarded_usd_per_mw: 700, regup_offer_mwh: 10000, regup_award_mwh: 1000 }),
  ...offer('2026-03', 5, 31, { mw: 100 })];
const strings = (rs) => rs.map((r) => ({ ...r, value: String(r.value) }));
const without = (rs, month, variable) => rs.filter((r) => !(r.ts_utc.startsWith(month) && (variable === undefined || r.variable === variable)));
console.log(JSON.stringify({
  g: m.gapOf(A, O, M), fromStrings: m.gapOf(strings(A), strings(O), strings(M)),
  noOffers: m.gapOf(A, [], M), noModel: m.gapOf(A, O, []), noAwards: m.gapOf([], O, M),
  febShort: m.gapOf(A, O.map((r) => (r.ts_utc.startsWith('2026-02') && r.variable === 'days_held' ? { ...r, value: 27 } : r)), M),
  febModelShort: m.gapOf(A, O, M.map((r) => (r.ts_utc.startsWith('2026-02') && r.variable.endsWith('days_held') ? { ...r, value: 20 } : r))),
  febLacks: m.gapOf(A, without(O, '2026-02', 'limit_mwh_no_offer'), M),
  onlyPartial: m.gapOf(A, O, M.filter((r) => r.ts_utc.startsWith('2026-03'))),
  usd: [m.usd(-0.6222), m.usd(9.7), m.usd(0)], pct: [m.pct(0.322, 1), m.pct(0.88)], list: [m.list(['a']), m.list(['a', 'b']), m.list(['a', 'b', 'c'])],
}));
"""


class Arithmetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node(FIXTURE)
        cls.g = cls.got["g"]

    def test_only_whole_months_are_in_it(self):
        g = self.g
        self.assertEqual(g["months"], ["2026-01", "2026-02"])   # December's 26 days and March's 5 are in no sum
        self.assertEqual(g["days"], 59)
        self.assertEqual(g["leftOut"], [])
        self.assertAlmostEqual(g["modelKw"], 15.0)
        self.assertAlmostEqual(g["awardsKw"], 3.0)
        self.assertAlmostEqual(g["gapKw"], 12.0)
        self.assertEqual(self.got["fromStrings"], g)  # the live set may serve a value as a string

    def test_never_offered_is_the_models_total_at_the_share_with_no_offer(self):
        g = self.g
        self.assertAlmostEqual(g["noOfferShare"], 45480 / 141600)
        self.assertAlmostEqual(g["noOfferOutShare"], 10440 / 141600)
        self.assertAlmostEqual(g["neverOfferedKw"], 15.0 * 45480 / 141600)

    def test_price_is_energy_only(self):
        e = self.g["energy"]
        self.assertAlmostEqual(e["modelPerMwDay"], 2.0)            # 118 MWh per MW over 59 days
        self.assertAlmostEqual(e["soldPerMwDay"], 0.5)             # 15.5 and 14 MWh per MW over 59 days
        self.assertAlmostEqual(e["modelUsdPerMwh"], 7000 / 118)
        self.assertAlmostEqual(e["awardsUsdPerMwh"], 1800 / 29.5)
        self.assertAlmostEqual(self.g["priceKw"], 29.5 * (7000 / 118 - 1800 / 29.5) / 1000)
        self.assertAlmostEqual(self.g["priceKw"], -0.05)           # the fleet netted more on each MWh: price narrows the gap
        self.assertAlmostEqual(e["above1000"], 0.8)
        self.assertAlmostEqual(e["above100"], 0.9)
        self.assertEqual([b["le"] for b in e["bands"]], [0, 25, 50, 100, 250, 1000, None])
        self.assertAlmostEqual(e["bands"][-1]["shareOfOffered"], 1.0)
        self.assertAlmostEqual(e["bands"][-1]["perMwDay"], (200 + 200) / 59)

    def test_the_three_parts_add_up_to_the_gap(self):
        g = self.g
        self.assertAlmostEqual(g["neverOfferedKw"] + g["offeredNotAwardedKw"] + g["priceKw"], g["gapKw"], places=12)
        self.assertAlmostEqual(g["offeredNotAwardedKw"], 12.0 - 15.0 * 45480 / 141600 + 0.05)

    def test_the_services(self):
        by = {s["key"]: s for s in self.g["services"]}
        self.assertEqual(list(by), SERVICES)
        up = by["regup"]
        self.assertAlmostEqual(up["modelKw"], 1.6)
        self.assertAlmostEqual(up["awardsKw"], 0.24)
        self.assertAlmostEqual(up["gapKw"], 1.36)
        self.assertAlmostEqual(up["unawardedKw"], 1.6)             # at least its gap: offered and not awarded
        self.assertAlmostEqual(up["awardOfOffer"], 0.1)
        self.assertAlmostEqual(up["offerShare"], 20000 / 141600)
        self.assertAlmostEqual(by["regdn"]["unawardedKw"], 2.0)    # the made-up default, 1,000 a month
        self.assertEqual(up["label"], "Regulation Up")

    def test_a_table_that_is_not_read_gives_no_figure(self):
        for k in ("noOffers", "noModel", "noAwards", "onlyPartial"):
            self.assertIsNone(self.got[k], k)

    def test_a_month_that_is_not_whole_everywhere_is_left_out_and_named(self):
        for k, why in (("febShort", "the offers table does not hold every day of it"), ("febModelShort", "the model does not hold every day of it"),
                       ("febLacks", "a figure is not held (limit_mwh_no_offer)")):
            g = self.got[k]
            self.assertEqual(g["months"], ["2026-01"], k)
            self.assertEqual(g["leftOut"], [{"m": "2026-02", "why": why}], k)
            self.assertAlmostEqual(g["modelKw"], 9.0)  # January's alone: February is not scaled, and not counted
            self.assertAlmostEqual(g["neverOfferedKw"] + g["offeredNotAwardedKw"] + g["priceKw"], g["gapKw"], places=12)

    def test_the_words_of_the_numbers(self):
        self.assertEqual(self.got["usd"], ["-0.62", "9.70", "0.00"])
        self.assertEqual(self.got["pct"], ["32.2%", "88%"])
        self.assertEqual(self.got["list"], ["a", "a and b", "a, b and c"])


class OnTheTables(unittest.TestCase):
    """On this machine's tables, when they are here: the page's arithmetic gives what the same arithmetic gives in Python
    (as runs/session116/analysis.py does it). Skipped in a checkout without the tables: warehouse/output is not in git."""

    @staticmethod
    def table(path, keep):
        rows = []
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if keep(r):
                    rows.append(r)
        return rows

    def test_the_page_and_python_agree(self):
        out = os.path.join(ROOT, "warehouse", "output")
        offers = next((p for p in (os.path.join(out, "ercot_storage_dam_offers_monthly.csv"),
                                   os.path.join(ROOT, "runs", "session116", "trial", "ercot_storage_dam_offers_monthly.csv")) if os.path.exists(p)), None)
        awards, stack = os.path.join(out, "ercot_storage_dam_awards_monthly.csv"), os.path.join(out, "battery_stack_monthly.csv")
        if not offers or not os.path.exists(awards) or not os.path.exists(stack):
            self.skipTest("the tables are not on this machine")
        O = self.table(offers, lambda r: True)
        A = self.table(awards, lambda r: True)
        M = self.table(stack, lambda r: r["entity"] == "ercot:HB_HUBAVG" and r["variable"].startswith("dayahead_2h_"))
        slim = lambda rs: [{"variable": r["variable"], "ts_utc": r["ts_utc"], "value": r["value"]} for r in rs]  # noqa: E731
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "rows.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"A": slim(A), "O": slim(O), "M": slim(M)}, f)
            g = node("import fs from 'node:fs'; const m = await import('./lib/storageawards.ts');"
                     f"const x = JSON.parse(fs.readFileSync({json.dumps(p)}, 'utf8')); console.log(JSON.stringify(m.gapOf(x.A, x.O, x.M)));")
        self.assertIsNotNone(g)

        def wide(rs, prefix=""):
            w = {}
            for r in rs:
                if r["variable"].startswith(prefix):
                    w.setdefault(r["ts_utc"][:7], {})[r["variable"][len(prefix):]] = float(r["value"])
            return w
        a, o, m = wide(A), wide(O), wide(M, "dayahead_2h_")
        months = [k for k in sorted(a) if a[k]["days_held"] == a[k]["days_in_month"] and k in o and o[k]["days_held"] == o[k]["days_in_month"]
                  and k in m and m[k]["days_held"] == m[k]["days_in_month"]]
        self.assertEqual(g["months"], months)
        self.assertTrue(months)
        s = lambda t, k: sum(t[x][k] for x in months)  # noqa: E731
        days, lim = s(o, "days_held"), s(o, "limit_mwh")
        model_kw, awards_kw = s(m, "revenue_total_usd_per_mw") / 1000, s(a, "revenue_total_usd_per_mw") / 1000
        never = model_kw * s(o, "limit_mwh_no_offer") / lim
        vm = s(m, "discharged_mwh_per_mw") / days
        va = sum(o[x]["energy_sold_mwh"] / o[x]["mw"] for x in months) / days
        pm = s(m, "revenue_energy_usd_per_mw") / (vm * days)
        pa = s(a, "revenue_energy_usd_per_mw") / (va * days)
        price = va * days * (pm - pa) / 1000
        for key, want in (("modelKw", model_kw), ("awardsKw", awards_kw), ("gapKw", model_kw - awards_kw), ("neverOfferedKw", never), ("priceKw", price),
                          ("offeredNotAwardedKw", model_kw - awards_kw - never - price), ("noOfferOutShare", s(o, "limit_mwh_no_offer_out") / lim)):
            self.assertAlmostEqual(g[key], want, places=9, msg=key)
        self.assertAlmostEqual(g["neverOfferedKw"] + g["offeredNotAwardedKw"] + g["priceKw"], g["gapKw"], places=9)
        for sv in g["services"]:
            k = sv["key"]
            self.assertAlmostEqual(sv["unawardedKw"], s(o, f"{k}_unawarded_usd_per_mw") / 1000, places=9, msg=k)
            self.assertAlmostEqual(sv["gapKw"], (s(m, f"revenue_{k}_usd_per_mw") - s(a, f"revenue_{k}_usd_per_mw")) / 1000, places=9, msg=k)
            self.assertAlmostEqual(sv["awardOfOffer"], s(o, f"{k}_award_mwh") / s(o, f"{k}_offer_mwh"), places=9, msg=k)
        # the offers table's own awards are the awards table's (the builder checks this before it writes a month)
        for x in months:
            self.assertAlmostEqual(o[x]["mw"], a[x]["mw"], places=3, msg=x)


if __name__ == "__main__":
    unittest.main()
