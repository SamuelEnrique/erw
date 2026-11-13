"""Session 4109 (chain 229, the licensing sweep): no table reaches the public site while its verdict is not public.

Energy Research Warehouse (ERW). A table's verdict is the one word of docs/licenses.md, "Every table", as the package
ships it (package/src/erw/data/tables.csv: public, internal or unsettled). A table reaches a visitor by four routes:

    the live set      every row loaded with the license "public" is readable with the anon key (row-level security,
                      warehouse/supabase/migrations/002_rls.sql), whatever page reads it; the pages mask only a table
                      held "license needed" (site/lib/license.ts, warehouse/metadata/license_status.csv)
    downloads         /api/download refuses a held table and any table whose verdict is not public (site/lib/packages.ts)
    release v1        the tables Redivis's version 1 holds (docs/redivis/release-v1/tables.csv, in_v1 = yes)
    findings cards    the cards' figures are computed into static files (site/data/findings/<card>.json and the charts and
                      CSV files under site/public/findings/), which the site's proxy serves by address whatever the
                      review curtain says (site/proxy.ts's matcher skips any path with a file extension)

A table held "license needed" is shown as those words, so it does not count as reaching the site through the live set.
The findings cards built from a table that is not public when this test was written are named in CARDS_WAITING: each
waits for the owner's ruling (archive/sessions/SESSION_4109_REPORT.md), the list only shrinks, and no page that draws the
cards may open while one is named.
"""

import csv
import glob
import json
import os
import re
import sys
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses as L  # noqa: E402

# card: the tables of it that are not public, as found on 13 November 2026 (session 4109)
CARDS_WAITING = {
    "gas_sets_price": {"isone_zone_prices_history"},      # ISO-NE's prices, internal: ISO-NE asks for permission
    "siting_flexible": {"texas_transmission_matrix"},     # the PUCT's transmission charge matrices, internal
    "siting_gigawatt": {"texas_transmission_matrix"},
}
PAGES_DRAWING_CARDS = ("/", "/research")   # site/app/page.tsx and site/app/research (its cards' pages under /research/card)


def rows(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def verdicts():
    return {r["table"]: r["verdict"] for r in rows("package", "src", "erw", "data", "tables.csv")}


def held():
    return {r["table"] for r in rows("warehouse", "metadata", "license_status.csv") if r["status"] == "license needed" and not r["permission"]}


def flags():
    return {r["table"]: r["license"] for r in rows("warehouse", "metadata", "coverage.csv")}


def shown(table, v, h, fl):
    """May the table's figures reach a visitor? Its verdict is public, or it is held (drawn as "license needed")."""
    return fl.get(table) == "public" and (v.get(table) == "public" or table in h)


class TheLiveSet(unittest.TestCase):
    def test_every_public_row_loaded_is_of_a_table_public_or_held(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        pats = list(cfg.get("full") or [])
        for k in ("recent", "select"):
            pats += list((cfg.get(k) or {}).keys())
        v, h, fl = verdicts(), held(), flags()
        loaded = [t for t in fl if any(re.search(p, t) for p in pats)]
        self.assertGreater(len(loaded), 50)
        bad = [t for t in loaded if fl[t] == "public" and not shown(t, v, h, fl)]
        self.assertEqual(bad, [], "flagged public and loaded, so anon-readable, but its verdict is not public and it is not held")

    def test_row_level_security_serves_public_rows_only(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "migrations", "002_rls.sql"), encoding="utf-8") as f:
            sql = f.read()
        for t in ("series", "entities", "events", "catalogue"):
            self.assertIn(f"create policy public_rows on public.{t} for select to anon, authenticated using (license = 'public');", sql)


class Downloads(unittest.TestCase):
    def test_the_route_refuses_a_held_table_and_any_verdict_not_public_before_it_reads(self):
        with open(os.path.join(ROOT, "site", "app", "api", "download", "route.ts"), encoding="utf-8") as f:
            src = f.read()
        held_at = src.index("if (licenseNeeded(table)) return text(")
        refused_at = src.index("if (refused) return text(refused, 403);")
        read_at = src.index("cat[0].license !== \"public\"")
        self.assertLess(held_at, read_at)
        self.assertLess(refused_at, read_at)


class ReleaseOne(unittest.TestCase):
    def test_every_table_in_version_1_is_public(self):
        v = verdicts()
        for r in rows("docs", "redivis", "release-v1", "tables.csv"):
            if r["in_v1"] == "yes" and r["shape"] != "metadata":
                self.assertEqual(v.get(r["table"]), "public", r["table"])


class FindingsCards(unittest.TestCase):
    def cards(self):
        out = {}
        for p in glob.glob(os.path.join(ROOT, "site", "data", "findings", "*.json")):
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict) and "tables" in d:
                out[d.get("id") or os.path.basename(p)[:-5]] = list(d["tables"])
        return out

    def test_a_card_is_built_only_from_tables_public_or_held_unless_it_waits_for_a_ruling(self):
        v, h, fl = verdicts(), held(), flags()
        cards = self.cards()
        self.assertGreater(len(cards), 10)
        found = {c: {t for t in ts if not shown(t, v, h, fl)} for c, ts in cards.items()}
        found = {c: ts for c, ts in found.items() if ts}
        for c, ts in found.items():
            self.assertIn(c, CARDS_WAITING, f"card {c} draws {sorted(ts)}, not public; its files are served by address")
            self.assertLessEqual(ts, CARDS_WAITING[c], c)

    def test_the_list_of_cards_waiting_only_shrinks(self):
        v, h, fl = verdicts(), held(), flags()
        cards = self.cards()
        for c, ts in CARDS_WAITING.items():
            if c in cards:
                still = {t for t in cards[c] if not shown(t, v, h, fl)}
                self.assertTrue(still, f"{c} is built only from public tables now: take it off CARDS_WAITING")

    def test_no_page_drawing_the_cards_opens_while_one_waits(self):
        if not CARDS_WAITING:
            return
        with open(os.path.join(ROOT, "site", "lib", "release.ts"), encoding="utf-8") as f:
            src = f.read()
        for page in PAGES_DRAWING_CARDS:
            m = re.search(r'^\s*"' + re.escape(page) + r'"\s*:\s*"(live|review)"', src, re.M)
            self.assertTrue(m, page)
            self.assertEqual(m.group(1), "review", f"{page} draws the findings cards; it may not open while {sorted(CARDS_WAITING)} wait")
        self.assertNotRegex(src, r'"/research/[^"]*"\s*:\s*"live"')


if __name__ == "__main__":
    unittest.main()
