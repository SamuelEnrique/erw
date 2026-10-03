import { SiteLink as Link } from "@/components/SiteLink";
import { caisoJoinDay } from "@/lib/caisoJoin";

// Session 73 put one sentence near any figure that uses EIA-930's generation for California after the series changed
// (the date is CAISO_JOIN, lib/caisoJoin.ts), saying the figures were under review. Session 78 (Samuel's ruling): the sentence now says what the
// figure is on each side of the join (docs/methods/eia930_caiso_break.md). One sentence, with the method link.
//   carbon  a carbon intensity of generation that crosses the date: EIA's CO2 over EIA's generation before it, over
//           CAISO's own generation from it (carbon_intensity_*, warehouse/derived/caiso_join.py)
//   mix     generation by fuel after the date, still read from EIA-930: said plainly, with what differs
//   both    a page that shows the two (the California grid page)
// The carbon sentence is true once the joined tables are the live ones (archive/sessions/SESSION_78_REPORT.md, "To
// finish"); this component and those tables go live together.
export type CaisoNoteKind = "carbon" | "mix" | "both";

export function CaisoBreakNote({ className = "mb-4", kind = "carbon" }: { className?: string; kind?: CaisoNoteKind }) {
  const day = caisoJoinDay();
  const carbon = <>California&apos;s carbon intensity of generation is EIA&apos;s CO2 over EIA&apos;s generation before {day} and over CAISO&apos;s own generation from that date, joined there and not blended</>;
  const mix = <>California&apos;s generation by fuel here is EIA-930&apos;s, whose solar and wind have read below CAISO&apos;s own supply since {day}</>;
  return (
    <p className={`${className} max-w-3xl border-l-2 border-accent bg-paper px-3 py-1.5 text-xs`} data-caiso-break="1" data-caiso-kind={kind}>
      {kind === "carbon" ? carbon : kind === "mix" ? mix : <>{carbon}; its generation by fuel here is still EIA-930&apos;s</>}:{" "}
      <Link href="/data/methods/eia930_caiso_break">the method note</Link>.
    </p>
  );
}
