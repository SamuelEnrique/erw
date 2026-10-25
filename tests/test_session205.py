"""Session 205: the licensing sweep.

The reader of a publisher's terms page (one request a publisher, none to a paused host, none past the ceiling), the
rules that turn publishers' verdicts into a table's verdict, and the three files docs/licenses.md is written from, held
to each other. No network: the reader is given a stand-in for requests. Nothing here reads coverage.csv or a table:
those move every day, and the document is of 12 October 2026.
"""
import csv
import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import license_read  # noqa: E402
import licenses  # noqa: E402

META = os.path.join(ROOT, "warehouse", "metadata")


def rows(name):
    with open(os.path.join(META, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Reply:
    def __init__(self, status=200, content=b"<html>terms</html>", url="https://example.org/terms"):
        self.status_code, self.content, self.url, self.headers = status, content, url, {"Content-Type": "text/html; charset=utf-8"}


class TheReader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.record = os.path.join(self.tmp, "license_reads.csv")
        self.asked = []

    def get(self, url, **kw):
        self.asked.append((url, kw))
        return Reply(url=url)

    def read(self, publisher, url, ceiling=40, get=None):
        return license_read.read_one(publisher, url, ceiling, os.path.join(self.tmp, "keep"), self.record, get=get or self.get,
                                     now=dt.datetime(2026, 10, 12, 9, 53, tzinfo=dt.timezone.utc), log=lambda m: None)

    def test_one_request_with_the_erws_own_name_and_the_answer_is_written_down(self):
        row = self.read("A publisher", "https://example.org/terms")
        self.assertEqual(len(self.asked), 1)
        self.assertIn("ERW-connector", self.asked[0][1]["headers"]["User-Agent"])
        self.assertEqual((row["outcome"], row["http_status"], row["bytes"], row["read_at"]), ("read", 200, 18, "2026-10-12T09:53:00Z"))
        self.assertEqual(license_read.record(self.record)[0]["publisher"], "A publisher")
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "keep", "01_a_publisher", "page.bin")))

    def test_a_publisher_is_asked_once_whatever_the_answer(self):
        self.read("A publisher", "https://example.org/terms", get=lambda url, **kw: Reply(404, b"no", url))
        self.assertEqual(license_read.record(self.record)[0]["outcome"], "not read: HTTP 404")
        self.assertIsNone(self.read("A publisher", "https://example.org/other"))
        self.assertEqual(self.asked, [])              # the second address was never asked: a failed read is a read

    def test_a_paused_host_is_never_asked(self):
        row = self.read("MISO", "https://www.misoenergy.org/meet-miso/legal-and-privacy/")
        self.assertEqual(self.asked, [])
        self.assertTrue(row["outcome"].startswith("not asked: paused"))
        self.assertEqual(license_read.asked(license_read.record(self.record)), 0)     # a line with no request does not count against the ceiling

    def test_nothing_is_asked_at_the_ceiling(self):
        self.read("One", "https://example.org/1", ceiling=2)
        self.read("Two", "https://example.org/2", ceiling=2)
        self.assertIsNone(self.read("Three", "https://example.org/3", ceiling=2))
        self.assertEqual(len(self.asked), 2)

    def test_a_request_that_fails_is_written_down_and_not_tried_again(self):
        import requests

        def get(url, **kw):
            self.asked.append(url)
            raise requests.ConnectionError("down")
        row = self.read("A publisher", "https://example.org/terms", get=get)
        self.assertEqual((row["outcome"], len(self.asked)), ("not read: ConnectionError", 1))


