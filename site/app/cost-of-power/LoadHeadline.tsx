"use client";
// Session 195: the headline of /cost-of-power, which scenario A sets. The three headline numbers are A's rows of the
// table "Scenarios A and B" (LoadScenarios.tsx): the market energy of the way A runs, the bad month of that way, and the
// power per GPU-hour at A's power per GPU and overhead ratio, with A's other charges. The power per GPU-hour of the
// summary sentence and of "What will it cost" prices the load as "Your load" describes it, at A's power per GPU and
// overhead ratio (GpuHourOfA). Until this session "Your load" held those two fields itself. Computed in the browser as
// scenario A is changed; nothing is sent.
import type { ReactNode } from "react";
import { useScenarios } from "@/components/decisions/ScenarioBlock";
import { HeadlineNumber, HeadlineRow } from "@/components/tool/ToolPage";
import { gpuHour as gpuHourOf, monthName, two, usdShort, whole } from "@/lib/datacenter";
import { FLAT, FLEX, resultOf, wayOf, type Assumptions } from "@/lib/datacenter/finance";
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
  return (
    <HeadlineRow>
      <HeadlineNumber label="Last twelve months, market energy"
        value={w ? <>USD {two(w.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={w ? <>USD {usdShort(w.cost * f.mw)} for {whole(w.energy * f.mw)} MWh, {f.span}.{own ? foreseen : <span data-scenario-a-run="1"> Scenario A runs {run === FLEX ? `flexible (${f.words[FLEX]})` : "flat"}. The sections below are the load as &quot;Your load&quot; describes it.</span>}</> : null} />
      <HeadlineNumber label="A bad month: the worst tenth of the last 36"
        value={bad ? <>USD {two(bad.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : missing}
        note={bad ? <>{monthName(bad.m)}. One month in ten of the {bad.of} held from {monthName(bad.first)} to {monthName(bad.to)} cost this or more.</> : null} />
      <HeadlineNumber label="Power per GPU-hour"
        value={r ? <>USD {r.gpuHour.toFixed(4)}</> : missing}
        note={<>At {a.gpu} kW per GPU and an overhead ratio of {a.pue}: {f.size} powers {whole((f.mw * 1000) / (a.gpu * a.pue))} GPUs.{a.adder > 0 ? <span data-scenario-a-adder="1"> With USD {plain(a.adder)} per MWh of other charges, as scenario A has them.</span> : null}</>} />
    </HeadlineRow>
  );
}
