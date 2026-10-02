"""Session 65: capacity and ancillary service prices, the gates, the lock's holder.

Energy Research Warehouse (ERW). No request leaves the machine. The CAISO and ERCOT parsers read real documents saved
in tests/fixtures/session65/ (public sources): two OASIS PRC_AS answers (an ordinary day and the 25-hour day), one
ERCOT NP4-188-CD daily document, and the first two days of ERCOT's 2018 NP4-181-ER yearly file. The capacity sources
whose terms do not allow republishing (PJM, ISO-NE, MISO) and NYISO's page are not copied into the repository: their
parsers are tested on the documents in warehouse/raw/iso_capacity_prices/ when this machine holds them (skipped
elsewhere), and their grammar on small made-up markup with made-up numbers.

    python -m unittest tests.test_session65 -v
"""

import csv
import glob
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/supabase", "warehouse/validate"):
    sys.path.insert(0, os.path.join(ROOT, p))

import iso_prices as ip  # noqa: E402
import caiso_as_prices as caiso  # noqa: E402
import ercot_as_prices as ercot  # noqa: E402
import iso_capacity_prices as cap  # noqa: E402
import lock  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session65")
RAW = os.path.join(ROOT, "warehouse", "raw")
quiet = lambda msg: None  # noqa: E731


def fixture(name):
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


