// Energy Research Warehouse (ERW) site, session 1170 (chain 078): a replayed day's figures on the Grid tool, drawn on the
// server from the replay's committed daily file (lib/gridReplay.ts), each with its check key and a one-line source. The
// Grid pack's blind spot 11: the replay holds a daily demand for 54 balancing authorities, so the day picked shows the
// demand of the balancing authority in the address (BPAT as well as the seven ISO grids) where the file holds it, and
// "not held" where it does not. On the Network tab, inside grid_network_<grid>: the node's demand, net exchange and ties
// that day. On the Gravity tab, inside grid_gravity_<grid>: one line, the day's demand of the grid in view, and that the
// shape still draws the live hour (ruling 1a: sized by net generation, held by hour for the live week only). EIA-930's
// daily demand and interchange are public for every grid (site/data/license_status.json): nothing here is held.
import { Num } from "@/components/Num";
import { NoData } from "@/components/NoData";
import { Missing } from "@/components/mix/Now";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { replayDay, type DayFig } from "@/lib/gridReplay";
import type { ReplayRead } from "@/lib/gridReplayFile";

/** The replayed day the address asks for: `day` the day drawn (held to the replay's first and last day, as the network
 *  component holds it), `asked` the address's own word, and the year's file as read. */
export type ReplayAsk = { day: string; asked: string; first: string; last: string; read: ReplayRead };

/** A figure with its key and its one-line source as the hover tip, written whole as its key's form says. */
function D({ f }: { f: DayFig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{f.text}</Num>
    </span>
  );
}

const moved = (a: ReplayAsk) => (a.asked !== a.day ? <> The address asks for {a.asked}; the replay holds {a.first} to {a.last}, so it opens on {a.day}.</> : null);

/** The Network tab: the balancing authority in the address on the day picked. */
export function ReplayDayFigures({ ask, ba, name }: { ask: ReplayAsk; ba: string; name: string }) {
  const title = `${name}, the day picked (${ask.day}, EIA's Eastern day)`;
  if (!ask.read.ok) {
    return (
      <div data-grid-replay-day={ba} data-replay-day={ask.day}>
        <ToolSection title={title}><NoData what={`${name}'s figures of ${ask.day}`} reason={ask.read.why} /></ToolSection>
      </div>
    );
  }
  const r = replayDay(ask.read.y, ba, ask.day);
  const not = <Missing words="not held" why={r.demandWhy ?? ""} />;
  return (
    <div data-grid-replay-day={ba} data-replay-day={ask.day}>
      <ToolSection title={title}
        note={<>From the replay&apos;s committed file of {ask.day.slice(0, 4)}, built from EIA-930&apos;s daily demand and interchange (public domain): a day&apos;s figure is its MWh over the hours of EIA&apos;s Eastern day, the day&apos;s average MW, so it reads on the scale of an hour. The file holds a daily demand for {r.withDemand} balancing authorities; where it holds none for {name} that day, the cell says not held. A tie&apos;s flow is signed from {name}&apos;s side. These are the figures of the day in the address when the page was opened: a day picked in the replay above moves the address, and the page opened again draws that day here.{moved(ask)} Hover a figure for its file, filter and day.</>}>
        {r.inFile ? (
          <ToolTable caption={`${name} on ${ask.day}, from the replay's daily file`} minWidth={420} head={["The day picked", "MW, the day's average", "Source"]}
            rows={[
              { key: "dem", cells: ["Demand", r.demand ? <D key="v" f={r.demand} /> : not, "eia930_daily_demand"] },
              { key: "net", cells: [r.net?.kind === "import" ? "Net import over the ties" : "Net export over the ties", r.net ? <D key="v" f={r.net} /> : <span key="v" className="text-muted">no tie reported</span>, "eia930_daily_interchange"] },
              { key: "ties", cells: ["Ties with a flow that day", <D key="v" f={r.ties} />, "eia930_daily_interchange"] },
            ]} />
        ) : <NoData what={`${name}'s figures of ${ask.day}`} reason={r.demandWhy ?? `${ask.day} is not a day of the replay's file`} />}
      </ToolSection>
    </div>
  );
}

/** The Gravity tab: one line under the table, the day's demand of the grid in view. */
export function ReplayDayDemand({ ask, ba, label }: { ask: ReplayAsk; ba: string; label: string }) {
  const shape = <> The shape above still draws the live hour: it is sized by net generation (ruling 1a), which is held by hour for the live week only, not by day.</>;
  if (ba === "US48") {
    return (
      <p className="mt-3 max-w-3xl text-sm" data-gravity-day={ask.day}>
        The day picked in the replay, {ask.day}: the Lower 48&apos;s demand that day is <Missing words="not held" why="the replay's files hold a daily demand for each balancing authority, not for the Lower 48 as a whole" />.{shape}{moved(ask)}
      </p>
    );
  }
  const r = ask.read.ok ? replayDay(ask.read.y, ba, ask.day) : null;
  return (
    <p className="mt-3 max-w-3xl text-sm" data-gravity-day={ask.day}>
      The day picked in the replay, {ask.day} (EIA&apos;s Eastern day): {r?.demand
        ? <>{label}&apos;s demand averaged <D f={r.demand} /> MW, from the replay&apos;s committed file of EIA-930&apos;s daily demand.</>
        : <>{label}&apos;s demand that day is <Missing words="not held" why={r?.demandWhy ?? (ask.read.ok ? "" : ask.read.why)} />.</>}{shape}{moved(ask)}
    </p>
  );
}
