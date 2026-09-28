import type { Metadata } from "next";
import { Related } from "@/components/Related";
import { Term } from "@/components/Term";
import { NoData } from "@/components/NoData";
import { datacenterPoints, projectPoints } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { Body } from "./Body";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Project map" };

export default async function MapPage() {
  const res = await attempt(projectPoints);
  // the datacenter power tracker's facilities, the fourth kind; the map stands without them
  const dc = await attempt(datacenterPoints);
  return (
    <>
      <h1 className="mb-1 text-3xl">Energy project map</h1>
      <p className="mb-2 max-w-3xl">
        Every operating and planned generator in <Term t="EIA" first />&apos;s monthly inventory, every active interconnection queue position of six <Term t="ISO" first />s, and
        datacenters named in the news, on one map, from EIA-860M, the ISOs&apos; queue reports and the news the ERW scores.
      </p>
      <p className="mb-2 max-w-3xl text-sm">
        Scope: datacenters are news-derived since 2025-10-01, plus the ISOs&apos; queues; this is not a census of every facility.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        The queues are those of <Term t="ERCOT" first />, <Term t="CAISO" first />, <Term t="NYISO" first />, <Term t="MISO" first />, <Term t="SPP" first /> and <Term t="ISO-NE" first />. EIA gives each plant&apos;s coordinates. The ISOs give only a county, so a queue position is drawn at its county&apos;s
        internal point from the Census Bureau&apos;s gazetteer, as a ring rather than a dot. Withdrawn queue positions are not on the map. Datacenters
        named in the news are the fourth kind.
      </p>
      {!res.ok ? (
        <NoData what="the project map" reason={res.reason} />
      ) : res.data.length === 0 ? (
        <NoData what="the project map" reason="energy_projects has no rows in the live set yet" />
      ) : (
        <Body rows={dc.ok ? [...res.data, ...dc.data.map((p) => ({ ...p, kind: "datacenter" }))] : res.data} />
      )}
      <Related href="/map" />
    </>
  );
}

