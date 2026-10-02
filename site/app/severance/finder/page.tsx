import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { Section } from "@/components/Section";
import { RULE_NAMES, readSummary, tokenOk, type Totals } from "@/lib/finder";

// Session 57: the Texas severance refund finder, internal. For a severance tax consultant who today pulls well data
// from a vendor and works it by hand: which leases may be paying more severance tax than the rules require, and how much
// might they save. Every Texas lease in the Railroad Commission's dump, tested month by month on the three rules the
// data can test (warehouse/derived/severance_screen.py). The data is internal, so the page reads the finder's outputs
// from the warehouse's output directory and answers 404 without the internal token, as /severance/lease/real does.
export const metadata: Metadata = { title: "Internal: the refund finder", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const usd = (v: number) => `$${Math.round(v).toLocaleString("en-US")}`;
const n0 = (v: number) => v.toLocaleString("en-US");
const title = (s: string) => s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

function Row({ label, t, extra }: { label: React.ReactNode; t: Totals; extra?: React.ReactNode }) {
  return (
    <tr className="border-b border-rule">
      <td className="py-1 pr-3">{label}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{n0(t.leases)}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{n0(t.months)}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{usd(t.base_tax)}</td>
      <td className="py-1 pr-3 text-right tabular-nums font-semibold">{usd(t.savings)}</td>
      {extra}
    </tr>
  );
}
const Head = ({ first, extra }: { first: string; extra?: React.ReactNode }) => (
  <thead>
    <tr className="border-b border-ink text-left text-xs text-muted">
      <th className="py-1 pr-3">{first}</th>
      <th className="py-1 pr-3 text-right">Leases flagged</th>
      <th className="py-1 pr-3 text-right">Lease-months</th>
      <th className="py-1 pr-3 text-right">Tax at the base rate, those months</th>
      <th className="py-1 pr-3 text-right">Potential saving</th>
      {extra}
    </tr>
  </thead>
);

export default async function Finder({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  if (!tokenOk(token)) notFound();
  const s = readSummary();
  const q = `token=${encodeURIComponent(token)}`;
  const head = (
    <>
      <p className="mb-1 text-sm"><Link href="/severance" prefetch={false}>Severance tax</Link> / the refund finder</p>
      <p className="mb-2 text-xs uppercase tracking-wide text-accent">Internal: not for circulation. The RRC data here is internal.</p>
      <h1 className="mb-1 text-3xl">The refund finder</h1>
    </>
  );
  if (!s) {
    return (
      <>
        {head}
        <p className="max-w-3xl text-sm">
          The finder&apos;s outputs are not on this server. They are built on a warehouse machine by <code className="font-mono">warehouse/derived/severance_screen.py</code>{" "}
          and kept out of git and the public database; run the site there (or set <code className="font-mono">ERW_OUTPUT_DIR</code>) to use this page.
        </p>
      </>
    );
  }
  const open = (l: { lease_id: string; county: string }) => `/severance/lease/real?${q}&src=statewide&county=${encodeURIComponent(l.county)}&lease=${encodeURIComponent(l.lease_id)}`;
  const rules = Object.keys(s.by_rule).sort();
  return (
    <>
      {head}
      <div className="mb-5 max-w-3xl space-y-2 text-sm">
        <p>
          Which Texas leases may be paying more severance tax than the rules require, and how much might they save? Every lease in the Railroad
          Commission&apos;s production dump ({n0(s.leases_screened)} leases in {s.counties} counties), tested month by month from {s.window[0]} to {s.window[1]} on the
          three rules its data can test. <strong>A flag means a lease may qualify, never that it qualifies:</strong> each states the test the data meets and what
          the data cannot see. Not tax advice.
        </p>
        <p className="text-muted">
          Built {s.built} from the dump of {s.dump.oil_extract} (oil) and {s.dump.gas_extract} (gas); rules file version {s.rules_version}.{" "}
          <a href={`/severance/finder/download?${q}`}>Download every flag (CSV)</a>.
        </p>
      </div>

      <Section title="Statewide">
        <div className="mb-3 grid gap-3 sm:grid-cols-3">
          <div className="border border-rule bg-panel p-3"><div className="text-xs text-muted">Leases flagged</div><div className="text-2xl tabular-nums">{n0(s.total.leases)}</div></div>
          <div className="border border-rule bg-panel p-3"><div className="text-xs text-muted">With a potential saving</div><div className="text-2xl tabular-nums">{n0(s.total.with_savings)}</div></div>
          <div className="border border-rule bg-panel p-3"><div className="text-xs text-muted">Potential saving, {s.window[0]} to {s.window[1]}</div><div className="text-2xl tabular-nums">{usd(s.total.savings)}</div></div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <Head first="Rule" extra={<th className="py-1 pr-3">Source</th>} />
            <tbody>
              {rules.map((r) => {
                const c = r === "tx_inactive" ? s.cites.tx_inactive_oil : s.cites[r];
                return <Row key={r} label={RULE_NAMES[r] ?? r} t={s.by_rule[r]} extra={<td className="py-1 pr-3 text-xs">{c ? <><a href={c.source.url}>{c.source.title}</a>{c.code ? `; ${c.code.section}` : ""}</> : null}</td>} />;
              })}
            </tbody>
          </table>
        </div>
        {s.by_case ? (
          <p className="mt-2 max-w-3xl text-xs text-muted">
            Two-year inactive wells: {Object.entries(s.by_case).map(([k, t]) => `${n0(t.leases)} ${k === "seen" ? "with the production before the gap in the months read (saving estimated)" : "older leases whose production before the gap is not read (no saving estimated)"}`).join("; ")}.
          </p>
        ) : null}
      </Section>

      <Section title="By county">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <Head first="County" />
            <tbody>{s.by_county.slice(0, 25).map((c) => <Row key={c.county} label={title(c.county)} t={c} />)}</tbody>
          </table>
        </div>
        <details className="mt-2 text-sm">
          <summary className="cursor-pointer">Every county ({s.by_county.length})</summary>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <Head first="County" />
              <tbody>{s.by_county.map((c) => <Row key={c.county} label={title(c.county)} t={c} />)}</tbody>
            </table>
          </div>
        </details>
      </Section>

      <Section title="By operator: the top 50">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <Head first="Operator" />
            <tbody>{s.by_operator.map((o) => <Row key={o.operator_no} label={`${o.operator_name} (${o.operator_no})`} t={o} />)}</tbody>
          </table>
        </div>
      </Section>

      <Section title="The largest leases">
        <p className="mb-2 max-w-3xl text-sm">Open a lease to see its months in the lease tool, with each rule&apos;s test and flag.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink text-left text-xs text-muted">
                <th className="py-1 pr-3">Lease</th><th className="py-1 pr-3">Operator</th><th className="py-1 pr-3">County</th><th className="py-1 pr-3">Rules</th>
                <th className="py-1 pr-3 text-right">Potential saving</th>
              </tr>
            </thead>
            <tbody>
              {s.top_leases.slice(0, 50).map((l) => (
                <tr key={l.lease_id} className="border-b border-rule">
                  <td className="py-1 pr-3"><Link href={open(l)} prefetch={false}>{l.lease_name}</Link> <span className="font-mono text-xs text-muted">{l.lease_id}</span></td>
                  <td className="py-1 pr-3">{l.operator_name}</td>
                  <td className="py-1 pr-3">{title(l.county)}</td>
                  <td className="py-1 pr-3 text-xs">{l.rules.split(";").map((r) => RULE_NAMES[r]?.split(" (")[0] ?? r).join("; ")}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">{usd(l.savings)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* a GET form on this internal page only */}
        <form method="get" action="/severance/lease/real" className="mt-3 flex flex-wrap items-end gap-3 text-sm">
          <input type="hidden" name="token" value={token} />
          <input type="hidden" name="src" value="statewide" />
          <label className="flex flex-col">County<input name="county" className="border border-rule bg-panel px-2 py-1" placeholder="MARTIN" /></label>
          <label className="flex flex-col">Lease id<input name="lease" className="border border-rule bg-panel px-2 py-1 font-mono" placeholder="O-08-12345" /></label>
          <button type="submit" className="border border-accent px-3 py-1 text-accent">Open any lease</button>
        </form>
      </Section>

      <Section title="Method">
        <div className="max-w-3xl space-y-2 border border-rule bg-panel p-3 text-sm">
          <p>
            <strong>The data.</strong> The Railroad Commission of Texas&apos;s Production Data Query dump, table OG_COUNTY_LEASE_CYCLE: each lease&apos;s
            production by county and month, as its operator reported it, read county by county. The RRC reports leases, not wells; a gas lease is one gas
            well. Wells per lease: OG_WELL_COMPLETION, at the extract. Recent months may be incomplete: operators file late.
          </p>
          <p><strong>The tests</strong>, each the lease tool&apos;s, with the rules and citations of the rules file:</p>
          <ul className="list-disc pl-6">
            <li><strong>Low-producing oil lease:</strong> the lease&apos;s oil averages under 15 barrels per well per day over the months of the 90 days ending with the month,
              divided by the wells listed and not shut in. The credit is set by the Comptroller&apos;s certified price for the month: every certified price held for
              this window is over $30 (2005 dollars), so no credit, and months with no certified price in the rules file get none either.</li>
            <li><strong>Low-producing gas well:</strong> a gas well averaging 90 Mcf a day or less over the three months before (the months with a filed report); the
              certified price sets the credit (100 percent for every month the rules file holds in this window; none where it holds no price).</li>
            <li><strong>Two-year inactive well:</strong> a lease producing again after 24 months or more without production, having produced before. When its
              production before the gap is in the 48 months read, the saving is estimated on at most its average producing month of the 12 before the gap (a
              returning well, not new wells on the lease); when the gap runs back past them and the RRC&apos;s first month for the lease is older, it is flagged with
              no saving estimated. New leases are not flagged.</li>
          </ul>
          <p><strong>Money.</strong> {s.prices} Tax at the base rate (4.6 percent of value for oil and condensate, 7.5 percent for gas) against the tax with the credit or exemption.</p>
          <p><strong>What a flag cannot see:</strong></p>
          <ul className="list-disc pl-6">
            {Object.entries(s.not_seen).map(([r, xs]) => <li key={r}><strong>{RULE_NAMES[r]?.split(" (")[0] ?? r}:</strong> {xs.join("; ")}.</li>)}
          </ul>
          <p className="text-muted">An estimate for screening, not tax advice. The method in full: the finder&apos;s source, warehouse/derived/severance_screen.py.</p>
        </div>
      </Section>
    </>
  );
}
