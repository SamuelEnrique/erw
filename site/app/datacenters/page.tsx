import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { NoData } from "@/components/NoData";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { Tabs } from "@/components/tool/Tabs";
import { datacenters, queueActive, queueSites } from "@/lib/data";
import { gridOfTable } from "@/lib/datacenter/bygrid";
import { INDEX } from "@/lib/datacenterdata";
import { one } from "@/lib/tabs";
import { attempt } from "@/lib/supabase";
import { licenseByRow, licenseNeeded } from "@/lib/license";
import { HeldRows } from "@/components/tool/HeldRows";  // session 500
import { DatacentersPublicLine } from "./PublicLine";  // session 827
import { Body, toFacility } from "./Body";
import { LargeLoad, LargeLoadSource } from "./LargeLoad";
import { GridsView } from "./GridsView";
import { PowerSide } from "./PowerSide";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Datacenter tracker" };  // session 203: renamed (the roadmap's ruling of 12 October 2026); "Datacenters" is the cost-of-power page's name in the menu now

// Session 240: on the brand (components/Brand.tsx, app/tokens.css), with a top block under the title (the facilities
// held, the megawatts stated with what the sum counts, and what changed this week) and the list grouped by operator.
// The words about scope and method, which stood above the numbers, now stand between the top block and the list.
// Session 241: the one tracker. What /datacenters/v2 showed (session 106: ERCOT's large-load status, and the Texas sites
// beside it) is drawn here, between the top block and the words about the list (./LargeLoad.tsx); /datacenters/v2
// redirects to this page (next.config.ts). The section is drawn whether or not the facilities table could be read.
// Session 468: two views, the facilities (the page's own address) and the tracker by grid (?view=grids, lib/tabs.ts).
export default async function DatacentersPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const view = one(await searchParams).view === "grids" ? "grids" : "facilities";
  const queues = await attempt(queueSites);   // session 467: the sites a public source names, read from the queues themselves
  const header = (
    <ToolHeader
      title="Datacenter power tracker"
      lead={<>
        Datacenter facilities from three sources: the energy news since 2025-01-01 (the stories the ERW scores), the public site lists of nine
        operators, and interconnection queue positions that name a datacenter or a large load. Who runs or builds them, where, how many megawatts and
        how they will be powered.
      </>}
    />
  );
  if (view === "grids") {
    const grids = queues.ok ? [...new Set(queues.data.rows.map((r) => gridOfTable(r.table_name)))] : [];
    const active = await attempt(() => queueActive(grids));
    const priceTables = grids.flatMap((g) => (INDEX.grids[g]?.regions ?? []).flatMap((r) => [...(r.rt?.tables ?? []), ...(r.da?.tables ?? [])]));
    return (
      <Brand>
        <ToolPage>
          {header}
          <Tabs page="/datacenters" active="grids" />
          <GridsView sites={queues} active={active} />
          <TableDownloads tables={[...grids.map((g) => `${g}_interconnection_queue`), ...priceTables]} />
          <Related href="/datacenters" />
        </ToolPage>
      </Brand>
    );
  }
  const res = await attempt(datacenters);
  const today = new Date().toISOString().slice(0, 10);   // the UTC day the page was drawn on: "this week" is the seven days to it
  const words = (
    <>
      <p className="mb-2 max-w-3xl text-sm">
        Scope: the news since 2025-01-01; the site lists of Amazon Web Services, Microsoft Azure, Google, Meta, Oracle, Digital Realty, Equinix, Vantage
        and Switch (QTS, CoreWeave and Crusoe publish none that can be read); and the six ISO queues. This is not a census of every facility.
      </p>
      <p className="mb-8 max-w-3xl text-sm text-muted">
        A news facility is extracted from the stories&apos; titles and summaries by a model, and every value was checked against the text; an
        operator&apos;s site is read from its own page, with MW only where the page states it. Nothing is inferred, so a field no source states is
        blank. A facility found by several stories, or by the news and an operator&apos;s list (same operator and place), is one row with every source
        linked. Placed facilities are also on the <Link href="/map">project map</Link>. What a datacenter pays for wholesale energy in each ISO:
        the <Link href="/cost-of-power">cost of power</Link> calculator. <Link href="/data/methods/datacenter_facilities">Method</Link>.
      </p>
    </>
  );
  return (
    <Brand>
      <ToolPage>
        {header}
        <Tabs page="/datacenters" active="facilities" />
        {!res.ok ? (
          <><NoData what="datacenters" reason={res.reason} /><DatacentersPublicLine /><LargeLoad read={res} />{words}</>
        ) : res.data.length === 0 ? (
          <>
            {/* session 500: a table held by row with no public row says so, then how many are held */}
            <NoData what="datacenters" reason={licenseNeeded("datacenter_facilities") && licenseByRow("datacenter_facilities") ? "no row of datacenter_facilities rests on a public source alone" : "datacenter_facilities has no rows in the live set yet"} />
            <HeldRows shape="entities" table="datacenter_facilities" shown={0} method="/data/methods/datacenter_facilities" />
            <LargeLoad read={res} />{words}
          </>
        ) : (
          <>
            {/* session 500: held by row, the public rows are shown and the held ones counted (nothing here until the mark) */}
            <HeldRows shape="entities" table="datacenter_facilities" shown={res.data.length} method="/data/methods/datacenter_facilities" />
            <Body rows={res.data.map(toFacility)} today={today}><LargeLoad read={res} />{words}</Body>
          </>
        )}
        {/* session 467: on the power side, drawn whether or not the facilities table can be read (it is held since 21 October 2026) */}
        <PowerSide read={queues} />
        <LargeLoadSource />
        {/* session 329: the tracker's public tables, as CSV with a Python and a Stata reader (session 328's shared line) */}
        <TableDownloads tables={["datacenter_facilities", "datacenter_operator_sites", "datacenter_projects", "ercot_large_load_status"]} />
        <Related href="/datacenters" />
      </ToolPage>
    </Brand>
  );
}
