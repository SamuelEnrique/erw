// Energy Research Warehouse (ERW) site, session 402: the Digest's figures, their keys and the hold of 21 October
// (lib/digest.ts), and the days of its archive. Needs no build, no network and no node_modules.
//
//   node --import ./scripts/alias-register.mjs scripts/test-digest-numbers.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/digest.ts");
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const BEFORE = new Date("2026-10-20T12:00:00Z"), HELD = new Date("2026-10-21T00:00:01Z");

// a Digest of the footnote form (since 28 September 2026), as brief.py writes it
const MD = `# ERW's Energy Digest, 2026-10-20

ERW's weekday brief of energy news for the 24 hours to 2026-10-20 06:55 UTC, from 335 scored stories.

## Top of the industry

1. **A story with a $45 Billion figure** (deal)
   Its reason. Sources: [Bloomberg](https://example.com/a)

## By sector

**Power**

- A power story (datacenter power): its reason. [DCD](https://example.com/b)

**Policy**

- A policy story (policy): its reason. [Bloomberg](https://example.com/c)
- Five storage projects v. ISO New England; Notice (FERC notice, policy action): a decision on 20 October. [FERC](https://www.federalregister.gov/x)

## AI and power

- An AI story (datacenter power): its reason. [WSJ](https://example.com/d)

## ERW's Numbers Today

Day-ahead power on 2026-10-19 was dearest at NYISO's N.Y.C., 52.53 USD/MWh, and cheapest at SPP's SPPSOUTH_HUB, 21.85. The latest closes were 3.22 USD/MMBtu.

**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day):

| ISO | Hub or zone | Operating day | Average USD/MWh | Table |
|---|---|---|---|---|
| ERCOT | HB_NORTH | 2026-10-19 | 23.41 | [1] |
| NYISO | N.Y.C. | 2026-10-19 | 52.53 | [2] |
| MISO | INDIANA.HUB | 2026-10-19 | not in the warehouse (0 of 24 hours) | [1] |
| SPP | SPPSOUTH_HUB | 2026-10-19 | 21.85 | [1] |
| ISO-NE | .H.INTERNAL_HUB | 2026-10-19 | 42.50 | [3] |
| PJM | | | no PJM price table (no API key) | |

**Highest real-time price, yesterday:** 192.89 USD/MWh at N.Y.C. (NYISO), interval starting 2026-10-19 08:00 local (2026-10-19 12:00 UTC), PT15M \`lmp_rtm_15m_mean\` (a 15-minute mean of 5-minute prices) [4].

**Latest fuel spot closes** (EIA, trading dates):

- Henry Hub natural gas: 3.22 USD/MMBtu on 2026-10-14 [5]
- Brent crude: 126.55 USD/bbl on 2026-10-14 [5]

Tables: [1] \`iso_dam_hub_prices\` (caiso:PRC_LMP); [2] \`nyiso_dam_zone_prices\` (nyiso:damlbmp); [3] \`isone_dam_zone_prices\` (isone:da_lmp_hourly); [4] \`nyiso_rtm_zone_prices\` (nyiso:realtime); real-time tables read: iso_rtm_hub_prices; [5] \`eia_fuel_spot_prices\` (eia:natural-gas/pri/fut).

## ERW's Chart of the Day

![Sales in Utah: 1,658,263 MWh in July 2026. The record until now was 1,484,757 MWh.](charts/2026-10-20.png)

Sales in Utah: 1,658,263 MWh in July 2026. The record until now was 1,484,757 MWh.

Table \`eia_retail_sales_monthly\`: chosen by rule (rule: record; 1.01 robust standard deviations past its threshold).

## ERW's Fun Fact

US oil extraction peaked at 10.2 million barrels per day in 1970.

ERW

---

[How this is made.](/about#digest)
`;
const CHART = { table: "eia_retail_sales_monthly", numbers: { sigma: 171583.61, value: 1658262.63, threshold: 1484756.88, strength: 1.0112, old_record: 1484756.88 } };
const keys = (fs) => fs.map((f) => f.key);