def raw_doc(connector, part):
    """A document this machine saved in warehouse/raw/<connector>/ whose URL holds `part`, or None."""
    for man in sorted(glob.glob(os.path.join(RAW, connector, "*", "manifest.csv")), reverse=True):
        with open(man, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                path = os.path.join(os.path.dirname(man), r["file"])
                if part in r["url"] and r["status"] == "200" and os.path.exists(path):
                    with open(path, "rb") as g:
                        return g.read()
    return None


def raw_store(root, connector, docs):
    """A raw folder as an earlier run leaves it: {url: bytes} saved with a manifest, so an offline run reads them."""
    d = os.path.join(root, connector, "20000101T000000Z")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "manifest.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("retrieved_at,status,bytes,sha256,last_modified,file,url\n")
        for i, (url, body) in enumerate(docs.items()):
            with open(os.path.join(d, f"doc{i}"), "wb") as g:
                g.write(body)
            f.write(f'"2026-10-02T15:00:00Z","200","{len(body)}","{hashlib.sha256(body).hexdigest()}","","doc{i}","{url}"\n')


def read_table(path):
    return pd.read_csv(path, comment="#", dtype=str, keep_default_na=False)


class Scratch(unittest.TestCase):
    """A run of a connector's main() into a temporary directory, raw files included, restored after."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw65_")
        self.saved = {k: getattr(ip, k) for k in ("OUT_DIR", "LOG_DIR", "RAW_DIR", "METADATA_DIR", "STATUS_DIR")}
        self.raw = os.path.join(self.tmp, "rawdocs")
        ip.RAW_DIR = self.raw
        self.out = os.path.join(self.tmp, "out")

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(ip, k, v)
        ip.RAW.dir = None
        shutil.rmtree(self.tmp, ignore_errors=True)

    def status(self, connector):
        with open(os.path.join(self.out, "status", connector + ".json"), encoding="utf-8") as f:
            return json.load(f)["results"]


# ---------------------------------------------------------------------------
# CAISO ancillary service prices
# ---------------------------------------------------------------------------

def caiso_without(raw, region, anc_type, hour_gmt):
    """The same OASIS answer with one (region, service, hour) row taken out."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    name = z.namelist()[0]
    lines = z.read(name).decode().splitlines(keepends=True)
    kept = [ln for ln in lines if not (ln.startswith(hour_gmt) and f",{anc_type},{region},DAM," in ln)]
    assert len(kept) == len(lines) - 1
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as o:
        o.writestr(name, "".join(kept))
    return out.getvalue()


class CaisoParsing(unittest.TestCase):
    def test_an_ordinary_day(self):
        day = pd.Timestamp("2024-09-01")
        rows = caiso.parse(fixture("caiso_prc_as_dam_20240901.zip"), day)
        self.assertEqual(set(rows["region"]), {"AS_CAISO", "AS_CAISO_EXP"})  # the sub-regions are not kept
        self.assertEqual(set(rows["type"]), {"RU", "RD", "SR", "NR"})  # the mileage prices are not kept
        self.assertEqual(len(rows), 2 * 4 * 24)
        first = rows[(rows["region"] == "AS_CAISO_EXP") & (rows["type"] == "RU")].sort_values("ts").iloc[0]
        self.assertEqual(ip.utc_iso(first["ts"]), "2024-09-01T07:00:00Z")  # midnight Pacific daylight time
        self.assertEqual(first["value"], 1.4583)
        kept, gaps = caiso.complete(rows, day, quiet)
        self.assertEqual((len(kept), gaps), (192, []))

    def test_the_25_hour_day(self):
        day = pd.Timestamp("2024-11-03")
        self.assertEqual(caiso.hours_in(day), 25)
        rows = caiso.parse(fixture("caiso_prc_as_dam_20241103.zip"), day)
        kept, gaps = caiso.complete(rows, day, quiet)
        self.assertEqual((len(kept), gaps), (200, []))
        self.assertIn("20241103T07:00-0000", caiso.url_for(day))
        self.assertIn("20241104T08:00-0000", caiso.url_for(day))

    def test_never_fill(self):
        day = pd.Timestamp("2024-09-01")
        raw = caiso_without(fixture("caiso_prc_as_dam_20240901.zip"), "AS_CAISO", "SR", "2024-09-01T10:00:00")
        kept, gaps = caiso.complete(caiso.parse(raw, day), day, quiet)
        self.assertEqual(gaps, ["AS_CAISO SR 2024-09-01: 23 of 24 hours"])
        self.assertEqual(len(kept), 192 - 24)  # the whole (region, service, day) is left out, nothing is filled
        self.assertTrue(kept[(kept["region"] == "AS_CAISO") & (kept["type"] == "SR")].empty)

    def test_an_error_document_is_not_data(self):
        def answer(text):
            out = io.BytesIO()
            with zipfile.ZipFile(out, "w") as o:
                o.writestr("INVALID_REQUEST.xml", text)
            return out.getvalue()
        with self.assertRaises(caiso.NoData):
            caiso.parse(answer("<m:ERR_DESC>No data returned for the specified selection</m:ERR_DESC>"), "2024-09-01")
        with self.assertRaises(caiso.Throttled):
            caiso.parse(answer("<m:ERR_DESC>Too many requests</m:ERR_DESC>"), "2024-09-01")
        with self.assertRaises(caiso.Throttled):
            caiso.parse(b"<html>429</html>", "2024-09-01")


class CaisoRun(Scratch):
    def run_day(self, raw=None):
        raw_store(self.raw, caiso.CONNECTOR,
                  {caiso.url_for(pd.Timestamp("2024-09-01")): raw or fixture("caiso_prc_as_dam_20240901.zip")})
        with mock.patch("builtins.print"):
            return caiso.main(["--offline", "--out-dir", self.out, "--start", "2024-09-01", "--until", "2024-09-02"])

    def test_table(self):
        self.assertEqual(self.run_day(), 0)
        t = read_table(os.path.join(self.out, "caiso_as_prices.csv"))
        self.assertEqual(len(t), 192)
        self.assertEqual(set(t["unit"]), {"USD/MW-hour"})
        self.assertEqual(set(t["entity"]), {"caiso:AS_CAISO", "caiso:AS_CAISO_EXP"})
        self.assertEqual(set(t["variable"]), {"as_price_dam_ru", "as_price_dam_rd", "as_price_dam_sr", "as_price_dam_nr"})
        self.assertEqual(self.status("caiso_as_prices")[0]["status"], "ok")

    def test_a_day_saved_under_the_address_oasis_answers_at_is_not_asked_for_again(self):
        day = pd.Timestamp("2024-09-01")
        self.assertIn("GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20240901T07:00-0000", caiso.answered_url_for(day))
        raw_store(self.raw, caiso.CONNECTOR, {caiso.answered_url_for(day): fixture("caiso_prc_as_dam_20240901.zip")})
        with mock.patch("builtins.print"), \
                mock.patch.object(ip.requests, "get", side_effect=AssertionError("a request was made")):
            code = caiso.main(["--out-dir", self.out, "--start", "2024-09-01", "--until", "2024-09-02"])  # not offline
        self.assertEqual(code, 0)
        self.assertEqual(len(read_table(os.path.join(self.out, "caiso_as_prices.csv"))), 192)

    def test_past_the_ceiling_keeps_the_expanded_region_only(self):
        with mock.patch.object(caiso, "CEILING", 100):
            self.assertEqual(self.run_day(), 0)
        t = read_table(os.path.join(self.out, "caiso_as_prices.csv"))
        self.assertEqual((len(t), set(t["entity"])), (96, {"caiso:AS_CAISO_EXP"}))

    def test_still_past_the_ceiling_writes_nothing(self):
        with mock.patch.object(caiso, "CEILING", 50), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(self.run_day(), 1)
        self.assertFalse(os.path.exists(os.path.join(self.out, "caiso_as_prices.csv")))
        self.assertEqual(self.status("caiso_as_prices")[0]["status"], "failed")

    def test_a_missing_hour_is_a_gap_row_in_the_status(self):
        raw = caiso_without(fixture("caiso_prc_as_dam_20240901.zip"), "AS_CAISO_EXP", "RU", "2024-09-01T07:00:00")
        self.assertEqual(self.run_day(raw), 0)
        t = read_table(os.path.join(self.out, "caiso_as_prices.csv"))
        self.assertEqual(len(t), 168)
        self.assertTrue(t[(t["entity"] == "caiso:AS_CAISO_EXP") & (t["variable"] == "as_price_dam_ru")].empty)
        gaps = [r for r in self.status("caiso_as_prices") if r["status"] == "gap"]
        self.assertEqual([g["detail"] for g in gaps], ["AS_CAISO_EXP RU 2024-09-01: 23 of 24 hours"])

    def test_offline_never_asks_the_source(self):
        with mock.patch("builtins.print"), mock.patch("sys.stderr", io.StringIO()), \
                mock.patch.object(ip.requests, "get", side_effect=AssertionError("a request was made")):
            code = caiso.main(["--offline", "--out-dir", self.out, "--start", "2024-09-01", "--until", "2024-09-02"])
        self.assertEqual(code, 1)  # the day is not in the raw files: the run fails, it does not go and get it


# ---------------------------------------------------------------------------
# ERCOT ancillary service prices
# ---------------------------------------------------------------------------

class ErcotParsing(unittest.TestCase):
    def test_the_yearly_file(self):
        rows = ercot.parse_year(fixture("ercot_np4_181_er_2018_first_two_days.zip"))
        self.assertEqual(rows.groupby("service").size().to_dict(), {"NSPIN": 48, "REGDN": 48, "REGUP": 48, "RRS": 48})
        first = rows[rows["service"] == "REGUP"].sort_values("ts").iloc[0]
        self.assertEqual(ip.utc_iso(first["ts"]), "2018-01-01T06:00:00Z")  # hour ending 01:00 Central, as its start
        self.assertEqual(first["value"], 2.51)
        self.assertNotIn("ECRS", set(rows["service"]))  # not bought before June 2023: no row, not a zero

    def test_the_daily_document(self):
        rows = ercot.parse_day(fixture("ercot_np4_188_cd_20260927.zip"))
        self.assertEqual(rows.groupby("service").size().to_dict(),
                         {"ECRS": 24, "NSPIN": 24, "REGDN": 24, "REGUP": 24, "RRS": 24})
        first = rows[rows["service"] == "ECRS"].sort_values("ts").iloc[0]
        self.assertEqual((ip.utc_iso(first["ts"]), first["value"]), ("2026-09-27T05:00:00Z", 0.28))
        s = ercot.to_series(rows.assign(source="ercot:NP4-188-CD", source_url="u", retrieved_at="r", vintage=""))
        self.assertEqual((set(s["unit"]), set(s["variable"]), set(s["freq"])), ({"USD/MW-hour"}, {"mcpc_dam"}, {"PT1H"}))

    def test_never_fill(self):
        rows = ercot.parse_year(fixture("ercot_np4_181_er_2018_first_two_days.zip"))
        cut = rows.drop(rows[(rows["service"] == "RRS") & (rows["day"] == "01/02/2018")].index[:1])
        kept, gaps = ercot.complete_days(cut, quiet)
        self.assertEqual(gaps, ["RRS 2018-01-02: 23 of 24 hours"])
        self.assertEqual(len(kept), 192 - 24)

    def test_an_empty_cell_is_no_row(self):
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as o:
            o.writestr("x.csv", "Delivery Date,Hour Ending,Repeated Hour Flag,REGDN,REGUP ,RRS,NSPIN,ECRS\n"
                                "06/09/2023,01:00,N,1,2,3,4,\n06/10/2023,01:00,N,1,2,3,4,5\n")
        rows = ercot.parse_year(out.getvalue())
        self.assertEqual(len(rows[rows["service"] == "ECRS"]), 1)

    def test_clock_changes(self):
        self.assertEqual([ercot.hours_in(d) for d in ("03/08/2026", "11/01/2026", "07/04/2026")], [23, 25, 24])
        ts = ercot.to_utc(pd.Series(["11/01/2026", "11/01/2026"]), pd.Series(["02:00", "02:00"]), pd.Series(["N", "Y"]))
        self.assertEqual([ip.utc_iso(t) for t in ts], ["2026-11-01T06:00:00Z", "2026-11-01T07:00:00Z"])

    def test_the_ceiling(self):
        self.assertEqual((ercot.CEILING, caiso.CEILING, cap.CEILING), (500_000, 500_000, 5_000))
        rows = ercot.parse_year(fixture("ercot_np4_181_er_2018_first_two_days.zip"))
        tmp = tempfile.mkdtemp(prefix="erw65_")
        saved = {k: getattr(ip, k) for k in ("OUT_DIR", "LOG_DIR", "RAW_DIR", "METADATA_DIR", "STATUS_DIR")}
        try:
            ip.RAW_DIR = os.path.join(tmp, "rawdocs")
            with mock.patch.object(ercot, "pull", return_value=rows), mock.patch.object(ercot, "CEILING", 100), \
                    mock.patch("builtins.print"), mock.patch("sys.stderr", io.StringIO()):
                self.assertEqual(ercot.main(["--offline", "--out-dir", os.path.join(tmp, "out")]), 1)
            self.assertFalse(os.path.exists(os.path.join(tmp, "out", "ercot_as_prices.csv")))
        finally:
            for k, v in saved.items():
                setattr(ip, k, v)
            ip.RAW.dir = None
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Capacity prices
# ---------------------------------------------------------------------------

NYISO_PAGE = """<html><body>
<td>05/2030&nbsp;Spot Market Auction Results - UCAP</td>
<td>Posted Date:&nbsp;04/26/2030 3:00 PM</td>
<table><tr><td colspan="2" class="inputLabel left noBorder">NYCA</td></tr>
<tr><td>Price ($/kW-M)</td><td class="right">$1.11</td></tr></table>
<table><tr><td colspan="2" class="inputLabel left noBorder">G-J Locality</td></tr>
<tr><td>Price ($/kW-M)</td><td class="right">$2.22</td></tr></table>
<table><tr><td colspan="2" class="inputLabel left noBorder">NYC</td></tr>
<tr><td>Price ($/kW-M)</td><td class="right">$1,003.33</td></tr></table>
<table><tr><td colspan="2" class="inputLabel left noBorder">LI</td></tr>
<tr><td>Price ($/kW-M)</td><td class="right">$4.44</td></tr></table>
<table><tr><td colspan="2" class="inputLabel left noBorder">PJM</td></tr>
<tr><td>Price ($/kW-M)</td><td class="right">$9.99</td></tr></table>
</body></html>"""


class CapacityGrammar(unittest.TestCase):
    """Made-up markup and numbers: the parsers' rules, not the publishers' data."""

    def test_nyiso_page(self):
        prices, posted = cap.parse_nyiso(NYISO_PAGE, 2030, 5)
        self.assertEqual(prices, {"NYCA": 1.11, "G-J Locality": 2.22, "NYC": 1003.33, "LI": 4.44})  # PJM is external
        self.assertEqual(posted, "2030-04-26T19:00:00Z")
        self.assertIsNone(cap.parse_nyiso(NYISO_PAGE, 2030, 6))  # another month's page is no auction, not a price
        with self.assertRaises(RuntimeError):  # a locality without its price fails; it is not filled
            cap.parse_nyiso(NYISO_PAGE.replace("$4.44", "n/a"), 2030, 5)
        with self.assertRaises(RuntimeError):
            cap.parse_nyiso(NYISO_PAGE.replace(">PJM<", ">Zone K<"), 2030, 5)

    def test_nyiso_capability_periods(self):
        self.assertEqual(cap.nyiso_season_of(2025, 5), ("Summer", 2025))
        self.assertEqual(cap.nyiso_season_of(2025, 10), ("Summer", 2025))
        self.assertEqual(cap.nyiso_season_of(2025, 11), ("Winter", 2025))
        self.assertEqual(cap.nyiso_season_of(2026, 4), ("Winter", 2025))
        ids = cap.nyiso_season_ids(json.dumps({"rows": [{"id": 1, "description": "Summer 2025"},
                                                        {"id": 2, "description": "Winter 2025-2026"}]}))
        self.assertEqual(ids, {("Summer", 2025): 1, ("Winter", 2025): 2})

    def test_isone_price_cell(self):
        self.assertEqual(cap.parse_isone_cell("$1.234"), [("System-wide", "capacity_price", 1.234, "")])
        self.assertEqual(cap.parse_isone_cell("$1.234 (floor price)"),
                         [("System-wide", "capacity_price", 1.234, "floor price")])
        self.assertEqual(cap.parse_isone_cell("ROP: $1.111 NNE: $2.222"),
                         [("ROP", "capacity_price", 1.111, ""), ("NNE", "capacity_price", 2.222, "")])
        self.assertEqual(cap.parse_isone_cell("$9.000/new & $5.000/existing"),
                         [("System-wide", "capacity_price_new", 9.0, ""),
                          ("System-wide", "capacity_price_existing", 5.0, "")])
        with self.assertRaises(RuntimeError):  # a cell the grammar does not know fails; no price is guessed
            cap.parse_isone_cell("to be determined")
        with self.assertRaises(RuntimeError):
            cap.parse_isone_cell("$1.234 except Maine")

    def test_miso_labels(self):
        self.assertEqual(cap.MONEY.match("$424.30").group(1), "424.30")  # the 2026 posting prints the dollar sign
        self.assertEqual(cap.MONEY.match("30.00").group(1), "30.00")
        self.assertIsNone(cap.MONEY.match("$405.31-"))  # the external zones' range is not one price
        self.assertIsNone(cap.MONEY.match("19,568.4"))
        self.assertEqual(cap.ZONE_LABEL.match("ERZ" + chr(0x2020)).group(1), "ERZ")  # a footnote mark on the label
        self.assertEqual(cap.ZONE_LABEL.match("Z10").group(1), "Z10")
        self.assertIsNone(cap.ZONE_LABEL.match("ERZ:"[:3] + "s"))
        self.assertIsNone(cap.ZONE_LABEL.match("Z11"))

    def test_a_dead_miso_link_is_a_failure_not_a_fill(self):
        self.assertTrue(all(u.startswith("https://cdn.misoenergy.org/") for u in cap.MISO_POSTINGS.values()))
        self.assertIn("20260522", cap.MISO_POSTINGS[2026])  # the corrected posting; the first link answers 403


class CapacityOnThisMachine(unittest.TestCase):
    """The parsers on the publishers' own documents, where warehouse/raw holds them (not in git)."""

    def need(self, part):
        raw = raw_doc(cap.CONNECTOR, part)
        if raw is None:
            self.skipTest(f"warehouse/raw/{cap.CONNECTOR}/ holds no document for {part}")
        return raw

    def test_nyiso_january_2018(self):
        prices, posted = cap.parse_nyiso(self.need("month=01%2F2018"), 2018, 1)
        self.assertEqual(prices, {"NYCA": 0.44, "G-J Locality": 3.19, "NYC": 3.19, "LI": 0.70})
        self.assertEqual(posted, "2017-12-28T15:00:00Z")

    def test_isone_auctions(self):
        rows = cap.parse_isone(self.need("key-stats/markets"))
        by = {(r[0], r[3], r[4]): r for r in rows}
        self.assertEqual(by[(16, "SENE", "capacity_price")][5], 2.639)
        self.assertEqual(by[(16, "SENE", "capacity_price")][2], 2025)  # FCA 16 is for June 2025 to May 2026
        self.assertEqual(by[(8, "System-wide", "capacity_price_new")][5], 15.0)
        self.assertEqual(by[(7, "System-wide", "capacity_price")][6], "floor price")
        self.assertNotIn((16, "System-wide", "capacity_price"), by)  # zones printed apart: no system price is made up

    def test_miso_2026_27(self):
        cells = cap.parse_miso(self.need("2026%20PRA%20Results%20Posting%2020260522"), 2026)
        summer = {c[3]: c[4] for c in cells if c[0] == "Summer 2026"}
        self.assertEqual((summer["Z1"], summer["Z8"], summer["Z9"], summer["Z10"]), (424.30, 384.10, 412.10, 384.10))
        self.assertNotIn("ERZ", summer)  # printed as a range: no row
        self.assertEqual({(c[1], c[2]) for c in cells if c[0] == "Winter 2026/27"}, {("2026-12-01", "2027-02-28")})
        self.assertEqual(len(cells), 43)

    def test_miso_2024_25(self):
        cells = cap.parse_miso(self.need("2024%20PRA%20Results%20Posting"), 2024)
        self.assertEqual({c[3]: c[4] for c in cells if c[0] == "Fall 2024"}["Z5"], 719.81)
        self.assertEqual(len(cells), 44)


class CapacityRun(Scratch):
    def test_the_ceiling_and_a_failed_market(self):
        row = dict(entity="nyiso:NYCA", variable="capacity_price", value=1.0, unit="USD/kW-month", freq="P1M",
                   geo="US-NY", market="nyiso_icap_spot", node="NYCA", source="nyiso:icap-spot-auction",
                   source_url="u", retrieved_at="2026-10-02T00:00:00Z", vintage="", x_auction="Spot", x_period_end="",
                   x_note="UCAP", x_license="public")
        months = pd.period_range("2000-01", periods=12, freq="M")
        rows = [dict(row, ts_utc=f"{p.year}-{p.month:02d}-01T00:00:00Z") for p in months]

        def boom(log, offline):
            raise RuntimeError("HTTP 403")
        pulls = {"nyiso": lambda log, offline: (rows, ["nyiso 2000-13: the page shows no spot auction"]), "miso": boom}
        with mock.patch.object(cap, "PULLS", pulls), mock.patch("builtins.print"), \
                mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(cap.main(["--offline", "--out-dir", self.out]), 1)  # one market failed: said so
        t = read_table(os.path.join(self.out, "iso_all_capacity_prices.csv"))
        self.assertEqual((len(t), set(t["market"])), (12, {"nyiso_icap_spot"}))  # the failed market has no row
        by = {(r["market"], r["status"]) for r in self.status("iso_capacity_prices")}
        self.assertEqual(by, {("nyiso", "ok"), ("nyiso", "gap"), ("miso", "failed")})
        shutil.rmtree(self.out)
        with mock.patch.object(cap, "PULLS", pulls), mock.patch.object(cap, "CEILING", 11), \
                mock.patch("builtins.print"), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(cap.main(["--offline", "--only", "nyiso", "--out-dir", self.out]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.out, "iso_all_capacity_prices.csv")))