class TheRules(unittest.TestCase):
    V = {"EIA": dict(verdict=licenses.PUBLIC, if_commercial=licenses.PUBLIC), "SPP": dict(verdict=licenses.PUBLIC, if_commercial=licenses.PERMISSION),
         "NYISO": dict(verdict=licenses.PERMISSION, if_commercial=licenses.PERMISSION), "PJM": dict(verdict=licenses.PAID, if_commercial=licenses.PAID)}

    def test_a_table_takes_the_most_restrictive_of_its_publishers(self):
        self.assertEqual(licenses.judge(["EIA", "SPP"], self.V), (licenses.PUBLIC, [], []))
        self.assertEqual(licenses.judge(["EIA", "NYISO", "SPP"], self.V), (licenses.PERMISSION, ["NYISO"], []))
        self.assertEqual(licenses.judge(["NYISO", "PJM"], self.V), (licenses.PAID, ["PJM"], []))
        self.assertEqual(licenses.judge(["EIA", "SPP"], self.V, "if_commercial"), (licenses.PERMISSION, ["SPP"], []))
        self.assertEqual(licenses.ORDER, [licenses.PUBLIC, licenses.PERMISSION, licenses.PAID, licenses.FORBIDDEN])

    def test_a_publisher_not_read_is_named_and_the_erws_own_work_has_none(self):
        self.assertEqual(licenses.judge(["EIA", "FERC"], self.V), (licenses.PUBLIC, [], ["FERC"]))     # write() calls this "not settled", never public
        self.assertEqual(licenses.judge(["ERW"], self.V), (licenses.PUBLIC, [], []))
        self.assertEqual(licenses.judge(["Anthropic"], self.V), (licenses.PUBLIC, [], []))
        self.assertIn('standing = "not settled"', src("scripts", "licenses.py"))

    def test_registry_names_and_hosts_fold_to_one_publisher(self):
        for name, key in (("California Independent System Operator (CAISO)", "CAISO"), ("California ISO (CAISO)", "CAISO"), ("New York ISO (NYISO)", "NYISO"),
                          ("U.S. Energy Information Administration", "EIA"), ("Board of Governors of the Federal Reserve System, through FRED (Federal Reserve Bank of St. Louis)", "FRED"),
                          ("International Monetary Fund (IMF PortWatch)", "IMF PortWatch"), ("International Monetary Fund (IMF)", "IMF"), ("mercury.bloomberg.com", "Bloomberg"),
                          ("partners.wsj.com", "WSJ"), ("cdn.misoenergy.org", "MISO"), ("hartenergy.com", "Hart Energy"), ("Switch", "Switch")):
            self.assertEqual(licenses.canon(name), key, name)

    def test_a_derived_table_keeps_the_operators_whose_grid_its_rows_cover(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        for name, head in (("iso_rtm_hub_prices", "# License: public\n"), ("texas_daily", "# Derived from: iso_rtm_hub_prices\n# License: public\n"),
                           ("all_daily", "# Derived from: iso_rtm_hub_prices; eia_fuel\n"), ("eia_fuel", "# License: public\n")):
            with open(os.path.join(tmp, name + ".csv"), "w", encoding="utf-8") as f:
                f.write(head + "entity,value\n")
        cov = [dict(table="iso_rtm_hub_prices", iso="CAISO;ERCOT;MISO;SPP"), dict(table="texas_daily", iso="ERCOT"), dict(table="all_daily", iso=""),
               dict(table="eia_fuel", iso="")]
        sources = [dict(publisher="U.S. Energy Information Administration (EIA)", tables="eia_fuel"), dict(publisher="Energy Research Warehouse (ERW), derived", tables="texas_daily; all_daily")]
        got = {t: pubs for t, pubs, _ in licenses.build_tables(tmp, cov, sources)}
        self.assertEqual(got["iso_rtm_hub_prices"], ["CAISO", "ERCOT", "MISO", "SPP"])
        self.assertEqual(got["texas_daily"], ["ERCOT"])                       # ERCOT's rows of a shared table do not inherit MISO
        self.assertEqual(got["all_daily"], ["CAISO", "EIA", "ERCOT", "MISO", "SPP"])   # no grid named in its own row: it keeps them all
        self.assertEqual(got["eia_fuel"], ["EIA"])


class TheFiles(unittest.TestCase):
    """The three files as committed, held to each other. None of them moves with a daily run."""

    def test_the_record_holds_the_reads_within_the_ceiling_and_asked_no_paused_publisher(self):
        reads = rows("license_reads.csv")
        self.assertEqual([int(r["n"]) for r in reads], list(range(1, len(reads) + 1)))
        self.assertLessEqual(license_read.asked(reads[:41]), 40)   # reads 1 to 41: session 205's sweep and the one read after it
        # later reads are each a later session's, under that session's own ceiling: 42 (session 307, Berkeley Lab) and
        # 43 (session 308, EEX), one read each
        # session 311's sweep may add up to 60; the licenses' later rounds (sessions 484 to 874) fitted within it, and
        # chain 048's sessions 887 and 888 add 12 and chain 049's session 902 adds 8, each session under its own ceiling of 20
        # (session 888 raised the bound); chain 051's sessions 911 and 914 add 3 and 14, each under its own ceiling (session
        # 914 raised the bound again); chain 052's session 928 adds 12 and chain 053's session 942 adds 5 (session 942 raised it
        # once more); chain 059's session 2047 adds 13 with chain 059's robots reads (session 2047 raised it again);
        # chain 056's sessions 2000 to 2005 add 7 (168 to 174) and chain 058's sessions 2028 to 2036 add 20, renumbered 192 to 211
        # at its merge after chain 059's (session 2041 raised it once more); chain 067's sessions 2070 to 2075 add 14,
        # renumbered 216 to 229 at its merge after chain 058's (session 2083 raised it once more);
        # chain 068's sessions 2084 to 2092 add 19, renumbered 223 to 241 after chain 066's and 237 to 255 after chain 067's (session
        # 2089 raised it by 40, with room for the chains' reads at their merges)
        # chain 069's sessions 2106 to 2114 add 17, renumbered 256 to 272 after chain 068's at session 2119's merge (session
        # 2111 raised it by 20; with chain 068's room of 40 the two chains' reads fit, 272 in all)
        # chain 079's sessions 2120 to 2127 add 17, renumbered 273 to 289 after chain 069's at session 2133's merge (session
        # 2123 raised it by 20 on its branch, joined here)
        # chain 092's sessions 2148 to 2153 add 12, renumbered 290 to 301 after chain 079's at session 2161's merge (its own
        # + 20 and chain 079's met as one; 260 later reads against 262 allowed)
        # chain 094's sessions 2162 to 2174 add 21, renumbered 302 to 322 after chain 092's at session 2171's merge (session
        # 2168 raised it by 20, joined here);
        # chain 090's sessions 2134 to 2141 add their reads from 256, renumbered 323 to 343 after chains 069, 079, 092 and 094's at session 2147's merges
        # (session 2135 raised it by 40, with room for the licenses' nineteenth round)
        # chain 098's sessions 2210 to 2217 add 13, renumbered 344 to 356 after chain 090's at session 2218's merge (session
        # 2211 raised it by 20, joined here)
        # chain 097's sessions 2176 to 2181 and 2188 add 22, renumbered 359 to 380 after chain 098's at session 2189's merge
        # (its sessions 2185 and 2188 raised it by 40 on its branch, met here as 20 more: 339 later reads against 342 allowed);
        # chain 099's sessions 2224 to 2236 add 23 from 344, renumbered 381 to 403 after chains 098 and 097's at session 2237's merges
        # (session 2236 raised it by 40)
        # chain 101's sessions 2238 to 2243 add 27 from 359, renumbered 404 to 430 after chains 097 and 099's at session 2247's
        # merge (session 2238 raised it by 20, joined here)
        # chain 102's sessions 2252 to 2257 add 31, renumbered 431 to 461 after chains 099 and 101's at session 2261's merge (within main's bound)
        # chain 103's sessions 2266 to 2278 add 21 from 404, renumbered 431 to 451 after chain 101's and 462 to 482 after
        # chain 102's at session 2279's merges (session 2279 raised it by 40)
        # chain 104's sessions 2280 to 2283 add 17 from 431, renumbered 483 to 499 after chains 102 and 103's at session 2293's merge
        # (session 2280 raised it by 20, joined here)
        # chain 106's sessions 2308 to 2315 add 25 from 483, renumbered 500 to 524 after chain 104's at session 2317's merge (session 2314 raised it by 40)
        # chain 105's sessions 2294 to 2299 add 19 from 483, renumbered 500 to 518 after chain 104's and 529 to 547 after
        # chain 106's at session 2307's merges (its + 20 met as one with chain 104's; within main's bound)
        # chain 108's sessions 2322 to 2329 add 36 from 500, renumbered 548 to 583 after chains 106's and 105's at session 2331's merge
        # (session 2322 raised it by 40; chain 106's + 40 met it as one at the merge, so it is raised by 40 again here)
        # chain 112's sessions from 2371 add reads from 584, beside chains 109's and 110's (session 2371 raised it by 40)
        # chain 110's sessions 2357 to 2362 add 38 from 584 (session 2362 raised it by 40), renumbered 636 to 673 after chain 112's at session 2370's merge
        # (chain 112's + 40 and session 2362's + 40 met as one at the merge, so it is raised by 40 again here)
        # chain 113's sessions 2385 to 2397 add 29 from 599, renumbered 636 to 664 after chain 112's and 674 to 702 after chain 110's
        # at session 2398's merge (chain 110's + 40 and session 2394's + 40 met as one at the merge, so it is raised by 40 again here)
        # chain 114's sessions 2406 to 2418 add 60 from 636, renumbered 703 to 762 after chains 110's and 113's at session 2415's merge
        # (sessions 2406 and 2413 raised it by 40 each; the two met main's as one at the merge, so it is raised by 40 again here)
        # chain 115's sessions 2420 to 2423 add 21 from 703 (session 2425 raised it by 40), renumbered 763 to 783 after chain 114's
        # at session 2433's merge
        # (session 2425's + 40 met chain 114's as one at the merge, so it is raised by 40 again here)
        # chain 117's sessions 2434 to 2446 add 26 from 703, renumbered 763 to 788 after chain 114's and 784 to 809 after chain 115's
        # at session 2447's merge (6 over main's bound of 762 once both chains' raises met as one, so it is raised by 40 here)
        # chain 121's sessions 2490 to 2497 add 46 from 810 (on its branch; chains 118 to 120 also begin at 810), so the bound is raised by 40
        # chain 122's sessions from 2504 add their reads from 867, so the bound is raised by 40 twice (sessions 2505 and 2516)
        # chain 123's sessions from 2518 add their reads from 930, so the bound is raised by 40
        # chain 124's sessions from 2532 add their reads from 971, so the bound is raised by 40
        # chain 125's sessions from 2546 add their reads from 1014, so the bound is raised by 40
        # chain 126's sessions from 2560 add their reads from 1048, so the bound is raised by 40
        # chain 127's sessions from 2574 add their reads from 1093, so the bound is raised by 40
        # chain 128's sessions from 2588 add their reads from 1139, so the bound is raised by 40
        # chain 129's sessions from 2602 add their reads from 1169, so the bound is raised by 40
        # chain 130's sessions from 2616 add their reads from 1222, so the bound is raised by 40
        # chain 131's sessions from 2630 add their reads from 1267, so the bound is raised by 40
        # chain 132's sessions from 2644 add their reads from 1296, so the bound is raised by 40
        # chain 133's sessions from 2658 add their reads from 1335, so the bound is raised by 40
        # chain 134's sessions from 2672 add their reads from 1373, so the bound is raised by 40
        # chain 135's sessions from 2686 add their reads from 1401, so the bound is raised by 40
        # chain 136's sessions from 2708 add their reads from 1425, so the bound is raised by 40
        # chain 137's sessions from 2722 add their reads from 1450, so the bound is raised by 40
        self.assertLessEqual(len(reads) - 41, 2 + 60 + 20 + 20 + 20 + 20 + 20 + 20 + 40 + 20 + 20 + 20 + 40 + 20 + 20 + 40 + 20 + 40 + 20 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40 + 40)
        self.assertEqual(len({r["publisher"] for r in reads}), len(reads))          # one page a publisher
        miso = [r for r in reads if "MISO" in r["publisher"]]
        self.assertEqual(len(miso), 1)
        self.assertTrue(miso[0]["outcome"].startswith("not asked: paused"))
        self.assertEqual((miso[0]["http_status"], miso[0]["bytes"]), ("", ""))
        for r in reads:
            self.assertNotRegex(r["url"], r"(?i)misoenergy|scc\.virginia") if not r["outcome"].startswith("not asked") else None
            if r["outcome"] == "read":
                self.assertEqual((r["http_status"], len(r["sha256"])), ("200", 64), r["publisher"])

    def test_every_verdict_is_one_of_the_four_and_every_sentence_has_a_read_behind_it(self):
        reads = {r["n"]: r for r in rows("license_reads.csv")}
        verdicts = rows("license_verdicts.csv")
        self.assertEqual(len({v["key"] for v in verdicts}), len(verdicts))
        for v in verdicts:
            self.assertIn(v["verdict"], licenses.ORDER, v["key"])
            self.assertIn(v["if_commercial"], licenses.ORDER, v["key"])
            self.assertLessEqual(licenses.ORDER.index(v["verdict"]), licenses.ORDER.index(v["if_commercial"]), v["key"])   # selling never loosens a verdict
            if v["sentence"]:
                self.assertIn(v["read"], reads, v["key"])
            if v["read"] and reads[v["read"]]["outcome"] != "read" and v["key"] != "MISO":
                self.assertEqual(v["sentence"], "", v["key"])                       # no sentence is quoted from a page that was not read
                self.assertTrue(v["note"].startswith("NOT READ"), v["key"])
                self.assertNotEqual(v["verdict"], licenses.PUBLIC) if v["key"] != "Berkeley Lab" else None
        miso = next(v for v in verdicts if v["key"] == "MISO")
        paused = next(r for r in rows("paused_sources.csv") if r["scope"] == "miso")
        self.assertEqual(miso["sentence"], paused["terms_quoted"])                  # the sentence a person already ruled on, not a new read
        self.assertTrue(miso["note"].startswith("NOT ASKED"))

    def test_every_publisher_of_a_table_is_read_or_named_as_not_read(self):
        verdicts = {v["key"] for v in rows("license_verdicts.csv")}
        tables = rows("license_tables.csv")
        self.assertEqual(len({t["table"] for t in tables}), len(tables))
        for t in tables:
            pubs = [p for p in t["publishers"].split("; ") if p]
            self.assertTrue(pubs, t["table"])
            self.assertTrue(t["how"], t["table"])
        named = {p for t in tables for p in t["publishers"].split("; ")}
        for key in ("EIA", "ERCOT", "CAISO", "ISO-NE", "NYISO", "SPP", "MISO", "PJM"):
            self.assertIn(key, named & verdicts)

    def test_the_document_and_the_drafts(self):
        doc = src("docs", "licenses.md")
        for words in ("## The reads", "## The publishers: the sentence and the verdict", "## Every table", "## Where the flag and the verdict disagree",
                      "### Public now", "### Permission needed", "### Paid", "Nothing was changed in `coverage.csv`", "not legal advice"):
            self.assertIn(words, doc)
        for t in rows("license_tables.csv"):
            self.assertIn(f"| `{t['table']}` |", doc, t["table"])
        for r in rows("license_reads.csv"):
            self.assertIn(r["url"], doc, r["publisher"])                            # every read is cited with its address
        for name in ("nyiso", "spp", "pjm", "miso", "isone", "fred", "imf", "rggi", "news-outlets", "datacenter-operators"):
            text = src("docs", "reviews", f"{name}-permission-email.md")
            self.assertIn("Nothing here was sent.", text, name)
            for words in ("What I am asking for:", "What we offer:", "No redistribution of your raw files or tables.", "github.com/SamuelEnrique/erw"):
                self.assertIn(words, text, name)
            self.assertNotIn(chr(0x2014), text, name)
            self.assertNotIn("@gmail.com", text, name)                              # no personal address is committed
        self.assertNotIn(chr(0x2014), doc)

    def test_the_scripts_ask_for_no_data_and_change_no_coverage(self):
        reader = src("scripts", "license_read.py")
        self.assertIn("ip.paused_host(host)", reader)
        self.assertIn("allow_redirects=True", reader)
        self.assertNotRegex(reader, r"for attempt in|retry")
        builder = src("scripts", "licenses.py")
        self.assertNotRegex(builder, r"(?m)^import requests|^from requests")
        self.assertNotRegex(builder, r"open\(COVERAGE, \"w\"")
        for f in ("tests/test_session205.py", "scripts/licenses.py", "scripts/license_read.py"):
            self.assertNotIn(chr(0x2014), src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
