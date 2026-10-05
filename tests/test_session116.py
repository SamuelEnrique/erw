"""Session 116: what Texas's storage resources offered day-ahead, and the standing pull of one zip a day.

    python -m unittest tests.test_session116

On a saved real sample, never on rows made for the test: tests/fixtures/session116/ holds, for the operating days 6 and
7 December 2025, the rows of 14 resources (and of one that offered without a row in the data file) cut from ERCOT's own
two files, 60d_DAM_ESR_Data and 60d_DAM_ESR_ASOffers, every column, as they came in the zips
(tests/fixtures/session116/make_fixture.py). The sums are computed again here in exact decimals, without the builder's code.
No request is made: ERCOT's server is a stand-in that counts what it is asked.
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import ercot_dam_esr as esr  # noqa: E402
import ercot_storage_dam_awards as awards  # noqa: E402
import ercot_storage_dam_offers as offers  # noqa: E402
import iso_prices as ip  # noqa: E402
import scheduled  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session116")
DAY1, DAY2 = dt.date(2025, 12, 6), dt.date(2025, 12, 7)
FILES = {DAY1: ("60d_DAM_ESR_Data-04-FEB-26.csv", "60d_DAM_ESR_ASOffers-04-FEB-26.csv"),
         DAY2: ("60d_DAM_ESR_Data-05-FEB-26.csv", "60d_DAM_ESR_ASOffers-05-FEB-26.csv")}
PUBLISHED = {DAY1: "2026-02-04T17:53:35-06:00", DAY2: "2026-02-05T11:42:13-06:00"}
PRICES = {"regup": ["REGUP"], "regdn": ["REGDOWN"], "rrs": ["RRSPFR", "RRSFFR", "RRSUFR"], "ecrs": ["ECRS", "OFFEC"], "nspin": ["ONLINE NONSPIN", "OFFLINE NONSPIN"]}
AWARDS = {"regup": (["RegUp Awarded"], "RegUp MCPC"), "regdn": (["RegDown Awarded"], "RegDown MCPC"),
          "rrs": (["RRSPFR Awarded", "RRSFFR Awarded", "RRSUFR Awarded"], "RRS MCPC"), "ecrs": (["ECRSSD Awarded"], "ECRS MCPC"),
          "nspin": (["NonSpin Awarded"], "NonSpin MCPC")}


def text(day, which):
    with open(os.path.join(FIX, FILES[day][which]), encoding="utf-8", newline="") as f:
        return f.read()


def dicts(day, which):
    return [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(io.StringIO(text(day, which)))]


def zip_of(day, data=None, aso=None):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(FILES[day][0], text(day, 0) if data is None else data)
        z.writestr(FILES[day][1], text(day, 1) if aso is None else aso)
        z.writestr("60d_DAM_Gen_Resource_Data-04-FEB-26.csv", "not read\n")
    return b.getvalue()


def D(x):
    return Decimal(x) if x != "" else Decimal(0)


def by_hand(day):
    """The day's sums from ERCOT's rows, in exact decimals, by a path that shares nothing with the builder."""
    data, aso = dicts(day, 0), dicts(day, 1)
    rows = {(r["Resource Name"], r["Hour Ending"]): r for r in data}
    mcpc = {}
    for r in data:
        for s, (_, m) in AWARDS.items():
            if r[m] != "":
                mcpc[(s, r["Hour Ending"])] = Decimal(r[m])
    out = {k: Decimal(0) for k in ["limit_mwh", "limit_mwh_no_offer", "limit_mwh_out", "energy_sold_mwh", "energy_bought_mwh", "energy_offer_mwh", "as_offer_mwh",
                                   "as_offer_mwh_unlisted"]}
    offered = {}
    with_offer = set()
    for r in aso:
        k = (r["Resource Name"], r["Hour Ending"])
        for i in range(1, 6):
            q = r[f"QUANTITY MW{i}"]
            priced = {s for s, cols in PRICES.items() if any(r[f"PRICE{i} {c}"] != "" for c in cols)}
            if q == "" or not priced:
                continue
            if k not in rows:
                out["as_offer_mwh_unlisted"] += Decimal(q)
                continue
            with_offer.add(k)
            out["as_offer_mwh"] += Decimal(q)
            for s in priced:
                offered[(s, k)] = offered.get((s, k), Decimal(0)) + Decimal(q)
                out[f"{s}_offer_mwh"] = out.get(f"{s}_offer_mwh", Decimal(0)) + Decimal(q)
                low = min(Decimal(r[f"PRICE{i} {c}"]) for c in PRICES[s] if r[f"PRICE{i} {c}"] != "")
                if low <= mcpc[(s, k[1])]:
                    out[f"{s}_offer_mwh_le_mcpc"] = out.get(f"{s}_offer_mwh_le_mcpc", Decimal(0)) + Decimal(q)
    n_none = 0
    for k, r in rows.items():
        hsl = max(Decimal(r["HSL"]), Decimal(0))
        curve = [Decimal(r[f"QSE submitted Curve-MW{i}"]) for i in range(1, 11) if r[f"QSE submitted Curve-MW{i}"] != ""]
        out["limit_mwh"] += hsl
        if r["Resource Status"] == "OUT":
            out["limit_mwh_out"] += hsl
        if not curve and k not in with_offer:
            out["limit_mwh_no_offer"] += hsl
            n_none += 1
        if curve:
            out["energy_offer_mwh"] += max(max(curve), Decimal(0))
        q = D(r["Awarded Quantity"])
        out["energy_sold_mwh"] += max(q, Decimal(0))
        out["energy_bought_mwh"] += max(-q, Decimal(0))
        for s, (cols, m) in AWARDS.items():
            a = sum(D(r[c]) for c in cols)
            out[f"{s}_award_mwh"] = out.get(f"{s}_award_mwh", Decimal(0)) + a
            if a:
                out[f"{s}_award_usd"] = out.get(f"{s}_award_usd", Decimal(0)) + a * Decimal(r[m])
            left = offered.get((s, k), Decimal(0)) - a
            if left > 0:
                out[f"{s}_unawarded_usd"] = out.get(f"{s}_unawarded_usd", Decimal(0)) + left * mcpc[(s, k[1])]
    out["resource_hours"] = len(rows)
    out["resource_hours_no_offer"] = n_none
    return out


def values(day, data=None, aso=None):
    e, a = offers.read_zip(zip_of(day, data, aso))
    return offers.day_values(e, a, day)


class Offers(unittest.TestCase):
    """The day's sums are ERCOT's rows added up: nothing filled, capped or smoothed."""

    def test_the_sample_is_real_and_holds_every_case(self):
        data, aso = dicts(DAY1, 0), dicts(DAY1, 1)
        self.assertEqual({r["Delivery Date"] for r in data}, {"12/06/2025"})
        self.assertEqual(len({r["Resource Name"] for r in data}), 14)
        self.assertTrue(any(r["Resource Status"] == "OUT" for r in data))
        self.assertTrue({r["Resource Name"] for r in aso} - {r["Resource Name"] for r in data}, "a resource that offers without a row in the data file")
        self.assertEqual(len(next(csv.reader(io.StringIO(text(DAY1, 0))))), 48)
        self.assertEqual(len(next(csv.reader(io.StringIO(text(DAY1, 1))))), 61)

    def test_each_days_sums_equal_the_sum_of_the_rows(self):
        for day in (DAY1, DAY2):
            v, hand = values(day), by_hand(day)
            self.assertGreater(hand["as_offer_mwh"], 0)
            self.assertGreater(hand["limit_mwh_no_offer"], 0)
            for k, x in hand.items():
                self.assertAlmostEqual(v.get(k, 0.0), float(x), places=6, msg=f"{day} {k}")

    def test_an_offer_is_counted_as_printed_also_above_the_limit(self):
        # ERCOT's blocks are added up as printed: on the sample a resource's upward blocks pass its limit in some hour
        data, aso = dicts(DAY1, 0), dicts(DAY1, 1)
        hsl = {(r["Resource Name"], r["Hour Ending"]): Decimal(r["HSL"]) for r in data}
        over = Decimal(0)
        for r in aso:
            k = (r["Resource Name"], r["Hour Ending"])
            q = sum(Decimal(r[f"QUANTITY MW{i}"]) for i in range(1, 6) if r[f"QUANTITY MW{i}"] != "" and r[f"PRICE{i} REGDOWN"] != "")
            if k in hsl and q > hsl[k]:
                over += q - hsl[k]
        src = open(os.path.join(ROOT, "warehouse", "derived", "ercot_storage_dam_offers.py"), encoding="utf-8").read()
        self.assertNotIn(".clip(upper", src.split("def day_values")[1].split("def unit_of")[0])
        self.assertAlmostEqual(values(DAY1)["regdn_offer_mwh"], float(by_hand(DAY1)["regdn_offer_mwh"]), places=6)
        self.assertGreaterEqual(over, 0)

    def test_an_offer_by_a_resource_with_no_data_row_is_counted_alone(self):
        v = values(DAY1)
        self.assertGreater(v["as_offer_mwh_unlisted"], 0)
        # with that resource's offers taken out of ERCOT's file, no other sum moves
        head, *body = list(csv.reader(io.StringIO(text(DAY1, 1))))
        names = {r["Resource Name"] for r in dicts(DAY1, 0)}
        b = io.StringIO()
        w = csv.writer(b, lineterminator="\n")
        w.writerow(head)
        w.writerows(r for r in body if r[head.index("Resource Name")].strip() in names)
        w2 = values(DAY1, aso=b.getvalue())
        self.assertEqual(w2["as_offer_mwh_unlisted"], 0)
        for k in v:
            if k != "as_offer_mwh_unlisted":
                self.assertEqual(v[k], w2[k], k)

    def test_the_curve_is_read_as_straight_lines_between_its_points(self):
        nan = float("nan")
        # a real curve of the sample day in ERCOT's file: charge 5 MW at -250 or less, sell 10 MW only at 5,000
        M = np.array([[-5, -0.1, 0, 0, 0.1, 10, nan, nan, nan, nan], [nan] * 10])
        P = np.array([[-250, -249, -248, 4998, 4999, 5000, nan, nan, nan, nan], [nan] * 10])
        for price, mw in ((-300, -5), (-250, -5), (-249.5, -2.55), (-248, 0), (22.85, 0), (4998, 0), (4998.5, 0.05), (4999, 0.1), (4999.5, 5.05), (5000, 10), (9000, 10)):
            self.assertAlmostEqual(offers.curve_at(M, P, price)[0], mw, places=9, msg=str(price))
        self.assertTrue(np.isnan(offers.curve_at(M, P, 0)[1]))
        # two points at one price: the higher MW at that price
        M2, P2 = np.array([[0.0, 10.0] + [nan] * 8]), np.array([[30.0, 30.0] + [nan] * 8])
        self.assertEqual(offers.curve_at(M2, P2, 30)[0], 10)
        self.assertEqual(offers.curve_at(M2, P2, 29.99)[0], 0)
        # on the sample, what the curves offer at each hour's own price is what was awarded, to within a tenth of a MW a row
        v = values(DAY1)
        self.assertGreater(v["_curve_rows"], 0)
        self.assertGreaterEqual(v["_curve_rows_award_on_curve"] / v["_curve_rows"], 0.9)
        self.assertLessEqual(v["energy_offer_mwh_le_0"], v["energy_offer_mwh_le_100"])
        self.assertLessEqual(v["energy_offer_mwh_le_1000"], v["energy_offer_mwh"])

    def test_a_day_that_fails_a_check_has_no_values(self):
        with self.assertRaises(ValueError):   # the file of another day
            e, a = offers.read_zip(zip_of(DAY1))
            offers.day_values(e, a, DAY2)
        with self.assertRaises(ValueError):   # a zip without the offers file
            b = io.BytesIO()
            with zipfile.ZipFile(b, "w") as z:
                z.writestr(FILES[DAY1][0], text(DAY1, 0))
            offers.read_zip(b.getvalue())
        with self.assertRaises(ValueError):   # a repeated resource and hour
            t = text(DAY1, 0)
            values(DAY1, data=t + t.split("\n")[1] + "\n")
        with self.assertRaises(ValueError):   # an offer in an hour with no clearing price printed: never valued at another
            head, *body = list(csv.reader(io.StringIO(text(DAY1, 0))))
            i = head.index("RegUp MCPC")
            b = io.StringIO()
            w = csv.writer(b, lineterminator="\n")
            w.writerow(head)
            w.writerows(r[:i] + [""] + r[i + 1:] for r in body)
            values(DAY1, data=b.getvalue())

    def _awards_table(self, days):
        frames = []
        for day in days:
            _, df = esr.read_esr(zip_of(day))
            frames.append(esr.to_rows(df, day, "https://example.invalid/zip", "2026-10-05T00:00:00Z", "2026-02-04T23:53:35Z"))
        res, held = awards.combine([awards.by_resource(pd.concat(frames, ignore_index=True))])
        return awards.rows_of(awards.monthly(res, held), "2026-10-05T00:00:00Z")

    def _daily_table(self, days):
        return pd.concat([offers.day_rows(values(d), d, "https://example.invalid/zip", "2026-10-05T00:00:00Z", "2026-02-04T23:53:35Z") for d in days], ignore_index=True)

    def test_the_month_is_its_days_added_up_and_checked_against_the_awards_table(self):
        daily = self._daily_table([DAY1, DAY2])
        self.assertFalse(daily["variable"].str.startswith("_").any())
        self.assertEqual(set(daily["unit"]), {"MWh", "USD", "count"})
        m = offers.monthly(daily, self._awards_table([DAY1, DAY2]))["2025-12"]
        hand = [by_hand(DAY1), by_hand(DAY2)]
        for k in ("limit_mwh", "limit_mwh_no_offer", "energy_offer_mwh", "regup_offer_mwh", "rrs_award_mwh", "nspin_unawarded_usd", "as_offer_mwh"):
            self.assertAlmostEqual(m[k], float(hand[0].get(k, 0) + hand[1].get(k, 0)), places=2, msg=k)
        self.assertEqual((m["days_held"], m["days_missing"], m["days_in_month"]), (2, 0, 31))   # a partial month: nothing scaled
        self.assertAlmostEqual(m["regup_unawarded_usd_per_mw"], m["regup_unawarded_usd"] / m["mw"], places=9)
        # the awards table of other days: the two disagree, and nothing is written
        with self.assertRaises(RuntimeError):
            offers.monthly(daily, self._awards_table([DAY1]))
        with self.assertRaises(RuntimeError):
            offers.monthly(self._daily_table([DAY1]), self._awards_table([DAY1, DAY2]))

    def test_a_missing_day_is_counted_and_nothing_is_filled(self):
        day3 = dt.date(2025, 12, 8)
        d1 = self._daily_table([DAY1])
        d3 = d1.assign(ts_utc=f"{day3.isoformat()}T00:00:00Z")   # the same real rows under a later day: only the calendar is tested
        a = self._awards_table([DAY1])
        a = a.assign(value=[str(float(v) * 2) if var in ("days_held", "resource_hours", "energy_sold_mwh", "energy_bought_mwh") or var.endswith("_usd") else v
                            for v, var in zip(a["value"], a["variable"])])
        m = offers.monthly(pd.concat([d1, d3], ignore_index=True), a)["2025-12"]
        self.assertEqual((m["days_held"], m["days_missing"]), (2, 1))
        self.assertAlmostEqual(m["limit_mwh"], 2 * float(by_hand(DAY1)["limit_mwh"]), places=3)

    def test_the_tables_the_builder_writes_pass_the_validator(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
        import erw_validate
        daily = self._daily_table([DAY1, DAY2]).sort_values(offers.KEY).reset_index(drop=True)
        months = offers.month_rows(offers.monthly(daily, self._awards_table([DAY1, DAY2])), "2026-10-05T00:00:00Z")
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = os.path.join(d, offers.DAILY + ".csv"), os.path.join(d, offers.MONTHLY + ".csv")
            offers.write_table(p1, offers.daily_header(daily, "20261005T000000Z", "x.log"), daily)
            offers.write_table(p2, ["Energy Research Warehouse (ERW): a test's copy", f"Source: {offers.SOURCE} a test", "License: public."], months)
            self.assertEqual(erw_validate.main([p1, p2]), 0)
            head = open(p1, encoding="utf-8").read().split("\n")[:12]
            self.assertTrue(any("WHAT IT IS NOT" in x for x in head))
            self.assertTrue(any("Operating days held: 2, 2025-12-06 to 2025-12-07" in x for x in head))


class Answer:
    def __init__(self, content=b"", text="", status_code=200):
        self.content, self.text, self.status_code = content, text, status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise IOError(f"HTTP {self.status_code}")


class StandingPull(unittest.TestCase):
    """One zip a run, the next operating day; a day is added to the table and never fills or replaces another."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.keep = (esr.RAW, esr.ZIPS, esr.MONTHS, esr.MANIFEST)
        esr.RAW, esr.ZIPS, esr.MONTHS = d, os.path.join(d, "zips"), os.path.join(d, "months")
        esr.MANIFEST = os.path.join(esr.ZIPS, "manifest.csv")
        self.table = os.path.join(d, esr.TABLE + ".csv")
        self.missing = os.path.join(d, "missing_days.csv")
        _, df = esr.read_esr(zip_of(DAY1))
        self.rows1 = esr.to_rows(df, DAY1, "https://example.invalid/1", "2026-10-05T03:13:00Z", "2026-02-04T23:53:35Z")
        with open(self.table, "w", encoding="utf-8", newline="") as f:
            f.write("# Energy Research Warehouse (ERW): a test's copy of the table, one real day of the sample\n")
            f.write("# Operating days held: 1, 2025-12-06 to 2025-12-06 (local, Central). Days missing between them: 0. Nothing is filled for a missing day.\n")
            f.write("# Retrieved: 20261005T031300Z (UTC) by warehouse/connectors/ercot_dam_esr.py\n# Run log: warehouse/output/logs/old.log\n")
            f.write(f"# File holds {len(self.rows1):,} rows of a ceiling of 9,000,000 (the approved pull).\n")
            self.rows1.to_csv(f, index=False, lineterminator="\n")
        self.calls, self.ran = [], []

    def tearDown(self):
        esr.RAW, esr.ZIPS, esr.MONTHS, esr.MANIFEST = self.keep
        self.tmp.cleanup()

    def server(self, docs, contents):
        listing = json.dumps({"ListDocsByRptTypeRes": {"DocumentList": [{"Document": d} for d in docs]}})

        def get(url, **kw):
            self.calls.append(url)
            if url == esr.LIST:
                return Answer(text=listing)
            return Answer(content=contents[url.split("=")[-1]])
        return get

    def run_builder(self, cmd, **kw):
        self.ran.append([os.path.basename(cmd[1])] + cmd[2:])
        return type("R", (), {"returncode": 0})()

    def doc(self, day, content, doc_id, size=None):
        published = (dt.datetime.combine(day, dt.time(17, 0)) + dt.timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S-06:00")
        return {"ConstructedName": f"ext.{doc_id}.zip", "DocID": doc_id, "ContentSize": str(len(content) if size is None else size), "PublishDate": published}

    def daily(self, docs, contents):
        return esr.daily(lambda m: None, "20261006T140000Z", get=self.server(docs, contents), run=self.run_builder, table_path=self.table,
                         missing_path=self.missing, pause=0)

    def test_one_zip_a_run_the_oldest_day_first(self):
        z2 = zip_of(DAY2)
        day3, day4 = DAY2 + dt.timedelta(days=1), DAY2 + dt.timedelta(days=2)
        # three days wait; the zip listed for the 8th holds the 7th's file, so the 8th fails its check
        docs = [self.doc(day4, z2, "40"), self.doc(DAY2, z2, "20"), self.doc(day3, z2, "30"), self.doc(DAY1, zip_of(DAY1), "10")]
        contents = {"20": z2, "30": z2, "40": z2, "10": zip_of(DAY1)}
        before = open(self.table, encoding="utf-8").read()
        self.assertEqual(self.daily(docs, contents), 0)
        self.assertEqual(self.calls, [esr.LIST, esr.FILE.format(doc="20")])          # the list, and one zip
        self.assertEqual(esr.last_day_held(self.table), DAY2)
        after = open(self.table, encoding="utf-8").read()
        self.assertIn("Operating days held: 2, 2025-12-06 to 2025-12-07", after)
        _, df2 = esr.read_esr(z2)
        n2 = len(df2)
        self.assertIn(f"File holds {len(self.rows1) + n2:,} rows", after)
        self.assertIn("# Retrieved: 20261006T140000Z (UTC)", after)
        old_rows = [x for x in before.split("\n") if x and not x.startswith("#")]
        new_rows = [x for x in after.split("\n") if x and not x.startswith("#")]
        self.assertEqual(new_rows[:len(old_rows)], old_rows)                          # every row already there, as it was
        self.assertEqual(len(new_rows) - len(old_rows), n2)
        t = ip.read_series(self.table, esr.COLS)
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual([r["how"] for r in esr.manifest()], ["requested daily"])
        self.assertEqual(self.ran, [["ercot_storage_dam_awards.py"], ["ercot_storage_dam_offers.py", "--days", "2025-12-07"]])
        # the next run: the 8th, one zip; it fails its check, has no rows, and is written down
        self.calls.clear()
        self.ran.clear()
        self.assertEqual(self.daily(docs, contents), 1)
        self.assertEqual(self.calls, [esr.LIST, esr.FILE.format(doc="30")])
        self.assertEqual(open(self.table, encoding="utf-8").read(), after)
        self.assertEqual(list(esr.failed_days(self.missing)), [day3])
        self.assertEqual(self.ran, [])
        # the run after goes on to the 9th and does not ask for the 8th again
        self.calls.clear()
        self.assertEqual(self.daily(docs, contents), 1)
        self.assertEqual(self.calls, [esr.LIST, esr.FILE.format(doc="40")])
        self.assertEqual(sorted(esr.failed_days(self.missing)), [day3, day4])
        # and then ERCOT lists nothing newer: the list only, no zip
        self.calls.clear()
        self.assertEqual(self.daily(docs, contents), 0)
        self.assertEqual(self.calls, [esr.LIST])

    def test_a_zip_already_on_the_machine_is_not_requested(self):
        z2 = zip_of(DAY2)
        os.makedirs(esr.ZIPS)
        with open(os.path.join(esr.ZIPS, "ext.20.zip"), "wb") as f:
            f.write(z2)
        self.assertEqual(self.daily([self.doc(DAY2, z2, "20")], {"20": z2}), 0)
        self.assertEqual(self.calls, [esr.LIST])
        self.assertEqual(esr.last_day_held(self.table), DAY2)

    def test_no_request_without_the_table_above_the_size_or_while_paused(self):
        z2 = zip_of(DAY2)
        with self.assertRaises(RuntimeError):   # a zip listed above 60 MB is not asked for
            self.daily([self.doc(DAY2, z2, "20", size=esr.DAILY_MAX_BYTES + 1)], {"20": z2})
        self.assertEqual(self.calls, [esr.LIST])
        self.calls.clear()
        os.remove(self.table)
        self.daily([self.doc(DAY2, z2, "20")], {"20": z2})
        self.assertEqual(self.calls, [])
        keep = (ip.paused, ip.pause_line)
        try:
            ip.paused, ip.pause_line = (lambda scope: True), (lambda scope: "PAUSED (a test)")
            with self.assertRaises(SystemExit):
                self.daily([self.doc(DAY2, z2, "20")], {"20": z2})
            self.assertEqual(self.calls, [])
        finally:
            ip.paused, ip.pause_line = keep

    def test_a_day_is_only_ever_added_after_the_last(self):
        with self.assertRaises(RuntimeError):
            esr.append_day(self.table, self.rows1, DAY1, "20261006T140000Z", "x.log")
        days, doc, waiting = esr.next_day([self.doc(DAY1, b"", "10")], DAY1)
        self.assertEqual((days, doc, waiting), (None, None, 0))

    def test_the_offers_builder_adds_the_day_from_its_saved_zip(self):
        keep = (offers.ZIPS, offers.MANIFEST)
        try:
            offers.ZIPS, offers.MANIFEST = esr.ZIPS, esr.MANIFEST
            os.makedirs(esr.ZIPS)
            for day, name in ((DAY1, "a.zip"), (DAY2, "b.zip")):
                with open(os.path.join(esr.ZIPS, name), "wb") as f:
                    f.write(zip_of(day))
                esr.manifest_add({"operating_day": day.isoformat(), "file": name, "doc_id": "1", "url": "https://example.invalid/" + name, "bytes": 1, "sha256": "",
                                  "published": PUBLISHED[day], "retrieved_at": "2026-10-05T03:13:00Z", "how": "requested daily"})
            log = lambda m: None  # noqa: E731
            one = offers.days_from_zips([DAY1], log)
            both = offers.merge_daily(one, offers.days_from_zips([DAY2], log))
            self.assertEqual(sorted(set(both["ts_utc"])), ["2025-12-06T00:00:00Z", "2025-12-07T00:00:00Z"])
            self.assertEqual(len(both), 2 * len(one))
            again = offers.merge_daily(both, offers.days_from_zips([DAY2], log))     # a day added twice is there once
            self.assertEqual(len(again), len(both))
            with self.assertRaises(RuntimeError):                                    # a day with no saved zip: never a hole
                offers.days_from_zips([dt.date(2025, 12, 9)], log)
        finally:
            offers.ZIPS, offers.MANIFEST = keep


class Records(unittest.TestCase):
    """Where the tables and the standing pull are registered, and what stays as it was."""

    def test_the_daily_run_starts_it_once_under_health(self):
        sh = open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8").read()
        self.assertEqual(sh.count('soft_step ercot_storage_dam "$PYTHON" warehouse/scheduled.py ercot_storage_dam'), 1)
        soft = open(os.path.join(ROOT, "warehouse", "soft_step.sh"), encoding="utf-8").read()
        self.assertIn('warehouse/health.py run --step "$name"', soft)
        job = scheduled.JOBS["ercot_storage_dam"]
        self.assertEqual(job["cmd"], ["warehouse/connectors/ercot_dam_esr.py", "--daily"])
        self.assertEqual(job["cadence"], "daily")
        self.assertEqual(set(job["tables"]), {"ercot_dam_esr_awards", "ercot_storage_dam_awards_monthly", offers.DAILY, offers.MONTHLY})
        src = open(os.path.join(ROOT, "warehouse", "connectors", "ercot_dam_esr.py"), encoding="utf-8").read()
        body = src.split("def daily(")[1].split("\ndef main(")[0]
        self.assertEqual(body.count("get(url"), 1)             # one zip is asked for in a run, in one place, outside any loop
        self.assertNotIn("for attempt", body)
        self.assertLess(body.index('ip.paused("ercot")'), body.index("get(LIST"))

    def test_the_tables_are_held_out_of_the_catalogue(self):
        live = yaml.safe_load(open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
        self.assertIn(offers.DAILY, live["catalogue_hold"])
        self.assertIn(offers.MONTHLY, live["review_hold"])
        self.assertIn(offers.SOURCE, live["sources_hold"])
        text = open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8").read()
        self.assertIn("'^ercot_storage_dam_offers_monthly$'", text)
        self.assertNotIn("'^ercot_storage_dam_offers_daily$'", text)

    def test_miso_stays_paused(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv"), encoding="utf-8") as f:
            self.assertIn("miso", f.read().lower())
        self.assertTrue(ip.paused("miso"))
        self.assertFalse(ip.paused("ercot"))

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in ("warehouse/derived/ercot_storage_dam_offers.py", "warehouse/connectors/ercot_dam_esr.py", "warehouse/scheduled.py", "tests/test_session116.py",
                    "tests/fixtures/session116/make_fixture.py", "docs/methods/ercot_storage_dam_offers.md"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)

    @unittest.skipUnless(os.path.exists(os.path.join(ip.OUT_DIR, offers.MONTHLY + ".csv")) and os.path.exists(os.path.join(ip.OUT_DIR, offers.DAILY + ".csv")),
                         "the tables are not on this machine")
    def test_the_tables_on_this_machine_add_up(self):
        d = ip.read_series(os.path.join(ip.OUT_DIR, offers.DAILY + ".csv"), offers.COLS)
        m = ip.read_series(os.path.join(ip.OUT_DIR, offers.MONTHLY + ".csv"), offers.COLS)
        d["x"], m["x"] = pd.to_numeric(d["value"]), pd.to_numeric(m["value"])
        for var in ("limit_mwh", "energy_offer_mwh", "as_offer_mwh", "rrs_unawarded_usd"):
            by_month = d[d["variable"] == var].groupby(d["ts_utc"].str[:7])["x"].sum()
            mm = m[m["variable"] == var]
            got = mm.set_index(mm["ts_utc"].str[:7])["x"]
            for month in by_month.index:
                self.assertAlmostEqual(by_month[month], got[month], delta=0.02 * 31, msg=f"{var} {month}")
        w = m.pivot(index="ts_utc", columns="variable", values="x")
        # the parts of the limit are parts: none is larger than the whole, and what the curves offer at the hour's price is within what they offer at any price
        self.assertTrue((w["limit_mwh_no_offer"] <= w["limit_mwh"]).all())
        self.assertTrue((w["limit_mwh_no_offer_out"] <= w["limit_mwh_no_offer"]).all())
        self.assertTrue((w["energy_offer_mwh_at_clearing"] <= w["energy_offer_mwh"]).all())
        for s in offers.SERVICES:
            self.assertTrue((w[f"{s}_offer_mwh_le_mcpc"] <= w[f"{s}_offer_mwh"]).all(), s)
            self.assertTrue((w[f"{s}_award_mwh"] <= w[f"{s}_offer_mwh"]).all(), s)


if __name__ == "__main__":
    unittest.main()
