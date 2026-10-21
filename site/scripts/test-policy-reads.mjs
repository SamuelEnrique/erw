// Energy Research Warehouse (ERW) site, session 469: what an impact read cites (lib/policyreads.ts) and the Tag filter's
// choice for large loads, interconnection and tariffs (lib/policyweek.ts, LOAD_GROUP). No request, no browser, no model.
//
//   node --import ./scripts/alias-register.mjs scripts/test-policy-reads.mjs
//
// THE SENTENCES BELOW ARE MADE UP FOR THIS TEST: no read, agency, docket or figure in this file is real.
// Prints one line per assertion; exits 1 if any fails.
const R = await import("../lib/policyreads.ts");
const W = await import("../lib/policyweek.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const figs = (s) => R.figuresOf(s);

// 1. figures: a number with its unit; dates, years, times, dockets, orders, sections and names are not figures
ok(same(figs("The rule applies to 450 MW of new load, 20 percent of the queue."), ["450 MW", "20 percent"]), "a figure keeps its unit");
ok(same(figs("Effective March 3, 2026, or 2026-03-03, or 3/3/2026, or June 2027, by 2030."), []), "dates and years are not figures");
ok(same(figs("Under Order No. 1920 and docket EL26-67, section 45Y and 10 CFR 50.54."), []), "orders, dockets, sections and the Code are not figures");
ok(same(figs("Comments are due by 5:00 p.m. Eastern."), []), "a time of day is not a figure");
ok(same(figs("Lease Sales 259 and 261, Compressor Station 308, four Xe-100 reactors, an EEA 3."), []), "numbered things and model names are not figures");
ok(same(figs("A loan of USD 1.2 billion for a 1,900 acres site; comments within 30 days."), ["USD 1.2 billion", "1,900 acres", "30 days"]), "money, a year-sized count with a unit, and a span");
ok(same(figs("raise capacity by 627,000 Dth/day over a 30-day period"), ["627,000 Dth/day", "30-day"]), "a gas rate and a hyphened span");
ok(same(figs("Rate Order No. WAPA-211 sets $3.45 per kW-month."), ["$3.45"]), "a rate order's number is not a figure; its price is");
ok(same(figs("Two reactors and three units."), []), "a number written in words is not read");
ok(same(figs(null), []) && same(figs(""), []), "no text, no figure");

// 2. a read's citation: none, the action's own text, or an ERW table it names
ok(same(R.citeOf(null), { kind: "none", figures: [], tables: [] }), "no read: none");
ok(R.citeOf({ plain_read: "The agency opens a comment period.", what_changes: "", timeline: "" }).kind === "none", "a read with no number is marked none");
const t = R.citeOf({ plain_read: "Adds 300 MW.", what_changes: "300 MW of storage, 4 hours.", timeline: "Due 2026-12-01." });
ok(t.kind === "text" && same(t.figures, ["300 MW", "4 hours"]), "figures from the three fields, once each, in the page's order");
const tb = R.citeOf({ plain_read: "As eia930_all_generation shows, 5 GW.", what_changes: "", timeline: "" }, ["eia930_all_generation", "policy_reads"]);
ok(tb.kind === "table" && same(tb.tables, ["eia930_all_generation"]), "a read naming a known ERW table is marked table");
ok(R.citeOf({ plain_read: "the made_up_table rose", what_changes: "", timeline: "" }, ["policy_reads"]).kind === "none", "a snake_case word that is no ERW table is not a table");
ok(same(R.READ_FIELDS, ["plain_read", "what_changes", "timeline"]), "the three sentence fields, in the page's order");
ok(Object.values(R.CITE_WORDS).every((w) => !/[–—]/.test(w)), "the words carry no em or en dash");

// 3. the Tag filter's choice for large loads, interconnection and tariffs
const chip = (key) => ({ key, label: key, why: "" });
const known = ["large_load", "interconnection", "transmission_cost", "tax_credit"];
ok(W.LOAD_GROUP === "loads_interconnection_tariffs" && same([...W.LOAD_GROUP_TAGS], ["large_load", "interconnection", "transmission_cost"]), "the group is three of the rule's tags");
ok(W.tagOf({ tag: W.LOAD_GROUP }, known) === W.LOAD_GROUP, "the address names the group");
ok(W.tagOf({ tag: W.LOAD_GROUP }, ["tax_credit"]) === "", "the group is no choice where none of its tags is known");
ok(W.tagOf({}, known) === "" && W.hasTag([chip("tax_credit")], ""), "not chosen: the page as it was, every row");
ok(W.hasTag([chip("large_load")], W.LOAD_GROUP) && W.hasTag([chip("interconnection")], W.LOAD_GROUP) && W.hasTag([chip("transmission_cost")], W.LOAD_GROUP), "each of the three tags is in the group");
ok(!W.hasTag([chip("tax_credit")], W.LOAD_GROUP) && !W.hasTag([], W.LOAD_GROUP) && !W.hasTag(undefined, W.LOAD_GROUP), "tax credits and untagged rows are not");
ok(W.hasTag([chip("tax_credit")], W.ANY_TAG) && W.hasTag([chip("large_load")], "large_load") && !W.hasTag([chip("large_load")], "tax_credit"), "the earlier choices answer as before");
ok(W.tagHref(W.LOAD_GROUP) === "/policy?tag=loads_interconnection_tariffs", "the group's address");

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
