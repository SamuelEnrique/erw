import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { NoData } from "@/components/NoData";
import { ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { datacenters } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { Body, toFacility } from "./Body";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Datacenter tracker" };  // session 203: renamed (the roadmap's ruling of 12 October 2026); "Datacenters" is the cost-of-power page's name in the menu now

// Session 240: on the brand (components/Brand.tsx, app/tokens.css), with a top block under the title (the facilities
// held, the megawatts stated with what the sum counts, and what changed this week) and the list grouped by operator.
// The words about scope and method, which stood above the numbers, now stand between the top block and the list.
export default async function DatacentersPage() {
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
        the <Link href="/cost-of-power">cost of power</Link> calculator.
      </p>
    </>
  );
  return (
    <Brand>
      <ToolPage>
        <ToolHeader
          title="Datacenter power tracker"
          lead={<>
            Datacenter facilities from three sources: the energy news since 2025-01-01 (the stories the ERW scores), the public site lists of nine
            operators, and interconnection queue positions that name a datacenter or a large load. Who runs or builds them, where, how many megawatts and
            how they will be powered.
          </>}
        />
        {!res.ok ? (
          <><NoData what="datacenters" reason={res.reason} />{words}</>
        ) : res.data.length === 0 ? (
          <><NoData what="datacenters" reason="datacenter_facilities has no rows in the live set yet" />{words}</>
        ) : (
          <Body rows={res.data.map(toFacility)} today={today}>{words}</Body>
        )}
        <Related href="/datacenters" />
      </ToolPage>
    </Brand>
  );
}
