"""Session 410: the /data catalogue against warehouse/metadata/coverage.csv and sources.csv.

What /data lists, and where the list comes from. site/app/data/page.tsx reads the live catalogue (lib/data.ts,
catalogue()), which warehouse/supabase/load.py writes from coverage.csv (live_set.yaml, "catalogue") less the tables
under catalogue_hold, with in_live_set "yes", "no" or "review" (live_flag); the site keeps the rows whose license is
public and whose in_live_set is not "review". So the page's source of tables is coverage.csv, read through those two
rules, and this test reads it the same way, statically: no running site, no database.

It fails when the page and the two registries disagree:
- the page stops showing a table's license, refresh (last run), row count, newest timestamp, download or Redivis link,
  or shows a held table (lib/license.ts) as downloadable;
- a table the page lists has a coverage field missing or malformed, or no source in sources.csv names it (directly, or
  a table table_migrations.csv records as migrated into it), or a source of its source report is not in sources.csv;
- a public table is named by an internal source without its own "License: public" header (the four that declare it are
  named below, with the reason);
- sources.csv names a table that coverage.csv does not hold and that is neither retired nor migrated;
- the site's copy of the license holds (site/data/license_status.json) differs from license_status.csv;
- a listed table has no Redivis draft in the public dataset.
"""

