import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Related } from "@/components/Related";
import { companies } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { CompaniesTable } from "./CompaniesTable";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Companies" };

// Session 26: the seed of the company database (platform tool 10), from the Thesis Builder (tool 27)
export default async function CompaniesPage() {
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
        (<Link href="/deals">/deals</Link>): every buyer, seller and other party of a deal is a row, with the deal&apos;s sector, tags, place and story links, and
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
          <Cite tables={["energy_companies"]} note="Found by warehouse/thesis/build.py from public web sources; method docs/methods/thesis_builder.md" />
        </>
      )}
      <Related href="/companies" />
    </>
  );
}
