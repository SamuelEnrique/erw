"""Session 587: /internal/holds, the held figures that show, on an internal page.

Session 505's site/scripts/check-holds.mjs writes docs/licenses_holds.csv on a build: one line a page that draws a figure
of a table held for a license without the words "license needed". site/scripts/build-content.mjs turns that file, with
each table's record in warehouse/metadata/license_status.csv, into site/content/holds.json (site/scripts/holds-content.mjs),
which site/lib/holds.ts imports for site/app/internal/holds/page.tsx. These tests hold that the page lists exactly the
CSV's rows, each cell as written and in its order, with each table's status and verdict from the record; that a missing
or misshapen file is said, not filled; that the page is gated as /internal/waits is and draws no figure of a held table;
and, when HOLDS_BASE names a running build and INTERNAL_COSTS_TOKEN is set, that the served page has one row a line."""

import csv
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
SCRIPT = os.path.join(SITE, "scripts", "holds-content.mjs")
BUILD = os.path.join(SITE, "scripts", "build-content.mjs")
PAGE = os.path.join(SITE, "app", "internal", "holds", "page.tsx")
WAITS = os.path.join(SITE, "app", "internal", "waits", "page.tsx")
LIB = os.path.join(SITE, "lib", "holds.ts")
HOLDS = os.path.join(ROOT, "docs", "licenses_holds.csv")
STATUS = os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")
COLUMNS = ["page", "figures", "kinds", "tables", "grids", "day"]
NODE = shutil.which("node")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def content(*args):
    """The JSON scripts/holds-content.mjs prints for the given files (none: the repository's)."""
    r = subprocess.run([NODE, SCRIPT, *args], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=60)
    if r.returncode != 0:
        raise AssertionError(f"holds-content.mjs exited {r.returncode}: {r.stderr}")
    return json.loads(r.stdout)


def csv_rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def status_rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


@unittest.skipUnless(NODE, "node is not on this machine")
class TheList(unittest.TestCase):
    def test_the_rows_are_exactly_the_csvs(self):
        self.assertTrue(os.path.exists(HOLDS), "docs/licenses_holds.csv (session 505) is on this branch")
        c = content()
        self.assertIsNone(c["unread"])
        want = csv_rows(HOLDS)
        self.assertEqual(c["rows"], [{k: r[k] for k in COLUMNS} for r in want])
        self.assertEqual(len(c["rows"]), len(want))
        self.assertEqual(c["columns"], COLUMNS)

    def test_each_table_carries_its_record(self):
        c = content()
        rec = status_rows(STATUS)
        named = {t.strip() for r in csv_rows(HOLDS) for t in r["tables"].split(";") if t.strip()}
        self.assertEqual(set(c["tables"]), named)
        for t in named:
            self.assertIn(t, rec, f"{t} has a row in license_status.csv")
            got = c["tables"][t]
            for k in ("status", "verdict", "from", "publishers"):
                self.assertEqual(got[k], rec[t][k], f"{t}: {k}")

    def test_a_scratch_file_is_read_cell_for_cell(self):
        rows = [
            {"page": "/a?x=1", "figures": "3", "kinds": "number; panel", "tables": "t_one; t_two", "grids": "ISO-NE; NYISO", "day": "2026-10-21"},
            {"page": "/b", "figures": "1", "kinds": "number", "tables": "t_three", "grids": "", "day": "2026-10-21"},
        ]
        with tempfile.TemporaryDirectory() as d:
            h = os.path.join(d, "holds.csv")
            s = os.path.join(d, "status.csv")
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
            with open(h, "w", encoding="utf-8", newline="") as f:
                f.write(buf.getvalue())
            with open(s, "w", encoding="utf-8", newline="") as f:
                f.write("table,status,from,publishers,verdict,permission,permission_ref,note\n"
                        "t_one,license needed,2026-10-21,ISO-NE,needs written permission,,,a note, with a comma\n"
                        "t_two,public,2026-10-21,NYISO,may be public,,,\n")
            c = content(h, s)
            self.assertEqual(c["rows"], rows)
            self.assertEqual(c["tables"]["t_one"], {"status": "license needed", "verdict": "needs written permission", "from": "2026-10-21", "publishers": "ISO-NE"})
            self.assertEqual(c["tables"]["t_two"]["verdict"], "may be public")
            self.assertIsNone(c["tables"]["t_three"], "a table with no record is null, not filled")

    def test_a_missing_or_misshapen_file_is_said(self):
        with tempfile.TemporaryDirectory() as d:
            c = content(os.path.join(d, "none.csv"))
            self.assertIn("was not found", c["unread"])
            self.assertEqual(c["rows"], [])
            bad = os.path.join(d, "bad.csv")
            with open(bad, "w", encoding="utf-8") as f:
                f.write("page,figures\n/a,1\n")
            c = content(bad)
            self.assertIn("header", c["unread"])
            self.assertEqual(c["rows"], [])
            short = os.path.join(d, "short.csv")
            with open(short, "w", encoding="utf-8") as f:
                f.write(",".join(COLUMNS) + "\n/a,1,number\n")
            c = content(short)
            self.assertIn("line 2", c["unread"])
            self.assertEqual(c["rows"], [])
            c = content(HOLDS, os.path.join(d, "none.csv"))
            self.assertIn("was not found", c["status_unread"])
            self.assertTrue(all(v is None for v in c["tables"].values()))


