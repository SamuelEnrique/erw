// Energy Research Warehouse (ERW) site, session 469: on the built site, in a real browser, what an impact read cites
// and the Tag filter's choice for large loads, interconnection or tariffs (lib/policyreads.ts, lib/policyweek.ts).
//
//   node --import ./scripts/alias-register.mjs scripts/check-policy-reads.mjs [base-url]
//
//   1. the page with no choice: the Tag filter shows "All" and the significance floor 5, as before session 469;
//   2. the address /policy?tag=loads_interconnection_tariffs chooses the group, lifts the floor and lists exactly the rows
//      that carry large_load, interconnection or transmission_cost; Reset gives the page as it was;
//   3. a row with a read, opened by a click, shows one "Figures:" line: its figures and the action as their source, or
//      "No figure"; a row without a read shows none.
// Exit 1 on a failure.
import { env, withBrowser } from "./browser.mjs";
import { LOAD_GROUP, LOAD_GROUP_LABEL, LOAD_GROUP_TAGS, tagHref } from "../lib/policyweek.ts";
import { CITE_WORDS } from "../lib/policyreads.ts";

const base = (process.argv[2] ?? "http://localhost:3469").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
if (!env("INTERNAL_COSTS_TOKEN")) { console.log("FAILED: INTERNAL_COSTS_TOKEN is not set"); process.exit(1); }

const code = await withBrowser(async ({ go, evaluate, wait, unlock, errors }) => {
  await unlock(base);
  const ready = () => wait(`!!document.querySelector('[data-policy-tag-filter] select') && !!document.querySelector('[data-policy-shown]')`, 30000, "the table of every action");
  const state = () => evaluate(`(() => {
    const sel = document.querySelector('[data-policy-tag-filter] select');
    const sig = [...document.querySelectorAll('select')].find((s) => [...s.options].some((o) => o.textContent === '5 or more'));
    return { tag: sel.value, choices: [...sel.options].map((o) => [o.value, o.textContent]), sig: sig ? sig.value : null,
      shown: Number(document.querySelector('[data-policy-shown]').dataset.policyShown),
      rows: [...document.querySelectorAll('tr[data-policy-row]')].map((tr) => ({ id: tr.dataset.policyRow, tags: (tr.querySelector('[data-policy-tags]')?.dataset.policyTags ?? '').split(' ').filter(Boolean), read: tr.textContent.includes('(read)') })) };
  })()`);

  await go(base + "/policy");
  await ready();
  const plain = await state();
  check(plain.tag === "" && plain.sig === "5", `with no choice the Tag filter shows All and the significance floor 5 (${plain.shown} shown)`);
  check(plain.choices.some(([v, l]) => v === LOAD_GROUP && l === LOAD_GROUP_LABEL), `the Tag filter offers "${LOAD_GROUP_LABEL}"`);

  await go(base + tagHref(LOAD_GROUP));
  await ready();
  const g = await state();
  const inGroup = g.rows.filter((r) => r.tags.some((t) => LOAD_GROUP_TAGS.includes(t)));
  check(g.tag === LOAD_GROUP && g.sig === "", `the address ${tagHref(LOAD_GROUP)} chooses the group and lifts the floor`);
  check(g.rows.length > 0 && inGroup.length === g.rows.length && g.shown === g.rows.length, `it lists ${g.rows.length} rows, every one tagged large loads, interconnection or transmission cost`);
  check(g.rows.every((r) => !(r.tags.length === 1 && r.tags[0] === "tax_credit")), "no row tagged only tax credits");
  await evaluate(`document.querySelector('[data-reset]').click()`);
  await wait(`document.querySelector('[data-policy-tag-filter] select').value === ''`, 10000, "the reset");
  const back = await state();
  check(back.tag === "" && back.sig === "5" && back.shown === plain.shown, `Reset gives the page as it was (${back.shown} shown)`);

  await go(base + "/policy");
  await ready();
  const withRead = plain.rows.find((r) => r.read), without = plain.rows.find((r) => !r.read);
  if (withRead) {
    await evaluate(`document.querySelector('tr[data-policy-row="${withRead.id}"]').click()`);
    await wait(`!!document.querySelector('[data-read-cites-of="${withRead.id}"]')`, 10000, "the opened read's line");
    const line = await evaluate(`(() => { const p = document.querySelector('[data-read-cites-of="${withRead.id}"]'); return { kind: p.dataset.readCites, words: p.textContent.replace(/\\s+/g, ' ').trim() }; })()`);
    const wordsOk = line.kind === "none" ? line.words === `Figures: ${CITE_WORDS.none}` : line.kind === "text" ? line.words.startsWith("Figures: ") && line.words.endsWith("Source: the action.") : line.words.includes(CITE_WORDS.table);
    check(["none", "text", "table"].includes(line.kind) && wordsOk, `an opened read says what it cites (${line.kind}): "${line.words.slice(0, 120)}"`);
  } else check(false, "a row with a read is on the first view");
  if (without) {
    await evaluate(`document.querySelector('tr[data-policy-row="${without.id}"]').click()`);
    await wait(`!!document.querySelector('tr[data-policy-row="${without.id}"] + tr')`, 10000, "the opened row without a read");
    check(!(await evaluate(`!!document.querySelector('[data-read-cites-of="${without.id}"]')`)), "a row without a read shows no Figures line");
  }
  check(errors.length === 0, `no script error on the page${errors.length ? ": " + errors.slice(0, 2).join(" | ").slice(0, 200) : ""}`);
  return bad ? 1 : 0;
});
console.log(`${n - bad} of ${n} checks pass`);
process.exitCode = code === 0 && bad === 0 ? 0 : 1;
