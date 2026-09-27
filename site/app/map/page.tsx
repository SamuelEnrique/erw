import type { Metadata } from "next";
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
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Every generator in EIA&apos;s monthly inventory (operating and planned) and every interconnection queue position at ERCOT, CAISO, NYISO, MISO, SPP
        and ISO-NE, on one map. EIA gives each plant&apos;s coordinates. The ISOs give only a county, so a queue position is drawn at its county&apos;s
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
    </>
  );
}

