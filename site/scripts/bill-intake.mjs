// Energy Research Warehouse (ERW) site, session 52: the private bill intake.
//
//   node site/scripts/bill-intake.mjs private/bills/<file>.csv [--out tests/fixtures/bills]
//
// Reads one real bill that Samuel typed or pasted into a CSV in private/bills/ (gitignored; private/bills/README.md
// gives the columns), keeps only what the bill explainer needs (the utility key, the plan type, the period, the kWh,
// each line's name and amount, and a Texas plan's energy charge) and writes a de-identified fixture to
// tests/fixtures/bills/. It never copies a name, address, account, meter or ESI ID, phone or email: columns with such
// names are dropped whole, lines whose name looks like one are dropped, and long digit runs in a line's name are removed.
// Prints what it dropped. Read the fixture before committing it. No network, no dependency.
import fs from "node:fs";
import path from "node:path";

const KEEP = ["utility", "plan_type", "period_start", "period_end", "kwh", "line", "amount", "energy_rate"];
const PERSONAL = /name|address|addr|street|city|zip|account|acct|meter|esi|premise|phone|email|customer\s*(no|number|id)|service\s*(address|location)/i;
const UTILITIES = ["CA", "SCE", "SDGE", "TX", "TXC"];

/** One CSV line, with quoted fields ("a, b" and doubled quotes). */
export function splitCsv(line) {
  const out = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) {
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch;
    } else if (ch === '"') q = true; else if (ch === ",") { out.push(cur); cur = ""; } else cur += ch;
  }
  out.push(cur);
  return out.map((s) => s.trim());
}

/** The de-identified fixture of one bill's CSV text, and what was dropped. */
export function deidentify(text, label) {
  const rows = text.split(/\r?\n/).filter((l) => l.trim() && !l.startsWith("#"));
  const head = splitCsv(rows[0]).map((h) => h.toLowerCase());
  const dropped = { columns: head.filter((h) => !KEEP.includes(h)), lines: [], scrubbed: 0 };
  const col = (r, name) => r[head.indexOf(name)] ?? "";
  const body = rows.slice(1).map(splitCsv);
  const first = body[0] ?? [];
  const utility = col(first, "utility").toUpperCase();
  if (!UTILITIES.includes(utility)) throw new Error(`utility must be one of ${UTILITIES.join(", ")}; got "${utility}"`);
  const lines = [];
  for (const r of body) {
    let name = col(r, "line");
    if (!name) continue;
    if (PERSONAL.test(name)) { dropped.lines.push("(a line whose name looks personal)"); continue; }
    const clean = name.replace(/\d{5,}/g, "").replace(/\s{2,}/g, " ").trim();
    if (clean !== name) dropped.scrubbed++;
    name = clean;
    const amount = Number(col(r, "amount").replace(/[$,]/g, "").replace(/^\((.*)\)$/, "-$1"));
    if (!Number.isFinite(amount)) throw new Error(`line "${name}": amount "${col(r, "amount")}" is not a number`);
    lines.push({ name, amount });
  }
  const kwh = Number(col(first, "kwh"));
  if (!Number.isFinite(kwh) || kwh <= 0) throw new Error("kwh must be a positive number");
  const fixture = {
    fictional: false,
    source: `private intake (site/scripts/bill-intake.mjs), de-identified; ${label}`,
    utility, plan_type: col(first, "plan_type"), period: { start: col(first, "period_start"), end: col(first, "period_end") }, kwh, lines,
  };
  const er = Number(col(first, "energy_rate"));
  if (Number.isFinite(er) && er > 0) fixture.energy_rate = er;
  return { fixture, dropped };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"))) {
  const file = process.argv[2];
  if (!file) { console.error("usage: node site/scripts/bill-intake.mjs private/bills/<file>.csv [--out dir]"); process.exit(2); }
  const out = process.argv.includes("--out") ? process.argv[process.argv.indexOf("--out") + 1] : path.join("tests", "fixtures", "bills");
  const { fixture, dropped } = deidentify(fs.readFileSync(file, "utf-8"), `entered ${new Date().toISOString().slice(0, 10)}`);
  fs.mkdirSync(out, { recursive: true });
  const n = fs.readdirSync(out).filter((f) => f.startsWith(`${fixture.utility.toLowerCase()}-${fixture.period.end}`)).length;
  const dest = path.join(out, `${fixture.utility.toLowerCase()}-${fixture.period.end || "undated"}-${n + 1}.json`);
  fs.writeFileSync(dest, JSON.stringify(fixture, null, 2) + "\n");
  console.log(`wrote ${dest}: ${fixture.lines.length} lines, ${fixture.kwh} kWh`);
  console.log(`dropped: columns [${dropped.columns.join(", ") || "none"}]; ${dropped.lines.length} personal-looking lines; ${dropped.scrubbed} line names with long digit runs scrubbed`);
  console.log("Read the fixture before committing it.");
}