test("every figure of the numbers section and the chart has its table and key", () => {
  const f = D.digestFigures(MD, "2026-10-20", CHART, BEFORE);
  assert.deepEqual(keys(f), [
    "digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-19", "digest_dam|NYISO|nyiso_dam_zone_prices|N.Y.C.|2026-10-19",
    "digest_dam|SPP|iso_dam_hub_prices|SPPSOUTH_HUB|2026-10-19", "digest_dam|ISO-NE|isone_dam_zone_prices|.H.INTERNAL_HUB|2026-10-19",
    "digest_rt|nyiso_rtm_zone_prices|N.Y.C.|lmp_rtm_15m_mean|2026-10-19T12:00:00Z",
    "digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-10-14", "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-10-14",
    "digest_chart|2026-10-20|eia_retail_sales_monthly|value", "digest_chart|2026-10-20|eia_retail_sales_monthly|old_record",
    "digest_chart|2026-10-20|eia_retail_sales_monthly|strength"]);
  assert.equal(f[0].raw, "23.41");
  assert.equal(f[1].entity, "nyiso:N.Y.C.");
  assert.equal(f[7].text, "1,658,263");
  assert.equal(f[7].raw, "1658262.63");
  assert.ok(f.every((x) => !x.held), "nothing is held before 21 October");
});

