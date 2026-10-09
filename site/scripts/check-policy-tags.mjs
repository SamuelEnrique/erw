// Energy Research Warehouse (ERW) site, session 164: the tag chips of the policy monitor (/policy, in review), seen in
// a real browser on real rows. Session 157 could prove a chip only in unit tests: no tagged action fell in the second
// view's windows. The first view lists every action, and since session 164 it has a Tag filter kept in the address
// (/policy?tag=any, /policy?tag=large_load ...), so every tagged action of the live table is one address away.
//
//   npm run build && npx next start -p 3164
//   node --import ./scripts/alias-register.mjs scripts/check-policy-tags.mjs [base-url] [screenshot.png]
//
// The page is read in the internal view (it is in review), as HTML and then in a real browser (scripts/browser.mjs):
//   rows       /policy?tag=any lists the tagged actions of the live table, each a real row with its date and title;
//              they are exactly the actions the warehouse's own tag file names (data/policy/action_tags.json), and no
//              row is made up for the check: every id is read back from the page
//   chips      for each of the rule's four tags (data/policy/tag_rules.json) a chip is drawn on a real row: it has a
//              box on the screen, the tag's label, and a hover that names the rule, its version, the term that matched
//              and the field it matched in, as the tag file holds them; the mouse over the chip puts it under :hover
//   filter     choosing a tag in the browser lists exactly the rows that carry it and writes the address; an address
//              with a tag restores the choice, on the server (no script) too; a tag the rule does not know is no choice
//   visitor    a visitor gets the in-review page and no chip
//   method     the three sentences of the first view's old method paragraph are not on the face; each is the hover of
//              the words it explains, and all three stand in the Method note
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { ANY_TAG, FIRST_VIEW_METHOD, METHOD, tagHref } from "../lib/policyweek.ts";

const base = (process.argv[2] ?? "http://localhost:3164").replace(/\/$/, "");
const shot = process.argv[3] ?? "";
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const readJson = (rel) => { const u = new URL(rel, import.meta.url); return fs.existsSync(u) ? JSON.parse(fs.readFileSync(u, "utf8")) : null; };
const rules = readJson("../data/policy/tag_rules.json"), file = readJson("../data/policy/action_tags.json");
if (!rules || !file) { console.log("FAILED: data/policy/tag_rules.json or action_tags.json is not in the site's files"); process.exit(1); }
const TAGS = Object.keys(rules.tags);
const FIELD = { title: "title", abstract: "summary", first_paragraph: "first paragraph of the printed text", docket: "docket field" };

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const face = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const rowIds = (html) => [...html.matchAll(/<tr[^>]*data-policy-row="([^"]+)"[^>]*>/g)].map((m) => decode(m[1]));

