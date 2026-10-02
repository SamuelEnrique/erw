import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import rules from "@/data/bill_rules.json";
import { BILL_KEYS, defaultBill, type BillKey } from "@/lib/bill";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { BillCalc } from "./BillCalc";

// Session 43: electricity bill explainer v0, for learning. Two bills (PG&E E-TOU-C in California, a home in Oncor's
// area of ERCOT); session 52 adds three (SCE TOU-D-4-9PM, SDG&E TOU-DR1, a home in CenterPoint's area of Houston), every rate from data/bill_rules.json with its tariff passage; the wholesale share from
// cost_of_power_monthly (derived, docs/methods/cost_of_power.md). The defaults are computed here, on the server, and
// checked by scripts/check-values.mjs (keys bill|...).
export const metadata: Metadata = { title: "What is on an electricity bill" };
export const revalidate = 3600;

const M = "cost_of_power_monthly";

function Chip() {
  return (
    <Link href="/data/standard" title="Text written for this site, with its sources named; not data" className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      written, cited
    </Link>
  );
}

/** The load-weighted real-time price of the latest complete month, else the latest month held (partial). */
async function wholesaleOf(entity: string): Promise<{ row: SeriesRow; partial: boolean } | null> {
  const rows = await series(M, { entity });
  const by = new Map<string, Record<string, SeriesRow>>();
  for (const r of rows) (by.get(r.ts_utc.slice(0, 7)) ?? by.set(r.ts_utc.slice(0, 7), {}).get(r.ts_utc.slice(0, 7))!)[r.variable] = r;
  const months = [...by.keys()].filter((m) => by.get(m)!.rt_load_weighted).sort();
  const full = months.filter((m) => by.get(m)!.rt_hours?.value === by.get(m)!.hours_in_month?.value);
  const m = full.at(-1) ?? months.at(-1);
  return m ? { row: by.get(m)!.rt_load_weighted, partial: !full.includes(m) } : null;
}

const GLOSSARY: [string, string, string][] = [
  ["Kilowatt-hour (kWh)", "The unit a bill counts: a thousand watts used for an hour. Both tariffs charge by it.", "PG&E E-TOU-C; Oncor Tariff for Retail Delivery Service"],
  ["Time of use", "A rate that costs more in some hours. On E-TOU-C the peak is 4 to 9 p.m. every day.", "PG&E E-TOU-C, Sheet 5"],
  ["Baseline allowance", "A daily amount of use, set by climate zone and season, that earns a credit; use above it pays more.", "PG&E E-TOU-C, Sheets 2 and 5"],
  ["Base services charge", "PG&E's fixed daily charge, set by household income, whose revenue lowers the per-kWh rates.", "PG&E E-TOU-C, Sheets 1 and 2"],
  ["Generation", "The cost of making or buying the electricity itself.", "PG&E E-TOU-C, Sheet 3"],
  ["Transmission", "The high-voltage lines that move power from plants to cities, shared across a grid.", "PG&E E-TOU-C, Sheet 3; Oncor Rider TCRF"],
  ["Distribution", "The local wires, poles and transformers that reach each home.", "PG&E E-TOU-C, Sheet 3; Oncor Residential Service"],
  ["Retail electric provider", "In most of ERCOT, the company that sells the power and sends the bill; the customer chooses it.", "Oncor Tariff for Retail Delivery Service (Competitive Retailer)"],
  ["Rider", "A separate charge added to a tariff to recover one cost, such as transmission or a rate case.", "Oncor Tariff, Riders TCRF, EECRF, DCRF, RCE, MG, IS"],
  ["Wholesale price", "What power costs between generators and buyers on the grid, before wires and programs: the ERW's cost of power.", "ERW, docs/methods/cost_of_power.md"],
];