test("from 21 October a held grid's figure is held, the others are not", () => {
  const f = D.digestFigures(MD, "2026-10-20", CHART, HELD);
  const held = Object.fromEntries(f.map((x) => [x.key.split("|").slice(0, 3).join("|"), x.held]));
  assert.equal(held["digest_dam|ERCOT|iso_dam_hub_prices"], false);
  assert.equal(held["digest_dam|SPP|iso_dam_hub_prices"], false);
  assert.equal(held["digest_dam|NYISO|nyiso_dam_zone_prices"], true);
  assert.equal(held["digest_dam|ISO-NE|isone_dam_zone_prices"], true);
  assert.equal(held["digest_rt|nyiso_rtm_zone_prices|N.Y.C."], true);
  assert.equal(held["digest_fuel|eia_fuel_spot_prices|eia:henry_hub"], false);
  assert.ok(f.filter((x) => x.part === "chart").every((x) => !x.held));
  assert.match(f.find((x) => x.held).title, /NYISO: the publisher's own page asks for permission/);
});

test("the old form (the table in the row) and an old table name are read, and held by the table they became", () => {
  const old = `## Numbers today

Every number below is read from the warehouse.

**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day):

| ISO | Hub or zone | Operating day | Average USD/MWh | Table |
|---|---|---|---|---|
| ERCOT | HB_NORTH | 2026-09-24 | 41.60 | \`ercot_dam_hub_prices\` (ercot:NP4-190-CD) |
| MISO | INDIANA.HUB | 2026-09-24 | 38.08 | \`miso_dam_hub_prices\` (miso:da_expost_lmp) |

**Highest real-time price, yesterday:** 111.75 USD/MWh at TH_NP15_GEN-APND (CAISO), interval starting 2026-09-24 17:30 local (2026-09-25 00:30 UTC), PT15M \`lmp_rtm_15m_mean\` (a 15-minute mean of 5-minute prices); \`caiso_rtm_hub_prices\` (caiso:PRC_INTVL_LMP). Real-time tables: caiso_rtm_hub_prices.

- Henry Hub natural gas: 2.90 USD/MMBtu on 2026-09-22
- Table: \`eia_fuel_spot_prices\` (eia:natural-gas/pri/fut)

---
`;
  const f = D.digestFigures(old, "2026-09-25", null, HELD);
  assert.deepEqual(keys(f), ["digest_dam|ERCOT|ercot_dam_hub_prices|HB_NORTH|2026-09-24", "digest_dam|MISO|miso_dam_hub_prices|INDIANA.HUB|2026-09-24",
    "digest_rt|caiso_rtm_hub_prices|TH_NP15_GEN-APND|lmp_rtm_15m_mean|2026-09-25T00:30:00Z", "digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-09-22"]);
  assert.deepEqual(f.map((x) => x.held), [false, true, false, false]);   // MISO's row of iso_dam_hub_prices, which miso_dam_hub_prices became
  assert.equal(D.currentTable("miso_dam_hub_prices"), "iso_dam_hub_prices");
  assert.equal(D.currentTable("nyiso_dam_zone_prices"), "nyiso_dam_zone_prices");
});

test("the markdown carries each figure as Num draws it, and the hold's words in place of a held one", () => {
  const before = D.digestMarkdown(MD, "2026-10-20", CHART, BEFORE);
  const html = D.fillDigest(before.md, before.spans);
  assert.ok(html.includes('| <span data-check="digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-19" data-raw="23.41">23.41</span> |'), html);
  assert.ok(html.includes('<span data-check="digest_rt|nyiso_rtm_zone_prices|N.Y.C.|lmp_rtm_15m_mean|2026-10-19T12:00:00Z" data-raw="192.89">192.89</span> USD/MWh at N.Y.C.'));
  assert.ok(html.includes('Henry Hub natural gas: <span data-check="digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-10-14" data-raw="3.22">3.22</span> USD/MMBtu on'));
  // the summary's figures carry the section's keys; the picture's words are left as they are (an attribute)
  assert.ok(/N\.Y\.C\., <span data-check="digest_dam\|NYISO[^"]*" data-raw="52.53">52.53<\/span> USD\/MWh/.test(html));
  assert.ok(html.includes("![Sales in Utah: 1,658,263 MWh in July 2026."));
  assert.ok(html.includes('Sales in Utah: <span data-check="digest_chart|2026-10-20|eia_retail_sales_monthly|value" data-raw="1658262.63">1,658,263</span> MWh'));
  assert.ok(html.includes('data-check="digest_chart|2026-10-20|eia_retail_sales_monthly|old_record" data-raw="1484756.88">1,484,757</span>'), "the old record, not the threshold of the same value");
  assert.ok(html.includes("1.01</span> robust"));
  assert.ok(html.includes("A story with a $45 Billion figure"), "the stories are shown before the hold");
  assert.ok(!html.includes("license needed"));

  const held = D.digestMarkdown(MD, "2026-10-20", CHART, HELD);
  const h = D.fillDigest(held.md, held.spans);
  assert.ok(h.includes('| <span data-license-held="nyiso_dam_zone_prices" class="text-muted" title="NYISO: the publisher'), h);
  assert.ok(!h.includes('data-raw="52.53"') && !h.includes("52.53"), "NYISO's day-ahead figure is not on the page, in the table or the summary");
  assert.ok(!h.includes("192.89") && !h.includes("42.50"));
  assert.ok(h.includes('data-raw="23.41">23.41</span>') && h.includes('data-raw="21.85">21.85</span>'), "ERCOT's and SPP's stay");
  assert.ok(/<span data-license-held="nyiso_dam_zone_prices"[^>]*>license needed<\/span>: the summary of these numbers names figures of a table held since 21 October 2026\./.test(h), h);
  // the stories are held with news_index, the policy action (policy_actions) stays under its label
  assert.ok(!h.includes("$45 Billion") && !h.includes("A power story") && !h.includes("An AI story") && !h.includes("A policy story"), h);
  assert.equal((h.match(/data-license-held="news_index"/g) ?? []).length, 3);
  assert.ok(/\*\*Policy\*\*\n\n- Five storage projects v\. ISO New England; Notice \(FERC notice, policy action\)/.test(h), h);
  // what follows the closing rule is kept, the chart and the fun fact are not held
  assert.ok(h.includes("[How this is made.](/about#digest)") && h.includes("10.2 million barrels") && h.includes("1,658,263</span>"));
});

test("a chart drawn from a held table is held with its picture", () => {
  const md = MD.replace("eia_retail_sales_monthly", "nyiso_zone_load_hourly");
  const t = D.digestMarkdown(md, "2026-10-20", { ...CHART, table: "nyiso_zone_load_hourly" }, HELD);
  const h = D.fillDigest(t.md, t.spans);
  assert.ok(!h.includes("charts/2026-10-20.png") && !h.includes("1,658,263"), h);
  assert.ok(/data-license-held="nyiso_zone_load_hourly"[^>]*>license needed<\/span>: the chart of the day is drawn from `nyiso_zone_load_hourly`/.test(h));
  assert.ok(h.includes("## ERW's Fun Fact"), "the next section stays");
});

test("a key's characters are escaped in the attribute", () => {
  assert.equal(D.figureSpan({ key: 'a|"b"<c>', raw: "1", text: "1", table: "t", held: false, title: "" }), '<span data-check="a|&quot;b&quot;&lt;c&gt;" data-raw="1">1</span>');
});

test("the chart's rounding is the chart-maker's", () => {
  assert.equal(D.chartText(1658262.63), "1,658,263");
  assert.equal(D.chartText(321.5), "321.5");
  assert.equal(D.chartText(1.0112), "1.01");
  assert.equal(D.chartText(0.04567), "0.0457");
});

test("the days: a Digest, a weekend, today before it is written, a weekday without one, and outside the archive", () => {
  const have = ["2026-10-14", "2026-10-20", "2026-09-26"];
  assert.equal(D.dayKind("2026-10-20", have, "2026-10-21"), "digest");
  assert.equal(D.dayKind("2026-09-26", have, "2026-10-21"), "digest", "a Saturday that has one (the weekend issues before session 23)");
  assert.equal(D.dayKind("2026-10-18", have, "2026-10-21"), "weekend");
  assert.equal(D.dayKind("2026-10-21", have, "2026-10-21"), "pending");
  assert.equal(D.dayKind("2026-10-19", have, "2026-10-21"), "missed");
  assert.equal(D.dayKind("2026-10-22", have, "2026-10-21"), null, "after today");
  assert.equal(D.dayKind("2026-09-25", have, "2026-10-21"), null, "before the first Digest");
  assert.equal(D.dayKind("2026-13-40", have, "2026-10-21"), null);
  assert.equal(D.dayKind("x", have, "2026-10-21"), null);
  const a = D.archiveOf(have, "2026-10-21");
  assert.equal(a[0].date, "2026-10-21");
  assert.equal(a[0].kind, "pending");
  assert.equal(a[a.length - 1].date, "2026-09-26");
  assert.equal(a.length, 26, "every day from 26 September to 21 October");
  assert.deepEqual(a.filter((x) => x.kind === "digest").map((x) => x.date), ["2026-10-20", "2026-10-14", "2026-09-26"]);
  assert.equal(D.dayWords("2026-10-21"), "Wednesday 21 October 2026");
});

test("every Digest the site holds has its numbers read: a key for each figure, and none left as a bare number", () => {
  const dir = path.join(here, "..", "..", "docs", "digest");
  const files = fs.readdirSync(dir).filter((f) => /^\d{4}-\d{2}-\d{2}\.md$/.test(f));
  assert.ok(files.length >= 12);
  for (const f of files) {
    const date = f.slice(0, 10), md = fs.readFileSync(path.join(dir, f), "utf-8").replace(/\r\n/g, "\n");
    const figs = D.digestFigures(md, date, null, BEFORE);
    const parts = new Set(figs.map((x) => x.part));
    assert.ok(parts.has("dam") && parts.has("fuel"), `${f}: ${[...parts]}`);
    assert.ok(figs.filter((x) => x.part === "dam").length >= 5, `${f}: five or six grids`);
    // no figure of the numbers section is left without a key: every price-like number of its lines is wrapped
    const t = D.digestMarkdown(md, date, null, BEFORE);
    // session 418: a fuel line is "- Brent crude: 126.55 USD/bbl ...", its colon before any parenthesis; a story whose
    // headline begins "Brent crude trades at $110.30 ... (oil): ..." (21 October) is a story, not the fuels section
    const sec = t.md.split("\n").filter((l) => /^\| (ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) \|/.test(l) || l.startsWith("**Highest real-time") || /^- (Henry Hub|WTI|Brent)[^:(\[]*: /.test(l));
    assert.equal(sec.filter((l) => l.startsWith("- ")).length, 3, `${f}: the three fuel lines`);
    for (const l of sec) assert.ok(!/(?<![\dA-Z.])\d+\.\d{2}(?= |$)(?! UTC)/.test(l.replace(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}/g, "")), `${f}: a bare figure in ${l}`);
  }
});

console.log(`\n${n} tests passed`);
