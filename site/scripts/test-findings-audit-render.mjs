// Energy Research Warehouse (ERW) site, chain 507 (session 8900): the findings audit at /internal/findings drawn to HTML
// with the site's own code, without a build.
//   node --import ./scripts/tsx-register.mjs scripts/test-findings-audit-render.mjs
// Checks: every draft of docs/findings has a row in data/findings_audit.json; the sheet's forty are in the sheet's order
// with sentence, chart, risk and the do-file whose text is the file on disk (to read and, as a data address, to save);
// each verdict draws its four checks with their reasons and hover tips; a withdrawn, not-checked or held draft cannot be
// approved (blockedReason, and the control drawn disabled with the reason); a passed draft and a draft the audit did not
// cover can; the filter opens on the sheet in its order, holds every verdict's count, and opens on every draft when no
// sheet draft is in the list; no em dash. Exit 0 when all hold, 1 otherwise. No network.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..", "..");
const { AUDIT, SHEET, auditOf, blockedReason } = await import("../lib/findingaudit.ts");
const { AuditPanel, SheetHead } = await import("../components/analysis/AuditPanel.tsx");
const { AuditBrowser } = await import("../components/analysis/AuditBrowser.tsx");
const { DraftReview } = await import("../components/analysis/DraftReview.tsx");
const { VERDICT_ORDER } = await import("../lib/findingauditwords.ts");
const fails = [];
const check = (ok, what) => { if (!ok) fails.push(what); };
const dash = String.fromCharCode(0x2014);
const unesc = (s) => s.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");

// every draft of docs/findings has its row, keyed by the id its document names
const docs = path.join(root, "docs", "findings");
let nDocs = 0;
for (const fam of fs.readdirSync(docs)) {
  const dir = path.join(docs, fam);
  if (!fs.statSync(dir).isDirectory()) continue;
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".md"))) {
    const m = fs.readFileSync(path.join(dir, f), "utf-8").match(/Draft `(scan-[a-z]+-[0-9a-f]{12})`/);
    if (!m) continue;
    nDocs += 1;
    const row = AUDIT.drafts[m[1]];
    check(row && row.slug === f.slice(0, -3) && row.family === fam, `${fam}/${f}: no row, or the row names another draft`);
  }
}
check(nDocs === Object.keys(AUDIT.drafts).length, `docs/findings holds ${nDocs} drafts, the file ${Object.keys(AUDIT.drafts).length}`);
check(nDocs >= 549, `fewer drafts than the audit's 549: ${nDocs}`);

