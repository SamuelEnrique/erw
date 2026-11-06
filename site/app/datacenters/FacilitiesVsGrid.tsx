// Session 2244 (chain 156): the tracker by grid, the facilities against what each grid holds. For each grid, the MW the
// tracker's facilities state (planned, under construction, operating; lib/dcrollups.ts gridLoads) beside the grid's
// peak hour and its operating generators' capacity (grid_peak_vs_capacity, as site/data/siting/headroom.json carries
// it for the All grids tab) and, for ERCOT, its planning reserve margin (ercot_cdr_reserve_margins, the same file).
// The facilities rest on the news and the operators' own pages, held (license needed): under the hold their cells are
// the hold's words with its footnote (the owner's rule for licensed figures), and the grid's public figures stay. A
// grid's reserve margin no source the ERW reads holds (NERC's: its terms were not read, session 666) says so in its
// cell, with the footnote, never an empty cell. Every figure carries its key: dcgrid|<stat>|<grid> (check-values).
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { gridKey, gridLoads, shareOfPeak, type FacRow } from "@/lib/dcrollups";
import { SITING_FILES } from "@/lib/sitingdata";

const GRID_ID: Record<string, string> = { ERCOT: "ercot", CAISO: "caiso", PJM: "pjm", MISO: "miso", SPP: "spp", NYISO: "nyiso", "ISO-NE": "isone" };
const ORDER = ["ERCOT", "PJM", "MISO", "SPP", "CAISO", "NYISO", "ISO-NE"];
const whole = (v: number) => Math.round(v).toLocaleString("en-US");

type Read = { ok: true; data: EntityRow[] } | { ok: false; reason: string };

export function FacilitiesVsGrid({ read, held }: { read: Read; held: boolean }) {
  const h = SITING_FILES.headroom;
  const loads = read.ok && !held ? gridLoads(read.data as unknown as FacRow[]) : [];
  const byGrid = new Map(loads.map((l) => [l.grid, l]));
  const hold = <span className="text-muted">license needed<sup>1</sup></span>;
  const none = <span className="text-muted">none stated</span>;
  const fig = (v: number | null, k: string) => (v === null ? none : <Num check={k} raw={v}>{whole(v)}</Num>);
  return (
    <ToolSection title="The facilities against each grid" id="facilities-vs-grid"
      note={<>The MW the tracker&apos;s facilities state (a named US state, not cancelled), by the grid a story names, else the facility&apos;s queue&apos;s ISO, else the grid that serves most of its state; beside each grid&apos;s peak hour of {h.peak_capacity?.ercot?.year ?? "its last whole year"} and its operating generators&apos; net summer capacity (EIA-930 and EIA-860M, <code className="font-mono">grid_peak_vs_capacity</code>). The share is the planned and under-construction MW over the peak hour: what the facilities state, not what they will draw. <Link href="/data/methods/grid_peak_vs_capacity">Method</Link>.</>}>
      <ToolTable caption="The facilities' stated MW against each grid's peak and capacity" minWidth={900}
        head={["Grid", "Facilities", "Stating MW", "Planned MW", "Under construction MW", "Operating MW", "Peak hour MW", "Capacity MW", "Planned and building, % of peak", "Reserve margin"]}
        rows={ORDER.map((g) => {
          const id = GRID_ID[g], pc = h.peak_capacity?.[id], l = byGrid.get(g) ?? null, rm = h.reserve?.grids?.[id];
          const share = l && pc ? shareOfPeak(l, pc.peak_mw) : null;
          return {
            key: g,
            cells: [
              g,
              held ? hold : l ? <Num key="f" check={gridKey("facilities", g)} raw={l.facilities}>{whole(l.facilities)}</Num> : "0",
              held ? hold : l ? <Num key="w" check={gridKey("with_mw", g)} raw={l.withMw}>{whole(l.withMw)}</Num> : "0",
              held ? hold : l ? fig(l.planned, gridKey("planned", g)) : none,
              held ? hold : l ? fig(l.underConstruction, gridKey("under_construction", g)) : none,
              held ? hold : l ? fig(l.operating, gridKey("operating", g)) : none,
              pc ? <Num key="p" check={gridKey("peak_mw", g)} raw={pc.peak_mw}>{whole(pc.peak_mw)}</Num> : <span key="p" className="text-muted">not held</span>,
              pc ? <Num key="c" check={gridKey("capacity_mw", g)} raw={pc.capacity_mw}>{whole(pc.capacity_mw)}</Num> : <span key="c" className="text-muted">not held</span>,
              held ? hold : share === null ? none : <Num key="s" check={gridKey("share_of_peak", g)} raw={share}>{share.toFixed(1)}</Num>,
              rm ? <span key="r"><Num check={gridKey("reserve_margin", g)} raw={rm.peak.pct}>{rm.peak.pct.toFixed(1)}</Num>% ({rm.peak.label.toLowerCase()})</span>
                : <span key="r" className="text-muted">not held<sup>2</sup></span>,
            ],
          };
        })} />
      <ol className="mt-3 max-w-3xl list-decimal space-y-1 pl-5 text-xs text-muted">
        <li>The facilities rest on news stories and the operators&apos; own pages, whose terms ask for permission; the ERW holds them and shows their count only where a license is recorded (<Link href="/data/methods/datacenter_facilities">method</Link>).</li>
        <li>A grid&apos;s reserve margin is held for ERCOT only (its Capacity, Demand and Reserves report, the first summer after the report); NERC&apos;s assessments of the others are not read while NERC&apos;s terms are not.</li>
      </ol>
    </ToolSection>
  );
}