import csv
import datetime as dt
import importlib.util
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
META = os.path.join(ROOT, "warehouse", "metadata")
OUT = os.path.join(ROOT, "warehouse", "output")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rows(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def loader():
    spec = importlib.util.spec_from_file_location("erw_supabase_load_s410", os.path.join(ROOT, "warehouse", "supabase", "load.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LOAD = loader()
COV = {r["table"]: r for r in rows("warehouse", "metadata", "coverage.csv")}
SOURCES = {r["source"]: r for r in rows("warehouse", "metadata", "sources.csv")}
RETIRED = {r["table"] for r in rows("warehouse", "metadata", "retired_tables.csv")}
MIGRATED = rows("warehouse", "metadata", "table_migrations.csv")

# The tables the registry names, by table: the sources whose `tables` field lists it.
NAMED = {}
for _s in SOURCES.values():
    for _t in re.split(r"[;,]\s*", _s["tables"]):
        if _t.strip():
            NAMED.setdefault(_t.strip(), []).append(_s)

# A public table that internal sources name, and why the ERW holds it public: its own header declares "License: public"
# (build_coverage.py, declared_license), which the header's line gives. Read in session 410 from warehouse/output.
DECLARED_PUBLIC = {
    "news_index": "links, metadata and the model's own fields; no outlet text (the outlets are internal sources)",
    "energy_deals": "the model's structured fields and the story links only, no outlet text",
    "datacenter_projects": "the model's checked fields and the story links only, no outlet text",
    "nyiso_load_queue": "public, with a caution (sessions 65, 85, 136, 138); the registry row says internal",
}

# A name the registry carries that no table of coverage.csv, retired_tables.csv or table_migrations.csv accounts for.
# The registry only grows (merge_sources.py, decision 13): a name is never removed. Session 410 found one.
REGISTRY_ONLY = {
    "curtailment_monthly": "erw:curtailment_monthly, first and last seen 2026-09-27: session 18's name for the table "
                           "that reached coverage as iso_curtailment_monthly (source erw:iso_curtailment_monthly)",
}


def page_tables():
    """The tables /data lists, read from coverage.csv as load.py and lib/data.ts read it."""
    held = set(LOAD.LIVE.get("catalogue_hold") or [])
    live = {t for t in COV if LOAD.live_rule(t)}  # statically, as if every table were on the machine
    out = []
    for t, r in sorted(COV.items()):
        if t in held:
            continue
        if r["license"] == "public" and LOAD.live_flag(t, live) != "review":
            out.append(t)
    return out


def iso(ts):
    return dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


class TheSourceOfThePage(unittest.TestCase):
    def test_the_page_reads_the_catalogue_the_loader_writes_from_coverage(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn("await attempt(catalogue)", page)
        self.assertIn('import { catalogue } from "@/lib/data"', page)
        data = src("site", "lib", "data.ts")
        self.assertIn('r.license === "public" && r.in_live_set !== "review"', data)
        self.assertEqual(LOAD.LIVE["catalogue"], "warehouse/metadata/coverage.csv")
        self.assertEqual(LOAD.LIVE["sources"], "warehouse/metadata/sources.csv")
        load = src("warehouse", "supabase", "load.py")
        self.assertIn("cov, plan, held = hold(cov, plan)", load)
        self.assertIn('row["in_live_set"] = live_flag(r["table"], live_names)', load)

    def test_the_page_shows_every_field(self):
        page = src("site", "app", "data", "page.tsx")
        for field in ("r.table_name", "r.license", "r.last_run", "r.n_rows", "r.ts_max", "r.source_report", "r.interval"):
            self.assertIn(field, page, field)
        for head in ("License", "Refreshed (UTC)", "Rows", "Last (UTC)", "Download", "Source report"):
            self.assertIn(f">{head}</th>", page, head)
        # the counts and times are the catalogue's: none written by hand in the table's cells
        self.assertIn("{count(r.n_rows)}", page)
        self.assertIn("{day(r.ts_max)}", page)
        self.assertIn("day(r.last_run)", page)

    def test_a_held_table_is_not_downloadable_and_the_rest_link_their_copy(self):
        page = src("site", "app", "data", "page.tsx")
        cell = page[page.index("Held: license needed") - 200:]
        held = cell.index("licenseNeeded(r.table_name)")
        self.assertLess(held, cell.index("Held: license needed"))
        self.assertLess(cell.index("Held: license needed"), cell.index("/api/download?table="))
        self.assertLess(cell.index("/api/download?table="), cell.index("site.redivis.url"))
        self.assertIn('r.in_live_set === "yes"', cell[:cell.index("/api/download?table=")])
        # the download route refuses a held table whatever the address (lib/license.ts)
        self.assertIn("if (licenseNeeded(table)) return text(", src("site", "app", "api", "download", "route.ts"))
        # no Redivis version is released yet (docs/redivis/release-v1.md): the link says so where the page has it
        self.assertIn("version 1 is pending release", page)


class CoverageAndTheRegistry(unittest.TestCase):
    def test_every_listed_table_has_its_coverage_fields(self):
        listed = page_tables()
        self.assertGreater(len(listed), 50)
        for t in listed:
            r = COV[t]
            with self.subTest(table=t):
                self.assertEqual(r["license"], "public")
                self.assertRegex(r["n_rows"], r"^\d+$")
                iso(r["ts_max"])
                iso(r["ts_min"])
                self.assertLessEqual(r["ts_min"], r["ts_max"])
                self.assertTrue(r["source_report"].strip())
                if r["last_run"]:
                    iso(r["last_run"])
                self.assertIn(r["tier"], ("source", "derived", "model_extracted"))

    def test_every_listed_table_is_named_by_the_registry(self):
        into = {}
        for m in MIGRATED:
            into.setdefault(m["new_table"], set()).add(m["old_table"])
        for t in page_tables():
            with self.subTest(table=t):
                ok = t in NAMED or any(o in NAMED for o in into.get(t, ()))
                self.assertTrue(ok, f"{t}: no source in sources.csv names it, nor a table migrated into it")
                for s in COV[t]["source_report"].split(";"):
                    if ":" in s:
                        self.assertIn(s, SOURCES, f"{t}: its source report names {s}, which sources.csv does not hold")

    def test_a_public_table_named_by_an_internal_source_declares_its_license(self):
        found = {}
        for t, r in COV.items():
            if r["license"] != "public":
                continue
            bad = [s["source"] for s in NAMED.get(t, []) if s["license"] != "public"]
            if bad:
                found[t] = bad
        self.assertEqual(sorted(found), sorted(DECLARED_PUBLIC), "a public table named by an internal source")
        for t in DECLARED_PUBLIC:
            p = os.path.join(OUT, t + ".csv")
            if not os.path.exists(p):
                continue  # the runner and a fresh clone hold no tables; the machine with the tables reads the header
            with open(p, encoding="utf-8", errors="replace") as f:
                head = [ln for ln in (next(f, "") for _ in range(40)) if ln.startswith("#")]
            self.assertTrue(any("License: public" in ln for ln in head), t)

    def test_every_table_the_registry_names_is_in_coverage_or_accounted_for(self):
        old = {m["old_table"] for m in MIGRATED}
        loose = sorted(t for t in NAMED if t not in COV and t not in RETIRED and t not in old)
        self.assertEqual(loose, sorted(REGISTRY_ONLY))
        for t in REGISTRY_ONLY:
            self.assertNotIn(t, COV)

    def test_session_410s_two_registry_lines(self):
        # datacenter_queue_positions's source report names the two operators' queue reports; their registry rows now
        # name it (session 410), as the other tables of those reports are named
        for s in ("ercot:interconnection_queue", "nyiso:interconnection_queue"):
            self.assertIn("datacenter_queue_positions", SOURCES[s]["tables"].split(";"), s)
            self.assertEqual(SOURCES[s]["license"], "public")
        self.assertEqual(COV["datacenter_queue_positions"]["source_report"], "ercot:interconnection_queue;nyiso:interconnection_queue")

    def test_no_retired_table_is_in_coverage(self):
        self.assertEqual(sorted(RETIRED & set(COV)), [])


class TheHoldsAndRedivis(unittest.TestCase):
    def test_the_site_holds_are_license_status_csv(self):
        site = json.loads(src("site", "data", "license_status.json"))["tables"]
        csvs = {r["table"]: r for r in rows("warehouse", "metadata", "license_status.csv")}
        self.assertEqual(sorted(site), sorted(csvs))
        for t, r in csvs.items():
            with self.subTest(table=t):
                self.assertIn(t, COV, f"{t}: a license status for a table coverage.csv does not hold")
                self.assertEqual(site[t]["status"], r["status"])
                self.assertEqual(site[t]["from"], r["from"])
                self.assertEqual(site[t]["publishers"], [p.strip() for p in r["publishers"].split(";") if p.strip()])

    def test_every_listed_table_has_a_draft_in_the_public_redivis_dataset(self):
        up = {r["table"]: r for r in rows("warehouse", "metadata", "redivis_uploads.csv")}
        for t in page_tables():
            with self.subTest(table=t):
                self.assertIn(t, up, f"{t}: no Redivis upload recorded")
                self.assertEqual(up[t]["dataset"], "energy_research_warehouse")

    def test_no_em_dash(self):
        for f in ("site/app/data/page.tsx", "tests/test_session410.py"):
            self.assertNotIn(chr(0x2014), src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
