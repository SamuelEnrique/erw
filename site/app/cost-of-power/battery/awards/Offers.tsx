import type { ReactNode } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { OFFERS_TABLE, list, pct, span, usd, whole, type Gap } from "@/lib/storageawards";

// Session 116: the one section added to /cost-of-power/battery/awards. What the fleet offered day-ahead, from
// ercot_storage_dam_offers_monthly (warehouse/derived, from the Energy Bid/Offer Curves of ERCOT's 60d_DAM_ESR_Data and
// the offer blocks of 60d_DAM_ESR_ASOffers), and the gap between the awards and the model's figure split in three:
// capacity that offered nothing day-ahead, capacity offered and not awarded, and price. Every figure is computed by
// lib/storageawards.ts (gapOf) from the three tables when the page is rendered, over the months all three hold whole;
// no partial month is scaled, and a table that could not be read shows a sentence and no number. The model's figures
// are labeled as the model's. In review with the page.

export const OFFERS_METHOD = "/data/methods/ercot_storage_dam_offers";
const TITLE = "Where the gap comes from: what was offered day-ahead";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const points = (v: number) => (v * 100).toFixed(1);

export function OffersSection({ gap, unread, loaded }: {
  /** the arithmetic's result; null when no month is held whole by all three tables */
  gap: Gap | null;
  /** why the offers table (or the model's rows) could not be read, when it could not */
  unread: string | null;
  /** the offers table gave at least one row */
  loaded: boolean;
}) {
  let body: ReactNode;
  if (unread !== null) {
    body = <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status" data-offers-state="unread">The offers table could not be read, so no number is shown in this section: {unread}</p>;
  } else if (!loaded) {
    body = <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status" data-offers-state="not-loaded">The offers table could not be read: <code className="font-mono">{OFFERS_TABLE}</code> is
      not loaded in the site&apos;s database, so no number is shown in this section.</p>;
  } else if (gap === null) {
    body = <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status" data-offers-state="no-whole-month">No month is held whole by the awards, the offers and the model together, so the gap
      is not split: a partial month is never set beside the model.</p>;
  } else {
    const g = gap, e = g.energy;
    const of = (v: number) => (g.gapKw !== 0 ? pct(v / g.gapKw) : "");
    const months = span(g.months);
    const withGap = g.services.filter((s) => s.gapKw > 0);
    const covered = withGap.filter((s) => s.unawardedKw >= s.gapKw), short = withGap.filter((s) => s.unawardedKw < s.gapKw);
    const noGap = g.services.filter((s) => s.gapKw <= 0);
    const lo = Math.min(...g.services.map((s) => s.awardOfOffer)), hi = Math.max(...g.services.map((s) => s.awardOfOffer));
    const soldOfClearing = e.atClearingPerMwDay > 0 ? e.soldPerMwDay / e.atClearingPerMwDay : null;
    body = (
      <div className="space-y-6" data-offers-gap="1" data-offers-months={g.months.join(",")}>
        <div className="max-w-3xl space-y-2 text-sm">
          <p>Over {months}, the model&apos;s 2-hour battery makes USD {usd(g.modelKw)} per kW on its day-ahead schedule and the fleet&apos;s day-ahead awards come to USD {usd(g.awardsKw)} per kW:
            a gap of USD {usd(g.gapKw)}. The offers ERCOT discloses split it in three.</p>
        </div>
        <ToolTable caption="The gap between the model's figure and the awards, in three parts" minWidth={520}
          head={["Of the gap", "USD per kW", "Share of the gap"]}
          rows={[
            { key: "never", cells: ["Capacity never offered day-ahead", <span key="v" data-offers-part="never" data-offers-raw={g.neverOfferedKw}>{usd(g.neverOfferedKw)}</span>, of(g.neverOfferedKw)] },
            { key: "unawarded", cells: ["Offered day-ahead and not awarded", <span key="v" data-offers-part="unawarded" data-offers-raw={g.offeredNotAwardedKw}>{usd(g.offeredNotAwardedKw)}</span>, of(g.offeredNotAwardedKw)] },
            { key: "price", cells: ["Price", <span key="v" data-offers-part="price" data-offers-raw={g.priceKw}>{usd(g.priceKw)}</span>, of(g.priceKw)] },
            { key: "gap", highlight: true, cells: ["The gap: the model's figure less the awards", <span key="v" data-offers-part="gap" data-offers-raw={g.gapKw}>{usd(g.gapKw)}</span>, of(g.gapKw)] },
          ]} />
        <ul className="max-w-3xl list-disc space-y-1.5 pl-4 text-sm">
          <li><strong>Never offered.</strong> {points(g.noOfferShare)} percent of the fleet&apos;s limit-hours (each resource&apos;s limit, hour by hour) carried no day-ahead offer of any kind, no energy curve and no
            ancillary service offer; {points(g.noOfferOutShare)} points of that were resources on outage. That share of the model&apos;s USD {usd(g.modelKw)} is USD {usd(g.neverOfferedKw)}.
            <span data-offers-allocation="1"> This part is an allocation, not a measurement: it assumes the hours and resources that offered nothing would have made the model&apos;s average.</span></li>
          <li><strong>Price.</strong> Energy only. On each MWh it sold day-ahead the fleet netted USD {two(e.awardsUsdPerMwh)}, against the model&apos;s USD {two(e.modelUsdPerMwh)} on each MWh it discharges,
            so price {g.priceKw < 0 ? "narrows" : "widens"} the gap by USD {usd(Math.abs(g.priceKw))}. In ancillary services there is no price part: every awarded MW is paid the hour&apos;s one clearing price, the same price the model takes.</li>
          <li><strong>Offered and not awarded.</strong> What is left of the gap after the other two. The three add up to the gap exactly, because this part is the remainder: the gap equals never offered,
            plus offered and not awarded, plus price.</li>
        </ul>

        <div>
          <h3 className="mb-2 font-serif text-lg">Energy: what the curves offered to sell, and at what price</h3>
          <div className="mb-3 max-w-3xl space-y-2 text-sm">
            <p data-offers-energy="1">The fleet&apos;s curves offered to sell on {pct(g.energyOfferShare)} of its limit-hours: {one(e.offeredPerMwDay)} MWh per MW per day at any price, against the {two(e.modelPerMwDay)} the
              model&apos;s battery discharges. That is power offered hour by hour, not energy: ERCOT&apos;s file states no state of charge, so it cannot be read as MWh the fleet could have delivered.
              {e.above1000 !== null && e.above100 !== null ? <> Of it, {pct(e.above1000)} was priced above USD 1,000 per MWh and {pct(e.above100)} above USD 100.</> : null}
              {" "}At each hour&apos;s own day-ahead price the curves offered {two(e.atClearingPerMwDay)} MWh per MW per day, and {two(e.soldPerMwDay)} was awarded.
              {soldOfClearing !== null && soldOfClearing >= 0.9 ? <> So the energy that was offered and not awarded was offered at a price the day-ahead market did not reach.</> : null}</p>
          </div>
          <ToolTable caption="What the energy curves offered to sell, by price" minWidth={520}
            head={["Offered to sell", "MWh per MW per day", "Share of all that was offered"]}
            rows={[
              ...e.bands.map((b) => ({ key: `b${b.le ?? "any"}`, cells: [b.le === null ? "at any price" : `at USD ${whole(b.le)} per MWh or less`, two(b.perMwDay), pct(b.shareOfOffered, 1)] as ReactNode[] })),
              { key: "clearing", cells: ["at each hour's own day-ahead price", two(e.atClearingPerMwDay), ""] },
              { key: "sold", highlight: true, cells: ["Awarded: sold day-ahead", two(e.soldPerMwDay), ""] },
              { key: "model", cells: [<>The model&apos;s<span className="block text-xs text-muted">2-hour battery, day-ahead schedule: discharged</span></>, two(e.modelPerMwDay), ""] },
            ]} />
        </div>

        <div>
          <h3 className="mb-2 font-serif text-lg">Ancillary services: offered, awarded, and the unawarded at the clearing price</h3>
          <ToolTable caption="Ancillary services: what was offered and what was awarded" minWidth={980}
            head={["Service",
              <>Offered<span className="mt-0.5 block text-xs opacity-80">share of limit-hours</span></>,
              <>Offered at or below the clearing price<span className="mt-0.5 block text-xs opacity-80">share of limit-hours</span></>,
              <>Awarded<span className="mt-0.5 block text-xs opacity-80">share of limit-hours</span></>,
              "Awarded, share of offered",
              <>Awards<span className="mt-0.5 block text-xs opacity-80">USD per kW</span></>,
              <>The model&apos;s<span className="mt-0.5 block text-xs opacity-80">2-hour battery, day-ahead schedule, USD per kW</span></>,
              <>Gap<span className="mt-0.5 block text-xs opacity-80">USD per kW</span></>,
              <>Offered and unawarded, at the clearing price<span className="mt-0.5 block text-xs opacity-80">USD per kW; overlaps between services</span></>]}
            rows={g.services.map((s) => ({
              key: s.key,
              cells: [<span key="s" data-offers-service={s.key}>{s.label}</span>, pct(s.offerShare, 1), pct(s.atOrBelowClearingShare, 1), pct(s.awardShare, 1), pct(s.awardOfOffer, 1),
                usd(s.awardsKw), usd(s.modelKw), usd(s.gapKw), <span key="u" data-offers-unawarded={s.key} data-offers-raw={s.unawardedKw}>{usd(s.unawardedKw)}</span>],
            }))} />
          <div className="mt-3 max-w-3xl space-y-2 text-sm">
            <p>{hi <= 1 / 3 ? "In every service the fleet offered several times what it was awarded" : "In every service the fleet offered more than it was awarded"}: between {pct(lo)} and {pct(hi)} of
              the offered capacity was awarded. Counting each block once, whichever services it was priced for, ancillary offers came to {pct(g.asOfferShareOfLimit)} of the fleet&apos;s limit-hours
              and awards to {pct(g.asAwardShareOfLimit)} (MW offered or awarded over MW of limit, hour by hour; a resource&apos;s blocks can add up to more than its limit).</p>
            {covered.length ? (
              <p data-offers-covered={covered.map((s) => s.key).join(",")}>In {list(covered.map((s) => s.label))}, the offered and unawarded capacity, valued at the clearing price, is as large as the
                service&apos;s gap or larger ({covered.map((s) => `${s.label}: ${usd(s.unawardedKw)} against a gap of ${usd(s.gapKw)}`).join("; ")}). The gap there is capacity that was offered and not awarded.</p>
            ) : null}
            {short.length ? (
              <p data-offers-short={short.map((s) => s.key).join(",")}>In {list(short.map((s) => s.label))}, it covers only part of the gap
                ({short.map((s) => `${s.label}: ${usd(s.unawardedKw)} of ${usd(s.gapKw)}, ${pct(s.unawardedKw / s.gapKw)}`).join("; ")}). The rest of that gap is capacity the fleet did not offer to that service.</p>
            ) : null}
            {noGap.length ? <p>In {list(noGap.map((s) => s.label))}, the awards are not below the model&apos;s figure, so there is no gap to split.</p> : null}
            <p data-offers-caution="overlap"><strong>Do not add the last column up.</strong> A block can be priced for several services and awarded to one, so the services&apos; unawarded values overlap and must not be added to a total.</p>
            <p data-offers-caution="forecast"><strong>It is not a forecast.</strong> The unawarded offers are valued at the price that was set. Had they been awarded, the price would have been lower: more awards would have lowered the price.</p>
          </div>
        </div>

        <div data-offers-cannot="1">
          <h3 className="mb-2 font-serif text-lg">What the offers still cannot show</h3>
          <ul className="max-w-3xl list-disc space-y-1.5 pl-4 text-sm">
            <li><strong>Why a resource offered nothing.</strong> An outage is visible for {points(g.noOfferOutShare)} of the {points(g.noOfferShare)} points. For the rest the file gives no reason: state of charge,
              a real-time strategy, a contract, or ancillary services its scheduling entity arranged itself, which ERCOT discloses by entity and not by resource.</li>
            <li><strong>What that capacity did in real time.</strong> The capacity not offered or not awarded day-ahead may have traded in real time. That is another report, and it is not in these tables.</li>
            <li><strong>How much energy stood behind the offered power.</strong> The file has no state of charge and no duration, so MWh offered on paper cannot be read as MWh deliverable.</li>
            <li><strong>What the market would have paid had more cleared.</strong> A clearing price is the price of what did clear.</li>
            <li><strong>Which service an unawarded block would have gone to.</strong> A block priced for several services is counted under each of them.</li>
          </ul>
        </div>
        {g.leftOut.length ? (
          <p className="max-w-3xl text-xs text-muted" data-offers-left-out="1">Held whole by the awards table and not in these sums: {g.leftOut.map((x) => `${x.m} (${x.why})`).join("; ")}.</p>
        ) : null}
      </div>
    );
  }
  return (
    <ToolSection title={TITLE} id="offers" note={<>From ERCOT&apos;s 60-Day DAM Disclosure, 60 days after each day: each storage resource&apos;s Energy Bid/Offer Curve and its ancillary service offer
      blocks. Over the months the awards, the offers and the model all hold whole, per kW of the fleet&apos;s MW; no partial month is scaled. The model&apos;s figures are the model&apos;s, not ERCOT&apos;s:
      one 2-hour battery on the day-ahead schedule. Day-ahead only, as the rest of this page. <Link href={OFFERS_METHOD}>Method</Link>.</>}>
      {body}
    </ToolSection>
  );
}
