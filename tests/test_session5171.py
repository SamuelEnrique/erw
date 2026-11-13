"""Session 5171: where the site redirects to, and which files its server reads
(docs/reviews/security-faults-2026-11-13.md, "The fresh pass", session 5171).

Energy Research Warehouse (ERW). No network, no model, no build: the source is read.

    a redirect goes to a path the code names on this site, never to an address a request supplied
    a file is read from the disk by a name the site holds in a list, or one bounded by a pattern with no path in it;
    the files of the site's server that read the disk are listed here, so a new one is read before it lands

    python -m unittest tests.test_session5171 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def site_files():
    out = [os.path.join(SITE, "proxy.ts")]
    for d in ("app", "components", "lib"):
        for base, dirs, names in os.walk(os.path.join(SITE, d)):
            dirs[:] = [x for x in dirs if x != "_retired"]
            out += [os.path.join(base, n) for n in names if n.endswith((".ts", ".tsx"))]
    return sorted(out)


def rel(f):
    return os.path.relpath(f, SITE).replace(os.sep, "/")


def code_lines(text):
    return [line for line in text.splitlines() if not line.lstrip().startswith(("//", "*", "/*"))]


class ARedirectGoesWhereTheCodeSays(unittest.TestCase):
    def test_every_answer_that_redirects_names_a_path_of_this_site(self):
        seen = 0
        for f in site_files():
            for line in code_lines(open(f, encoding="utf-8").read()):
                for m in re.finditer(r"(?:NextResponse|Response)\.redirect\(\s*(.{0,60})", line):
                    seen += 1
                    self.assertRegex(m.group(1), r"""^new URL\(\s*["'`]/""", f"{rel(f)}: a redirect whose address does not begin with a path of this site: {m.group(1)[:50]}")
                    self.assertIn("req.url)", line, f"{rel(f)}: a redirect not resolved against this request's own address")
        # a floor, so the scan cannot pass by finding nothing (seven once the old unlock link is retired: its GET redirects no more)
        self.assertGreaterEqual(seen, 6)

    def test_every_page_that_redirects_names_a_path_of_this_site(self):
        seen = {}
        for f in site_files():
            t = open(f, encoding="utf-8").read()
            if not re.search(r"""import \{[^}]*\b(?:redirect|permanentRedirect)\b[^}]*\} from ["']next/navigation["']""", t):
                continue
            for line in code_lines(t):
                for m in re.finditer(r"\b(?:redirect|permanentRedirect)\(\s*(.{0,40})", line):
                    seen.setdefault(rel(f), []).append(m.group(1))
        self.assertEqual(sorted(seen), ["app/ask/page.tsx", "app/play/battery/page.tsx"], "a page now redirects: read where to, then list it here")
        self.assertTrue(all(a.startswith('"/play/battery?mode=normal"') for a in seen["app/play/battery/page.tsx"]))
        # the Ask page goes to the Grid tool: the grid is looked up, the question is cut to 500 characters and encoded
        ask = src("site", "app", "ask", "page.tsx")
        self.assertIn('const base = gridHref(gridBy(grid)?.slug ?? "us48");', ask)
        self.assertIn("encodeURIComponent(q.slice(0, 500))", ask)
        self.assertTrue(all(a.startswith("`${base}") for a in seen["app/ask/page.tsx"]))

    def test_no_destination_is_read_from_the_address(self):
        for f in site_files():
            t = "\n".join(code_lines(open(f, encoding="utf-8").read()))
            # ("to" is not in the list: the price board reads a range's end by that name, a date)
            self.assertNotRegex(t, r"""(?:searchParams|sp|q|params)\.get\(\s*["'](?:next|return|returnTo|return_to|redirect|redirect_to|continue|dest|destination|url|goto)["']""",
                                f"{rel(f)} reads a destination from the address")


# The files of the site's server that read the disk, each with the line that decides the name it reads.
READS_THE_DISK = {
    "app/attention/page.tsx": 'path.join(process.cwd(), "data", "attention.json")',
    "app/cost-of-power/seller/model.ts": "HUBS.grids[iso]",                                   # a file the site's own index names (window P1's file)
    "app/play/ev/page.tsx": 'path.join(process.cwd(), "data", "ev_prices.json")',
    "app/severance/finder/download/route.ts": "const f = `${outDir()}/${FLAGS}`;",
    "app/severance/lease/real/page.tsx": r"if (!fs.existsSync(idx) || !/^[OG]-[0-9A-Z]{2}-\d{1,6}$/.test(lease)) return null;",
    "lib/chat/pagefiles.ts": 'path.join(process.cwd(), "data", "resources", "manifest.json")',   # the Ask engine's (window P3's file): its names come from the manifest and the tools' indexes
    "lib/companydata.ts": "if (!/^[a-z0-9-]{1,80}$/.test(id)) return null;",
    "lib/datacenterdata.ts": "const g = INDEX.grids[grid];",
    "lib/finder.ts": "const f = `${outDir()}/${SUMMARY}`;",
    "lib/findings.ts": "if (!/^[a-z0-9_.-]+$/i.test(cardId) || !fs.existsSync(f)) return null;",
    "lib/howsoondata.ts": None,
    "lib/policyweekdata.ts": None,
    "lib/problemEditions.ts": r"if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !editions().includes(date)) return null;",
    "lib/problems.ts": 'path.join(process.cwd(), "data", "merchant_snapshot.json")',
    "lib/resourcesdata.ts": 'if (!/^[A-Za-z0-9._-]+$/.test(file) || file.includes("..")) return null;',
    "lib/rulesdata.ts": None,
}


class AFileIsReadByANameTheSiteHolds(unittest.TestCase):
    def test_the_files_that_read_the_disk_are_the_listed_ones(self):
        reads = sorted(rel(f) for f in site_files() if re.search(r"""from ["'](?:node:)?fs(?:/promises)?["']""", open(f, encoding="utf-8").read()))
        self.assertEqual([r for r in reads if r not in READS_THE_DISK], [], "a file of the site's server now reads the disk: read how it names what it reads, then list it in READS_THE_DISK")

    def test_each_name_is_decided_as_listed(self):
        for name, line in READS_THE_DISK.items():
            p = os.path.join(SITE, *name.split("/"))
            if line is None or not os.path.exists(p):
                continue
            self.assertIn(line, open(p, encoding="utf-8").read(), f"{name}: the line that decided the file's name is gone")

    def test_a_card_or_a_layer_cannot_name_a_folder(self):
        # the two patterns that allow a dot allow no slash, so "..", even where it passes, names no other folder
        self.assertNotRegex("^[a-z0-9_.-]+$", r"[/\\]")
        self.assertNotRegex("^[A-Za-z0-9._-]+$", r"[/\\]")
        self.assertIn('file.includes("..")', src("site", "lib", "resourcesdata.ts"))

    def test_the_three_fixed_files_take_no_name_from_a_request(self):
        for name in ("lib/howsoondata.ts", "lib/policyweekdata.ts", "lib/rulesdata.ts"):
            t = open(os.path.join(SITE, *name.split("/")), encoding="utf-8").read()
            for line in code_lines(t):
                if re.search(r"fs\.(?:readFileSync|statSync|existsSync)\(", line):
                    self.assertRegex(line, r"fs\.(?:readFileSync|statSync|existsSync)\(\s*at\b", f"{name}: {line.strip()[:80]}")
            self.assertNotRegex(t, r"searchParams|params\b.*\bat\b", name)


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        self.assertIn("**Session 5171 (chain 247), redirects and file reads.**", src("docs", "reviews", "security-faults-2026-11-13.md"))

    def test_no_em_or_en_dash(self):
        t = src("tests", "test_session5171.py")
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
