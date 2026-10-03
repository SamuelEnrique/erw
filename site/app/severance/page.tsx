import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { Section } from "@/components/Section";
import rulesJson from "@/data/severance_rules.json";
import { series } from "@/lib/data";
import type { Rules } from "@/lib/severance";
import { attempt } from "@/lib/supabase";
import { Calculator } from "./Calculator";

// Session 40: severance tax engine v0 (Texas, Louisiana, New Mexico). The rules live in data/severance_rules.json, each
// citing the statute or agency page whose text states it (docs/methods/severance.md); the default prices are the
// warehouse's EIA spot prices. An estimate for education and planning, not tax advice.
export const metadata: Metadata = { title: "Severance tax calculator" };
export const revalidate = 3600;

const rules = rulesJson as unknown as Rules;
const T = "eia_fuel_spot_prices";

/** The mean of the latest complete calendar month of an EIA daily spot series (a month is complete once a later
 * month's first day is held). */
async function monthMean(entity: string): Promise<{ value: number; month: string; n: number } | null> {
  const since = new Date(Date.now() - 75 * 86_400_000).toISOString().slice(0, 10) + "T00:00:00Z";
  const rows = await series(T, { entity, variable: "spot_price", since });
  if (!rows.length) return null;
  const last = rows.map((r) => r.ts_utc.slice(0, 7)).sort().pop()!;
  const months = [...new Set(rows.map((r) => r.ts_utc.slice(0, 7)))].sort().filter((m) => m < last);
  const m = months.pop();
  if (!m) return null;
  const xs = rows.filter((r) => r.ts_utc.startsWith(m)).map((r) => r.value);
  return { value: Math.round((xs.reduce((a, b) => a + b, 0) / xs.length) * 100) / 100, month: m, n: xs.length };
}

export default async function Severance() {
  const [wti, hh] = await Promise.all([attempt(() => monthMean("eia:wti_cushing")), attempt(() => monthMean("eia:henry_hub"))]);
  const w = wti.ok ? wti.data : null, h = hh.ok ? hh.data : null;
  const prices = {
    oil: w?.value ?? null, gas: h?.value ?? null,
    label: {
      oil: w ? `WTI Cushing, the mean of ${w.n} daily EIA spot prices in ${w.month}, $${w.value.toFixed(2)} per barrel` : "not held: enter a price",
      gas: h ? `Henry Hub, the mean of ${h.n} daily EIA spot prices in ${h.month}, $${h.value.toFixed(2)} per MMBtu, applied per Mcf as if one Mcf held one MMBtu` : "not held: enter a price",
    },
  };
  return (
    <>
      <h1 className="mb-1 text-3xl">Severance tax calculator: Texas, Louisiana, New Mexico</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <p className="mb-2">
          What a month of oil, gas or condensate owes in state production taxes at the base rate, what it owes with the reduced rates and exemptions a
          well may qualify for, and the difference. Every rate, exemption and threshold cites the statute or state agency page whose text states it.
        </p>
        <p className="border-l-2 border-accent pl-2 text-muted">
          <strong>An estimate for education and planning, not tax advice.</strong> Deductions such as marketing costs vary by state: they are listed, and
          computed only where the state&apos;s rule states them (Louisiana&apos;s transport charges on oil, New Mexico&apos;s royalties and trucking). New Mexico&apos;s
          rates are the Taxation and Revenue Department&apos;s latest published table, for April to August 2026. Local taxes, county levies and
          federal royalties are not here. <Link href="/data/methods/severance">Method</Link>.
        </p>
        <p className="mt-2">
          <strong>A whole lease?</strong> <Link href="/severance/lease">The lease tool</Link> takes a CSV of every well&apos;s monthly production, computes
          each well and month, and flags the reduced rates each well&apos;s numbers may qualify for. Your file is read in your browser and never sent.
        </p>
      </div>
      <Section title="Calculator">
        <Calculator rules={rules} prices={prices} />
        <Cite tables={[T]} note="Default prices only: EIA daily spot prices (WTI Cushing, Henry Hub). The tax rules are site/data/severance_rules.json, each with its statute or agency citation" />
        <p className="text-xs text-muted">Rules version {rules.version}.</p>
      </Section>
      <Section title="Every rule, with its source">
        {Object.entries(rules.states).map(([k, st]) => (
          <div key={k} className="mb-4">
            <h3 className="mb-1 text-base">{st.name}</h3>
            <ul className="space-y-1 text-sm">
              {Object.entries(st.products).flatMap(([p, pr]) => [
                ...pr.base.map((b) => (
                  <li key={b.id}>
                    <strong>{p}, {b.name}:</strong>{" "}
                    {typeof b.rate === "number" ? (b.basis === "per_unit" ? `$${b.rate} per ${pr.unit}` : `${(b.rate * 100).toLocaleString("en-US", { maximumFractionDigits: 4 })}% of value`)
                      : b.rate === "variant" ? pr.variants!.map((v) => `${(v.rate * 100).toLocaleString("en-US")}% (${v.label.toLowerCase()})`).join("; ")
                      : b.rate === "choice" ? b.choices!.map((c) => c.label).join("; ") : "your production unit's rate (by county, district and suffix)"}
                    {b.effective ? `; effective ${b.effective}` : ""}. <a href={rules.sources[b.cite].url}>{rules.sources[b.cite].title}</a>
                    {b.code ? <>; <a href={rules.sources[b.code.cite].url}>{b.code.section}</a></> : null}
                  </li>
                )),
                ...pr.options.map((o) => (
                  <li key={o.id} className="text-muted">
                    {p}, {o.name}: {o.what}.{o.how_long ? ` ${o.how_long}.` : ""} <a href={rules.sources[o.cite].url}>{rules.sources[o.cite].title}</a>
                    {o.code ? <>; <a href={rules.sources[o.code.cite].url}>{o.code.section}</a></> : null}
                    {o.certified ? <> Latest certified price: ${o.certified.prices[0].price} for {o.certified.as_of} (2005 dollars).</> : null}
                  </li>
                )),
                ...pr.fees.map((f) => (
                  <li key={f.id} className="text-muted">{p}, {f.name}: ${f.per_unit} per {pr.unit}{f.effective ? ` (${f.effective})` : ""}. <a href={rules.sources[f.cite].url}>{rules.sources[f.cite].title}</a></li>
                )),
              ])}
            </ul>
          </div>
        ))}
      </Section>
    </>
  );
}
