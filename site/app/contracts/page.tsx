import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { attempt } from "@/lib/supabase";
import { PRODUCTS, TABLE, byBa, choices, counts, fercDate, filedQuarter, filter, listed, quarterDates, quarters, rateText, termYears, type Contract } from "@/lib/contracts";
import { contractRows, contractSummary } from "./read";

// Session 83: "Where power contracts are being struck". A credit investor asked where bilateral power contracts are
// being signed; FERC's Electric Quarterly Reports hold them (scoped in session 81). The rows are ferc_eqr_contracts, an
// internal table, read through two database functions that answer only with the internal token (./read.ts). The page
// lists the contract rows executed in a chosen quarter: seller, buyer, product, term, quantity, price as filed, and
// delivery point. It counts the rows it shows and does no other arithmetic. In review (lib/release.ts), and it stays
// behind the internal view: the table is internal. The panel's links point at this same page: plain next/link.
export const metadata: Metadata = { title: "Where power contracts are being struck", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const SHOWN = 400;
const count = (v: number) => v.toLocaleString("en-US");

function Limits({ rows, priced }: { rows: number | null; priced: number | null }) {
  return (
    <ul className="max-w-3xl list-disc space-y-1.5 pl-5 text-sm" data-limits="3">
      <li><strong>No column says what technology a contract is for.</strong> Solar, wind or storage can be read only from a seller&apos;s name; a utility or a marketer selling from a portfolio says nothing about the source.</li>
      <li><strong>About half the rows give their price as words, not a number.</strong>{rows !== null && priced !== null ? <> Of the {count(rows)} rows held
        here, <span data-n="unpriced">{count(rows - priced)}</span> do.</> : null} &quot;Market Based Rate&quot; or a formula is what the filer wrote; the column below shows it as filed and never fills one in.</li>
      <li><strong>Every agreement in force is filed again each quarter.</strong> A contract here is new because its execution date is recent, not because it appears in this filing. One agreement is one row per product, so it can have several rows.</li>
    </ul>
  );
}

export default async function Contracts({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const summary = await attempt(contractSummary);
  const every = summary.ok ? quarters(summary.data) : [];
  const { upTo: held, laterRows, laterLast } = listed(every, summary.ok ? filedQuarter(summary.data) : null);
  const { quarter, product, ba } = choices(q, held.map((h) => h.quarter));
  const read = quarter ? await attempt(() => { const d = quarterDates(quarter); return contractRows(d.from, d.to); }) : null;
  const all: Contract[] = read?.ok ? read.data : [];
  const rows = filter(all, product, ba);
  const c = counts(rows);
  const bas = byBa(filter(all, product, null));
  const ercot = summary.ok ? summary.data.by_ba.find((b) => b.ba === "ERCO")?.rows ?? 0 : 0;
  const href = (qq: string, p: string, b?: string | null) => `/contracts?q=${qq}&product=${p}${b ? `&ba=${encodeURIComponent(b)}` : ""}`;
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  return (
    <ToolPage>
      <ToolHeader title="Where power contracts are being struck"
        lead={<>Sellers of wholesale power file their contracts with the Federal Energy Regulatory Commission every quarter: who sells to whom, which product,
          for how long, at what price and delivered where. This lists the contracts by the quarter they were signed. It hardly covers Texas: sales inside
          ERCOT are outside the Commission&apos;s jurisdiction. See also <SiteLink href="/deals">deals from the news</SiteLink>.</>} />
      <div className="mb-8 border-l-2 border-accent bg-paper px-4 py-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">Three limits of this record</div>
        <Limits rows={summary.ok ? summary.data.rows : null} priced={summary.ok ? summary.data.priced : null} />
      </div>
      {!summary.ok || !quarter ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-contracts="unavailable">
          The contract table is internal and is read only with this server&apos;s internal token: {summary.ok ? "it holds no row yet" : summary.reason}.
        </p>
      ) : (
        <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Choose" note={`Filed for ${summary.data.quarters.map((x) => x.replace("_", " ")).join(", ")}. The rows held were executed from ${summary.data.first} to ${summary.data.last}.`}>
              <nav aria-label="Quarter signed" className="mb-4 text-sm">
                <div className="mb-1 text-xs uppercase tracking-wide text-muted">Quarter signed</div>
                {held.slice(0, 12).map((h) => (
                  <div key={h.quarter}><Link href={href(h.quarter, product.slug)} aria-current={h.quarter === quarter ? "true" : undefined} className={item(h.quarter === quarter)}>{h.quarter.replace("-", " ")}</Link>{" "}
                    <span className="text-xs text-muted">{count(h.rows)} rows</span></div>
                ))}
                {laterRows > 0 ? <p className="mt-2 text-xs text-muted" data-later={laterRows}>{count(laterRows)} rows carry an execution date after the quarter they were
                  filed for (the latest in {laterLast?.replace("-", " ")}): signed after the quarter closed, or mistyped. They are held as filed and not listed.</p> : null}
              </nav>
              <nav aria-label="Product" className="mb-4 text-sm">
                <div className="mb-1 text-xs uppercase tracking-wide text-muted">Product</div>
                {PRODUCTS.map((p) => <div key={p.slug}><Link href={href(quarter, p.slug)} aria-current={p.slug === product.slug ? "true" : undefined} className={item(p.slug === product.slug)}>{p.label}</Link></div>)}
              </nav>
              <nav aria-label="Delivered in" className="text-sm">
                <div className="mb-1 text-xs uppercase tracking-wide text-muted">Delivered in</div>
                <div><Link href={href(quarter, product.slug)} aria-current={!ba ? "true" : undefined} className={item(!ba)}>Every balancing authority</Link></div>
                {bas.slice(0, 14).map((b) => (
                  <div key={b.ba}><Link href={href(quarter, product.slug, b.ba)} aria-current={b.ba === ba ? "true" : undefined} className={item(b.ba === ba)}>{b.ba}</Link>{" "}
                    <span className="text-xs text-muted">{count(b.rows)}</span></div>
                ))}
              </nav>
            </InputPanel>
          </aside>
          <div className="min-w-0">
            {!read?.ok ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-contracts="unavailable">The contracts signed in {quarter.replace("-", " ")} could not be read: {read ? read.reason : "no quarter"}.</p>
            ) : (
              <>
                <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                  Among the contracts filed with FERC, <span data-n="rows">{count(c.rows)}</span> rows of {product.label.toLowerCase()}{ba ? ` delivered in ${ba}` : ""} were
                  signed in {quarter.replace("-", " ")}: <span data-n="agreements">{count(c.agreements)}</span> agreements between <span data-n="sellers">{count(c.sellers)}</span> sellers
                  and <span data-n="buyers">{count(c.buyers)}</span> buyers. <span data-n="priced">{count(c.priced)}</span> of the rows state a price as a number.
                </p>
                <HeadlineRow>
                  <HeadlineNumber label="Contract rows signed that quarter" value={count(c.rows)} note={<>{count(c.agreements)} agreements; one row per product of an agreement.{all.length >= 5000 ? " The quarter holds more than the 5,000 rows read." : ""}</>} />
                  <HeadlineNumber label="Rows with a price as a number" value={count(c.priced)} note={<>The other {count(c.rows - c.priced)} give words: a market-based rate, a formula, or nothing.</>} />
                  <HeadlineNumber label="Between affiliates" value={count(c.affiliate)} note="Rows the seller marked as a contract with an affiliate." />
                </HeadlineRow>
                <ToolSection title={`Signed in ${quarter.replace("-", " ")}`} note={rows.length > SHOWN ? `The first ${SHOWN} of ${count(rows.length)} rows, newest first. Narrow by product or balancing authority to see the rest.` : "Newest first. Every cell is as the seller filed it."}>
                  <ToolTable caption={`Contracts signed in ${quarter.replace("-", " ")}, as filed with FERC`} minWidth={980} words
                    head={["Signed", "Seller", "Buyer", "Product", "Term", "Quantity", "Price, as filed", "Delivered"]}
                    rows={rows.slice(0, SHOWN).map((r) => {
                      const t = termYears(r), rate = rateText(r);
                      return {
                        key: r.event_id,
                        cells: [r.event_date, r.seller ?? "", <>{r.buyer ?? ""}{(r.affiliate ?? "").toUpperCase() === "Y" ? <span className="text-muted"> (affiliate)</span> : null}</>,
                          <>{r.product ?? ""}{r.class && r.class !== "N/A" ? <span className="text-muted">, {r.class}</span> : null}{r.term && r.term !== "N/A" ? <span className="text-muted">, {r.term}</span> : null}</>,
                          <>{fercDate(r.commencement) || "not stated"} to {fercDate(r.termination) || "no end filed"}{t !== null ? <span className="text-muted"> ({t.toFixed(1)} years)</span> : null}</>,
                          (r.quantity ?? "").trim() === "" ? <span className="text-muted">not stated</span> : `${r.quantity} ${r.units ?? ""}`,
                          rate.numeric ? rate.text : <span className="text-muted">{rate.text}</span>,
                          <>{(r.pod_ba ?? "").trim() || <span className="text-muted">not stated</span>}{r.pod_location ? <span className="text-muted">, {r.pod_location}</span> : null}</>],
                      };
                    })} />
                </ToolSection>
              </>
            )}
            <div className="mb-8 border-t border-rule">
              <Fold title="What a row is">
                <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                  <li><strong>The record:</strong> FERC&apos;s Electric Quarterly Reports. Public utilities, and other sellers with more than a small presence in the market, file the terms of their agreements each quarter. This page reads the contract files of one quarter&apos;s filings and nothing of the transactions.</li>
                  <li><strong>Signed:</strong> the contract&apos;s execution date. A row whose execution date cannot be read is left out, not guessed.</li>
                  <li><strong>Product:</strong> FERC&apos;s product name, with the class (F firm, NF non-firm, UP unit power) and the term (LT long, ST short) where filed.</li>
                  <li><strong>Term:</strong> the filed commencement and termination dates; the years between them when both are dates.</li>
                  <li><strong>Price, as filed:</strong> the rate and its units when the filer gave a number; otherwise the filer&apos;s own description, in grey.</li>
                  <li><strong>Delivered:</strong> the balancing authority and the point of delivery, as filed. Many rows state neither.</li>
                  <li><strong>A company with more than one filing in the quarter</strong> is read from its newest filing.</li>
                </ul>
              </Fold>
              <Fold title="What this cannot see">
                <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                  <li><strong>Texas.</strong> Sales inside ERCOT are not filed with FERC. {count(ercot)} of the {count(summary.data.rows)} rows held here name ERCOT as the
                    delivery point; in the quarter&apos;s whole file they are almost all one utility&apos;s transmission agreements.</li>
                  <li><strong>Buyers that do not sell power.</strong> A company buying under a power purchase agreement appears only as the customer of a seller that files.</li>
                  <li><strong>Financial contracts.</strong> A contract settled in money and not in power is not a sale under a FERC tariff.</li>
                  <li><strong>Names as one thing.</strong> The same buyer is spelled several ways across filers; nothing here merges them.</li>
                  <li><strong>Totals of megawatts.</strong> Quantity is empty in many rows and its units vary, so no total is given.</li>
                </ul>
              </Fold>
            </div>
          </div>
        </div>
      )}
      <SourceLine tables={[TABLE]}
        note={<>Federal Energy Regulatory Commission, Electric Quarterly Reports, the contract files of one quarter&apos;s filings (eqrreportviewer.ferc.gov). An internal table: this page is read only in the internal view.</>} />
    </ToolPage>
  );
}
