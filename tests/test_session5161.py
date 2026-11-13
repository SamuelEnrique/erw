"""Session 5161: the fresh pass of the security review, secrets and what a browser can fetch
(docs/reviews/security-faults-2026-11-13.md, "The fresh pass", row 31).

Energy Research Warehouse (ERW). No network, no model, no build: the tree is read.

tests/test_session5102.py scans the site's source (no secret can reach a browser). This widens the scan to what runs
the ERW and what a browser is handed without a page:

    the code and the configuration outside the site hold no text shaped like a key, and no file is named like one
    the workflows name only the secrets listed here, never print one, and none runs on a stranger's request
    the one data file a browser-side file imports is the license status: whatever a client file imports is in a
    script any visitor can fetch, whatever the page's status

    python -m unittest tests.test_session5161 -v
"""

import importlib.util
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def patterns():
    spec = importlib.util.spec_from_file_location("scan_git_secrets_5161", os.path.join(ROOT, "scripts", "scan_git_secrets.py"))
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    return [(k, p) for k, p in scan.PATTERNS if k != "named_literal"]


# What runs the ERW, outside the site's own source (which tests/test_session5102.py reads): by folder and by ending.
CODE = (("scripts", (".py", ".ps1", ".sh", ".mjs")), ("warehouse", (".py", ".sh", ".sql", ".yaml", ".yml", ".toml")), (".github", (".yml", ".yaml")),
        ("package", (".py", ".toml", ".txt", ".cfg")), (os.path.join("site", "scripts"), (".mjs", ".js", ".ts")))
SKIP_DIRS = {"__pycache__", "node_modules", ".venv", "output", "raw", "runs", ".next", "_retired"}


def tracked():
    """The files git tracks, or None where git cannot say (then every file found is read). A machine's own untracked
    file (a local setting, a scratch script) is that machine's, not the repository's: it is not this test's to read."""
    try:
        r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return {os.path.normpath(os.path.join(ROOT, *line.split("/"))) for line in r.stdout.splitlines()}


def code_files():
    out = []
    for folder, endings in CODE:
        for base, dirs, names in os.walk(os.path.join(ROOT, folder)):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            out += [os.path.join(base, n) for n in names if n.endswith(endings)]
    for n in os.listdir(ROOT):
        if n.endswith((".txt", ".toml", ".yml", ".yaml", ".json", ".sh", ".ps1", ".cfg", ".ini")) and os.path.isfile(os.path.join(ROOT, n)):
            out.append(os.path.join(ROOT, n))
    known = tracked()
    return sorted(f for f in out if known is None or os.path.normpath(f) in known)


class NoKeyInWhatRunsTheWarehouse(unittest.TestCase):
    def test_no_text_shaped_like_a_key(self):
        kinds = patterns()
        self.assertGreaterEqual(len(kinds), 9)
        files = code_files()
        self.assertGreaterEqual(len(files), 300, "the scan found too few files to mean anything")
        for f in files:
            if os.path.getsize(f) > 4_000_000:
                continue
            t = open(f, encoding="utf-8", errors="replace").read()
            for kind, pat in kinds:
                self.assertIsNone(pat.search(t), f"{os.path.relpath(f, ROOT)} holds text shaped like a {kind}")

    def test_no_file_named_like_a_key_or_an_env_file_beside_the_code(self):
        known = tracked()
        if known is None:
            self.skipTest("git cannot list the tracked files here")
        bad = [os.path.relpath(f, ROOT) for f in sorted(known)
               if os.path.basename(f).endswith((".pem", ".key", ".p12", ".pfx")) or (os.path.basename(f).startswith(".env") and os.path.basename(f) != ".env.example")]
        self.assertEqual(bad, [], "a file named like a key or an env file is tracked by git")

    def test_the_env_files_are_never_committed(self):
        ignore = src(".gitignore")
        self.assertRegex(ignore, r"(?m)^\.env\b")
        site_ignore = src("site", ".gitignore") if os.path.exists(os.path.join(SITE, ".gitignore")) else ignore
        self.assertRegex(site_ignore + ignore, r"(?m)^\.env")


# The secrets the workflows may name. A new one is added here when a workflow is given it, so the giving is read.
WORKFLOW_SECRETS = {"ANTHROPIC_API_KEY", "DIGEST_FROM", "DIGEST_RECIPIENTS", "EIA_API_KEY", "EMAIL_TOKEN_SECRET", "PJM_API_KEY", "REDIVIS_API_TOKEN",
                    "REDIVIS_OWNER", "RESEND_API_KEY", "SITE_URL", "SUPABASE_ANON_KEY", "SUPABASE_DB_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_URL", "GITHUB_TOKEN"}


