import type { Metadata } from "next";
import { Related } from "@/components/Related";
import Link from "next/link";
import { NoData } from "@/components/NoData";
import { datacenters } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { Body, toFacility } from "./Body";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Datacenters" };

export default async function DatacentersPage() {
  const res = await attempt(datacenters);
  return (
    <>
      <h1 className="mb-1 text-3xl">Datacenter power tracker</h1>
      <p className="mb-2 max-w-3xl">
        Datacenter facilities named in the energy news since 2025-10-01, from the stories the ERW scores: who runs or builds them, where, how many
        megawatts and how they will be powered.
      </p>
      <p className="mb-2 max-w-3xl text-sm">
        Scope: news-derived since 2025-10-01, plus the ISOs&apos; queues on the <Link href="/map">project map</Link>; this is not a census of every facility.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        For each: who runs or builds it, where, how many megawatts, their status and how they
        will be powered. Each facility is extracted from the stories&apos; titles and summaries by a model, and every value was checked against the text:
        nothing is inferred, so a field the stories do not state is blank. A facility reported by several stories is one row, with every story linked.
        Facilities with a stated county or city are also on the <Link href="/map">project map</Link>.
      </p>
      {!res.ok ? (
        <NoData what="datacenters" reason={res.reason} />
      ) : res.data.length === 0 ? (
        <NoData what="datacenters" reason="datacenter_projects has no rows in the live set yet" />
      ) : (
        <Body rows={res.data.map(toFacility)} />
      )}
      <Related href="/datacenters" />
    </>
  );
}

