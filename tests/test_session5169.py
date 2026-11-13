"""Session 5169: what chain 237's fresh pass did not reach, read and held
(docs/reviews/security-faults-2026-11-13.md, "The fresh pass", session 5169).

Energy Research Warehouse (ERW). No network, no model, no build: the workflows and the site's source are read.

    the workflows: each sets its permissions; each runs only GitHub's own actions; an input or an event's words reach
    a command only through the step's environment, never written into the command's own line
    the site has no server action (a function a browser can call by POST at any page's address, which the standing
    tests of the route handlers would not see), publishes no source map, and lets no SVG through the image optimizer

    python -m unittest tests.test_session5169 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def workflows():
    return sorted(os.path.join(WORKFLOWS, n) for n in os.listdir(WORKFLOWS) if n.endswith((".yml", ".yaml")))


def code(text):
    """The text without its comments, line by line. A comment of several lines is one whose first line begins with its
    opening mark: a slash and a star inside a string (an address) must not take code out with them. The stripper the
    earlier tests of this chain used did that to site/next.config.ts; this session corrected it in each of them."""
    out, inside = [], False
    for line in text.splitlines():
        s = line.strip()
        if inside:
            inside = "*/" not in s
            continue
        if s.startswith(("/*", "{/*")):
            if "*/" not in s:
                inside = True
                continue
            line = line.split("*/", 1)[1]
        line = re.sub(r"\{/\*.*?\*/\}", "", line)
        out.append(re.sub(r"(^|\s)//.*$", "", line))
    return "\n".join(out)


class TheWorkflows(unittest.TestCase):
    def test_each_sets_its_permissions(self):
        self.assertGreaterEqual(len(workflows()), 9)
        for f in workflows():
            t = open(f, encoding="utf-8").read()
            self.assertRegex(t, r"(?m)^permissions:\s*$", f"{os.path.basename(f)} sets no permissions: the token would hold the repository's defaults")
            block = t[re.search(r"(?m)^permissions:\s*$", t).end():]
            block = re.split(r"(?m)^\S", block, maxsplit=1)[0]
            grants = dict(re.findall(r"(?m)^\s+([a-z-]+):\s*(\w+)", block))
            self.assertTrue(grants, os.path.basename(f))
            for scope, level in grants.items():
                self.assertIn(level, ("read", "write", "none"), f"{os.path.basename(f)}: {scope}")
            self.assertNotIn("write-all", t)
            # no workflow may change the workflows or the repository's settings
            for scope in ("actions", "security-events", "id-token", "packages", "deployments"):
                self.assertNotEqual(grants.get(scope), "write", f"{os.path.basename(f)} may write {scope}")

    def test_each_runs_only_githubs_own_actions(self):
        for f in workflows():
            for line in open(f, encoding="utf-8").read().splitlines():
                m = re.match(r"\s*(?:-\s*)?uses:\s*(\S+)", line)
                if m:
                    self.assertRegex(m.group(1), r"^actions/[a-z-]+(?:/[a-z-]+)?@v\d+", f"{os.path.basename(f)} runs {m.group(1)}: an action that is not GitHub's own is read before it is run, and pinned")

    def test_an_input_reaches_a_command_only_through_the_environment(self):
        expr = re.compile(r"\$\{\{\s*(?:inputs\.|github\.event\.|github\.head_ref|github\.ref_name)")
        for f in workflows():
            name = os.path.basename(f)
            for n, line in enumerate(open(f, encoding="utf-8").read().splitlines(), 1):
                if line.lstrip().startswith("#") or not expr.search(line):
                    continue
                # allowed: NAME: ${{ ... }} (a step's environment, a job's condition, a group's name), never a line of a script
                self.assertRegex(line, r"^\s+(?:[A-Za-z_][A-Za-z0-9_-]*|if|group|name):\s*.*\$\{\{", f"{name}:{n}: an input is written into a line that is not a named value")
                self.assertNotRegex(line, r"^\s+(?:-\s*)?run:", f"{name}:{n}: an input is written into a command")

    def test_none_runs_on_a_strangers_request(self):
        for f in workflows():
            lines = [line for line in open(f, encoding="utf-8").read().splitlines() if not line.lstrip().startswith("#")]
            # the triggers: the keys two spaces under "on:", up to the next key at the left edge
            start = next(i for i, line in enumerate(lines) if re.match(r"^(on|'on'|\"on\"):", line))
            triggers = []
            for line in lines[start + 1:]:
                if re.match(r"^\S", line):
                    break
                m = re.match(r"^ {2}([a-z_]+)\s*:", line)
                if m:
                    triggers.append(m.group(1))
            self.assertTrue(triggers, os.path.basename(f))
            self.assertLessEqual(set(triggers), {"schedule", "workflow_dispatch", "push"}, f"{os.path.basename(f)} runs on {triggers}")


class WhatTheBuildOffers(unittest.TestCase):
    def files(self):
        out = []
        for d in ("app", "components", "lib"):
            for base, dirs, names in os.walk(os.path.join(SITE, d)):
                dirs[:] = [x for x in dirs if x != "_retired"]
                out += [os.path.join(base, n) for n in names if n.endswith((".ts", ".tsx"))]
        return out

    def test_no_server_action(self):
        for f in self.files():
            t = open(f, encoding="utf-8").read()
            self.assertNotRegex(t, r"""(?m)^\s*['"]use server['"]""",
                                f"{os.path.relpath(f, SITE)} declares a server action: a browser can call it by POST; bound it, guard it and list it as the route handlers are")

    def test_the_configuration_publishes_no_source_map_and_lets_no_svg_through(self):
        # the file's own lines of code: a line that is a comment may name what the code must not do (the file holds
        # addresses with a slash and a star in them, so comments are dropped line by line, not by their marks)
        c = "\n".join(line for line in src("site", "next.config.ts").splitlines() if not line.lstrip().startswith("//"))
        for word in ("productionBrowserSourceMaps", "dangerouslyAllowSVG", "remotePatterns", "domains:", "serverActions", "allowedOrigins", "ignoreBuildErrors", "ignoreDuringBuilds"):
            self.assertNotIn(word, c, f"site/next.config.ts now names {word}: read what it opens")
        self.assertIn("poweredByHeader: false", c)

    def test_no_page_of_errors_prints_the_error(self):
        # the framework's own error page prints a digest and nothing of the error; a page of the site's own would be read here
        for base, dirs, names in os.walk(os.path.join(SITE, "app")):
            dirs[:] = [x for x in dirs if x != "_retired"]
            for n in names:
                if n in ("error.tsx", "global-error.tsx"):
                    t = code(open(os.path.join(base, n), encoding="utf-8").read())
                    self.assertNotRegex(t, r"error\.(message|stack)", f"{os.path.relpath(os.path.join(base, n), SITE)} prints the error's own words to a visitor")


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        self.assertIn("**Session 5169 (chain 247), the workflows and what the build offers.**", src("docs", "reviews", "security-faults-2026-11-13.md"))

    def test_no_em_or_en_dash(self):
        t = src("tests", "test_session5169.py")
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
