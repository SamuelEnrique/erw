import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { companies, deals, renderTime } from "@/lib/data";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { count } from "@/lib/format";
import { isLicenseReason, licenseByRow, licenseNeeded } from "@/lib/license";
import { HeldRows } from "@/components/tool/HeldRows";
import { attempt } from "@/lib/supabase";
import { Tabs } from "@/components/tool/Tabs";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ToolPage } from "@/components/tool/ToolPage";
import { one, tabOf } from "@/lib/tabs";
import { CompaniesView } from "../companies/view";
import { DealsTable, type Deal } from "./DealsTable";
import { TrackerView } from "./v2/view";
import { ComparablesView } from "./comparables/view";
import { DealsDecisions } from "./Decisions";
import { DealsHeld } from "./Held";
import { fileIsSound, type PublicDealRow, type PublicDealsFile } from "@/lib/dealspublic";
import publicFile from "@/data/deals_public.json";

// Session 822: the public rows of the held table (lib/dealspublic.ts): the file warehouse/deals/public_rows.py writes
// from the archive's copy of energy_deals and its evidence rows. Read once; a file that is not sound (a row without
// public evidence, a source outside it) is not drawn, and the page shows the whole-table hold as before.
const PUBLIC_FILE = publicFile as unknown as PublicDealsFile;
const PUBLIC: PublicDealsFile | undefined = fileIsSound(PUBLIC_FILE) ? PUBLIC_FILE : undefined;

export const revalidate = 3600;
export const metadata: Metadata = { title: "Deals" };

// Session 239: one page, three tabs (lib/tabs.ts): the deals (what this page drew, below), the tracker (what /deals/v2
// drew: the same deals by type, technology, grid, counterparty and year) and the companies (what /companies drew).
// The two old addresses redirect to their tabs. The tab is in the address, ?tab=; a company is a filter of the
// tracker (?tab=tracker&party=<name>), and each company row links to it.
export default async function DealsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = one(await searchParams);
  // session 466: /deals?view=comparables, the tracker's disclosed figures side by side, under the tracker's tab
  const comparablesView = sp.view === "comparables";
  const tab = comparablesView ? "tracker" : tabOf("/deals", sp.tab);
  return (
    <Brand>
      <ToolPage>
        <div data-deals-tab={tab}>
          <Tabs page="/deals" active={tab} />
          {comparablesView ? <ComparablesView sp={sp} /> : tab === "tracker" ? <TrackerView sp={sp} /> : tab === "companies" ? <CompaniesView /> : <DealsView />}
          {/* session 465: the decisions block, under every tab and under the hold */}
          <DealsDecisions />
          {/* session 329: each tab's public tables, as CSV with a Python and a Stata reader (session 328's shared line) */}
          <TableDownloads tables={tab === "companies" ? ["energy_companies", "energy_deals"] : ["energy_deals", "news_stories"]} />
          <Related href="/deals" />
        </div>
      </ToolPage>
    </Brand>
  );
}

/** The first tab: every deal in a sortable table, with the counts of this month (what /deals drew before session 239). */
async function DealsView() {
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
        story linked. A party that is in the company table links to its row on <Link href="/deals?tab=companies">Companies</Link>.{" "}
        <Link href="/data/methods/energy_deals">Method</Link>.
      </p>
      {!res.ok ? (
        isLicenseReason(res.reason) && PUBLIC && PUBLIC.shown.length ? (
          <>
            {/* session 822: the table is held whole; the rows a public source stands behind are drawn from the public rows' file,
                the held and the unsettled counted in the line above them */}
            <DealsHeld file={PUBLIC} />
            <DealsTable rows={PUBLIC.shown.map(toPublicDeal)} companies={cos.ok ? cos.data.map((c) => c.name) : []} />
            <Cite
              tables={["energy_deals"]}
              note="The rows shown are those of energy_deals at least one evidence row of which comes from a publisher whose terms the ERW reads as public (warehouse/deals/public_rows.py); every other row is counted and held"
            />
          </>
        ) : (
          <>
            <NoData what="deals" reason={res.reason} />
            {isLicenseReason(res.reason) ? <DealsHeld /> : null}
          </>
        )
      ) : res.data.length === 0 ? (
        <>
          {/* session 500: a table held by row with no public row says so, then how many are held */}
          <NoData what="deals" reason={licenseNeeded("energy_deals") && licenseByRow("energy_deals") ? "no row of energy_deals rests on a public source alone" : "energy_deals has no rows in the live set"} />
          <HeldRows shape="events" table="energy_deals" shown={0} method="/data/methods/energy_deals" />
        </>
      ) : (
        <>
          {/* session 500: held by row, the public rows are shown and the held ones counted (nothing here until the mark) */}
          <HeldRows shape="events" table="energy_deals" shown={res.data.length} method="/data/methods/energy_deals" />
          <Body rows={res.data.map(toDeal)} month={month} companies={cos.ok ? cos.data.map((c) => c.name) : []} />
        </>
      )}
    </>
  );
}

/** Session 822: a shown row of the public rows' file, as the table draws it: the live set's row shape, with the public
 * evidence as its sources and the other publishers as a count. */
function toPublicDeal(r: PublicDealRow): Deal {
  const d = toDeal({ ...r, extra: r.extra });
  return { ...d, source: r.source, storyUrls: r.public_evidence.map((e) => e.url), publicEvidence: r.public_evidence, otherPublishers: r.other_publishers };
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
          By the deal&apos;s date: the announced date where a story states it, else the first story&apos;s publish date (UTC). Deals are extracted only from
          the stories the ERW has scored; a deal&apos;s date can be earlier than its story&apos;s.
        </p>
      </section>
      <DealsTable rows={rows} companies={companies} />
      <Cite
        tables={["energy_deals"]}
        note="Extracted by warehouse/deals/extract.py from the scored stories of news_stories; the evidence sentences are outlet text and stay in the internal table energy_deals_evidence"
      />
    </>
  );
}
