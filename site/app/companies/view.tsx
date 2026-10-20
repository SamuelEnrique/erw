import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { companies } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { CompaniesTable } from "./CompaniesTable";

// Session 239: the companies tab of /deals (lib/tabs.ts). What /companies drew is drawn here, block for block; the page
// (app/deals/page.tsx) carries the brand, the sheet, the tabs and the Related line, and /companies redirects to the
// tab. Each company row links to the tracker filtered by its name (/deals?tab=tracker&party=<name>).

// Session 26: the seed of the company database (platform tool 10), from the Thesis Builder (tool 27)
export async function CompaniesView() {
  const res = await attempt(companies);
  return (
    <>
      <h1 className="mb-1 text-3xl">Companies</h1>
      <p className="mb-2 max-w-3xl">
        Energy companies the ERW has found and sourced: what each does, its stage, what it has raised, where it is, who founded it, and how sure the
        ERW is, with every source linked.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Scope: a seed, not a census. The table grows from Thesis Builder runs, each of which maps one niche for investors, and from the deal tracker
        (<Link href="/deals">Deals</Link>): every buyer, seller and other party of a deal is a row, with the deal&apos;s sector, tags, place and story links, and
        is marked &quot;from deals; not yet researched&quot; until the Thesis Builder researches it. Public companies are listed with their raised amount left blank and noted as public.
        A number no cited source confirmed reads &quot;not confirmed&quot;; the confidence score (0 to 100) is a rule, explained on each row.
      </p>
      {!res.ok ? (
        <NoData what="companies" reason={res.reason} />
      ) : res.data.length === 0 ? (
        <NoData what="companies" reason="energy_companies has no rows in the live set" />
      ) : (
        <>
          {/* session 27: a blank field arrives from the live set as null (the deal-seeded rows have many); the table reads strings */}
          <CompaniesTable rows={res.data.map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v ?? ""])) as typeof r)} />
          <Cite tables={["energy_companies"]} note="Found by warehouse/thesis/build.py from public web sources; what its reports hold: docs/methods/thesis.md" />
          {/* session 329: the two notes the tab's rows follow */}
          <p className="mt-1 text-xs text-muted">Method: <Link href="/data/methods/energy_deals">the companies a deal names</Link>; <Link href="/data/methods/thesis">the Thesis Builder&apos;s research</Link>.</p>
        </>
      )}
    </>
  );
}
