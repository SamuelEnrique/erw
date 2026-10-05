import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { attempt } from "@/lib/supabase";
import { LARGEST_PRODUCTS, PRODUCTS, STORAGE_FIELDS, TABLE, UNREAD, byBa, changesOf, choices, counts, fercDate, filedQuarter, filter, largestHref, listed, mwHref, quarterDates, quarters,
  rateText, termYears, viewOf, type Contract, type LargestProduct, type MwParty, type Party, type Summary } from "@/lib/contracts";
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
  const v = viewOf(q);
  const every = summary.ok ? quarters(summary.data) : [];
  const { upTo: held, laterRows, laterLast } = listed(every, summary.ok ? filedQuarter(summary.data) : null);
  const { quarter, product, ba } = choices(q, held.map((h) => h.quarter));
  const read = quarter && v.view === "quarter" ? await attempt(() => { const d = quarterDates(quarter); return contractRows(d.from, d.to); }) : null;
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
      <nav aria-label="View" className="mb-6 flex flex-wrap gap-x-6 gap-y-1 border-b border-rule pb-3 text-sm" data-view={v.view}>
        <Link href="/contracts" aria-current={v.view === "quarter" ? "true" : undefined} className={item(v.view === "quarter")}>Contracts by the quarter signed</Link>
        <Link href={largestHref(v.product.slug)} aria-current={v.view === "largest" ? "true" : undefined} className={item(v.view === "largest")}>The largest buyers and sellers</Link>
        <Link href={mwHref(v.product.slug)} aria-current={v.view === "mw" ? "true" : undefined} className={item(v.view === "mw")}>Ranked by megawatts stated</Link>
        <Link href="/contracts?view=terms" aria-current={v.view === "terms" ? "true" : undefined} className={item(v.view === "terms")}>What the filings state</Link>
      </nav>
      {v.view === "mw" ? <MwView summary={summary.ok ? summary.data : null} reason={summary.ok ? null : summary.reason} product={v.product} />
        : v.view === "terms" ? <TermsView summary={summary.ok ? summary.data : null} reason={summary.ok ? null : summary.reason} />
        : v.view === "largest" ? <LargestView summary={summary.ok ? summary.data : null} reason={summary.ok ? null : summary.reason} product={v.product} /> : !summary.ok || !quarter ? (
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
                  <li><strong>Names as one thing.</strong> The same buyer is spelled several ways across filers; this list shows each name as filed. The view of the largest buyers and sellers counts a buyer&apos;s spellings together, by rule.</li>
                  <li><strong>Totals of megawatts.</strong> Quantity is empty in many rows and its units vary, so this list gives no total. The view &quot;Ranked by megawatts stated&quot; adds up the few contracts that state one, and says how few.</li>
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

/** Session 99: the largest buyers and sellers of one product, contracts in force, from the whole quarter's file. Buyers
 * are counted under one name by rule (warehouse/derived/eqr_buyers.py; docs/methods/eqr_buyers.md); sellers by FERC's
 * company identifier. The figures are the stored summary's (the loader puts them there); the page ranks nothing. */
function LargestView({ summary, reason, product }: { summary: Summary | null; reason: string | null; product: LargestProduct }) {
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const L = summary?.largest;
  if (!summary || !L) {
    return (
      <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-largest="unavailable">
        The largest buyers and sellers are not loaded here yet: {summary ? "the stored summary was computed before this view existed; the next load of the contract table adds it" : reason}.
      </p>
    );
  }
  const buyers = L.lists.buyer[product.slug], sellers = L.lists.seller[product.slug];
  const table = (role: "buyer" | "seller", list: typeof buyers) => (
    <ToolTable minWidth={720} caption={`The largest ${role}s of ${product.label.toLowerCase()}, contracts in force`}
      head={["", role === "buyer" ? "Buyer, by its merged name" : "Seller", "Contracts", "Rows", role === "buyer" ? "Sellers" : "Buyers", "MW filed", "Rows with a MW"]}
      rows={list.top.map((r: Party) => ({ key: `${role}${r.rank}`, cells: [String(r.rank), <span key="n" className="block text-left" data-party={`${role}|${r.rank}`}>{r.name}</span>,
        <span key="c" data-n={`${role}|${r.rank}|contracts`}>{count(r.contracts)}</span>, <span key="r" data-n={`${role}|${r.rank}|rows`}>{count(r.rows)}</span>,
        <span key="o" data-n={`${role}|${r.rank}|counterparties`}>{count(r.counterparties)}</span>,
        r.rows_with_mw > 0 ? <span key="m" data-n={`${role}|${r.rank}|mw`}>{r.mw_filed.toLocaleString("en-US", { maximumFractionDigits: 1 })}</span> : <span key="m" className="text-muted">none filed</span>,
        <span key="w" data-n={`${role}|${r.rank}|rows_with_mw`}>{count(r.rows_with_mw)}</span>] }))} />
  );
  return (
    <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]" data-largest="1">
      <aside>
        <InputPanel title="Choose" note={`Contracts in force in the filings for ${(L.quarter ?? "").replace("_", " ")}: every agreement in force is filed again each quarter, so this is the standing book, not one quarter's signings.`}>
          <nav aria-label="Product" className="text-sm">
            <div className="mb-1 text-xs uppercase tracking-wide text-muted">Product</div>
            {LARGEST_PRODUCTS.map((p) => <div key={p.slug}><Link href={largestHref(p.slug)} aria-current={p.slug === product.slug ? "true" : undefined} className={item(p.slug === product.slug)}>{p.label}</Link></div>)}
          </nav>
        </InputPanel>
      </aside>
      <div className="min-w-0">
        <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="largest">
          <span data-n="contracts">{count(buyers.contracts)}</span> {product.label.toLowerCase()} contracts are in force in FERC&apos;s filings, between <span data-n="sellers">{count(sellers.parties)}</span> sellers
          and <span data-n="buyers">{count(buyers.parties)}</span> buyers. The buyer with the most is {buyers.top[0]?.name}, on <span data-n="top|buyer">{count(buyers.top[0]?.contracts ?? 0)}</span>; the seller with the most
          is {sellers.top[0]?.name}, on <span data-n="top|seller">{count(sellers.top[0]?.contracts ?? 0)}</span>.
        </p>
        <HeadlineRow>
          <HeadlineNumber label="Contracts in force" value={count(buyers.contracts)} note={<>{count(buyers.rows)} product rows. A contract is one filer&apos;s contract identifier.</>} />
          <HeadlineNumber label="Buyers, after the name rules" value={count(buyers.parties)} note={<>Sellers: {count(sellers.parties)}, by FERC&apos;s company identifier.</>} />
          <HeadlineNumber label="Buyer names brought together" value={<span data-n="names|merged">{count(L.names.merged_names)}</span>}
            note={<><span data-n="names|filed">{count(L.names.filed)}</span> names as filed, across every product, are counted as <span data-n="names|after">{count(L.names.after_rules)}</span>. <span data-n="names|doubtful">{count(L.names.doubtful_pairs)}</span> pairs that look alike were not merged.</>} />
        </HeadlineRow>
        <ToolSection title={`The largest buyers of ${product.label.toLowerCase()}`} note={<>The first {L.top} of {count(buyers.parties)}, by contracts in force, then rows. The market operators stand at the top of energy and capacity because a sale into an organized market is filed with the operator as its customer: they are counterparties of record, not users of the power.</>}>
          {table("buyer", buyers)}
        </ToolSection>
        <ToolSection title={`The largest sellers of ${product.label.toLowerCase()}`} note={<>The first {L.top} of {count(sellers.parties)}. A seller is a filer: one company identifier, one name.</>}>
          {table("seller", sellers)}
        </ToolSection>
        <div className="mb-8 border-t border-rule">
          <Fold title="How a buyer's names are brought together">
            <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
              <li><strong>By rule, never by a guess.</strong> Two spellings are one buyer only when they are identical after: capitals and spaces; punctuation (&amp; read as &quot;and&quot;); a leading &quot;The&quot;; a short list of whole-word abbreviations (Corp, Inc, Co, Ltd, Coop, Assn, Elec, Dept and a few more); the legal form written one way (L.L.C. as LLC); and a name filed with and without its one legal form.</li>
              <li><strong>Every merge is listed</strong> in the internal table <code className="font-mono">ferc_eqr_buyer_names</code>: each name as filed, the name it is counted under, and the rules that changed it.</li>
              <li><strong>Doubtful pairs are listed and not merged</strong> in <code className="font-mono">ferc_eqr_buyer_doubtful</code>: the same name under two legal forms (LLC and Inc may be two companies); a name with an added d/b/a or bracketed clause; and names 94 percent alike that may be a typing error. A person decides each.</li>
              <li><strong>So a buyer can still be split.</strong> A parent and its subsidiaries are different names and stay apart; a misspelling stays apart until a person rules on it. A buyer&apos;s count here is a floor.</li>
            </ul>
          </Fold>
          <Fold title="What the ranking is, and is not">
            <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
              <li><strong>By contracts, not by megawatts.</strong> Few rows file a quantity in MW; the column shows what is filed and on how many rows. No total of megawatts is a ranking here: the view &quot;Ranked by megawatts stated&quot; ranks the few contracts that state one.</li>
              <li><strong>In force, not new.</strong> Every agreement in force is filed again each quarter. For what was signed lately, use the other view.</li>
              <li><strong>Not Texas.</strong> Sales inside ERCOT are not filed with FERC.</li>
              <li><strong>Not buyers that never appear as a seller&apos;s customer</strong> in a filing: a contract settled in money, or one outside FERC&apos;s jurisdiction.</li>
            </ul>
          </Fold>
        </div>
      </div>
    </div>
  );
}

const notLoaded = (what: string, summary: Summary | null, reason: string | null) => (
  <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-terms="unavailable">
    {what} not loaded here yet: {summary ? "the stored summary was computed before this view existed; the next load of the contract table adds it" : reason}.
  </p>
);
const mwText = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 1 });
const quarterText = (q: string | null) => (q ?? "").replace("_", " ");

