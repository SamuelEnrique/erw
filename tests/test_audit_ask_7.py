"""Session 10234 (chain 710, part D): the terms and the privacy page say the visitor's daily code is irreversible only
without the server's secret.

docs/reviews/ask-model-audit-2026-11-26.md, finding 7. The code the database keeps for the chat's daily count and the
request limits is HMAC-SHA256 of the UTC day and the address under ASK_VISITOR_SALT (site/lib/chat/limits.ts visitorKey,
site/lib/guard.ts). /terms and /privacy said it "cannot be turned back into an address". Without the secret that holds;
with it, an IPv4 address is one of about 4.3 billion, and trying each against a code is a short computation, so the
server that holds the secret can turn a code back (the code's own comment, the ceilings' note and site/lib/guard.ts all
say "without the secret"). Words only, on both pages. Fails on main, passes on the branch.

Both pages are drawn to HTML with the site's own code (site/scripts/tsx-register.mjs and font-stub-loader.mjs, no
build, no network) when node and the site's packages are here; skipped otherwise.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PAGES = {"terms": "turned back into an address without the server's secret, and is another value the next day",
         "privacy": "it cannot be turned back into an address without the server's secret, it is another value the next day"}


def src(name):
    with open(os.path.join(SITE, "app", name, "page.tsx"), encoding="utf-8") as f:
        return " ".join(f.read().replace("&apos;", "'").split())


class TheWords(unittest.TestCase):
    def test_the_sources(self):
        for name, words in PAGES.items():
            self.assertIn(words, src(name), name)
        self.assertIn("keyed code of the address for that day only", src("terms"))   # tests/test_session177.py reads it

    def test_the_code_and_the_note_say_without_the_secret(self):
        with open(os.path.join(SITE, "lib", "chat", "limits.ts"), encoding="utf-8") as f:
            self.assertIn("cannot be turned back into an address without the secret", " ".join(f.read().split()))

    def test_the_pages_drawn(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        tmp = tempfile.mkdtemp(prefix="audit_ask_7_")
        script = os.path.join(tmp, "draw.mjs")
        with open(script, "w", encoding="utf-8") as f:
            f.write(DRAW)
        for name, words in PAGES.items():
            out = os.path.join(tmp, f"{name}.txt")
            r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", script, name, out], cwd=SITE, capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            with open(out, encoding="utf-8") as f:
                self.assertIn(words, f.read(), name)


DRAW = r"""
import fs from "node:fs";
import path from "node:path";
import { createRequire, register } from "node:module";
import { pathToFileURL } from "node:url";
register(pathToFileURL(path.join(process.cwd(), "scripts", "font-stub-loader.mjs")).href, import.meta.url);
const [name, outFile] = process.argv.slice(2);
const req = createRequire(path.join(process.cwd(), "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
globalThis.fetch = async () => new Response("not held", { status: 404 });
async function resolveTree(node) {
  if (node == null || typeof node !== "object") return node;
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  if (typeof node.type === "function" && node.type.constructor?.name === "AsyncFunction") return resolveTree(await node.type(node.props));
  const kids = node.props?.children;
  if (kids === undefined) return node;
  const rk = await resolveTree(kids);
  return React.cloneElement(node, undefined, ...(Array.isArray(rk) ? rk : [rk]));
}
const Page = (await import(pathToFileURL(path.join(process.cwd(), "app", name, "page.tsx")).href)).default;
const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve({}) })));
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
fs.writeFileSync(outFile, ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " "));
process.exitCode = 0;
"""


if __name__ == "__main__":
    unittest.main()
