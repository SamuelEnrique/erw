"use client";
// Session 195: the headline of /cost-of-power, which scenario A sets. The three headline numbers are A's rows of the
// table "Scenarios A and B" (LoadScenarios.tsx): the market energy of the way A runs, the bad month of that way, and the
// power per GPU-hour at A's power per GPU and overhead ratio, with A's other charges. The power per GPU-hour of the
// summary sentence and of "What will it cost" prices the load as "Your load" describes it, at A's power per GPU and
// overhead ratio (GpuHourOfA). Until this session "Your load" held those two fields itself. Computed in the browser as
// scenario A is changed; nothing is sent.
// Session 213: with a contract in A (its share and price are two of A's assumptions) the first headline number is the
// price of the energy consumed, the contracted share at its price and the rest at the market's, and says so; at a
// share of 0 it is the market's figure, as before.
import type { ReactNode } from "react";
import { useScenarios } from "@/components/decisions/ScenarioBlock";
import { HeadlineNumber, HeadlineRow } from "@/components/tool/ToolPage";
import { gpuHour as gpuHourOf, monthName, two, usdShort, whole } from "@/lib/datacenter";
import { FLAT, FLEX, contractYear, marketYear, resultOf, wayOf, type Assumptions } from "@/lib/datacenter/finance";
import type { Facts } from "./LoadScenarios";

const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });

/** Power per GPU-hour at a price per MWh, at scenario A's power per GPU and overhead ratio: the figure of the summary
 * sentence and of "What will it cost", which price the load as "Your load" describes it. */
export function GpuHourOfA({ per }: { per: number }) {
  const { s } = useScenarios<Assumptions>();
  return <>{gpuHourOf(per, s.a.gpu, s.a.pue).toFixed(4)}</>;
}

/** The three headline numbers: scenario A's rows "Market energy", "A bad month" and "Power per GPU-hour". `foreseen`
 * is the server's own note beside the first, for the way "Your load" describes; `missing` says why a figure is not held. */
export function LoadHeadline({ facts: f, foreseen, missing }: { facts: Facts; foreseen: ReactNode; missing: ReactNode }) {
  const { s } = useScenarios<Assumptions>();
  const a = s.a, run = a.run === FLEX ? FLEX : FLAT;
  const w = wayOf(a, f.ways), r = w ? resultOf(a, w) : null, bad = f.bads[run];
  const own = run === (f.load.run === FLEX ? FLEX : FLAT);
  const contracted = (a.cshare ?? 0) > 0 && !!w;
  const per = w ? (contracted ? (marketYear(a, w) + contractYear(a, w)) / w.energy : w.per) : null;
  // session 7622, the other choice of the ruling on energy and delivery together (wip/alt-cost-of-power-2, not landed):
  // once the site's wires utility is known, the first number is energy and delivery, scenario A's delivery charge added
  const withDelivery = !!f.adderSource && a.adder > 0 && !!w;
  const shown = per !== null ? per + (withDelivery ? a.adder : 0) : null;
  return (
    <HeadlineRow>
      <HeadlineNumber label={withDelivery ? (contracted ? "Last twelve months, energy with the contract, and delivery" : "Last twelve months, energy and delivery") : contracted ? "Last twelve months, energy with the contract" : "Last twelve months, market energy"}
        value={w && shown !== null ? <><span data-headline-contract={contracted ? "1" : undefined} data-headline-delivery={withDelivery ? "1" : undefined}>USD {two(shown)}</span><span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={w ? <>USD {usdShort(((contracted ? marketYear(a, w) + contractYear(a, w) : w.cost) + (withDelivery ? a.adder * w.energy : 0)) * f.mw)} for {whole(w.energy * f.mw)} MWh, {f.span}.{withDelivery && per !== null ? <span data-headline-delivery="2"> Energy USD {two(per)} per MWh and delivery USD {plain(a.adder)}, as scenario A has it.</span> : null}{contracted ? <span data-headline-contract="2"> Scenario A&apos;s contract: {plain(a.cshare)} percent of the energy at USD {plain(a.cprice)} per MWh, the rest at the market&apos;s USD {two(w.per)}.</span> : null}{own ? foreseen : <span data-scenario-a-run="1"> Scenario A runs {run === FLEX ? `flexible (${f.words[FLEX]})` : "flat"}. The sections below are the load as &quot;Your load&quot; describes it.</span>}</> : null} />
      <HeadlineNumber label="A bad month: the worst tenth of the last 36"
        value={bad ? <>USD {two(bad.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={bad ? <>{monthName(bad.m)}. One month in ten of the {bad.of} held from {monthName(bad.first)} to {monthName(bad.to)} cost this or more.</> : null} />
      <HeadlineNumber label="Power per GPU-hour"
        value={r ? <>USD {r.gpuHour.toFixed(4)}</> : missing}
        note={<>At {a.gpu} kW per GPU and an overhead ratio of {a.pue}: {f.size} powers {whole((f.mw * 1000) / (a.gpu * a.pue))} GPUs.{a.adder > 0 ? <span data-scenario-a-adder="1"> With USD {plain(a.adder)} per MWh of other charges, as scenario A has them.</span> : null}</>} />
    </HeadlineRow>
  );
}