/** Session 125: the buyers and sellers of one product ranked by the megawatts their contracts in force state
 * (warehouse/derived/eqr_terms.py; docs/methods/eqr_terms.md). Most contracts state none: the page says how many do,
 * and shows each party's place by contracts beside its place by megawatts. The figures are the stored summary's. */
function MwView({ summary, reason, product }: { summary: Summary | null; reason: string | null; product: LargestProduct }) {
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const T = summary?.terms;
  if (!summary || !T) return notLoaded("The ranking by megawatts is", summary, reason);
  const buyers = T.by_mw.buyer[product.slug], sellers = T.by_mw.seller[product.slug];
  const stated = T.mw.by_product[product.slug] ?? { contracts: 0, contracts_with_mw: 0, contracts_over: 0 };
  const ceiling = T.mw_ceiling ?? 0;
  const table = (role: "buyer" | "seller", list: typeof buyers) => (
    <ToolTable minWidth={720} caption={`The ${role}s of ${product.label.toLowerCase()} with the most megawatts stated, contracts in force`}
      head={["", role === "buyer" ? "Buyer, by its merged name" : "Seller", "MW stated", "Contracts that state a MW", "Contracts in force", "Place by contracts"]}
      rows={list.top.map((r: MwParty) => ({ key: `${role}${r.rank}`, cells: [String(r.rank), <span key="n" className="block text-left" data-party={`mw|${role}|${r.rank}`}>{r.name}</span>,
        <span key="m" data-n={`mw|${role}|${r.rank}|mw`}>{mwText(r.mw)}</span>, <span key="w" data-n={`mw|${role}|${r.rank}|with`}>{count(r.contracts_with_mw)}</span>,
        <span key="c" data-n={`mw|${role}|${r.rank}|contracts`}>{count(r.contracts)}</span>, <span key="p" data-n={`mw|${role}|${r.rank}|place`}>{count(r.rank_contracts)}</span>] }))} />
  );
  return (
    <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]" data-mw="1">
      <aside>
        <InputPanel title="Choose" note={`Contracts in force in the filings for ${quarterText(T.quarter)}. Only a contract that states a quantity in MW, or in kW, is ranked.`}>
          <nav aria-label="Product" className="text-sm">
            <div className="mb-1 text-xs uppercase tracking-wide text-muted">Product</div>
            {LARGEST_PRODUCTS.map((p) => <div key={p.slug}><Link href={mwHref(p.slug)} aria-current={p.slug === product.slug ? "true" : undefined} className={item(p.slug === product.slug)}>{p.label}</Link></div>)}
          </nav>
        </InputPanel>
      </aside>
      <div className="min-w-0">
        <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="mw">
          Of the <span data-n="mw|contracts">{count(stated.contracts)}</span> {product.label.toLowerCase()} contracts in force in FERC&apos;s filings, <span data-n="mw|with">{count(stated.contracts_with_mw)}</span> state
          a quantity in megawatts. Those add up to <span data-n="mw|total">{mwText(buyers.mw)}</span> MW, bought by <span data-n="mw|buyers">{count(buyers.parties)}</span> buyers
          from <span data-n="mw|sellers">{count(sellers.parties)}</span> sellers. This ranks what is stated: it is not a ranking of the market.
        </p>
        <HeadlineRow>
          <HeadlineNumber label="Contracts that state a MW" value={count(stated.contracts_with_mw)} note={<>Of {count(stated.contracts)} in force. The others state megawatt-hours, a rate period, or nothing.</>} />
          <HeadlineNumber label="MW stated, in all" value={mwText(buyers.mw)} note="Per contract, the largest MW any of its rows states; a contract's rows repeat its quantity by period and by product." />
          <HeadlineNumber label="Contracts left out as not megawatts" value={<span data-n="mw|over">{count(stated.contracts_over)}</span>}
            note={<>They state more than {count(ceiling)} MW, the largest power station operating in the United States: a year&apos;s megawatt-hours or kilowatts filed under MW.</>} />
        </HeadlineRow>
        <ToolSection title={`Buyers of ${product.label.toLowerCase()}, by megawatts stated`} note={<>The first {Math.min(T.top, buyers.parties)} of {count(buyers.parties)} buyers with a megawatt stated. &quot;Place by contracts&quot; is the buyer&apos;s place in the other view, among every buyer of the product.</>}>
          {table("buyer", buyers)}
        </ToolSection>
        <ToolSection title={`Sellers of ${product.label.toLowerCase()}, by megawatts stated`} note={<>The first {Math.min(T.top, sellers.parties)} of {count(sellers.parties)}. A seller is a filer: one company identifier, one name.</>}>
          {table("seller", sellers)}
        </ToolSection>
        <div className="mb-8 border-t border-rule">
          <Fold title="What a megawatt stated is, and what this leaves out">
            <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
              <li><strong>Stated:</strong> the row&apos;s quantity when its units are MW, or kW divided by 1,000. A quantity in megawatt-hours, per month, per day, or with no units is not a number of megawatts and is not converted. A quantity of zero is not a quantity.</li>
              <li><strong>Per contract, the largest MW any row states,</strong> then added up by party. Adding the rows would count one contract once for each period and product it lists.</li>
              <li><strong>Left out, and counted:</strong> a contract stating more than {count(ceiling)} MW. No single contract is for more than the largest station in the country; the figure is another unit filed under MW. Across every product {count(T.mw.rows_over)} rows do.</li>
              <li><strong>A figure under that ceiling can be mislabelled too,</strong> and nothing in the filing can tell. A person should read the contract before quoting one row.</li>
              <li><strong>Most of the book is absent.</strong> A full-requirements sale or a sale into an organized market states no megawatts. The largest buyers by contracts are mostly not here.</li>
            </ul>
          </Fold>
        </div>
      </div>
    </div>
  );
}