// the sheet: forty, in order, each with its head, and the do-file the file on disk
check(SHEET.length === 40, `the sheet holds ${SHEET.length}, not 40`);
SHEET.forEach(({ id, row }, i) => {
  check(row?.sheet?.rank === i + 1, `sheet ${i + 1}: rank ${row?.sheet?.rank}`);
  check(["passed", "passed after a fix"].includes(row.verdict) && !row.blocked, `sheet ${i + 1}: verdict ${row.verdict}, blocked "${row.blocked}"`);
  const html = renderToStaticMarkup(h(SheetHead, { id, row }));
  for (const mark of ["data-sheet-sentence", "data-sheet-chart", "data-sheet-risk", "data-sheet-figure", "data-sheet-do-text", "data-sheet-do-save"]) check(html.includes(`${mark}="${id}"`), `sheet ${i + 1}: ${mark}`);
  check(row.sheet.risk.length > 20, `sheet ${i + 1}: no risk`);
  const disk = fs.readFileSync(path.join(root, ...row.files.do.split("/")), "utf-8").replace(/\r\n/g, "\n");
  check(row.sheet.do_text === disk, `sheet ${i + 1}: the do-file's text is not the file on disk`);
  const href = unesc(html.match(/data-sheet-do-save="[^"]*"|href="(data:text\/plain[^"]*)"/g)?.find((x) => x.startsWith("href=")) ?? "").replace(/^href="|"$/g, "");
  check(decodeURIComponent(href.replace("data:text/plain;charset=utf-8,", "")) === disk, `sheet ${i + 1}: the saved file is not the do-file`);
  check(html.includes(`name=${id}_1200x627.png&amp;show=1`), `sheet ${i + 1}: the chart is not the draft's own picture`);
});

// each verdict: the panel draws it with its four checks; the blocked ones say why and the control is disabled
const byVerdict = {};
for (const [id, row] of Object.entries(AUDIT.drafts)) (byVerdict[row.verdict] ??= []).push(id);
for (const v of ["passed", "passed after a fix", "not checked", "held", "withdrawn"]) {
  const ids = byVerdict[v] ?? [];
  check(ids.length > 0, `no draft of verdict ${v}`);
  for (const id of ids) {
    const row = auditOf(id);
    const html = renderToStaticMarkup(h(AuditPanel, { id, row }));
    check(html.includes(`data-audit="${v}"`) && html.includes(`data-audit-checks="4"`), `${row.slug}: the panel or its four checks`);
    check((html.match(/role="tooltip"/g) ?? []).length >= 6, `${row.slug}: fewer than six hover tips`);
    check(!html.includes(dash), `${row.slug}: an em dash`);
    const blocked = blockedReason(id);
    check(["passed", "passed after a fix"].includes(v) ? blocked === "" : blocked.length > 10, `${row.slug}: blocked "${blocked}" for ${v}`);
  }
}
check(AUDIT.counts.withdrawn >= 1 && AUDIT.counts.passed >= 360, `counts ${JSON.stringify(AUDIT.counts)}`);
const wid = byVerdict.withdrawn[0];
const review = renderToStaticMarkup(h(DraftReview, { id: wid, state: "draft", history: [], requestId: null, fullCard: "x", blocked: blockedReason(wid) }));
check(/<button[^>]*disabled=""[^>]*data-draft-button="approved"/.test(review), "a withdrawn draft's Approve is not disabled");
check(review.includes(`data-draft-blocked="${wid}"`) && review.includes("does not reproduce"), "a withdrawn draft does not say why");
const pid = byVerdict.passed[0];
const ok = renderToStaticMarkup(h(DraftReview, { id: pid, state: "draft", history: [], requestId: null, fullCard: "x", blocked: blockedReason(pid) }));
check(!/<button[^>]*disabled=""[^>]*data-draft-button="approved"/.test(ok) && !ok.includes("data-draft-blocked"), "a passed draft's Approve is stopped");
check(blockedReason("scan-scan-000000000000") === "", "a draft the audit did not cover is stopped");
check(renderToStaticMarkup(h(AuditPanel, { id: "scan-scan-000000000000", row: null })).includes('data-audit="none"'), "a draft the audit did not cover: no line");

// the filter: the sheet first, in its order; every verdict's count; every draft when no sheet draft is listed
const all = Object.entries(AUDIT.drafts).map(([id, r]) => ({ id, family: r.family, verdict: r.verdict, known: r.known.state, reader: r.sheet?.reader ?? "", rank: r.sheet?.rank ?? 0, text: r.sentence.toLowerCase(), ruling: "draft" }));
const kids = all.map((it) => h("p", { key: it.id, "data-k": it.id }, it.id));
const b = renderToStaticMarkup(h(AuditBrowser, { items: all, readers: AUDIT.readers }, kids));
const order = [...b.matchAll(/data-k="([^"]+)"/g)].map((m) => m[1]);
check(JSON.stringify(order) === JSON.stringify(AUDIT.sheet), "the filter does not open on the sheet in its order");
check(b.includes('data-audit-view="sheet"') && b.includes('data-audit-matches="40"'), "the filter's view or its count");
for (const v of VERDICT_ORDER.filter((x) => AUDIT.counts[x])) check(b.includes(`data-audit-count="${v}"`), `no count for ${v}`);
check(AUDIT.readers.length === 3 && AUDIT.readers.every((r) => b.includes(`>${r.replace(/&/g, "&amp;")}</option>`)), `the readers: ${AUDIT.readers.join(", ")}`);
const few = all.filter((it) => it.rank === 0).slice(0, 5);
const b2 = renderToStaticMarkup(h(AuditBrowser, { items: few, readers: [] }, few.map((it) => h("p", { key: it.id, "data-k": it.id }, it.id))));
check(b2.includes('data-audit-view="all"') && (b2.match(/data-k=/g) ?? []).length === 5, "a list with no sheet draft does not open on every draft");
check(!b.includes(dash), "an em dash in the filter");

if (fails.length) { console.log(`FAIL ${fails.length}:\n  ${fails.slice(0, 40).join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${nDocs} drafts with a row, the sheet of ${SHEET.length} in order, ${Object.keys(byVerdict).length} verdicts drawn, approval stopped on ${Object.values(AUDIT.drafts).filter((r) => r.blocked).length}`);
