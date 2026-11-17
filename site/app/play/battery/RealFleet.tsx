// Energy Research Warehouse (ERW) site, session 7551 (chain 304, part B, the read of /play/battery): the fleet section's
// cards, moved out of page.tsx (a page file may not export a component) so that they draw to HTML for the read's test
// (site/scripts/test-battery-game-read.mjs). Session 46 drew the game's fictional fleet beside ERCOT's real one; the read
// (row 4) adds CAISO's, since two of the game's days are California's, and says that both real fleets are the EIA's latest
// monthly inventory, not the fleet on the day played. ERCOT's card, its keys and its words are as they were.
import { Num } from "@/components/Num";
import { shown } from "@/lib/format";
import { FLEET, FLEET_MW, FLEET_MWH } from "@/lib/battery";
import type { StorageUnit } from "@/lib/data";

const GRIDS = ["ERCOT", "CAISO"] as const;
const AS_OF = "The EIA's latest monthly inventory of generators (EIA-860M), as the warehouse holds it: the fleet operating now, not on the day the game replays. A battery counts where its balancing authority is the grid.";

/** One grid's operating battery fleet: nameplate MW, units, and the MWh where the EIA gives an energy capacity. */
export function fleetOf(units: StorageUnit[], iso: string) {
  const op = units.filter((u) => u.iso === iso && u.status === "operating");
  const mw = Math.round(op.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
  const withMwh = op.filter((u) => u.mwh !== null && u.mwh !== "");
  const mwh = Math.round(withMwh.reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;
  return { n: op.length, mw, mwh, nMwh: withMwh.length };
}

export function RealFleet({ units }: { units: StorageUnit[] }) {
  const cell = "border border-rule bg-panel p-3";
  const fleets = GRIDS.map((iso) => ({ iso, ...fleetOf(units, iso) }));
  return (
    <div className="grid gap-3 sm:grid-cols-3" data-real-fleet>
      <div className={cell}>
        <div className="text-xs text-muted">The game&apos;s fleet (fictional)</div>
        <div className="text-2xl tabular-nums"><Num check="battery|fleet_mw" raw={FLEET_MW}>{shown(FLEET_MW)}</Num> <span className="text-sm text-muted">MW</span></div>
        <div className="text-sm">
          <Num check="battery|fleet_mwh" raw={FLEET_MWH}>{shown(FLEET_MWH)}</Num> MWh: {FLEET.toLocaleString("en-US")} homes, each 5 kW and 13.5 kWh (an assumption)
        </div>
      </div>
      {fleets.map((f) => (
        <div key={f.iso} className={cell} data-real-fleet-grid={f.iso}>
          <div className="text-xs text-muted">
            {f.iso}&apos;s real battery fleet, operating (EIA-860M,{" "}
            <span className="cursor-help border-b border-dotted border-muted" title={AS_OF}>the latest inventory</span>)
          </div>
          {f.n ? (
            <>
              <div className="text-2xl tabular-nums"><Num check={`storage|iso_mw|${f.iso}|operating`} raw={f.mw}>{shown(f.mw)}</Num> <span className="text-sm text-muted">MW</span></div>
              <div className="text-sm">
                <Num check={`storage|iso_n|${f.iso}|operating`} raw={f.n}>{f.n.toLocaleString("en-US")}</Num> units;{" "}
                <Num check={`storage|iso_mwh|${f.iso}|operating`} raw={f.mwh}>{shown(f.mwh)}</Num> MWh where EIA gives the energy capacity (
                <Num check={`storage|iso_n_mwh|${f.iso}|operating`} raw={f.nMwh}>{f.nMwh.toLocaleString("en-US")}</Num> units)
              </div>
            </>
          ) : (
            <div className="text-sm">No operating unit of {f.iso} in the inventory read.</div>
          )}
        </div>
      ))}
      <p className="text-sm sm:col-span-3">
        {fleets.filter((f) => f.n).map((f, i) => (
          <span key={f.iso}>
            {i ? "; " : ""}{f.iso}&apos;s real fleet has <Num check={`calc|ratio|storage~iso_mw~${f.iso}~operating|battery~fleet_mw`} raw={f.mw / FLEET_MW}>{shown(f.mw / FLEET_MW)}</Num> times the power of
            the game&apos;s 10,000 homes
          </span>
        ))}
        . A real grid battery is a power plant: it bids into the same real-time market the game replays.
      </p>
    </div>
  );
}
