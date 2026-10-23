// Energy Research Warehouse (ERW) site, session 2302 (chain 087): which queue positions the datacenter tracker's power
// side shows, on fixtures. lib/datacenter/bygrid.ts, queueSiteMatch: the first field of a row (name, fuel or type field,
// operator) that names a datacenter or a large load by the builder's own pattern (QUEUE_SITE_PATTERN), or null. Five
// rows: the two ERCOT positions session 2102 found (docs/reviews/datacenters-power-side-2026-10-23.md), whose only
// data-center word is their operator's name; a row matched by its name; a row matched by its fuel field; and a solar
// row with "load" in its point of interconnection, which must not match (a substation's name is not a large load).
// Then: lib/data.ts reads every field of QUEUE_SITE_FIELDS and keeps the match on the row; scripts/check-values.mjs
// reads the same fields for the dcq| keys; the page says how a site was named.
//
//   node --import ./scripts/alias-register.mjs scripts/test-queue-sites.mjs
//
// Exit 1 on a failure. No request, no browser.
import fs from "node:fs";
import { QUEUE_SITE_FIELDS, QUEUE_SITE_PATTERN, matchWords, queueSiteMatch } from "../lib/datacenter/bygrid.ts";

let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");

// the rows as the review prints them (the positions table's shape, the fields this rule reads)
const bullock = { entity_id: "ercot_queue:33INR0005", name: "Bullock Gas", operator: "Bullock Data Center, LLC", extra: { fuel_technology: "Gas - Combined-Cycle", poi: "BULLOCK 345 KV STATION (Bus# 68096)", county: "Hill", state: "TX" } };
const liberty = { entity_id: "ercot_queue:33INR0006", name: "Liberty Thermal Energy Center", operator: "Liberty Data Center I, LLC", extra: { fuel_technology: "Gas - Combined-Cycle", poi: "LIBERTY 345 KV STATION (Bus# 68092)", county: "Hill", state: "TX" } };
const byName = { entity_id: "x:1", name: "Suffern Quarry Data Center", operator: "Some Power LLC", extra: { fuel_technology: "Load" } };
const byFuel = { entity_id: "x:2", name: "Aurora Load", operator: "Some Power LLC", extra: { fuel_technology: "Large Load" } };
const solar = { entity_id: "x:3", name: "Aurelius 2", operator: "Aurelius Solar LLC", extra: { fuel_technology: "Solar - Photovoltaic Solar", poi: "LOAD 138 KV STATION" } };

check(queueSiteMatch(bullock) === "operator", "Bullock Gas is named a data center by its operator alone");
check(queueSiteMatch(liberty) === "operator", "Liberty Thermal Energy Center is named a data center by its operator alone");
check(queueSiteMatch(byName) === "name", "a position with \"Data Center\" in its name is matched by the name first");
check(queueSiteMatch(byFuel) === "extra->>fuel_technology", "a position with \"Large Load\" in its fuel field is matched by that field");
check(queueSiteMatch(solar) === null, "a solar position with \"load\" in its point of interconnection is not matched");
check(queueSiteMatch({ name: null, operator: null, extra: null }) === null && queueSiteMatch({}) === null, "empty fields match nothing");
check(queueSiteMatch({ name: "DATACENTRE CAMPUS" }) === "name" && queueSiteMatch({ operator: "Crypto Mining Inc" }) === "operator", "the match ignores case and reads every word of the pattern");
check(JSON.stringify(QUEUE_SITE_FIELDS) === JSON.stringify(["name", "extra->>fuel_technology", "operator"]), "the fields read are the name, the fuel field and the operator, in that order");
check(matchWords("operator") === "named by its operator's name" && matchWords(null) === "not matched", "the words of a match");

// the pattern is still the builder's (tests/test_session467.py holds the two equal; the rule here adds a field, not a word)
check(QUEUE_SITE_PATTERN === "data ?cent(?:er|re)s?|datacenter|large load|co-?located load|digital campus|hyperscale|crypto|bitcoin", "the pattern's words are unchanged");

// the readers use the fields
const data = read("../lib/data.ts"), cv = read("../scripts/check-values.mjs"), ps = read("../app/datacenters/PowerSide.tsx");
check(/for \(const field of QUEUE_SITE_FIELDS\)/.test(data) && /matched_by: queueSiteMatch\(r\) \?\? field/.test(data), "lib/data.ts queueSites reads every field and keeps the match on the row");
check(/for \(const field of B\.QUEUE_SITE_FIELDS\)/.test(cv) && !/byFuel/.test(cv), "check-values.mjs recomputes the dcq| keys over the same fields");
check(/data-matched-by=\{r\.extra\?\.matched_by/.test(ps) && /named a data center by its operator/.test(ps) && /datacenter_queue_positions/.test(ps), "the power side says how a site was named, and that an operator-named one joins the derived table at the data machine's next run");
for (const [name, text] of [["bygrid.ts", read("../lib/datacenter/bygrid.ts")], ["data.ts", data], ["PowerSide.tsx", ps]]) check(!/—/.test(text), `${name}: no em dash`);

console.log(`${n - bad} of ${n} passed`);
process.exit(bad ? 1 : 0);