/** Session 125: what the filings state and what they do not: prices as numbers, as words, and the few words that leave
 * one reading; the tags the product fields allow; contracts new and gone by quarter; the name merges; and FERC's own
 * words on the data. Counts only, from the stored summary. */
function TermsView({ summary, reason }: { summary: Summary | null; reason: string | null }) {
  const T = summary?.terms;
  if (!summary || !T) return notLoaded("What the filings state is", summary, reason);
  const P = T.prices, unread = P.words_only - P.read;
  const all = changesOf(T, "all");
  const products = ["all", "energy", "capacity", "tolling"] as const;
  const label = { all: "Every product", energy: "Energy", capacity: "Capacity", tolling: "Tolling energy" } as const;
  const doubtful = summary.largest?.names.doubtful_pairs ?? null;
  return (
    <div className="min-w-0" data-terms="1">
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="terms">
        Of the <span data-n="terms|rows">{count(T.rows)}</span> contract rows filed for {quarterText(T.quarter)}, <span data-n="terms|number">{count(P.filed_number)}</span> give their rate as a
        number and <span data-n="terms|words">{count(P.words_only)}</span> give words. A price can be read from the words, with no doubt about number or unit,
        in <span data-n="terms|read">{count(P.read)}</span> of them. <span data-n="terms|unread">{count(unread)}</span> remain unread.
      </p>
      <HeadlineRow>
        <HeadlineNumber label="Rates filed as words" value={count(P.words_only)} note={<>{count(P.filed_number)} rows file a number; {count(P.none)} file neither.</>} />
        <HeadlineNumber label="Prices read from the words" value={count(P.read)} note={<>{count(P.read_usd_per_mwh)} of them in dollars per megawatt-hour; the others are capacity prices per kW or MW and month or day, kept in their own unit.</>} />
        <HeadlineNumber label="Left unread" value={count(unread)} note="Never estimated. The reasons are counted below." />
      </HeadlineRow>
      <ToolSection title="Why a rate in words was not read" note="The rule reads a price only when the words hold exactly one dollar amount, followed at once by its unit, with no condition and no other number beside it. The first test a row fails is its reason.">
        <ToolTable minWidth={720} caption="Rates filed as words, by what the rule found" words
          head={["What the words hold", "For example", "Rows"]}
          rows={[...UNREAD.map((u) => ({ key: u.key, cells: [u.label, <span key="e" className="text-muted">{u.example}</span>, <span key="n" data-n={`unread|${u.key}`}>{count(P.unread[u.key] ?? 0)}</span>] })),
            { key: "read", cells: [<strong key="l">One amount, its unit, nothing else: read</strong>, <span key="e" className="text-muted">{Object.entries(P.read_by_unit).map(([u, n]) => `${n} in ${u}`).join(", ")}</span>, <span key="n" data-n="unread|read">{count(P.read)}</span>] }]} />
      </ToolSection>
      <ToolSection title="Tolling and storage, from the product fields" note="A tag is given only from FERC's product fields: product name, product type, class, term and increment.">
        <ul className="max-w-3xl list-disc space-y-1.5 pl-5 text-sm">
          <li><strong>Tolling:</strong> <span data-n="tag|tolling_rows">{count(T.tags.tolling_rows)}</span> rows of <span data-n="tag|tolling_contracts">{count(T.tags.tolling_contracts)}</span> contracts carry the product name Tolling Energy.</li>
          <li><strong>Storage:</strong> <span data-n="tag|storage_rows">{count(T.tags.storage_rows)}</span> rows. FERC&apos;s product list has no storage product, so no product field names storage or a battery, and no row is tagged.</li>
          <li><strong>Where the words do stand:</strong> in <span data-n="tag|elsewhere">{count(T.tags.storage_words_rows)}</span> rows, outside the product fields: {STORAGE_FIELDS.map((f, i) => (
            <span key={f.key}>{i ? ", " : ""}{f.label} (<span data-n={`tag|${f.key}`}>{count(T.tags.storage_words_elsewhere[f.key] ?? 0)}</span>)</span>))}. These are not tagged: a seller named
            for a battery sells other things too, and a tariff&apos;s storage schedule is not a contract for a battery. They say where a person would have to read.</li>
        </ul>
      </ToolSection>
      <ToolSection title="Contracts new and gone, by quarter" note={all.length > 1 ? "A contract is one filer's contract identifier. New: in force in this quarter's filings and not in the quarter before. Gone: the reverse. A filer that renumbers its contracts makes one gone and one new." : "Only one quarter is held: nothing to compare yet."}>
        <ToolTable minWidth={720} caption="Contracts in force in FERC's filings by quarter, and the change from the quarter before"
          head={["Filed for", "Product", "Contracts in force", "New", "Gone", "Kept"]}
          rows={all.flatMap((q) => products.map((p) => {
            const c = T.changes.find((x) => x.quarter === q.quarter && x.product === p);
            const cell = (k: "contracts_new" | "contracts_gone" | "contracts_kept") => c && c[k] !== undefined ? <span key={k} data-n={`change|${q.quarter}|${p}|${k}`}>{count(c[k] as number)}</span> : <span key={k} className="text-muted">no quarter before</span>;
            return { key: `${q.quarter}${p}`, cells: [quarterText(q.quarter), label[p], <span key="f" data-n={`change|${q.quarter}|${p}|in_force`}>{count(c?.contracts_in_force ?? 0)}</span>, cell("contracts_new"), cell("contracts_gone"), cell("contracts_kept")] };
          }))} />
      </ToolSection>
      <ToolSection title="Buyers under one name" note="Only the merges a rule makes certain are applied. A pair that merely looks alike is listed for a person and left apart.">
        <ul className="max-w-3xl list-disc space-y-1.5 pl-5 text-sm">
          <li><span data-n="buyers|merged">{count(T.buyers.rows_merged)}</span> of the {count(T.rows)} rows carry a buyer name that the rules count together with at least one other spelling.</li>
          {doubtful !== null ? <li><span data-n="buyers|doubtful">{count(doubtful)}</span> doubtful pairs stay listed in <code className="font-mono">ferc_eqr_buyer_doubtful</code> and are not merged in any figure on this page.</li> : null}
        </ul>
      </ToolSection>
      <ToolSection title="FERC's terms for this data" note="Quoted, not interpreted. The table stays internal until a person has read the Commission's own statement of terms.">
        <ul className="max-w-3xl list-disc space-y-1.5 pl-5 text-sm">
          <li>&quot;The Commission established the EQR reporting requirements to help ensure the collection of information needed to perform its regulatory functions over transmission and wholesale sales of electricity, while making data available to the public and allowing public utilities to better fulfill their responsibility under Federal Power Act (FPA) section 205(c) to have rates on file in a convenient form and place.&quot; Federal Register, 17 February 2026, 91 FR 7278, at 7279, FR Doc. 2026-03012.</li>
          <li>&quot;The Commission adopted the EQR as the reporting mechanism for public utilities to fulfill their responsibility under FPA section 205(c) to have information relating to their rates, terms and conditions of service available for public inspection in a convenient form and place.&quot; Federal Register, 24 March 2026, 91 FR 14306, at 14310, FR Doc. 2026-05709.</li>
          <li><strong>What this machine did not reach:</strong> the Commission&apos;s own pages of terms on ferc.gov answered this machine&apos;s requests with HTTP 403 on 5 October 2026, as they did in session 83. That was not worked around. The two passages say the filings are public; neither is a statement of the terms on which the data may be republished.</li>
        </ul>
      </ToolSection>
    </div>
  );
}