// ---- as HTML: the address restores the choice on the server; a visitor sees no chip -------------------------------------
{
  const any = await get(tagHref(ANY_TAG));
  const ids = rowIds(any.html);
  check(any.status === 200 && any.html.includes('data-policy="all"') && ids.length > 0 && (any.html.match(/data-policy-tag="/g) ?? []).length >= ids.length,
    `${tagHref(ANY_TAG)} lists ${ids.length} tagged actions on the server, each with a chip`);
  const v = await get(tagHref(ANY_TAG), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-policy-tag=") && !v.html.includes("data-policy-row="), "as a visitor: the in-review page, no row and no chip");
  const odd = await get("/policy?tag=zoning");
  check(odd.status === 200 && /data-policy-tag-filter=""/.test(odd.html), "a tag the rule does not know is no choice");
  // the method paragraph: off the face, on the hovers, in the Method note
  const plain = await get("/policy");
  const t = face(plain.html), all = decode(plain.html);
  const sentences = Object.entries(FIRST_VIEW_METHOD);
  const onFace = sentences.filter(([, s]) => t.includes(s)).map(([k]) => k);
  const onHover = sentences.filter(([k, s]) => new RegExp(`title="[^"]*"[^>]*data-policy-hover="${k}"|data-policy-hover="${k}"`).test(plain.html) && all.includes(s)).map(([k]) => k);
  check(onFace.length === 0 && onHover.length === sentences.length, `the first view's method paragraph is off the face (${sentences.length} sentences), each the hover of the words it explains${onFace.length ? `; STILL ON THE FACE: ${onFace.join(", ")}` : ""}`);
  const note = fs.readFileSync(new URL(`../../${METHOD.doc}`, import.meta.url), "utf8").replace(/\s+/g, " ");
  const lost = sentences.filter(([, s]) => !note.includes(s)).map(([k]) => k);
  check(lost.length === 0 && plain.html.includes(METHOD.href), `all three sentences stand in the Method note (${METHOD.doc}), which the page links${lost.length ? `; NOT IN THE NOTE: ${lost.join(", ")}` : ""}`);
}

// ---- in a real browser ---------------------------------------------------------------------------------------------
const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, send, errors }) => {
  await open(base);
  const ready = () => wait(`document.querySelectorAll('select').length >= 6 && !!document.querySelector('[data-policy-tag-filter]')`, 30000, "the table of every action with its Tag filter");
  /** What the table shows now: the filter's choice, the address and every row drawn, with its chips as the screen has them. */
  const read = () => evaluate(`(() => {
    const box = (el) => { const b = el.getBoundingClientRect(), s = getComputedStyle(el); return b.width > 4 && b.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) > 0; };
    const rows = [...document.querySelectorAll('tr[data-policy-row]')].map((tr) => ({
      id: tr.dataset.policyRow, date: tr.children[0]?.textContent.trim() ?? '', agency: tr.children[1]?.textContent.trim() ?? '', title: (tr.children[3]?.childNodes[0]?.textContent ?? '').trim(),
      chips: [...tr.querySelectorAll('[data-policy-tag]')].map((c) => ({ key: c.dataset.policyTag, of: c.dataset.policyTagOf, label: c.textContent.trim(), tip: c.getAttribute('title') ?? '', drawn: box(c) })),
    }));
    const f = document.querySelector('[data-policy-tag-filter]'), sel = f.querySelector('select');
    return { tag: f.dataset.policyTagFilter, tagged: Number(f.dataset.policyTagged), choices: sel ? [...sel.options].map((o) => [o.value, o.textContent]) : [], value: sel ? sel.value : null,
      shown: Number(document.querySelector('[data-policy-shown]')?.dataset.policyShown ?? -1), address: location.pathname + location.search, rows };
  })()`);
  /** Choose in the Tag select as a reader does: the value, then the change the browser sends. */
  const choose = (value) => evaluate(`(() => { const sel = document.querySelector('[data-policy-tag-filter] select'); const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set; set.call(sel, ${JSON.stringify(value)}); sel.dispatchEvent(new Event('change', { bubbles: true })); return sel.value; })()`);

  await go(base + tagHref(ANY_TAG));
  await ready();
  const any = await read();
  {
    // the lead as a reader sees it, and its three hovers
    const lead = await evaluate(`(() => { const p = document.querySelector('[data-policy-lead]'); return { words: p.textContent.replace(/\\s+/g, ' ').trim(), hovers: Object.fromEntries([...p.querySelectorAll('[data-policy-hover]')].map((s) => [s.dataset.policyHover, { on: s.textContent.trim(), tip: s.getAttribute('title') }])) }; })()`);
    const said = "Energy rules, proposed rules and notices of DOE, FERC, EPA, NRC, BLM and Interior from the Federal Register, and news releases of the NRC, DOE, the Texas PUC and the CPUC, since 2025-10-01, each scored for significance and, when it scores 5 or more, read for its impact.";
    check(lead.words === said, "the lead still says what the page holds, word for word as before session 164");
    check(Object.entries(FIRST_VIEW_METHOD).every(([k, s]) => lead.hovers[k]?.tip === s) && lead.hovers.ferc.on === "FERC" && lead.hovers.scored.on === "scored for significance" && lead.hovers.read.on === "read for its impact",
      `each sentence of the old method paragraph is the hover of the words it explains: ${Object.entries(lead.hovers).map(([, h]) => `"${h.on}"`).join(", ")}`);
  }
  const held = Object.keys(file.tags).sort(), seen = any.rows.map((r) => r.id).sort();
  check(any.tag === ANY_TAG && any.value === ANY_TAG && any.rows.length > 0 && any.rows.every((r) => r.chips.length > 0 && /^\d{4}-\d{2}-\d{2}$/.test(r.date) && r.title.length > 3 && r.agency),
    `${tagHref(ANY_TAG)} in the browser: ${any.rows.length} rows, every one a real action with its date, agency, title and at least one chip (the filter counts ${any.tagged} tagged of the live table)`);
  const notHeld = seen.filter((id) => !held.includes(id)), notSeen = held.filter((id) => !seen.includes(id));
  check(notHeld.length === 0 && notSeen.length === 0 && any.tagged === held.length, `the rows are exactly the ${held.length} actions the warehouse's tag file names${notSeen.length ? `; IN THE FILE, NOT ON THE PAGE: ${notSeen.join(", ")}` : ""}${notHeld.length ? `; ON THE PAGE, NOT IN THE FILE: ${notHeld.join(", ")}` : ""}`);
  // every chip against the file: the tag, and a hover that names the rule, the term and the field
  {
    const wrong = [];
    let chips = 0;
    for (const r of any.rows) {
      const want = (file.tags[r.id] ?? []).filter((h) => TAGS.includes(h.tag));
      if (!same(r.chips.map((c) => c.key), TAGS.filter((k) => want.some((h) => h.tag === k)))) wrong.push(`${r.id}: chips ${r.chips.map((c) => c.key).join(" ")} against the file's ${want.map((h) => h.tag).join(" ")}`);
      for (const c of r.chips) {
        chips += 1;
        const h = want.find((x) => x.tag === c.key);
        if (!c.drawn) wrong.push(`${r.id}: the chip ${c.key} has no box on the screen`);
        if (c.of !== r.id || !c.label) wrong.push(`${r.id}: a chip with no label or of another row`);
        if (h && !(c.tip.includes(`version ${rules.version}`) && c.tip.includes(`"${h.matched_term}"`) && c.tip.includes(FIELD[h.matched_field] ?? h.matched_field) && c.tip.startsWith("Tagged by the written rule"))) wrong.push(`${r.id}: the hover of ${c.key} does not name the rule, "${h.matched_term}" and the ${h.matched_field}: ${c.tip}`);
      }
    }
    check(wrong.length === 0 && chips > 0, `every chip is drawn, labeled and hovers with the rule's version, its matched term and its field, as the tag file holds them (${chips} chips on ${any.rows.length} rows)${wrong.length ? `: ${wrong.slice(0, 3).join(" | ")}` : ""}`);
  }
  // each of the four tags: a chip on a real row, under the mouse
  for (const tag of TAGS) {
    const row = any.rows.find((r) => r.chips.some((c) => c.key === tag));
    if (!row) { check(false, `tag ${tag}: no action of the live table carries it, so no chip could be seen`); continue; }
    const chip = row.chips.find((c) => c.key === tag);
    const sel = `[data-policy-tag="${tag}"][data-policy-tag-of="${row.id}"]`;
    const at = await evaluate(`(() => { const c = document.querySelector(${JSON.stringify(sel)}); c.scrollIntoView({ block: 'center' }); const b = c.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2, w: b.width, h: b.height }; })()`);
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: at.x, y: at.y });
    const under = await evaluate(`(() => { const c = document.querySelector(${JSON.stringify(sel)}); return { hover: c.matches(':hover'), top: document.elementFromPoint(${at.x}, ${at.y}) === c, cursor: getComputedStyle(c).cursor }; })()`);
    check(chip.drawn && under.hover && under.top && under.cursor === "help" && chip.tip.length > 20,
      `tag ${tag}: the chip "${chip.label}" is drawn (${Math.round(at.w)} by ${Math.round(at.h)} px) on ${row.id} of ${row.date} (${row.agency}), under the mouse, with its hover: ${chip.tip}`);
  }
  if (shot) {
    await evaluate(`document.querySelector('[data-policy-tag-filter]').scrollIntoView({ block: 'start' })`);   // the filter and the tagged rows under it
    const png = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    fs.writeFileSync(shot, Buffer.from(png.data, "base64"));
    console.log(`     screenshot: ${shot}`);
  }
  // the filter, tag by tag, chosen in the browser
  for (const tag of TAGS) {
    await choose(tag);
    await wait(`document.querySelector('[data-policy-tag-filter]').dataset.policyTagFilter === ${JSON.stringify(tag)}`, 15000, `the tag ${tag} chosen`);
    const got = await read();
    const want = any.rows.filter((r) => r.chips.some((c) => c.key === tag)).map((r) => r.id).sort();
    check(same(got.rows.map((r) => r.id).sort(), want) && got.shown === want.length && got.address === tagHref(tag), `choosing ${tag} lists exactly the ${want.length} rows that carry it (${got.shown} shown) and writes the address ${got.address}`);
    const server = rowIds((await get(tagHref(tag))).html).sort();
    check(same(server, want), `the address ${tagHref(tag)} restores it on the server (${server.length} rows)`);
  }
  await choose("");
  await wait(`document.querySelector('[data-policy-tag-filter]').dataset.policyTagFilter === ""`, 15000, "the tag choice cleared");
  const cleared = await read();
  check(cleared.address === "/policy" && cleared.shown >= any.rows.length, `clearing the choice lists every action again (${cleared.shown}) at ${cleared.address}`);
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors.slice(0, 2).join(" | ").slice(0, 200)}` : ""}`);
  return 0;
});
if (code === null) { console.log("FAILED: no Chrome or Edge on this machine, so the chips were not seen in a browser"); bad += 1; }
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