export default async function LearnBill() {
  // session 52: five bills; each wholesale reference is its ISO zone's (two bills may share one)
  const ents = [...new Set(BILL_KEYS.map((k) => rules.bills[k].wholesale_entity as string))];
  const got = await Promise.all(ents.map((e) => attempt(() => wholesaleOf(e))));
  const byEnt = Object.fromEntries(ents.map((e, i) => [e, got[i].ok ? got[i].data : null]));
  const W = Object.fromEntries(BILL_KEYS.map((k) => [k, byEnt[rules.bills[k].wholesale_entity]])) as Record<BillKey, Awaited<ReturnType<typeof wholesaleOf>>>;
  const bills = Object.fromEntries(BILL_KEYS.map((k) => [k, defaultBill(rules, k)])) as Record<BillKey, ReturnType<typeof defaultBill>>;
  const wholesale = Object.fromEntries(BILL_KEYS.map((s) => [s, W[s] ? { price: W[s]!.row.value, month: W[s]!.row.ts_utc.slice(0, 7), partial: W[s]!.partial } : null]));
  const note: Record<BillKey, string> = {
    CA: "Summer, 20 percent in peak hours, territory T (San Francisco), Income Tier 3, 30 days.",
    SCE: "Winter (the season on 2026-10-01), 20 percent from 4 to 9 p.m., a third in 8 a.m. to 4 p.m., Baseline Region 9, 30 days.",
    SDGE: "Summer, 20 percent from 4 to 9 p.m., 34.5 percent in super off-peak hours, 30 days; no baseline credit until you enter your allowance.",
    TX: `Energy charge $${rules.bills.TX.energy_default.rate} per kWh (the labelled default).`,
    TXC: `Energy charge $${rules.bills.TXC.energy_default.rate} per kWh (the labelled default).`,
  };
  return (
    <>
      <h1 className="mb-1 text-3xl">What is on an electricity bill</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <p className="mb-2">
          A home&apos;s electricity bill pays for much more than the power itself: the wires and poles on the street, the high-voltage grid, meters,
          state programs and credits. This page builds five real bills line by line from the utilities&apos; own tariffs, a PG&amp;E, an SCE and an SDG&amp;E
          home in California and a home in Oncor&apos;s and in CenterPoint&apos;s area of Texas, then shows how much of each is the wholesale price of energy. <Chip />
        </p>
        <p className="text-muted">
          For learning, not a bill: the rates are the tariffs&apos; as read on 2026-09-30 (PG&amp;E, Oncor) and 2026-10-01 (SCE, SDG&amp;E, CenterPoint), taxes and local fees are not included, and your usage and plan
          differ. Wholesale prices: <Link href="/cost-of-power">cost of power</Link>. The grids: <Link href="/grid/caiso">CAISO</Link>, <Link href="/grid/ercot">ERCOT</Link>.
        </p>
      </div>

      <Section title="The default bills (600 kWh a month, an assumption)">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {BILL_KEYS.map((s) => {
            const w = W[s];
            const wUsd = w ? (bills[s].kwh * w.row.value) / 1000 : null;
            return (
              <div key={s} className="border border-rule bg-panel p-3 text-sm">
                <p className="font-semibold">{rules.bills[s].name}</p>
                <p>Total: <strong><Num check={`bill|${s}|total`} raw={bills[s].total}>{shown(bills[s].total)}</Num></strong> USD for {bills[s].kwh} kWh.</p>
                {w && wUsd !== null ? (
                  <p>
                    Wholesale energy: <Num check={`bill|${s}|wholesale|${w.row.ts_utc}`} raw={wUsd}>{shown(wUsd)}</Num> USD, <Num check={`bill|${s}|share|${w.row.ts_utc}`} raw={(wUsd / bills[s].total) * 100}>{shown((wUsd / bills[s].total) * 100)}</Num> percent
                    of the bill, at <Num check={`series|${M}|${w.row.entity}|${w.row.variable}|${w.row.ts_utc}`} raw={w.row.value}>{shown(w.row.value)}</Num> USD/MWh ({w.row.ts_utc.slice(0, 7)}{w.partial ? ", a partial month" : ""}).
                  </p>
                ) : <p className="text-muted">The wholesale price is not held.</p>}
                <p className="text-xs text-muted">{note[s]}</p>
              </div>
            );
          })}
        </div>
        <Cite tables={[M]} note="Bills: site/data/bill_rules.json, each rate with its tariff passage (PG&E Electric Schedule E-TOU-C; SCE Schedule TOU-D; SDG&E Schedule TOU-DR1; Oncor and CenterPoint Tariffs for Retail Delivery Service). Wholesale: the load-weighted real-time price of the ISO's zone" />
      </Section>

      <Section title="Build a bill">
        <BillCalc rules={rules} wholesale={wholesale} />
        <p className="mt-3 max-w-3xl text-sm">
          What is the rest? Each line of the bill above names it, in the utility&apos;s own tariff: the local wires, poles and transformers
          (distribution), the high-voltage grid (transmission), the meter and fixed charges, and programs the state funds through the bill, such as
          public purpose programs, energy efficiency and, in California, wildfire charges. Open a line to read what it is, why it exists and the tariff
          passage behind its rate. <Chip />
        </p>
      </Section>

      <Section title="Ten terms" aside={<Chip />}>
        <dl className="grid gap-x-6 gap-y-2 text-sm md:grid-cols-2">
          {GLOSSARY.map(([t, d, s]) => (
            <div key={t}><dt className="font-semibold">{t}</dt><dd>{d} <span className="text-xs text-muted">({s})</span></dd></div>
          ))}
        </dl>
      </Section>
    </>
  );
}
