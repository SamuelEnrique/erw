// Energy Research Warehouse (ERW) site: bundle the committed markdown the site renders.
//
// Reads, from the repository (one level above site/):
//   docs/digest/YYYY-MM-DD.md and docs/digest/latest.md   the Energy Digest archive
//   docs/datastandard.md                                   the data standard
//   docs/methods/*.md                                      method documents
// and writes site/content/docs.json, which the pages import. Runs before
// `next dev` and `next build` (package.json predev and prebuild), so the
// content is part of the build and no page reads the file system at request
// time. A missing file fails the build: the site never shows a stand-in.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
const docs = path.join(repo, "docs");

function read(p) {
  if (!fs.existsSync(p)) {
    console.error(`build-content: missing ${path.relative(repo, p)}`);
    process.exit(1);
  }
  return fs.readFileSync(p, "utf-8").replace(/\r\n/g, "\n");
}

const digestDir = path.join(docs, "digest");
const digests = {};
for (const f of fs.readdirSync(digestDir).sort()) {
  const m = f.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
  if (m) digests[m[1]] = read(path.join(digestDir, f));
}
if (Object.keys(digests).length === 0) {
  console.error("build-content: no dated digests in docs/digest");
  process.exit(1);
}

const methods = {};
for (const f of fs.readdirSync(path.join(docs, "methods")).sort()) {
  if (f.endsWith(".md")) methods[f.replace(/\.md$/, "")] = read(path.join(docs, "methods", f));
}

const out = {
  built_at: new Date().toISOString(),
  digests,
  latest: read(path.join(digestDir, "latest.md")),
  datastandard: read(path.join(docs, "datastandard.md")),
  methods,
};
fs.mkdirSync(path.join(here, "..", "content"), { recursive: true });
fs.writeFileSync(path.join(here, "..", "content", "docs.json"), JSON.stringify(out));
console.log(`build-content: ${Object.keys(digests).length} digests, ${Object.keys(methods).length} method documents, the data standard`);
