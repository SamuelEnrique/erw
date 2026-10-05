import type { Metadata } from "next";
import { Related } from "@/components/Related";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { companies, deals, renderTime } from "@/lib/data";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { count } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { DealsTable, type Deal } from "./DealsTable";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Deals" };

export default async function DealsPage() {
  const res = await attempt(deals);
  const cos = await attempt(companies); // session 26: party names that match a company link to /companies
  const month = new Date(renderTime()).toISOString().slice(0, 7);
  return (
    <>
      <h1 className="mb-1 text-3xl">Energy deals</h1>
      <p className="mb-2 max-w-3xl">
        Energy deals reported in the news since 2025-10-01, from the stories the ERW scores, each with its sources.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Transactions: power purchase agreements, offtakes, acquisitions, financings, joint ventures, fuel supply,
        nuclear and datacenter power deals. Each deal is extracted from the stories&apos; titles and summaries by a model, and every number was checked
        against the text it came from; a number the stories do not state is left blank. A deal reported by several stories is one row, with every
        story linked. A party that is in the company table links to its row on <Link href="/companies">/companies</Link>.
      </p>
      {!res.ok ? (
        <NoData what="deals" reason={res.reason} />
      ) : res.data.length === 0 ? (
        <NoData what="deals" reason="energy_deals has no rows in the live set" />
      ) : (
        <Body rows={res.data.map(toDeal)} month={month} companies={cos.ok ? cos.data.map((c) => c.name) : []} />
      )}
    </>
  );
}

function toDeal(r: Awaited<ReturnType<typeof deals>>[number]): Deal {
  const x = r.extra ?? {};
  const num = (v: string | number | null | undefined) => (v === null || v === undefined || v === "" ? null : Number(v));
  return {
    id: r.event_id,
    date: r.event_date,
    dateBasis: x.date_basis ?? "",
    type: x.deal_type ?? "",
    status: r.status ?? "",
    buyer: x.buyer ?? "",
    seller: x.seller ?? "",
    others: x.other_parties ?? "",
    asset: x.asset ?? "",
    technology: x.technology ?? "",
    state: x.state ?? "",
    country: x.country ?? "",
    mw: num(r.mw),
    mwh: num(x.mwh),
    dollars: num(x.dollars),
    priceValue: num(x.price_value),
    priceUnit: x.price_unit ?? "",
    termYears: num(x.term_years),
    aiPower: String(x.ai_power ?? "").toLowerCase() === "true", // session 114: the table holds "True", "False" and "false"
    confidence: num(x.confidence),
    storyUrls: (x.story_urls ?? r.source_url).split(";").filter(Boolean),
    source: r.source,
  };
}

function Body({ rows, month: current, companies }: { rows: Deal[]; month: string; companies: string[] }) {
  // session 49: at the start of a month with no deals yet, the previous month, labeled
  const prev = new Date(Date.UTC(Number(current.slice(0, 4)), Number(current.slice(5, 7)) - 2, 1)).toISOString().slice(0, 7);
  const empty = !rows.some((d) => d.date.slice(0, 7) === current);
  const month = empty ? prev : current;
  const inMonth = rows.filter((d) => d.date.slice(0, 7) === month);
  const mw = inMonth.reduce((a, d) => a + (d.mw ?? 0), 0);
  const withMw = inMonth.filter((d) => d.mw !== null).length;
  const aiPct = inMonth.length ? Math.round((100 * inMonth.filter((d) => d.aiPower).length) / inMonth.length) : null;
  const cells = [
    { k: `Deals in ${month}`, v: <Num check={`deals|month_count|${month}`} raw={inMonth.length}>{count(inMonth.length)}</Num> },
    {
      k: `MW announced in ${month}`,
      v: (
        <>
          <Num check={`deals|month_mw|${month}`} raw={mw}>{count(mw)}</Num>{" "}
          <span className="text-xs text-muted">from the {withMw} deals that state MW</span>
        </>
      ),
    },
    {
      k: "Share tagged AI or datacenter power",
      v:
        aiPct === null ? (
          <span className="text-sm text-muted">no data: no deals this month</span>
        ) : (
          <Num check={`deals|month_ai_pct|${month}`} raw={aiPct}>{`${aiPct}%`}</Num>
        ),
    },
  ];
  return (
    <>
      <section aria-label="This month" className="mb-6">
        <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
          {cells.map((c) => (
            <div key={c.k} className="bg-panel px-3 py-2">
              <div className="text-xs text-muted">{c.k}</div>
              <div className="text-lg tabular-nums">{c.v}</div>
            </div>
          ))}
        </div>
        {empty ? (
          <p className="mt-1 text-sm">No deals dated {current} yet, so these are {month}&apos;s, the month before.</p>
        ) : null}
        <p className="mt-1 text-xs text-muted">
          By the deal&apos;s date: the announced date where a story states it, else the first story&apos;s publish date (UTC). The ERW has scored news since
          2026-09-23, so the table starts there.
        </p>
      </section>
      <DealsTable rows={rows} companies={companies} />
      <Cite
        tables={["energy_deals"]}
        note="Extracted by warehouse/deals/extract.py from the scored stories of news_stories; the evidence sentences are outlet text and stay in the internal table energy_deals_evidence"
      />
      <Related href="/deals" />
    </>
  );
}