class TheWorkflows(unittest.TestCase):
    def files(self):
        d = os.path.join(ROOT, ".github", "workflows")
        return sorted(os.path.join(d, n) for n in os.listdir(d) if n.endswith((".yml", ".yaml")))

    def test_only_the_listed_secrets_are_named(self):
        named = set()
        for f in self.files():
            named |= set(re.findall(r"secrets\.([A-Z_0-9]+)", open(f, encoding="utf-8").read()))
        self.assertGreaterEqual(len(named), 10)
        self.assertEqual(named - WORKFLOW_SECRETS, set(), "a workflow names a secret that is not listed here")

    def test_no_workflow_prints_a_secret_or_traces_its_shell(self):
        for f in self.files():
            name = os.path.basename(f)
            for line in open(f, encoding="utf-8").read().splitlines():
                if line.lstrip().startswith("#"):
                    continue
                self.assertNotRegex(line, r"\becho\b.*\$\{\{\s*secrets\.", f"{name}: a secret is printed")
                self.assertNotRegex(line, r"^\s*(?:-\s*)?(?:run:\s*)?set -[a-z]*x", f"{name}: the shell is traced")
                self.assertNotRegex(line, r"\bprintenv\b|\benv\s*\|\s*", f"{name}: the environment is printed")

    def test_no_workflow_runs_on_a_strangers_request_with_the_secrets(self):
        for f in self.files():
            t = "\n".join(line for line in open(f, encoding="utf-8").read().splitlines() if not line.lstrip().startswith("#"))
            for trigger in ("pull_request_target", "issue_comment", "workflow_run"):
                self.assertNotRegex(t, rf"(?m)^\s*{trigger}\s*:", f"{os.path.basename(f)} runs on {trigger}")


# Whatever a browser-side file imports is in a script any visitor can fetch, whatever the page's status.
CLIENT_DATA = {"data/license_status.json": "the license status of each table: public words, printed on the pages"}
IMPORT = re.compile(r"""(?:^|\n)\s*(?:import|export)\s+(?!type\b)(?:[^'";]*?\sfrom\s+)?['"]([^'"]+)['"]|\bimport\(\s*['"]([^'"]+)['"]\s*\)""")


class WhatABrowserIsHanded(unittest.TestCase):
    def resolve(self, spec, importer):
        if spec.startswith("@/"):
            base = os.path.join(SITE, *spec[2:].split("/"))
        elif spec.startswith("."):
            base = os.path.normpath(os.path.join(os.path.dirname(importer), *spec.split("/")))
        else:
            return None
        for cand in (base, base + ".ts", base + ".tsx", os.path.join(base, "index.ts"), os.path.join(base, "index.tsx")):
            if os.path.isfile(cand):
                return cand
        return None

    def test_the_data_files_a_browser_side_file_imports_are_the_listed_ones(self):
        files = []
        for d in ("app", "components", "lib"):
            for base, dirs, names in os.walk(os.path.join(SITE, d)):
                dirs[:] = [x for x in dirs if x != "_retired"]
                files += [os.path.join(base, n) for n in names if n.endswith((".ts", ".tsx"))]
        clients = [f for f in files if re.match(r"""\s*(?://[^\n]*\n\s*)*['"]use client['"]""", open(f, encoding="utf-8").read())]
        self.assertGreaterEqual(len(clients), 20)
        found = {}
        for c in clients:
            seen, todo = set(), [c]
            while todo:
                f = todo.pop()
                if f in seen:
                    continue
                seen.add(f)
                for m in IMPORT.finditer(open(f, encoding="utf-8").read()):
                    got = self.resolve(m.group(1) or m.group(2), f)
                    if not got or got in seen:
                        continue
                    if got.endswith((".json", ".csv", ".txt", ".md")):
                        found.setdefault(os.path.relpath(got, SITE).replace(os.sep, "/"), os.path.relpath(c, SITE).replace(os.sep, "/"))
                    elif got.endswith((".ts", ".tsx")):
                        todo.append(got)
        extra = {k: v for k, v in found.items() if k not in CLIENT_DATA}
        self.assertEqual(extra, {}, "a browser-side file now imports a data file: every visitor can fetch it; read it, then list it in CLIENT_DATA")


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        t = src("docs", "reviews", "security-faults-2026-11-13.md")
        row = [line for line in t.splitlines() if line.startswith("| 31 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("held-public-files-2026-11-13.md", row[0])
        self.assertIn("**Session 5161, secrets and what a browser can fetch.**", t)

    def test_no_em_or_en_dash(self):
        t = src("tests", "test_session5161.py")
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
