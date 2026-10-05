import type { ReactNode } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { kw, list, monthName, pct, span, usd, whole } from "@/lib/storageawards";
import { BASIS_TABLE, RT_TABLE, rtAncillary, rtEnergy, rtTotal, type Basis, type RtMonth } from "@/lib/storagerealtime";

// Session 120: the real-time side, one section added to /cost-of-power/battery/awards. What the fleet did in real time,
// from ercot_storage_rt_monthly (warehouse/derived, from the file 60d_ESR_Data_in_SCED of ERCOT's 60-Day SCED Disclosure
// Reports, set beside the day-ahead awards of the same days), and how far the storage settlement points' prices stand
// from the hub's, from ercot_storage_node_basis (the one week of node prices ERCOT's public list holds). Every figure is
// computed by lib/storagerealtime.ts from those rows when the page is rendered; no partial month is scaled or set beside
// the model, and a table that could not be read shows a sentence and no number. What the section leaves out is stated
// first. Every real-time dollar is at the hub average's price and is labeled so: ERCOT settles at the resource's own
// node, and the node price of a disclosed day is not public. In review with the page.

export const RT_METHOD = "/data/methods/ercot_storage_realtime";
const TITLE = "The real-time side: what the fleet did after the day-ahead market closed";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const signed = (usdPerMw: number) => (usdPerMw > 0 ? "+" : "") + kw(usdPerMw);
const mwh = (v: number) => Math.round(v).toLocaleString("en-US");
const notHeld = <span className="text-muted">not held</span>;