class ThePage(unittest.TestCase):
    def test_build_content_writes_its_own_file(self):
        b = read(BUILD)
        self.assertIn('import { holdsFromRepo } from "./holds-content.mjs";', b)
        self.assertIn('"holds.json"', b)
        self.assertIn("/content/holds.json", read(os.path.join(SITE, ".gitignore")))
        lib = read(LIB)
        self.assertIn('import "server-only";', lib)
        self.assertIn('import holds from "@/content/holds.json";', lib)

    def test_one_row_a_line_and_nothing_else(self):
        p = read(PAGE)
        self.assertEqual(p.count("h.rows.map((r, i) => <Row "), 1)
        self.assertIn("data-hold-row={i} data-hold-page={r.page}", p)
        # every cell of the line is drawn as written
        for k in COLUMNS:
            self.assertIn(f"r.{k}", p, k)

    def test_gated_as_waits_is(self):
        p = read(PAGE)
        gate = 'if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();'
        self.assertIn(gate, p)
        self.assertIn(gate, read(WAITS))
        self.assertIn('export const dynamic = "force-dynamic";', p)
        self.assertIn("robots: { index: false, follow: false }", p)
        self.assertIn("<Brand noUsage>", p)
        self.assertIn("data-no-usage", p)
        self.assertNotIn("token", re.sub(r"//[^\n]*", "", p).replace("INTERNAL_COSTS_TOKEN", ""))
        self.assertNotIn("/internal/holds", read(os.path.join(SITE, "lib", "release.ts")))

    def test_no_figure_of_a_held_table_is_drawn(self):
        p = read(PAGE)
        code = re.sub(r"//[^\n]*", "", p)
        for word in ("<Num", "data-check", "@/lib/supabase", "@/lib/license", "fetch(", "searchParams"):
            self.assertNotIn(word, code, word)
        imports = re.findall(r'from "([^"]+)"', p)
        self.assertEqual(sorted(imports), sorted(["next", "@/components/Brand", "next/headers", "next/navigation", "@/lib/holds", "@/lib/release", "@/lib/thesis/server"]))

    def test_no_em_dash(self):
        for f in (PAGE, LIB, SCRIPT, BUILD, __file__):
            self.assertNotIn(chr(0x2014), read(f), f)


@unittest.skipUnless(os.environ.get("HOLDS_BASE") and len(os.environ.get("INTERNAL_COSTS_TOKEN", "")) >= 24, "HOLDS_BASE and INTERNAL_COSTS_TOKEN name a running build")
class Served(unittest.TestCase):
    def test_the_served_page_lists_the_csvs_rows(self):
        base = os.environ["HOLDS_BASE"].rstrip("/")
        body = urllib.parse.urlencode({"token": os.environ["INTERNAL_COSTS_TOKEN"]}).encode()

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        op = urllib.request.build_opener(NoRedirect)
        try:
            origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(base))
            req = urllib.request.Request(f"{origin}/internal/unlock", data=body, method="POST", headers={
                "Content-Type": "application/x-www-form-urlencoded", "Origin": origin, "User-Agent": "erw-check (python)"})
            r = op.open(req, timeout=60)
            headers = r.headers
        except urllib.error.HTTPError as e:
            headers = e.headers
        cookie = "; ".join(c.split(";")[0] for c in headers.get_all("Set-Cookie") or [])
        self.assertTrue(cookie, "the internal cookie was set")
        html = urllib.request.urlopen(urllib.request.Request(f"{base}/internal/holds", headers={"Cookie": cookie}), timeout=120).read().decode("utf-8")
        got = [x.replace("&amp;", "&") for x in re.findall(r'data-hold-page="([^"]*)"', html)]
        self.assertEqual(got, [r["page"] for r in csv_rows(HOLDS)])
        self.assertNotIn('data-in-review="1"', html)


if __name__ == "__main__":
    unittest.main()