# ---------------------------------------------------------------------------
# The raw-file cache: nothing is pulled twice
# ---------------------------------------------------------------------------

class RawCache(Scratch):
    def test_a_saved_document_is_reused_and_a_403_is_not(self):
        raw_store(self.raw, "x", {"https://example.org/a": b"saved"})
        with mock.patch.object(ip.requests, "get", side_effect=AssertionError("a request was made")):
            body, rec = ip.fetch_raw("x", "https://example.org/a", quiet)
        self.assertEqual((body, rec["cached"], rec["retrieved_at"]), (b"saved", True, "2026-10-02T15:00:00Z"))
        with self.assertRaises(RuntimeError):
            ip.fetch_raw("x", "https://example.org/b", quiet, offline=True)
        man = os.path.join(self.raw, "x", "20000101T000000Z", "manifest.csv")
        with open(man, encoding="utf-8") as f:
            text = f.read()
        with open(man, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace('"200"', '"403"'))
        self.assertIsNone(ip.raw_cached("x", "https://example.org/a"))  # an error answer is never a cached document

    def test_a_redirected_answer_is_found_by_the_address_asked_for(self):
        ip.RAW.open("x", "20000102T000000Z")
        ip.RAW.by_hash.clear()
        ip.RAW.record("https://example.org/answered", 200, b"body", {})
        self.assertIsNone(ip.raw_cached("x", "https://example.org/asked"))  # what session 65 found: pulled twice
        ip.RAW.alias("https://example.org/asked", b"body", {})
        self.assertEqual(ip.raw_cached("x", "https://example.org/asked")[0], b"body")
        self.assertEqual(ip.raw_cached("x", "https://example.org/answered")[0], b"body")

    def test_a_changed_file_is_not_trusted(self):
        raw_store(self.raw, "x", {"https://example.org/a": b"saved"})
        with open(os.path.join(self.raw, "x", "20000101T000000Z", "doc0"), "wb") as f:
            f.write(b"cut short")  # as a file being written when the machine restarted
        self.assertIsNone(ip.raw_cached("x", "https://example.org/a"))


