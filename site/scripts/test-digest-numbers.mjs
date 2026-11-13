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
- Energy Department closes a USD 480 million loan (DOE news release, policy action). [DOE](https://www.energy.gov/x)

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
  // session 1980 (faults file row 85): a policy action whose why line failed ends "). " and is kept too
  assert.ok(h.includes("- Energy Department closes a USD 480 million loan (DOE news release, policy action). [DOE]"), h);
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

// session 2207 (Samuel's ruling of 23 October 2026, item 7): a figure the warehouse revised after the issue was written
// is said in one line under the numbers, the issue's own figure and its key kept
test("a revised figure keeps its span and gains one note line at the end of the numbers, at the value held now", () => {
  const fuel = D.digestFigures(MD, "2026-10-20", null, BEFORE).find((f) => f.part === "fuel");
  assert.ok(fuel, "the fixture holds a fuel close");
  const t = D.digestMarkdown(MD, "2026-10-20", CHART, BEFORE, { [fuel.key]: { key: fuel.key, value: 96.34, retrieved: "2026-10-22T06:00:00Z" } });
  const html = t.spans.join("\n");
  assert.ok(html.includes(`<span data-check="${fuel.key}" data-raw="${fuel.raw}"`), "the figure's own span and key stay");
  const note = t.spans.find((x) => x.includes(`data-revised="${fuel.key}"`));
  assert.ok(note, "the note's span");
  assert.ok(note.includes('data-revised-value="96.34"') && note.includes(`data-revised-printed="${fuel.raw}"`), note);
  assert.ok(note.includes("EIA revised the") && note.includes("after this issue was written: the warehouse now holds 96.34") && note.includes(`the issue printed ${fuel.text}`), note);
  // the note's token sits in the numbers section, after its last line and before the next section
  const lines = t.md.split("\n"), from = lines.findIndex((l) => l.startsWith("## ERW's Numbers")), to = lines.findIndex((l, k) => k > from && l.startsWith("## "));
  const at = lines.findIndex((l) => l === `ERWDIGESTFIG${t.spans.indexOf(note)}Z`);
  assert.ok(at > from && (to < 0 || at < to), `the note at line ${at}, the section ${from} to ${to}`);
  // no revision given, or a value equal to the one printed, or a chart key: no note
  assert.equal(D.digestMarkdown(MD, "2026-10-20", CHART, BEFORE).spans.filter((x) => x.includes("data-revised=")).length, 0);
  assert.equal(D.digestMarkdown(MD, "2026-10-20", CHART, BEFORE, { "digest_chart|2026-10-20|x|value": { key: "x", value: 1, retrieved: null } }).spans.filter((x) => x.includes("data-revised=")).length, 0);
  // a held figure's revision is not said (its value is not shown at all)
  assert.equal(D.digestMarkdown(MD, "2026-10-20", CHART, HELD, { [fuel.key]: { key: fuel.key, value: 96.34, retrieved: null } }).spans.filter((x) => x.includes("data-revised=")).length,
    D.digestFigures(MD, "2026-10-20", null, HELD).find((f) => f.key === fuel.key).held ? 0 : 1);
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
    // session 483: only the numbers section's lines (a news line of 21 October 2026 began "- Brent crude trades at
    // $110.30", a headline's own figure, not a figure of the section); session 418: a fuel line is
    // "- Brent crude: 126.55 USD/bbl ...", its colon before any parenthesis (merged by session 429)
    const lines = t.md.split("\n"), from = lines.findIndex((l) => l.startsWith("## ERW's Numbers"));
    const to = lines.findIndex((l, k) => k > from && l.startsWith("## "));
    const sec = (from < 0 ? lines : lines.slice(from, to < 0 ? undefined : to))
      .filter((l) => /^\| (ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) \|/.test(l) || l.startsWith("**Highest real-time") || /^- (Henry Hub|WTI|Brent)[^:(\[]*: /.test(l));
    // session 804: a mover line ("- Brent crude: ... down 2.10 USD/bbl (1.7%) from ...") is not a fuel line
    assert.equal(sec.filter((l) => l.startsWith("- ") && !/, (up|down) /.test(l)).length, 3, `${f}: the three fuel lines`);
    // session 3808 (chain 216): a fuel mover line ranked among the five largest moves (2026-11-12: "- Brent crude: 92.14 USD/bbl
    // on 2026-11-11, up 1.98 USD/bbl (2.2%) from 90.16 USD/bbl ...") keys its two table figures, the newest and the previous
    // close (lib/digest.ts, session 804); its change and percent are the difference of the two, no table's figure, and are
    // set aside here as they are for a hub's mover line, which this filter never reads; and so is the table's last cell, the
    // change of the day-before column (session 804: "| 38.24 | +2.10 (+5.5%) |"), the first issue with it being 2026-11-12's
    const unchange = (l) => l.replace(/, (up|down) [\d,.]+ \S+ \([\d.]+%\) from /, ", from ").replace(/\| [+-][\d,.]+ \([+-][\d.]+%\) \|$/, "| |");
    for (const l of sec) assert.ok(!/(?<![\dA-Z.])\d+\.\d{2}(?= |$)(?! UTC)/.test(unchange(l).replace(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}/g, "")), `${f}: a bare figure in ${l}`);
  }
});

test("session 804: the day before, the movers and the demand line carry their keys", () => {
  const md = `# ERW's Energy Digest, 2026-09-28

## ERW's Numbers Today

**What moved most** (the 5 largest moves in percent):

- CAISO TH_SP15_GEN-APND day-ahead: 45.01 USD/MWh on 2026-09-27, up 4.20 USD/MWh (10.3%) from 40.81 USD/MWh on 2026-09-26 [1]. Reason, from the day's stories: Heat lifted load. ([X](https://example.org/x))
- Brent crude: 114.89 USD/bbl on 2026-09-22, down 4.77 USD/bbl (4.0%) from 119.66 USD/bbl on 2026-09-18 [2].
- Not ranked: NYISO N.Y.C. (licensed source needed); TTF, the Dutch gas benchmark (not held).

**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day, and the day before):

| ISO | Hub or zone | Operating day | Average USD/MWh | Table | Day before USD/MWh | Change |
|---|---|---|---|---|---|---|
| ERCOT | HB_NORTH | 2026-09-27 | 28.38 | [1] | 26.28 | +2.10 (+8.0%) |
| MISO | INDIANA.HUB | 2026-09-27 | not in the warehouse (0 of 24 hours) | [1] | | not computed |
| PJM | | | no PJM price table (no API key) | | | |

**Latest fuel spot closes** (EIA, trading dates; EIA publishes its closes about a week after the day):

- Brent crude: 114.89 USD/bbl on 2026-09-22 [2], EIA's newest close when this was written (6 days before this issue)

**US48 demand, yesterday:** peaked at 612,345 MW in the hour starting 2026-09-27 21:00 UTC [3]; the same weekday a year before (2025-09-28) peaked at 598,100 MW in the hour starting 2025-09-28 22:00 UTC [3], so +2.4% on the year.

Tables: [1] \`iso_dam_hub_prices\` (caiso:PRC_LMP); [2] \`eia_fuel_spot_prices\` (eia:petroleum/pri/spt); [3] \`eia930_all_demand\` (eia:electricity/rto/region-data); balancing authority us48.

ERW

---
`;
  const f = D.digestFigures(md, "2026-09-28", null, BEFORE);
  assert.deepEqual(keys(f), [
    "digest_dam|CAISO|iso_dam_hub_prices|TH_SP15_GEN-APND|2026-09-27", "digest_dam|CAISO|iso_dam_hub_prices|TH_SP15_GEN-APND|2026-09-26",
    "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-09-22", "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-09-18",
    "digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-09-27", "digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-09-26",
    "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-09-22",
    "digest_demand|eia930_all_demand|eia930:US48|demand_mw|2026-09-27T21:00:00Z", "digest_demand|eia930_all_demand|eia930:US48|demand_mw|2025-09-28T22:00:00Z"]);
  assert.equal(f[1].raw, "40.81");
  assert.equal(f[5].raw, "26.28");
  assert.equal(f[7].raw, "612345");
  assert.equal(f[7].text, "612,345");
  const page = D.digestMarkdown(md, "2026-09-28", null, BEFORE);
  const row = page.md.split("\n").find((l) => l.startsWith("| ERCOT"));
  assert.equal((row.match(/ERWDIGESTFIG\d+Z/g) || []).length, 2, "both cells of the ERCOT row carry a figure");
  const demand = page.md.split("\n").find((l) => l.startsWith("**US48 demand"));
  assert.equal((demand.match(/ERWDIGESTFIG\d+Z MW/g) || []).length, 2, "both peaks keep their unit");
});

console.log(`\n${n} tests passed`);

// session 1449 (chain 149): the source trail as a hover, and the Roundup's opening number not printed twice
test("the Tables line folds under Sources and each mark gets its table as a hover", () => {
  const html = "<p><strong>Brent crude: 128.12 USD/bbl on 2026-10-26 [1].</strong> EIA's close.</p>\n"
    + "<p>Tables: [1] <code>eia_fuel_spot_prices</code> (eia:petroleum/pri/spt); [2] <code>eia930_all_demand</code> (eia:x); balancing authority us48.</p>\n"
    + "<ul><li>US48 demand peaked at 470,627 MW in the hour starting 2026-10-25 23:00 UTC [2]; x.</li></ul>";
  const out = D.sourceTrail(html);
  assert.ok(out.includes('<details class="digest-tables"><summary>Sources</summary><p>Tables: [1] <code>eia_fuel_spot_prices</code>'));
  assert.ok(out.includes('on 2026-10-26 <abbr class="digest-mark" title="eia_fuel_spot_prices">[1]</abbr>.'));
  assert.ok(out.includes('23:00 UTC <abbr class="digest-mark" title="eia930_all_demand">[2]</abbr>;'));
  assert.equal((out.match(/<abbr/g) || []).length, 2);   // the marks inside the Tables line are not wrapped
  assert.equal(D.sourceTrail("<p>No marks here.</p>"), "<p>No marks here.</p>");
});

test("the five numbers' row that is the opening number says so", () => {
  const html = '<h2 id="the-opening-number">The opening number</h2>\n<p><strong>Brent crude closed at 120.15 USD/bbl on 2026-10-30, against 128.30 USD/bbl on 2026-10-23 (-8.15 USD/bbl, -6.3%) [5].</strong> Status: calculated.</p>\n'
    + '<h2 id="the-week-in-five-numbers">The week in five numbers</h2>\n<ul>\n<li><strong>Price move of the week:</strong> Brent crude closed at 120.15 USD/bbl on 2026-10-30, against 128.30 USD/bbl on 2026-10-23 (-8.15 USD/bbl, -6.3%) [5].</li>\n<li><strong>US48 peak demand:</strong> 500,538 MW [6].</li>\n</ul>';
  const out = D.dedupeOpening(html);
  assert.ok(out.includes("<li><strong>Price move of the week:</strong> the opening number, above.</li>"), out);
  assert.ok(out.includes("<li><strong>US48 peak demand:</strong> 500,538 MW [6].</li>"));
  assert.ok(out.includes("<p><strong>Brent crude closed at 120.15"));   // the opening itself stays
  assert.equal(D.dedupeOpening("<p>nothing</p>"), "<p>nothing</p>");
});

// session 1450 (chain 149, fault 6): the block's story rows carry a key to their story's scored field
test("a story row of the v2 block is keyed to its story", () => {
  const md = `# ERW Daily Digest, 2026-10-26

**26 October 2026.** Data through 11:45 ET, 15:45 UTC.

## The opening number

**Brent crude: 128.12 USD/bbl on 2026-10-26, down 0.18 USD/bbl (0.1%) from 128.30 USD/bbl on 2026-10-23 [1].** EIA's close.

Tables: [1] \`eia_fuel_spot_prices\` (eia:petroleum/pri/spt).

## The numbers

- **Market price.** Brent crude: 128.12 USD/bbl on 2026-10-26, down 0.18 USD/bbl (0.1%) from 128.30 USD/bbl on 2026-10-23 [1]. Status: observed.
- **Physical.** US48 demand peaked at 470,627 MW in the hour starting 2026-10-25 23:00 UTC [2]; x. Status: observed.
- **Project or capacity.** Datacenter load, Australia: 1,000 MW (Gingerah Energy; Energy-Storage.news, 2026-10-26) [3]. Change: first report, no earlier figure held. Status: the outlet's figure, not a table's.
- **Policy, capital or reliability.** Policy sum, USA: USD 1.6 trillion (EPA; EPA (.gov), 2026-10-23) [3]. Change: first report, no earlier figure held. Status: the outlet's figure, not a table's.

Tables: [1] \`eia_fuel_spot_prices\` (eia:petroleum/pri/spt); [2] \`eia930_all_demand\` (eia:x); balancing authority us48; [3] \`news_stories\`; story news:f43900b681794577 (mw); story news:ca99c1cbd4a165c7 (price).

## What moved

1. **A story** (gas)
   Why. Sources: [Outlet](https://example.com/a)

## More

### The rest of the top ten

- no further story in the top ten today
`;
  const f = D.digestFigures(md, "2026-10-26", null, BEFORE);
  const story = f.filter((x) => x.part === "story");
  assert.deepEqual(story.map((x) => [x.key, x.raw]), [["digest_story|news_stories|news:f43900b681794577|mw", "1000"], ["digest_story|news_stories|news:ca99c1cbd4a165c7|price", "1.6 trillion"]]);   // the tracer reads the digits
  assert.ok(f.some((x) => x.key === "digest_demand|eia930_all_demand|eia930:US48|demand_mw|2026-10-25T23:00:00Z"));
});

// session 1461 (chain 150, fault 41): the chart of the day drawn from its record's points, a hover on each
test("the chart is drawn with a hover on each point", () => {
  const p = { x: ["2026-04-01", "2026-05-01", "2026-06-01"], series: [{ name: "receipts", values: [100, null, 251] }], unit: "kbbl", decimals: 1 };
  const svg = D.chartSvg(p, "Receipts by tanker & barge");
  assert.ok(svg.startsWith('<svg class="digest-chart" viewBox="0 0 640 300" role="img" aria-label="Receipts by tanker &amp; barge"'), svg.slice(0, 120));
  assert.equal((svg.match(/<circle /g) || []).length, 2);   // the missing value has no point
  assert.ok(svg.includes("<title>2026-04-01: 100.0 kbbl</title>"));
  assert.ok(svg.includes("<title>2026-06-01: 251.0 kbbl</title>"));
  assert.ok(svg.includes(">251.0</text>") && svg.includes(">100.0</text>"));   // the axis: the highest and the lowest
  assert.ok(!/style=|<script/.test(svg));   // the CSP: no style attribute, no script
  const two = D.chartSvg({ x: ["a", "b"], series: [{ name: "A", values: [1, 2] }, { name: "B", values: [2, 3] }] }, "Two");
  assert.ok(two.includes("<title>B, b: 3.00</title>"));   // two series: the series' name first
  assert.ok(two.includes('stroke-dasharray="5 3"'));
  assert.equal(D.chartSvg(undefined, "x"), "");
  assert.equal(D.chartSvg({ x: [], series: [] }, "x"), "");
  assert.equal(D.chartSvg({ x: ["a"], series: [{ name: "s", values: [null] }] }, "x"), "");
});

test("a stored Roundup holds a held grid's prices (session 1989, faults file row 94)", () => {
  const md = [
    "| ISO | Hub or zone | This week USD/MWh | Week before USD/MWh | Change | Table |",
    "|---|---|---|---|---|---|",
    "| ERCOT | HB_NORTH | 33.19 | 35.02 | -1.83 | [1] |",
    "| NYISO | N.Y.C. | not in the warehouse (120 of 168 hours) | 40.90 | not computed | [2] |",
    "| ISO-NE | .H.INTERNAL_HUB | 41.10 | 40.28 | +0.82 | [3] |",
    "| Henry Hub natural gas | 2.63 USD/MMBtu on 2026-11-03 | 2.76 on 2026-10-27 | -0.13 (-4.7%) | [5] |",
  ].join("\n");
  const out = D.holdRoundupGrids(md, new Date("2026-11-13T00:00:00Z")).split("\n");
  assert.equal(out[2], "| ERCOT | HB_NORTH | 33.19 | 35.02 | -1.83 | [1] |");
  assert.equal(out[3], "| NYISO | N.Y.C. | not in the warehouse (120 of 168 hours) | license needed | not computed | [2] |");
  assert.equal(out[4], "| ISO-NE | .H.INTERNAL_HUB | license needed | license needed | license needed | [3] |");
  assert.equal(out[5], "| Henry Hub natural gas | 2.63 USD/MMBtu on 2026-11-03 | 2.76 on 2026-10-27 | -0.13 (-4.7%) | [5] |");
  assert.equal(D.holdRoundupGrids(md, new Date("2026-10-01T00:00:00Z")), md);   // before the hold began
});

console.log(`${n} passed`);
