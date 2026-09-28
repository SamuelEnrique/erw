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
        Datacenter facilities from three sources: the energy news since 2025-01-01 (the stories the ERW scores), the public site lists of nine
        operators, and interconnection queue positions that name a datacenter or a large load. Who runs or builds them, where, how many megawatts and
        how they will be powered.
      </p>
      <p className="mb-2 max-w-3xl text-sm">
        Scope: the news since 2025-01-01; the site lists of Amazon Web Services, Microsoft Azure, Google, Meta, Oracle, Digital Realty, Equinix, Vantage
        and Switch (QTS, CoreWeave and Crusoe publish none that can be read); and the six ISO queues. This is not a census of every facility.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        A news facility is extracted from the stories&apos; titles and summaries by a model, and every value was checked against the text; an
        operator&apos;s site is read from its own page, with MW only where the page states it. Nothing is inferred, so a field no source states is
        blank. A facility found by several stories, or by the news and an operator&apos;s list (same operator and place), is one row with every source
        linked. Placed facilities are also on the <Link href="/map">project map</Link>.
      </p>
      {!res.ok ? (
        <NoData what="datacenters" reason={res.reason} />
      ) : res.data.length === 0 ? (
        <NoData what="datacenters" reason="datacenter_facilities has no rows in the live set yet" />
      ) : (
        <Body rows={res.data.map(toFacility)} />
      )}
      <Related href="/datacenters" />
    </>
  );
}

