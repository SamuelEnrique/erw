"""Session 89, the closing ruling: every MISO pull is paused (docs/methods/miso_pause.md).

Energy Research Warehouse (ERW). MISO's terms forbid automated access, so no scheduled run and no connector may
request MISO's servers while warehouse/metadata/paused_sources.csv holds its row. These tests replace every way of
making a request with a failure and run each MISO path: none is reached. They also check that the other grids are
read as before, that the registry and the notes record the pause, and that nothing of MISO's was deleted.

    python -m unittest tests.test_session89_miso_pause -v
"""

import contextlib
import io
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/news"):
    sys.path.insert(0, os.path.join(ROOT, p))

import iso_as_common as common  # noqa: E402
import iso_capacity_prices as cap  # noqa: E402
import iso_prices as ip  # noqa: E402
import iso_queues  # noqa: E402
import latest_prices  # noqa: E402
import miso_as_prices  # noqa: E402

TERMS = "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class NoRequest(Exception):
    """A request was attempted."""


def refuse(*a, **k):
    raise NoRequest("a request was attempted")


@contextlib.contextmanager
def no_network(tmp):
    """Every way a connector reaches a server fails loudly, and every output goes under tmp."""
    keep = (ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)
    ip.set_out_dir(tmp)
    try:
        with mock.patch("requests.get", refuse), mock.patch("requests.Session.send", refuse), \
                mock.patch("urllib.request.urlopen", refuse), mock.patch("gridstatus.MISO", refuse), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            yield out
    finally:
        ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = keep


class ThePause(unittest.TestCase):
    def test_the_list_holds_miso_with_the_terms_quoted_and_who_ruled(self):
        r = ip.paused("miso")
        self.assertIsNotNone(r)
        self.assertEqual(r["paused_on"], "2026-10-04")
        self.assertIn(TERMS, r["terms_quoted"])
        self.assertTrue(r["terms_url"].startswith("https://www.misoenergy.org/"))
        self.assertIn("Samuel", r["ruled_by"])
        self.assertIn("review", r["until"])
        for other in ("ercot", "caiso", "nyiso", "spp", "isone", "pjm"):
            self.assertIsNone(ip.paused(other), other)
        self.assertIn("No request made", ip.pause_line("miso"))

    def test_the_daily_run_no_longer_lists_miso(self):
        sh = src("warehouse", "run_daily.sh")
        m = re.search(r'^ISOS="\$\{ISOS:-([a-z ]+)\}"', sh, re.M)
        self.assertEqual(m.group(1).split(), ["ercot", "caiso", "nyiso", "spp", "isone"])
        self.assertNotRegex(sh, r"(?m)^[^#\n]*miso_as_prices")                    # the reserve connector is in no run

    def test_the_daily_price_connector_refuses_miso_without_a_request(self):
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp) as out:
            self.assertEqual(ip.run("miso", 2), 0)
            self.assertIn("PAUSED since 2026-10-04", out.getvalue())
            self.assertFalse([f for f in os.listdir(tmp) if f.endswith(".csv")])    # nothing written
            status = pd.read_json(os.path.join(tmp, "status", "miso.json"), typ="series")
            self.assertEqual(status["results"][0]["status"], "skipped")

    def test_the_fifteen_minute_run_skips_miso_and_reads_the_others(self):
        asked = []

        def fake(iso):
            def fn():
                asked.append(iso)
                raise RuntimeError("stand-in: no data in a test")
            return (fn, "LMP", [], "v", f"{iso}:x")
        fetchers = {iso: fake(iso) for iso in ("ercot", "caiso", "miso", "spp")}
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp), mock.patch.object(latest_prices, "fetchers", lambda: fetchers):
            latest_prices.main(["--no-upsert"])
        self.assertEqual(asked, ["ercot", "caiso", "spp"])                         # MISO's reader was never called
        self.assertIn("miso", latest_prices.fetchers())                            # the reader is still there: nothing deleted

    def test_the_queue_connector_skips_miso(self):
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp) as out:
            iso_queues.main(["miso", "--out-dir", tmp])
            self.assertIn("PAUSED since 2026-10-04", out.getvalue())
            self.assertFalse(os.path.exists(os.path.join(tmp, "miso_interconnection_queue.csv")))

    def test_the_capacity_connector_skips_miso_and_fails_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp) as out:
            self.assertEqual(cap.main(["--only", "miso", "--out-dir", tmp]), 0)
            self.assertIn("PAUSED since 2026-10-04", out.getvalue())
            self.assertFalse(os.path.exists(os.path.join(tmp, cap.NAME + ".csv")))
        self.assertIn("miso", cap.PULLS)

    def test_the_reserve_connector_refuses_to_run(self):
        called = []
        spec = dict(miso_as_prices.SPEC, documents=lambda *a: called.append("documents") or [])
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp) as out:
            self.assertEqual(common.run(spec, ["--out-dir", tmp]), 0)
            self.assertIn("PAUSED since 2026-10-04", out.getvalue())
            self.assertFalse(os.path.exists(os.path.join(tmp, "miso_as_prices.csv")))
        self.assertEqual(called, [])                                               # it never listed a document to fetch

    def test_another_grids_connector_is_not_paused(self):
        import spp_as_prices
        called = []

        def documents(*a):
            called.append("documents")
            return []
        with tempfile.TemporaryDirectory() as tmp, no_network(tmp):
            common.run(dict(spp_as_prices.SPEC, documents=documents), ["--out-dir", tmp, "--start", "2026-10-01", "--until", "2026-10-02"])
        self.assertEqual(called, ["documents"])

    def test_no_feed_the_ingest_reads_searches_misos_site_and_a_miso_story_is_not_opened(self):
        with open(os.path.join(ROOT, "warehouse", "news", "feeds.yaml"), encoding="utf-8") as f:
            y = yaml.safe_load(f)
        self.assertFalse([x["name"] for x in y["feeds"] if "misoenergy" in x["url"].lower() or "miso" in x["name"].lower()])
        self.assertEqual([x["name"] for x in y["paused_feeds"]], ["MISO newsroom"])   # kept, not deleted
        import ingest
        df = pd.DataFrame({"google_news_url": ["", ""], "url_resolved": ["", ""], "source": ["cdn.misoenergy.org", "MISO Help Center"],
                           "source_url": ["https://news.google.com/rss/articles/a", "https://news.google.com/rss/articles/b"]})
        with mock.patch.object(ingest, "resolve_google", refuse):
            out, tried, ok = ingest.resolve_rows(df, lambda m: None)
        self.assertEqual((tried, ok), (0, 0))
        self.assertEqual(list(out["url_resolved"]), ["no: the outlet's pulls are paused"] * 2)
        self.assertEqual(list(out["source_url"]), list(df["source_url"]))           # the Google News link is kept as it was