# ---------------------------------------------------------------------------
# D1: gates are never piped; the loader refuses a stale coverage
# ---------------------------------------------------------------------------

class Gates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw65_")
        with open(os.path.join(self.tmp, "t_a_b.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# Energy Research Warehouse (ERW): a table\n# Retrieved: 20261002T101112Z (UTC) by x.py\n"
                    'entity,variable,ts_utc,value\na,v,2026-01-01T00:00:00Z,1\nb,v,2026-01-01T00:00:00Z,"2\n3"\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cov(self, n_rows, last_run):
        return pd.DataFrame([{"table": "t_a_b", "n_rows": n_rows, "last_run": last_run}])

    def test_the_loader_refuses_a_stale_coverage(self):
        import load
        self.assertEqual(load.coverage_stale(self.cov("2", "2026-10-02T10:11:12Z"), ["t_a_b"], self.tmp), [])
        stale = load.coverage_stale(self.cov("1", "2026-10-02T10:11:12Z"), ["t_a_b"], self.tmp)
        self.assertEqual(stale, [("t_a_b", "coverage says 1 rows, the file holds 2")])
        stale = load.coverage_stale(self.cov("2", "2026-10-01T00:00:00Z"), ["t_a_b"], self.tmp)
        self.assertIn("the file is from 2026-10-02T10:11:12Z", stale[0][1])
        stale = load.coverage_stale(self.cov("2", "2026-10-02T10:11:12Z").iloc[0:0], ["t_a_b"], self.tmp)
        self.assertEqual(stale, [("t_a_b", "not in coverage.csv")])

    def test_the_refusal_comes_before_any_write(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "load.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertLess(src.index("stale = coverage_stale("), src.index('print(f"live set:'))
        self.assertIn("nothing loaded", src)

    def test_the_rule_is_written_down(self):
        with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Gate commands are never piped", text)

    def test_no_gate_is_piped_in_the_daily_run(self):
        gates = ("erw_validate.py", "build_coverage.py", "supabase/load.py", "unittest", "npm run build")
        paths = [os.path.join(ROOT, "warehouse", "run_daily.sh")] + glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml"))
        piped = []
        for path in paths:
            with open(path, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    code = line.split("#", 1)[0]
                    if any(g in code for g in gates) and any(f"| {p}" in code for p in ("tail", "head", "grep", "tee")):
                        piped.append(f"{os.path.basename(path)}:{n}")
        self.assertEqual(piped, [])


# ---------------------------------------------------------------------------
# D2: the lock's holder is the session
# ---------------------------------------------------------------------------

class FakeLocks:
    """The erw_locks row as the Supabase functions keep it: one holder at a time."""

    def __init__(self):
        self.holder, self.token, self.n = None, None, 0

    def rpc(self, fn, **a):
        if fn == "erw_lock_acquire":
            if self.token:
                return None
            self.n += 1
            self.holder, self.token = a["p_holder"], f"tok-{self.n}"
            return self.token
        if fn == "erw_lock_check":
            return a["p_token"] == self.token
        if fn == "erw_lock_release":
            if a["p_token"] != self.token:
                return False
            self.holder = self.token = None
            return True
        raise AssertionError(fn)


class LockHolder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw65_")
        self.db = FakeLocks()
        self.patches = [
            mock.patch.object(lock, "STATE", self.tmp),
            mock.patch.object(lock, "LOCKFILE", os.path.join(self.tmp, "lock.json")),
            mock.patch.object(lock, "machine", return_value={"name": "laptop", "role": "data"}),
            mock.patch.object(lock, "rpc", side_effect=self.db.rpc),
            mock.patch.object(lock, "status", return_value={"holder": "laptop/sessionA", "task": "x", "expires": "later"}),
            mock.patch.object(lock, "_checked", {}),
            mock.patch.object(sys, "argv", ["connector.py"]),
        ]
        for p in self.patches:
            p.start()
        self.path = os.path.join(ROOT, "warehouse", "output", "x_y_z.csv")

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, session):
        return mock.patch.dict(os.environ, {"ERW_SESSION": session, "ERW_LOCK_EXEMPT": "", "ERW_LOCK_TOKEN": "",
                                            "GITHUB_ACTIONS": ""})

    def test_two_sessions_on_one_machine_cannot_both_hold_it(self):
        with self.env("sessionA-1111"):
            lock.acquire("backfill")
            self.assertEqual(self.db.holder, "laptop/sessionA")
            os.environ["ERW_LOCK_TOKEN"] = ""  # another process of the same session: it reads the session's file
            lock.require(self.path, "writing x")  # passes
        with self.env("sessionB-2222"):
            self.assertFalse(lock.token())  # before session 65 this was session A's token
            with self.assertRaises(SystemExit) as c:
                lock.require(self.path, "writing x")
            self.assertIn("laptop/sessionB", str(c.exception))
            with self.assertRaises(SystemExit):
                lock.acquire("another task")  # held by the first session
            self.assertFalse(lock.release())  # and B cannot give up A's lock
            self.assertEqual(self.db.holder, "laptop/sessionA")
        with self.env("sessionA-1111"):
            os.environ["ERW_LOCK_TOKEN"] = ""
            self.assertTrue(lock.release())
        with self.env("sessionB-2222"):
            lock.acquire("another task")
            self.assertEqual(self.db.holder, "laptop/sessionB")

    def test_each_session_keeps_its_own_token_file(self):
        with self.env("sessionA-1111"):
            self.assertTrue(lock.lockfile().endswith("lock.sessionA-1111.json"))
        with mock.patch.dict(os.environ, {"ERW_SESSION": "", "CLAUDE_CODE_SESSION_ID": "", "GITHUB_RUN_ID": ""}):
            self.assertEqual((lock.session(), lock.holder()), ("", "laptop"))  # a plain terminal
            self.assertTrue(lock.lockfile().endswith("lock.json"))


# ---------------------------------------------------------------------------
# The standard, the registry and the docs know the new tables
# ---------------------------------------------------------------------------

class Registered(unittest.TestCase):
    def test_units(self):
        import erw_validate
        self.assertLessEqual({"USD/kW-month", "USD/MW-hour", "USD/MW-day"}, erw_validate.UNITS)

    def test_names(self):
        import erw_validate
        for name in (cap.NAME, ercot.NAME, caiso.NAME):
            self.assertRegex(name, erw_validate.NAME_RE)

    def test_coverage_builder_llms_and_methods(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
        import build_coverage as bc
        import re
        for name in (cap.NAME, ercot.NAME, caiso.NAME):
            self.assertTrue(any(re.search(p, name) for p, _ in bc.SECTOR_RULES), name)
        for path in ("package/llms.txt", "docs/methods/capacity_and_ancillary.md", "warehouse/metadata/sources.csv"):
            with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                text = f.read()
            for name in (cap.NAME, ercot.NAME, caiso.NAME):
                self.assertIn(name, text, f"{name} not in {path}")
            self.assertNotIn(chr(0x2014), text, path)  # no em dash

    def test_the_capacity_table_is_internal_and_not_live(self):
        import load
        self.assertIsNone(load.live_rule(cap.NAME))
        self.assertIsNone(load.live_rule(ercot.NAME))
        self.assertIsNone(load.live_rule(caiso.NAME))


if __name__ == "__main__":
    unittest.main()
