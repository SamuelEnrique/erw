// Session 2401: the line both views of /policy carry when a source is paused: each paused publisher by the page's name
// for it, with "paused since <day>" and the record's reason, day, ruling and condition on hover. The record is
// data/policy/paused.json, built from warehouse/metadata/paused_sources.csv (scripts/build-paused.mjs); only a person
// adds or removes a row. Nothing when none is paused. A server component with no state: the words are the record's.
import { pausedLine, type PausedFile } from "@/lib/policyweek";

const dotted = "cursor-help border-b border-dotted border-muted";
const WHAT = "A paused publisher is one the ERW never requests (warehouse/metadata/paused_sources.csv): its rows already held stay as they are, nothing new is read from it, and only a person lifts the pause.";

export function PausedLine({ file, names }: { file: PausedFile | null; names?: Record<string, string> }) {
  const line = pausedLine(file, names);
  if (!line.items.length) return null;
  return (
    <p className="mb-5 max-w-3xl text-xs text-muted" data-policy-paused={line.items.map((i) => i.key).join(" ")}>
      <span className={dotted} title={WHAT}>{line.words}</span>:{" "}
      {line.items.map((i, k) => (
        <span key={i.key} data-policy-paused-source={i.key}>
          {k ? "; " : ""}{i.name}, <span className={`${dotted} italic`} title={i.why}>{i.words}</span>
        </span>
      ))}.
    </p>
  );
}
