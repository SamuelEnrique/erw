// Session 10229 (problems audit): the five problem sets of the whole country and /learn/bill drawn with the site's own
// code (no build, no server, every request refused). For each set: every question's parts, each keyed figure with its
// key, value, unit and the string the page prints (lib/format.ts shown); the set's page drawn to HTML and its visible
// text. For the bill: the five default bills line by line (lib/bill.ts on site/data/bill_rules.json) and the page drawn.
// node --import ./scripts/problem-sets-register.mjs ../runs/c10229/draw_problems.mjs <out dir>   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const out = process.argv[2];
fs.mkdirSync(out, { recursive: true });
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
const asked = [];
globalThis.fetch = async (url) => { asked.push(String(url)); throw new Error("no request in this audit"); };
async function resolveTree(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolveTree(await t(node.props));
  if (node.props && node.props.children !== undefined) return React.cloneElement(node, undefined, ...[].concat(await resolveTree(node.props.children)));
  return node;
}
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const textOf = (html) => unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));

const { problemSet } = await import(pathToFileURL(path.join(site, "lib", "problems.ts")).href);
const { shown } = await import(pathToFileURL(path.join(site, "lib", "format.ts")).href);
const SLUGS = ["who-trades-with-whom", "storm-across-the-country", "under-the-ground-and-in-the-wind", "where-energy-goes", "your-own-balancing-authority"];
const flat = (parts) => parts.map((p) => (typeof p === "string" ? p : `${shown(p.v)}${p.u ? ` ${p.u}` : ""}`)).join("");
const figs = (parts) => parts.filter((p) => typeof p !== "string").map((p) => ({ k: p.k, v: p.v, u: p.u ?? "", shown: shown(p.v) }));
const sets = {};
for (const slug of SLUGS) {
  const s = await problemSet(slug);
  const qs = [s.example, ...s.questions].filter(Boolean).map((q) => ({
    id: q.id, q: q.q, answer: flat(q.answer), line: flat(q.line), steps: q.steps.map(flat), why: q.why,
    figures: [...figs(q.answer), ...figs(q.line), ...q.steps.flatMap(figs)],
  }));
  sets[slug] = { title: s.title, teacher: s.teacher, questions: qs };
  console.log(`${slug}: ${qs.length} questions, ${qs.reduce((a, q) => a + q.figures.length, 0)} figure parts`);
}
fs.writeFileSync(path.join(out, "sets.json"), JSON.stringify(sets, null, 1));

// each set's page, drawn
const Live = (await import(pathToFileURL(path.join(site, "app", "learn", "problems", "[slug]", "page.tsx")).href)).default;
for (const slug of SLUGS) {
  const el = await Live({ params: Promise.resolve({ slug }) });
  const html = renderToStaticMarkup(await resolveTree(el));
  fs.writeFileSync(path.join(out, `page_${slug}.html`), html);
  const checks = [...html.matchAll(/data-check="([^"]*)"[^>]*>([^<]*)</g)].map((m) => [unq(m[1]), unq(m[2])]);
  fs.writeFileSync(path.join(out, `page_${slug}.txt`), [`${slug}: ${html.length} characters, ${checks.length} checked numbers; em dashes ${html.split(String.fromCharCode(0x2014)).length - 1}; requests ${asked.length}`, "", textOf(html)].join("\n"));
  console.log(`page ${slug}: ${checks.length} checked numbers`);
}

// the bill: the five defaults line by line, and the page
const rules = JSON.parse(fs.readFileSync(path.join(site, "data", "bill_rules.json"), "utf-8"));
const bill = await import(pathToFileURL(path.join(site, "lib", "bill.ts")).href);
const bills = {};
for (const k of bill.BILL_KEYS) {
  const b = bill.defaultBill(rules, k);
  bills[k] = { total: b.total, shown: shown(b.total), kwh: b.kwh, lines: b.lines.map((l) => ({ id: l.id, name: l.name, group: l.group ?? "", amount: l.amount, detail: l.detail, effective: l.effective })) };
}
fs.writeFileSync(path.join(out, "bills.json"), JSON.stringify(bills, null, 1));
const Bill = (await import(pathToFileURL(path.join(site, "app", "learn", "bill", "page.tsx")).href)).default;
const bhtml = renderToStaticMarkup(await resolveTree(await Bill()));
fs.writeFileSync(path.join(out, "page_bill.html"), bhtml);
fs.writeFileSync(path.join(out, "page_bill.txt"), [`/learn/bill: ${bhtml.length} characters; em dashes ${bhtml.split(String.fromCharCode(0x2014)).length - 1}; requests asked ${asked.length}`, "", textOf(bhtml)].join("\n"));
console.log(`bill: ${Object.entries(bills).map(([k, b]) => `${k} ${b.shown}`).join(", ")}; requests refused ${asked.length}`);
process.exitCode = 0;
