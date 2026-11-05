"""Session 445: the reader's guide (docs/guide.md). No em or en dash; every repository path it names exists; the figures
it states agree with the files it cites; package/llms.txt and package/README.md agree with it on the citation form, the
Redivis address, the download route and its readers, and the license holds."""

import csv
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


GUIDE = src("docs", "guide.md")
LLMS = src("package", "llms.txt")
README = src("package", "README.md")
SITE = json.loads(src("site", "data", "site.json"))
CITE = "Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD)"
SHORT = re.compile(r"^(battery|seller|datacenter|grid|findings)/")


def flat(s):
    return re.sub(r"\s+", " ", s)


class Guide(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for name, text in (("guide", GUIDE), ("llms.txt", LLMS), ("README", README)):
            self.assertNotIn(chr(0x2014), text, name)   # em dash
            self.assertNotIn(chr(0x2013), text, name)   # en dash

    def test_every_repository_path_exists(self):
        ticks = set(re.findall(r"`([^`\s]+)`", GUIDE))
        paths = [t for t in ticks if "/" in t and not t.startswith("/") and "://" not in t and not set("<?#") & set(t)]
        self.assertGreater(len(paths), 40)
        for p in paths:
            q = "site/public/" + p if SHORT.match(p) else p
            self.assertTrue(os.path.exists(os.path.join(ROOT, q)), q)

    def test_every_site_route_is_a_page_or_a_route(self):
        routes = set(re.findall(r"`(/[a-z0-9/_\-]+)", GUIDE))
        self.assertTrue({"/api/download", "/data", "/data/faults", "/research", "/cost-of-power/battery"} <= routes)
        for r in routes:
            self.assertTrue(any(os.path.exists(os.path.join(ROOT, "site", "app", *r.strip("/").split("/"), f))
                                for f in ("page.tsx", "route.ts")), r)

    def test_the_readers_are_the_routes_own(self):
        route = src("site", "app", "api", "download", "route.ts")
        self.assertIn('as === "py" || as === "do"', route)
        self.assertIn("&as=py", GUIDE)
        self.assertIn("&as=do", GUIDE)
        # session 535: the route writes an R reader too (as=r); the guide names it and says it is checked by its text
        self.assertIn('if (as === "r") return reader(', route)
        self.assertIn("&as=r", GUIDE)
        self.assertIn("The R reader (session 535) is checked by its text", GUIDE)
        self.assertIn("MAX_ROWS = 500_000", route)
        # session 1009: the hourly limit is read from the environment, 60 when it is not set (the guide's figure)
        self.assertIn('"download", PER_HOUR, 3600', route)
        self.assertIn("const PER_HOUR = Number(process.env.ERW_DOWNLOAD_PER_HOUR) || 60;", route)
        self.assertIn("500,000 rows", GUIDE)
        self.assertIn("60 downloads an hour", GUIDE)

    def test_figures_agree_with_their_files(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv"), encoding="utf-8") as f:
            held = list(csv.DictReader(f))
        self.assertIn(f"{len(held)} tables, the rows of `warehouse/metadata/license_status.csv`", GUIDE)
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            cov = list(csv.DictReader(line for line in f if not line.startswith("#")))
        pub = sum(r["license"] == "public" for r in cov)
        internal = sum(r["license"] == "internal" for r in cov)
        # the counts are the guide's of 21 October 2026; the warehouse may grow, so only the total's parts are pinned
        self.assertIn("179 public and 33 internal of 212", GUIDE)
        self.assertGreaterEqual(pub + internal, 212)
        self.assertEqual(SITE["redivis"]["dataset"], "energy_research_warehouse")
        self.assertIn(SITE["redivis"]["url"], GUIDE)
        self.assertFalse(SITE["redivis"]["released"])
        self.assertIn("Version 1 is pending release", GUIDE)

    def test_the_citation_form_is_the_release_s(self):
        release = flat(src("docs", "redivis", "release-v1.md"))
        self.assertIn(CITE, release.replace("\\<", "<").replace("\\>", ">"))
        self.assertIn(CITE, flat(GUIDE))


class PackageAgrees(unittest.TestCase):
    def test_llms_txt(self):
        llms = flat(LLMS)
        self.assertIn(CITE, llms)
        self.assertIn(SITE["redivis"]["url"], llms)
        self.assertIn("/api/download?table=<table>", llms)
        self.assertIn("&as=do or &as=r for a Python, Stata or base-R reader", llms)   # session 535
        self.assertIn("warehouse/metadata/license_status.csv", llms)
        self.assertIn("docs/guide.md", llms)

    def test_readme(self):
        readme = flat(README)
        self.assertIn("held: license needed", readme)
        self.assertIn("warehouse/metadata/license_status.csv", readme)
        self.assertIn("[`docs/guide.md`](../docs/guide.md)", readme)
        # session 1001 (chain 070): the package's citation is the specification's (docs/methods/packages.md), on the
        # Stanford dataset; the guide and llms.txt keep the release-v1.md form until they are rewritten (session 1011)
        self.assertIn("Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `datapages.erw`, version <tag> (released <YYYY-MM-DD>)", readme)

    def test_the_held_count_agrees(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv"), encoding="utf-8") as f:
            n = sum(1 for _ in csv.DictReader(f))
        for name, text in (("llms.txt", flat(LLMS)), ("README", flat(README)), ("guide", flat(GUIDE))):
            self.assertIn(str(n), text, name)


if __name__ == "__main__":
    unittest.main()
