"""Session 503: a fresh worktree passes the suite. On 21 October 2026 tests failed in fresh worktrees only for want of
files the build generates and git ignores: the node tests that import the site's modules stopped with "alias-loader:
nothing at @/content/docs.json" (sessions 464, 470, 471, 473). The alias loader (site/scripts/alias-loader.mjs) now
writes a missing generated file once, with the script `npm run content` runs for it, before it resolves it; a file
already there is never rewritten; a failing script stops the import with an error that names `npm run content`.
docs/machines.md, "Other checkouts", says what a fresh worktree needs and what writes itself."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
LOADER = os.path.join(SITE, "scripts", "alias-loader.mjs")
REGISTER = os.path.join(SITE, "scripts", "alias-register.mjs")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def generated_map():
    """The GENERATED map of the loader, read from its source: {file: script}."""
    block = re.search(r"export const GENERATED = \{(.*?)\};", src("site", "scripts", "alias-loader.mjs"), re.S).group(1)
    return dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', block))


class TheMap(unittest.TestCase):
    def test_the_loader_names_both_generated_files_and_their_scripts(self):
        self.assertEqual(generated_map(), {"content/docs.json": "scripts/build-content.mjs",
                                           "content/waits.json": "scripts/build-waits.mjs"})

    def test_each_script_exists_and_is_what_npm_run_content_runs(self):
        content = json.loads(src("site", "package.json"))["scripts"]["content"]
        for script in generated_map().values():
            self.assertTrue(os.path.isfile(os.path.join(SITE, script)), script)
            self.assertIn(f"node {script}", content)

    def test_each_file_is_one_git_ignores(self):
        ignore = src("site", ".gitignore")
        for rel in generated_map():
            self.assertIn("/" + rel, ignore)

    def test_machines_md_says_what_a_fresh_worktree_needs(self):
        section = src("docs", "machines.md").split("Other checkouts", 1)[1][:6000]
        self.assertIn("session 503", section)
        for words in ("npm ci", "npm run content", ".env.local", "next build"):
            self.assertIn(words, section)

    def test_no_dash(self):
        for p in (("tests", "test_session503.py"), ("site", "scripts", "alias-loader.mjs")):
            self.assertNotRegex(src(*p), "[" + chr(0x2013) + chr(0x2014) + "]", p)


@unittest.skipUnless(NODE, "node is not on this machine")
class TheLoader(unittest.TestCase):
    """The loader in a small copy of the site: a stub script stands in for build-content.mjs, so the test writes
    nothing in the repository."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.site = os.path.join(self.tmp.name, "site")
        os.makedirs(os.path.join(self.site, "scripts"))
        for f in (LOADER, REGISTER):
            shutil.copy(f, os.path.join(self.site, "scripts"))
        with open(os.path.join(self.site, "probe.mjs"), "w", encoding="utf-8") as f:
            f.write('import docs from "@/content/docs.json";\nconsole.log(JSON.stringify(docs));\n')

    def tearDown(self):
        self.tmp.cleanup()

    def stub(self, body):
        with open(os.path.join(self.site, "scripts", "build-content.mjs"), "w", encoding="utf-8") as f:
            f.write(body)

    def run_probe(self):
        return subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "probe.mjs"], cwd=self.site,
                              capture_output=True, text=True, timeout=60)

    def test_a_missing_file_is_written_once_by_its_script(self):
        self.stub('import fs from "node:fs";\nfs.mkdirSync("content", { recursive: true });\n'
                  'fs.writeFileSync("content/docs.json", JSON.stringify({ made: 1 }));\nconsole.log("noise on stdout");\n')
        r = self.run_probe()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), '{"made":1}')                     # the script's own stdout is not passed on
        self.assertIn("content/docs.json was missing; written by node scripts/build-content.mjs", r.stderr)
        # a second run finds it and writes nothing: the stub now writes something else, which must not appear
        self.stub('import fs from "node:fs";\nfs.writeFileSync("content/docs.json", JSON.stringify({ made: 2 }));\n')
        r = self.run_probe()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), '{"made":1}')
        self.assertNotIn("was missing", r.stderr)

    def test_a_failing_script_stops_the_import_and_names_the_command(self):
        self.stub('console.error("boom"); process.exit(1);\n')
        r = self.run_probe()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("npm run content", r.stderr)
        self.assertIn("boom", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.site, "content", "docs.json")))

    def test_an_import_outside_the_map_is_resolved_as_before(self):
        os.makedirs(os.path.join(self.site, "data"))
        with open(os.path.join(self.site, "data", "x.json"), "w", encoding="utf-8") as f:
            f.write('{"a": 3}')
        with open(os.path.join(self.site, "probe.mjs"), "w", encoding="utf-8") as f:
            f.write('import x from "@/data/x.json";\nconsole.log(x.a);\n')
        r = self.run_probe()
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "3"), r.stderr)


if __name__ == "__main__":
    unittest.main()