class TheRecord(unittest.TestCase):
    def test_the_registrys_miso_rows_say_paused_and_no_other_row_does(self):
        reg = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        is_miso = reg["source"].str.contains(r"(?i)^miso:|misoenergy\.org|Midcontinent Independent System Operator|^MISO Help Center$") \
            | reg["publisher"].str.contains(r"(?i)misoenergy\.org|Midcontinent Independent System Operator|^MISO Help Center$")
        marked = reg["report"].str.contains(r"\[PAUSED 2026-10-04: MISO's terms forbid automated access", regex=True)
        self.assertGreaterEqual(int(is_miso.sum()), 6)
        self.assertTrue((marked == is_miso).all(), reg.loc[marked != is_miso, "source"].tolist())
        self.assertTrue(reg.loc[is_miso, "tables"].str.len().gt(0).all())           # no table was taken off a MISO row
        for s in ("miso:da_expost_lmp", "miso:rt_lmp_final", "miso:interconnection_queue", "miso:pra-results-posting", "miso:asm_expost_damcp"):
            self.assertIn(s, set(reg["source"]), s)                                 # no row was deleted

    def test_whoever_writes_the_registry_keeps_the_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            keep = ip.METADATA_DIR
            ip.METADATA_DIR = tmp
            try:
                entry = dict(source="miso:da_expost_lmp", publisher="Midcontinent Independent System Operator (MISO)",
                             report="Day-Ahead Ex-Post LMP (daily csv)", report_url="u", document_list="", tables=["t"])
                other = dict(source="spp:DA-MCP", publisher="Southwest Power Pool (SPP)", report="Day-Ahead MCP", report_url="u", document_list="", tables=["t"])
                ip.update_sources([entry, other])
                ip.update_sources([entry])                                          # a second write does not add it twice
                reg = pd.read_csv(os.path.join(tmp, "sources.csv"), dtype=str, keep_default_na=False).set_index("source")
            finally:
                ip.METADATA_DIR = keep
        self.assertEqual(reg.at["miso:da_expost_lmp", "report"].count("[PAUSED "), 1)
        self.assertNotIn("PAUSED", reg.at["spp:DA-MCP", "report"])

    def test_the_method_notes_and_the_instructions_record_it(self):
        note = src("docs", "methods", "miso_pause.md")
        self.assertIn(TERMS, note)
        for word in ("Nothing is deleted", "paused_sources.csv", "To lift the pause", "Not paused"):
            self.assertIn(word, note)
        for rel in ("docs/methods/capacity_and_ancillary.md", "docs/methods/price_board.md", "docs/methods/cost_of_power.md",
                    "docs/methods/trader_view.md", "docs/methods/energy_projects.md", "docs/price-sources.md"):
            self.assertIn("MISO is paused (4 October 2026)", src(*rel.split("/")), rel)
        self.assertIn("paused_sources.csv", src("CLAUDE.md"))
        self.assertIn("PAUSED (Samuel's ruling of 4 October 2026", src("warehouse", "connectors", "miso_as_prices.py"))

    def test_nothing_of_misos_was_deleted(self):
        for rel in ("warehouse/connectors/miso_as_prices.py",):
            self.assertTrue(os.path.exists(os.path.join(ROOT, rel)), rel)
        self.assertIn('"miso"', src("warehouse", "connectors", "iso_queues.py"))
        self.assertIn("def pull_miso", src("warehouse", "connectors", "iso_prices.py"))
        self.assertIn("def pull_miso", src("warehouse", "connectors", "iso_capacity_prices.py"))
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        for t in ("miso_as_prices", "miso_interconnection_queue"):
            self.assertIn(t, set(cov["table"]), t)                                  # the tables are still in the catalogue's source
        for rel in ("site/app/cost-of-power/battery/page.tsx", "site/lib/batterystack.ts"):
            self.assertIn("MISO", src(*rel.split("/")), rel)                        # the pages still name MISO, as before

    def test_no_em_dash_in_what_the_ruling_wrote(self):
        for rel in ("docs/methods/miso_pause.md", "warehouse/metadata/paused_sources.csv", "tests/test_session89_miso_pause.py", "warehouse/run_daily.sh"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
