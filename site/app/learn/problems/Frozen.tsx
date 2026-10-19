// Session 293: the parts of a question of a dated edition. Its figures are frozen with the edition, so they are drawn
// as they were built, not as live numbers (no check key is read against today's tables: the edition's source rows are
// in each question's download). The live sets keep components/Num.tsx and their checks.
import { shown } from "@/lib/format";
import type { Part } from "@/lib/problems";

export function FrozenParts({ parts }: { parts: Part[] }) {
  return (
    <>
      {parts.map((p, i) =>
        typeof p === "string" ? <span key={i}>{p}</span> : (
          <span key={i} className="font-mono" data-frozen={p.k}>{shown(p.v)}{p.u ? ` ${p.u}` : ""}</span>
        ))}
    </>
  );
}
