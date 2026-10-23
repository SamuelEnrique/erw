"""Session 1001 (chain 070): the Python package meets its specification (docs/methods/packages.md).

Every table of coverage.csv has its license verdict as docs/licenses.md gives it, and its citation in
warehouse/redivis/release_v1.py's words (the same publishers and reports, the same sentence). A table that is not
public is refused, with the license's words, by a backend that serves publicly, and warned when read from local
files. fetch takes entity, variable and backend; every frame carries its version line. No request, no model call: the
local backend reads the tables kept in git, and the backends that serve publicly are stood in for by a local one.
"""
import importlib
import os
import re
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "package" / "src"))
sys.path.insert(0, str(ROOT / "warehouse" / "redivis"))

import pandas as pd  # noqa: E402

import erw  # noqa: E402
from erw import api, licenses  # noqa: E402

OUTPUT = ROOT / "warehouse" / "output"


def md_verdicts():
    out, on = {}, False
    for ln in (ROOT / "docs" / "licenses.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            on = ln.strip() == "## Every table"
            continue
        m = re.match(r"^\| `([a-z0-9_]+)` \|", ln) if on else None
        if m:
            out[m.group(1)] = ln.strip().strip("|").split("|")[-1].strip()
    return out


class Base(unittest.TestCase):
    def setUp(self):
        self._w = warnings.catch_warnings()
        self._w.__enter__()
        warnings.simplefilter("ignore", erw.ERWLicenseWarning)   # energy_deals is held: each local read warns
        self.env = {k: os.environ.get(k) for k in ("ERW_DATA_DIR", "ERW_BACKEND")}
        os.environ["ERW_DATA_DIR"] = str(OUTPUT)
        os.environ.pop("ERW_BACKEND", None)
        erw.set_backend()

    def tearDown(self):
        self._w.__exit__(None, None, None)
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        erw.set_backend()


class Licenses(Base):
    def test_every_table_has_the_record_s_verdict_and_words(self):
        cov = pd.read_csv(ROOT / "warehouse" / "metadata" / "coverage.csv", dtype=str, keep_default_na=False)
        md = md_verdicts()
        self.assertEqual(licenses.read_from(), str(ROOT))
        for t in cov["table"]:
            lic = erw.license(t)
            self.assertIn(lic["verdict"], ("public", "internal", "unsettled"), t)
            if t in md:
                self.assertEqual(lic["verdict"], md[t], t)
            self.assertTrue(lic["words"].endswith("."), t)
        held = pd.read_csv(ROOT / "warehouse" / "metadata" / "license_status.csv", dtype=str, keep_default_na=False)
        for r in held.to_dict("records"):
            if r["table"] in set(cov["table"]):
                lic = erw.license(r["table"])
                self.assertEqual(lic["status"], "license needed")
                self.assertIn(f"license needed since {r['from']}", lic["words"])

    def test_the_shipped_copy_has_every_field(self):
        rows = licenses._csv(licenses.shipped_path())
        self.assertGreaterEqual(len(rows), 290)
        self.assertEqual(list(rows[0]), licenses.FIELDS)
        self.assertTrue(all(r["verdict"] in licenses.VERDICTS and r["words"] for r in rows))

    def test_tables_lists_every_table_with_its_verdict(self):
        t = erw.tables()
        cov = erw.coverage()
        self.assertEqual(sorted(t["table"]), sorted(cov["table"]))
        self.assertEqual(list(t.columns), ["table", "shape", "interval", "ts_min", "ts_max", "n_rows", "verdict",
                                           "in_live", "title"])
        self.assertTrue(set(t["shape"]) <= {"series", "entities", "events"})
        self.assertEqual(t.set_index("table").loc["energy_deals", "shape"], "events")
        self.assertTrue(t.set_index("table").loc["energy_deals", "title"])
        self.assertEqual(erw.coverage("energy_deals")["table"].tolist(), ["energy_deals"])
        with self.assertRaises(erw.ERWDataNotFound) as e:
            erw.coverage("energy_deal")
        self.assertIn("energy_deals", str(e.exception))


class Citation(Base):
    def test_every_table_is_cited_in_the_release_s_words(self):
        import release_v1 as R
        sources = R.rows(os.path.join(R.META, "sources.csv"))
        pubs = {r["table"]: r["publishers"] for r in R.rows(os.path.join(R.META, "license_tables.csv"))}
        cov = pd.read_csv(ROOT / "warehouse" / "metadata" / "coverage.csv", dtype=str, keep_default_na=False)
        via = " Via the Energy Research Warehouse (ERW), table "
        for t in cov["table"]:
            want = R.citation(t, sources, pubs.get(t, "")).split(via)[0]
            got = erw.cite(t)
            self.assertEqual(got.split(via)[0], want, t)
            self.assertIn(f"{via}`{t}`, ", got)
            self.assertNotIn("Provenance tier", got)

    def test_the_last_clause_says_where_the_rows_came_from(self):
        c = erw.cite("energy_deals")
        commit = erw.version()["data_commit"]
        if commit:
            self.assertTrue(c.endswith(f"ERW commit {commit[:12]}."), c)
        else:
            self.assertTrue(c.endswith("local files (no ERW commit identifies them)."), c)


class Fetch(Base):
    def test_entity_variable_and_the_version_line(self):
        df = erw.fetch("energy_deals")
        kind = df["event_type"].iloc[0]
        sub = erw.fetch("energy_deals", variable=kind)
        self.assertEqual(set(sub["event_type"]), {kind})
        self.assertEqual(len(sub), int((df["event_type"] == kind).sum()))
        outlet = df["source"].iloc[0]
        self.assertEqual(set(erw.fetch("energy_deals", entity=outlet)["source"]), {outlet})
        line = sub.attrs["erw"]["version_line"]
        self.assertRegex(line, r"^ERW energy_deals: local files; ERW commit ([0-9a-f]{12}|unknown); "
                               r"fetched \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ; \d+ rows$")
        self.assertEqual(sub.attrs["erw"]["license"]["table"], "energy_deals")
        self.assertEqual(erw.fetch("energy_deals", backend="local").shape, df.shape)
        with self.assertRaises(ValueError):
            erw.fetch("energy_deals", backend="nowhere")

    def test_a_table_not_public_is_refused_where_the_erw_serves_it(self):
        held = next(t for t in erw.list_tables() if erw.license(t)["verdict"] != "public")
        public = next((t for t in erw.list_tables() if erw.license(t)["verdict"] == "public"), None)

        class Served(erw.LocalBackend):
            name = "live"   # stands in for the live set: the ERW serving publicly, with no request

        erw.set_backend(Served(str(OUTPUT)))
        with self.assertRaises(erw.ERWLicenseHeld) as e:
            erw.fetch(held)
        msg = str(e.exception)
        self.assertTrue(msg.startswith(f"{held} is not public: {erw.license(held)['verdict']}. "), msg)
        self.assertIn(erw.license(held)["words"], msg)
        self.assertTrue(msg.endswith(licenses.LICENSES_URL))
        if public:
            self.assertGreaterEqual(len(erw.fetch(public)), 0)
        erw.set_backend(str(OUTPUT))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            erw.fetch(held)
        self.assertTrue(any(issubclass(x.category, erw.ERWLicenseWarning) for x in w))


class Standard(Base):
    def test_columns_types_and_key(self):
        s = erw.standard("energy_deals")
        self.assertEqual(s["shape"], "events")
        self.assertEqual(s["key"], ["event_id"])
        by = {c["name"]: c for c in s["columns"]}
        self.assertEqual(by["event_date"]["type"], "utc time")
        self.assertEqual(by["event_id"]["required"], "yes")
        self.assertEqual(api.column_type("series", "value"), "number")
        self.assertEqual(api.column_type("series", "ts_utc"), "utc time")
        self.assertEqual(api.column_type("entities", "status_date"), "date")
        self.assertEqual(api.column_type("entities", "capacity_mw"), "number")
        self.assertEqual(api.shape_of(["entity", "variable", "ts_utc", "value", "unit"]), "series")


class Routing(unittest.TestCase):
    def test_the_live_set_is_read_within_its_window(self):
        now = pd.Timestamp.now(tz="UTC")
        self.assertTrue(api._live_covers("whole", None))
        self.assertTrue(api._live_covers("35 days", now - pd.Timedelta(days=10)))
        self.assertFalse(api._live_covers("35 days", now - pd.Timedelta(days=31)))
        self.assertFalse(api._live_covers("35 days", None))
        self.assertFalse(api._live_covers("none", now))

    def test_the_live_filters(self):
        from erw.live import series_filters
        f = dict(series_filters(["HB_NORTH"], "spp_rtm", "2026-10-01", "2026-10-02"))
        self.assertEqual(f["node"], 'in.("HB_NORTH")')
        self.assertEqual(f["variable"], 'in.("spp_rtm")')
        self.assertEqual(f["ts_utc"], "lt.2026-10-02T00:00:00Z")
        self.assertEqual(dict(series_filters(["ercot:HB_NORTH"]))["entity"], 'in.("ercot:HB_NORTH")')
        self.assertNotIn("entity", dict(series_filters(["ercot:HB_NORTH", "HB_WEST"])))

    def test_requests_are_counted(self):
        from erw import counter
        before = erw.requests()["live"]
        counter.add("live")
        self.assertEqual(erw.requests()["live"], before + 1)


class Specification(unittest.TestCase):
    def test_the_six_calls_are_the_package_s(self):
        for call in ("tables", "coverage", "fetch", "cite", "license", "standard"):
            self.assertIn(call, erw.__all__)
            self.assertTrue(callable(getattr(erw, call)))


if __name__ == "__main__":
    unittest.main()
