import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { Section } from "@/components/Section";
import rulesJson from "@/data/severance_rules.json";
import { series } from "@/lib/data";
import type { PriceBook, PricePoint } from "@/lib/lease";
import type { Rules } from "@/lib/severance";
import { attempt } from "@/lib/supabase";
import { LeaseTool } from "./LeaseTool";

// Session 45: severance v0.2, the lease tool. The reader's lease file is parsed and taxed in the browser (LeaseTool,
// lib/lease.ts, lib/severance.ts) and never sent to the server; the server sends only the rules and the monthly means of
// the warehouse's EIA daily spot prices, the default prices. An estimate for education and planning, not tax advice.
// Session 46: every link on this page is prefetch={false}, and the shared ones (components/SiteLink) turn prefetch off
// here, so no request fires after a file is loaded.
export const metadata: Metadata = { title: "Severance tax: the lease tool" };
export const revalidate = 3600;

const rules = rulesJson as unknown as Rules;
const T = "eia_fuel_spot_prices";
const SINCE = "2023-01-01T00:00:00Z";

/** The mean of each calendar month of an EIA daily spot series since 2023; the latest month is labeled as partial. */
async function monthMeans(entity: string, name: string, unit: string, per: string): Promise<Record<string, PricePoint>> {
  const rows = await series(T, { entity, variable: "spot_price", since: SINCE });
  const by = new Map<string, number[]>();
  for (const r of rows) {
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, []);
    by.get(m)!.push(r.value);
  }
  const months = [...by.keys()].sort();
  const last = months[months.length - 1];
  const out: Record<string, PricePoint> = {};
  for (const m of months) {
    const xs = by.get(m)!;
    const value = Math.round((xs.reduce((a, b) => a + b, 0) / xs.length) * 100) / 100;
    out[m] = {
      value, n: xs.length,
      label: `${name}, the mean of ${xs.length} daily EIA spot prices in ${m}${m === last ? " (the latest month held, possibly partial)" : ""}, $${value.toFixed(2)} ${unit}${per}`,
    };
  }
  return out;
}

export default async function LeasePage() {
  const [wti, hh] = await Promise.all([
    attempt(() => monthMeans("eia:wti_cushing", "WTI Cushing", "per barrel", "")),
    attempt(() => monthMeans("eia:henry_hub", "Henry Hub", "per MMBtu", ", applied per Mcf as if one Mcf held one MMBtu")),
  ]);
  const prices: PriceBook = { oil: wti.ok ? wti.data : {}, gas: hh.ok ? hh.data : {} };
  const span = (b: Record<string, PricePoint>) => {
    const ks = Object.keys(b).sort();
    return ks.length ? `${ks[0]} to ${ks[ks.length - 1]}` : "none held (enter prices in the file)";
  };
  return (
    <>
      <p className="mb-1 text-sm"><Link href="/severance" prefetch={false}>Severance tax calculator</Link> / the lease tool</p>
      <h1 className="mb-1 text-3xl">Severance tax for a lease: every well, every month</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <p className="mb-2">
          Drop a CSV of your wells&apos; monthly production, or paste the rows. For each well and month the tool computes the state production tax at
          the base rate and with the reduced rates you tick, and flags each rule whose thresholds the well&apos;s own numbers meet, with the statute or
          agency page that states it. Texas, Louisiana and New Mexico, on the same cited rules as the <Link href="/severance" prefetch={false}>calculator</Link>.
        </p>
        <p className="mb-2 border-l-2 border-accent pl-2">
          <strong>Your file stays on your computer.</strong> It is read and computed in this browser tab. Nothing in it is sent to this site&apos;s server
          or anywhere else, and nothing is stored: close the tab and it is gone. The results download is made in the browser too.
        </p>
        <p className="border-l-2 border-accent pl-2 text-muted">
          <strong>An estimate for education and planning, not tax advice.</strong> A &quot;may qualify&quot; flag means the numbers in your file meet the
          rule&apos;s thresholds; the state still has to certify or designate the well, and some tests (payout, pressure, the Railroad Commission&apos;s
          designation) are not in the file. <Link href="/data/methods/severance" prefetch={false}>Method</Link>.
        </p>
      </div>
      <Section title="Your lease">
        <LeaseTool rules={rules} prices={prices} />
        <Cite tables={[T]} note={`Default prices only: monthly means of EIA daily spot prices, WTI Cushing (oil, condensate; ${span(prices.oil)}) and Henry Hub (gas; ${span(prices.gas)}). The tax rules are site/data/severance_rules.json, each with its statute or agency citation`} />
        <p className="text-xs text-muted">Rules version {rules.version}.</p>
      </Section>
    </>
  );
}