export function RealTimeSection({ months, basis, unread, basisUnread }: {
  /** the months of the real-time table, oldest first; empty when it is not loaded */
  months: RtMonth[];
  /** the week of node prices against the hub; null when that table gave no row */
  basis: Basis | null;
  /** why the real-time table could not be read, when it could not */
  unread: string | null;
  /** why the node table could not be read, when it could not */
  basisUnread: string | null;
}) {
  const leftOut = (
    <div className="max-w-3xl space-y-2 text-sm" data-rt-not="1">
      <p><strong>What this still leaves out.</strong> It is still not what any battery earned. Not in these files, and so not in any figure below:</p>
      <ul className="list-disc space-y-1.5 pl-4">
        <li><strong>Contracts.</strong> A toll, a hedge or a capacity sale outside ERCOT&apos;s markets. For a battery under contract that is income these markets do not show, and no public file holds it.</li>
        <li><strong>The price at each battery&apos;s own node.</strong> ERCOT settles real-time energy at the resource&apos;s node, and charging at the price at its bus. Its public list keeps seven days of node
          prices and this disclosure is 60 days old when it is posted, so the node price of a disclosed day is not public. Real-time energy is valued here at the hub average&apos;s price, a stand-in, and every such
          figure says so. One node&apos;s price can move more than the hub average&apos;s, which is an average of many: the last part of this section measures the difference.</li>
        <li><strong>Real-time ancillary service money.</strong> The file holds each resource&apos;s real-time awards, and ERCOT settles the difference from its day-ahead awards at real-time prices that neither
          file holds. The quantities are shown and not valued.</li>
        <li><strong>Charges and credits of the settlement statement.</strong> Set point deviation charges, make-whole payments, uplift and fees.</li>
        <li><strong>The meter.</strong> Real-time energy here is telemetry integrated between dispatch runs, about five minutes apart. ERCOT settles on the meter, which this disclosure does not hold for storage.</li>
      </ul>
    </div>
  );

  let body: ReactNode;
  if (unread !== null) {
    body = <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status" data-rt-state="unread">The real-time table could not be read, so no number is shown in this section: {unread}</p>;
  } else if (!months.length) {
    body = <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status" data-rt-state="not-loaded">The real-time table could not be read: <code className="font-mono">{RT_TABLE}</code> is
      not loaded in the site&apos;s database, so no number is shown in this section.</p>;
  } else {
    const ms = months;
    const total = rtTotal(ms), energy = rtEnergy(ms), anc = rtAncillary(ms);
    const partial = ms.filter((r) => !r.complete);
    const first = ms[0], last = ms[ms.length - 1];
    body = (
      <div className="space-y-6" data-rt-months={ms.map((r) => r.m).join(",")}>
        <div className="max-w-3xl space-y-2 text-sm">
          <p data-rt-coverage="1">Held: {span(ms.map((r) => r.m))}, {whole(ms.reduce((a, r) => a + r.daysHeld, 0))} operating days. ERCOT&apos;s market change of 5 December 2025 put a battery in the real-time
            market as one resource. The disclosure from 6 December on is larger than this pull&apos;s download ceiling, so the most recent months that fit were taken and the earlier weeks were not:
            nothing stands in for them.{partial.length ? ` ${list(partial.map((r) => `${monthName(r.m)} holds ${r.daysHeld} of ${r.daysInMonth} days`))}; a partial month is the held days' sum and is never scaled.` : ""}</p>
          {total ? (
            <p data-rt-summary="1">Over {span(total.months)}, the months held whole, the fleet&apos;s day-ahead awards come to USD {usd(total.dayAhead / 1000)} per kW. What it did in real time beyond its
              day-ahead position, at the hub average&apos;s price, {total.deviationHub >= 0 ? "adds" : "takes off"} USD {usd(Math.abs(total.deviationHub) / 1000)}, for USD {usd(total.marketHub / 1000)} per kW in the two
              energy markets and day-ahead ancillary services together.{total.model !== null ? <> The model&apos;s 2-hour battery on its day-ahead schedule makes USD {usd(total.model / 1000)} over the same months.</> : null}</p>
          ) : (
            <p data-rt-summary="none">No month is held whole yet, so no figure is set beside the model: {list(ms.map((r) => `${monthName(r.m)} holds ${r.daysHeld} of ${r.daysInMonth} days`))}.</p>
          )}
        </div>

        <div data-rt-table="1">
        <ToolTable caption="Day-ahead awards and real-time deviations by month" minWidth={900}
          head={["Month", "Days held", "MW",
            <>Day-ahead awards<span className="mt-0.5 block text-xs opacity-80">the floor, USD per kW</span></>,
            <>Real-time deviations<span className="mt-0.5 block text-xs opacity-80">at the hub average&apos;s price, USD per kW</span></>,
            <>The two together<span className="mt-0.5 block text-xs opacity-80">real time at the hub average&apos;s price, USD per kW</span></>,
            <>The model&apos;s<span className="mt-0.5 block text-xs opacity-80">2-hour battery, day-ahead schedule, USD per kW</span></>,
            "The two together as a share of the model's"]}
          rows={[...ms].reverse().map((r) => ({
            key: r.m, muted: !r.complete,
            cells: [
              <span key="m" data-rt-month={r.m}>{monthName(r.m)}{r.complete ? null : <span className="block text-xs">partial</span>}</span>,
              `${r.daysHeld} of ${r.daysInMonth}`,
              r.mw === null ? notHeld : whole(r.mw),
              <span key="d" data-rt-dayahead={r.m} data-rt-raw={r.dayAhead}>{kw(r.dayAhead)}</span>,
              <span key="v" data-rt-deviation={r.m} data-rt-raw={r.deviationHub}>{signed(r.deviationHub)}</span>,
              <span key="t" data-rt-market={r.m} data-rt-raw={r.marketHub}>{kw(r.marketHub)}</span>,
              !r.complete ? <span key="x" className="text-muted">not set beside a partial month</span>
                : r.model === null ? notHeld
                : !r.model.whole ? <span key="x" className="text-muted">the model&apos;s month is partial</span>
                : <span key="x" data-rt-model={r.m} data-rt-raw={r.model.total}>{kw(r.model.total)}</span>,
              r.complete && r.model !== null && r.model.whole && r.model.total > 0 ? pct(r.marketHub / r.model.total) : "",
            ],
          }))} />
        </div>
        <ul className="max-w-3xl list-disc space-y-1.5 pl-4 text-sm">
          <li><strong>Day-ahead awards.</strong> The same figure as in the tables above, over the days both disclosures hold: energy awards at the day-ahead price of the resource&apos;s own settlement point, and each
            ancillary service award at its day-ahead clearing price.</li>
          <li><strong>Real-time deviations.</strong> For each resource and each 15-minute interval, the energy it put out less a quarter of its day-ahead award of that hour, times the interval&apos;s real-time price
            at the hub average. Energy sold day-ahead and delivered adds nothing here. Energy delivered and not sold day-ahead is paid the real-time price; energy sold day-ahead and not delivered is bought back at it.</li>
          <li><strong>The model&apos;s.</strong> The battery page&apos;s figure, not ERCOT&apos;s: one 2-hour battery scheduled without error against day-ahead prices at the hub average. It has no real-time side.</li>
        </ul>

        {energy ? (
          <div>
            <h3 className="mb-2 font-serif text-lg">How much of what the fleet did was sold day-ahead</h3>
            <div className="mb-3 max-w-3xl space-y-2 text-sm">
              <p data-rt-energy="1">Over the {whole(energy.days)} days held, the fleet discharged {mwh(energy.discharged)} MWh in real time and had sold {mwh(energy.sold)} MWh day-ahead
                {energy.soldOfDischarged !== null ? <>: {pct(energy.soldOfDischarged)} of what it put out</> : null}. It charged {mwh(energy.charged)} MWh and had bought {mwh(energy.bought)} MWh day-ahead.
                {energy.dischargedPerMwDay !== null ? <> That is {two(energy.dischargedPerMwDay)} MWh discharged per MW of the fleet per day; a 2-hour battery emptied once a day would discharge two.</> : null}
                {energy.pricedShare !== null ? <> A hub price was held for {pct(energy.pricedShare, 2)} of the resource-intervals; the rest are not valued.</> : null}</p>
            </div>
            <ToolTable caption="Real-time energy and day-ahead energy by month, MWh" minWidth={760}
              head={["Month", "Discharged in real time, MWh", "Sold day-ahead, MWh", "Sold day-ahead as a share of discharged", "Charged in real time, MWh", "Bought day-ahead, MWh",
                <>Node less hub, day-ahead<span className="mt-0.5 block text-xs opacity-80">USD per MWh: on energy sold; on energy bought</span></>]}
              rows={[...ms].reverse().map((r) => ({
                key: r.m, muted: !r.complete,
                cells: [
                  monthName(r.m),
                  r.discharged === null ? notHeld : <span key="o" data-rt-discharged={r.m} data-rt-raw={r.discharged}>{mwh(r.discharged)}</span>,
                  r.sold === null ? notHeld : mwh(r.sold),
                  r.sold === null || r.discharged === null || r.discharged <= 0 ? "" : pct(r.sold / r.discharged),
                  r.charged === null ? notHeld : mwh(r.charged),
                  r.bought === null ? notHeld : mwh(r.bought),
                  r.nodeLessHubSold === null || r.nodeLessHubBought === null ? notHeld : `${usd(r.nodeLessHubSold)}; ${usd(r.nodeLessHubBought)}`,
                ],
              }))} />
            <p className="mt-3 max-w-3xl text-sm">The last column is the first measure of what the hub price misses. It is day-ahead, where the warehouse holds both prices: the price at the resources&apos; own
              settlement points less the hub average&apos;s, weighted by the MWh sold and by the MWh bought. Selling above the hub and buying below it is what a node that moves more than the hub gives a battery.</p>
          </div>
        ) : null}

        {anc.length ? (
          <div>
            <h3 className="mb-2 font-serif text-lg">Real-time ancillary awards: held, and not valued</h3>
            <ToolTable caption="Ancillary service awards in real time and day-ahead, MW for an hour" minWidth={620}
              head={["Service", "Awarded in real time", "Awarded day-ahead", "Real time less day-ahead"]}
              rows={anc.map((a) => ({ key: a.key, cells: [<span key="s" data-rt-service={a.key}>{a.label}</span>, mwh(a.realTime), mwh(a.dayAhead),
                <span key="i" data-rt-imbalance={a.key} data-rt-raw={a.imbalance}>{(a.imbalance > 0 ? "+" : "") + mwh(a.imbalance)}</span>] }))} />
            <p className="mt-3 max-w-3xl text-sm">Each figure is a MW awarded for an hour, added up over {span(ms.map((r) => r.m))}, {first.m === last.m ? "the month" : "every month"} held. Since 5 December 2025 ERCOT awards ancillary
              services in real time as well, at each dispatch run, and pays or charges a resource the difference between its real-time award and its day-ahead award at the service&apos;s real-time price.
              The awards are in the disclosure; that price is not, and the warehouse does not hold it. So the last column is the quantity that settlement moves, with no dollar figure put on it.</p>
          </div>
        ) : null}

        <div data-rt-basis={basis ? "1" : "none"}>
          <h3 className="mb-2 font-serif text-lg">What the hub price misses: one real week at the batteries&apos; own nodes</h3>
          {basisUnread !== null ? (
            <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table of node prices against the hub could not be read, so no number is shown here: {basisUnread}</p>
          ) : basis === null ? (
            <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table <code className="font-mono">{BASIS_TABLE}</code> is not loaded in the site&apos;s database, so no number is shown here.</p>
          ) : (
            <div className="max-w-3xl space-y-2 text-sm">
              <p>This is the second measure, and it is real time. It is not from the months above: it is the week of node prices ERCOT&apos;s public list held when it was read,
                from {new Date(`${basis.from}T12:00:00Z`).toLocaleString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })}, at the {whole(basis.nodes)} settlement points storage resources are settled at.</p>
              {basis.spreadHub !== null && basis.spreadMedian !== null && basis.wholeDays !== null && basis.nodesWithSpread !== null ? (
                <p data-rt-spread="1">Take a day&apos;s four dearest hours of real-time prices less its four cheapest: what moving four hours of energy a day could capture, before losses. Over the {whole(basis.wholeDays)} whole
                  days held, that spread averaged USD {two(basis.spreadHub)} per MWh at the hub average. At the storage settlement points the median was USD {two(basis.spreadMedian)}
                  {basis.spreadP10 !== null && basis.spreadP90 !== null ? <>, with the middle eight tenths of them between USD {two(basis.spreadP10)} and USD {two(basis.spreadP90)}</> : null}
                  {basis.aboveHub !== null ? <>; at {whole(basis.aboveHub)} of {whole(basis.nodesWithSpread)} points it was wider than the hub&apos;s</> : null}.</p>
              ) : null}
              {basis.meanAbsDifference !== null ? (
                <p>At the median point, the real-time price stood USD {two(basis.meanAbsDifference)} per MWh away from the hub average in the average interval, one way or the other.</p>
              ) : null}
              <p>One week is one week. It says which way the stand-in errs and roughly by how much in one week of early autumn; it is not applied to any figure above, and nothing above is adjusted by it.
                To value a disclosed day at its own node, the node prices have to be kept from the day they are posted, before the list drops them.</p>
            </div>
          )}
        </div>
      </div>
    );
  }
  return (
    <ToolSection title={TITLE} id="real-time" note={<>From ERCOT&apos;s 60-Day SCED Disclosure, 60 days after each day: each storage resource&apos;s telemetered output, state of charge and real-time awards at every
      dispatch run, reduced to hours and 15-minute intervals and set beside its day-ahead awards of the same days, per kW of the fleet&apos;s MW. <Link href={RT_METHOD}>Method</Link>.</>}>
      <div className="space-y-6">
        {leftOut}
        {body}
      </div>
    </ToolSection>
  );
}
